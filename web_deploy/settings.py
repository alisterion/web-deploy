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

from six import add_metaclass, PY2
import xmltodict

if PY2:
    from codecs import open

__author__ = 'y.gavenchuk'


@add_metaclass(ABCMeta)
class AbstractSettings(object):
    _parser = None

    def __init__(self, config):
        self._cfg_file = config
        self._data = self.parse()

    @abstractmethod
    def parse(self):
        pass

    @property
    def data(self):
        return self._data


class SettingsXML(AbstractSettings):
    _parser = xmltodict

    def parse(self):
        with open(self._cfg_file, 'r', encoding='utf-8') as fp:
            return self._parser.parse(fp.read())['WebDeploy']
