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

import os

from fabric import api, context_managers
from fabric.contrib import files


__author__ = 'y.gavenchuk'
__all__ = ('DeployError', 'DeployEntity', 'LocatedDeployEntity', )


class DeployError(Exception):
    pass


class DeployEntity(object):
    __slots__ = ()

    _api = api
    _files = files
    _cm = context_managers
    _os = os


class LocatedDeployEntity(DeployEntity):
    __slots__ = ('_path', )

    def __init__(self, path):
        self._path = str(path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = str(value)
