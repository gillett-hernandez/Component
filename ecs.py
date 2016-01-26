#!/usr/bin/python

# theoretical outline of the Entity Component System
# an Entity holds components and defines interactions between them.
# a Component holds data
# a System acts on components and alters their data.


import sys
from collections import namedtuple

import pygame
from pygame.locals import *


class Namespace(object):
    def __init__(self):
        self.__dict__ = {}

    def __getattr__(self, name):
        if name not in self.__dict__:
            raise AttributeError("")
        else:
            return self.__dict__[name]

C = Namespace()
C.G = 3
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

    def register():  # are "register" and "listen" one and the same
        pass

    def trigger():  # "raise" or "notify"?
        pass


class PhysicsSystem(System):
    events = ['update']

    def __init__(self):
        super(PhysicsSystem, self).__init__()
        PhysicsSystem.events


class InputSystem(System):
    events = []

    def __init__(self):
        super(InputSystem, self).__init__()
        InputSystem.events


class SpriteSystem(System):
    events = ['update']

    def __init__(self):
        super(SpriteSystem, self).__init__()
        SpriteSystem.events


class PhysicsComponent(Component):

    system = PhysicsSystem()

    def __init__(self, obj, pos):
        super(PhysicsComponent, self).__init__(obj)
        self.pos = pos
        self.vec = [0, 0]
        self.weightless = False


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
        self.image = pygame.Surface([20, 20])
        self.image.fill(pygame.Color(255, 0, 0))

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.topleft = self.physics.pos


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

    i = 0
    dt = 1/60

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
                pygame.quit()
            elif event.type == KEYDOWN:
                if event.key in [K_ESCAPE, K_Q]:
                    sys.exit()
                    pygame.quit()

        for system in systems:
            update = getattr(system, "update", False)
            if update is not False:
                update(dt=dt)
        screen.blit(bg.image, bg.rect)
        screen.blit(player.image, player.rect)
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()
