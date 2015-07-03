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

from unittest import TestCase
from unittest import mock

from test_tools import FixtureManager

from web_deploy.factory import SystemFactory
from web_deploy.system import System
from web_deploy.settings import SettingsXML


__author__ = 'y.gavenchuk'
__all__ = ('SystemFactoryTestCase', )


class SystemFactoryTestCase(TestCase):
    _cfg = SettingsXML(
        FixtureManager.get_fixture_path('config.xml')
    ).data['project']

    def test_system_factory_should_return_system_instance(self):
        sf = SystemFactory().get(self._cfg)
        self.assertIsInstance(sf, System)

    def test_ensure_log_should_check_if_log_file_exists(self):
        sys_files = mock.MagicMock()
        target_files = 'web_deploy.system.FileSystemAPI._files'
        target_api = 'web_deploy.system.FileSystemAPI._api'
        with mock.patch(target_files, sys_files), mock.patch(target_api):
            SystemFactory().get(self._cfg).ensure_log_files()

        self.assertEqual(
            sys_files.exists.call_args_list,
            [
                mock.call('/var/log/web-deploy/web-deploy.log'),
                mock.call('/var/log/web-deploy/celery/out.log')
            ]
        )

    def test_if_log_not_exists_ensure_log_should_create_them(self):
        sys_files = mock.MagicMock(**{'exists.return_value': False})
        sys_api = mock.MagicMock()
        tg_files = 'web_deploy.system.FileSystemAPI._files'
        tg_api = 'web_deploy.system.FileSystemAPI._api'
        with mock.patch(tg_files, sys_files), mock.patch(tg_api, sys_api):
            SystemFactory().get(self._cfg).ensure_log_files()

        self.assertEqual(
            sys_api.sudo.call_args_list,
            [
                mock.call('mkdir -p -- "/var/log/web-deploy"'),
                mock.call(
                    'chown www-data:www-data -- "/var/log/web-deploy"'
                ),
                mock.call('chmod 755 -- "/var/log/web-deploy"'),
                mock.call('touch -- "/var/log/web-deploy/web-deploy.log"'),
                mock.call('chmod 0664 -- "/var/log/web-deploy/web-deploy.log"'),
                mock.call(
                    'chown me:www-data -- "/var/log/web-deploy/web-deploy.log"'
                ),
                mock.call('mkdir -p -- "/var/log/web-deploy/celery"'),
                mock.call(
                    'chown www-data:www-data -- '
                    '"/var/log/web-deploy/celery"'
                ),
                mock.call('chmod 755 -- "/var/log/web-deploy/celery"'),
                mock.call('touch -- "/var/log/web-deploy/celery/out.log"'),
                mock.call('chmod 0644 -- "/var/log/web-deploy/celery/out.log"'),
                mock.call(
                    'chown www-data:www-data -- '
                    '"/var/log/web-deploy/celery/out.log"'
                )
            ]
        )
