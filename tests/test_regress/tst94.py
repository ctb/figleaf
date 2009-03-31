d = { 'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1 }
del d['a']
del d[
    'b'
    ]
del d['c'], \
    d['d'], \
    d['e']
assert(len(d.keys()) == 0)
