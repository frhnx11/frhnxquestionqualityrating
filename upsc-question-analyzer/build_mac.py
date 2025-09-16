#!/usr/bin/env python3
"""
Build script for macOS application
"""
import os
import sys
import shutil
import subprocess

def build_mac():
    print("🏗️  Building UPSC Question Analyzer for macOS...")
    
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
        print(f"📁 App location: dist/UPSC Question Analyzer.app")
        
        # Create zip file for distribution
        print("📦 Creating distribution zip...")
        os.chdir('dist')
        zip_cmd = [
            'zip',
            '-r',
            'UPSC-Analyzer-macOS.zip',
            'UPSC Question Analyzer.app'
        ]
        subprocess.run(zip_cmd)
        os.chdir('..')
        print("✅ Created: dist/UPSC-Analyzer-macOS.zip")
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    build_mac()