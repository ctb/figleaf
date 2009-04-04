import os
import re
import sys

import figleaf
from figleaf.annotate import read_exclude_patterns, filter_files, logger, \
     read_files_list

# use builtin sets if in >= 2.4, otherwise use 'sets' module.
try:
    set()
except NameError:
    from sets import Set as set


###


def format_not_covered(numbers):
    """Format the list of uncovered lines to have ranges where possible."""

    numbers = sorted(numbers)

    ranges = [[]]
    for num in numbers:
        if not ranges[-1] or num == ranges[-1][-1] + 1:
            ranges[-1].append(num)
        else:
            ranges.append([num])

    output = []
    for range in ranges:
        if len(range) < 3:
            for x in range:
                output.append(str(x))
        else:
            output.append('%d-%d' % (range[0], range[-1]))

    return ','.join(output)


def calc_coverage_lines(fp, lines, covered):
    n_covered = n_lines = 0
    not_covered = set()

    for i, line in enumerate(fp):
        i += 1
        if i in covered:
            n_covered += 1
            n_lines += 1
        elif i in lines:
            n_lines += 1
            not_covered.add(i)

    try:
        percent = n_covered * 100. / n_lines
    except ZeroDivisionError:
        percent = 100

    return n_covered, n_lines, percent, not_covered


def write_txt_report(info_dict):
    info_dict_items = info_dict.items()

    def sort_by_percent(a, b):
        a = a[1][2]
        b = b[1][2]

        return -cmp(a,b)
    info_dict_items.sort(sort_by_percent)

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

    sys.stdout.write('''
figleaf code coverage report
============================

summary
-------

 %d files total: %d files > 90%%, %d files > 75%%, %d files > 50%%


 totals:
     # lines: %d
     # covered: %d
     %% covered: %.1f%%

details
-------

 filename\t# lines\t# covered\t%% covered
 ---------------------------------------------------
''' % (len(percents), len(percent_90), len(percent_75), len(percent_50),
       summary_lines, summary_cover, summary_percent,))

    for filename, (n_lines, n_covered, percent_covered, not_covered) in info_dict_items:
        not_covered = format_not_covered(not_covered)
        sys.stdout.write(' %s\t%d\t%d\t%.1f\t%s\n'
                % (filename, n_lines, n_covered, percent_covered, not_covered))


def create_report(args, exclude_patterns_file, files_list):

    coverage = {}
    for filename in args:
        logger.debug("loading coverage info from '%s'\n" % (filename,))
        try:
            d = figleaf.read_coverage(filename)
            coverage = figleaf.combine_coverage(coverage, d)
        except IOError:
            logger.error("cannot open filename '%s'\n" % (filename,))

    if not coverage:
        logger.warning('EXITING -- no coverage info!\n')
        sys.exit(-1)

    exclude_patterns = []
    if exclude_patterns_file:
        exclude_patterns = read_exclude_patterns(exclude_patterns_file)

    files_list = files_list and read_files_list(options.files_list) or {}

    keys = coverage.keys()
    info_dict = {}
    for pyfile in filter_files(keys, exclude_patterns, files_list):

        try:
            fp = open(pyfile, 'rU')
            lines = figleaf.get_lines(fp)
        except KeyboardInterrupt:
            raise
        except IOError:
            logger.error('CANNOT OPEN: %s' % (pyfile,))
            continue
        except Exception, e:
            logger.error('ERROR: file %s, exception %s' % (pyfile, str(e)))
            continue

        #
        # ok, we want to annotate this file.  now annotate file ==> html.
        #

        # initialize
        covered = coverage.get(pyfile, set())

        # rewind
        fp.seek(0)

        # annotate
        n_covered, n_lines, percent, not_covered \
                = calc_coverage_lines(fp, lines, covered)

        # summarize
        info_dict[pyfile] = (n_lines, n_covered, percent, not_covered)

    ### print the report
    write_txt_report(info_dict)

    logger.info('reported on %d file(s) total\n' % len(info_dict))

def main():
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

    option_parser.add_option('-q', '--quiet', action='store_true',
                             dest='quiet',
                             help='Suppress all but error messages')
    
    option_parser.add_option('-D', '--debug', action='store_true',
                             dest='debug',
                             help='Show all debugging messages')

    (options, args) = option_parser.parse_args()

    if options.quiet:
        logging.disable(logging.DEBUG)
        
    if options.debug:
        logger.setLevel(logging.DEBUG)

    if not args:
        args = ['.figleaf']

    create_report(args, options.exclude_patterns_file, options.files_list)
