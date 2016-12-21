
import pygame
import json
import os
import sound
from component import DotDict, constants
global resources
resources = {}


def load_basic_resources(resources):
    """loads basic resources into ram"""
    # print(dir(DotDict))
    with open(os.path.join("json", "resources.json"), 'r') as fd:
        _resources = DotDict(json.load(fd))
    # print(dir(_resources.playerimage))
    for name, data in _resources.items():
        if data["type"] == constants.IMAGE:
            with open(data["path"], 'rb') as fd:
                resources[name] = pygame.image.load(fd)
        elif data["type"] in [constants.SFX, constants.MUSIC]:
            with open(data["path"], 'rb') as fd:
                resources[name] = sound.load(fd)


def get_resource(name):
    global resources
    return resources[name]
