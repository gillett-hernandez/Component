#!/usr/bin/python

# TODO LIST:
# |-> fix broken acceleration
# |
# |-> add altered turn speed when boosting
# |
# |-> add slight graphical acceleration effect
# |  |
# |  -> find a way to display graphical effects. try the pygame.gfxdraw or pygame.draw modules
# |-> scrolling screen effects
# --> swappable engine parts

import sys
import os
import logging
import math

from composite import *
# import sound
import kwargsGroup
import pygame
from pygame.locals import *

POSTMESSAGE = USEREVENT+1

class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item


with open("./lf_constants.json", 'r') as fd:
    constants = DotDict(json.load(fd))

with open("./lf_keyconfig.json", 'r') as fd:
    keyconfig = DotDict(json.load(fd))

logging.basicConfig(**constants.logging_setup)


def outputInfo(info, pos=None, color=(0, 0, 0)):
    pygame.event.post(pygame.event.Event(POSTMESSAGE,
                      {'info': info, 'pos': pos, 'color': color}))


def translate_event(event):
    # print(pygame.event.event_name(event.type))
    if event.type == pygame.KEYDOWN:
        return Event('keydown', {'key': event.key})
    elif event.type == pygame.KEYUP:
        return Event('keyup', {'key': event.key})
    elif event.type == pygame.MOUSEBUTTONDOWN:
        return Event('mousebuttondown', {'key': event.key})


class ScreenLocator(object):
    _screen = None

    def __init__(self):
        super(ScreenLocator, self).__init__()

    @staticmethod
    def getScreen():
        return ScreenLocator._screen, ScreenLocator._camera

    @staticmethod
    def provide(screen, camera):
        ScreenLocator._screen = screen
        ScreenLocator._camera = camera


class Bullet(Composite):
    def __init__(self, pos, **kwargs):
        super(Bullet, self).__init__(pos)
        self.attach_component('position', PositionComponent, pos)
        if 'vector' in kwargs:
            vector = kwargs['vector']
            assert isinstance(vector, list), "vector is "+str(vector)
            assert all(isinstance(elem, (float, int)) for elem in vector)
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
        self.obj.accelerating = False

        @Reaction
        def accel(**kwargs):
            # print("gravity is {g}".format(g=self.obj.get_component("physics").gravity))
            # if distance(self.obj.get_component("physics").vector)>constants.maxspeed:
                # if not vproj(self.obj.get_component("physics").vector, miscfunc.vector_transform(constants.accel, self.obj.get_component("physics").dir))<0:
                    # return {"dv": 0}
            return {"dv": constants.accel}

        @accel.defstart
        def accel(**kwargs):
            self.obj.dispatch_event(Event("change_gravity", {'g': constants.GRAVITY/8.}))
            self.obj.accelerating = True

        @accel.defend
        def accel(**kwargs):
            self.obj.dispatch_event(Event("change_gravity", {}))
            self.obj.accelerating = False

        self.add_hold("accelerate", "accel", accel)

        @Reaction
        def turnleft(**kwargs):
            if self.obj.accelerating:
                return {"d0": constants.accelturnspeed}
            return {"d0": constants.turnspeed}
        print(turnleft.start)
        self.add_hold("left", "turn", turnleft)

        @Reaction
        def turnright(**kwargs):
            if self.obj.accelerating:
                return {"d0": -constants.accelturnspeed}
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
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('sprite', SpriteFromImage,
                              (os.path.join(".",
                                            "resources",
                                            "images",
                                            "playerimage.png")))
        # where to attach the special behavior for the sprite logic.
        # here?
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    def __getattr__(self, name):
        if name == "pos" or name == "x" or name == "y":
            return getattr(self.get_component("position"), name)
        return super(Player, self).__getattr__(name)

    def add_collision_check(self, group, **kwargs):
        proximity = kwargs.get('proximity', self.height+10)
        self.attach_component('proximity_{group.__class__.__name__}'.format(group=group), ProximitySensor, group, proximity)

    def update(self, **kwargs):
        logging.debug('update in Player')
        dt = kwargs['dt']
        self.dispatch_event(Event("update", {"dt": dt}))
        vector = self.get_component('physics').vector
        pdir = self.get_component('physics').dir
        logging.debug('vga', vector, self.get_component("physics").gravity, self.accelerating)
        screen, camera = ScreenLocator.getScreen()
        altered_center = camera.apply(self.rect).center
        selfcenter_plus_100_len_vector = [self.rect.center[0]+lengthdir_x([100, pdir]), self.rect.center[1]+lengthdir_y([100, pdir])]
        selfcenter_plus_current_vector = [self.rect.center[0]+vector[0], self.rect.center[1]+vector[1]]

        pygame.draw.line(screen, (255, 0, 0), altered_center, camera.apply(selfcenter_plus_100_len_vector).topleft)
        pygame.draw.line(screen, (0, 0, 255), altered_center, camera.apply(selfcenter_plus_current_vector).topleft)

    @property
    def pos(self):
        return self.get_component('position').pos


class AIComponent(Component):
    def __init__(self, obj):
        super(AIComponent, self).__init__(obj)


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
        return getattr(self.spriteref,name)

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
        if isinstance(target, pygame.Rect):
            return target.move(self.state.topleft)
        elif isinstance(target, pygame.Surface):
            return target.get_rect().move(self.state.topleft)
        elif isinstance(target, pygame.sprite.Sprite):
            return target.rect.move(self.state.topleft)
        elif isinstance(target, list):
            return pygame.Rect(vadd(target, self.state.topleft),[0,0])
        else:
            raise ValueError("target is not something that can be 'move'd")

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+constants.HALF_WIDTH, -t+constants.HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+constants.HALF_WIDTH, -t+constants.HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-constants.SCREEN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-constants.SCREEN_HEIGHT), t) # stop scrolling at the bottom
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

    bg = pygame.Surface((constants.SCREEN_WIDTH,
                        constants.SCREEN_HEIGHT)).convert()
    bg.fill((255, 255, 255))
    pygame.draw.rect(bg, (128, 128, 128), pygame.Rect(0, constants.SCREEN_HEIGHT-100, constants.SCREEN_WIDTH, 100))

    screen.blit(bg, (0, 0))

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

    ScreenLocator.provide(screen, camera)
    # camera = pygame.Rect(0,0,constants.SCREEN_WIDTH//2, constants.SCREEN_HEIGHT//2)

    clock = pygame.time.Clock()
    pygame.display.update()  # update with no args is equivalent to flip

    print(player.image, player.rect, "player image and rect")
    while True:
        events = pygame.event.get([QUIT, KEYDOWN, KEYUP])
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
                player.notify(translate_event(event))
        pygame.event.pump()
        # all.clear(screen, bg)
        screen.fill((255,255,255))
        # screen.blit(bg, (0, 0))

        camera.update(player)
        # screen.blit(bg, camera.camera_func(camera.state, bg.get_rect(topleft=(0,0))))
        all.update(dt=dt)
        screen.blit(bg, bg.get_rect(topleft=camera.state.topleft))
        # screen.blit(bg, bg.get_rect(center=(0,0)))
        # all.draw()
        for e in all:
            screen.blit(e.image, camera.apply(e))

        # if screen.

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
