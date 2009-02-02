import sys, os, figleaf

class TestInclude:
    def setUp(self):
        assert not figleaf._t

    def tearDown(self):
        figleaf.stop()
        figleaf._t = None
    
    def test_include_misc_path(self):
        "Check that tests/tst_include1.py is the only thing covered, if set"
        figleaf.init(None, 'tests')
        figleaf.start()

        execfile('tests/tst_include1.py')

        figleaf.stop()

        coverage = figleaf.get_data().gather_files()

        assert 'tests/tst_include1.py' in coverage.keys()
        assert len(coverage) == 1

    def test_noinclude_misc_path(self):
        "Check that tests/tst_include1.py is not the only thing covered by def"
        figleaf.init(None, None)
        figleaf.start()

        execfile('tests/tst_include1.py')

        figleaf.stop()

        coverage = figleaf.get_data().gather_files()

        assert 'tests/tst_include1.py' in coverage.keys()
        assert len(coverage) > 1
