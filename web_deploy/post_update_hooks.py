# -*- coding: utf-8 -*-
"""
    Pluggable post update hooks. May be specified in config file
"""

from web_deploy.system import FileSystemAPI

__author__ = 'y.gavenchuk'
__all__ = ('create_symlink', )


def create_symlink(*items):
    fsa = FileSystemAPI()

    for item in items:
        fsa.mk_symlink(item)
