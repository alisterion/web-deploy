#!/usr/bin/env python
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
import re

from setuptools import setup, find_packages


__author__ = 'y.gavenchuk aka murminathor'


version = re.compile(r'__version__\s*=\s*[\'"](.*?)[\'"]')


def get_package_version():
    """returns package version without importing it"""
    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "web_deploy/__init__.py")) as f:
        for line in f:
            m = version.match(line.strip())
            if not m:
                continue
            return m.group(1)


setup(
    name='web-deploy',
    version=get_package_version(),
    description='Tools for automatic deployment of web projects '
                '(e.g. django based)',
    long_description=open('README').read(),
    author='y.gavenchuk aka murminathor',
    author_email='murminathor@gmail.com',
    url='https://github.com/ygavenchuk/web-deploy',
    license='Apache2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent'
    ],
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=['Fabric>=1.10.2', ],
    dependency_links=['git+https://github.com/akaariai/fabric.git@py34#egg=Fabric-1.10.2', ],
    zip_safe=True
)
