#!/usr/bin/env python3

class Component(object):
    def __init__(self, *args, **kw):
        pass

    def component_function(self):
        pass


class ConcreteComponent(Component):
    def __init__(self, *args, **kw):
        Component.__init__(self, *args, **kw)

    def component_function(self):
        print("some function")


class Composite(Component):
    def __init__(self, *args, **kw):
        Component.__init__(self, *args, **kw)
        self.children = []

    def append_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def component_function(self):
        map(lambda x: x.component_function(), self.children)

    def print_structure(self, n=0):
        print(n*"|->"+"Composite")
        for i, child in enumerate(self.children):
            if isinstance(child, Composite):
                child.print_structure(n+1)
            else:
                if not i == len(self.children)-1:
                    print(n*"|  "+"|->"+child.__class__.__name__)
                else:
                    print(n*"|  "+"+->"+child.__class__.__name__)
        if n != 0:
            print(n*"|  ")

c = Composite()
child_leaf = Composite()
child_leaf.append_child(ConcreteComponent())
child_leaf.append_child(ConcreteComponent())
c.append_child(ConcreteComponent())
c.append_child(ConcreteComponent())
c.append_child(child_leaf)
c.append_child(child_leaf)
c.component_function()

c.print_structure()


# Composite
# |->Composite
# |  |->ConcreteComponent
# |  -->ConcreteComponent
# |->ConcreteComponent
# -->ConcreteComponent
