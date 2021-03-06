#!/usr/bin/env python

import sys
# import os
import json
import logging

from component import *
# import sound
import kwargsGroup

import pygame
from pygame.locals import *


class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item


with open("./constants.json", 'r') as fd:
    constants = DotDict(json.load(fd))

with open("./keyconfig.json", 'r') as fd:
    keyconfig = DotDict(json.load(fd))

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

        def jump(**kwargs):
            return {"dv_y": yvel_to_jump(kwargs["jumpspeed"])}
        self.add_tap("jump", "kick", jump)
        # when you press jump, you should jump just once.

        def left(**kwargs):
            return {"dv_x": -constants.runspeed/constants.runaccel}
        self.add_hold("left", "kick", left)
        # when you press left it should kick you left,
        # and repeated presses increase leftspeed

        def right(**kwargs):
            return {"dv_x": constants.runspeed/constants.runaccel}
        self.add_hold("right", "kick", right)
        # when you press right, you should accellerate to the right
        # until you release right.

        # self.add_handler("", "")


class Player(Object):
    width, height = 16, 32

    def __init__(self, pos):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('image', SimpleSprite, (self.width, self.height))
        self.mask = pygame.mask.from_surface(self.image)
        self.mask.fill()
        assert self.mask.count() > 0

    def add_collision_check(self, group, **kwargs):
        proximity = kwargs.get('proximity', self.height+10)
        self.attach_component('proximity_{group.__class__.__name__}'.format(group=group), ProximitySensor, group, proximity)

    def update(self, **kwargs):
        # logging.debug('update in Player')
        dt = kwargs['dt']
        self.dispatch_event(Event("update", {"dt": dt}))

    @property
    def pos(self):
        return self['position'].pos


class Block(Object):
    width, height = 16, 16

    def __init__(self, pos):
        super(Block, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('image', SimpleSprite, (self.width, self.height))
        print(self.image.get_at((8, 8)))
        self.mask = pygame.mask.from_surface(self.image)
        self.mask.fill()
        print(self.mask.get_at((8, 8)))
        assert self.mask.count() > 0

    update = void


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

    with open("./resources/maps/map1.txt", 'r') as mapfile:
        levelmap = mapfile.read().split("\n")

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

    bw = Block.width
    bh = Block.height
    print(bw, bh)
    all = kwargsGroup.UserGroup()
    wall = kwargsGroup.UserGroup()

    for y, line in enumerate(levelmap):
        # print(y, line)
        for x, char in enumerate(line):
            # print(x)
            if char == 'W':
                wall.add(Block([x*bw, y*bh]))
            elif char == 'P':
                playerpos = [x*bw, y*bh]

    player = Player(playerpos)
    player.add_collision_check(wall)

    all.add(player)
    all.add(wall.sprites())

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

                if event.type is KEYDOWN:
                    if event.key in [K_ESCAPE, K_q]:
                        logging.info('event K_ESCAPE')
                        sys.exit(0)
                        return
                    else:
                        logging.info("notifying player of {event} from mainloop".format(
                                     event=event))
                        player.notify(event)

        all.clear(screen, bg)
        screen.blit(bg, (0, 0))

        all.update(dt=dt)

        all.draw(screen)

        pygame.display.update()

        dt = clock.tick(constants.FRAMERATE)
        if dt > 34:
            dt = 34
        # logging.info(str(dt)+' dt\n')d

if __name__ == '__main__':
    pygame.init()
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()
