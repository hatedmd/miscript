#!/usr/bin/env python3
"""Main entry point for MIS file parser."""

import os
from functions.file_handler import find_mis_files
from functions.runner import run_all_mis_files

def clear_terminal():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main function - just orchestrates the flow."""
    # Clear terminal
    clear_terminal()
    
    apps_dir = "apps"
    recursive = False
    
    mis_files, error = find_mis_files(apps_dir, recursive)
    
    if error:
        print(f"❌ {error}")
        return 1
    
    run_all_mis_files(mis_files)
    
    return 0

if __name__ == "__main__":
    exit(main())