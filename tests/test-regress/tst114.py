def fn():
    a = 1
    return (a,
        a + 1,
        a + 2)
        
x,y,z = fn()
assert x == 1 and y == 2 and z == 3
