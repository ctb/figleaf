a = 0
try:
    a = 1
except:       #pragma: NO COVER
    a = 99
else:
    a = 123
assert a == 123
