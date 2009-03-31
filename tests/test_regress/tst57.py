a = 0; b = 0
try:
    a = 1
    try:
        raise Exception("foo")
    finally:
        b = 123
except:
    a = 99
assert a == 99 and b == 123
