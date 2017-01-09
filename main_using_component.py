#!/usr/bin/env python3

import sys
import math # lint:ok
import json  # lint:ok
from typing import *
import logging

from DotDict import DotDict
import config

with open("json/constants.json", 'r') as fd:
    constants = DotDict(json.load(fd))

with open("json/keyconfig.json", 'r') as fd:
    keyconfig = DotDict(json.load(fd))

config.supply("constants", constants)
config.supply("keyconfig", keyconfig)
logging.basicConfig(**constants.logging_setup)



import pygame
import json
import config

from pygame.locals import *

constants = config.get("constants")
keyconfig = config.get("keyconfig")
from vector import Vector
from component import Object, Event
POSTMESSAGE = USEREVENT + 1 # lint:ok

from DotDict import DotDict

global resources

from vector import Vector
from component import *
from components import *
import kwargsGroup

import pygame # lint:ok
from pygame.locals import * # lint:ok

logging.debug("start of logging file, platformer instance")


global resources
resources = {} # type: Dict[str,Any]
def outputInfo(info, pos=None, color=(0, 0, 0)):
    pygame.event.post(pygame.event.Event(POSTMESSAGE,
                      {'info': info, 'pos': pos, 'color': color}))


def translate_event(event):
    # print(pygame.event.event_name(event.type))
    """pure"""
    if event.type == pygame.KEYDOWN:
        return Event('keydown', {'key': event.key})
    elif event.type == pygame.KEYUP:
        return Event('keyup', {'key': event.key})
    elif event.type == pygame.MOUSEBUTTONDOWN:
        return Event('mousebuttondown', {})
    else:
        return Event("unknown", {})


def load_basic_resources(resources):
    """loads basic resources into ram"""
    with open("json/resources.json", 'r') as fd:
        _resources = DotDict(json.load(fd))
    for name, data in _resources.items():
        if data["type"] == constants.IMAGE:
            opentype = 'rb'
            function = pygame.image.load
        elif data["type"] in [constants.SFX, constants.MUSIC]:
            opentype = 'rb'
            function = sound.load
        elif data["type"] == constants.MAP:
            opentype = 'r'
            function = lambda fd: fd.read().splitlines()

        with open(data["path"], opentype) as fd:
            resources[name] = function(fd)


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
    truebg = pygame.Surface((constants.LEVEL_WIDTH,
                             constants.LEVEL_HEIGHT)).convert()

    # bg = pygame.transform.scale2x(bg)
    truebg.fill((255, 255, 255))
    truebg.blit(bg, (0, 0))

    resources["truebg"] = truebg


def prep_font(resources):
    font = pygame.font.Font(None, 16)  # 16 pt font
    resources["font"] = font


offset = 0
text_to_render = []


def render_text(text, color=(0, 0, 0)):
    global offset
    global text_to_render
    if not isinstance(text, str):
        text = str(text)
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


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        if isinstance(target, pygame.Rect):
            rect = target
            topleft = rect.topleft
            w, h = rect.size
        elif isinstance(target, pygame.Surface):
            rect = target.get_rect()
            topleft = rect.topleft
            w, h = rect.size
        elif isinstance(target, (pygame.sprite.Sprite, Object)):
            rect = target.rect
            topleft = rect.topleft
            w, h = rect.size
        elif isinstance(target, list):
            topleft = target
            w, h = 0, 0
        else:
            raise ValueError("target is not something that can be 'move'd")
        vector = (Vector(l=topleft) - Vector(l=self.state.topleft)).components
        rect = pygame.Rect(vector, (w, h))
        return rect

    def update(self, target):
        self.camera_func(self.state, target)
        outputInfo("state topleft = {}".format(self.state.topleft))
        outputInfo("adjusted = {}".format(Vector(l=self.state.center)-Vector(l=self.state.size)//2))
        # assert self.state.topleft == (Vector(l=self.state.center) - Vector(l=self.state.size)).components


def simple_camera(camera, target_rect):
    # l, t, w, h = target_rect
    # _, _, W, H = camera
    camera.center = target_rect.center
    # return Rect(-(l+w//2)+W//2, -(t+h//2)+H//2, W, H)


def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l+constants.LEVEL_WIDTH//2, -t+constants.LEVEL_HEIGHT//2

    l = min(0, l)                                        # stop scrolling at the left edge
    l = max(-(camera.width-constants.LEVEL_WIDTH), l)    # stop scrolling at the right edge
    t = max(-(camera.height-constants.LEVEL_HEIGHT), t)  # stop scrolling at the bottom
    t = min(0, t)
    return Rect(l, t, w, h)


def prep_map(resources):
    text_map = resources["map1"]
    assert all([all([isinstance(C, str) for C in row]) for row in text_map])

    translate_chara_table = {
        " ": (None, None),
        "B": (Block, None),
        "P": (Player, None),
        "E": (Enemy, None)
    }

    entities = []
    blocks = []
    enemies = []
    player = None
    scale = constants.SCALE
    for y, row in enumerate(text_map):
        for x, chara in enumerate(row):
            e = list(translate_chara_table[chara])
            if e[0] is not None:
                e[1] = (x * scale, constants.LEVEL_HEIGHT - y * scale)
                if e[0] is not Player:
                    entity = e[0](e[1])
                else:
                    player = e[1]
            else:
                continue
            if isinstance(entity, Enemy):
                enemies.append(entity)
                entities.append(entity)
            elif isinstance(entity, Block):
                blocks.append(entity)
                entities.append(entity)
    return player, blocks, enemies, entities


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

        # reactions and everything in the code below
        # manage events through this object

        # use @Reaction to specify something to be a reaction
        # e.g.
        # @Reaction
        # def accel(**kwargs):
        #     return {"dv": constants.accel}

        # @accel.defstart
        # def accel(**kwargs):
        #     self.obj.dispatch_event(Event("change_gravity",
        #                                   {'g': constants.FLIGHTGRAVITY}))
        #     self.obj.accelerating = True

        # @accel.defend
        # def accel(**kwargs):
        #     self.obj.dispatch_event(Event("change_gravity", {}))
        #     self.obj.accelerating = False
        #
        # self.add_hold("accelerate", "accel", accel)

        @Reaction
        def jump(**kwargs):
            # kinda direct, huh.
            self.obj["physics"].vector[1] = 0
            self.logger.debug("reaction jump called")
            return {"dv": [0, constants.JUMPSPEED]}

        self.add_tap("up", "kick", jump)

        # Reaction
        # def left(**kwargs):
        #     return {"dv": -constants.runaccel}

        left = Reaction(void)
        left.defhold({"dv": -constants.runaccel})
        self.add_hold("left", "run", left)

        # @Reaction
        # def right(**kwargs):
        #     return {"dv": constants.runaccel}

        right = Reaction(void)
        right.defhold({"dv": constants.runaccel})

        self.add_hold("right", "run", right)


class Player(Object, pygame.sprite.Sprite):
    width, height = 16, 32

    def __init__(self, pos, walls):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('sprite', SimpleSprite, size=(16, 32),
                              color=(255, 128, 128))
        self.attach_component('proximity', ProximitySensor, walls, 30)

    @staticmethod
    def render_text(text):
        outputInfo(text)

    def __getattr__(self, name):
        if name == "pos" or name == "x" or name == "y":
            return getattr(self["position"], name)
        return super(Player, self).__getattr__(name)

    def update(self, **kwargs):
        screen, camera = ScreenLocator.getScreen()
        acenter = camera.apply(self.rect).center
        vec = self["physics"].vector.components[:]
        vec[1] = -vec[1]
        pygame.draw.line(screen, (255, 0, 0),
                         acenter,
                         (Vector(l=acenter)+Vector(l=vec)).components)
        self.notify("update", **kwargs)

    # def add_collision_check(self, group, **kwargs):
    #     proximity = kwargs.get('proximity', self.height+10)
    #     self.attach_component('proximity_{group.__class__.__name__}'.format(group=group),
    #                           ProximitySensor, group, proximity)

    @property
    def pos(self):
        return self['position'].pos


class Enemy(Object, pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('handler', EnemyEventHandler)
        self.attach_component('sprite', SimpleSprite, size=(16, 32), color=(128, 128, 128))


class Block(Object, pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Block, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        # self.attach_component('handler', EnemyEventHandler)
        self.attach_component('sprite', SimpleSprite, size=(16, 16), color=(128, 128, 128))
        self.notify("update", dt=0)

    def update(self, **kwargs):
        pass


def main():
    do_prep()
    dt = 1000/constants.FRAMERATE

    global resources

    screen = get_resource("screen")

    screenrect = screen.get_rect()

    camera = Camera(simple_camera, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

    truebg = get_resource("truebg")
    bgrect = truebg.get_rect()
    screen.blit(truebg, (0, 0), screenrect)
    _screenrect = screenrect.copy()

    # strangely calling a prep_* function separately from all the other ones.
    # fix?
    playercoor, blocks, enemies, entities = prep_map(resources)

    All = kwargsGroup.UserGroup()
    Walls = pygame.sprite.Group()

    # player = Player((500, constants.LEVEL_HEIGHT-500))
    # player.notify(Event("toggle_gravity", {}))

    for obj in blocks:
        All.add(obj)
        Walls.add(obj)
    player = Player(playercoor, Walls)
    All.add(player)

    camera.update(player.rect)
    ScreenLocator.provide(screen, camera)

    clock = pygame.time.Clock()
    pygame.display.update()  # update with no args is equivalent to flip

    # print(player.image, player.rect, "player image and rect")
    try:
        while True:
            logging.debug("at top of main loop")
            events = pygame.event.get()
            for event in events:
                if event.type is QUIT:
                    # print("got event quit")
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
                    if event.type is MOUSEBUTTONDOWN:
                        player.notify(Event("move", {"dr": [-constants.SCREEN_WIDTH//2 + event.pos[0], constants.SCREEN_HEIGHT//2 - event.pos[1]]}))
                elif event.type is POSTMESSAGE:
                    render_text(event.info, event.color)

            pygame.event.pump()

            render_text("player rect topleft = {}".format(player.rect.topleft))
            render_text("transformed = {}".format(camera.apply(player.rect)))
            render_text("bg topleft transformed = {}".format(camera.apply(screenrect)))
            render_text("framerate: {}".format(round(1000/dt,1)))

            screen.fill((255, 255, 255))

            new_pos = camera.apply(screenrect)

            x = new_pos.topleft[0]
            y = new_pos.topleft[1]
            pos = max(0, x), max(0, y)
            topleft = max(0, -x), max(0, -y)
            _screenrect.topleft = topleft
            _area = _screenrect.clip(bgrect)
            screen.blit(truebg, pos, _area)

            for text_surface, pos in text_to_render:
                screen.blit(text_surface, pos)

            camera.update(player.rect)

            All.update(dt=dt)  # contained in here is player.update

            for e in All:
                screen.blit(e.image, camera.apply(e))

            pygame.display.update()

            dt = clock.tick(constants.FRAMERATE)

            clear_text_buffer()
            logging.debug("at bottom of main loop\n")
    except:
        raise
    finally:
        logging.debug("--------------------------------------------------------------------------------")
        logging.debug("START OF DUMPSTATE")
        for sprite in iter(All):
            try:
                sprite.dumpstate()
            except:
                pass

if __name__ == '__main__':
    try:
        main()
    finally:
        logging.info("END\n")
        pygame.quit()
