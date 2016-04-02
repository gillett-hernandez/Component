#!/usr/bin/env python

import logging
import json
import math


import pygame
from math import hypot

from vector import Vector


class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def items(self):
        return self.__dict__.items()

with open("./lf_constants.json", 'r') as fd:
    constants = DotDict(json.load(fd))

with open("./lf_keyconfig.json", 'r') as fd:
    keyconfig = DotDict(json.load(fd))

logging.basicConfig(**constants.logging_setup)


def void(*args, **kwargs):
    return


def sign(n):
    return int(n/abs(n))


def vproj(v1, v2):
    return distance(v1)*math.cos((math.atan2(v2[1], v2[0])-math.atan2(v1[1], v1[0])))


class Event:
    def __init__(self, keyword, data):
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.keyword = keyword
        self.data = data

    def __repr__(self):
        return ("<Event instance with keyword:"
                " {keyword} and data: {data}>".format(keyword=str(self.keyword),
                                                      data=str(self.data)))


class Component(object):
    def __init__(self, obj):
        super(Component, self).__init__()
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.attached_events = []
        self.obj = obj
        self.callbacks = {}

    def __repr__(self):
        return ("<{self.__class__.__name__} " +
                "attached to {self.obj!r}>").format(self=self)

    def __str__(self):
        return repr(self)

    def attach_event(self, keyword, callback):
        if keyword not in self.callbacks:
            self.callbacks[keyword] = {}
        _id = hash(callback)
        self.callbacks[keyword][_id] = callback
        logging.debug(("attaching event {keyword} " +
                       "with callback {callback}").format(
                      keyword=keyword, callback=callback))
        return _id

    def detach_event(self, _hash):
        for keyword in self.callbacks:
            for _id in self.callbacks[keyword]:
                if _id == _hash:
                    logging.debug("calling detach_event on {callback}".format(callback=self.callbacks[keyword][_id]))
                    del self.callbacks[keyword][_id]
                    return

    def dispatch_event(self, event):
        try:
            assert event.data is not None
            if event.keyword not in self.callbacks:
                return
            if event.keyword is not "update":
                logging.debug("dispatching event {event!r}".format(event=event))
            if len(self.callbacks[event.keyword]) == 0:
                return -1
            for func in self.callbacks[event.keyword].values():
                func(**event.data)
        except AttributeError as e:
            print(event, func)
            raise e

    def remove_events(self):
        logging.debug("called remove_events from " +
                      "{self.__class__.__name__}".format(self=self))
        for eventid in self.attached_events:
            self.obj.detach_event(eventid)

    def notify(self, event):
        self.dispatch_event(event)


class Object(object):
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

    def __getattr__(self, name):
        for component in self.components.values():
            if hasattr(component, name):
                return getattr(component, name)
        else:
            raise AttributeError("Object has no attribute {name}".format(name=name))

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
        c = 0
        if event.keyword is not "update":
            logging.debug("dispatching event {event!r}".format(event=event))
            for component in self.components.values():
                rvalue = component.dispatch_event(event)
                if rvalue == -1:
                    c += 1
            return
        if event.keyword in self.callbacks:
            for _id, func in self.callbacks[event.keyword].items():
                func(**event.data)
        else:
            if c == len(self.components):
                raise RuntimeError("CallbackNotFoundError")

    def attach_event(self, keyword, callback):
        if keyword not in self.callbacks:
            self.callbacks[keyword] = {}
        _id = hash(callback)
        self.callbacks[keyword][_id] = callback
        logging.debug(("attaching event {keyword} " +
                       "with callback {callback}").format(
                      keyword=keyword, callback=callback))
        return _id

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
        self.dispatch_event(event)

    def __repr__(self):
        return self.__class__.__name__


from components import *


def test():
    class PlayerEventHandler(EventHandler):
        def __init__(self, obj):
            super(PlayerEventHandler, self).__init__(obj)

            # raise NotImplementedError

            @Reaction
            def accel(**kwargs):
                # print("gravity is {g}".format(g=self.obj.get_component("physics").gravity))
                if distance(self.obj.get_component("physics").vector)>constants.maxspeed:
                    if not vproj(self.obj.get_component("physics").vector, miscfunc.vector_transform(constants.accel, self.obj.get_component("physics").dir))<0:
                        return {"dv": 0}
                return {"dv": constants.accel}

            @accel.defstart
            def accel(**kwargs):
                self.obj.dispatch_event(Event("change_gravity", {'g':constants.GRAVITY/4.}))
                self.obj.accelerating = True

            @accel.defend
            def accel(**kwargs):
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

    class Player(Object, pygame.sprite.Sprite):
        width, height = 16, 16

        def __init__(self, pos):
            super(Player, self).__init__()
            self.attach_component('position', PositionComponent, pos)
            self.attach_component('physics', PhysicsComponent)
            self.attach_component('input', InputController)
            self.attach_component('handler', PlayerEventHandler)
            # where to attach the special behavior for the sprite logic.
            # here?

        def __getattr__(self, name):
            if name == "pos" or name == "x" or name == "y":
                return getattr(self.get_component("position"), name)
            return super(Player, self).__getattr__(name)

        def update(self, **kwargs):
            logging.debug('update in Player')
            vector = self.get_component('physics').vector
            pdir = self.get_component('physics').dir
            self.dispatch_event(Event("update", kwargs))
            # start of wonky code
            logging.info("vector = {0!r}, {1}, {2}".format(vector.components,
                                                           self.get_component("physics").gravity,
                                                           self.pos))

        @property
        def pos(self):
            return self.get_component('position').pos


    player = Player((100, 100))
    print(dir(player.get_component("physics")))
    player.update(dt=1000)
    print(player.pos.components)
    player.notify(Event("move", {"dr": [10, 0]}))
    player.update(dt=1000)
    print(player.pos.components)
    player.notify(Event("kick", {"dv": [10, 0]}))
    assert(player.get_component("physics").vector[0] == 10)
    player.update(dt=1000)
    print(player.pos.components)
    player.update(dt=1000)
    print(player.pos.components)
    player.update(dt=1000)
    print(player.pos.components)
    player.update(dt=1000)
    print(player.pos.components)

if __name__ == '__main__':
    try:
        pygame.init()
        test()
    finally:
        pygame.quit()
