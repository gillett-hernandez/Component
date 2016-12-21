

class DotDict:
    def __init__(self, d={}):
        self.__dict__.update(d)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def items(self):
        return self.__dict__.items()
