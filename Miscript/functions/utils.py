#!/usr/bin/env python3
"""Utility functions for the MIS parser."""

import re

def is_string_literal(value):
    """Check if value is a string literal (wrapped in quotes)."""
    return (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'"))

def is_number(value):
    """Check if value is a number."""
    return bool(re.match(r'^-?\d+(\.\d+)?$', value))

def extract_string_content(value):
    """Remove quotes from string literal."""
    if is_string_literal(value):
        return value[1:-1]
    return value

def format_variable_output(name, var_type, value, line_num):
    """Format variable information for display."""
    if var_type == 'string':
        return f"  Line {line_num}: {name} = \"{value}\" [STRING]"
    elif var_type == 'number':
        return f"  Line {line_num}: {name} = {value} [NUMBER]"
    else:
        return f"  Line {line_num}: {name} = {value} [OTHER]"