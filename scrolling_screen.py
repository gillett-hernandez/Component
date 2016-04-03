#!/usr/bin/python

import sys
import logging

# import sound

# import miscfunc

import pygame
from pygame.locals import *


class Camera(object):
    def __init__(self):
        self.offset = [0, 0]

    def move(self, dx=0, dy=0):
        self.offset[0] += dx
        self.offset[1] += dy

    def set_camera_topleft(self, x, y):
        self.offset = [x, y]

    def apply(self, rect):
        return rect.move(self.offset[0], self.offset[1])


def main():
    # try:
    # font = pygame.font.Font(None, 12)
    winstyle = 0
    bestdepth = pygame.display.mode_ok((800, 600), winstyle, 32)
    screen = pygame.display.set_mode((800, 600),
                                     winstyle, bestdepth)

    bg = pygame.image.load("./resources/images/startBG.jpg").convert()
    bg = pygame.transform.scale2x(bg)

    screen.blit(bg, (0, 0))
    camera = Camera()

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
                    directions = {K_RIGHT: {"dx": 10},
                                  K_DOWN: {"dy": 10},
                                  K_UP: {"dy": -10},
                                  K_LEFT: {"dx": -10}}
                    if event.key in [K_RIGHT, K_LEFT, K_DOWN, K_UP]:
                        camera.move(**directions[event.key])

        # all.clear(screen, bg)
        screen.blit(bg, (0, 0), camera.apply(bg.get_rect()))

        pygame.display.update()

        # dt = clock.tick(60)
        clock.tick(60)


if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()
