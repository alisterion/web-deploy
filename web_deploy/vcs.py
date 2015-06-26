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

from .base import LocatedDeployEntity


__author__ = 'y.gavenchuk'
__all__ = ('Git', )


class Git(LocatedDeployEntity):
    __slots__ = ('_name', '_url', )

    def __init__(self, path, name, url):
        super(Git, self).__init__(path)
        self._name = name
        self._url = url

    @property
    def _git_cmd(self):
        return 'git '

    @property
    def repository_dir(self):
        return self._os.path.join(self._path, self._name)

    @property
    def url(self):
        return self._url

    def clone(self):
        if self._files.exists(self.repository_dir):
            return

        self._api.run('{git} clone "{repository}" "{target_dir}"'.format(
            git=self._git_cmd,
            repository=self.url,
            target_dir=self.repository_dir
        ))

    def update(self, tag=None):
        self.clone()

        with self._api.cd(self.repository_dir):
            # If the working directory does not exist before initializing,
            # it has already been cloned and are not in need of updating
            self._api.run('{git} clean -fd'.format(git=self._git_cmd))

            if tag:
                self._api.run('{git} fetch'.format(git=self._git_cmd))
                self._api.run('{git} checkout {tag}'.format(
                    tag=tag,
                    git=self._git_cmd
                ))

            self._api.run('{git} pull'.format(git=self._git_cmd))
