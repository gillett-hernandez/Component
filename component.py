#!/usr/bin/python

import logging

import constants
import keyconfig

import pygame

logging.basicConfig(**constants.logging_setup)
from math import hypot


def void(*args, **kwargs):
    return


def yvel_to_jump(jumpspeed):
    return -jumpspeed


def sign(n):
    return int(n/abs(n))


def vadd(x, y):
    return [x[0]+y[0], x[1]+y[1]]


def vsub(x, y):
    return [x[0]-y[0], x[1]-y[1]]


def vmul(x, m):
    return [x[0]*m, x[1]*m]


def vdot(x, y):
    return x[0]*y[0]+x[1]*y[1]

from miscfunc import lengthdir_x, lengthdir_y


def distance(x, y=[0, 0]):
    return hypot(x[0]-y[0], x[1]-y[1])


class Component(object):
    def __init__(self, obj):
        self.obj = obj
        self.attached_events = []

    def __repr__(self):
        return ("<{self.__class__.__name__} " +
                "attached to {self.obj!r}>").format(self=self)

    def __str__(self):
        return repr(self)

    def attach_event(self, keyword, callback):
        self.attached_events.append(self.obj.attach_event(keyword, callback))

    def detach_event(self, eventid):
        self.obj.detach_event(eventid)

    def remove_events(self):
        logging.debug("called remove_events from " +
                      "{self.__class__.__name__}".format(self=self))
        for eventid in self.attached_events:
            self.obj.detach_event(eventid)


class Event:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data

    def __repr__(self):
        return "<Event instance with keyword:" +\
            " {keyword} and data: {data}>".format(keyword=str(self.keyword),
                                                  data=str(self.data))


class EventHandler(Component):
    """Handles events. A collection of reactions"""
    def __init__(self, obj):
        super(EventHandler, self).__init__(obj)
        self.handlers = []
        self.events = []
        # obj.attach_event('update', self.update)

    def add_tap(self, hear, react, func):
        def reaction(**kwargs):
            if kwargs['press'] is True:
                # self.obj.on_ground = False
                self.obj.dispatch_event(Event(react, func(**kwargs)))
                return
            # self.on_ground = True
        self.attach_event(hear, reaction)

    def add_hold(self, hear, react, func):
        def reaction(**kwargs):
            pressed = kwargs['press']
            logging.debug("reaction with pressed as {pressed}".format(
                          pressed=pressed))
            if pressed:

                logging.debug(
                    "reaction if branch right before attach_component")

                self.obj.attach_component(
                    "{hear}_{react}_repeater".format(hear=hear, react=react),
                    Repeater, react, 1, func(**kwargs)
                )
            else:

                logging.debug(
                    "reaction else branch right before detach_component")

                self.obj.detach_component(
                    "{hear}_{react}_repeater".format(hear=hear, react=react))

        self.attach_event(hear, reaction)


class Repeater(Component):
    """Repeatedly broadcasts an event every n ticks"""
    def __init__(self, obj, keyword, n, data={}):
        super(Repeater, self).__init__(obj)
        self.i = 0
        self.keyword = keyword
        self.n = n
        self.data = data
        if n == 1:
            self.attach_event("update", self.update1)
        else:
            self.attach_event("update", self.update)

    def update(self, **kwargs):
        self.i += 1
        if self.i % self.n == 0:
            self.obj.dispatch_event(Event(self.keyword, self.data))

    def update1(self, **kwargs):
        self.obj.dispatch_event(Event(self.keyword, self.data))


class Reaction(Component):
    """Causes one event when it hears another"""
    def __init__(self, obj, hear, react, heardata={}, reactdata={}):
        super(Reaction, self).__init__(obj)
        assert(isinstance(hear, str))
        self.hear = hear
        assert(isinstance(react, str))
        self.react = react
        assert(isinstance(heardata, dict))
        self.heardata = heardata

        if callable(reactdata):
            self.reactdata = reactdata
        self.attach_event(hear, self.reaction)

    def reaction(self, data):
        self.reactdata = self.reactdata(self.heardata)
        self.obj.dispatch_event(self.react, data)


class Delay(Component):
    """Causes an event after a specified delay,
assuming that update gets called every frame."""
    def __init__(self, obj, timeout, event, data={}):
        super(Delay, self).__init__(obj)
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
        self.reactions = keyconfig.keys
        logging.debug(self.reactions)
        self.attach_event('keydown', self.keydown)
        self.attach_event('keyup', self.keyup)

    def keydown(self, **kwargs):
        key = kwargs["key"]
        logging.debug(("keydown {key} from " +
                      "InputController.keydown").format(key=key))
        logging.debug(pygame.key.name(key))
        logging.debug(key in self.reactions)
        if key in self.reactions:
            logging.debug(self.reactions[key])
            reaction = self.reactions[key]
            reaction[1].update({'press': True})
            logging.debug(reaction)
            self.obj.dispatch_event(Event(reaction[0], reaction[1]))

    def keyup(self, **kwargs):
        key = kwargs['key']

        logging.debug("keyup {key} from InputController.keyup".format(key=key))
        logging.debug(pygame.key.name(key))
        logging.debug(key in self.reactions)

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
        self.x, self.y = pos
        self.xstart, self.ystart = pos

    @property
    def pos(self):
        return [self.x, self.y]

    @pos.setter
    def pos(self, value):
        self.x, self.y = value


class ProximitySensor(Component):
    def __init__(self, obj, group, r):
        super(ProximitySensor, self).__init__(obj)
        logging.debug("ProximitySensor init")
        self.group = group
        self.r = r
        self.attach_event('update', self.update)

    def update(self, **kwargs):
        sprlist = filter(lambda spr: distance(self.obj.rect.center, spr.rect.center) < self.r, self.group.sprites())
        self.obj.dispatch_event(Event("nearby", data={"spritelist": sprlist}))


class PhysicsComponent(Component):
    """docstring for PhysicsComponent"""
    def __init__(self, obj, **kwargs):
        super(PhysicsComponent, self).__init__(obj)
        self.p = obj.get_component('position')
        self.gravity = kwargs['gravity']\
            if 'gravity' in kwargs else constants.GRAVITY
        self.vector = [0, 0]
        self.dir = -90
        self.attach_event('update', self.update)
        self.attach_event('nearby', self.collidelist)
        self.attach_event('move', self.move)
        self.attach_event('kick', self.kick)
        self.attach_event('turn', self.turn)

    def collidelist(self, **kwargs):
        slist = kwargs['spritelist']
        self.nearby = slist
        for s in slist:
            self.collide(sprite=s)

    def collide(self, **kwargs):
        s = kwargs["sprite"]
        logging.debug("collide in PhysicsComponent")
        """Test if the sprites are colliding and
        resolve the collision in this case."""
        offset = [int(x) for x in vsub(s.pos, self.obj.pos)]
        # print(self.obj.mask.count(), s.mask.count())
        overlap = self.obj.mask.overlap_area(s.mask, offset)
        # print(overlap)

        if overlap == 0:
            # print("overlap == 0")
            return
        # """Calculate collision normal"""
        nx = (self.obj.mask.overlap_area(s.mask, (offset[0]+1, offset[1])) -
              self.obj.mask.overlap_area(s.mask, (offset[0]-1, offset[1])))
        ny = (self.obj.mask.overlap_area(s.mask, (offset[0], offset[1]+1)) -
              self.obj.mask.overlap_area(s.mask, (offset[0], offset[1]-1)))
        logging.debug("overlapping, {nx}, {ny}".format(nx=nx, ny=ny))
        if nx == 0 and ny == 0:
            # """One sprite is inside another"""
            return
        n = [nx, ny]
        # dv = vsub(s.vel, self.vel)
        dv = vsub([0, 0], self.vector)
        J = vdot(dv, n)/(2*vdot(n, n))
        if J > 0:
            logging.debug("J>0")
            # """Can scale up to 2*J here to get bouncy collisions"""
            J *= 1.9
            # special resolution of collisions in case of
            # one being a static, immovable object

            # raise NotImplementedError
            # because im in physics component,
            # should i even use dispatch_event?
            # or should i just call self.kick and self.move?

            # self.obj.dispatch_event(Event("kick",
            # data={"vector": [nx*J, ny*J]}))
            self.kick(vector=[nx*J, ny*J])
            # s.kick([-J*nx, -J*ny])
            return
        # """Separate the sprites"""
        c1 = -overlap/vdot(n, n)
        c2 = -c1/2
        # self.obj.dispatch_event(Event("move", data={"dr": [c2*nx, c2*ny]}))
        # s.move([(c1+c2)*nx, (c1+c2)*ny])
        logging.debug("moving in collision")
        self.move(dr=[c2*nx, c2*ny])
        return

    def move(self, **kwargs):
        dr = [0, 0]
        # logging.debug(("move called in {self.__class__.__name__}" +
        #               " with kwargs as {kwargs}").format(
        #               self=self, kwargs=kwargs))
        if "dx" in kwargs:
            dr[0] += kwargs['dx']
        if "dy" in kwargs:
            dr[1] += kwargs['dy']
        if "dr" in kwargs:
            dr[0] += kwargs["dr"][0]
            dr[1] += kwargs["dr"][1]

        self.p.pos = vadd(self.p.pos, dr)

    def kick(self, **kwargs):
        dv = [0, 0]
        if "dv" in kwargs:
            if isinstance(kwargs["dv"], int):
                self.accel(kwargs["dv"])
                return
            elif isinstance(kwargs["dv"], list) or isinstance(kwargs["dv"], tuple):
                dv = kwargs['dv']
            else:
                raise TypeError
        if "dv_x" in kwargs:
            dv[0] = kwargs['dv_x']

        if "dv_y" in kwargs:
            dv[1] = kwargs['dv_y']

        if "vector" in kwargs:
            dv = kwargs['vector']

        if "impulse" in kwargs:
            dv = kwargs['impulse']

        # if not distance(self.vector, [0, 0]) > constants.maxspeed:
        # if abs(self.vector[0]+dv[0]) > abs(self.vector[0]):
        self.vector[0] += dv[0]
        # if abs(self.vector[1]+dv[1]) > abs(self.vector[1]):
        self.vector[1] += dv[1]

        logging.info(("kick called in PhysicsComponent {dv}." +
                     " current vector is {v}").format(dv=dv, v=self.vector))

    def turn(self, d0):
        logging.debug("calling turn from PhysicsComponent, d0={0}".format(d0))
        self.dir -= d0

    def accel(self, dv):
        v = [lengthdir_x(dv, self.dir), lengthdir_y(dv, self.dir)]
        print(v)
        self.kick(dv=v)

    def bounce_horizontal(self):
        self.vector[0] *= -1

    def bounce_vertical(self):
        self.vector[1] *= -1

    # def move_outside_solid(self, dir, maxdist):
        # pass

    # def place_empty(self, x, y):
        # pass

    # def move_contact_solid(self, sprite):
        # pass

    def toggle_gravity(self):
        self.on_ground = not self.on_ground

    def update(self, **kwargs):
        print(self.dir, 'phys')
        dt = kwargs['dt']
        x, y = self.p.pos
        # if self is outside screen ceiling or floor
        # if abs(self.p.pos[1]-h2) > h2:
        if y > constants.SCREEN_HEIGHT or y < 0:
            # |y-h/2|>h/2 = y-h/2>h/2 or y-h/2<-h/2
            # = y>h or y<0
            # tested using %timeit with ipython
            # y > h or y < 0 is better
            # self.bounce_vertical()
            # self.vector[1] *= .9
            self.p.pos = [self.p.xstart, self.p.ystart]
            self.vector = [0, 0]

        # if self is outside screen side barriers
        # if abs(self.p.pos[0]-w2) > w2:
        if x > constants.SCREEN_WIDTH or x < 0:
            # self.bounce_horizontal()
            # self.vector[0] *= .9
            self.p.pos = [self.p.xstart, self.p.ystart]
            self.vector = [0, 0]

        self.vector[1] += self.gravity*dt/1000.

        if self.vector is not [0, 0]:
            self.move(dr=list(vmul(self.vector, dt/1000.)))
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

        self.vector[0] = round(self.vector[0]*constants.friction, 5)
        self.vector[1] = round(self.vector[1]*constants.friction, 5)
        # only restrict when accellerating due to running,
        # and dont set it to maxspeed, but instead, don't apply the speed


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
        self.attach_event('turn', self.turn)

        self.p = self.obj.get_component('position')
        self.image = pygame.image.load(imagepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.obj.image = self.image
        self.obj.rect = self.obj.image.get_rect()
        self.obj.rect.topleft = self.p.pos

        self.dir = 0
        logging.warning("using turn may result in a slowdown due to the use of an expensive operation: pygame.transform.rotate")

    def turn(self, d0):
        self.dir += d0
        logging.debug("d0 is {d0}, dir is {self.dir}".format(d0=d0, self=self))
        self.obj.image = pygame.transform.rotate(self.image, self.dir)
        # self.obj.rect = self.obj.image.get_rect(center=self.obj.rect.center)

    def update(self, **kwargs):
        print(self.dir)
        if self.obj.rect.topleft is not self.p.pos:
            self.obj.rect.topleft = self.p.pos


class Object(pygame.sprite.Sprite):
    def __init__(self):
        super(Object, self).__init__()
        self.callbacks = {}
        self.components = {}

    def __getitem__(self, key):
        return self.components[key]

    def __setitem__(self, key, value):
        self.components[key] = value

    def __delitem__(self, key):
        del self.components[key]

    def __len__(self):
        return len(self.components)

    def attach_component(self, name, component, *initargs):
        assert(issubclass(component, Component))
        logging.debug("attaching component with name: " +
                      "{name} {component!r}{initargs!s}".format(
                          name=name, component=component, initargs=initargs))
        self[name] = component(self, *initargs)

    def get_component(self, name):
        return self[name]

    def dispatch_event(self, event):
        assert(event.data is not None)
        if event.keyword is not "update":
            logging.debug("dispatching event {event!r}".format(event=event))
        if event.keyword not in self.callbacks:
            return
        for _id, func in self.callbacks[event.keyword].items():
            func(**event.data)

    def attach_event(self, keyword, callback):
        if keyword not in self.callbacks:
            self.callbacks[keyword] = {}
        _id = hash(callback)
        self.callbacks[keyword][_id] = callback
        logging.debug(("attaching event {keyword} " +
                       "with callback {callback}").format(
                      keyword=keyword, callback=callback))
        return _id

    def break_event(self):
        pass

    def detach_event(self, _hash):
        for keyword in self.callbacks:
            for _id in self.callbacks[keyword]:
                if _id == _hash:
                    logging.debug("calling detach_event on {callback}".format(callback=self.callbacks[keyword][_id]))
                    del self.callbacks[keyword][_id]
                    return

    def detach_component(self, name):
        logging.debug("calling detach_component on {name}".format(name=name))
        self[name].remove_events()
        del self[name]

    def notify(self, event):
        if event.type == pygame.KEYDOWN:
            self.dispatch_event(Event('keydown', {'key': event.key}))
        elif event.type == pygame.KEYUP:
            self.dispatch_event(Event('keyup', {'key': event.key}))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.dispatch_event(Event('mousebuttondown', {'key': event.key}))

    def __repr__(self):
        return self.__class__.__name__


def test():
    pass

if __name__ == '__main__':
    test()
