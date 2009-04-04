import figleaf
figleaf.start()

def a():
    print 'this is a'

def b():
    print 'this is b'

def c():
    print 'this is c'

figleaf.start_section('foo')
a()
figleaf.start_section('bar')
b()
figleaf.stop_section()
c()

figleaf.stop()
figleaf.dump_pickled_coverage(open('.figleaf_sections', 'wb'))
