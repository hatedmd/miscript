#!/usr/bin/env python3
"""Handle file operations for .mis files."""

from pathlib import Path

def find_mis_files(directory, recursive=False):
    """Find all .mis files in directory."""
    apps_dir = Path(directory)
    
    if not apps_dir.exists():
        return None, f"Error: '{directory}' directory not found!"
    
    if recursive:
        mis_files = list(apps_dir.rglob("*.mis"))
    else:
        mis_files = list(apps_dir.glob("*.mis"))
    
    return mis_files, None

def read_file_content(filepath):
    """Read content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), None
    except Exception as e:
        return None, f"Error reading file: {e}"

def get_file_info(filepath):
    """Get file information."""
    return {
        'name': filepath.name,
        'path': str(filepath),
        'exists': filepath.exists()
    }