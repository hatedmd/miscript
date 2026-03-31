#!/usr/bin/env python3
from pathlib import Path
import re

def parse_mis_file(content):
    """Parse .mis file content and extract variables and print statements."""
    variables = []
    print_statements = []
    
    # Pattern for variable assignment: var_name = "string" or var_name = number
    var_pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?)\s*$'
    
    # Pattern for print statements with string literals
    print_pattern = r'print\s*\(\s*["\']([^"\']*)["\']\s*\)'
    
    for line_num, line in enumerate(content.split('\n'), 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for variable assignment
        var_match = re.match(var_pattern, line)
        if var_match:
            var_name = var_match.group(1)
            var_value = var_match.group(2).strip()
            
            # Determine if it's a string or number
            if (var_value.startswith('"') and var_value.endswith('"')) or \
               (var_value.startswith("'") and var_value.endswith("'")):
                var_type = "string"
                var_content = var_value[1:-1]  # Remove quotes
            elif var_value.replace('.', '', 1).replace('-', '', 1).isdigit():
                var_type = "number"
                var_content = var_value
            else:
                var_type = "other"
                var_content = var_value
            
            variables.append({
                'line': line_num,
                'name': var_name,
                'type': var_type,
                'value': var_content
            })
        
        # Check for print statement
        print_match = re.search(print_pattern, line)
        if print_match:
            print_statements.append({
                'line': line_num,
                'text': print_match.group(1)
            })
    
    return variables, print_statements

# Define the directory to search
apps_dir = Path("apps")

if not apps_dir.exists():
    print(f"Error: '{apps_dir}' directory not found!")
    exit(1)

mis_files = list(apps_dir.glob("*.mis"))

if not mis_files:
    print("No .mis files found.")
    exit(0)

print(f"📁 Processing {len(mis_files)} .mis file(s):\n")

for mis_file in mis_files:
    print(f"{'='*60}")
    print(f"📄 File: {mis_file.name}")
    print(f"{'='*60}")
    
    try:
        with open(mis_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        variables, print_statements = parse_mis_file(content)
        
        # Display variables
        if variables:
            print("\n📌 VARIABLES:")
            print("-" * 60)
            for var in variables:
                if var['type'] == 'string':
                    print(f"  Line {var['line']}: {var['name']} = \"{var['value']}\" [STRING]")
                elif var['type'] == 'number':
                    print(f"  Line {var['line']}: {var['name']} = {var['value']} [NUMBER]")
                else:
                    print(f"  Line {var['line']}: {var['name']} = {var['value']} [OTHER]")
        else:
            print("\n📌 No variables found.")
        
        # Display print statements
        if print_statements:
            print("\n🖨️  PRINT STATEMENTS:")
            print("-" * 60)
            for stmt in print_statements:
                print(f"  Line {stmt['line']}: → {stmt['text']}")
        else:
            print("\n🖨️  No print statements found.")
        
        print()
    
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        print()

print(f"{'='*60}")
print("✅ Done!")