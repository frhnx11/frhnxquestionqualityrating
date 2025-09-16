#!/usr/bin/env python3
"""
Test script to verify path resolution for PyInstaller bundles
"""

import os
import sys
import json

# Helper function to get resource path (same as in app.py)
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

print("Path Resolution Test")
print("=" * 50)
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
print(f"Script location: {__file__ if '__file__' in globals() else 'N/A'}")
print(f"sys.executable: {sys.executable}")

if getattr(sys, 'frozen', False):
    print(f"sys._MEIPASS: {sys._MEIPASS}")
    print(f"PYINSTALLER_EXE_DIR: {os.environ.get('PYINSTALLER_EXE_DIR', 'Not set')}")

print("\nResource Paths:")
print("-" * 50)

# Test paths
test_paths = [
    'config/config.json',
    'config/system_prompt_enhanced.txt',
    'templates',
    'src',
    'version.txt',
    'output'
]

for path in test_paths:
    resolved = get_resource_path(path)
    exists = os.path.exists(resolved)
    print(f"{path:30} -> {resolved}")
    print(f"{'':30}    Exists: {exists}")

# Test loading config
print("\nConfig Loading Test:")
print("-" * 50)
try:
    config_path = get_resource_path('config/config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(f"✓ Config loaded successfully")
    print(f"  Model: {config['ollama']['model']}")
except Exception as e:
    print(f"✗ Failed to load config: {e}")

# Test output directory
print("\nOutput Directory Test:")
print("-" * 50)
if getattr(sys, 'frozen', False):
    exe_dir = os.environ.get('PYINSTALLER_EXE_DIR', os.path.dirname(sys.executable))
    output_dir = os.path.join(exe_dir, 'output')
    print(f"Output directory (bundled): {output_dir}")
else:
    output_dir = get_resource_path('output')
    print(f"Output directory (dev): {output_dir}")

print(f"Output dir exists: {os.path.exists(output_dir)}")
print(f"Output dir writable: {os.access(output_dir, os.W_OK) if os.path.exists(output_dir) else 'N/A'}")

print("\nCurrent Working Directory:")
print("-" * 50)
print(f"CWD: {os.getcwd()}")