# -*- coding: utf-8 -*-
"""
    Pluggable post update hooks. May be specified in config file
"""

from web_deploy.system import FileSystemAPI

__author__ = 'y.gavenchuk'
__all__ = ('create_symlink',)


def create_symlink(module, *items):
    fsa = FileSystemAPI()

    for item in items:
        item['target'] = module._sys.fs.join_path(module.path, item['target'])
        item['text'] = module._sys.fs.join_path(module.path, item['text'])
        fsa.mk_symlink(item)


def create_dir(module, *items):
    fsa = FileSystemAPI()

    for item in items:
        item['text'] = module._sys.fs.join_path(module.path, item['text'])
        fsa.mkdir(item)