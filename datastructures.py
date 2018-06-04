#!/usr/bin/python

import pygame


class UserGroup(pygame.sprite.RenderUpdates):
    def __init__(self, *sprites):
        super(UserGroup, self).__init__(*sprites)

    def update(self, *args, **kwargs):
        for s in self.sprites():
            s.update(*args, **kwargs)

class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def items(self):
        return self.__dict__.items()


class Factory:
    def __init__(self, _class):
        self._class = _class

    def create(self, *args, **kwargs):
        d = {}
        d.update(kwargs)
        d.update(self.__dict__)
        return self._class(*args, **d)