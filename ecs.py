#!/usr/bin/python

# theoretical outline of the Entity Component System
# an Entity holds components and defines interactions between them.
# a Component holds data
# a System acts on components and alters their data.


import sys
from collections import namedtuple

import pygame
import pygame.locals as pgl


class Namespace(object):
    def __init__(self):
        self.__dict__ = {}

    def __getattr__(self, name):
        if name not in self.__dict__:
            raise AttributeError("")
        else:
            return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

C = Namespace()
C.G = 3 # type: int
C.SCREEN = pygame.Rect((0, 0), (640, 480))
C.PHYSICS = 'PHYSICS'
C.INPUT = 'INPUT'
C.SPRITE = 'SPRITE'
C.keybinding = "keyconfig.json"
C.blocksize = 16

print(C.G)

ENTITY_COUNT = 1000
COMPONENT_NONE          = 0
COMPONENT_POSITION      = 1 << 0
COMPONENT_PHYSICS       = 1 << 1
COMPONENT_INPUT         = 1 << 2
COMPONENT_SPRITE        = 1 << 3
COMPONENT_LAYEREDSPRITE = 1 << 4

class EntityAllocationError(Exception):
    def __init__(self, msg):
        super(EntityAllocationError, self).__init__(msg)


class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, pos, size):
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect().move(pos)

class Entity(object):
    __slots__ = ["id"]
    def __init__(self, e_id, mask):
        self.id = e_id
        World.mask[self.id] = mask

    @staticmethod
    def static_get_component(e_id, cname):
        return World.components[cname][e_id]

    def get_component(self, cname):
        return self.static_get_component(self.id, cname)

    @staticmethod
    def static_set_component(e_id, cname, component):
        assert component.id == e_id, (e_id, cname, component)
        World.components[cname][e_id] = component

    def set_component(self, cname, component):
        self.static_set_component(self.id, cname, component)

    @classmethod
    def makeEntity(cls):
        for entity in range(ENTITY_COUNT):
            if World.mask[entity] == COMPONENT_NONE:
                return entity
        else:
            raise EntityAllocationError()


class Component(object):
    __slots__ = ["id"]
    def __init__(self, id, **data):
        self.id = id
        for k, v in data.items():
            setattr(self, k, v)


class System(object):
    @classmethod
    def update(cls):
        for entity in range(ENTITY_COUNT):
            if (World.mask[entity] & cls.mask == cls.mask):
                # quick wrapper for convenience
                cls.c_update(Entity(entity, World.mask[entity]))


class _EventSystem(System):
    def __init__(self):
        super(_EventSystem, self).__init__()
        self.callbacks = {}

    def register(self):  # are "register" and "listen" one and the same
        pass

    def trigger(self):  # "raise" or "notify"?
        pass


class PositionSystem(System):
    mask = COMPONENT_POSITION

    @staticmethod
    def c_update(entity):
        pass


class PhysicsSystem(System):
    events = ['update'] # type: List[str]
    mask = COMPONENT_POSITION | COMPONENT_PHYSICS

    @staticmethod
    def c_update(entity):
        p = entity.get_component("position")
        v = entity.get_component("physics")

        v.y -= v.grav

        p.x += v.x
        p.y += v.y


class InputSystem(System):
    events = [] # type: List[str]
    mask = COMPONENT_INPUT
    queue = []

    @staticmethod
    def c_update(entity):
        pass


class SpriteSystem(System):
    events = ['update'] # type: List[str]
    mask = COMPONENT_SPRITE | COMPONENT_POSITION

    @staticmethod
    def c_update(entity):
        s = entity.get_component("sprite")
        p = entity.get_component("position")
        s.rect.topleft = p.pos

    @staticmethod
    def c_draw(entity, surface):
        s = entity.get_component("sprite")
        p = entity.get_component("position")
        surface.blit(s.image, (p.x, p.y))


class LayeredSpriteSystem(SpriteSystem):
    events = ["update"]
    mask = COMPONENT_LAYEREDSPRITE | COMPONENT_POSITION

    @staticmethod
    def c_update(entity):
        # component keeps the same internal name "sprite"
        # but has multiple layers
        s = entity.get_component("sprite")
        p = entity.get_component("position")
        # update each layer individually
        for layer in s.layers:
            layer.rect.topleft = (p.x, p.y)

    @staticmethod
    def c_draw(entity, surface):
        s = entity.get_component("sprite")
        p = entity.get_component("position")
        # draw each layer individually
        for layer in s.layers:
            assert hasattr(layer, "image")
            surface.blit(layer.image, layer.rect)

    @staticmethod
    def set_type(entity, type):
        s = entity.get_component("sprite")
        grid = get_grid_for(type)
        color = get_color_for(type)
        for y in range(4):
            for x in range(4):
                if grid[y][x]:
                    image = pygame.Surface([C.blocksize, C.blocksize])
                    image.fill(color)
                    rect = pygame.image.get_rect()
                    rect.topleft = (x, y)
                    sprite = pygame.Sprite(image, rect)
                    s.layers.append(sprite)


class World(object):
    mask = [0]*ENTITY_COUNT
    components = {
        "position": [None]*ENTITY_COUNT,
        "physics": [None]*ENTITY_COUNT,
        "sprite": [None]*ENTITY_COUNT,
        "lsprite": [None]*ENTITY_COUNT
    }
    systems = {
        "position": PositionSystem,
        "physics": PhysicsSystem,
        "sprite": SpriteSystem,
        "lsprite": LayeredSpriteSystem
    }



grid_cache={}
def get_grid_for(type):
    pass


color_cache = {}
def get_color_for(type):
    pass


class PositionComponent(Component):
    __slots__ = ["x", "y"]
    @property
    def pos(self):
        return [self.x, self.y]

    @pos.setter
    def pos(self, value):
        self.x, self.y = value


class PhysicsComponent(Component):
    __slots__ = ["x", "y", "grav"]
    def __init__(self, id, **data):
        super().__init__(id, **data, x=0, y=0, grav=0.1)


class InputController(Component):
    __slots__ = ["keybinding"]
    def __init__(self, id, **data):
        super(InputController, self).__init__(id, **data)
        with open(C.keybinding, 'r') as fd:
            self.keybinding = json.load(fd.read())


class SpriteComponent(Component):
    __slots__ = ["image", "rect"]
    def __init__(self, id, pos, playersize, color, **data):
        super().__init__(id, **data)
        self.image = pygame.Surface(playersize)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos


class LayeredSpriteComponent(Component):
    __slots__ = ["layers"]


class Player(Entity):
    __slots__ = []
    def __init__(self, pos):
        e_id = self.makeEntity()
        super(Player, self).__init__(e_id, COMPONENT_POSITION | COMPONENT_SPRITE | COMPONENT_PHYSICS)
        self.set_component("position", PositionComponent(e_id, pos=pos))
        self.set_component("physics", PhysicsComponent(e_id))
        self.set_component("sprite", SpriteComponent(e_id, pos=pos, playersize=[16,32], color=(128,128,128)))


if __name__ == '__main__':
    pygame.init()

    screen = pygame.display.set_mode((C.SCREEN.width, C.SCREEN.height))
    clock = pygame.time.Clock()

    bg = Sprite((0, 0), C.SCREEN.size)

    player = Player([120, 120])

    # i = 0
    dt = 1.0/6.0

    while True:
        for event in pygame.event.get():
            if event.type == pgl.QUIT:
                sys.exit()
                pygame.quit()
            elif event.type == pgl.KEYDOWN:
                if event.key in [pgl.K_ESCAPE, pgl.K_q]:
                    sys.exit()
                    pygame.quit()

        screen.blit(bg.image, bg.rect)
        World.systems["sprite"].c_draw(player, screen)
        for _,system in World.systems.items():
            update = getattr(system, "update", False)
            if update is not False:
                update()
            else:
                print("system {} did not have a update method".format(system))
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()
