"""
HTML annotation of figleaf results.

Functions:
 - annotate_file
 - write_html_summary
 - report_as_html
 - prepare_reportdir
 - make_html_filename
 - escape_html
"""
import os
import re

import figleaf
from figleaf import annotate
from figleaf.annotate import logger

from figleaf.compat import set

###

def annotate_file_html(fp, lines, covered):
    """Take file pointer & sets of covered/uncovered lines, turn into HTML."""
    
    # initialize stats
    n_covered = n_lines = 0

    output = []
    for i, line in enumerate(fp):
        is_covered = False
        is_line = False

        i += 1

        if i in covered:
            is_covered = True

            n_covered += 1
            n_lines += 1
        elif i in lines:
            is_line = True

            n_lines += 1

        color = 'black'
        if is_covered:
            color = 'green'
        elif is_line:
            color = 'red'

        line = escape_html(line.rstrip())
        output.append('<font color="%s">%4d. %s</font>' % (color, i, line))

    try:
        percent = n_covered * 100. / n_lines
    except ZeroDivisionError:
        percent = 100

    return output, n_covered, n_lines, percent

def write_html_summary(info_dict, directory):
    info_dict_items = info_dict.items()

    def sort_by_pcnt(a, b):
        return cmp(-a[1][2], -b[1][2])

    info_dict_items.sort(sort_by_pcnt)

    summary_lines = sum([ v[0] for (k, v) in info_dict_items])
    summary_cover = sum([ v[1] for (k, v) in info_dict_items])

    summary_percent = 100
    if summary_lines:
        summary_percent = float(summary_cover) * 100. / float(summary_lines)


    percents = [ float(v[1]) * 100. / float(v[0])
                 for (k, v) in info_dict_items if v[0] ]
    
    percent_90 = [ x for x in percents if x >= 90 ]
    percent_75 = [ x for x in percents if x >= 75 ]
    percent_50 = [ x for x in percents if x >= 50 ]

    ### write out summary.

    index_fp = open('%s/index.html' % (directory,), 'w')
    index_fp.write('''
<html>
<title>figleaf code coverage report</title>
<h2>Summary</h2>
%d files total: %d files &gt; 90%%, %d files &gt; 75%%, %d files &gt; 50%%
<p>
<table border=1>
<tr>
 <th>Filename</th><th># lines</th><th># covered</th><th>%% covered</th>
</tr>

<tr>
 <td><b>totals:</b></td>
 <td><b>%d</b></td>
 <td><b>%d</b></td>
 <td><b>%.1f%%</b></td>
</tr>

<tr></tr>

''' % (len(percents), len(percent_90), len(percent_75), len(percent_50),
       summary_lines, summary_cover, summary_percent,))

    for filename, (n_lines, n_covered, percent_covered,) in info_dict_items:
        html_outfile = make_html_filename(filename)

        index_fp.write('''
<tr>
 <td><a href="./%s">%s</a></td>
 <td>%d</td>
 <td>%d</td>
 <td>%.1f</td>
</tr>
''' % (html_outfile, filename, n_lines, n_covered, percent_covered,))

    index_fp.write('</table>\n')
    index_fp.close()

def report_as_html(coverage, directory, exclude_patterns, files_list,
                   extra_files=None, include_zero=True):
    """
    Write an HTML report on all of the files, plus a summary.
    """

    ### assemble information.
    
    line_info = annotate.build_python_coverage_info(coverage, exclude_patterns,
                                                    files_list)

    if extra_files:
        for (otherfile, lines, covered) in extra_files:
            line_info[otherfile] = (lines, covered)

    ### now, output.
    info_dict = {}

    for filename, (lines, covered) in line_info.items():
        fp = open(filename, 'rU')

        #
        # ok, we want to annotate this file.  now annotate file ==> html.
        #

        # annotate
        output, n_covered, n_lines, percent = annotate_file_html(fp,
                                                                 lines,
                                                                 covered)

        if not include_zero and n_covered == 0:
            continue

        # summarize
        info_dict[filename] = (n_lines, n_covered, percent)

        # write out the file
        html_outfile = make_html_filename(filename)
        html_outfile = os.path.join(directory, html_outfile)
        html_outfp = open(html_outfile, 'w')
        
        html_outfp.write('source file: <b>%s</b><br>\n' % (filename,))
        html_outfp.write('''

file stats: <b>%d lines, %d executed: %.1f%% covered</b>
<pre>
%s
</pre>

''' % (n_lines, n_covered, percent, "\n".join(output)))
            
        html_outfp.close()

        logger.info('reported on %s' % (filename,))

    ### print a summary, too.
    write_html_summary(info_dict, directory)

    logger.info('reported on %d file(s) total\n' % len(info_dict))

def prepare_reportdir(dirname):
    "Create output directory."
    try:
        os.mkdir(dirname)
    except OSError:                         # already exists
        pass

def make_html_filename(orig):
    "'escape' original paths into a single filename"

    orig = os.path.abspath(orig)
#    orig = os.path.basename(orig)
    orig = os.path.splitdrive(orig)[1]
    orig = orig.replace('_', '__')
    orig = orig.replace(os.path.sep, '_')
    orig += '.html'
    return orig

def escape_html(s):
    """
    @CTB rather inadequate, no? ;)
    """
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s

###

def main():
    """
    Command-line function to do HTML annotation (red/green).

    Setuptools entry-point for figleaf2cov; see setup.py.
    """
    import sys
    import logging
    from optparse import OptionParser

    ###

    usage = "usage: %prog [options] [coverage files ... ]"
    option_parser = OptionParser(usage=usage)

    option_parser.add_option('-x', '--exclude-patterns', action="store",
                             dest="exclude_patterns_file",
        help="file containing regexp patterns of files to exclude from report")

    option_parser.add_option('-f', '--files-list', action="store",
                             dest="files_list",
                             help="file containing filenames to report on")

    option_parser.add_option('-d', '--output-directory', action='store',
                             dest="output_dir",
                             default = "html",
                             help="directory for HTML output")

    option_parser.add_option('-q', '--quiet', action='store_true',
                             dest='quiet',
                             help='Suppress all but error messages')
    
    option_parser.add_option('-D', '--debug', action='store_true',
                             dest='debug',
                             help='Show all debugging messages')

    option_parser.add_option('-z', '--no-zero', action='store_true',
                             dest='no_zero',
                             help='Omit files with zero lines covered.')

    (options, args) = option_parser.parse_args()

    logger.setLevel(logging.INFO)

    if options.quiet:
        logging.disable(logging.WARNING)
        
    if options.debug:
        logger.setLevel(logging.DEBUG)

    ### load/combine

    if not args:
        args = ['.figleaf']

    coverage = {}
    for filename in args:
        logger.debug("loading coverage info from '%s'\n" % (filename,))
        d = figleaf.read_coverage(filename)
        coverage = figleaf.combine_coverage(coverage, d)

    if not coverage:
        logger.warning('EXITING -- no coverage info!\n')
        sys.exit(-1)

    exclude = []
    if options.exclude_patterns_file:
        exclude = annotate.read_exclude_patterns(options.exclude_patterns_file)

    files_list = {}
    if options.files_list:
        files_list = annotate.read_files_list(options.files_list)

    ### make directory
    prepare_reportdir(options.output_dir)
    report_as_html(coverage, options.output_dir, exclude, files_list,
                   include_zero=not options.no_zero)

    print 'figleaf: HTML output written to %s' % (options.output_dir,)
