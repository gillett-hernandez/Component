#!/usr/bin/env python

import os

import pygame
from pygame.locals import *


def make_spritesheet(root, folder, name):
    fns = []
    for droot, dirnames, filenames in os.walk(os.path.join(root, folder)):
        fns = filenames
    fns.sort()
    fns = [os.path.join(root, folder, fn) for fn in fns]
    with open(fns[0]) as fd:
        first = pygame.image.load(fd)
        width, height = first.get_size()
    whole = pygame.Surface((width*len(fns), height))
    for i, fn in enumerate(fns):
        image = pygame.image.load(fn)
        whole.blit(image, (i*width, 0))
    pygame.image.save(whole, os.path.join(root, name))

if __name__ == '__main__':
    root = "/home/gillett/Documents/Code/Python/Platformer/resources/images"
    make_spritesheet(root, "plane", "plane.png")

    planepath = os.path.join(root, "plane.png")

    plane = pygame.image.load(planepath)

    width, height = plane.get_size()

    planem = pygame.transform.flip(plane, True, False)

    uwidth = 64
    uheight = 64

    nplanem = pygame.Surface((60*uwidth, uheight))
    nplanem.blit(plane, (0, 0), pygame.Rect((0, 0), (uwidth*31, uheight)))
    nplanem.blit(planem, (uwidth*30, 0), pygame.Rect((0, 0), (uwidth*30, uheight)))

    pygame.image.save(nplanem, os.path.join(root, "spritesheet.png"))
