# A comment.
class theClass:
    ''' the docstring.
        Don't be fooled.
    '''
    def __init__(self):
        ''' Another docstring. '''
        self.a = 1
    
    def foo(self):
        return self.a

x = theClass().foo()
assert x == 1
