#!/usr/bin/env python

import logging
import json
import math
import os
import pygame
import pygame.locals

import versionnumber
from vector import Vector

from datastructures import DotDict

constants = None
keyconfig = None

def load_stuff(modulename):
    print("component.py/load_stuff got called")
    global constants
    global keyconfig
    base, name, ext = versionnumber.split(modulename)
    with open(os.path.join(base, "json", "constants.json"), 'r') as fd:
        constants = DotDict(json.load(fd))

    with open(os.path.join(base, "json", "keyconfig.json"), 'r') as fd:
        keyconfig = DotDict(json.load(fd))

    logging.basicConfig(**constants.logging_setup)
    print(versionnumber.render_version(__file__))
    logging.info(versionnumber.render_version(__file__))

def increment():
    versionnumber.increment(__file__)

def void(*args, **kwargs):
    return


def sign(n):
    return int(n/abs(n))


def vproj(v1, v2):
    return distance(v1)*math.cos((math.atan2(v2[1], v2[0])-math.atan2(v1[1], v1[0])))


class Event:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data
        logging.debug("created {0!r}".format(self))

    def __repr__(self):
        return ("<Event instance with keyword:"
                " {keyword} and data: {data}>".format(keyword=str(self.keyword),
                                                      data=str(self.data)))


class Component(object):
    def __init__(self, obj):
        super(Component, self).__init__()
        logging.debug("{0.__class__.__name__} super being instantiated now".format(self))
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
        # callbacks = {
        #     "update": {
        #         12312412: function1,
        #         432323: function2,
        #         95984: function3
        #     },
        #     "etc"
        # }
        logging.debug(("attaching event {keyword} " +
                       "with callback {callback}").format(
                      keyword=keyword, callback=callback))
        return _id

    def detach_event(self, _hash):
        # volatile list length?
        # no bc return statement right after del
        for keyword in self.callbacks:
            for _id in self.callbacks[keyword]:
                if _id == _hash:
                    logging.debug("calling detach_event on {callback}".format(callback=self.callbacks[keyword][_id]))
                    del self.callbacks[keyword][_id]
                    return

    def dispatch_event(self, event):
        func = None
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
            raise

    def remove_events(self):
        logging.debug("called remove_events from " +
                      "{self.__class__.__name__}".format(self=self))
        for _ in self.callbacks:
            for eventid in self.callbacks[_]:
                self.callbacks[_][eventid] = None
                # should be equivalent to `del`ing the function

    def notify(self, event):
        self.dispatch_event(event)

    def dumpstate(self):
        for keyword in self.callbacks:
            for eventid in self.callbacks[keyword]:
                logging.debug("        {} callback {}".format(keyword, self.callbacks[keyword][eventid]))

        for varname in dir(self):
            if varname not in dir(self.__class__):
                logging.debug("        {}={}".format(varname, getattr(self, varname)))


class Object(object):
    def __init__(self):
        logging.debug("{0.__class__.__name__} being instantiated now".format(self))
        self.components = {}

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise KeyError()
        return self.components[key]

    def __setitem__(self, key, value):
        self.components[key] = value

    def __delitem__(self, key):
        del self.components[key]

    def __len__(self):
        return len(self.components)

    def __getattr__(self, name):
        for componentname in self.components.keys():
            if name == componentname:
                return self.components[componentname]
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
        logging.debug("dispatching event {event!r}".format(event=event))
        for component in self.components.values():
            rvalue = component.dispatch_event(event)
            if rvalue == -1:
                c += 1
        if c == len(self.components):
            raise RuntimeError("CallbackNotFoundError")

    def detach_component(self, name):
        logging.debug("calling detach_component on {name}".format(name=name))
        self[name].remove_events()
        del self[name]

    def notify(self, event):
        self.dispatch_event(event)

    def dumpstate(self):
        # components
        logging.debug("    start of Object dumpstate")
        for name, component in self.components.items():
            logging.debug("    {} component dumpstate".format(name))
            component.dumpstate()

    def __repr__(self):
        return self.__class__.__name__

# from components import *


def test():
    class PlayerEventHandler(EventHandler):
        def __init__(self, obj):
            super(PlayerEventHandler, self).__init__(obj)
            self.attach_event("update", self.update)

            @Reaction
            def accel(**kwargs):
                # print("gravity is {g}".format(g=self.obj.get_component("physics").gravity))
                if distance(self.obj.get_component("physics").vector) > constants.maxspeed:
                    if not vproj(self.obj.get_component("physics").vector, miscfunc.vector_transform(constants.accel, self.obj.get_component("physics").dir)) < 0:
                        return {"dv": 0}
                return {"dv": constants.accel}

            @accel.defstart
            def accel(**kwargs):
                self.obj.dispatch_event(Event("change_gravity", {'g': constants.GRAVITY/4.}))
                self.obj.accelerating = True

            @accel.defend
            def accel(**kwargs):
                self.obj.dispatch_event(Event("change_gravity", {'g': constants.GRAVITY}))
                self.obj.accelerating = False

            self.add_hold("accelerate", "accel", accel)

            @Reaction
            def turnleft(**kwargs):
                if self.obj.accelerating:
                    return {"d0": constants.accelturnspeed}
                return {"d0": constants.turnspeed}
            self.add_hold("left", "turn", turnleft)

            @Reaction
            def turnright(**kwargs):
                if self.obj.accelerating:
                    return {"d0": -constants.accelturnspeed}
                return {"d0": -constants.turnspeed}
            self.add_hold("right", "turn", turnright)

        def update(self, **kwargs):
            logging.debug('update in Player')
            vector = self.obj.get_component('physics').vector
            # start of wonky code
            logging.info("vector = {0!r}, {1}, {2}".format(vector.components,
                                                           self.obj.get_component("physics").gravity,
                                                           self.obj.pos))

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
            self.notify(Event("update", kwargs))

        @property
        def pos(self):
            return self.get_component('position').pos

    player = Player((100, 100))
    player.update(dt=1000)
    print(player.pos.components)
    player.notify(Event("move", {"dr": [10, 0]}))
    assert(player.pos[0] == 110)
    player.update(dt=1000)
    print(player.pos.components)
    # import pdb
    # pdb.set_trace()
    player.notify(Event("kick", {"dv": Vector(10, 0)}))
    assert(player.get_component("physics").vector[0] == 10)
    player.update(dt=1000)
    print(player.pos.components)
    player.notify(Event("turn", {"d0": -90}))
    player.notify(Event("accel", {"dv": 100}))
    player.update(dt=1000)
    print(player.pos.components)
    print(player.get_component("physics").vector.components)

if __name__ == '__main__':
    try:
        pygame.init()
        test()
    finally:
        pygame.quit()
