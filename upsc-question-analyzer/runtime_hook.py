import os
import sys

# This file is run by PyInstaller at runtime to set up the environment

if getattr(sys, 'frozen', False):
    # If we're running as a bundled executable, change to the directory
    # containing the executable so relative paths work correctly
    exe_dir = os.path.dirname(sys.executable)
    os.chdir(exe_dir)