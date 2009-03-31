def f():
    for i in range(0, 5):
        yield i

for x in f():
    print 'hello', x
