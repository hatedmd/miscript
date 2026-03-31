#!/usr/bin/env python3
"""Run .mis files with all parsing and output logic."""

import re
from .file_handler import read_file_content, get_file_info
from .variable_parser import parse_all_variables
from .statement_parser import parse_all_statements
from .expression_evaluator import evaluate_print_statement, escape_string_for_eval
from .window_handler import (
    create_window, add_text_to_window, add_input_to_window, 
    set_window_background, wait_for_windows, get_input_from_window,
    pack_window, update_label_in_window, add_button_to_window
)

# Global function storage
_functions = {}
_window_callbacks = {}

def interpolate_string(text, variables):
    """Replace $variable references inside a string."""
    result = text
    pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)\s*'
    
    for match in re.finditer(pattern, text):
        var_name = match.group(1)
        full_match = match.group(0)
        if var_name in variables:
            var_value = str(variables[var_name]['value'])
            result = result.replace(full_match, var_value, 1)
    
    return result

def is_string_literal(var_value):
    """Check if value is a string literal."""
    stripped = var_value.strip()
    while stripped.startswith('(') and stripped.endswith(')'):
        stripped = stripped[1:-1].strip()
    return (stripped.startswith('"') and stripped.endswith('"')) or \
           (stripped.startswith("'") and stripped.endswith("'"))

def extract_string_content(var_value):
    """Extract string content."""
    stripped = var_value.strip()
    while stripped.startswith('(') and stripped.endswith(')'):
        stripped = stripped[1:-1].strip()
    if (stripped.startswith('"') and stripped.endswith('"')) or \
       (stripped.startswith("'") and stripped.endswith("'")):
        return stripped[1:-1]
    return stripped

def resolve_param_value(param, variables, window_name=None):
    """Resolve parameter value."""
    if isinstance(param, str) or isinstance(param, int):
        return param
    
    if isinstance(param, dict):
        if param.get('type') == 'variable_ref':
            var_name = param.get('value', '')
            if var_name in variables:
                return variables[var_name]['value']
            return f"${var_name}"
        elif param.get('type') == 'entry_keyword':
            if window_name:
                return get_input_from_window(window_name, 'var')
            return ''
        else:
            return param.get('value', '')
    
    return param

def execute_function_body(function_body, variables, window_name):
    """Execute statements inside a function."""
    for stmt in function_body:
        if stmt['type'] == 'variable':
            var_name = stmt['name']
            var_value = stmt['value']
            
            if var_value == 'entry':
                if window_name:
                    input_value = get_input_from_window(window_name, 'var')
                    if input_value is not None:
                        variables[var_name] = {
                            'type': 'string',
                            'value': input_value
                        }
            elif is_string_literal(var_value):
                string_content = extract_string_content(var_value)
                if '$' in string_content:
                    string_content = interpolate_string(string_content, variables)
                variables[var_name] = {
                    'type': 'string',
                    'value': string_content
                }
        
        elif stmt['type'] == 'window_pack':
            if window_name:
                pack_window(window_name)

def create_button_callback(function_body, variables, window_name):
    """Create a callback function for button onClick."""
    def callback():
        execute_function_body(function_body, variables, window_name)
    return callback

def execute_statements(statements, variables):
    """Execute all parsed statements."""
    window_name = None
    
    for stmt in statements:
        if stmt['type'] == 'print':
            output, error = evaluate_print_statement(stmt['argument'], variables)
            if error:
                print(f"⚠️ Error: {error}")
            else:
                print(output)
        
        elif stmt['type'] == 'input':
            try:
                prompt = stmt['prompt']
                if (prompt.startswith('"') and prompt.endswith('"')) or \
                   (prompt.startswith("'") and prompt.endswith("'")):
                    prompt = prompt[1:-1]
                user_input = input(prompt)
                variables[stmt['var_name']] = {
                    'type': 'string',
                    'value': user_input
                }
            except Exception as e:
                print(f"⚠️ Input error: {e}")
        
        elif stmt['type'] == 'function_def':
            _functions['default'] = stmt['body']
        
        elif stmt['type'] == 'function_call':
            if 'default' in _functions:
                execute_function_body(_functions['default'], variables, window_name)
        
        elif stmt['type'] == 'variable':
            var_name = stmt['name']
            var_value = stmt['value']
            
            if is_string_literal(var_value):
                string_content = extract_string_content(var_value)
                if '$' in string_content:
                    string_content = interpolate_string(string_content, variables)
                variables[var_name] = {
                    'type': 'string',
                    'value': string_content
                }
            else:
                output, error = evaluate_print_statement(var_value, variables)
                if not error:
                    variables[var_name] = {
                        'type': 'string',
                        'value': output
                    }
        
        elif stmt['type'] == 'window_init':
            window = create_window(stmt['var_name'], stmt['width'], stmt['height'])
            if window:
                variables[stmt['var_name']] = {
                    'type': 'window',
                    'value': window
                }
                window_name = stmt['var_name']
        
        elif stmt['type'] == 'window_method':
            if stmt['method'] == 'Text':
                params = stmt['params']
                text_param = params.get('text', {'value': '', 'type': 'string'})
                x_param = params.get('x', {'value': 0, 'type': 'number'})
                y_param = params.get('y', {'value': 0, 'type': 'number'})
                
                text = resolve_param_value(text_param, variables, window_name)
                x = resolve_param_value(x_param, variables, window_name)
                y = resolve_param_value(y_param, variables, window_name)
                
                add_text_to_window(window_name, str(text), int(x), int(y), label_name='entry')
            
            elif stmt['method'] == 'BG':
                params = stmt['params']
                if 'colourRGB' in params and params['colourRGB']['type'] == 'rgb_color':
                    set_window_background(window_name, 'rgb_color', params['colourRGB']['value'])
                elif 'colourHEX' in params and params['colourHEX']['type'] == 'hex_color':
                    set_window_background(window_name, 'hex_color', params['colourHEX']['value'])
                elif 'colour' in params and params['colour']['type'] == 'named_color':
                    set_window_background(window_name, 'named_color', params['colour']['value'])
            
            elif stmt['method'] == 'Input':
                params = stmt['params']
                entry_param = params.get('entry', {'value': '', 'type': 'string'})
                x_param = params.get('x', {'value': 0, 'type': 'number'})
                y_param = params.get('y', {'value': 0, 'type': 'number'})
                width_param = params.get('width', {'value': 10, 'type': 'number'})
                length_param = params.get('length', {'value': 20, 'type': 'number'})
                
                var_name = resolve_param_value(entry_param, variables, window_name)
                x = resolve_param_value(x_param, variables, window_name)
                y = resolve_param_value(y_param, variables, window_name)
                width_chars = resolve_param_value(width_param, variables, window_name)
                max_length = resolve_param_value(length_param, variables, window_name)
                
                add_input_to_window(window_name, str(var_name), int(x), int(y), int(width_chars), int(max_length), variables)
            
            elif stmt['method'] == 'Button':
                params = stmt['params']
                x_param = params.get('x', {'value': 0, 'type': 'number'})
                y_param = params.get('y', {'value': 0, 'type': 'number'})
                text_param = params.get('text', {'value': 'Click', 'type': 'string'})
                width_param = params.get('width', {'value': 10, 'type': 'number'})
                length_param = params.get('length', {'value': 1, 'type': 'number'})
                onclick_param = params.get('onClick', None)
                bg_param = params.get('bg', {'value': 'lightgray', 'type': 'string'})  # Default visible color
                fg_param = params.get('fg', {'value': 'black', 'type': 'string'})
                
                x = resolve_param_value(x_param, variables, window_name)
                y = resolve_param_value(y_param, variables, window_name)
                text = resolve_param_value(text_param, variables, window_name)
                width = resolve_param_value(width_param, variables, window_name)
                length = resolve_param_value(length_param, variables, window_name)
                bg = resolve_param_value(bg_param, variables, window_name)
                fg = resolve_param_value(fg_param, variables, window_name)
                
                # Create callback if onClick is specified
                callback = None
                if onclick_param and onclick_param.get('type') == 'function_call':
                    if 'default' in _functions:
                        callback = create_button_callback(_functions['default'], variables, window_name)
                
                add_button_to_window(window_name, int(x), int(y), str(text), callback, int(width), int(length), str(bg), str(fg))
                
                x = resolve_param_value(x_param, variables, window_name)
                y = resolve_param_value(y_param, variables, window_name)
                text = resolve_param_value(text_param, variables, window_name)
                width = resolve_param_value(width_param, variables, window_name)
                length = resolve_param_value(length_param, variables, window_name)  # CHANGED
                
                # Create callback if onClick is specified
                callback = None
                if onclick_param and onclick_param.get('type') == 'function_call':
                    if 'default' in _functions:
                        callback = create_button_callback(_functions['default'], variables, window_name)
                
                add_button_to_window(window_name, int(x), int(y), str(text), callback, int(width), int(length))  # CHANGED
            
            elif stmt['method'] == 'pack':
                if window_name:
                    pack_window(window_name)
        
        elif stmt['type'] == 'window_pack':
            if window_name:
                pack_window(window_name)

def run_mis_file(filepath):
    """Run a single .mis file."""
    content, error = read_file_content(filepath)
    if error:
        print(f"❌ {error}")
        print()
        return False
    
    variables = parse_all_variables(content)
    statements = parse_all_statements(content)
    execute_statements(statements, variables)
    
    return True

def run_all_mis_files(mis_files):
    """Run all .mis files."""
    if not mis_files:
        print("No .mis files found.")
        return 0
    
    for mis_file in mis_files:
        run_mis_file(mis_file)
    
    wait_for_windows()
    
    return len(mis_files)