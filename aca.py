import logging

def loggable(f):
    def func(*args, **kwargs):
        logging.debug(f.__name__+", args="+str(args)+", kwargs="+str(kwargs))
        result = f(*args, **kwargs)
        logging.debug("result is "+str(result))
        return result
    func.__name__ = f.__name__
    return func
