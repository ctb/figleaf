a = 0
for i in range(5):
    a += i+1
    break
    a = 99
else:               #pragma: NO COVER
    a = 123
assert a == 1
