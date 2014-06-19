#!/usr/bin/python

import logging

import constants
import keyconfig

import pygame

logging.basicConfig(**constants.logging_setup)


def yvel_to_jump(jumpstrength):
    pass


def sign(n):
    return int(n/abs(n))


def vadd(x, y):
    return [x[0]+y[0], x[1]+y[1]]


def vsub(x, y):
    return [x[0]-y[0], x[1]-y[1]]


def vmul(x, m):
    return [x[0]*m, x[1]*m]


def vdot(x, y):
    return [x[0]*y[0], x[1]*y[1]]


class Component:
    def __init__(self, obj):
        raise NotImplementedError


class Event:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data

# class EventHandler(Object):
    # """Handles events. A collection of Reactions"""
    # def __init__(self, obj):
        # super(EventHandler, self).__init__()
        # self.obj = obj
    # def add_handler(self, thing):
        # pass
    # def dispatch_event(self, event):
        # self.obj.dispatch_event(event)
    # def attach_event(self, keyword, callback):
        # self.obj.attach_event(keyword, callback)


class EventHandler(Component):
    """Handles events. A collection of reactions"""
    def __init__(self, obj):
        self.obj = obj
        self.handlers = []
        # self.obj.attach_event('update', self.update)

    def add_handler(self, hear):
        pass


class PlayerEventHandler(EventHandler):
    def __init__(self, obj):
        # super(PlayerEventHandler, self).__init__(obj)
        EventHandler.__init__(self, obj)
        raise NotImplementedError
        # self.add_handler("", "")
        # self.add_handler("", "")
        # self.add_handler("", "")
        # self.add_handler("", "")


class Repeater(Component):
    """Repeatedly broadcasts an event every n ticks"""
    def __init__(self, obj, keyword, n, data={}):
        self.i = 0
        self.obj = obj
        self.keyword = keyword
        self.n = n
        self.data = data
        self.obj.attach_event("update", self.update)

    def update(self, **kwargs):
        self.i += 1
        if self.i % self.n == 0:
            self.obj.dispatch_event(Event(self.keyword, self.data))


class Reaction(Component):
    """Causes one event when it hears another"""
    def __init__(self, obj, hear, react, heardata={}, reactdata={}):
        self.obj = obj
        assert(isinstance(hear, str))
        self.hear = hear
        assert(isinstance(react, str))
        self.react = react
        assert(isinstance(heardata, dict))
        self.heardata = heardata

        if callable(reactdata):
            self.reactdata = reactdata
        self.obj.attach_event(hear, self.reaction)

    def reaction(self, data):
        self.reactdata = self.reactdata(self.heardata)
        self.obj.dispatch_event(self.react, data)


class Delay(Component):
    """Causes an event after a specified delay,
assuming that update gets called every frame."""
    def __init__(self, obj, timeout, event, data={}):
        self.obj = obj
        self.event = event
        self.data = data
        self.t = timeout
        self.obj.attach_event('update', self.update)

    def update(self, **kwargs):
        if self.t > 0:
            self.t -= 1
            return
        self.obj.dispatch_event(self.event, self.data)


class InputController(Component):
    def __init__(self, obj):
        self.obj = obj
        self.reactions = keyconfig.keys
        print(self.reactions)
        obj.attach_event('keydown', self.keydown)
        obj.attach_event('keyup', self.keyup)

    # impliment keyboard input
    # what i want to do is map a key to an event
    # i.e. map K_SPACE to the "jump" event

    def keydown(self, **kwargs):
        key = kwargs["key"]
        logging.info("keydown %s from InputController.keydown" % key)
        logging.info(pygame.key.name(key))
        logging.info(self.reactions[key])
        logging.info(key in self.reactions)
        if key in self.reactions:
            self.obj.dispatch_event(Event(self.reactions[key], data={'press': True}))

    def keyup(self, **kwargs):
        key = pygame.key.name(kwargs['key'])
        logging.info("keyup %s from InputController.keyup" % key)
        if key in self.reactions:
            self.obj.dispatch_event(Event(self.reactions[key], data={'press': False}))

    def update(self, **kwargs):
        pass


class PositionComponent(Component):
    def __init__(self, obj, pos=(0, 0)):
        self.obj = obj
        self.x, self.y = pos

    @property
    def pos(self):
        return [self.x, self.y]

    @pos.setter
    def pos(self, value):
        self.x, self.y = value


class PhysicsComponent(Component):
    """docstring for PhysicsComponent"""
    def __init__(self, obj, **kwargs):
        self.p = obj.get_component('position')
        self.gravity = kwargs['gravity']\
            if 'gravity' in kwargs else constants.GRAVITY
        self.vector = [0, self.gravity]
        obj.attach_event('update', self.update)
        obj.attach_event('collision', self.collide)
        obj.attach_event('move', self.move)
        obj.attach_event('kick', self.kick)

    def collide(self, s):
        """Test if the sprites are colliding and
        resolve the collision in this case."""
        # offset = [int(x) for x in vsub(s.pos, self.pos)]
        # overlap = self.mask.overlap_area(s.mask, offset)
        # if overlap == 0:
        #     return
        # # """Calculate collision normal"""
        # nx = (self.mask.overlap_area(s.mask, (offset[0]+1, offset[1])) -
        #       self.mask.overlap_area(s.mask, (offset[0]-1, offset[1])))
        # ny = (self.mask.overlap_area(s.mask, (offset[0], offset[1]+1)) -
        #       self.mask.overlap_area(s.mask, (offset[0], offset[1]-1)))
        # if nx == 0 and ny == 0:
        #     # """One sprite is inside another"""
        #     return
        # n = [nx, ny]
        # dv = vsub(s.vel, self.vel)
        # J = vdot(dv, n)/(2*vdot(n, n))
        # if J > 0:
        #     # """Can scale up to 2*J here to get bouncy collisions"""
        #     J *= 1.9
        #     self.kick([nx*J, ny*J])
        #     s.kick([-J*nx, -J*ny])
        #     return
        # # """Separate the sprites"""
        # c1 = -overlap/vdot(n, n)
        # c2 = -c1/2
        # self.move([c2*nx, c2*ny])
        # s.move([(c1+c2)*nx, (c1+c2)*ny])
        return

    def move(self, **kwargs):
        dr = [0, 0]
        logging.debug("move called in PhysicsComponent with kwargs as %s" %
                      kwargs)
        if "dx" in kwargs:
            logging.debug('dx in kwargs')
            dr[0] += kwargs['dx']
        if "dy" in kwargs:
            logging.debug('dy in kwargs')
            dr[1] += kwargs['dy']
        if "dr" in kwargs:
            logging.debug('dr in kwargs')
            dr[0] += kwargs["dr"][0]
            dr[1] += kwargs["dr"][1]

        print(dr)
        self.p.pos = vadd(self.p.pos, dr)
        print(self.p.pos)

    def kick(self, **kwargs):
        logging.info("kick in PhysicsComponent")
        dv = [0, 0]
        if "dv_x" in kwargs:
            dv[0] = kwargs['dv_x']

        if "dv_y" in kwargs:
            dv[1] = kwargs['dv_y']

        if "vector" in kwargs:
            dv = kwargs['vector']

        if "impulse" in kwargs:
            dv = kwargs['impulse']

        self.vector[0] += dv[0]
        self.vector[1] += dv[1]

        logging.info("kick called in PhysicsComponent %s" % str(dv))

    def update(self, **kwargs):
        dt = kwargs['dt']
        if self.vector != [0, 0]:
            self.move(dr=list(vmul(self.vector, dt)))
        self.vector[1] += self.gravity
        if abs(self.vector[0]) > constants.runspeed:
            self.vector[0] = sign(self.vector[0])*constants.runspeed


class SimpleSprite(Component):
    def __init__(self, obj):
        self.obj = obj
        self.p = self.obj.get_component('position')
        self.obj.image = pygame.Surface((32, 64))
        self.obj.image.fill(pygame.Color(128, 128, 128))
        self.obj.rect = self.obj.image.get_rect()
        self.obj.attach_event('update', self.update)

    def update(self, **kwargs):
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

    def attach_component(self, name, component, *initargs):
        assert(issubclass(component, Component))
        self[name] = component(self, *initargs)

    def get_component(self, name):
        return self[name]

    def dispatch_event(self, event):
        if event.keyword not in self.callbacks:
            return
        for priority, func in reversed(sorted(self.callbacks[event.keyword],
                                       key=lambda elem: elem[0])):
            func(**event.data)
        logging.debug("dispatching event %s with data %s" % (event.keyword,
                                                             str(event.data)))

    def attach_event(self, keyword, callback, priority=-1):
        if keyword not in self.callbacks:
            self.callbacks[keyword] = []
        _hash = hash((priority, callback))
        self.callbacks[keyword].append((priority, callback))
        return _hash
        logging.debug("attaching event %s with callback %s" %
                      (keyword, callback.__name__))

    def break_event(self):
        pass

    def detach_event(self, keyword, _hash):
        for priority, func in self.callbacks[keyword]:
            if hash((priority, func)) == _hash:
                self.callbacks[keyword].remove((priority, func))

    def remove_component(self, name):
        del self[name]

    def notify(self, event):
        if event.type == pygame.KEYDOWN:
            self.dispatch_event(Event('keydown', {'key': event.key}))
        elif event.type == pygame.KEYUP:
            self.dispatch_event(Event('keyup', {'key': event.key}))


class Player(Object):
    def __init__(self, pos):
        # super(Player,self).__init__()
        Object.__init__(self)
        self.attach_component('position', PositionComponent, pos)
        self.attach_component('physics', PhysicsComponent)
        self.attach_component('input', InputController)
        self.attach_component('handler', PlayerEventHandler)
        self.attach_component('image', SimpleSprite)

    def update(self, kwargs):
        # print('update in Player')
        dt = kwargs['dt']
        self.dispatch_event(Event("update", {"dt": dt}))
