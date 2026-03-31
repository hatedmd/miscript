#!/usr/bin/env python3
"""Parse all statements from .mis files."""

import re

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
    
    # Check for window method call
    window_method_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*$', line)
    if window_method_match:
        window_name = window_method_match.group(1)
        method_name = window_method_match.group(2)
        params_str = window_method_match.group(3)
        
        # Parse named parameters
        params = {}
        param_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([^,]+)', params_str)
        for param_name, param_value in param_matches:
            param_value = param_value.strip()
            
            # Check for $variable reference
            if param_value.startswith('$'):
                var_name = param_value[1:]
                params[param_name] = {
                    'value': var_name,
                    'type': 'variable_ref'
                }
            # Check for function call (onClick:function())
            elif param_value.startswith('function()'):
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
            # Check for named color
            elif param_name == 'colour' and not param_value.isdigit():
                params[param_name] = {
                    'value': param_value,
                    'type': 'named_color'
                }
            # Check for RGB color
            elif param_name == 'colourRGB':
                rgb_values = re.findall(r'\d+', params_str)
                if len(rgb_values) >= 3:
                    params['colourRGB'] = {
                        'value': [int(rgb_values[0]), int(rgb_values[1]), int(rgb_values[2])],
                        'type': 'rgb_color'
                    }
            # Check for quoted string
            elif (param_value.startswith('"') and param_value.endswith('"')) or \
                 (param_value.startswith("'") and param_value.endswith("'")):
                params[param_name] = {
                    'value': param_value[1:-1],
                    'type': 'string'
                }
            # Check for number
            elif param_value.isdigit():
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