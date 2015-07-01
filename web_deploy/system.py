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

from .base import DeployEntity
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

    __slots__ = ('_raw', '_path', '_type', '_owner', '_group', '_mode', )

    def __init__(self, item, type_=DEFAULT_TYPE, owner=DEFAULT_OWNER,
                 group=DEFAULT_GROUP, mode=DEFAULT_MODE):
        """

        :param dict|str item:
        :param str type_:
        :param str owner:
        :param str group:
        :param str mode:
        """
        assert isinstance(item, (string_types, dict)), "Should be dict or str!"
        self._raw = item

        if isinstance(item, string_types):
            self._path = item
            self._type = type_
            self._owner = owner
            self._group = group
            self._mode = mode
        else:
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


class System(DeployEntity):
    __slots__ = ('_tree', '_log_files', '_app_dir', '_daemons', )

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

    def _mk_log_dir(self, dir_item):
        self._api.sudo('mkdir -p -- "%s"' % dir_item)
        self._api.sudo('chown -R www-data:www-data -- "%s"' % dir_item)
        self._api.sudo('chmod -R 755 -- "%s"' % dir_item)

    def _mk_file(self, file_item):
        """
        :param FileSystemEntity file_item:
        """
        self._api.sudo('touch -- "%s"' % file_item.path)

        if file_item.mode:
            self._api.sudo('chmod {mode} -- "{path}"'.format(
                mode=file_item.mode,
                path=file_item.path
            ))

        if file_item.group or file_item.owner:
            self._api.sudo('chown {owner}:{group} -- "{path}"'.format(
                owner=file_item.owner,
                group=file_item.group,
                path=file_item.path
            ))

    def _mk_log(self, log_file):
        fs_log = FileSystemEntity(log_file)

        if not self._files.exists(fs_log.path):
            self._mk_log_dir(self._os.path.dirname(fs_log.path))
            self._mk_file(fs_log)

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
