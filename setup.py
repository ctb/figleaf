try:
    import setuptools
except ImportError:
    raise Exception("you must have ez_setup/setuptools installed in order to use figleaf, sorry...")

from setuptools import setup, find_packages

setup(name = 'figleaf',
      version="0.6.1",
      url = 'http://darcs.idyll.org/~t/projects/figleaf/doc/',
      download_url = 'http://darcs.idyll.org/~t/projects/figleaf-0.6.1.tar.gz',
      
      description = 'figleaf code coverage tool',
      author = 'C. Titus Brown',
      author_email = 'titus@caltech.edu',
      license='BSD',
      packages=['figleaf'],
      entry_points = {
         'console_scripts': [
            'figleaf = figleaf:main',
            'figleaf2html = figleaf.annotate_html:main',
            'figleaf2cov = figleaf.annotate_cover:main',
            'figleaf2ast = figleaf:display_ast',
            'annotate-sections = figleaf.annotate_sections:main',
        ],
        'nose.plugins.0.10': [
            'figleaf-sections = figleaf.nose_sections:FigleafSections',
            ],
         }
)

