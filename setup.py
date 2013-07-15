#!/usr/bin/env python

from setuptools import setup

VERSION = "1.0"
OVATION_VERSION = "2.0-beta2"

setup(name='field-data',
      version=VERSION,
      description='Ovation Field Data Importer',
      author='Physion',
      author_email='info@ovation.io',
      url='http://ovation.io',
      packages=['field_data'],
      install_requires=["ovation >= {version}".format(version=OVATION_VERSION),
                        "scipy >= 0.12.0",
                        "numpy >= 1.7.1",
                        "pandas >= 0.11.0",
                        "quantities >= 0.10.1",
                        ]
)
