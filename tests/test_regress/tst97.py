globs = {}
locs = {'a': 1, 'b': 1, 'c': 1}
exec "a = 2" in globs, locs
exec ("b = " +
    "c = " +
    "2") in globs, locs
assert locs['a'] == 2 and locs['b'] == 2 and locs['c'] == 2
