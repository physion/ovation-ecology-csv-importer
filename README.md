# Ovation Ecology Field Data Importer

[Ovation](http://ovation.io "ovation.io") is the revolutionary data management service that empowers researchers through the seamless organization of multiple data formats and sources, preservation of the link between raw data and analyses and the ability to securely share of all of this with colleagues and collaborators.

This project provides a Python package for importing field data, recorded in CSV format, into Ovation. The importer leverages the [Pandas](http://http://pandas.pydata.org/ "Pandas") package for reading and manipulating CSV data.

## Installation

To use the the ecology field data importer, install it into your Python interpreter from the terminal command line:

	easy_install field_data

This will install the `field_data` module and all of its dependencies.

If you don't have the `easy_install` program already, install the `setuptools` package by downloading
[distribute_setup.py](http://python-distribute.org/distribute_setup.py) and installing `setuptools` before installing
`field_data`:

    python distribute_setup.py
    easy_install field_data


## Usage

The field data importer is run from the terminal command line. The basic usage looks like:

	python -m field_data --timezone <time zone ID> --container <experiment URI> --protocol <protocol URI> file1.csv file2.csv...

You can get more information about the available arguments by running:

	python -m field_data -h

To find the `Experiment` and `Protocol` URIs, you can copy-and-paste the relevant object(s) from the Ovation application or call the `getURI()` method on either object within Python.

## License

The Ovation Ecology Field Data Importer is Copyright (c) 2013 Physion Consulting LLC and is licensed under the [GPL v3.0 license](http://www.gnu.org/licenses/gpl.html "GPLv3") license.
