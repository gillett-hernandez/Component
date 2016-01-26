import logging
import math

from miscfunc import lengthdir_x, lengthdir_y, point_distance, to_mag_dir, vector_transform, normalize
import luftrausers_constants as constants
import luftrausers_keyconfig as keyconfig

logging.basicConfig(**constants.logging_setup)


def loggable(f):
    def func(*args, **kwargs):
        logging.debug(f.__name__+", args="+str(args)+", kwargs="+str(kwargs))
        result = f(*args, **kwargs)
        logging.debug("result is "+str(result))
        return result
    func.__name__ = f.__name__
    return func


