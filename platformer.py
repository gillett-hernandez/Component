#!/usr/bin/env python

import pygame
import sys
from pygame.locals import *

MESSAGE=USEREVENT+1

GRAV=0.5

#do rect.topleft or rect.center or what?

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


class Movable(pygame.sprite.DirtySprite):
    def __init__(self,pos,vector=[0,0],image=None):
        super(Movable, self).__init__()
        self.gravity=True
        self.vector=vector
        if image==None:
            self.visible=False
        else:
            self.visible=True
        self.image=image
        self.rect=self.image.get_rect() if self.visible else dummyrect()
        self.rect.topleft=pos
        self.pos=pos
    def move(self,relPos):
        self.pos[0]+=relPos[0]
        self.pos[1]+=relPos[1]
    def moveTo(self,pos):
        self.pos=pos
    def nMove(self):
        self.pos[0]+=self.vector[0]
        self.pos[1]+=self.vector[1]
    def update(self,keys):
        self.nMove()
        self.dirty=1
        left=keys[K_LEFT]
        right=keys[K_RIGHT]
        down=keys[K_DOWN]
        up=keys[K_UP]
        collided=self.collision(platforms)
        self.collide(collided)
        if left:
            self.accelerate([-1,0])
        if right:
            self.accelerate([1,0])
        if up and self.onGround:
            self.accelerate([0,-5])
            self.gravity=True
            self.onGround=False

        self.accelerate()
        self.rect.topleft=self.pos
        
    def collide(self,sprite):
        if sprite!=None:
            if sprite.rect.bottom<self.rect.bottom: #sprite is above
                self.vector[1]=0
                self.rect.top=sprite.rect.bottom

            if sprite.rect.top>self.rect.top: #sprite is below
                self.vector[1]=0
                self.gravity=False
                self.onGround=True
                self.rect.bottom=sprite.rect.top

            if sprite.rect.right<self.rect.right:
                self.vector[0]=0
                self.rect.left=sprite.rect.right

            if sprite.rect.left>self.rect.left: #do better checking for sprites being left right up or down.
                self.vector[0]=0
                self.rect.right=sprite.rect.left

    def collision(self,walls):
        for sprite in iter(walls):
            if pygame.sprite.collide_rect(self,sprite):
                return sprite
    def accelerate(self,vector=None):
        if vector!=None:
            self.vector[0]+=vector[0]
            self.vector[1]+=vector[1]
        if self.gravity:
            self.vector[1]+=GRAV
    def collision_fast(self):
        """To be used when the horizontal or vertical velocity of the object is greater the width or height of a block."""
        x,y=self.pos
        vx,vy=self.vector
        raise NotImplemented
    def draw(self,screen):
        if self.dirty==1:
            screen.blit(self.image,self.rect)
            self.dirty=0
        elif self.dirty==2:
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

def post_message(message_str,color=(0,0,0)):
    Message=pygame.event.Event(pygame.USEREVENT,{'utype':MESSAGE,'message':message_str,'color':color})
    pygame.event.post(Message)

def dummyrect():
    return pygame.Rect((0,0),(0,0))

pygame.init()
sysfont=pygame.font.SysFont(pygame.font.get_default_font(),12)

post_message("Hello world!")

platforms=pygame.sprite.Group()

x = y = 0
level = [
"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
"WWP   WW                                        WW",
"WW    WWWWWWWWWW                                WW",
"WW    WW        WW                              WW",
"WW    WW          WW        WW                  WW",
"WW    WW            WW      WW                  WW",
"WW    WW                  WWWW        WWWWWWWWWWWW",
"WW    WW                WW  WW                  WW",
"WW    WW              WW    WW                  WW",
"WW    WW            WW      WWWWWW              WW",
"WW    WW          WW        WWW                 WW",
"WW    WW  WWWW              WWWWWW            WWWW",
"WW    WWWWWWWWWW            WWWWWWWW        WWWWWW",
"WW              WW          WWWWWWWWW     WWWWWWWW",
"WW                WW        WW                  WW",
"WW                        WWWW                  WW",
"WW                    WWWW  WW                  WW",
"WW              WWWW        WW                  WW",
"WW            WWWWWWWW      WWE                 WW",
"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",]
# build the level
width=len(level[0])*32
height=len(level)*32
SCREEN=pygame.Rect((0,0),(width,height))
screen=pygame.display.set_mode(SCREEN.size)
pygame.display.set_caption('Platformer')
bg=pygame.Surface((SCREEN.size))
bg.fill((127,127,127))
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

movables=pygame.sprite.LayeredUpdates()

keys=[bool(b) for b in list(pygame.key.get_pressed())]
# print(keys)

clock=pygame.time.Clock()

while True:
    screen.blit(bg,(0,0))
    # if pygame.event.peek([QUIT,KEYDOWN,KEYUP,USEREVENT]):
    i=0
    for event in pygame.event.get([QUIT,KEYDOWN,KEYUP,USEREVENT]):
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        if event.type==KEYDOWN:
            # if not keys.has_key(event.key):
            keys[event.key]=True
            # keys.append(event.key)
            continue
        if event.type==KEYUP:
            keys[event.key]=False
            # keys.remove(event.key)
            continue
        if event.type==USEREVENT:
            # print(event)
            if event.utype==MESSAGE:
                # print(event)
                # help(sysfont.render)
                # print(event.message)
                text=sysfont.render(event.message,False,event.color)
                if type(text)!=pygame.Surface:
                    print(text)
                screen.blit(text,(0,i*32))
                i+=1
                pygame.event.post(event)
        
    pygame.event.pump()


    player.update(keys)
    player.draw(screen)

    movables.update()
    movables.draw(screen)

    platforms.update()
    platforms.draw(screen)


    pygame.display.flip()

    clock.tick(60)

pygame.quit()
