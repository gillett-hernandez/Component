#!/usr/bin/python

import logging

from miscfunc import lengthdir_x, lengthdir_y, point_distance, point_direction
import constants
import keyconfig

import pygame

logging.basicConfig(**constants.logging_setup)


def void(*args, **kwargs):
    return


def yvel_to_jump(jumpspeed):
    return -jumpspeed


def sign(n):
    return int(n/abs(n))


def vadd(v1, v2):
    return [v1[0]+v2[0], v1[1]+v2[1]]


def vsub(v1, v2):
    return [v1[0]-v2[0], v1[1]-v2[1]]


def vmul(v1, m):
    return [v1[0]*m, v1[1]*m]


def vdot(v1, v2):
    return v1[0]*v2[0]+v1[1]*v2[1]


def distance(v1, v2=[0, 0]):
    return point_distance(v1[0], v2[0], v1[1], v2[1])


class Event:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data

    def __repr__(self):
        return "<Event instance with keyword:" +\
            " {keyword} and data: {data}>".format(keyword=str(self.keyword),
                                                  data=str(self.data))


class Component(object):
    def __init__(self, obj):
        super(Component, self).__init__()
        self.attached_events = []
        self.obj = obj
        self.callbacks = {}

    def attach_event(self, keyword, callback):
        if keyword not in self.callbacks:
            self.callbacks[keyword] = {}
        _id = hash(callback)
        self.callbacks[keyword][_id] = callback
        logging.debug(("attaching event {keyword} " +
                       "with callback {callback}").format(
                      keyword=keyword, callback=callback))
        return _id

    def __repr__(self):
        return ("<{self.__class__.__name__} " +
                "attached to {self.obj!r}>").format(self=self)

    def __str__(self):
        return repr(self)

    def detach_event(self, _hash):
        for keyword in self.callbacks:
            for _id in self.callbacks[keyword]:
                if _id == _hash:
                    logging.debug("calling detach_event on {callback}".format(callback=self.callbacks[keyword][_id]))
                    del self.callbacks[keyword][_id]
                    return

    def dispatch_event(self, event):
        assert(event.data is not None)
        if event.keyword is not "update":
            logging.debug("dispatching event {event!r}".format(event=event))
        if event.keyword not in self.callbacks:
            return
        for _id, func in self.callbacks[event.keyword].items():
            func(**event.data)

    def remove_events(self):
        logging.debug("called remove_events from " +
                      "{self.__class__.__name__}".format(self=self))
        for eventid in self.attached_events:
            self.obj.detach_event(eventid)

    def break_event(self):
        pass


class Composite(Component):
    def __init__(self):
        super(Composite, self).__init__(self)
        self.components = {}

    def __len__(self):
        return len(self.components)

    def attach_component(self, name, component, *initargs):
        assert isinstance(component, Component), super(Component, component)
        logging.debug("attaching component with name: " +
                      "{name} {component!r}{initargs!s}".format(
                          name=name, component=component, initargs=initargs))
        self.components[name] = component(self, *initargs)

    def get_component(self, name):
        return self.components[name]

    def detach_component(self, name):
        logging.debug("calling detach_component on {name}".format(name=name))
        self.components[name].remove_events()
        del self.components[name]

    def notify(self, event):
        if event.type == pygame.KEYDOWN:
            self.dispatch_event(Event('keydown', {'key': event.key}))
        elif event.type == pygame.KEYUP:
            self.dispatch_event(Event('keyup', {'key': event.key}))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.dispatch_event(Event('mousebuttondown', {'key': event.key}))

    def __repr__(self):
        return self.__class__.__name__


class PositionComponent(Component):
    def __init__(self, pos):
        super(self, PositionComponent).__init__()
        self.x, self.y = pos

    @property
    def pos(self):
        return self.x, self.y
    @pos.setter
    def pos(self, value):
        self.x, self.y = value    


class Player(Composite):
    def __init__(self, pos):
        super(Player, self).__init__()
        self.attach_component('position', PositionComponent, pos)

    def update(self):
        self.dispatch_event("update")
        self.get_component("position").x += 1

player=Player((100, 100))

player.update()
