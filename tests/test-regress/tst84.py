def require_int(func):
    def wrapper(arg):
        assert isinstance(arg, int)
        return func(arg)
    return wrapper
def boost_by(extra):
    def decorator(func):
        def wrapper(arg):
            return extra*func(arg)
        return wrapper
    return decorator

@require_int
@boost_by(10)
def boosted1(arg):
    return arg*2

assert boosted1(10) == 200
@boost_by(10)
@require_int
def boosted2(arg):
    return arg*2

assert boosted2(10) == 200
