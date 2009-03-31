def boost_by(extra):
    def decorator(func):
        def wrapper(arg):
            return extra*func(arg)
        return wrapper
    return decorator

@boost_by(10)
def boosted(arg):
    return arg*2

assert boosted(10) == 200
