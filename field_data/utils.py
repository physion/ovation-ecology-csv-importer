import tempfile
import csv

import pandas as pd
import numpy as np
from ovation import DateTime


def read_csv(path, header_row=2, date_column=1):
    tmp_csv = strip_blank_lines(path)
    df = pd.read_csv(tmp_csv,
                        header=header_row,
                        index_col=date_column,
                        parse_dates=True,
                        na_values=[''])

    df['Date'] = [DateTime(str(d)) for d in np.asarray(df.index)]

    return df

def strip_blank_lines(csv_path, reset_cursor=True):
    tmp_csv = tempfile.TemporaryFile(mode='w+b')
    writer = csv.writer(tmp_csv)
    with open(csv_path, 'rU') as csv_file:
        for row in csv.reader(csv_file):
            if any(field.strip() for field in row):
                writer.writerow(row)

    if reset_cursor:
        tmp_csv.seek(0)

    return tmp_csv
