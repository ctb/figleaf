"""
setuptools config file for figleaf.
"""

try:
    import setuptools
except ImportError:
    raise Exception("you must have ez_setup/setuptools installed in order to use figleaf, sorry...")

from setuptools import setup, find_packages
from distutils.core import Extension

setup(name = 'figleaf',
      version="0.7",
      url = 'http://ctb.github.com/figleaf/doc/',
      download_url = 'http://ctb.github.com/figleaf/figleaf-0.7.tar.gz',
      
      description = 'figleaf code coverage tool',
      author = 'C. Titus Brown',
      author_email = 'titus@idyll.org',
      license='MIT',
      packages=['figleaf'],

# DISABLED until I can get Windows packages building.
#      ext_modules=[Extension('figleaf._coverage', ['figleaf/_coverage.c']),],
      
      entry_points = {
         'console_scripts': [
            'figleaf = figleaf:main',
            'figleaf2html = figleaf.annotate_html:main',
            'figleaf2cov = figleaf.annotate_cover:main',
            'figleaf-report = figleaf.report_text:main',
            'annotate-sections = figleaf.annotate_sections:main',
        ],
        'nose.plugins.0.10': [
            'figleaf = figleaf.nose_plugin:Figleaf',
            'figleaf-sections = figleaf.nose_sections:FigleafSections',
            ],
         },

      test_suite = 'nose.collector'

)
