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

from component import *
# import sound
import kwargsGroup
from animation import SpriteComponent

import pygame
from pygame.locals import *

global resources
resources = {}


POSTMESSAGE = USEREVENT+1

# with open("./lf_constants.json", 'r') as fd:
#     constants = DotDict(json.load(fd))

# with open("./lf_keyconfig.json", 'r') as fd:
#     keyconfig = DotDict(json.load(fd))

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
        return Event('mousebuttondown', {})
    else:
        return Event("unknown", {})


class ScreenLocator(object):
    _screen = None

    @staticmethod
    def getScreen():
        return ScreenLocator._screen, ScreenLocator._camera

    @staticmethod
    def provide(screen, camera):
        ScreenLocator._screen = screen
        ScreenLocator._camera = camera


class PlayerEventHandler(EventHandler):
    def __init__(self, obj):
        super(PlayerEventHandler, self).__init__(obj)

        # reactions and everything in the code below manage events through this object
        self.obj.accelerating = False

        @Reaction
        def accel(**kwargs):
            return {"dv": constants.accel}

        @accel.defstart
        def accel(**kwargs):
            self.obj.dispatch_event(Event("change_gravity", {'g': constants.FLIGHTGRAVITY}))
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

        @Reaction
        def shoot(**kwargs):
            return {"dv": constants.bulletspeed}
        self.add_hold("fire", "shoot", shoot)


class Player(Object, pygame.sprite.Sprite):
    width, height = 16, 16

    def __init__(self, pos):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('sprite', SpriteComponent, get_resource("playerimage"), 64, 64)
        # where to attach the special behavior for the sprite logic.
        # here?
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    def __getattr__(self, name):
        if name == "pos" or name == "x" or name == "y":
            return getattr(self.get_component("position"), name)
        return super(Player, self).__getattr__(name)

    def update(self, **kwargs):
        screen, camera = ScreenLocator.getScreen()
        acenter = camera.apply(self.rect).center
        vec = self.get_component("physics").vector.components[:]
        vec[1] = -vec[1]
        pygame.draw.line(screen, (255, 0, 0),
                         acenter,
                         (Vector(l=acenter)+Vector(l=vec)).components)
        self.notify(Event("update", kwargs))

    @property
    def pos(self):
        return self.get_component('position').pos


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)
        self.startstate = Rect(0, 0, width, height)

    def apply(self, target):
        if isinstance(target, pygame.Rect):
            return target.move(self.state.topleft)
        elif isinstance(target, pygame.Surface):
            return target.get_rect().move(self.state.topleft)
        elif isinstance(target, pygame.sprite.Sprite):
            return target.rect.move(self.state.topleft)
        elif isinstance(target, list):
            return pygame.Rect((Vector(l=target) + Vector(l=self.state.topleft)).components, [0, 0])
        else:
            raise ValueError("target is not something that can be 'move'd")

    def update(self, target):
        self.state = self.camera_func(self.startstate, target)


def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+constants.HALF_WIDTH, -t+constants.HALF_HEIGHT, w, h)


def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+constants.LEVEL_WIDTH//2, -t+constants.LEVEL_HEIGHT//2, w, h

    l = min(0, l)                                       # stop scrolling at the left edge
    l = max(-(camera.width-constants.LEVEL_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-constants.LEVEL_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                                       # stop scrolling at the top
    return Rect(l, t, w, h)


def load_basic_resources(resources):
    """loads basic resources into ram"""
    print(dir(DotDict))
    with open("resources.json", 'r') as fd:
        _resources = DotDict(json.load(fd))
    print(dir(_resources.playerimage))
    for name, data in _resources.items():
        if data["type"] == constants.IMAGE:
            with open(data["path"], 'rb') as fd:
                resources[name] = pygame.image.load(fd)
        elif data["type"] in [constants.SFX, constants.MUSIC]:
            with open(data["path"], 'rb') as fd:
                resources[name] = sound.load(fd)


def get_resource(name):
    global resources
    return resources[name]


def do_prep():
    pygame.init()
    global resources
    load_basic_resources(resources)
    prep_screen(resources)
    prep_background(resources)
    prep_font(resources)


def prep_screen(resources):
    winstyle = 0
    bestdepth = pygame.display.mode_ok(constants.SCREEN_SIZE, winstyle, 32)
    screen = pygame.display.set_mode(constants.SCREEN_SIZE,
                                     winstyle, bestdepth)
    resources["screen"] = screen


def prep_background(resources):
    bg = get_resource("background1")
    truebg = pygame.Surface((constants.LEVEL_WIDTH, constants.LEVEL_HEIGHT)).convert()

    bg = pygame.transform.scale2x(bg)
    truebg.fill((255, 255, 255))
    truebg.blit(bg, (0, 0)) 

    pygame.draw.rect(truebg, (128, 128, 128), pygame.Rect(0, constants.LEVEL_HEIGHT-100, constants.LEVEL_WIDTH, 100))
    resources["truebg"] = truebg


def prep_font(resources):
    font = pygame.font.Font(None, 16) # 16 pt font
    resources["font"] = font

offset = 0
text_to_render = []


def render_text(text, color=(0, 0, 0)):
    global offset
    global text_to_render
    font = get_resource("font")
    size = font.size(text)
    h = size[1]
    size = pygame.Rect((0, offset), size)
    offset += h
    text = font.render(text, False, color)
    text_to_render.append((text, size))


def clear_text_buffer():
    global offset
    global text_to_render
    offset = 0
    text_to_render = []


def make_enemies(resources):
    w2, h2 = constants.SCREEN_WIDTH//2, constants.SCREEN_HEIGHT//2
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

    enemies = []
    for location in locations:
        enemies.append(Enemy(location))
    return enemies


def main():
    do_prep()
    dt = 1000/constants.FRAMERATE

    global resources

    screen = get_resource("screen")

    font = get_resource("font")

    # camera = Camera(simple_camera, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    camera = Camera(lambda camera, tr: Rect(0, 0, camera.width, camera.height),
                    constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

    truebg = get_resource("truebg")
    screen.blit(truebg, (0, 0), screen.get_rect())

    All = kwargsGroup.UserGroup()

    player = Player((50, constants.LEVEL_HEIGHT-50))

    camera.update(player.rect)
    All.add(player)

    ScreenLocator.provide(screen, camera)

    clock = pygame.time.Clock()
    pygame.display.update()  # update with no args is equivalent to flip

    print(player.image, player.rect, "player image and rect")
    try:
        while True:
            logging.debug("at top of main loop")
            events = pygame.event.get()
            for event in events:
                if event.type is QUIT:
                    print("got event quit")
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
                elif event.type is POSTMESSAGE:
                    render_text(event.info, event.color)

            pygame.event.pump()

            render_text(str(player.rect.topleft))

            screen.fill((255, 255, 255))

            screen.blit(truebg, (0, 0), camera.apply(screen.get_rect()))

            for text_surface, pos in text_to_render:
                screen.blit(text_surface, pos)

            camera.update(player.rect)

            All.update(dt=dt)

            for e in All:
                screen.blit(e.image, camera.apply(e))

            pygame.display.update()

            dt = clock.tick(constants.FRAMERATE)
            if dt > 16:
                dt = 16

            clear_text_buffer()
            logging.debug("at bottom of main loop\n")
    except NotImplementedError:
        for sprite in iter(All):
            sprite.dumpstate()
        raise

if __name__ == '__main__':
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()
