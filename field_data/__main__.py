#Copyright (c) 2013, Physion Consulting

import sys
import argparse
import getpass
import logging

from field_data.importer import import_csv
from ovation.connection import connect

DESCRIPTION = """Import field CSV data into the local Ovation database.
"""

def main():

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    auth_group = parser.add_argument_group('authentication')
    auth_group.add_argument('--user', help='ovation.io user email')

    parser.add_argument('files', metavar='f.csv', nargs='+', type=str)#argparse.FileType('r'))

    csv_group = parser.add_argument_group("CSV")
    csv_group.add_argument('--header-rows', help='number of csv header rows. Default = 2', default=2)
    csv_group.add_arguent('--date-column', help='column number of measurement date (0-indexed). Default = 1', default=1)

    parser.add_argument('--timezone', default=None, help='timezone name in which data was collected. Default = local time zone')

    experiment_group = parser.add_argument_group('epoch container')
    experiment_group.add_argument('--container', help='epoch container ID', required=True)
    experiment_group.add_argument('--protocol', help='protocol ID', required=True)


    args = parser.parse_args()

    logging.basicConfig(filename='import.log',level=logging.INFO)

    if args.user is None:
        args.user = raw_input('ovation.io user: ')

    password = getpass.getpass(prompt='ovation.io password: ')

    dsc = connect(args.user, password)
    ctx = dsc.getContext()

    return import_csv(ctx,
                      container_id=args.container,
                      protocol_id=args.protocol,
                      files=args.files,
                      timezone=args.timezone)



if __name__ == '__main__':
    sys.exit(main())
