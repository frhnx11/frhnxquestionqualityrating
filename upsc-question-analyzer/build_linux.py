#!/usr/bin/env python3
"""
Build script for Linux executable
"""
import os
import sys
import shutil
import subprocess

def build_linux():
    print("🏗️  Building UPSC Question Analyzer for Linux...")
    
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
        print(f"📁 Executable location: dist/upsc-question-analyzer")
        
        # Make executable
        os.chmod('dist/upsc-question-analyzer', 0o755)
        
        # Create tar.gz for distribution
        print("📦 Creating distribution archive...")
        tar_cmd = [
            'tar',
            '-czf',
            'dist/UPSC-Analyzer-Linux.tar.gz',
            '-C', 'dist',
            'upsc-question-analyzer'
        ]
        subprocess.run(tar_cmd)
        print("✅ Created: dist/UPSC-Analyzer-Linux.tar.gz")
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    build_linux()