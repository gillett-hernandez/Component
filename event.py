from component import Component


import constants
import logging

logging.basicConfig(**constants.logging_setup)


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

