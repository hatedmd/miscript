#!/usr/bin/env python3
"""Parse print statements from .mis files."""

import re

def extract_print_argument(line):
    """Extract the argument from a print statement."""
    print_match = re.match(r'^print\s*\(\s*(.+?)\s*\)\s*$', line)
    
    if not print_match:
        return None
    
    return print_match.group(1).strip()

def is_simple_string(print_arg):
    """Check if print argument is a simple string literal."""
    return bool(re.match(r'^["\']([^"\']*)["\']$', print_arg))

def extract_string_from_print(print_arg):
    """Extract string content from simple print statement."""
    string_match = re.match(r'^["\']([^"\']*)["\']$', print_arg)
    if string_match:
        return string_match.group(1)
    return None

def parse_all_print_statements(content):
    """Parse all print statements from file content."""
    print_statements = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for print statement
        if line.startswith('print'):
            print_arg = extract_print_argument(line)
            if print_arg:
                print_statements.append({
                    'line': line_num,
                    'argument': print_arg,
                    'is_simple_string': is_simple_string(print_arg)
                })
    
    return print_statements