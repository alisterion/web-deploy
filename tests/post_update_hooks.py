# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest import mock

from test_tools import FixtureManager

from web_deploy.factory import ProjectModuleFactory
from web_deploy.settings import SettingsXML


__author__ = 'y.gavenchuk'
__all__ = ('PostUpdateHookTestCase', )


class PostUpdateHookTestCase(TestCase):
    _cfg = SettingsXML(
        FixtureManager.get_fixture_path('config.xml')
    ).data['project']

    def _get_hook(self):
        path = '/srv/www/web-deploy/www2/data'
        config = self._cfg.copy()
        config.update(dict(
            path=path,
            python_rq_file=mock.MagicMock(),
            apt_rq_file=mock.MagicMock(),
            manage_py=mock.MagicMock()
        ))
        factory = ProjectModuleFactory()
        factory._git = mock.MagicMock()
        factory._sys = mock.MagicMock()
        factory._venv = mock.MagicMock()
        factory._db = mock.MagicMock()

        dj_m = factory.get(config)[0]
        return dj_m._post_update_hooks[-1]

    def test_create_symlink_hook(self):
        target_files = 'web_deploy.system.FileSystemAPI._files'
        target_api = 'web_deploy.system.FileSystemAPI._api'
        sys_f = mock.MagicMock(**{'exists.return_value': False})
        m_api = mock.MagicMock()

        hook = self._get_hook()
        with mock.patch(target_files, sys_f), mock.patch(target_api, m_api):
            hook()

        self.assertEqual(
            m_api.run.call_args_list,
            [
                mock.call(
                    'ln -sT -- "/srv/www/web-deploy/public_files" '
                    '"/srv/www/web-deploy/www1/data/web-deploy/public"'
                ),
                mock.call(
                    'ln -sT -- "/srv/www/web-deploy/public_files" '
                    '"/srv/www/web-deploy/www2/data/web-deploy/public"'
                )
            ]
        )
