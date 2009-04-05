"""
Run some tests of the various command line programs.
"""

import os, sys, shutil, tempfile
import utils

testdir = os.path.dirname(__file__)

import figleaf

cwd = None
def setup():
    global cwd
    cwd = os.getcwd()
    os.chdir(testdir)

    sys.path.insert(0, testdir)

def teardown():
    os.chdir(cwd)
    sys.path.remove(testdir)

class Test_SimpleCommandLine:
    """
    Do a simple test of some of the command line scripts.
    """
    def setUp(self):
        try:
            os.unlink('.figleaf')
        except OSError:
            pass
        
        try:
            os.unlink('.figleaf_sections')
        except OSError:
            pass

    tearDown = setUp

    def test_figleaf_main_args(self):
        # now run coverage...
        status, out, errout = utils.run('figleaf')
        print out, errout
        assert status != 0
        
        status, out, errout = utils.run('figleaf', 'tst-cover.py')
        print out, errout
        assert "ARGV: \n" in out
        assert status == 0
        
        status, out, errout = utils.run('figleaf', 'tst-cover.py', 'a1', 'b2')
        print out, errout
        assert "ARGV: a1::b2\n" in out
        assert status == 0

        status, out, errout = utils.run('figleaf', 'tst-cover.py', '-a', 'b2')
        print out, errout
        assert "ARGV: -a::b2\n" in out
        assert status == 0

class Test_FigleafMiscOutput:
    """
    Test output.
    """
    def setUp(self):
        try:
            os.unlink('.figleaf')
        except OSError:
            pass
        
        try:
            os.unlink('.figleaf_sections')
        except OSError:
            pass

        try:
            os.unlink('./tst-cover.py.cover')
        except OSError:
            pass

        # record coverage...
        status, out, errout = utils.run('figleaf', 'tst-cover.py')
        print out, errout
        assert status == 0

    tearDown = setUp

    def test_figleaf2cov(self):
        status, out, errout = utils.run('figleaf2cover')
        print out, errout
        assert status == 0

        results = open('./tst-cover.py.cover').read()
        
        # UPDATE "GOOD" output?
        # open('./tst-cover.py.cover.good', 'w').write(results)
        good = open('./tst-cover.py.cover.good').read()

        assert results == good
        
    def test_figleaf_report(self):
        status, out, errout = utils.run('figleaf-report')
        print out, errout
        assert status == 0

        # UPDATE "GOOD" output?
        # open('./tst-cover.py.report.good', 'w').write(out)
        good = open('./tst-cover.py.report.good').read()

        assert out == good

class Test_Figleaf2HTML:
    """
    Test output.
    """
    def setUp(self):
        try:
            os.unlink('.figleaf')
        except OSError:
            pass
        
        try:
            os.unlink('.figleaf_sections')
        except OSError:
            pass

        # remove any previous output, allowing for change of htmldir name
        # in teardown.  (this getattr should always fail in setup)
        
        if getattr(self, 'htmldir', None) is None:
            htmldir = os.path.join(testdir, 'html')
            htmldir = os.path.abspath(htmldir)
            self.htmldir = htmldir

        try:
            shutil.rmtree(self.htmldir)
        except OSError:                 # doesn't exist? that's ok
            pass
        
        # run coverage...
        status, out, errout = utils.run('figleaf', 'tst-cover.py')
        print out, errout
        assert status == 0

    tearDown = setUp
        
    def test_basic(self):
        # precondition assert
        assert not os.path.exists(self.htmldir)
        assert not os.path.isdir(self.htmldir)
        assert not os.path.exists(os.path.join(self.htmldir, 'index.html'))
        
        utils.run('figleaf2html')

        # should output to ./html/ by default
        assert os.path.exists(self.htmldir)
        assert os.path.isdir(self.htmldir)
        assert os.path.exists(os.path.join(self.htmldir, 'index.html'))

    def test_dirname(self):
        "Test use of explicit output directory"
        from figleaf.annotate_html import make_html_filename
        
        newhtmldir = os.path.join(testdir, 'foohtml')
        newhtmldir = os.path.abspath(newhtmldir)
        self.htmldir = newhtmldir       # RESET HTMLDIR
            
        # precondition assert in case of improper cleanup...
        assert not os.path.exists(self.htmldir)
        assert not os.path.isdir(self.htmldir)
        assert not os.path.exists(os.path.join(self.htmldir, 'index.html'))
        
        utils.run('figleaf2html', '-d', 'foohtml')

        # should output to ./foohtml/ now
        assert os.path.exists(self.htmldir)
        assert os.path.isdir(self.htmldir)
        assert os.path.exists(os.path.join(self.htmldir, 'index.html'))

        assert utils.does_dir_contain(self.htmldir,
                                      'index.html',
                                      make_html_filename('tst-cover.py'))

    def test_filelist(self):
        "Test use of explicit file list"
        from figleaf.annotate_html import make_html_filename
        
        x = utils.run_check('figleaf2html', '-f', 'tst-cover.file-list', '-D')
        (status, out, errout) = x
        print out, errout

        assert utils.does_dir_contain(self.htmldir,
                                      'index.html',
                                      make_html_filename('tst-cover.py'),
                                      only_contains = True)

    def test_filelist(self):
        "Test use of exclude file list"
        from figleaf.annotate_html import make_html_filename
        
        x = utils.run_check('figleaf2html', '-x', 'tst-cover.exclude', '-D')
        (status, out, errout) = x
        print out, errout

        assert utils.does_dir_NOT_contain(self.htmldir,
                                          make_html_filename('tst-cover.py'))

class Test_Sections:
    """
    Test the annotat-sections script.
    """
    def setUp(self):
        try:
            os.unlink('.figleaf_sections')
        except OSError:
            pass

    tearDown = setUp

    def test_figleaf_main_args(self):
        # run the sections-generating script
        figleaf.start()
        figleaf._t.clear()
        
        execfile('tst-sections.py')
        
        fp = open('.figleaf_sections', 'wb')
        figleaf.dump_pickled_coverage(fp)
        fp.close()
        
        # now run coverage...
        status, out, errout = utils.run('annotate-sections', 'tst-sections.py')
        print out, errout
        assert status == 0

        results = open('./tst-sections.py.sections').read()
        good = open('./tst-sections.py.sections.good').read()

        assert results == good
