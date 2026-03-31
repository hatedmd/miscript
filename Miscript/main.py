#!/usr/bin/env python3
"""Main entry point for MIS file parser with smart file selection."""

import os
import sys
from pathlib import Path
from functions.file_handler import find_mis_files, read_file_content
from functions.variable_parser import parse_all_variables
from functions.statement_parser import parse_all_statements
from functions.runner import execute_statements, wait_for_windows

def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_file_menu(mis_files):
    """Show a menu of .mis files to choose from."""
    print("\n" + "=" * 60)
    print("🎮 MIS SCRIPT - SELECT FILE TO RUN")
    print("=" * 60)
    print()
    
    for i, file in enumerate(mis_files, 1):
        print(f"  [{i}] {file.name}")
    
    print()
    print("=" * 60)
    
    while True:
        try:
            choice = input("\nEnter file number (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("Goodbye!")
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(mis_files):
                return mis_files[choice_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(mis_files)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

def run_single_file(filepath):
    """Run a single .mis file by path."""
    print(f"\n🚀 Running: {filepath.name}\n")
    print("-" * 60)
    
    content, error = read_file_content(filepath)
    if error:
        print(f"❌ {error}")
        return False
    
    variables = parse_all_variables(content)
    statements = parse_all_statements(content)
    execute_statements(statements, variables)
    return True

def main():
    """Main function with smart file selection."""
    clear_terminal()
    
    # Check if file path provided as argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if filepath.endswith('.mis'):
            return 0 if run_single_file(Path(filepath)) else 1
        else:
            print("Error: File must end with .mis")
            return 1
    
    # Find all .mis files in apps/ folder
    apps_dir = "apps"
    recursive = False
    
    mis_files, error = find_mis_files(apps_dir, recursive)
    
    if error:
        print(f"❌ {error}")
        return 1
    
    if not mis_files:
        print("No .mis files found in 'apps/' folder.")
        return 1
    
    # 🎯 SMART SELECTION LOGIC
    if len(mis_files) == 1:
        # Only 1 file - run it automatically
        selected_file = mis_files[0]
        print(f"\n✅ Found 1 .mis file: {selected_file.name}")
    else:
        # Multiple files - show selection menu
        selected_file = show_file_menu(mis_files)
        
        if not selected_file:
            return 1
    
    # Run the selected file
    run_single_file(selected_file)
    wait_for_windows()
    
    return 0

if __name__ == "__main__":
    exit(main())