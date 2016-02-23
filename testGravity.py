#!/usr/bin/python

import sys
import os
import logging

from component import *
import constants
# import sound
import kwargsGroup

# import miscfunc

import pygame
from pygame.locals import *

VERSION = [0, 0, 0]
POSTMESSAGE = USEREVENT+1

logging.basicConfig(**constants.logging_setup)


def outputInfo(info, pos=None, color=(0, 0, 0)):
    pygame.event.post(pygame.event.Event(POSTMESSAGE,
                      {'info': info, 'pos': pos, 'color': color}))


class ScreenLocator(object):
    _screen = None

    def __init__(self):
        super(ScreenLocator, self).__init__()

    @staticmethod
    def getScreen():
        return ScreenLocator._screen

    @staticmethod
    def provide(screen):
        ScreenLocator._screen = screen


class GravityPhysics(PhysicsComponent):
    def __init__(self, obj):
        super(GravityPhysics, self).__init__(obj)

    def update(self, dt, **kwargs):
        # query for locations and masses of all other planets
        planets = kwargs['objects']
        # apply force based on that.
        F_x = constants.G_c*self.mass*sum([planet.mass/planet.x**2 for planet in planets])
        F_y = constants.G_c*self.mass*sum([planet.mass/planet.y**2 for planet in planets])

        


class Planet(Object):
    def __init__(self, pos):
        self.attach_component("position", Position)
        # self.attach_component("position", Position(self, pos))
        self.attach_component("gravityphysics", GravityPhysics)
        # self.attach_component("gravityphysics", GravityPhysics(self))

def main():
    # font = pygame.font.Font(None, 12)
    dt = 1000/constants.FRAMERATE
    winstyle = 0
    bestdepth = pygame.display.mode_ok(constants.SCREEN_SIZE, winstyle, 32)
    screen = pygame.display.set_mode(constants.SCREEN_SIZE,
                                     winstyle, bestdepth)
    ScreenLocator.provide(screen)

    bg = pygame.Surface((constants.SCREEN_WIDTH,
                        constants.SCREEN_HEIGHT)).convert()
    bg.fill((255, 255, 255))

    screen.blit(bg, (0, 0))

    all = kwargsGroup.UserGroup()

    locations = []

    pass

    for i in range(8):
        all.add(Enemy(locations[i]))

    clock = pygame.time.Clock()
    pygame.display.update()  # update with no args is equivalent to flip

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
                logging.info("notifying player of {event} from mainloop".format(
                             event=event))
                player.notify(event)
        all.clear(screen, bg)
        # screen.blit(bg, (0, 0))
        all.update(dt=dt)
        # all.update({"dt": dt})
        all.draw(screen)

        pygame.display.update()

        dt = clock.tick(constants.FRAMERATE)
        # assert dt < 100, dt
        # logging.info(str(dt)+' dt\n')d


if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()

