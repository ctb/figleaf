def foo(
    a = (lambda x: x*2)(10),
    b = (
        lambda x:
            x+1
        )(1)
    ):
    ''' docstring
    '''
    return a+b
    
x = foo()
assert x == 22
