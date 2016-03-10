GRAVITY = 200
# GRAVITY = 0

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


FRAMERATE = 60

# strength_or_speed = 'strength'

turnspeed = 2

maxspeed = 200  # run max 200px/s
accel = 12
friction = .99

import logging
logging_setup = {"filename": './lfclone.log',
                 "filemode": 'w',
                 "level": logging.DEBUG}
