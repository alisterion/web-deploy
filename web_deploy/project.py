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

from .base import LocatedDeployEntity, DeployEntity

__author__ = 'y.gavenchuk'
__all__ = ('Project', 'ProjectModule',)


class ProjectModule(LocatedDeployEntity):
    __slots__ = ('_git', '_post_update_hooks', '_container')

    DEFAULT_CONTAINER_NAME = 'data'

    def __init__(self, path, git, container_name=None):
        super(ProjectModule, self).__init__(path)
        self._git = git
        self._git.path = self.path
        self._container = container_name or self.DEFAULT_CONTAINER_NAME
        self._post_update_hooks = []

    @property
    def git(self):
        return self._git

    @property
    def container(self):
        return self._container

    @LocatedDeployEntity.path.setter
    def path(self, value):
        new_path = self._os.path.join(value, self._container)
        LocatedDeployEntity.path.fset(self, new_path)

        self._git.path = new_path

    @property
    def post_update_hooks(self):
        yield from self._post_update_hooks

    def add_hook(self, *hooks):
        before_list = []
        after_list = []
        for priority, hook in hooks:
            if priority == 1:
                before_list.append(hook)
            else:
                after_list.append(hook)

        self._post_update_hooks = before_list + self._post_update_hooks + after_list

    def post_update_hndl(self):
        for hook in self._post_update_hooks:
            hook()

    def update(self, tag):
        """
        Perform module update: pull changes from git and apply all  post
                               update hooks

        :param str tag: git tag
        """
        self.git.update(tag)
        self.post_update_hndl()


class Project(DeployEntity):
    __slots__ = ('_p_modules', '_sys',)

    def __init__(self, system, modules):
        super(Project, self).__init__()
        self._sys = system

        t_error = "Expected modules is instance of list or tuple. Got '%s'."
        assert isinstance(modules, (list, tuple)), t_error % str(type(modules))
        assert len(modules), "Expected at least one module"
        self._p_modules = modules

    def _update_modules(self, tag=None):
        for prj_mod in self._p_modules:
            prj_mod.path = self._sys.app_directory_inactive
            prj_mod.update(tag)

    def update(self, tag=None):
        self._sys.create_project_tree()
        self._sys.ensure_log_files()
        self._update_modules(tag)
        self._sys.app_directory_switch()
        self._sys.restart_daemons()
