GRAVITY = 4
# GRAVITY = 0

WATER_GRAVITY = -4*GRAVITY

ROUND_DEPTH = 6

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
HALF_WIDTH = SCREEN_WIDTH//2
HALF_HEIGHT = SCREEN_HEIGHT//2
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

LEVEL_WIDTH, LEVEL_HEIGHT = 1000, 1000-(1000/8)


FRAMERATE = 60

# strength_or_speed = 'strength'

turnspeed = 4

accelturnspeed = 3

always_restrict_velocity = True
maxspeed = 240
accel = 15
friction = 0

bulletspeed = 10

PHYS = 'PHYSICS'

import logging
# logging_setup = {
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "brief",
#             "level": "INFO",
#             "filters": ["allow_foo"],
#             "stream": "ext://sys.stdout"
#         },
#         "file": {
#             "class": "logging.handlers.RotatingFileHandler",
#             "formatter": "precise",
#             "filename": "LuftrausersClone.log",
#             "maxBytes": 1024,
#             "backupCount": 3
#         }
#     }
# }

logging_setup = {"filename": './LuftrausersClone.log',
                 "filemode": 'w',
                 "level": logging.DEBUG}
