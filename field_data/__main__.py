#Copyright (c) 2013, Physion Consulting

import sys
import argparse
import getpass
import logging

from field_data.importer import import_csv, CSV_HEADER_ROW, FIRST_MEASUREMENT_COLUMN_NUMBER, DATE_COLUMN_NUMBER
from ovation.connection import connect

DESCRIPTION = """Import field CSV data into the local Ovation database.
"""

def main(args=sys.argv):

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    auth_group = parser.add_argument_group('authentication')
    auth_group.add_argument('--user', help='ovation.io user email')
    auth_group.add_argument('--password', help='ovation.io password')

    parser.add_argument('files', metavar='f.csv', nargs='+', type=str)#argparse.FileType('r'))

    csv_group = parser.add_argument_group("CSV")
    csv_group.add_argument('--header-rows',
                           help='number of csv header rows. Default = 2',
                           default=CSV_HEADER_ROW)
    csv_group.add_argument('--date-column',
                          help='column number of measurement date (0-indexed). Default = {}'.format(DATE_COLUMN_NUMBER),
                          default=DATE_COLUMN_NUMBER)
    csv_group.add_argument('--measurement-column',
                           help='column number of first measurement. Default = {}'.format(FIRST_MEASUREMENT_COLUMN_NUMBER),
                           default=FIRST_MEASUREMENT_COLUMN_NUMBER)

    parser.add_argument('--timezone', default=None, help='timezone name in which data was collected. Default = local time zone')

    experiment_group = parser.add_argument_group('epoch container')
    experiment_group.add_argument('--container', help='epoch container ID', required=True)
    experiment_group.add_argument('--protocol', help='protocol ID', required=True)


    args = parser.parse_args(args=args)

    logging.basicConfig(filename='import.log',level=logging.INFO)

    if args.user is None:
        args.user = raw_input('ovation.io user: ')

    if args.password is None:
        password = getpass.getpass(prompt='ovation.io password: ')
    else:
        password = args.password

    dsc = connect(args.user, password)
    ctx = dsc.getContext()

    try:
        return import_csv(ctx,
                          container_id=args.container,
                          protocol_id=args.protocol,
                          files=args.files,
                          timezone=args.timezone,
                          csv_header_row=args.header_rows,
                          date_column=args.date_column,
                          first_measurement_column=args.measurement_column)
    except Exception, e:
        logging.error('Unable to import {}'.format(args.files), e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
