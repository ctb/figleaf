g = h = i = 1
def fn():
    global g
    global h, \
        i
    g = h = i = 2
fn()
assert g == 2 and h == 2 and i == 2
