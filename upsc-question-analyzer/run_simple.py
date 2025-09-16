#!/usr/bin/env python3
"""
Simple runner with clean progress display
"""

import subprocess
import sys
import os

def main():
    print("🎯 UPSC Question Quality Analyzer")
    print("=" * 40)
    
    # Check for input files
    input_files = [f for f in os.listdir('input') if f.endswith('.txt')]
    if not input_files:
        print("❌ No .txt files found in input folder!")
        sys.exit(1)
    
    print(f"📄 Found {len(input_files)} file(s)\n")
    
    # Run analyzer with no display mode for clean output
    try:
        result = subprocess.run([
            sys.executable, 'src/main.py', '--no-display'
        ])
        
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\n⚠️  Stopped by user")
        sys.exit(130)

if __name__ == '__main__':
    main()