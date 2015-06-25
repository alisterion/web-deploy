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

from fabric import api


__author__ = 'y.gavenchuk'
__all__ = ('Daemon', 'SimpleService', 'Nginx', 'Uwsgi', 'Supervisor', )


class Daemon(object, metaclass=ABCMeta):
    _name = None
    _api = api

    def __str__(self):
        return self.name

    @property
    def name(self):
        return str(self._name)

    @abstractmethod
    def restart(self):
        pass


class SimpleService(Daemon):
    def restart(self):
        self._api.sudo('service %s restart' % self.name)


class Nginx(SimpleService):
    _name = 'nginx'


class Uwsgi(SimpleService):
    _name = 'uwsgi'


class Supervisor(Daemon):
    _name = 'supervisor'
    _service = 'all'

    def __init__(self, service=None):
        super(Supervisor, self).__init__()
        if service:
            self._service = service

    def restart(self):
        self._api.sudo('supervisorctl reread')
        self._api.sudo(
            'supervisorctl %s restart %s' % (self.name, self._service, )
        )
