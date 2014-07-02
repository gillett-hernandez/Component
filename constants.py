
# class Error(Exception):
#     """Base class for exceptions in this module."""
#     pass

# class Stop(Error):
#     def __init__(self, message="in the name of love."):
#         super(Stop, self).__init__()
#         self.message = message

#     def __str__(self):
#         return repr(self.message)

GRAVITY = 300

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT


FRAMERATE = 60

friction = .9

strength_or_speed = 'strength'

runspeed = 200  # run max 200px/s
runaccel = 10  # take 10 frames to accelerate to top speed

jumpstrength = 5*16  # jump ten blocks high, assuming 16px block height

from miscfunc import vel_to_go_height


if strength_or_speed == 'strength':
    jumpspeed = round(vel_to_go_height(90, jumpstrength, GRAVITY), 5)
else:
    jumpspeed = 700  # jump with a speed of jumpspeed px/s upward


import logging
logging_setup = {"filename": './PlatformerEngine.log',
                 "filemode": 'w',
                 "level": logging.DEBUG}
