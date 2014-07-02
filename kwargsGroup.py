#!/usr/bin/python

import pygame


class UserGroup(pygame.sprite.RenderUpdates):
    def __init__(self, *sprites):
        super(UserGroup, self).__init__(*sprites)

    def update(self, *args, **kwargs):
        for s in self.sprites():
            s.update(*args, **kwargs)
