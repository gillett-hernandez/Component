#!/usr/bin/env python

import pygame
from pygame.locals import *
import sys


class Animation:
    def __init__(self, strip, uwidth=None, uheight=None, sprite_count=None):
        """frameids are as if """
        # strip width, strip height
        self.swidth, self.sheight = strip.get_size()
        # unit width, unit height
        self.uwidth, self.uheight = uwidth, uheight

        if sprite_count is None:
            self.sprite_count = (self.swidth//self.uwidth)*(self.sheight//self.uheight)
        self.cycles = []
        self.strip = strip
        self.i = 0
        self.set_image(0)
        self.c = 0

    def add_cycle(self, name, frameids, timestops):
        l = list(zip(frameids, timestops))
        self.cycles[name] = l

    def set_cycle(self, name):
        if name not in self.cycles:
            raise IndexError
        self.cycle = self.cycles[name]
        self.c = 0
        self.i = 0

    def set_image(self, ind):
        # make image somehow be a view on the spritesheet at the location
        # self.image = 

    def update(self):
        self.set_image(self.cycle[self.i][0])
        if self.c % self.timestop == 0:
            self.i += 1
            self.timestop = self.cycle[self.i][1]
        if self.i % len(self.cycle) == 0:
            self.i = 0
        self.c += 1


def test():

    sprite_sheet = pygame.image.load("./resources/images/playerstrip.png")

    screen = pygame.display.set_mode((200, 200), pygame.RESIZABLE)

    swidth, sheight = sprite_sheet.get_size()

    spr_anim = Animation(sprite_sheet, swidth//10, sheight, 10)
    spr_anim.add_cycle("run", list(range(10)), [10]*10)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_q:
                    sys.exit()
                    pygame.quit()

        screen.blit(spr_anim.image, (0, 0))
        spr_anim.update()
        pygame.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    test()
