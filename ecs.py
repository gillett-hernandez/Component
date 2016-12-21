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

print(C.G)

systems = []


class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, pos, size):
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect().move(pos)


class Entity(object):
    def __init__(self):
        self.components = {}

    def get_component(self, name):
        return self.components[name]


class Component(object):
    def __init__(self, obj):
        self.system.add_component(self)
        self.obj = obj


class System(object):
    def __init__(self):
        systems.append(self)
        self.components = []

    def add_component(self, component):
        self.components.append(component)


class _EventSystem(System):
    def __init__(self):
        super(_EventSystem, self).__init__()
        self.callbacks = {}

    def register(self):  # are "register" and "listen" one and the same
        pass

    def trigger(self):  # "raise" or "notify"?
        pass


class PhysicsSystem(System):
    events = ['update'] # type: List[str]

    def __init__(self):
        super(PhysicsSystem, self).__init__()
        # PhysicsSystem.events

    # still called self because it will be called on components so its useful to have the "self" mindset
    @staticmethod
    def update(self, **kwargs):
        self.pos[1] += 1

    def add(self, component):
        self.components.append(component)


class InputSystem(System):
    events = [] # type: List[str]

    def __init__(self):
        super(InputSystem, self).__init__()
        InputSystem.events


class SpriteSystem(System):
    events = ['update'] # type: List[str]

    def __init__(self):
        super(SpriteSystem, self).__init__()
        SpriteSystem.events

    @staticmethod
    def update(self, **kwargs):
        self.rect.topleft = self.physics.pos


class PhysicsComponent(Component):

    system = PhysicsSystem()

    def __init__(self, obj, pos):
        super(PhysicsComponent, self).__init__(obj)
        self.pos = list(pos)
        PhysicsComponent.system.add(self)


class InputController(Component):

    system = InputSystem()

    def __init__(self, obj):
        super(InputController, self).__init__(obj)


class SpriteComponent(Component):

    system = SpriteSystem()

    def __init__(self, obj):
        super(SpriteComponent, self).__init__(obj)
        self.physics = self.obj.get_component(C.PHYSICS)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.

        self.chunks = []

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y

        self.rect = pygame.Rect((0,0),(0,0))

    def set_type(self, type):
        grid = get_grid_for(type)
        color = get_color_for(type)
        for y in range(4):
            for x in range(4):
                if grid[y][x]:
                    image = pygame.Surface([16, 16])
                    image.fill(color)
                    rect = pygame.image.get_rect()
                    rect.topleft = (x, y)
                    sprite = pygame.Sprite(image, rect)
                    self.chunks.append(sprite)

    def blit(self, surface):
        for sprite in self.chunks:
            surface.blit(sprite.image, sprite.rect)



class Player(Entity):
    def __init__(self, pos):
        super(Player, self).__init__()
        self.components[C.PHYSICS] = PhysicsComponent(self, pos)
        self.components[C.INPUT] = InputController(self)
        self.components[C.SPRITE] = SpriteComponent(self)

    def __getattr__(self, name):
        candidates = []
        for component in self.components.values():
            try:
                candidates.append(getattr(component, name))
            except AttributeError:
                pass
        for candidate in candidates:
            if candidate is None:
                candidates.remove(candidate)
        if len(candidates) < 1:
            raise AttributeError(name)
        return candidates[0]


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

        for system in systems:
            update = getattr(system, "update", False)
            if update is not False:
                for component in system.components:
                    update(component)
        screen.blit(bg.image, bg.rect)
        screen.blit(player.image, player.rect)
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()
