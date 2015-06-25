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

from .base import DeployEntity


__author__ = 'y.gavenchuk'
__all__ = ('System', )


class System(DeployEntity):
    __slots__ = ('_tree', '_log_files', '_app_dir', '_daemons', )

    def __init__(self, project_tree, app_dir, log_files, daemons=None):
        super(System, self).__init__()
        self._tree = project_tree
        self._log_files = log_files
        self._app_dir = app_dir
        self._daemons = daemons or []

    def _mk_log_dir(self, dir_name):
        self._api.sudo('mkdir -p -- "%s"' % dir_name)
        self._api.sudo('chown -R www-data:www-data -- "%s"' % dir_name)
        self._api.sudo('chmod -R 755 -- "%s"' % dir_name)

    def _mk_file(self, file_name):
        self._api.sudo('touch -- "%s"' % file_name)
        self._api.sudo('chmod 644 -- "%s"' % file_name)
        self._api.sudo('chown -R www-data:www-data -- "%s"' % file_name)

    def _mk_log(self, log_file):
        if not self._files.exists(log_file):
            self._mk_log_dir(self._os.path.dirname(log_file))
            self._mk_file(log_file)

    def _mk_symlink(self, source, target):
        self._api.run('ln -sfT -- "{source}" "{target}"'.format(
            source=source,
            target=target
        ))

    @property
    def app_directory(self):
        return self._app_dir

    @property
    def app_directory_active(self):
        return self._api.run('readlink -- "{0}"'.format(self.app_directory))

    @property
    def app_directory_inactive(self):
        active_dir = self._os.path.abspath(self.app_directory_active)
        inactive_dir_suffix = ({'1', '2'} ^ {active_dir[-1]}).pop()

        return active_dir[:-1] + inactive_dir_suffix

    def app_directory_switch(self):
        self._mk_symlink(self.app_directory_inactive, self.app_directory)

    def create_project_tree(self):
        for directory in self._tree:
            self._api.run('mkdir -p -- "%s"' % directory)

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
