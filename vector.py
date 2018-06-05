#!/usr/bin/env python

import math


class Vector(object):
    """class representing a vector"""
    def __init__(self, xcomponent=None, ycomponent=None, l=None):
        if xcomponent is None and ycomponent is None:
            if l is not None:
                assert all(isinstance(e, (int, float)) for e in l)
                self.components = list(l)
            else:
                self.components = [0, 0]
        else:
            if xcomponent is None:
                xcomponent = 0
            if ycomponent is None:
                ycomponent = 0
            self.components = [xcomponent, ycomponent]

    def is_zero_vector(self):
        return all(c == 0 for c in self.components)

    @property
    def x(self):
        return self.components[0]

    @x.setter
    def x(self, value):
        assert isinstance(value, (int, float)), value
        self[0] = value

    @property
    def y(self):
        return self.components[1]

    @y.setter
    def y(self, value):
        assert isinstance(value, (int, float)), value
        self[1] = value

    @property
    def magnitude(self):
        return math.hypot(*self.components)

    def __add__(self, other):
        assert isinstance(other, Vector)
        return Vector(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        assert isinstance(other, Vector)
        return Vector(self.x-other.x, self.y-other.y)

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.dot(other)
        else:
            assert isinstance(other, (int, float))
            return Vector(self.x*other, self.y*other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        assert not isinstance(other, Vector)
        return self*(1./other)

    def __floordiv__(self, other):
        assert not isinstance(other, Vector)
        return Vector(self.x // other, self.y // other)

    def __iadd__(self, other):
        try:
            assert isinstance(other, Vector)
            self.x += other.x
            self.y += other.y
            # ????
            return self
        except TypeError:
            print(self.x, self.y, other.x, other.y)
            raise

    def __isub__(self, other):
        assert isinstance(other, Vector)
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, m):
        self.x *= m
        self.y *= m
        return self

    def __idiv__(self, other):
        return self.__itruediv__(other)

    def __itruediv__(self, other):
        assert not isinstance(other, Vector)
        self.x /= other
        self.y /= other
        return self

    def __ifloordiv__(self, other):
        assert not isinstance(other, Vector)
        self.x //= other
        self.y //= other

    def dot(self, other):
        assert isinstance(other, Vector)
        return self.x*other.x + self.y*other.y

    def normalize(self):
        assert hasattr(self, "__div__")
        m = self.magnitude
        return self / m

    def normalize_ip(self):
        assert hasattr(self, "__idiv__")
        m = self.magnitude
        self /= m

    def copy(self):
        return Vector(*self.components)

    def __getitem__(self, key):
        return self.components[key]

    def __setitem__(self, key, value):
        try:
            self.components[key] = value
        except TypeError:
            print(self, key, value)
            raise

    @classmethod
    def from_euclidean(cls, magnitude, direction):
        return Vector(math.cos(direction), math.sin(direction))*magnitude

    @classmethod
    def from_vector(cls, vector):
        return cls.from_euclidean(vector.magnitude, vector.components[1])

    def __repr__(self):
        return "vector with components {}".format(self.components)


class EuclideanVector2D(Vector):
    """class representing a 2 dimensional euclidean vector"""
    def __init__(self, magnitude=0, direction=0):
        self.components = [magnitude, math.radians(direction)]

    def is_zero_vector(self):
        return self.components[0] == 0

    @property
    def x(self):
        return self.components[0] * math.cos(self.components[1])

    @property
    def y(self):
        return self.components[0] * math.sin(self.components[1])

    @property
    def magnitude(self):
        return self.components[0]

    @magnitude.setter
    def magnitude(self, value):
        self.components[0] = value

    @property
    def direction(self):
        return math.degrees(self.components[1])

    @direction.setter
    def direction(self, value):
        self.components[1] = math.radians(value)

    @classmethod
    def from_cartesian(cls, x, y):
        magnitude = math.sqrt(math.hypot(x, y))
        direction = math.arctan2(y, x)
        return cls(magnitude, direction)

    @classmethod
    def from_vector(cls, vector):
        return cls.from_cartesian(vector.x, vector.y)


def test():
    v1 = Vector()
    v2 = Vector(2, 3)
    v3 = Vector(5, 10)
    ev1 = EuclideanVector2D()
    ev2 = EuclideanVector2D(10, 45)
    ev3 = EuclideanVector2D(15, -10)

    assert v1.is_zero_vector()
    assert not v2.is_zero_vector()
    assert not v3.is_zero_vector()

    assert all(a == 0 for a in [v1.x, v1.y]), v1

    assert not all(a == 0 for a in [v2.x, v2.y]), v1

    assert ev1.is_zero_vector(), ev1
    assert not ev2.is_zero_vector(), ev2
    assert not ev3.is_zero_vector(), ev3

    assert all(a == 0 for a in [ev1.x, ev1.y, ev1.magnitude]), ev1.components
    assert not all(a == 0 for a in [ev2.x, ev2.y, ev2.magnitude]), ev2.magnitude
    assert not all(a == 0 for a in [ev3.x, ev3.y, ev3.magnitude]), ev3

    assert v2.x == 2
    v2.x = 10
    assert v2.x == 10

    assert v2.y == 3
    v2.y = 0.5
    assert v2.y == 0.5

    v3 * 20
    v3 *= 10

    v3 / 10
    v3 /= 20

    assert ev2.magnitude == 10
    ev2.magnitude = 100
    assert ev2.magnitude == 100

    print(ev2, ev2.x, ev2.y, ev2.magnitude, ev2.direction)

    assert abs(ev2.x - 100*math.sqrt(2)/2) < 0.00005, ev2.x
    ev2.magnitude = 10
    assert abs(ev2.x - 10*math.sqrt(2)/2) < 0.00005, ev2.x

if __name__ == '__main__':
    test()
