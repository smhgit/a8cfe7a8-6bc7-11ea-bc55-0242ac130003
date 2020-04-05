'''General utils, not related specific to custom components'''

import iso8601


def parse_int(input_value, default_value=None):
    if input_value is None:
        return default_value
    try:
        return int(input_value)
    except ValueError:
        return default_value

def parse_float(input_value, default_value=None):
    if input_value is None:
        return default_value
    try:
        return float(input_value)
    except ValueError:
        return default_value