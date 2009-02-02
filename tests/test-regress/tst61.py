a = 3; b = 0
while a:
    b += 1
    a -= 1
    break
    b = 123
else:
    b = 99
assert a == 2 and b == 1
