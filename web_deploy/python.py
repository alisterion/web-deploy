# -*- coding: utf-8 -*-
#
# Copyright 2015 Yuriy Gavenchuk aka murminathor
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .base import LocatedDeployEntity
from .project import ProjectModule


__author__ = 'y.gavenchuk'
__all__ = ('VirtualEnv', 'PythonProjectModule', 'DjangoProjectModule', )


class VirtualEnv(LocatedDeployEntity):
    __slots__ = ('_v_name', )

    DEFAULT_NAME = '.virtualenv'

    def __init__(self, path, name=DEFAULT_NAME):
        super(VirtualEnv, self).__init__(path)

        self._v_name = str(name)

    def _activate(self):
        return 'source "%s"' % self._os.path.join(
            self.directory, 'bin/activate'
        )

    @property
    def directory(self):
        return self._os.path.join(self._path, self._v_name)

    @property
    def name(self):
        return self._v_name

    @property
    def is_exists(self):
        return self._files.exists(
            self._os.path.join(self._path, self.name, 'bin', 'python')
        )

    def run(self, command):
        activate_str = 'source "%s"' % self._os.path.join(
            self.directory, 'bin/activate'
        )

        cmd_list = command if isinstance(command, (list, tuple)) else [command]
        with self._api.prefix(activate_str):
            for cmd in cmd_list:
                self._api.run(cmd)

    def mk(self):
        if self.is_exists:
            return

        with self._api.cd(self._path):
            self._api.run(
                '/usr/bin/virtualenv -p /usr/bin/python3.4 "%s"' % self._v_name
            )

        self.run('pip install -U pip setuptools')

    def install_packages(self, packages_file):
        self.mk()
        self.run([
            'pip install -U pip setuptools',
            'pip install -r "%s"' % packages_file
        ])

    @property
    def python(self):
        return self._os.path.join(
            self._path, self._v_name, 'bin/python'
        )


class PythonProjectModule(ProjectModule):
    __slots__ = ('_v_env', '_sys', '_py_rq', '_apt_rq')

    def __init__(self, path, git, virtual_env, system, python_rq_file,
                 apt_rq_file, container_name=None):
        """
        :param Git git:
        :param VirtualEnv virtual_env:
        :param System system:
        :param str python_rq_file: path to file with python requirement pkg.
                                   Note! This should be relative path.
                                   From module's container
        :param str apt_rq_file: path to file with system requirement pkg
                                Note! This should be relative path.
                                From module's container
        """
        super(PythonProjectModule, self).__init__(path, git, container_name)
        self._v_env = virtual_env
        self._v_env.path = path
        self._sys = system
        self._py_rq = python_rq_file
        self._apt_rq = apt_rq_file

        self._post_update_hooks = [
            self.puh_system,
            self.puh_python,
        ]

    @ProjectModule.path.setter
    def path(self, value):
        ProjectModule.path.fset(self, value)

        self._v_env.path = self.path

    def puh_system(self):
        self._sys.install_system_packages(
            self._sys.fs.join_path(self.path, self._apt_rq)
        )

    def puh_python(self):
        self._v_env.install_packages(
            self._sys.fs.join_path(self.path, self._py_rq)
        )


class DjangoProjectModule(PythonProjectModule):
    __slots__ = ('_manage_py', '_db', '_static_dir', '_media_dir', )

    def __init__(self, path, git, virtual_env, system, python_rq_file,
                 apt_rq_file, db, manage_py, collect_static=True,
                 container_name=None, static_dir='static', media_dir=None):
        super(DjangoProjectModule, self).__init__(
            path, git, virtual_env, system, python_rq_file, apt_rq_file,
            container_name
        )
        self._manage_py = manage_py
        self._db = db
        self._static_dir = static_dir
        self._media_dir = media_dir

        self._post_update_hooks += [
            self.puh_db_backup,
            self.puh_migrate,
            self.puh_ensure_media_root
        ]

        if collect_static:
            self._post_update_hooks.append(
                self.puh_collect_static
            )

    @property
    def manage_py(self):
        return self._sys.fs.join_path(self.path, self._manage_py)

    def puh_db_backup(self):
        self._db.create_backup()

    def puh_migrate(self):
        self._v_env.run('"%s" migrate' % self.manage_py)

    def puh_collect_static(self):
        static_path = self._sys.fs.join_path(self.path, self._static_dir)
        if not self._sys.fs.exists(static_path):
            self._sys.fs.mkdir(static_path)

        self._v_env.run('"%s" collectstatic --noinput' % self.manage_py)

    def puh_ensure_media_root(self):
        if self._media_dir:
            self._media_dir['target'] = self._sys.fs.join_path(
                self.path, self._media_dir['target']
            )
            self._sys.fs.mk_symlink(self._media_dir)
