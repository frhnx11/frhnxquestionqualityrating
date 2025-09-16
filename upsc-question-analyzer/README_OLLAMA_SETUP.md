# UPSC Question Analyzer - Local Ollama Setup Guide

## Overview
This application runs entirely on your local machine using Ollama, ensuring complete privacy and no cloud costs. Follow this guide to get started.

## Quick Start

### Step 1: Install Ollama

#### Windows
1. Download Ollama from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically in the background

#### macOS
1. Download Ollama from: https://ollama.com/download/mac
2. Install the application
3. Ollama will be available in your menu bar

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download the AI Model
Open your terminal/command prompt and run:
```bash
ollama pull gemma2:9b
```

This downloads the Google Gemma 2 (9B parameter) model (~6-7GB).

### Step 3: Run the UPSC Analyzer
```bash
python app.py
```

The application will automatically:
- Detect your local Ollama installation
- Connect to the AI model
- Show a green "Ollama Ready" indicator when ready

## Alternative Models
If you prefer a different model, you can use:
- `ollama pull llama3.1:8b` - Meta's Llama 3.1 (8B)
- `ollama pull mistral:7b` - Mistral AI (7B)
- `ollama pull gemma:7b` - Google Gemma (7B)

After downloading, update `config/config.json` to use your preferred model.

## Troubleshooting

### "Ollama Not Found" Error
- **Windows**: Make sure Ollama is running (check system tray)
- **Mac**: Make sure Ollama is running (check menu bar)
- **Linux**: Run `ollama serve` in a terminal

### "Model Not Installed" Error
- Run the model download command: `ollama pull gemma2:9b`
- Wait for the download to complete (~6-7GB)
- Refresh the web page

### Connection Issues
- Verify Ollama is running: `ollama list`
- Check if port 11434 is available
- Restart Ollama service if needed

## System Requirements
- **RAM**: 16GB recommended (minimum 8GB)
- **Storage**: 10GB free space for models
- **OS**: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+)

## Privacy & Security
- All processing happens locally on your machine
- No data is sent to any cloud service
- Your questions and analysis remain completely private

## How It Works
1. **Frontend** connects to your local web server (Flask)
2. **Backend** connects to Ollama running on localhost:11434
3. **Ollama** processes questions using the AI model
4. **Results** are generated and saved locally as Excel files

No internet connection required after initial model download!