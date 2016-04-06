
import math
import logging

from component import Component, Event, constants, keyconfig
from vector import Vector

import pygame

logging.basicConfig(**constants.logging_setup)


class EventHandler(Component):
    """Handles events. A collection of reactions"""
    def __init__(self, obj):
        super(EventHandler, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))

        # obj.attach_event('update', self.update)

    def add_tap(self, hear, react, func):
        def reaction(**kwargs):
            if kwargs['press'] is True:

                self.obj.dispatch_event(Event(react, func(**kwargs)))
                return

        self.attach_event(hear, reaction)

    def add_hold(self, hear, react, reaction):
        def holdreaction(**kwargs):
            pressed = kwargs['press']
            logging.debug("reaction with pressed as {pressed}".format(
                          pressed=pressed))
            if pressed:

                logging.debug(
                    "reaction if branch right before attach_component")
                # print(reaction)
                reaction.start(**kwargs)
                # timing for a hold reaction goes here
                self.obj.attach_component(
                    "{hear}_{react}_repeater".format(hear=hear, react=react),
                    Repeater, react, 1, reaction.hold
                )
            else:

                logging.debug(
                    "reaction else branch right before detach_component")
                reaction.end(**kwargs)
                self.obj.detach_component(
                    "{hear}_{react}_repeater".format(hear=hear, react=react))
        holdreaction.__name__ = "{hear}_{react}_repeater".format(hear=hear, react=react)
        self.attach_event(hear, holdreaction)


class Repeater(Component):
    """Repeatedly broadcasts an event every n ticks"""
    def __init__(self, obj, keyword, n=1, data={}):
        super(Repeater, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.i = 0
        self.keyword = keyword
        self.n = n  # default 1
        self.data = data
        self.attach_event("update", self.update)

    def update(self, **kwargs):
        self.i += 1
        if self.i % self.n == 0:
            if callable(self.data):
                self.obj.dispatch_event(Event(self.keyword, self.data(**kwargs)))
            else:
                self.obj.dispatch_event(Event(self.keyword, self.data))


class Reaction(object):
    def __init__(self, f):
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.defhold(f)
        self.start = self.void
        self.end = self.void

    def void(self, *args, **kwargs):
        pass

    def defhold(self, f):
        self.hold = f

    def defstart(self, f):
        self.start = f
        return self

    def defend(self, f):
        self.end = f
        return self

    def __str__(self):
        return " ".join([str(self.start), str(self.hold), str(self.end)])


class Delay(Component):
    """Causes an event after a specified delay,
assuming that update gets called every frame."""
    def __init__(self, obj, timeout, event, data={}):
        super(Delay, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.event = event
        self.data = data
        self.t = timeout
        self.attach_event('update', self.update)

    def update(self, **kwargs):
        if self.t > 0:
            self.t -= 1
            return
        self.obj.dispatch_event(self.event, self.data)


class InputController(Component):
    def __init__(self, obj):
        super(InputController, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.reactions = {}
        logging.debug("reactions = {0.reactions}".format(self))
        for key, data in keyconfig.keys.items():
            self.reactions[getattr(pygame.locals, key)] = data
        self.attach_event('keydown', self.keydown)
        self.attach_event('keyup', self.keyup)

    def keydown(self, **kwargs):
        key = kwargs["key"]
        keyname = pygame.key.name(key)
        logging.debug(("keydown {key} from " +
                      "InputController.keydown").format(key=(keyname, key)))
        if key not in self.reactions:
            logging.warn("{key} does not have a mapped reaction in InputController".format(key=(keyname, key)))
        if key in self.reactions:
            logging.debug(self.reactions[key])
            reaction = self.reactions[key]
            reaction[1].update({'press': True})
            logging.debug(reaction)
            self.obj.dispatch_event(Event(reaction[0], reaction[1]))

    def keyup(self, **kwargs):
        key = kwargs['key']
        keyname = pygame.key.name(key)
        logging.debug(("keydown {key} from " +
                      "InputController.keydown").format(key=(keyname, key)))
        if key not in self.reactions:
            logging.warn("{key} does not have a mapped reaction in InputController".format(key=(keyname, key)))
        if key in self.reactions:
            logging.debug(self.reactions[key])
            reaction = self.reactions[key]
            reaction[1].update({'press': False})
            logging.debug(reaction)
            self.obj.dispatch_event(Event(reaction[0], reaction[1]))

    # def update(self, **kwargs):
        # pass


class PositionComponent(Component):
    def __init__(self, obj, pos=(0, 0)):
        super(PositionComponent, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.pos = Vector(*pos)
        self.xstart, self.ystart = pos

    @property
    def x(self):
        return self.pos.x

    @x.setter
    def x(self, value):
        self.pos.x = value

    @property
    def y(self):
        return self.pos.y

    @y.setter
    def y(self, value):
        self.pos.y = value

    def reset(self):
        self.pos.components = [self.xstart, self.ystart]


class ProximitySensor(Component):
    def __init__(self, obj, group, r):
        super(ProximitySensor, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.group = group
        self.r = r
        self.attach_event('update', self.update)

    def update(self, **kwargs):
        sprlist = filter(lambda spr: (Vector(l=self.obj.rect.center) - Vector(l=spr.rect.center)).magnitude < self.r,
                         self.group.sprites())

        self.obj.dispatch_event(Event("nearby", data={"spritelist": sprlist}))


class PhysicsComponent(Component):
    def __init__(self, obj, **kwargs):
        super(PhysicsComponent, self).__init__(obj)
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.p = obj.get_component('position')
        assert self.p is not None
        self.gravity = kwargs.get("gravity", constants.GRAVITY)
        self.frictionless = kwargs.get("frictionless", False)
        self.weightless = kwargs.get("weightless", False)
        # for some reason vector is being set to None
        self.vector = Vector(0, 0)
        assert self.vector is not None
        self.dir = 90
        self.attach_event('update', self.update)
        self.attach_event('nearby', self.collidelist)
        self.attach_event('move', self.move)
        self.attach_event('kick', self.kick)
        self.attach_event('turn', self.turn)
        self.attach_event('accel', self.accel)
        self.attach_event('toggle_gravity', self.toggle_gravity)
        self.attach_event('change_gravity', self.change_gravity)

    def collidelist(self, **kwargs):
        slist = kwargs['spritelist']
        self.nearby = slist
        for s in slist:
            self.collide(sprite=s)

    def collide(self, **kwargs):
        raise NotImplementedError

    def move(self, dx=None, dy=None, dr=None, **kwargs):
        # legacy capturing **kwargs until its purged
        if dr is None:
            dr = Vector(0, 0)

        logging.debug(("move called in {self.__class__.__name__}" +
                      " with kwargs as {kwargs}").format(
                      self=self, kwargs=kwargs))

        # strange behavior
        if dx is not None:
            dr[0] += dx
        if dy is not None:
            dr[1] += dy

        if not isinstance(self.p.pos, Vector):
            raise NotImplementedError
        if not isinstance(dr, Vector):
            self.p.pos += Vector(l=dr)
        else:
            self.p.pos += dr

    def kick(self, dv=Vector(0, 0), restrict_velocity=True):
        if isinstance(dv, (list, tuple)):
            dv = Vector(l=dv)
        logging.debug("vector before kick is {}".format(self.vector))
        self.vector += dv
        if restrict_velocity:
            if self.vector.magnitude > constants.maxspeed - Vector(l=dv).magnitude:
                logging.debug("normalized velocity")
                self.vector.normalize_ip()
                self.vector *= constants.maxspeed
        logging.info("kick called in PhysicsComponent {dv}".format(dv=dv))
        logging.info("current vector is {v}".format(v=self.vector))

    def turn(self, d0):
        logging.debug("calling turn from PhysicsComponent, d0={0}, current angle is {1}".format(d0, self.dir))
        self.dir += d0
        self.dir %= 360

    def accel(self, dv=None, dir=None):
        assert dv is not None
        logging.debug("before kick current angle is {}".format(self.dir))
        if dir is None:
            dir = self.dir

        # direction of 0 degrees has a sin of 1 and a cos of 0
        # direction of +90 degrees has a sin of 0 and cos of 1
        # direction of +180 degrees has a sin of -1 and cos of 0
        # direction of +270 degrees has a sin of 0 and cos of -1

        v = Vector(dv * math.cos(math.radians(self.dir)), dv * math.sin(math.radians(self.dir)))
        logging.debug("accel {}".format(v))
        self.kick(dv=v)

    def bounce_horizontal(self):
        self.vector[0] *= -1

    def bounce_vertical(self):
        self.vector[1] *= -1

    def toggle_gravity(self):
        self.weightless = not self.weightless

    def change_gravity(self, g=None):
        if g is None:
            self.gravity = constants.GRAVITY
        else:
            self.gravity = g

    def outside_top(self):
        self.change_gravity(constants.GRAVITY*4)

    def outside_bottom(self):
        # self.p.pos = [self.p.xstart, self.p.ystart]
        self.change_gravity(-constants.GRAVITY*4)

    def outside_sides(self):
        self.p.reset()
        self.vector = Vector(0, 0)

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
        if y < 0:
            print("outside bottom")
            self.outside_bottom()
        elif y > constants.LEVEL_HEIGHT:
            print("outside top")
            self.outside_top()
        else:
            if not self.obj.accelerating:
                self.change_gravity()
            else:
                self.change_gravity(constants.FLIGHTGRAVITY)

        # if self is outside screen side barriers
        if not (0 < x < constants.LEVEL_WIDTH):
            self.outside_sides()

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


class SimpleSprite(Component):
    def __init__(self, obj, size, color=(128, 128, 128)):
        super(SimpleSprite, self).__init__(obj)
        self.p = self.obj.get_component('position')
        self.obj.image = pygame.Surface(size).convert()
        self.obj.image.fill(pygame.Color(*color))
        self.obj.rect = self.obj.image.get_rect()
        self.obj.rect.topleft = self.p.pos
        self.attach_event('update', self.update)

    def update(self, **kwargs):
        self.obj.rect.topleft = self.p.pos


class SpriteFromImage(Component):
    """Simple sprite from an image that supports rotation"""
    def __init__(self, obj, imagepath):
        super(SpriteFromImage, self).__init__(obj)

        self.attach_event('update', self.update)

        self.p = self.obj.get_component('position')
        self.a = self.obj.get_component('physics')
        self.image = pygame.image.load(imagepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.obj.image = self.image
        self.obj.rect = self.obj.image.get_rect()
        self.obj.rect.center = self.p.pos.components

    def update(self, **kwargs):
        self.obj.image = self.image
        # print(self.obj.rect, self.image.get_rect(), self.rect)
        self.obj.rect = self.obj.image.get_rect(center=self.rect.center)
        self.rect.topleft = self.p.pos.components
        # self.obj.rect.topleft = self.p.pos
        # if self.obj.rect.topleft is not self.p.pos:
