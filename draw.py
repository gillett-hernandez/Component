from pyprocessing import *


class Namespace(object):
    def __init__(self):
        self.__dict__ = {}

ns = Namespace()
ns.i=0

def draw(ns=ns):
    ns.m = 500
    background(255, 255, 255)
    ns.i += 0.005
    for theta in range(0, 360):
        ns.r = theta
        point(ns.m+ns.r*ns.i*math.cos(math.radians(theta*137.5077)), ns.m+ns.r*ns.i*math.sin(math.radians(theta*137.5077)))


if __name__ == '__main__':
    size(1000, 1000)
    i = 0
    run()
