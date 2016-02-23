#!/usr/bin/python

import sys
import os
import logging

from composite import *
import constants
# import sound
import kwargsGroup

# import miscfunc

import pygame
from pygame.locals import *



def main():
    # try:
    # font = pygame.font.Font(None, 12)
    winstyle = 0
    bestdepth = pygame.display.mode_ok((10000, 6000), winstyle, 32)
    screen = pygame.display.set_mode((10000, 6000),
                                     winstyle, bestdepth)

    screen = screen.subsurface(pygame.Rect((0, 0), constants.SCREEN_SIZE))

    bg = pygame.Surface((constants.SCREEN_WIDTH,
                        constants.SCREEN_HEIGHT)).convert()
    bg.fill((255, 255, 255))

    screen.blit(bg, (0, 0))

    clock = pygame.time.Clock()
    pygame.display.update()  # update with no args is equivalent to flip

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type is QUIT:
                logging.info('event QUIT')
                sys.exit(0)
                return
            elif event.type in [KEYDOWN, KEYUP,
                                MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                if event.type is KEYDOWN:
                    if event.key in [K_ESCAPE, K_q]:
                        logging.info('event K_ESCAPE')
                        sys.exit(0)
                        return
                    elif event.key is K_RIGHT:
                        screen.scroll(dx=100)
                    elif event.key is K_DOWN:
                        screen.scroll(dy=100)

        # all.clear(screen, bg)
        screen.blit(bg, (0, 0))

        pygame.display.update()

        dt = clock.tick(constants.FRAMERATE)
        # assert dt < 100, dt
        # logging.info(str(dt)+' dt\n')d
    # except Exception as e:
        # for sprite in iter(all):
            # sprite.dumpstate()
        # raise e


if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()
