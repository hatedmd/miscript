#!/usr/bin/env python3
"""Parse variable assignments from .mis files."""

import re
from .utils import is_string_literal, is_number, extract_string_content

def parse_variable(line):
    """Parse a single variable assignment line."""
    var_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?)\s*$', line)
    
    if not var_match:
        return None
    
    var_name = var_match.group(1)
    var_value = var_match.group(2).strip()
    
    # Determine type
    if is_string_literal(var_value):
        var_type = "string"
        var_content = extract_string_content(var_value)
    elif is_number(var_value):
        var_type = "number"
        var_content = float(var_value) if '.' in var_value else int(var_value)
    else:
        var_type = "other"
        var_content = var_value
    
    return {
        'name': var_name,
        'type': var_type,
        'value': var_content,
        'raw_value': var_value
    }

def parse_all_variables(content):
    """Parse all variables from file content."""
    variables = {}
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Skip print statements
        if line.startswith('print'):
            continue
        
        var_data = parse_variable(line)
        if var_data:
            var_data['line'] = line_num
            variables[var_data['name']] = var_data
    
    return variables