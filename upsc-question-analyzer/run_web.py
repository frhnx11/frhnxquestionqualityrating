#!/usr/bin/env python3
"""
Web Server Launcher for UPSC Question Quality Analyzer
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading
import requests

def check_server_ready(max_attempts=30):
    """Check if the Flask server is ready"""
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:5000/health', timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def open_browser():
    """Open browser after server starts"""
    if check_server_ready():
        print("✅ Server is ready!")
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:5000')
    else:
        print("⚠️ Server took too long to start, please open http://localhost:5000 manually")

def main():
    print("🎯 UPSC Question Quality Analyzer - Web Interface")
    print("=" * 60)
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is available")
    except ImportError:
        print("❌ Flask not installed!")
        print("💡 Run: pip install -r requirements.txt")
        return
    
    # Check if Ollama is running
    print("🔄 Checking Ollama connection...")
    try:
        import ollama
        models = ollama.list()
        print("✅ Ollama is running")
        
        # Check if our model is available
        with open('config/config.json', 'r') as f:
            import json
            config = json.load(f)
            model_name = config['ollama']['model']
            
        model_found = False
        for model in models['models']:
            if model['name'].startswith(model_name):
                model_found = True
                break
                
        if model_found:
            print(f"✅ Model '{model_name}' is available")
        else:
            print(f"⚠️ Model '{model_name}' not found!")
            print(f"💡 Run: ollama pull {model_name}")
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
    
    print("\n🚀 Starting web server...")
    print("💡 The browser will open automatically")
    print("🌐 Manual URL: http://localhost:5000")
    print("⚠️ Press Ctrl+C to stop the server\n")
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n✋ Server stopped by user")

if __name__ == '__main__':
    main()