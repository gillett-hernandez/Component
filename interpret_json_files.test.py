#!/usr/bin/env python

import logging
import json


class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item


with open("./lf_constants.json", 'r') as fd:
    constants = DotDict(json.load(fd))

logging.basicConfig(**constants.logging_setup)

print(constants.GRAVITY)
print(constants.maxspeed)
print(constants.SCREEN_SIZE)
