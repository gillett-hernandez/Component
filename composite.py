#!/usr/bin/env python

import logging
import json
import math

# from miscfunc import lengthdir_x, lengthdir_y, point_distance, point_direction, to_mag_dir, vector_transform, normalize

import pygame


class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item


with open("./lf_constants.json", 'r') as fd:
    constants = DotDict(json.load(fd))

with open("./lf_keyconfig.json", 'r') as fd:
    keyconfig = DotDict(json.load(fd))

logging.basicConfig(**constants.logging_setup)


def lengthdir_x(v):
    # assert v.type == v.types.magdir
    # v[0] is magnitude
    # v[1] is angle
    return v[0] * math.cos(v[1])


def lengthdir_y():
    # assert v.type == v.types.magdir
    # v[0] is magnitude
    # v[1] is angle
    return v[0] * math.sin(v[1])


def void(*args, **kwargs):
    return


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
    return point_distance(v1, v2)


def vproj(v1, v2):
    return distance(v1)*math.cos((math.atan2(v2[1], v2[0])-math.atan2(v1[1], v1[0])))


def normalize(v, euclidean=True):
    if euclidean:  # euclidean vectors are vectors in the form magnitude, direction
        return [1, v[1]]
    else:
        x, y = v
        m = math.sqrt(x**2+y**2)
        if m == 0:
            return [x, y]
        return [x/m, y/m]


class Event:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data

    def __repr__(self):
        return ("<Event instance with keyword:"
                " {keyword} and data: {data}>".format(keyword=str(self.keyword),
                                                      data=str(self.data)))


class Component(object):
    def __init__(self, obj):
        super(Component, self).__init__()
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
            for _id, func in self.callbacks[event.keyword].items():
                func(**event.data)
        except AttributeError as e:
            print(event, func)
            raise e

    def remove_events(self):
        logging.debug("called remove_events from " +
                      "{self.__class__.__name__}".format(self=self))
        for eventid in self.attached_events:
            self.obj.detach_event(eventid)


class Composite(Component):
    def __init__(self):
        super(Composite, self).__init__(self)
        self.components = {}

    def __len__(self):
        return len(self.components)

    def __repr__(self):
        return self.__class__.__name__

    def __getattr__(self, name):
        for cname in self.components:
            if hasattr(self.components[cname], name):
                return getattr(self.components[cname], name)
        else:
            raise AttributeError(name)

    def attach_component(self, name, component, *initargs):
        assert issubclass(component, Component)
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

    def dispatch_event(self, event):
        newcomponents = []
        for name in self.components.copy():
            try:
                cname = self.components[name].dispatch_event(event)
                if cname is not None:
                    newcomponents.append(cname)
            except KeyError:  # catches the case of a dispatched event causing a component to be removed.
                #               really janky
                pass
                # raise e
        while len(newcomponents) > 0:  # this should take care of new components who like to add new components. although could present a vulnerability.
            for name in newcomponents[:]:
                cname = self.components[name].dispatch_event(event)
                if cname is not None:
                    newcomponents.append(cname)
                newcomponents.remove(name)

    def notify(self, event):
        self.dispatch_event(event)


class Reaction:
    def __init__(self, f):
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


class EventHandler(Component):
    """Handles events. A collection of reactions"""
    def __init__(self, obj):
        super(EventHandler, self).__init__(obj)
        # obj.attach_event('update', self.update)

    def add_tap(self, hear, react, func):
        print("add_tap called", hear, react, func)

        def reaction(**kwargs):
            # print("reaction called ")
            if kwargs['press'] is True:
                self.obj.dispatch_event(Event(react, func(**kwargs)))
                return
        self.attach_event(hear, reaction)

    def add_hold(self, hear, react, reaction):
        # hear is the event keyword that this reaction reacts to
        # react is the event keyword that the reaction emits
        # reaction is the reaction object
        #
        print("add_hold called", hear, react, reaction)
        assert isinstance(reaction, Reaction)
        print(reaction)

        def holdreaction(**kwargs):
            assert isinstance(reaction, Reaction)
            pressed = kwargs['press']
            logging.debug("reaction with pressed as {pressed}".format(
                          pressed=pressed))
            if pressed:

                logging.debug(
                    "reaction if branch right before attach_component")
                # print(reaction)
                reaction.start(**kwargs)
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
            if callable(self.data):
                self.obj.dispatch_event(Event(self.keyword, self.data(**kwargs)))
            else:
                self.obj.dispatch_event(Event(self.keyword, self.data))

    def update1(self, **kwargs):
            if callable(self.data):
                self.obj.dispatch_event(Event(self.keyword, self.data(**kwargs)))
            else:
                self.obj.dispatch_event(Event(self.keyword, self.data))


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
                      "InputController.keydown").format(key=pygame.key.name(key)))
        if key not in self.reactions:
            logging.warn("{key} does not have a mapped reaction in InputController".format(key=pygame.key.name(key)))
        if key in self.reactions:
            logging.debug(self.reactions[key])
            reaction = self.reactions[key]
            reaction[1].update({'press': True})
            logging.debug(reaction)
            self.obj.dispatch_event(Event(reaction[0], reaction[1]))

    def keyup(self, **kwargs):
        key = kwargs['key']
        logging.debug(("keydown {key} from " +
                      "InputController.keydown").format(key=pygame.key.name(key)))
        if key not in self.reactions:
            logging.warn("{key} does not have a mapped reaction in InputController".format(key=pygame.key.name(key)))
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
        assert self.p is not None
        self.gravity = kwargs.get("gravity", constants.GRAVITY)
        self.frictionless = kwargs.get("frictionless", False)
        self.weightless = kwargs.get("weightless", False)

        self.vector = kwargs['vector'] if 'vector' in kwargs else [0, 0]
        self.dir = 270
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

    def collide(self, sprite):
        # s = kwargs["sprite"]
        s = sprite
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

    def move(self, dr=[0, 0]):
        self.p.pos = vadd(self.p.pos, dr)

    def kick(self, dv=[0, 0], restrict_velocity=True):

        if restrict_velocity:
            v = vadd(self.vector, dv)
            # normalize to the maxspeed
            v = normalize(v, False)
            v = vmul(v, constants.maxspeed**0.5)
            self.vector = v
        else:
            self.vector = vadd(self.vector, dv)

        logging.info(("kick called in PhysicsComponent {dv}." +
                     " current vector is {v}").format(dv=dv, v=self.vector))

    def turn(self, d0):
        logging.debug("calling turn from PhysicsComponent, d0={0}".format(d0))
        self.dir -= d0

    def accel(self, dv=None, dir=None):
        assert dv is not None
        if dir is None:
            dir = self.dir

        v = [lengthdir_x(dv, dir), lengthdir_y(dv, dir)]

        self.kick(dv=v)

    def bounce_horizontal(self):
        self.vector[0] *= -1

    def bounce_vertical(self):
        self.vector[1] *= -1

    def toggle_gravity(self):
        self.weightless = not self.weightless

    def change_gravity(self, g):
        self.gravity = g

    def outside_top(self):
        pass

    def outside_bottom(self):
        # self.p.pos = [self.p.xstart, self.p.ystart]
        if self.p.pos[1] > constants.SCREEN_HEIGHT:
            self.change_gravity(-constants.GRAVITY*4)

    def outside_sides(self):
        raise NotImplementedError
        if self.vector[0] > 0:
            self.p.pos[0] = 0
        else:
            self.p.pos[0] = constants.LEVEL_WIDTH

    def update(self, **kwargs):
        self.pdir = self.dir
        dt = kwargs['dt']
        x, y = self.p.pos
        if not (0 < y < constants.SCREEN_HEIGHT):
            self.outside_top_or_bottom()
        else:
            self.change_gravity(constants.GRAVITY)

        # if self is outside screen side barriers
        if not (0 < x < constants.SCREEN_WIDTH):
            self.outside_sides()

        if not self.weightless:
            self.kick(dv_y=constants.GRAVITY)

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

        if not self.frictionless:
            self.vector[0] += -self.vector[0]*constants.friction
            self.vector[1] += -self.vector[1]*constants.friction
        self.vector[0] = round(self.vector[0], 9)
        self.vector[1] = round(self.vector[1], 9)
        # only restrict when accellerating due to key input,
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

        self.p = self.obj.get_component('position')
        self.a = self.obj.get_component('physics')
        self.image = pygame.image.load(imagepath).convert_alpha()
        self.rect = self.image.get_rect()
        self.obj.image = self.image
        self.obj.rect = self.obj.image.get_rect()
        self.obj.rect.center = self.p.pos

    def update(self, **kwargs):
        self.obj.image = pygame.transform.rotozoom(self.image, -self.a.dir-90, 1)
        # print(self.obj.rect, self.image.get_rect(), self.rect)
        self.obj.rect = self.obj.image.get_rect(center=self.rect.center)
        self.rect.topleft = self.p.pos
        # self.obj.rect.topleft = self.p.pos
        # if self.obj.rect.topleft is not self.p.pos:


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


    class Player(Composite):
        width, height = 16, 16

        def __init__(self, pos):
            super(Player, self).__init__()
            self.attach_component('position', PositionComponent, pos)
            self.attach_component('physics', PhysicsComponent) 
            self.attach_component('input', InputController)
            self.attach_component('handler', PlayerEventHandler)
            # self.attach_component('sprite', SpriteFromImage,
            #                       (os.path.join(".",
            #                                     "resources",
            #                                     "images",
            #                                     "playerimage.png")))
            # where to attach the special behavior for the sprite logic.
            # here?
            # self.mask = pygame.mask.from_surface(self.image)
            # assert(self.mask.count() > 0

        def __getattr__(self, name):
            if name == "pos" or name == "x" or name == "y":
                return getattr(self.get_component("position"), name)
            for cname in self.components:
                # print(self.components[cname], hasattr(self.components[cname], name))
                if hasattr(self.components[cname], name):
                    # print("getattr {name} from {cname}".format(name=name, cname=cname))
                    return getattr(self.components[cname], name)
            res = super(Player, self).__getattr__(name)
            if res is not None:
                return res
            else:
                raise AttributeError(name)

        def add_collision_check(self, group, **kwargs):
            proximity = kwargs.get('proximity', self.height+10)
            self.attach_component('proximity_{group.__class__.__name__}'.format(group=group), ProximitySensor, group, proximity)

        def update(self, **kwargs):
            # logging.debug('update in Player')
            dt = kwargs['dt']
            self.dispatch_event(Event("update", {"dt": dt}))
            vector = self.get_component('physics').vector
            pdir = self.get_component('physics').dir
            if "ScreenLocator" in globals():
                pygame.draw.line(ScreenLocator.getScreen(), (255, 0, 0), self.rect.center, [self.rect.center[0]+lengthdir_x(100, pdir), self.rect.center[1]+lengthdir_y(100, pdir)])
                pygame.draw.line(ScreenLocator.getScreen(), (0, 0, 255), self.rect.center, [self.rect.center[0]+vector[0], self.rect.center[1]+vector[1]])

        def dumpstate(self):
            pass


    player = Player((100, 100))
    print(dir(player.get_component("physics")))
    player.toggle_gravity()
    player.update(dt=1000)
    print(player.pos)
    player.notify(Event("move", {"dr": [10,0]}))
    player.update(dt=1000)
    print(player.pos)
    player.notify(Event("kick", {"dv": [10,0]}))
    player.update(dt=1000)
    print(player.pos)
    player.update(dt=1000)
    print(player.pos)
    player.update(dt=1000)
    print(player.pos)
    player.update(dt=1000)
    print(player.pos)

if __name__ == '__main__':
    try:
        pygame.init()
        test()
    finally:
        pygame.quit()
