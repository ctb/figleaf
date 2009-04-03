"""
Some simple compatibility functionality for different python versions (2.4-3.x)
"""

__all__ = ('set', 'do_execfile')

# use builtin sets if in >= 2.4, otherwise use 'sets' module.
try:
    set = set
except NameError:
    from sets import Set as set

# is execfile defined?  (it's not there in 3.x)
try:
    do_execfile = execfile
except NameError:
    def do_execfile(filename, maindict=None):
        """A replacement execfile for python 3.x"""
        
        if maindict is None:
            maindict = {}

        data = open(filename).read('rU')
        code = compile(data, filename, 'exec')
        exec(code, maindict)
