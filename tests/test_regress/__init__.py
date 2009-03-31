"""
A test generator for all of the files in tests/test-regress.
"""

import sys
import os
import imp
import __main__
import figleaf, figleaf.annotate_cover

version_string = ".".join([ str(x) for x in sys.version_info[:2] ])

#

testdir = os.path.dirname(__file__)
libdir = os.path.abspath(testdir + '../../..')

cwd = None
def setup():
    global cwd
    cwd = os.getcwd()
    os.chdir(testdir)

    sys.path.insert(0, testdir)

def teardown():
    os.chdir(cwd)
    sys.path.remove(testdir)

    figleaf.stop()
    figleaf._t = None

def test_source_generator():
    """
    A test generator function for many independent test cases.

    This function yields tests that run coverage analysis on a bunch
    of little test files & reports mismatches against presumed "good" results.

    Note that we have to keep track of the version # here because Python
    can change what lines are traced between versions, so we have to have
    a set of good results for each Python version supported.
    """
    for filename in os.listdir(testdir):
        if filename.startswith('tst') and filename.endswith('.py'):
            yield compare_coverage, filename

def compare_coverage(filename):
    print(filename)
    
    fullpath = os.path.abspath(os.path.join(testdir, filename))

    ### run file & record coverage
    
    maindict = dict(__main__.__dict__)

    figleaf.start()
    
    try:
        figleaf.execfile(fullpath, maindict)
    except:
        pass
    
    figleaf.stop()

    d = figleaf.get_data().gather_files()
    coverage_info = d.get(fullpath, None)

    ### ok, now get the interesting lines from our just-executed python script

    f1 = open(fullpath)

    SYNTAX_ERROR = False
    try:
        line_info = figleaf.get_lines(f1)
    except SyntaxError:
        SYNTAX_ERROR = True             # not supported in this ver?

    ### load in the previously annotated lines

    coverage_file = filename + '.cover.' + version_string

    try:
        f2 = open(os.path.join(testdir, coverage_file))
        assert not SYNTAX_ERROR
    except IOError:
#@CTB        assert SYNTAX_ERROR
        
        # it's ok, skip this test
        return
    
    ########## No syntax error, check aginst previously annotated stuff.
    
    actual_lines = f2.readlines()
    f2.close()
    
    ### annotate lines with coverage style 'cover'
    
    f1.seek(0)
    (_, _, output) = figleaf.annotate_cover.make_cover_lines(line_info,
                                                             coverage_info, f1)

    ### compare!
    
    f1.close()

    for (i, (check_line, recorded_line)) in enumerate(zip(output, actual_lines)):
        check_line = check_line.strip()
        recorded_line = recorded_line.strip()
        
        assert check_line == recorded_line, "regression mismatch, file %s:%d\ncurrent '%s'\nactual  '%s'\n" % (fullpath, i, check_line, recorded_line,)
