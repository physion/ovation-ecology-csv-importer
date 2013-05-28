from nose.tools import istest, assert_equals

from field_data.utils import strip_blank_lines

@istest
def should_remove_blank_csv_lines():
    tmp = strip_blank_lines('fixtures/example_field_data.csv')
    assert_equals(9, len(tmp.readlines()))
