#!/usr/bin/env python3
"""
Build script for Windows executable
"""
import os
import sys
import shutil
import subprocess

def build_windows():
    print("🏗️  Building UPSC Question Analyzer for Windows...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    # Install PyInstaller if not installed
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Run PyInstaller
    print("🔨 Running PyInstaller...")
    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        'upsc-analyzer.spec',
        '--noconfirm',
        '--clean'
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        print(f"📁 Executable location: dist/UPSC-Question-Analyzer.exe")
        
        # Create zip file for distribution
        if shutil.which('powershell'):
            print("📦 Creating distribution zip...")
            zip_cmd = [
                'powershell',
                'Compress-Archive',
                '-Path', 'dist/UPSC-Question-Analyzer.exe',
                '-DestinationPath', 'dist/UPSC-Analyzer-Windows.zip',
                '-Force'
            ]
            subprocess.run(zip_cmd)
            print("✅ Created: dist/UPSC-Analyzer-Windows.zip")
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    build_windows()