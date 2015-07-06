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

from six import add_metaclass

from .system import System
from . import daemon, db, post_update_hooks
from .vcs import Git
from .python import VirtualEnv, DjangoProjectModule
from .settings import SettingsXML
from .project import Project


__author__ = 'y.gavenchuk'
__all__ = (
    'DaemonFactory', 'SystemFactory', 'GitFactory', 'DbFactory',
    'VirtualEnvFactory', 'ProjectModuleFactory', 'ProjectFactory',
)


@add_metaclass(ABCMeta)
class AbstractFactory(object):
    @abstractmethod
    def get(self, config):
        pass


class DaemonFactory(AbstractFactory):
    def get(self, config):
        if isinstance(config, dict):
            d_type = config.get('text')
            name = config.get('name')
        else:
            d_type = config
            name = None

        d_class = getattr(daemon, d_type.title())
        try:
            return d_class(name)
        except TypeError:
            return d_class()


class SystemFactory(AbstractFactory):
    _inst = None

    def __init__(self):
        self._df = DaemonFactory()

    def get(self, config, force_new=False):
        """
        :param dict config:
        :param bool force_new:
        :return System:
        """
        if SystemFactory._inst is None or force_new:
            cfg_system = config['system'].copy()
            cfg_system['project_tree'] = cfg_system['project_tree']['item']
            cfg_system['log_files'] = cfg_system['log_files']['item']

            cfg_system['daemons'] = []
            for d in config['system']['daemons']['daemon']:
                cfg_system['daemons'].append(self._df.get(d))

            SystemFactory._inst = System(**cfg_system)

        return SystemFactory._inst


class GitFactory(AbstractFactory):
    def get(self, config):
        return Git(**config)


class DbFactory(AbstractFactory):
    def get(self, config):
        db_cfg = config.copy()
        del db_cfg['type']
        db_type = getattr(db, config['type'])

        return db_type(**db_cfg)


class VirtualEnvFactory(AbstractFactory):
    def get(self, config):
        return VirtualEnv(**config)


class HooksFactory(AbstractFactory):
    def get(self, config):
        hook = getattr(post_update_hooks, config['type'])
        items = config.get('item')

        return lambda: hook(*items)


class ProjectModuleFactory(AbstractFactory):
    @staticmethod
    def _2b(value):
        return str(value).lower() not in {
            '0', 'false', '', 'none', 'null', 'no'
        }

    @staticmethod
    def _get_hooks(cfg):
        if 'hooks' not in cfg:
            return []

        hd = cfg.get('hooks', {}) or {}
        del cfg['hooks']

        hooks = hd.get('hook', [])
        if not hooks:
            return []

        hook_factory = HooksFactory()

        hooks_list = hooks if isinstance(hooks, list) else [hooks]
        return [hook_factory.get(h) for h in hooks_list]

    def __init__(self):
        self._sys = SystemFactory()
        self._venv = VirtualEnvFactory()
        self._db = DbFactory()
        self._git = GitFactory()

    def get_djangoprojectmodule(self, config):
        cfg_module = config.copy()
        del cfg_module['type']

        cfg_module['git'] = self._git.get(cfg_module['git'])
        cfg_module['virtual_env'] = self._venv.get(cfg_module['virtual_env'])
        cfg_module['db'] = self._db.get(cfg_module['db'])
        cfg_module['system'] = self._sys.get(config)

        cfg_module['collect_static'] = self._2b(cfg_module['collect_static'])
        hooks = self._get_hooks(cfg_module)

        dj = DjangoProjectModule(**cfg_module)
        dj.add_hook(*hooks)

        return dj

    def get(self, config):
        res = []
        if isinstance(config['modules']['module'], list):
            modules_list = config['modules']['module']
        else:
            modules_list = [config['modules']['module']]

        for m in modules_list:
            method = getattr(self, 'get_%s' % m['type'].lower())
            res.append(method(m))

        return res


class ProjectFactory(object):
    def __init__(self, config_file):
        self._cfg_file = config_file
        self._cfg = None
        self._sys = SystemFactory()
        self._p_mod = ProjectModuleFactory()

    @property
    def config(self):
        if self._cfg is None:
            self._cfg = SettingsXML(self._cfg_file).data['project']

        return self._cfg

    def get(self):
        return Project(
            system=self._sys.get(self.config),
            modules=self._p_mod.get(self.config)
        )
