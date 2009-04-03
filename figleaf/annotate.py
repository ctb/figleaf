"""
Common functions for annotating files with figleaf coverage information.

 - read_exclude_patterns
 - read_files_list
 - filter_files

"""
import sys, os
from optparse import OptionParser
import ConfigParser
import re
import logging

from compat import set

import figleaf

thisdir = os.path.dirname(__file__)

try:                                    # 2.3 compatibility
    logging.basicConfig(format='%(message)s', level=logging.WARNING)
except TypeError:
    pass

logger = logging.getLogger('figleaf.annotate')

DEFAULT_CONFIGURE_FILE = ".figleafrc"

### utilities

def read_exclude_patterns(filename):
    """
    Read in exclusion patterns from a file; these are just regexps.
    """
    if not filename:
        return []

    exclude_patterns = []

    fp = open(filename)
    for line in fp:
        line = line.rstrip()
        if line and not line.startswith('#'):
            pattern = re.compile(line)
        exclude_patterns.append(pattern)

    return exclude_patterns

def read_files_list(filename):
    """
    Read in a list of files from a file; these are relative or absolute paths.
    """
    s = {}
    for line in open(filename):
        f = line.strip()
        s[os.path.abspath(f)] = 1
        s[os.path.realpath(f)] = 1

    return s

def filter_files(filenames, exclude_patterns = [], files_list = {}):
    files_list = dict(files_list)       # make copy

    # list of files specified?
    if files_list:
        for filename in filenames:
            try:
                del files_list[os.path.realpath(filename)]
                yield os.path.abspath(filename)
            except KeyError:
                logger.info('SKIPPING %s -- not in files list' % (filename,))
                
        for filename in files_list.keys():
            yield filename

        return

    ### no files list given -- handle differently

    for filename in filenames:
        abspath = os.path.abspath(filename)
        realpath = os.path.realpath(filename)
        
        # check to see if we match anything in the exclude_patterns list
        skip = False
        for pattern in exclude_patterns:
            if pattern.search(abspath) or pattern.search(realpath):
                logger.info('SKIPPING %s -- matches exclusion pattern' % \
                            (filename,))
                skip = True
                break

        if skip:
            continue

        # next, check to see if we're part of the figleaf package.
        if thisdir in filename:
            logger.debug('SKIPPING %s -- part of the figleaf package' % \
                         (filename,))
            continue

        # also, check for <string> (source file from things like 'exec'):
        if filename == '<string>':
            continue

        # miscellaneous other things: doctests
        if filename.startswith('<doctest '):
            continue

        yield realpath
