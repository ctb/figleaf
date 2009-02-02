import urllib

x = 5

def foo(
    a = (
    lambda x: x*2)(10),
    b = (
        lambda x:
            x+1
        )(1)
    ):
    5
    ''' docstring
    '''
    x = (
        5,
        10,
        15,
        (lambda x: x+1)(1)
        )

    "test"
    6
    
    return a+b

x = foo()
assert x == 22
