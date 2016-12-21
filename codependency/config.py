#!/usr/bin/env python


class Config(object):
    @classmethod
    def _supply(cls, module):
        cls.config = module


def supply(module):
    Config._supply(module)


def get():
    return Config.config
