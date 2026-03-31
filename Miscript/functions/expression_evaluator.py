#!/usr/bin/env python3
"""Evaluate expressions with variable substitution."""

import re
from .utils import is_string_literal
from .print_parser import extract_string_from_print

def escape_string_for_eval(text):
    """Escape a string value so it's safe for eval."""
    # Escape backslashes first, then quotes
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace("'", "\\'")
    return text

def substitute_variables(expression, variables):
    """Substitute variable names with their values in expression."""
    eval_expr = expression
    
    # First, handle $variable syntax (e.g., $number_as_word)
    dollar_var_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
    for match in re.finditer(dollar_var_pattern, expression):
        var_name = match.group(1)
        if var_name in variables:
            var_value = variables[var_name]['value']
            if isinstance(var_value, str):
                escaped_value = escape_string_for_eval(var_value)
                eval_expr = eval_expr.replace(f'${var_name}', f'"{escaped_value}"')
            else:
                eval_expr = eval_expr.replace(f'${var_name}', str(var_value))
    
    # Then, handle plain variable syntax (e.g., number_as_word)
    # Sort by length (longest first) to avoid partial replacements
    sorted_vars = sorted(variables.keys(), key=len, reverse=True)
    for var_name in sorted_vars:
        # Skip if already processed as $variable
        if f'${var_name}' in expression:
            continue
        
        var_value = variables[var_name]['value']
        # Use word boundaries to match whole variable names only
        pattern = r'\b' + re.escape(var_name) + r'\b'
        
        if isinstance(var_value, str):
            # Wrap string values in quotes for eval (with proper escaping)
            escaped_value = escape_string_for_eval(var_value)
            eval_expr = re.sub(pattern, f'"{escaped_value}"', eval_expr)
        else:
            eval_expr = re.sub(pattern, str(var_value), eval_expr)
    
    return eval_expr

def safe_eval_expression(expression, variables):
    """Safely evaluate expression with variable substitution."""
    try:
        eval_expr = substitute_variables(expression, variables)
        
        # Allow safe built-in functions
        safe_builtins = {
            'str': str,
            'int': int,
            'float': float,
            'len': len,
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
        }
        
        result = eval(eval_expr, {"__builtins__": safe_builtins}, {})
        return str(result), None
    except Exception as e:
        return None, f"Cannot evaluate '{expression}': {e}"

def evaluate_print_statement(print_arg, variables):
    """Evaluate a print statement and return output."""
    # Check if it's a simple string literal (no variables)
    if re.match(r'^["\']([^"\']*)["\']$', print_arg):
        return extract_string_from_print(print_arg), None
    else:
        # Contains variables or expressions - evaluate
        return safe_eval_expression(print_arg, variables)