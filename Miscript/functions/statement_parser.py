#!/usr/bin/env python3
"""Parse all statements from .mis files."""

import re

def _extract_method_params(line):
    """
    Extract window_name, method_name, and params_str from a window method call.
    Handles nested parentheses like onClick:function().
    Returns (window_name, method_name, params_str) or None.
    """
    # Match up to the first '(' after the method name
    header_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
    if not header_match:
        return None

    window_name = header_match.group(1)
    method_name = header_match.group(2)

    # Find the matching closing ')' by counting depth
    start = header_match.end()  # index right after the opening '('
    depth = 1
    i = start
    while i < len(line) and depth > 0:
        if line[i] == '(':
            depth += 1
        elif line[i] == ')':
            depth -= 1
        i += 1

    if depth != 0:
        return None  # unmatched parens

    params_str = line[start:i - 1].strip()
    return window_name, method_name, params_str


def parse_statement(line):
    """Parse a single statement line."""
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None
    
    # Check for function definition
    func_match = re.match(r'^function\s*\(\s*\)\s*\{', line)
    if func_match:
        return {
            'type': 'function_start',
            'body': []
        }
    
    # Check for function end
    if line == '}':
        return {
            'type': 'function_end'
        }
    
    # Check for function call
    func_call_match = re.match(r'^function\s*\(\s*\)', line)
    if func_call_match:
        return {
            'type': 'function_call'
        }
    
    # Check for window.pack
    if line == 'window.pack':
        return {
            'type': 'window_pack'
        }
    
    # Check for print statement
    print_match = re.match(r'^print\s*\(\s*(.+?)\s*\)\s*$', line)
    if print_match:
        return {
            'type': 'print',
            'argument': print_match.group(1).strip()
        }
    
    # Check for input statement (terminal input)
    input_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*input\s*\(\s*(.+?)\s*\)\s*$', line)
    if input_match:
        var_name = input_match.group(1)
        prompt = input_match.group(2).strip()
        return {
            'type': 'input',
            'var_name': var_name,
            'prompt': prompt
        }
    
    # Check for window method call (handles nested parens like onClick:function())
    method_result = _extract_method_params(line)
    if method_result:
        window_name, method_name, params_str = method_result

        # Parse named parameters — split on commas that are NOT inside parentheses
        params = {}
        param_pairs = _split_params(params_str)

        for pair in param_pairs:
            colon_idx = pair.find(':')
            if colon_idx == -1:
                continue
            param_name = pair[:colon_idx].strip()
            param_value = pair[colon_idx + 1:].strip()

            if not param_name:
                continue

            # Check for $variable reference
            if param_value.startswith('$'):
                var_name = param_value[1:]
                params[param_name] = {
                    'value': var_name,
                    'type': 'variable_ref'
                }
            # Check for function call (onClick:function())
            elif re.match(r'^function\s*\(\s*\)', param_value):
                params[param_name] = {
                    'value': 'function',
                    'type': 'function_call'
                }
            # Check for special 'entry' keyword
            elif param_value == 'entry':
                params[param_name] = {
                    'value': 'entry',
                    'type': 'entry_keyword'
                }
            # Check for HEX color
            elif param_value.startswith('#'):
                params[param_name] = {
                    'value': param_value,
                    'type': 'hex_color'
                }
            # Check for quoted string
            elif (param_value.startswith('"') and param_value.endswith('"')) or \
                 (param_value.startswith("'") and param_value.endswith("'")):
                params[param_name] = {
                    'value': param_value[1:-1],
                    'type': 'string'
                }
            # Check for RGB color (colourRGB:255, 0, 0)
            elif param_name == 'colourRGB':
                # Parse the RGB values from this parameter's value
                rgb_values = re.findall(r'\d+', param_value)
                if len(rgb_values) >= 3:
                    params['colourRGB'] = {
                        'value': [int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2])],
                        'type': 'rgb_color'
                    }
            # Check for named color (colour param with non-numeric value)
            elif param_name == 'colour' and not param_value.isdigit():
                params[param_name] = {
                    'value': param_value,
                    'type': 'named_color'
                }
            # Check for number
            elif re.match(r'^\d+$', param_value):
                params[param_name] = {
                    'value': int(param_value),
                    'type': 'number'
                }
            else:
                params[param_name] = {
                    'value': param_value,
                    'type': 'unknown'
                }

        return {
            'type': 'window_method',
            'window_name': window_name,
            'method': method_name,
            'params': params
        }

    # Check for window.init assignment
    window_init_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*window\.init\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', line)
    if window_init_match:
        return {
            'type': 'window_init',
            'var_name': window_init_match.group(1),
            'width': int(window_init_match.group(2)),
            'height': int(window_init_match.group(3))
        }
    
    # Check for variable assignment
    var_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?)\s*$', line)
    if var_match:
        return {
            'type': 'variable',
            'name': var_match.group(1),
            'value': var_match.group(2).strip()
        }
    
    # Unknown statement type
    return {
        'type': 'unknown',
        'raw': line
    }


def _split_params(params_str):
    """
    Split a parameter string by commas, but ignore commas inside parentheses.
    e.g. 'onClick:function(), x:100, y:200' → ['onClick:function()', ' x:100', ' y:200']
    """
    parts = []
    depth = 0
    current = []
    for ch in params_str:
        if ch == '(':
            depth += 1
            current.append(ch)
        elif ch == ')':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())
    return parts


def parse_all_statements(content):
    """Parse all statements from file content, including function bodies."""
    statements = []
    lines = content.split('\n')
    
    in_function = False
    function_body = []
    
    for line_num, line in enumerate(lines, 1):
        stmt = parse_statement(line)
        if stmt:
            stmt['line'] = line_num
            
            if stmt['type'] == 'function_start':
                in_function = True
                function_body = []
            elif stmt['type'] == 'function_end':
                in_function = False
                statements.append({
                    'type': 'function_def',
                    'body': function_body,
                    'line': line_num
                })
            elif in_function:
                function_body.append(stmt)
            else:
                statements.append(stmt)
    
    return statements