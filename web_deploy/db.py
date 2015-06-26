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

from abc import ABCMeta, abstractmethod
from datetime import datetime

from .base import LocatedDeployEntity

__author__ = 'y.gavenchuk'


class DataBase(LocatedDeployEntity, metaclass=ABCMeta):
    DEFAULT_BACKUP_COUNT = 5

    __slots__ = ('_host', '_user', '_port', '_db_name', '_password',
                 '_bkp_count', )

    def __init__(self, path, name, user, password, host='localhost', port='',
                 backup_count=DEFAULT_BACKUP_COUNT):
        super(DataBase, self).__init__(path)
        self._host = host
        self._user = user
        self._db_name = name
        self._port = port
        self._password = password
        self._bkp_count = int(backup_count)
        assert self._bkp_count > 1, "Backups count can't be less than 2"

    def _rotate_backups(self):
        """
        Keep no more than `backup_count` dumps
        """
        backups = self._api.run('ls "%s"' % self.path, quiet=True).split()
        if not backups:
            return

        bkp_to_remove = sorted(backups)[:-self.backup_count]
        if not bkp_to_remove:
            return

        cmd = 'rm -- %s' % ' '.join(map(lambda x: '"%s"' % x, bkp_to_remove))
        with self._api.cd(self.path):
            self._api.run(cmd)

    @abstractmethod
    def _do_backup(self):
        pass

    @property
    def backup_count(self):
        return self._bkp_count

    def create_backup(self):
        self._do_backup()
        self._rotate_backups()


class Postgres(DataBase):
    __slots__ = ()

    def _do_backup(self):
        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        dump_file = 'dump_sql_%s' % now
        cmd_tpl = 'pg_dump --clean -h {host} -U {user} {dbname} ' \
                  '|gzip > {file}_db.sq.gz'
        cmd = cmd_tpl.format(
            host=self._host,
            user=self._user,
            dbname=self._db_name,
            file=dump_file
        )

        with self._api.cd(self.path):
            with self._cm.shell_env(PGPASSWORD=self._password):
                self._api.run(cmd)
