# UPSC Question Quality Analyzer

A comprehensive tool for analyzing UPSC question quality using Ollama AI models and generating detailed Excel reports.

## Features

- 🤖 **AI-Powered Analysis**: Uses Ollama models for sophisticated question quality assessment
- 📊 **Excel Reports**: Generates detailed Excel files with comprehensive analysis tables  
- 📈 **Real-time Progress**: Live progress tracking with rich console display
- 🔄 **Auto-save**: Excel file updates in real-time as questions are processed
- ⚡ **Batch Processing**: Analyze multiple questions efficiently
- 🎯 **UPSC Standards**: Analysis based on actual UPSC examination standards

## Quick Start

### Prerequisites

1. **Ollama Installation**: Install [Ollama](https://ollama.ai) on your system
2. **Python 3.8+**: Ensure Python is installed
3. **Ollama Model**: Pull the recommended model:
   ```bash
   ollama pull llama3.1:8b
   ```

### Installation

#### Option 1: Automatic Setup (Recommended)
```bash
python setup.py
```

#### Option 2: Manual Setup
1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Install and setup Ollama**:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.1:8b
   ```

### Usage

1. **Prepare Questions**: Add your question text file to the `input/` folder
2. **Run Analysis**:
   ```bash
   python run.py        # Easy launcher
   # OR
   python src/main.py   # Direct execution
   ```
3. **View Results**: Open the generated Excel file in `output/` folder

## Input Format

Place your questions file in the `input/` folder with this format:

```
Subject:Indian Physical Geography. Topic:Physiography   Subtopic:Western Ghats

**QUESTION 1**
--------------------
**Q:** With reference to the general characteristics of the Western Ghats, consider the following statements:
1. The Western Ghats stretch for 1,600 km, originating from the Narmada Valley and extending to Kanniyakumari.
2. The average elevation of the Western Ghats consistently decreases from the northern to the southern parts.
3. They rise abruptly from the Western Coastal Plain and feature a gentle slope on their eastern flank.
Which of the statements given above is/are correct?

   A. 1 and 2 only
   B. 3 only
   C. 1, 2 and 3
   D. 2 and 3 only

**Correct Answer:** B. 3 only

**Explanation:** Statement 1 is incorrect because the Western Ghats stretch from the Tapti Valley, not the Narmada Valley, to slightly north of Kanniyakumari. Statement 2 is incorrect as the elevation of the Western Ghats increases from north to south. Statement 3 is correct; the Western Ghats form an abrupt, steep-sided range facing the Western Coastal Plain, while their eastern flank slopes gently towards the Deccan tableland.

============================================================

**QUESTION 2**
[... more questions ...]
```

## Output Format

The tool generates a comprehensive Excel file with these columns:

| Column | Description |
|--------|-------------|
| Subject | Subject area of the question |
| Topic | Main topic covered |
| Subtopic | Specific subtopic |
| Question (Complete) | Full question text with all options |
| Answer with Explanation (Complete) | Correct answer with detailed explanation |
| Rating (out of 10) | Quality rating based on UPSC standards |
| Conceptual Depth | Analysis of conceptual complexity |
| Answer Accuracy | Assessment of factual correctness |
| Topic-Subtopic Relevance | Alignment with specified topics |
| Improved Version | Enhanced question (for low-rated questions) |

## Command Line Options

```bash
# Analyze all files in input folder
python src/main.py

# Analyze specific file
python src/main.py --file questions.txt

# Use simple text output (no rich display)
python src/main.py --no-display

# List available Ollama models
python src/main.py --models

# Check system status
python src/main.py --status

# Use custom config file
python src/main.py --config my_config.json
```

## Configuration

Edit `config/config.json` to customize settings:

```json
{
  "ollama": {
    "model": "llama3.1:8b",
    "base_url": "http://localhost:11434",
    "timeout": 120
  },
  "analysis": {
    "batch_size": 5,
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

## Quality Assessment Scale

- **9-10/10**: UPSC PYQ Standard - Sophisticated analysis requiring deep understanding
- **7-8/10**: Good Quality - Conceptually sound with clear specificity  
- **5-6/10**: Average Quality - Basic institutional level with moderate depth
- **4/10 and below**: Below Standard - Requires improvement

## Recommended Models

| Model | Quality | Speed | RAM Requirement |
|-------|---------|-------|-----------------|
| `llama3.1:70b` | Highest | Slow | 40GB+ |
| `llama3.1:8b` | Good | Fast | 8GB |
| `gemma2:27b` | High | Medium | 16GB |
| `qwen2.5:32b` | High | Medium | 20GB |

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   ollama list
   # Start Ollama if not running
   ollama serve
   ```

2. **Model Not Found**
   ```bash
   # Pull the required model
   ollama pull llama3.1:8b
   ```

3. **No Input Files**
   - Ensure `.txt` files are in the `input/` folder
   - Check file format matches the expected structure

4. **Excel File Issues**
   - Close Excel if the output file is open
   - Check write permissions in `output/` folder

### Performance Tips

- Use `llama3.1:8b` for fastest processing
- Close other applications to free up RAM
- Enable hardware acceleration if available
- Process in smaller batches for large question sets

## Project Structure

```
upsc-question-analyzer/
├── input/              # Place your question files here
├── output/             # Generated Excel files
├── src/                # Source code
│   ├── main.py         # Main application
│   ├── question_parser.py
│   ├── ollama_analyzer.py
│   ├── excel_generator.py
│   └── progress_tracker.py
├── config/             # Configuration files
│   ├── config.json
│   └── system_prompt.txt
└── requirements.txt
```

## License

This project is for educational and research purposes.