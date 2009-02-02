class Fooey:
    def __init__(self):
        self.a = 1
        
    def foo(self):     #pragma: NO COVER
        return self.a
        
x = Fooey()
assert x.a == 1
