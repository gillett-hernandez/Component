#!/usr/bin/python

import pygame
import os

SOUNDS_PATH = "./resources/sounds"


class SoundLibrary:
    def __init__(self):
        self.sounds = {}

    def add_sound(self, name, path):
        self.sounds[name] = pygame.mixer.Sound(path)

    def __getitem__(self, key):
        return self.sounds[key]


def init():
    sound_library = SoundLibrary()
    dirpath, dirnames, filenames = os.walk(SOUNDS_PATH)
    for dirname, filename in zip(dirnames, filenames):
        sound_library.add_sound(os.get_name(filename),
                                os.join(dirpath, dirname, filename))
