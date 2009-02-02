import sys, os, figleaf

sysdir = os.path.dirname(os.__file__)
print 'sysdir is', sysdir

version_string = ".".join([ str(x) for x in sys.version_info[:2] ])

class TestExclude:
    def setUp(self):
        assert not figleaf._t           # something leaked, if this fails!

    def tearDown(self):
        figleaf.stop()
        figleaf._t = None
    
    def test_exclude_stdlib(self):
        "Check that stdlib files are not covered if excluded."
        if version_string in ('2.3', '2.4'): # CTB
            return

        ### first check that they would be covered ordinarily!
        
        figleaf.start(ignore_python_lib=False)
        
        os.path.dirname('/some/weird/path') # use some stdlib code
        
        figleaf.stop()

        coverage = figleaf.get_data().gather_files()
        
        found = False
        for k in coverage:
            print k
            if k.startswith(sysdir):
                found = True
                break

        assert found                    # this will fail in 2.3, 2.4

        ### ok, now check that they're ignored properly.
        
        figleaf._t = None               # RESET
        
        figleaf.start(ignore_python_lib=True)
        
        os.path.dirname('/some/weird/path') # use some stdlib code
        
        figleaf.stop()

        coverage = figleaf.get_data().gather_files()
        for k in coverage:
            assert not k.startswith(sysdir)

    def test_noexclude_stdlib(self):
        """Check that stdlib files are covered if not excluded.

        Only works for python >= 2.5, because of some changes in the way
        frame objs f_code.co_filename is reported.
        """
        if version_string in ('2.3', '2.4'): # CTB
            return
        
        figleaf.start(ignore_python_lib=False)
        
        os.path.dirname('/some/weird/path') # use some stdlib code
        
        figleaf.stop()

        coverage = figleaf.get_data().gather_files()

        found = False
        for k in coverage:
            print k
            if k.startswith(sysdir):
                found = True
                break

        assert found

    ###

    def test_exclude_misc_path(self):
        "Check that tests/tst_exclude1.py is not covered, if excl specified"


        testspath = os.path.abspath('tests/')
        print 'IGNORING', testspath
        
        figleaf.init(testspath, None)
        figleaf.start()

        execfile('tests/tst_exclude1.py')

        figleaf.stop()

        coverage = figleaf.get_data().gather_files()

        print coverage.keys()
        assert not 'tests/tst_exclude1.py' in coverage.keys()

    def test_noexclude_misc_path(self):
        "Check that tests/tst_exclude1.py is covered, if no excl specified"
        figleaf.init(None, None)
        figleaf.start()

        execfile('tests/tst_exclude1.py')

        figleaf.stop()

        coverage = figleaf.get_data().gather_files()

        assert 'tests/tst_exclude1.py' in coverage.keys()
