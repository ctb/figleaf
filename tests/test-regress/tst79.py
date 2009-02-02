a = 3; b = 0
while a*b:           #pragma: NO COVER
    b += 1
    break
    b = 99
assert a == 3 and b == 0
