#!/usr/bin/env python3

import math


class Vector:
    """class representing a vector"""
    def __init__(self, xcomponent=None, ycomponent=None, l=None):
        if xcomponent is None and ycomponent is None:
            assert all(isinstance(e, (int, float)) for e in l)
            self.components = l
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

    def __mul__(self, m):
        return Vector(self.x*m, self.y*m)

    def dot(self, other):
        assert isinstance(other, Vector)
        return self.x*other.x + self.y*other.y

    def normalize(self):
        return Vector(self.x/self.magnitude, self.y/self.magnitude)

    def __iadd__(self, other):
        assert isinstance(other, Vector)
        self.x += other.x
        self.y += other.y

    def __isub__(self, other):
        assert isinstance(other, Vector)
        self.x -= other.x
        self.y -= other.y

    def __imul__(self, m):
        self.x *= m
        self.y *= m

    def normalize_ip(self):
        m = self.magnitude
        self.mul_ip(1/m)

    def __getitem__(self, key):
        return self.components[key]

    def __setitem__(self, key, value):
        self.components[key] = value


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
    def from_vector(cls, vector):
        assert hasattr(vector, "x")
        assert hasattr(vector, "y")
        assert hasattr(vector, "components")
        magnitude = math.sqrt(math.hypot(vector.x, vector.y))
        direction = math.arctan2(vector.y, vector.x)
        return cls(magnitude, direction)


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

    assert ev2.magnitude == 10
    ev2.magnitude = 100
    assert ev2.magnitude == 100

    assert abs(ev2.x - 100*math.sqrt(2)/2) < 0.00005
    ev2.magnitude = 10
    assert abs(ev2.x - 10*math.sqrt(2)/2) < 0.00005

if __name__ == '__main__':
    test()
