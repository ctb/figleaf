vars = {'a': 1, 'b': 1, 'c': 1}
exec "a = 2" in vars
exec ("b = " +
    "c = " +
    "2") in vars
assert vars['a'] == 2 and vars['b'] == 2 and vars['c'] == 2
