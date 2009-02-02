import os, sys

thisdir = os.path.dirname(__file__)
bindir = thisdir + '../../../bin/'
bindir = os.path.abspath(bindir)

def run(program, *plus_args):
    """
    Execute a program in the figleaf bin/ directory; return exit code,
    output, and stderr.
    """
    program = bindir + '/' + program
    args = [sys.executable, program]
    args.extend(plus_args)

    print 'running', args

    try:
        import subprocess
    
        p = subprocess.Popen(args, shell=False, stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
        (out, errout) = p.communicate()

        return (p.returncode, out, errout)
    except ImportError:
        from popen2 import Popen3

        p = Popen3(args, True)
        status = p.wait()
        
        (outfp, errfp) = p.fromchild, p.childerr
        out = outfp.read()
        errout = errfp.read()

        print 'STATUS:', status
        print 'OUT:', out
        print 'ERROUT:', errout

        return (status, out, errout)
        

def run_check(*args, **kw):
    x = run(*args, **kw)
    assert x[0] == 0, 'NOT A SUCCESS'
    return x

def does_dir_contain(dirname, *query_files, **kw):
    # should we assert that the directory contains *only* those files?
    only_contains = kw.get('only_contains', False)

    # get list of files; kludgy!
    actual_files = [ c for (a, b, c,) in os.walk(dirname) if a == dirname ][0]

    print ' --- does dir contain', dirname
    print 'QUERY FILES:', query_files
    print 'ACTUAL FILES:', actual_files
    print ' --- '
    
    for testfile in query_files:
        if testfile not in actual_files:
            return False
        actual_files.remove(testfile)

    if only_contains:
        if len(actual_files):
            assert False, 'several additional files in %s: %s' % (dirname,
                                                                  actual_files)
    
    return True

def does_dir_NOT_contain(dirname, *query_files):
    # get list of files; kludgy!
    actual_files = [ c for (a, b, c,) in os.walk(dirname) if a == dirname ][0]

    print ' --- does dir NOT contain', dirname
    print 'QUERY FILES:', query_files
    print 'ACTUAL FILES:', actual_files
    print ' --- '
    
    for testfile in query_files:
        if testfile in actual_files:
            return False
    
    return True
