g = h = i = 1
def fn():
    global g; g = 2
fn()
assert g == 2 and h == 1 and i == 1
