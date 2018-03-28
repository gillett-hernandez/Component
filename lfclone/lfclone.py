#!/usr/bin/python

import sys
import os
import logging
import math

from ..component import load_stuff
load_stuff(__file__)
from ..component import *
from ..components import *
# import sound
import Component.kwargsGroup as kwargsGroup
from ..animation import SpriteComponent
import Component.versionnumber as versionnumber

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
    path, base, ext = versionnumber.split(__file__)
    with open(os.path.join(path,"json","resources.json"), 'r') as fd:
        _resources = DotDict(json.load(fd))
    for name, data in _resources.items():
        if data["type"] == constants.IMAGE:
            with open(data["path"].replace(".",path,1), 'rb') as fd:
                resources[name] = pygame.image.load(fd)
        elif data["type"] in [constants.SFX, constants.MUSIC]:
            with open(data["path"].replace(".",path,1), 'rb') as fd:
                resources[name] = sound.load(fd)


def get_resource(name):
    global resources
    return resources[name]


def do_prep():
    pygame.init()
    print(versionnumber.render_version(__file__))
    logging.info(versionnumber.render_version(__file__))
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

    pygame.draw.rect(truebg, (128, 128, 128), pygame.Rect(0, constants.LEVEL_HEIGHT-constants.WATER_LEVEL, constants.LEVEL_WIDTH, 100))
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
    # all.add([Enemy(locations[i]) for i in range(len(locations))])
    return enemies


class ScreenLocator(object):
    _screen = None

    @staticmethod
    def getScreen():
        return ScreenLocator._screen, ScreenLocator._camera

    @staticmethod
    def provide(screen, camera):
        ScreenLocator._screen = screen
        ScreenLocator._camera = camera


# class Bullet(Composite):
#     def __init__(self, pos, **kwargs):
#         super(Bullet, self).__init__(pos)
#         self.attach_component('position', PositionComponent, pos)
#         if 'vector' in kwargs:
#             vector = kwargs['vector']
#             assert isinstance(vector, list), "vector is "+str(vector)
#             assert all(isinstance(elem, (float, int)) for elem in vector)
#         elif 'velocity' in kwargs:
#             vector = [lengthdir_x(kwargs['velocity'][0], kwargs['velocity'][1]),
#                       lengthdir_y(kwargs['velocity'][0], kwargs['velocity'][1])]
#         elif 'speed' in kwargs and 'direction' in kwargs:
#             vector = [lengthdir_x(kwargs['speed'], kwargs['direction']), lengthdir_y(kwargs['speed'], kwargs['direction'])]
#         self.attach_component('physics', PhysicsComponent, vector)
#         self.attach_component('sprite', SimpleSprite)

class PlayerPhysicsComponent(PhysicsComponent):
    def __init__(self, obj, **kwargs):
        super(PlayerPhysicsComponent, self).__init__(obj)

    def bounce_horizontal(self):
        self.vector[0] *= -1

    def bounce_vertical(self):
        self.vector[1] *= -1

    def outside_vertical(self, side="UP"):
        dir = self.dir
        value = constants.EJECT_TURN_SPEED
        flag = ["DOWN","UP"].index(side.upper())
        self.change_gravity((2*flag-1)*constants.GRAVITY*3)
        # four cases
        # aimed left and high, aimed right and high
        # aimed left and low, aimed right and low
        cos = math.cos(math.radians(dir))
        if flag: # if up
            if cos < -0.1:
                self.obj.dispatch_event(Event("turn", {"d0":value}))
            elif cos > 0.1:
                self.obj.dispatch_event(Event("turn", {"d0":-value}))
        else: # if down
            if cos < -0.1:
                self.obj.dispatch_event(Event("turn", {"d0":-value}))
            elif cos > 0.1:
                self.obj.dispatch_event(Event("turn", {"d0":value}))

    def outside_horizontal(self):
        # self.p.reset()
        # self.vector = Vector(0, 0)
        self.bounce_horizontal()

    def update(self, **kwargs):
        logging.debug("top of physics update call")
        dt = kwargs['dt']
        x, y = self.p.pos
        # logging.debug("physics xy: {}".format((x, y)))
        # logging.debug("gravity   : {}".format(self.gravity))
        # logging.debug("vector    : {}".format(self.vector))
        # logging.debug("dir       : {}".format(self.dir))
        self.obj.render_text("x, y = ({:3.1f}, {:3.1f})".format(x, y))
        self.obj.render_text("gravity = {0.gravity}".format(self))
        self.obj.render_text("vector = ({self.vector[0]:3.1f}, {self.vector[1]:3.1f})".format(self=self))
        self.obj.render_text("direction = {0.dir}".format(self))
        if y-32 < constants.WATER_LEVEL:
            # print("outside bottom")
            self.outside_vertical(side="DOWN")
        elif y-32 > constants.LEVEL_HEIGHT:
            # print("outside top")
            self.outside_vertical(side="UP")
        else:
            if not self.obj.accelerating:
                self.change_gravity()
            else:
                self.change_gravity(constants.FLIGHTGRAVITY)

        # if self is outside screen side barriers
        if not (0 < x+32 < constants.LEVEL_WIDTH):
            self.outside_horizontal()

        if not self.weightless:
            # self.kick(dv=Vector(0, -self.gravity), restrict_velocity=False)
            self.kick(dv=Vector(0, -self.gravity))

        if not self.vector.is_zero_vector():
            self.move(dr=(self.vector * dt/1000.))
        # on ground code should not go here.
        # if not self.place_free(x, y+1) and self.place_free(x, y):
            # self.on_ground = True
        # else:
            # self.on_ground = False

        # if pygame.Rect(self.obj.rect, topleft=(self.p.x, self.p.y+1)).collidelist([s.rect for s in self.nearby]):
            # self.on_ground = True
        # else:
            # self.on_ground = False

        # raise NotImplementedError
        # self.obj.on_ground = whether your feet are touching the ground

        if not self.frictionless:
            self.vector[0] -= self.vector[0]*constants.friction
            self.vector[1] -= self.vector[1]*constants.friction
        self.vector[0] = round(self.vector[0], 9)
        self.vector[1] = round(self.vector[1], 9)
        # only restrict when accellerating due to key input,
        # and dont set it to maxspeed, but instead, don't apply the speed
        logging.debug("bottom of physics update call")



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

        self.add_hold(hear="accelerate", react="accel", callback=accel)

        @Reaction
        def turnleft(**kwargs):
            if self.obj.accelerating:
                return {"d0": constants.accelturnspeed}
            return {"d0": constants.turnspeed}
        # print(turnleft.start)
        self.add_hold(hear="left", react="turn", callback=turnleft)

        @Reaction
        def turnright(**kwargs):
            if self.obj.accelerating:
                return {"d0": -constants.accelturnspeed}
            return {"d0": -constants.turnspeed}
        self.add_hold(hear="right", react="turn", callback=turnright)

        @Reaction
        def shoot(**kwargs):
            return {"dv": constants.bulletspeed}
        self.add_hold(hear="fire", react="shoot", callback=shoot)

        @Reaction
        def reset(**kwargs):
            return {"x":constants.LEVEL_WIDTH//2, "y":constants.LEVEL_HEIGHT//2, "vx":0, "vy":0}
        self.add_tap(hear="space", react="reset", callback=reset)


class Player(Object, pygame.sprite.Sprite):
    width, height = 16, 16

    def __init__(self, pos):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PlayerPhysicsComponent)
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('sprite', SpriteComponent, get_resource("playerimage"), 64, 64)
        # where to attach the special behavior for the sprite logic.
        # here?
        self.mask = pygame.mask.from_surface(self.image)
        assert(self.mask.count() > 0)

    @staticmethod
    def render_text(text):
        outputInfo(text)

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

    # def add_collision_check(self, group, **kwargs):
    #     proximity = kwargs.get('proximity', self.height+10)
    #     self.attach_component('proximity_{group.__class__.__name__}'.format(group=group),
    #                           ProximitySensor, group, proximity)

    @property
    def pos(self):
        return self.get_component('position').pos


# class AIComponent(Component):
#     def __init__(self, obj):
#         super(AIComponent, self).__init__(obj)
#         self.attach_event("update", self.update)

#     def update(self, dt):
#         # raise NotImplementedError
#         # playerangle = direction(self, player)
#         # self.turn()  # find player and turn towards him
#         # if abs(self.dir-direction(self, player)) < 10:
#             # self.accel()  # accel toward player.
#         pass


# class Enemy(Composite, pygame.sprite.Sprite):
#     width, height = 16, 16

#     def __init__(self, pos):
#         super(Enemy, self).__init__()
#         self.attach_component('position', PositionComponent, pos)
#         self.attach_component('physics', PhysicsComponent)
#         self.attach_component('image', SpriteFromImage, (os.path.join('.', 'resources', 'images', 'playerimage.png')))
#         self.attach_component('ai', AIComponent)
#         # self.get_component('image').image = pygame.transform.scale(self.get_component('image').image, (self.get_component('image').rect.width//4*3, self.get_component('image').rect.height))
#         self.mask = pygame.mask.from_surface(self.image)
#         assert(self.mask.count() > 0)

#     def __getattr__(self, name):
#         return getattr(self.spriteref, name)

#     def update(self, **kwargs):
#         dt = kwargs['dt']
#         self.dispatch_event(Event("update", {"dt": dt}))

#     @property
#     def pos(self):
#         return self.get_component('position').pos


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


def main():
    do_prep()
    dt = 1000/constants.FRAMERATE

    global resources

    screen = get_resource("screen")

    camera = Camera(simple_camera, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    # camera = Camera(lambda camera, tr: Rect(0, 0, camera.width, camera.height),
    #                 constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)

    truebg = get_resource("truebg")
    screen.blit(truebg, (0, 0), screen.get_rect())

    All = kwargsGroup.UserGroup()

    player = Player((500, constants.LEVEL_HEIGHT-500))
    # player.notify(Event("toggle_gravity", {}))

    camera.update(player.rect)
    All.add(player)

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
                elif event.type is POSTMESSAGE:
                    render_text(event.info, event.color)

            pygame.event.pump()

            render_text("player rect topleft = {}".format(player.rect.topleft))
            render_text("transformed = {}".format(camera.apply(player.rect)))
            render_text("bg topleft transformed = {}".format(camera.apply(screen.get_rect())))

            screen.fill((255, 255, 255))

            screen.blit(truebg, camera.apply(screen.get_rect()))

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
    except:
        logging.debug("------------------------------------------")
        logging.debug("start of dumpstate")
        for sprite in iter(All):
            sprite.dumpstate()
        raise

if __name__ == '__main__':
    try:
        main()
    finally:
        versionnumber.increment(__file__)
        logging.info("END\n")
        pygame.quit()
