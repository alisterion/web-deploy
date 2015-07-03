# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock

from test_tools import FixtureManager

from web_deploy.python import DjangoProjectModule
from web_deploy.system import FileSystemAPI
from web_deploy.settings import SettingsXML


__author__ = 'y.gavenchuk'
__all__ = ('DjangoPrjModuleTestCase', )


class DjangoPrjModuleTestCase(TestCase):
    _cfg = SettingsXML(
        FixtureManager.get_fixture_path('config.xml')
    ).data['project']

    def test_ensure_media_root(self):
        target_files = 'web_deploy.system.FileSystemAPI._files'
        target_api = 'web_deploy.system.FileSystemAPI._api'
        sys_f = mock.MagicMock(**{'exists.return_value': False})
        m_api = mock.MagicMock()
        path = '/srv/www/web-deploy/www2/data'
        with mock.patch(target_files, sys_f), mock.patch(target_api, m_api):
            fs = FileSystemAPI()
            dj_m = DjangoProjectModule(
                path=path,
                git=mock.MagicMock(),
                virtual_env=mock.MagicMock(),
                system=mock.MagicMock(fs=fs),
                python_rq_file=mock.MagicMock(),
                apt_rq_file=mock.MagicMock(),
                db=mock.MagicMock(),
                manage_py=mock.MagicMock(),
                media_dir=self._cfg['modules']['module']['media_dir']
            )
            dj_m.puh_ensure_media_root()

        self.assertEqual(
            m_api.run.call_args_list,
            [
                mock.call(
                    'ln -sT -- "/srv/www/web-deploy/public_files" '
                    '"/srv/www/web-deploy/www2/data/web-deploy/public"'
                )
            ]
        )
