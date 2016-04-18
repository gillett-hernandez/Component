import logging


def loggable_class(cls):
    cls.logger = logging.getLogger(__name__ + "." + cls.__name__)
    return cls


@loggable_class
class Event:
    def __init__(self, keyword, data):
        self.keyword = keyword
        self.data = data
        self.logger.debug("created {0!r}".format(self))

    def __repr__(self):
        return ("<Event instance with keyword:"
                " {keyword} and data: {data}>".format(keyword=str(self.keyword),
                                                      data=str(self.data)))

e = Event("update", {"dt": 16})
