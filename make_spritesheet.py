#!/usr/bin/env python

import os

import pygame
from pygame.locals import *


def create_rotations(sprite, subdivisions):
    pass



def make_spritesheet(folder, name):
    """takes a folder of images and makes a spritesheet out of them
assumes that they are uniformly sized and lexicographically ordered.
puts the spritesheet in folder/..
returns the path of the saved spritesheet"""
    root = os.path.realpath(os.path.join(folder, ".."))
    filenames = []
    for _, _, _filenames in os.walk(os.path.join(folder)):
        filenames = _filenames
    filenames.sort()
    filenames = [os.path.join(folder, filename) for filename in filenames]
    with open(filenames[0], 'rb') as fd:
        first = pygame.image.load(fd)
        width, height = first.get_size()
    whole = pygame.Surface((width*len(filenames), height))
    for i, filename in enumerate(filenames):
        image = pygame.image.load(filename)
        whole.blit(image, (i*width, 0))
    spritesheet_path = os.path.join(root, name)
    pygame.image.save(whole, spritesheet_path)
    return spritesheet_path

if __name__ == '__main__':
    path = "~/Platformer/resources/images/plane/"
    path = os.path.realpath(os.path.expanduser(path))
    plane_sheet_path = make_spritesheet(path, "plane.png")

    plane_sheet = pygame.image.load(plane_sheet_path)

    width, height = plane_sheet.get_size()

    plane_sheet_mirrored = pygame.transform.flip(plane_sheet, True, False)

    uwidth = 64
    uheight = 64

    new_sheet = pygame.Surface((60*uwidth, uheight))
    new_sheet.blit(plane_sheet, (0, 0), pygame.Rect((0, 0), (uwidth*31, uheight)))
    new_sheet.blit(plane_sheet_mirrored, (uwidth*30, 0), pygame.Rect((0, 0), (uwidth*30, uheight)))

    pygame.image.save(nplanem, os.path.join(root, "spritesheet.png"))
