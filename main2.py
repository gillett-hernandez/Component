#!/usr/bin/python

# imports

import sys
import os
import math
import pygame
import miscfunc
from pygame.locals import *

# game constants

VERSION = [0, 0, 0]
GRAV = .25
SCREENSIZE = WIDTH, HEIGHT = 640, 480
FRAMERATE = 60
POSTMESSAGE = USEREVENT+1

# resource-handling functions


def load_image(name):
    """ Load image and return image object and rect"""
    fullname = os.path.abspath(os.path.join("resources", "images", name))
    image = pygame.image.load(fullname)
    if image.get_alpha() is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image, image.get_rect()


def load_sound(name):
    """ Load sound and return sound object"""
    fullname = os.path.abspath(os.path.join("resources", "sounds", name))
    sound = pygame.mixer.Sound(fullname)
    return sound


def load_music(name):
    """ Load music to prepare for playback"""
    fullname = os.path.abspath(os.path.join("resources", "sounds", name))
    pygame.mixer.music.load(fullname)


def make_channel(idNum):
    if idNum < pygame.mixer.get_num_channels() and idNum > 0 and\
       type(idNum) is int:
        channel = pygame.mixer.Channel(idNum)
    else:
        print('\nid is too big, less than zero, or not an integer')
    return channel

# convienence functions


def vadd(x, y):
    return [x[0]+y[0], x[1]+y[1]]


def vsub(x, y):
    return [x[0]-y[0], x[1]-y[1]]


def vdot(x, y):
    return x[0]*y[0]+x[1]*y[1]


def make3dPointList(pointList, angle):
    make3dFromGivenAngle = lambda point: miscfunc.make3D(point, angle)
    return map(make3dFromGivenAngle, pointList)


def split_spritesheet(imageName, numImages):
    sheet, rect = load_image(imageName)
    width, height = rect.size
    singleWidth, singleHeight = width/numImages, height
    singleSize = singleWidth, singleHeight
    assert(width % numImages == 0)
    sprite_images = []
    for i in range(numImages):
        sprite_images[i] = pygame.Surface(singleSize)
        sheet.blit(sprite_images[i], (singleWidth*i, 0),
                   (singleWidth*i, 0, singleWidth*(i+1), singleHeight))
    return sprite_images


def colorMixer(color1, color2, ratio=(1, 1)):
    ratio = (ratio[0]/(ratio[0]+ratio[1]), ratio[1]/(ratio[0]+ratio[1]))
    average = lambda x, y: (ratio[0]*x+ratio[1]*y)/2
    return pygame.Color(average(color1.r, color2.r),
                        average(color1.g, color2.g),
                        average(color1.b, color2.b),
                        average(color1.a, color2.a))


def grid(width, height, func=lambda x, y: (x, y)):
    return [[func(x, y) for x in xrange(width)] for y in xrange(height)]


def outputInfo(info, pos=None, color=(0, 0, 0)):
    pygame.event.post(pygame.event.Event(POSTMESSAGE,
                      {'info': info, 'pos': pos, 'color': color}))


class StaticObject(pygame.sprite.Sprite):
    def __init__(self, worldPos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = worldPos
        self.visible = True
        self._alive = True
        # self.image_index = 0
        # self.image_speed = 0

    def _kill(self):
        self.visible = False
        self._alive = False
        self.kill()


class Wall(StaticObject):
    solid = True
    substituteImage = pygame.Surface((16, 16))
    substituteImage.fill(pygame.Color("Gray"))

    def __init__(self, worldPos, image=None):
        StaticObject.__init__(self, worldPos)
        if image is None:
            self.image = Wall.substituteImage
        else:
            self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos


class MoveableObject(pygame.sprite.DirtySprite):
    def __init__(self, pos, image, vector, mask=False):
        pygame.sprite.DirtySprite.__init__(self, self.containers)
        self.vector = vector
        self.speed = (vector[0]**2+vector[1]**2)**0.5
        if type(image) is str:
            self.image, self.rect = load_image(image)
        else:
            self.image, self.rect = image, image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.origimage = self.image
        # self.image = split_spritesheet(self.image)  # issue
        # self.pos = pos
        self.pos = pos
        self.keysPressed = []
        self.gravity = True
        self._alive = True
        self.visible = True

    def accelerate(self, force):
        self.vector[0] += force[0]*math.cos(math.radians(force[1]))
        self.vector[1] += force[0]*math.sin(math.radians(force[1]))

    def applyGravity(self):
        self.accelerate([GRAV, 270])

    def relativeMove(self, dr):
        self.pos = (self.pos[0]+dr[0], self.pos[1]+dr[1])

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value
        self.rect.center = value

    def collide(self, s):
        """Test if the sprites are colliding and
        resolve the collision in this case."""
        offset = [int(x) for x in vsub(s.pos, self.pos)]
        overlap = self.mask.overlap_area(s.mask, offset)
        if overlap == 0:
            return
        # """Calculate collision normal"""
        nx = (self.mask.overlap_area(s.mask, (offset[0]+1, offset[1])) -
              self.mask.overlap_area(s.mask, (offset[0]-1, offset[1])))
        ny = (self.mask.overlap_area(s.mask, (offset[0], offset[1]+1)) -
              self.mask.overlap_area(s.mask, (offset[0], offset[1]-1)))
        if nx == 0 and ny == 0:
            # """One sprite is inside another"""
            return
        n = [nx, ny]
        dv = vsub(s.vel, self.vel)
        J = vdot(dv, n)/(2*vdot(n, n))
        if J > 0:
            # """Can scale up to 2*J here to get bouncy collisions"""
            J *= 1.9
            self.kick([nx*J, ny*J])
            s.kick([-J*nx, -J*ny])
            return
        # """Separate the sprites"""
        c1 = -overlap/vdot(n, n)
        c2 = -c1/2
        self.move([c2*nx, c2*ny])
        s.move([(c1+c2)*nx, (c1+c2)*ny])

    def collide_group(self, group, precise=True):
        if precise:
            for sprite in pygame.sprite.spritecollide(self, group, False):
                self.collide(sprite)
        else:
            raise NotImplementedError

    def _kill(self):  # desintigrate?
        self._alive = False
        self.visible = False
        self.dirty = 1
        self.kill()

    def setRotation(self, degrees):
        self.image = pygame.transform.rotate(self.origimage, degrees)

    def rotate(self, degrees):
        self.image = pygame.transform.rotate(self.image, degrees)

    def move(self):
        self.relativeMove((self.vector[0], -self.vector[1]))
        self.apply_friction()
        if self.gravity:
            self.applyGravity()
        self.dirty = 1

    def update(self):
        if self._alive:
            self.collide_group(Wall.container)
            # elif self.collision(Enemy.containers["hostiles"]):
            pass
            self.move()
            outputInfo(str(self.pos))
            if self.pos[1] > HEIGHT:
                self.vector[1] = -self.vector[1]


class Player(MoveableObject):
    def __init__(self, pos, imageOrImageName, vector, sound_names=None):
        MoveableObject.__init__(self, pos, imageOrImageName, vector)
        self.solid = False

    def apply_friction(self):
        self.vector[0] *= .9

    def keyDownEvent(self, event):
        if (event.key == K_SPACE):
            self.vector[1] += 8
        print(pygame.key.name(event.key))

    def keyUpEvent(self, event):
        pass

    def keyHeldEvent(self):
        if (pygame.key.get_pressed()[K_w]):
            self.vector[1] += 0.5
        if abs(self.vector[0]) <= 3:
            if (pygame.key.get_pressed()[K_a]):
                self.vector[0] -= 0.5
            if (pygame.key.get_pressed()[K_d]):
                self.vector[0] += 0.5

    def mousePress(self, event):
        self.fire(self.pos, 5,
                  90-math.degrees(
                      miscfunc.point_direction(self.pos, event.pos)))

    def mouseRelease(self, event):
        pass

    def mouseHeld(self, event):
        pass

    def fire(self, pos, speed, direction):
        self.lastShot = Bullet(pos, (miscfunc.lengthdir_x(speed, direction),
                                     miscfunc.lengthdir_y(speed, direction)))

    def update(self):
        MoveableObject.update(self)
        self.keyHeldEvent()


class NPC(MoveableObject):
    def __init__(self, pos, image, vector):
        MoveableObject.__init__(self, pos, image, vector)


class Enemy(NPC):
    def __init__(self, pos, image, vector, group):
        NPC.__init__(self, pos, image, vector)


class Projectile(MoveableObject):
    def __init__(self, pos, image, vector=[0, 0]):
        MoveableObject.__init__(self, pos, image, vector)

    def move(self):
        relativeMove(self.vector)


class Bullet(Projectile):
    def __init__(self, pos, vector):
        self.image = pygame.Surface((8, 8))
        pygame.draw.circle(self.image, colors["red"],
                           self.image.get_rect().center, 4, 0)
        Projectile.__init__(self, pos, self.image, vector)
        self.rect = self.image.get_rect(center=self.pos)
        self.ttl = 600

    def move(self):
        self.relativeMove(self.vector)

    def update(self):
        self.move()

        if self.collide_group(Wall.container):
            self._kill()
        if self.ttl > 0:
            self.ttl -= 1
        else:
            self._kill()


def main(winstyle=0):
    t = 0

    font = pygame.font.Font(None, 12)
    bestdepth = pygame.display.mode_ok(SCREENSIZE, winstyle, 32)
    screen = pygame.display.set_mode(SCREENSIZE, winstyle, bestdepth)
    clock = pygame.time.Clock()

    global colors
    black = pygame.Color("Black")
    white = pygame.Color("White")
    grey = pygame.Color("Gray")  # too light
    gray = pygame.Color(156, 156, 156)
    red = pygame.Color("Red")
    green = pygame.Color("Green")
    blue = pygame.Color("Blue")
    yellow = pygame.Color("Yellow")
    orange = pygame.Color("Orange")
    colors = {"black": black, "white": white, "gray": gray, "grey": grey,
              "red": red, "green": green, "blue": blue,
              "yellow": yellow, "orange": orange}

    load_music('brave song.ogg')

    # bg, bg_rect = load_image('startBG.jpg')
    bg = pygame.Surface((WIDTH, HEIGHT)).convert()
    bg.fill(black)

    # player = Player([WIDTH/2, HEIGHT/2], playerSprites)

    playerGroup = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    walls.precise = False
    hostiles = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()

    # assign default groups to each sprite class
    # protocol for here: <name>,<additional groups>, all
    Player.containers = playerGroup, all
    Enemy.containers = hostiles, all
    Bullet.containers = projectiles, all
    Wall.containers = walls, all

    Player.container = playerGroup
    Enemy.container = hostiles
    Bullet.container = projectiles
    Wall.container = walls

    playerImage = pygame.Surface((20, 40)).convert()
    playerImage.fill(grey)
    player = Player((WIDTH/2, HEIGHT/2), playerImage, [0, 0])

    for x in xrange(WIDTH//16):
        Wall.container.add(Wall((x*16, 0)))  # top wall
        Wall.container.add(Wall((x*16, HEIGHT-16)))  # bottom wall
    for y in xrange(HEIGHT//16):
        Wall.container.add(Wall((0, y*16)))  # left wall
        Wall.container.add(Wall((WIDTH-16, y*16)))  # right wall

    texts = []
    toOutput = []
    affectedArea = pygame.Rect((0, 0), (0, 0))

    # pygame.mixer.music.play()
    screen.blit(bg, (0, 0))
    pygame.display.update()

    print('\nRunning...')
    while True:

        events = pygame.event.get()

        for event in events:
            if event.type is QUIT:
                sys.exit(0)
                return

            if event.type is MOUSEBUTTONDOWN:
                player.mousePress(event)

            if event.type is MOUSEBUTTONUP:
                player.mouseRelease(event)

            if event.type is KEYDOWN:
                player.keyDownEvent(event)

                if event.key is K_ESCAPE:
                    sys.exit(0)
                    return

                elif (pygame.key.get_mods() & (KMOD_LCTRL | KMOD_RCTRL))\
                        and (event.key is K_c):  # ctrl+c

                    sys.exit(0)
                    return

                elif event.key is K_SPACE:  # space to stop music
                    pygame.mixer.music.stop()

            if event.type is KEYUP:
                player.keyUpEvent(event)

        # end events

        all.clear(screen, bg)

        all.update()

        toOutput.append("Thing To Output")
        toOutput.append("Player vector %s + position %s" %
                        (str(player.vector), str(player.pos)))

        screen.blit(bg, affectedArea)

        height = 0
        for text in toOutput:
            textR = font.render(text, True, white)
            affectedArea.union_ip(screen.blit(textR, (0, height)))
            height += font.size(text)[1]

        texts.append(affectedArea)
        toOutput = []

        pygame.display.update(affectedArea)
        clock.tick(FRAMERATE)
        t += 1

    return 0

if __name__ == "__main__":
    print('Starting platformerEngine version %s from directory: %s' %
          (VERSION, os.getcwd()))
    pygame.init()
    main()
    pygame.quit()
