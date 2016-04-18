#!/usr/bin/env python

import json
import logging

import config

from DotDict import DotDict

with open("config2.json", 'r') as fd:
    conf = DotDict(json.load(fd))

config.supply(conf)
logging.basicConfig(**conf.logging_setup)

import dep_ab_1 as da1
import dep_ab_2 as da2
