import sys, os
import tempfile, glob

thisdir = os.path.dirname(__file__)

def test_dos_eol():
    """
    Make sure that we can annotate files with DOS EOL characters in them.
    """
    import figleaf, figleaf.annotate_html
    
    figleaf.start()
    execfile(os.path.join(thisdir, 'tst_dos_eol.py'))
    figleaf.stop()

    coverage = figleaf.get_data().gather_files()

    tmpdir = tempfile.mkdtemp('.figleaf')

    try:
        figleaf.annotate_html.report_as_html(coverage, tmpdir, [], {})
    finally:
        files = glob.glob('%s/*' % (tmpdir,))
        for f in files:
            os.unlink(f)
        os.rmdir(tmpdir)

def test_end_comment():
    """
    Make sure that we can parse files with '#' at the very end.
    """
    import figleaf
    
    filename = os.path.join(thisdir, 'tst_end_comment.py')
    figleaf.get_lines(open(filename))
