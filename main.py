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


class Bullet(Object):
    def __init__(self, pos, **kwargs):
        super(Bullet, self).__init__(pos)
        self.attach_component('position', PositionComponent, pos)
        if 'vector' in kwargs:
            vector = kwargs['vector']
            assert isinstance(vector, list)
            assert all(isinstance(elem, float) or isinstance(elem, int) for elem in vector)
        elif 'velocity' in kwargs:
            vector = [lengthdir_x(kwargs['velocity'][0], kwargs['velocity'][1]), lengthdir_y(kwargs['velocity'][0], kwargs['velocity'][1])]
        elif 'speed' in kwargs and 'direction' in kwargs:
            vector = [lengthdir_x(kwargs['speed'], kwargs['direction']), lengthdir_y(kwargs['speed'], kwargs['direction'])]
        self.attach_component('physics', PhysicsComponent, vector)
        self.attach_component('sprite', SimpleSprite)


class PlayerEventHandler(EventHandler):
    def __init__(self, obj):
        super(PlayerEventHandler, self).__init__(obj)

        # raise NotImplementedError

        def accel(**kwargs):
            return {"dv": constants.accel}
        self.add_hold("accel", "kick", accel)

        def turnleft(**kwargs):
            return {"d0": constants.turnspeed}
        self.add_hold("left", "turn", turnleft)

        def turnright(**kwargs):
            return {"d0": -constants.turnspeed}
        self.add_hold("right", "turn", turnright)


class Player(Object):
    width, height = 16, 16

    def __init__(self, pos):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('sprite', SpriteFromImage, (os.path.join(".", "resources", "images", "playerimage.png")))
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    def add_collision_check(self, group, **kwargs):
        proximity = kwargs.get('proximity', self.height+10)
        self.attach_component('proximity_{group.__class__.__name__}'.format(group=group), ProximitySensor, group, proximity)

    def update(self, **kwargs):
        # logging.debug('update in Player')
        dt = kwargs['dt']
        self.dispatch_event(Event("update", {"dt": dt}))
        vector = self['physics'].vector
        pdir = self['physics'].dir
        pygame.draw.line(ScreenLocator.getScreen(), (255, 0, 0), self.rect.center, [self.rect.center[0]+lengthdir_x(100, pdir), self.rect.center[1]+lengthdir_y(100, pdir)])
        pygame.draw.line(ScreenLocator.getScreen(), (0, 0, 255), self.rect.center, [self.rect.center[0]+vector[0], self.rect.center[1]+vector[1]])

    @property
    def pos(self):
        return self['position'].pos


class AIComponent(Component):
    def __init__(self, obj):
        super(AIComponent, self).__init__(obj)


class Enemy(Object):
    width, height = 16, 16

    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('image', SpriteFromImage, (os.path.join('.', 'resources', 'images', 'playerimage.png')))
        self.attach_component('ai', AIComponent)
        self['image'].image = pygame.transform.scale(self['image'].image, (self['image'].rect.width//2, self['image'].rect.height//2))
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    def update(self, **kwargs):
        dt = kwargs['dt']
        self.dispatch_event(Event("update", {"dt": dt}))


    @property
    def pos(self):
        return self['position'].pos


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

    w2, h2 = constants.SCREEN_WIDTH//2,constants.SCREEN_HEIGHT//2

    player = Player((w2, h2))

    all.add(player)

    locations = []

    # locations should be like this
    # *______________*______________*
    # |                             |
    # |                             |
    # |                             |
    # |                             |
    # *                             *
    # |                             |
    # |                             |
    # |                             |
    # *______________*______________*
    # thus
    for i in range(2):  # should be equivalent to for i in [0, 1, 2]:
        locations.append((i*w2, 0))
    locations.append((w2*2-16, 0))

    locations.append((0, h2))
    locations.append((w2*2-16, h2))

    for i in range(2):
        locations.append((i*w2, h2*2-16))

    locations.append((w2*2-16, h2*2-16))

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
        # all.clear(screen, bg)
        screen.blit(bg, (0, 0))
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
