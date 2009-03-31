from __future__ import generators
def gen():
    yield 1
    yield (2+
        3+
        4)
    yield 1, \
        2
a,b,c = gen()
assert a == 1 and b == 9 and c == (1,2)
