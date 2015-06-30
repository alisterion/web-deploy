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

from test_tools import FixtureManager

from web_deploy.factory import ProjectFactory
from web_deploy.project import Project


__author__ = 'y.gavenchuk'
__all__ = ('AppTestCase', )


class AppTestCase(TestCase):
    _cfg = FixtureManager.get_fixture_path('config.xml')

    def test_project_factory_should_return_project_instance(self):
        pf = ProjectFactory(self._cfg).get()
        self.assertIsInstance(pf, Project)
