import logging

logging.basicConfig(filename="hello.log", filemode="w", level=logging.DEBUG)


def loggable(f):
    def func(*args, **kwargs):
        logging.debug(f.__name__+", args="+str(args)+", kwargs="+str(kwargs))
        result = f(*args, **kwargs)
        logging.debug("result is "+str(result))
        return result
    func.__name__ = f.__name__
    return func


@loggable
def butts(x, y):
    return x + y


def buggs(x, y):
    return x + y

buggs = loggable(buggs)

print(butts(4, 5))
print(buggs(4, 5))
