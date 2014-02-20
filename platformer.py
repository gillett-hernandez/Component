#!/usr/bin/env python

import pygame
import sys
from pygame.locals import *

SCREEN=pygame.Rect((0,0),(800,640))

GRAV=0.5

#do rect.topleft or rect.center or what?

def dummyrect():
    return pygame.Rect((0,0),(0,0))

class Object(pygame.sprite.Sprite):
    def __init__(self,pos,image=None):
        super(Object, self).__init__()
        if image==None:
            self.visible=False
        else:
            self.visible=True
        self.image=image
        self.rect=self.image.get_rect() if self.visible else dummyrect()
        self.rect.topleft=pos
        self.pos=pos

    def update(self):
        pass

class Movable(Object):
    def __init__(self,pos,vector=[0,0],image=None):
        super(Movable, self).__init__(pos,image)
        self.gravity=True
        self.vector=vector
        # self.rect
        # self.image
        # self.pos
    def move(self,relPos):
        self.pos[0]+=relPos[0]
        self.pos[1]+=relPos[1]
    def moveTo(self,pos):
        self.pos=pos
    def nMove(self):
        self.pos[0]+=self.vector[0]
        self.pos[1]+=self.vector[1]
    def update(self):
        self.nMove()
        self.accelerate()
        self.rect.topleft=self.pos
    def accelerate(self,vector=None):
        if vector!=None:
            self.vector[0]+=vector[0]
            self.vector[1]+=vector[1]
        if self.gravity:
            self.vector[1]+=GRAV
    def draw(self,screen):
        screen.blit(self.image,self.rect)

class Player(Movable):
    def __init__(self,pos,vector=[0,0],image=None):
        if image==None:
            image=pygame.Surface((32,64))
            image.fill((255,255,255))
        super(Player,self).__init__(pos,vector,image)


class Immovable(Object):
    """Immovable Object"""
    def __init__(self, pos, image):
        super(Immovable, self).__init__(pos, image)
        self.pos = pos

class Platform(Immovable):
    """A Platform"""
    def __init__(self, pos, image=None):
        super(Platform, self).__init__(pos,image)
        if image==None:
            self.visible=False
        else:
            self.image=image
    def update(self):
        pass
class ExitBlock(Immovable):
    """docstring for ExitBlock"""
    def __init__(self, pos, image=None):
        super(ExitBlock, self).__init__(pos,image)
        self.pos = pos

pygame.init()

screen=pygame.display.set_mode(SCREEN.size)

bg=pygame.Surface((SCREEN.size))
bg.fill((127,127,127))


platforms=pygame.sprite.Group()
npcs=pygame.sprite.RenderUpdates()

x = y = 0
level = [
"WWWWWWWWWWWWWWWWWWWWWWWWW",
"WP W                    W",
"W  WWWWW                W",
"W  W    W               W",
"W  W     W    W         W",
"W  W      W   W         W",
"W  W         WW    WWWWWW",
"W  W        W W         W",
"W  W       W  W         W",
"W  W      W   WWW       W",
"W  W     W    WW        W",
"W  W WW       WWW      WW",
"W  WWWWW      WWWW    WWW",
"W       W     WWWWW  WWWW",
"W        WW   W         W",
"W            WW         W",
"W          WW W         W",
"W       WW    W         W",
"W      WWWW   WE        W",
"WWWWWWWWWWWWWWWWWWWWWWWWW",]
# build the level
platform_image=pygame.Surface((32,32))
platform_image.fill((192,192,192))
exit_image=pygame.Surface((32,32))
exit_image.fill((0,0,255))
for row in level:
    for col in row:
        if col == "W":
            w = Platform((x, y),platform_image)
            platforms.add(w)
        if col == "E":
            e = ExitBlock((x, y),exit_image)
            platforms.add(e)
        if col == "P":
            p = [x,y]
        x += 32
    y += 32
    x = 0
player=Player(p)

clock=pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            sys.exit()
            break

    screen.blit(bg,(0,0))

    player.update()
    player.draw(screen)

    npcs.update()
    npcs.draw(screen)

    platforms.update()
    platforms.draw(screen)


    pygame.display.flip()

    clock.tick(60)

pygame.quit()
