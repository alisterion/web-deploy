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

from six import string_types

from .base import DeployEntity, DeployError
from .daemon import Daemon


__author__ = 'y.gavenchuk'
__all__ = ('System', )


class FileSystemEntity(object):
    TYPE_FILE = 'file'
    TYPE_DIRECTORY = 'dir'
    TYPE_SYMLINK = 'symlink'

    DEFAULT_TYPE = TYPE_FILE
    DEFAULT_GROUP = 'www-data'
    DEFAULT_OWNER = 'www-data'
    DEFAULT_MODE = '0644'

    __slots__ = ('_raw', '_path', '_type', '_owner', '_group', '_mode',
                 '_target', )

    def _validate_symlink_target(self):
        if self._type == self.TYPE_SYMLINK:
            err_msg_target = 'There should be not empty target of symlink!'
            assert self._target is not None, err_msg_target
        else:
            self._target = self.path

    @staticmethod
    def _validate_item(item):
        err_msg_type = "Should be instance of dict, str or FileSystemEntity!"
        allowed_types = (string_types, dict, FileSystemEntity)
        assert isinstance(item, allowed_types), err_msg_type

    def _from_str(self, item, type_, owner, group, mode, target):
        self._path = item
        self._type = type_
        self._owner = owner
        self._group = group
        self._mode = mode
        self._target = target

        self._validate_symlink_target()

    def _from_dict(self, item, type_, owner, group, mode, target):
        err_path_msg = 'Should be "path" or "text" specified!'
        assert 'path' in item or 'text' in item, err_path_msg

        self._path = item.get('path') or item.get('text')

        if type_ != self.DEFAULT_TYPE:
            self._type = type_
        else:
            self._type = item.get('type', self.DEFAULT_TYPE)

        if owner != self.DEFAULT_OWNER:
            self._owner = owner
        else:
            self._owner = item.get('owner', self.DEFAULT_OWNER)

        if group != self.DEFAULT_GROUP:
            self._group = group
        else:
            self._group = item.get('group', self.DEFAULT_GROUP)

        if mode != self.DEFAULT_MODE:
            self._mode = mode
        else:
            self._mode = item.get('mode', self.DEFAULT_MODE)

        self._target = item.get('target', target)
        self._validate_symlink_target()

    def _clone(self, other):
        for f in self.__slots__:
            setattr(self, f, getattr(other, f))

    def __init__(self, item, type_=DEFAULT_TYPE, owner=DEFAULT_OWNER,
                 group=DEFAULT_GROUP, mode=DEFAULT_MODE, target=None):
        """

        :param dict|str item:
        :param str type_:
        :param str owner:
        :param str group:
        :param str mode:
        :param str target: target of symlink
        """
        self._validate_item(item)

        self._raw = item
        self._path = ''
        self._type = ''
        self._owner = ''
        self._group = ''
        self._mode = ''
        self._target = ''

        if isinstance(item, string_types):
            self._from_str(item, type_, owner, group, mode, target)
        elif isinstance(item, dict):
            self._from_dict(item, type_, owner, group, mode, target)
        else:
            self._clone(item)

    def __str__(self):
        return self.path

    @property
    def path(self):
        return self._path

    @property
    def type(self):
        return self._type

    @property
    def owner(self):
        return self._owner

    @property
    def group(self):
        return self._group

    @property
    def mode(self):
        return self._mode

    @property
    def target(self):
        return self._target


class FileSystemAPI(DeployEntity):
    def _run(self, cmd, sudo=False):
        if sudo:
            return self._api.sudo(cmd)

        return self._api.run(cmd)

    def mkdir(self, item, sudo=False):
        """
        :param FileSystemEntity item:
        :param bool sudo:
        """
        fse_item = FileSystemEntity(item)
        self._run('mkdir -p -- "%s"' % fse_item.path, sudo)

    def chown(self, item):
        fse_item = FileSystemEntity(item)

        if fse_item.group or fse_item.owner:
            self._api.sudo('chown {owner}:{group} -- "{path}"'.format(
                owner=fse_item.owner,
                group=fse_item.group,
                path=fse_item.path
            ))

    def chmod(self, item):
        fse_item = FileSystemEntity(item)
        if not fse_item.mode:
            return

        self._api.sudo('chmod {mode} -- "{path}"'.format(
            mode=fse_item.mode,
            path=fse_item.path
        ))

    def exists(self, item):
        return self._files.exists(str(item))

    def readlink(self, item):
        """
        :param FileSystemEntity|str item:

        :return str:
        """
        return self._api.run('readlink -- "{0}"'.format(str(item)))

    def touch(self, item, sudo=False):
        self._run('touch -- "%s"' % str(item), sudo)

    def mk_symlink(self, item, force=False):
        import sys
        sys.stdout.write("START")
        fse = FileSystemEntity(item)
        if fse.type != FileSystemEntity.TYPE_SYMLINK:
            sys.stdout.write("err 1")
            raise DeployError("Symlink expected!. Got '%s'" % fse.type)

        if fse.path == fse.target:
            sys.stdout.write("err 2")
            raise DeployError("Source and target are equal! '%s'" % str(fse))

        sys.stdout.write("-----"+str(self.exists(fse.target)))
        if not self.exists(fse.target) or force:
            self._api.run('ln -s{force}T -- "{source}" "{target}";'.format(
                source=fse.path.strip(),
                target=fse.target.strip(),
                force='f' if force else ''
            ))

    def join_path(self, *paths):
        return self._os.path.join(
            *map(lambda x: str(FileSystemEntity(x)), paths)
        )


class System(DeployEntity):
    __slots__ = ('_tree', '_log_files', '_app_dir', '_daemons', '_fs', )

    def __init__(self, project_tree, app_dir, log_files, daemons=None):
        super(System, self).__init__()
        self._tree = project_tree
        self._log_files = log_files
        self._app_dir = app_dir

        daemon_err_msg = 'Expected instance of "{daemon}". Got "%s"'.format(
            daemon=Daemon
        )
        for d in daemons:
            assert isinstance(d, Daemon), daemon_err_msg % type(d)
        self._daemons = daemons or []

        self._fs = FileSystemAPI()

    def _mk_log_dir(self, dir_item):
        fse_dir = FileSystemEntity(
            dir_item,
            type_=FileSystemEntity.TYPE_DIRECTORY,
            owner='www-data',
            group='www-data',
            mode='755'
        )
        self.fs.mkdir(fse_dir, sudo=True)
        self.fs.chown(fse_dir)
        self.fs.chmod(fse_dir)

    def _mk_file(self, file_item):
        """
        :param FileSystemEntity file_item:
        """
        self.fs.touch(file_item, sudo=True)
        self.fs.chmod(file_item)
        self.fs.chown(file_item)

    def _mk_log(self, log_file):
        fs_log = FileSystemEntity(log_file)

        if not self.fs.exists(fs_log.path):
            self._mk_log_dir(self._os.path.dirname(fs_log.path))
            self._mk_file(fs_log)

    def _mk_symlink(self, source, target):
        fse_item = FileSystemEntity(
            source,
            target=target,
            type_=FileSystemEntity.TYPE_SYMLINK,
        )
        self.fs.mk_symlink(fse_item, force=True)

    @property
    def fs(self):
        return self._fs

    @property
    def app_directory(self):
        return self._app_dir

    @property
    def app_directory_active(self):
        return self.fs.readlink(self.app_directory)

    @property
    def app_directory_inactive(self):
        active_dir = self._os.path.abspath(self.app_directory_active)
        inactive_dir_suffix = ({'1', '2'} ^ {active_dir[-1]}).pop()

        return active_dir[:-1] + inactive_dir_suffix

    def app_directory_switch(self):
        self._mk_symlink(self.app_directory_inactive, self.app_directory)

    def create_project_tree(self):
        for directory in self._tree:
            self.fs.mkdir(directory)

        if not self._files.is_link(self.app_directory):
            self._mk_symlink(self.app_directory + '1', self.app_directory)

    def install_system_packages(self, apt_pkg_file):
        self._api.sudo('apt-get -y install -- `cat "%s"`' % apt_pkg_file)

    def ensure_log_files(self):
        for f in self._log_files:
            self._mk_log(f)

    def restart_daemons(self):
        for daemon in self._daemons:
            daemon.restart()
