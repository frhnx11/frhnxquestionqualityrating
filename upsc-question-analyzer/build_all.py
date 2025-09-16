#!/usr/bin/env python3
"""
Build script to create executables for all platforms
Note: This should be run on the respective platforms
"""
import os
import sys
import platform
import subprocess

def get_platform():
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'mac'
    elif system == 'linux':
        return 'linux'
    else:
        return None

def main():
    current_platform = get_platform()
    
    if not current_platform:
        print("❌ Unsupported platform!")
        sys.exit(1)
    
    print(f"🎯 Detected platform: {current_platform}")
    print(f"📦 Building for {current_platform}...")
    
    # Run the appropriate build script
    if current_platform == 'windows':
        subprocess.run([sys.executable, 'build_windows.py'])
    elif current_platform == 'mac':
        subprocess.run([sys.executable, 'build_mac.py'])
    elif current_platform == 'linux':
        subprocess.run([sys.executable, 'build_linux.py'])
    
    print("\n📝 Build Instructions for Other Platforms:")
    print("--------------------------------------------")
    print("To build for other platforms, run this script on those systems:")
    print("- Windows: python build_windows.py")
    print("- macOS:   python build_mac.py")
    print("- Linux:   python build_linux.py")
    print("\nOr use GitHub Actions for automated multi-platform builds!")

if __name__ == '__main__':
    main()