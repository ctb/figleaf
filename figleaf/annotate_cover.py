"""
Build coverage reports in a simple text format.

Functions:

 - report_as_cover
 - annotate_file_cov

"""

import os
import re

import figleaf
from figleaf import annotate
from figleaf.annotate import read_exclude_patterns, filter_files, logger

def report_as_cover(coverage, exclude_patterns, files_list,
                    extra_files=None, include_zero=True):
    """
    Annotate Python & other files with basic coverage information.
    """

    ### assemble information

    # python files
    line_info = annotate.build_python_coverage_info(coverage,
                                                    exclude_patterns,
                                                    files_list)

    # any other files that were passed in
    if extra_files:
        for (otherfile, lines, covered) in extra_files:
            line_info[otherfile] = (lines, covered)

    ### annotate each files & gather summary statistics.

    info_dict = {}
    for filename, (lines, covered) in line_info.items():
        fp = open(filename, 'rU')

        (n_covered, n_lines, output) = annotate_file_cov(fp, lines, covered)

        if not include_zero and n_covered == 0: # include in summary stats?
            continue
        
        try:
            pcnt = n_covered * 100. / n_lines
        except ZeroDivisionError:
            pcnt = 100
        info_dict[filename] = (n_lines, n_covered, pcnt)

        outfile = filename + '.cover'
        try:
            outfp = open(outfile, 'w')
            outfp.write("\n".join(output))
            outfp.write("\n")
            outfp.close()
        except IOError:
            logger.warning('cannot open filename %s' % (outfile,))
            continue

        logger.info('reported on %s' % (outfile,))

    logger.info('reported on %d file(s) total\n' % len(info_dict))
    
def annotate_file_cov(fp, line_info, coverage_info):
    """
    Annotate a single file with covered/uncovered lines, returning statistics.
    """
    n_covered = n_lines = 0
    output = []
    
    for i, line in enumerate(fp):
        is_covered = False
        is_line = False

        i += 1

        if i in coverage_info:
            is_covered = True
            prefix = '+'

            n_covered += 1
            n_lines += 1
        elif i in line_info:
            prefix = '-'
            is_line = True

            n_lines += 1
        else:
            prefix = '0'

        line = line.rstrip()
        output.append(prefix + ' ' + line)
    
    return (n_covered, n_lines, output)

###

def main():
    """
    Command-line function to do a basic 'coverage'-style annotation.

    Setuptools entry-point for figleaf2cov; see setup.py
    """
    
    import sys
    import logging
    from optparse import OptionParser
    
    ###

    option_parser = OptionParser()

    option_parser.add_option('-x', '--exclude-patterns', action="store",
                             dest="exclude_patterns_file",
                             help="file containing regexp patterns to exclude")

    option_parser.add_option('-f', '--files-list', action="store",
                             dest="files_list",
                             help="file containing filenames to report on")

    option_parser.add_option('-q', '--quiet', action='store_true',
                             dest='quiet',
         help="file containig regexp patterns of files to exclude from report")
    
    option_parser.add_option('-D', '--debug', action='store_true',
                             dest='debug',
                             help='Show all debugging messages')

    option_parser.add_option('-z', '--no-zero', action='store_true',
                             dest='no_zero',
                             help='Omit files with zero lines covered.')

    (options, args) = option_parser.parse_args()

    logger.setLevel(logging.INFO)

    if options.quiet:
        logger.setLevel(logging.ERROR)

    if options.debug:
        logger.setLevel(logging.DEBUG)

    ### load

    if not args:
        args = ['.figleaf']

    coverage = {}
    for filename in args:
        logger.info("loading coverage info from '%s'\n" % (filename,))
        d = figleaf.read_coverage(filename)
        coverage = figleaf.combine_coverage(coverage, d)

    files_list = {}
    if options.files_list:
        files_list = annotate.read_files_list(options.files_list)

    if not coverage:
        logger.warning('EXITING -- no coverage info!\n')
        sys.exit(-1)

    exclude = []
    if options.exclude_patterns_file:
        exclude = annotate.read_exclude_patterns(options.exclude_patterns_file)

    report_as_cover(coverage, exclude, files_list,
                    include_zero=not options.no_zero)
