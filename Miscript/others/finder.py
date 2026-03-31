#!/usr/bin/env python3
from pathlib import Path

# Define the directory to search
apps_dir = Path("apps")

# Check if the directory exists
if not apps_dir.exists():
    print(f"Error: '{apps_dir}' directory not found!")
    exit(1)

# Find and print all .mis files
print(f"Files with .mis extension in '{apps_dir}':")
print("-" * 50)

mis_files = list(apps_dir.glob("*.mis"))

if mis_files:
    for file in mis_files:
        print(file.name)
    print("-" * 50)
    print(f"Total: {len(mis_files)} file(s) found")
else:
    print("No .mis files found.")