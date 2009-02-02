"""
Run some tests of the various command line programs.
"""

import os, sys, shutil, tempfile
import utils

testdir = os.path.dirname(__file__)

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
        
    def test_annotate_no_args(self):
        status, out, errout = utils.run('figleaf-annotate')
        assert out.startswith('ERROR')

    def test_basic_record(self):
        "Does figleaf record the proper thing?"
        # fail to list anything (no .figleaf file)
        status, out, errout = utils.run('figleaf-annotate', 'list', "tst-")
        assert status != 0

        # now run coverage...
        status, out, errout = utils.run('figleaf', 'tst-cover.py')
        print out, errout
        assert status == 0

        # list *all* files
        status, out, errout = utils.run('figleaf-annotate', 'list')
        assert status == 0
        assert out.find("\ntst-cover.py\n")

        # list only the one file (matching 'tst-')
        status, out, errout = utils.run('figleaf-annotate', 'list', "tst-")
        assert status == 0
        assert out == "tst-cover.py\n", out

    def test_annotate_coverage_filename(self):
        "Does the '-c' flag work for figleaf-annotate?"

        TEST_FILENAME = '.figleaf_blah'
        
        # fail to list anything (no .figleaf_blah file)
        status, out, errout = utils.run('figleaf-annotate', 'list',
                                        '-c', TEST_FILENAME)
        assert status != 0

        # now run coverage...
        status, out, errout = utils.run('figleaf', 'tst-cover.py')
        print out, errout
        assert status == 0

        # rename coverage output file
        os.rename('.figleaf', TEST_FILENAME)

        # now list files that are covered in that recording...
        status, out, errout = utils.run('figleaf-annotate', 'list',
                                        '-c', TEST_FILENAME)
        assert status == 0
        assert out.find("\ntst-cover.py\n")

        # be sure to remove the file.
        os.unlink(TEST_FILENAME)

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

class Test_Figleaf2HTML:
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
