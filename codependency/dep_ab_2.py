#!/usr/bin/env python

import logging
import config

logger = logging.getLogger(__name__)
conf = config.get()

# this needs to have access to either config1 or config2 depending on who imports it.
print(conf.friction)
