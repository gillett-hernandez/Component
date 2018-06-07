#!/usr/bin/env python

import pygame
from pygame.locals import *
import os
import sys
import logging

from component import Component, constants


class Sprite(object):
    def __init__(self, strip, uwidth=None, uheight=None, sprite_count=None):
        """frameids are as if """
        # strip width, strip height
        self.swidth, self.sheight = strip.get_size()
        # unit width, unit height
        self.uwidth, self.uheight = uwidth, uheight

        self.image = pygame.Surface((uwidth, uheight)).convert()

        self.rect = self.image.get_rect()

        self.image.set_colorkey((0, 0, 0))

        if sprite_count is None:
            self.sprite_count = (self.swidth//self.uwidth)*(self.sheight//self.uheight)
        else:
            self.sprite_count = sprite_count
        self.strip = strip
        self.images = []
        for ind in range(self.sprite_count):
            self.images.append(self.strip.subsurface(pygame.Rect(ind*self.uwidth, 0, self.uwidth, self.uheight)))
        self.set_image(0)

    def set_image(self, ind):
        self.image = self.images[ind]


class AngledSpriteComponent(Sprite, Component, pygame.sprite.Sprite):
    def __init__(self, obj, strip, uwidth=None, uheight=None, sprite_count=None):
        Component.__init__(self, obj)
        Sprite.__init__(self, strip, uwidth, uheight, sprite_count)
        self.po = self.obj.position
        self.ph = self.obj.physics
        self.obj.rect = self.obj.image.get_rect()
        self.obj.rect.topleft = self.po.pos.components
        self.attach_event('update', self.update)
        self.attach_event('turn', self.turn)
        self.dir = 90

    def update(self, **kwargs):
        x, y = self.po.pos.components
        self.obj.rect.topleft = [x, constants.LEVEL_HEIGHT-y]
        self.set_image(((self.dir-90)//6) % self.sprite_count)

    def turn(self, d0=0):
        self.dir -= d0
        self.dir %= 360

    def set_image(self, ind):
        super(AngledSpriteComponent, self).set_image(ind)
        self.obj.image = self.image


class AnimatedSpriteComponent(Sprite, Component, pygame.sprite.Sprite):
    """A Component that uses frame delays and spritesheets to animate an image
example usage to add a cycle that stops for 1 frame on each image: self.add_cycle("default", range(self.sprite_count), [1]*self.sprite_count)"""
    def __init__(self, obj, strip, uwidth=None, uheight=None, sprite_count=None):
        Component.__init__(self, obj)
        Sprite.__init__(self, strip, uwidth, uheight, sprite_count)
        self.attach_event('update', self.update)
        self.cycles = {}
        self.po = self.obj.position
        self.i = 0
        self.c = 0
        self.add_cycle_firstcalled = True
        self.add_cycle("default", range(self.sprite_count), [1]*self.sprite_count)

    def add_cycle(self, name, frameids, timestops):
        l = list(zip(frameids, timestops))
        self.cycles[name] = l
        if self.add_cycle_firstcalled is True:
            self.set_cycle(name)
            self.add_cycle_firstcalled = False

    def set_cycle(self, name):
        if name not in self.cycles:
            raise IndexError
        self.cycle = self.cycles[name]
        self.c = 0
        self.i = 0
        self.timestop = self.cycle[self.i][1]

    def update(self, **kwargs):
        logging.info("set image to next image at {} {}".format(self.i,0))
        self.set_image(self.cycle[self.i][0])
        if self.c % self.timestop == 0:
            self.i += 1
        if self.i % len(self.cycle) == 0:
            self.i = 0
        self.timestop = self.cycle[self.i][1]
        self.c += 1
        x, y = self.po.pos.components
        self.obj.rect.topleft = [x, constants.LEVEL_HEIGHT-y]

    def set_image(self, ind):
        super(AnimatedSpriteComponent, self).set_image(ind)
        self.obj.image = self.image




def test():

    screen = pygame.display.set_mode((64, 64), pygame.RESIZABLE)

    print(os.getcwd())
    sprite_sheet = pygame.image.load("./platformer/resources/images/plane.png").convert()

    swidth, sheight = sprite_sheet.get_size()

    from datastructures import DotDict
    obj = DotDict()
    obj.rect = DotDict()

    obj.position = DotDict()
    obj.position.pos = DotDict()
    obj.position.pos.components = [0,0]
    global constants
    constants = DotDict()
    constants.LEVEL_HEIGHT = 64
    spr_anim = AnimatedSpriteComponent(obj, sprite_sheet, 64, sheight, swidth//64)
    spr_anim.add_cycle("run", list(range(swidth//64)), [1]*(swidth//64))

    clock = pygame.time.Clock()

    bg = pygame.Surface((64, 64)).convert()
    bg.fill((255, 255, 255))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_q:
                    sys.exit()
                    pygame.quit()

        screen.blit(bg, (0, 0))
        screen.blit(spr_anim.image, (0, 0))
        spr_anim.update()
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    test()
