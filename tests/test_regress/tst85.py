def require_int(func):
    def wrapper(arg):
        assert isinstance(arg, int)
        return func(arg)

    return wrapper

@require_int
def p1(arg):
    return arg*2

assert p1(10) == 20
