import figleaf

def thisfile():
    if __file__.endswith('.pyc'):
        return __file__.rstrip('c')
    return __file__

### functions to run for tests

def common():
    print 0

def common2():
    print 4

def a():
    common()
    print 1

def b():
    common()
    print 2

def c():
    common()
    print 3

###

# the actual test!

# use builtin sets if in >= 2.4, otherwise use 'sets' module.
try:
    set()
except NameError:
    from sets import Set as set

def test():
    figleaf.start()
    common()

    figleaf.start_section('a')
    a()
    figleaf.stop_section()
    common2()

    figleaf.start_section('b')
    b()
    figleaf.start_section('c')
    c()
    figleaf.stop()

    in_common = set()
    union = set()

    expected = dict(a = set([17, 18, 11, 14]),
                    b = set([22, 11, 21, 14]),
                    c = set([25, 26, 11, 14]))
    
    for i in ('a', 'b', 'c'):
        actual = figleaf.get_info(section_name=i).get(thisfile())
        print '******', thisfile()
        print 'section:', i, '; lines:', actual
        print expected[i]

        x = list(expected[i])
        x.sort()
        
        y = list(actual)
        y.sort()

        print x, y
        
        assert x == y                   # note: depends on absolute line no.
                                        # so don't shift lines in this file ;)
        if not in_common:
            in_common.update(actual)
        else:
            in_common.intersection_update(actual)
        union.update(actual)

    in_common = list(in_common)
    in_common.sort()
    print 'common:', in_common

    assert in_common == [11, 14]

    union = list(union)
    union.sort()
    print 'union:', union
    
    assert union == [11, 14, 17, 18, 21, 22, 25, 26]

def setup():
    pass

def teardown():
    figleaf.stop()
    figleaf._t = None
