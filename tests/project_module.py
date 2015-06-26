# -*- coding: utf-8 -*-
from unittest import TestCase, mock
from web_deploy.project import ProjectModule


__author__ = 'y.gavenchuk'
__all__ = ('ProjectModuleTestCase', )


class ProjectModuleTestCase(TestCase):
    def test_setup_path(self):
        path_before = '/a/b/c'
        path_after = '/e/f/g'
        git = mock.MagicMock()

        pm = ProjectModule(path_before, git)
        pm.path = path_after

        self.assertEqual(pm.path, path_after)
