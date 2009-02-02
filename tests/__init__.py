"""
Basic test fixtures for figleaf.
"""
import sys, os

thisdir = os.path.dirname(__file__)
libdir = os.path.abspath(thisdir + '/..')

def setup():
    sys.path.insert(0, libdir)

    # this makes sure that the figleaf module is loaded from the
    # correct directory, and not from some other figleaf installation.
    # (seems to be a pkg_resources issue where setuptools is loading
    # figleaf egg in by default.)
    import figleaf

    reload(sys.modules['figleaf'])
    reload(sys.modules['figleaf.internals'])

    assert libdir in figleaf.__file__

def teardown():
    sys.path.remove(libdir)
