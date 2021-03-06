#Copyright (c) 2013, Physion Consulting

import sys

from field_data.importer import import_csv, CSV_HEADER_ROW, FIRST_MEASUREMENT_COLUMN_NUMBER, DATE_COLUMN_NUMBER
from ovation.importer import import_main

DESCRIPTION = """Import field CSV data into the local Ovation database.
"""

def main(args=sys.argv, dsc=None):

    def parser_callback(parser):
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

        return parser


    def import_wrapper(ctx,
                       container=None,
                       protocol=None,
                       files=None,
                       timezone=None,
                       header_rows=None,
                       date_column=None,
                       measurement_column=None,
                       **args):

        return import_csv(ctx,
                          container_uri=container,
                          protocol_uri=protocol,
                          files=files,
                          timezone=timezone,
                          csv_header_row=header_rows,
                          date_column=date_column,
                          first_measurement_column=measurement_column)

    return import_main(argv=args,
                       name='field_data',
                       description=DESCRIPTION,
                       file_ext='csv',
                       parser_callback=parser_callback,
                       import_fn=import_wrapper,
                       dsc=dsc)



if __name__ == '__main__':
    sys.exit(main())
