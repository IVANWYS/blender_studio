"""Custom validators."""
import re


re_variable_name = re.compile(r'^[a-z][a-z_]+$')


def validate_variable_key(value):
    """Checks if a value looks like a Pythonic variable name."""
    return re_variable_name.match(value)
