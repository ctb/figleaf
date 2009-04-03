"""
figleaf plugin for nose.

Automatically records coverage info for Python tests.
"""

DEFAULT_COVERAGE_FILE='.figleaf'
import pkg_resources

try:
    pkg_resources.require('figleaf>=0.6.1')
    import figleaf
except ImportError:
    figleaf = None

import nose.case
from nose.plugins.base import Plugin

import logging
import os

log = logging.getLogger(__name__)

class Figleaf(Plugin):
    def __init__(self):
        self.name = 'figleaf'
        Plugin.__init__(self)
        self.testname = None

    def add_options(self, parser, env=os.environ):
        env_opt = 'NOSE_WITH_%s' % self.name.upper()
        env_opt.replace('-', '_')
        parser.add_option("--with-%s" % self.name,
                          action="store_true",
                          dest=self.enableOpt,
                          default=env.get(env_opt),
                          help="Enable plugin %s: %s [%s]" %
                          (self.__class__.__name__, self.help(), env_opt))

        parser.add_option("--figleaf-file",
                          action="store",
                          dest="figleaf_file",
                          default=None,
                          help="Store figleaf coverage in this file")
        
    def configure(self, options, config):
        """
        Configure: enable plugin?  And if so, where should the coverage
        info be placed?
        """
        self.conf = config

        # enable?
        if hasattr(options, self.enableOpt):
            self.enabled = getattr(options, self.enableOpt)

        ### save coverage file name, if given.
        if options.figleaf_file:
            self.figleaf_file = options.figleaf_file
        else:
            self.figleaf_file = DEFAULT_COVERAGE_FILE

        if self.enabled and figleaf is None:
            raise Exception("You must install figleaf 0.6.1 before you can use the figleafsections plugin! See http://darcs.idyll.org/~t/projects/figleaf/doc/")

    def begin(self):
        """
        Initialize: start recording coverage info.
        """
        figleaf.start()

    def finalize(self, result):
        """
        Finalize: stop recording coverage info, save & exit.
        """
        figleaf.stop()
        
        figleaf.write_coverage(self.figleaf_file, append=False)
