
class Config(object):
    @classmethod
    def _supply(cls, string, module):
        setattr(cls, string, module)


def supply(string, module):
    Config._supply(string, module)


def get(name):
    return getattr(Config, name, None)
