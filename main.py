#!/usr/bin/python

import sys
# import os
import logging

import component
import constants
# import sound
# import miscfunc

import pygame
from pygame.locals import *

VERSION = [0, 0, 0]
POSTMESSAGE = USEREVENT+1

logging.basicConfig(**constants.logging_setup)


def outputInfo(info, pos=None, color=(0, 0, 0)):
    pygame.event.post(pygame.event.Event(POSTMESSAGE,
                      {'info': info, 'pos': pos, 'color': color}))


def main():
    # font = pygame.font.Font(None, 12)
    SCREENSIZE = WIDTH, HEIGHT = 800, 640
    FRAMERATE = 60
    dt = 1./FRAMERATE
    winstyle = 0
    bestdepth = pygame.display.mode_ok(SCREENSIZE, winstyle, 32)
    screen = pygame.display.set_mode(SCREENSIZE, winstyle, bestdepth)
    clock = pygame.time.Clock()

    black = pygame.Color("Black")

    all = pygame.sprite.RenderPlain()

    player = component.Player([WIDTH//2, HEIGHT//2])

    all.add(player)

    bg = pygame.Surface((WIDTH, HEIGHT)).convert()
    bg.fill(black)

    screen.blit(bg, (0, 0))
    pygame.display.update()

    print(player.image, player.rect, "player image and rect")
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type is QUIT:
                logging.info('event QUIT')
                sys.exit(0)
                return
            elif event.type in [KEYDOWN, KEYUP,
                                MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                if event.type is KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                    logging.info('event K_ESCAPE')
                    sys.exit(0)
                    return
                logging.info("notify %s from mainloop" % event)
                player.notify(event)
        all.clear(screen, bg)
        # all.update(dt=dt)
        all.update({"dt": dt})
        print(player.rect, 'rect')
        all.draw(screen)

        pygame.display.update()

        dt = clock.tick(FRAMERATE)/1000.
        print(dt, 'dt')


if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()
