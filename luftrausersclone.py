#!/usr/bin/python
# all ideas regarding top level game features are from the game Luftrausers and were not created by me.
# TODO LIST:
# |-> fix broken acceleration
# |
# |-> add altered turn speed when boosting
# |
# |-> add swappable engine parts
# |
# |-> add slight graphical acceleration effect
# |  |
# |  -> find a way to display graphical effects. try the pygame.gfxdraw or pygame.draw modules
# |-> scrolling screen effects
# |-> fix water and cloud level
# |-> make it so the coordinates are all based on the level locations, not the screen's.
# --> swappable engine parts

import sys
import os
import logging

from composite import *
import luftrausers_constants as constants
import sound
import kwargsGroup

from .. import miscfunc

import pygame
from pygame.locals import *

POSTMESSAGE = USEREVENT+1


logging.basicConfig(**constants.logging_setup)


def add_info(info, pos, color):
    pygame.event.post(pygame.event.Event(POSTMESSAGE,
                      {'info': info, 'pos': pos, 'color': color}))


def translate_event(event):
    """pure"""
    if event.type == pygame.KEYDOWN:
        return Event('keydown', {'key': event.key})
    elif event.type == pygame.KEYUP:
        return Event('keyup', {'key': event.key})
    elif event.type == pygame.MOUSEBUTTONDOWN:
        return Event('mousebuttondown', {'key': event.key})
    elif event.type == pygame.MOUSEBUTTONUP:
        return Event('mousebuttonup', {'key': event.key})
    return None


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


class Bullet(Composite):
    def __init__(self, pos, **kwargs):
        super(Bullet, self).__init__(pos)
        self.attach_component('position', PositionComponent, pos)
        if 'vector' in kwargs:
            vector = kwargs['vector']
            assert isinstance(vector, list), "vector is "+str(vector)
            assert all(isinstance(elem, (float, int)) for elem in vector)
        elif 'velocity' in kwargs:
            vector = [lengthdir_x(kwargs['velocity'][0], kwargs['velocity'][1]),
                      lengthdir_y(kwargs['velocity'][0], kwargs['velocity'][1])]
        elif 'speed' in kwargs and 'direction' in kwargs:
            vector = [lengthdir_x(kwargs['speed'], kwargs['direction']), lengthdir_y(kwargs['speed'], kwargs['direction'])]
        self.attach_component('physics', PhysicsComponent, vector)
        self.attach_component('sprite', SimpleSprite)


class PlayerEventHandler(EventHandler):
    def __init__(self, obj):
        super(PlayerEventHandler, self).__init__(obj)

        # raise NotImplementedError
        self.obj.accelerating = False

        @Reaction
        def accel(**kwargs):
            # print("gravity is {g}".format(g=self.obj.get_component("physics").gravity))
            # if distance(self.obj.get_component("physics").vector)>constants.maxspeed:
                # if not vproj(self.obj.get_component("physics").vector, miscfunc.vector_transform(constants.accel, self.obj.get_component("physics").dir))<0:
                    # return {"dv": 0}
            return {"dv": constants.accel}

        @accel.def_start
        def startaccel(**kwargs):
            self.obj.dispatch_event(Event("change_gravity", {'g':constants.GRAVITY/8.}))
            self.obj.accelerating = True

        @accel.def_end
        def endaccel(**kwargs):
            self.obj.dispatch_event(Event("change_gravity", {'g':constants.GRAVITY}))
            self.obj.accelerating = False

        self.add_hold("accelerate", "accel", accel)

        @Reaction
        def turnleft(**kwargs):
            if self.obj.accelerating:
                return {"d0":constants.accelturnspeed}
            return {"d0": constants.turnspeed}
        print(turnleft.start)
        self.add_hold("left", "turn", turnleft)

        @Reaction
        def turnright(**kwargs):
            if self.obj.accelerating:
                return {"d0":-constants.accelturnspeed}
            return {"d0": -constants.turnspeed}
        self.add_hold("right", "turn", turnright)

        def shoot(**kwargs):
            return {"dv": constants.bulletspeed}


class Player(Composite, pygame.sprite.Sprite):
    width, height = 16, 16

    def __init__(self, pos):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('input', InputHandler)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('sprite', SpriteFromImage,
                              (os.path.join(".",
                                            "resources",
                                            "images",
                                            "playerimage.png")))
        # where to attach the special behavior for the sprite logic.
        # here? nvm, just use multi-inheritance
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    def __getattr__(self, name):
        if name == "pos" or name == "x" or name == "y":
            return getattr(self.get_component("position"), name)
        return super(Player, self).__getattr__(name)

    def add_collision_check(self, group, **kwargs):
        proximity = kwargs.get('proximity', self.height+10)
        self.attach_component('proximity_{group.__class__.__name__}'.format(group=group),
                              ProximitySensor, group, proximity)

    def update(self, **kwargs):
        logging.debug('update in Player')
        dt = kwargs['dt']
        # print("gravity is {g}".format(g=self.get_component("physics").gravity))
        self.dispatch_event(Event("update", {"dt": dt}))
        vector = self.get_component('physics').vector
        # print("velocity", distance(vector))
        pdir = self.get_component('physics').dir
        print("vector, grav, accel", vector, self.get_component("physics").gravity, self.accelerating)
        rc = self.rect.center
        pygame.draw.line(self.image, (255, 0, 0), rc, [rc[0]+lengthdir_x(100, pdir), rc[1]+lengthdir_y(100, pdir)])
        pygame.draw.line(self.image, (0, 0, 255), rc, [rc[0]+vector[0], rc[1]+vector[1]])

        logging.debug('end update in Player\n ')

    @property
    def pos(self):
        return self.get_component('position').pos


class AIComponent(Component):
    def __init__(self, obj):
        super(AIComponent, self).__init__(obj)
        self.attach_event("update", self.update)

    def update(self, dt):
        # raise NotImplementedError
        # playerangle = direction(self, player)
        # self.turn()  # find player and turn towards him
        # if abs(self.dir-direction(self, player)) < 10:
            # self.accel()  # accel toward player.
        pass


class Enemy(Composite, pygame.sprite.Sprite):
    width, height = 16, 16

    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('image', SpriteFromImage, (os.path.join('.', 'resources', 'images', 'playerimage.png')))
        self.attach_component('ai', AIComponent)
        # self.get_component('image').image = pygame.transform.scale(self.get_component('image').image, (self.get_component('image').rect.width//4*3, self.get_component('image').rect.height))
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    def __getattr__(self, name):
        return getattr(self.spriteref, name)

    def update(self, **kwargs):
        dt = kwargs['dt']
        self.dispatch_event(Event("update", {"dt": dt}))

    @property
    def pos(self):
        return self.get_component('position').pos


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        try:
            rect = target.rect
        except AttributeError:
            rect = target.get_rect()
        assert rect is not None, target
        return rect.move(self.state.topleft)

    def update(self, target):
        # self.state = self.camera_func(self.state,
                                        # (target.rect if not isinstance(target, pygame.Rect) else target))

        self.state = self.camera_func(self, target.rect)


def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera.state
    return Rect(-l+constants.HALF_WIDTH, -t+constants.HALF_HEIGHT, w, h)


def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera.state
    l, t, _, _ = -l+constants.HALF_WIDTH, -t+constants.HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-constants.SCREEN_WIDTH), l)  # stop scrolling at the right edge
    t = max(-(camera.height-constants.SCREEN_HEIGHT), t)  # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)


def main():
    # try:
    # font = pygame.font.Font(None, 12)
    dt = 1000/constants.FRAMERATE
    winstyle = 0
    bestdepth = pygame.display.mode_ok(constants.SCREEN_SIZE, winstyle, 32)
    screen = pygame.display.set_mode(constants.SCREEN_SIZE,
                                     winstyle, bestdepth)
    ScreenLocator.provide(screen)

    level = pygame.Surface((constants.LEVEL_WIDTH,
                            constants.LEVEL_HEIGHT)).convert()
    level.fill((255, 255, 255))
    pygame.draw.rect(level, (128, 128, 128), pygame.Rect(0, constants.LEVEL_HEIGHT-100, constants.LEVEL_WIDTH, 100))

    screen.blit(level, (0, 0))

    all = kwargsGroup.UserGroup()

    w2, h2 = constants.SCREEN_WIDTH//2, constants.SCREEN_HEIGHT//2

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
    locations.append((0, 0))
    locations.append((w2, 0))
    locations.append((w2*2-16, 0))

    locations.append((0, h2))
    locations.append((w2*2-16, h2))

    locations.append((0, h2*2-16))
    locations.append((w2, h2*2-16))
    locations.append((w2*2-16, h2*2-16))

    all.add([Enemy(locations[i]) for i in range(len(locations))])

    camera = Camera(simple_camera, constants.SCREEN_WIDTH//2, constants.SCREEN_HEIGHT//2)

    # camera = pygame.Rect(0,0,constants.SCREEN_WIDTH//2, constants.SCREEN_HEIGHT//2)

    clock = pygame.time.Clock()
    pygame.display.update()  # update with no args is equivalent to flip

    print(player.image, player.rect, "player image and rect")
    while True:
        events = pygame.event.get([QUIT, KEYDOWN, KEYUP])
        for event in events:
            if event.type is QUIT:
                logging.info('event QUIT')
                print(Event("None", {'': None}).datatypes)
                sys.exit(0)

                return
            elif event.type in [KEYDOWN, KEYUP,
                                MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
                if event.type is KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                    logging.info('event K_ESCAPE')
                    print(Event("None", {'': None}).datatypes)
                    sys.exit(0)
                    return
                logging.info("notifying player of {event} from mainloop".format(
                             event=event))
                player.notify(translate_event(event))
        pygame.event.pump()
        # all.clear(screen, level)
        screen.fill((255, 255, 255))

        camera.update(player)

        screen.blit(level, camera.apply(level))  # blit the entire level at pos 0,0
        # screen.blit(level, (0, 0))  # blit the entire level at pos 0,0
        all.update(dt=dt)
        # screen.blit(level, level.get_rect(topleft=camera.state.topleft))
        # screen.blit(level, level.get_rect(center=(0,0)))
        # all.draw()

        for e in all:
            screen.blit(e.image, camera.apply(e))  # blit the entities' image after getting translated by the camera

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
