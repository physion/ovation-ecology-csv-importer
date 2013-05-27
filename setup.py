#!/usr/bin/env python

from setuptools import setup

VERSION = "1.0"
setup(name='field_data',
      version=VERSION,
      description='Ovation Field Data Importer',
      author='Physion',
      author_email='info@ovation.io',
      url='http://ovation.io',
      packages=['field_data'],
      install_requires=["ovation_api >= {version}".format(version=VERSION),
                        "scipy >= 0.12.0",
                        "numpy >= 1.7.1",
                        "pandas >= 0.11.0",
                        "quantities >= 0.10.1",
                        ]
)
