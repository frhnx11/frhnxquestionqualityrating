#!/usr/bin/env python3
"""
Web Frontend for UPSC Question Quality Analyzer
"""

from flask import Flask, render_template, request, jsonify, send_file, session
import os
import sys
import uuid
import threading
import time
from datetime import datetime
import json

# Helper function to get resource path (defined early for use throughout)
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

# Add src to path
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    base_path = sys._MEIPASS
    src_path = os.path.join(base_path, 'src')
else:
    # Running in normal Python environment
    base_path = os.path.dirname(__file__)
    src_path = os.path.join(base_path, 'src')

sys.path.insert(0, src_path)

from question_parser import QuestionParser
from ollama_analyzer import OllamaAnalyzer
from excel_generator import ExcelGenerator

app = Flask(__name__)
app.secret_key = 'upsc_analyzer_secret_key_2024'

# Version information
try:
    with open(get_resource_path('version.txt'), 'r') as f:
        __version__ = f.read().strip()
except:
    __version__ = '1.0.0'

# Global storage for analysis sessions
analysis_sessions = {}

class WebAnalysisSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.status = "initializing"
        self.current_question = 0
        self.total_questions = 0
        self.progress_messages = []
        self.excel_path = None
        self.error = None
        self.completed = False
        
        # Load config
        config_path = get_resource_path('config/config.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
    
    def add_message(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.progress_messages.append(f"[{timestamp}] {message}")
    
    def analyze_questions(self, subject, topic, subtopic, question_text):
        try:
            self.status = "parsing"
            self.add_message("🔄 Parsing questions from text...")
            
            # Create formatted text for parsing
            formatted_text = f"Subject:{subject}. Topic:{topic}   Subtopic:{subtopic}\n\n{question_text}"
            
            # Parse questions
            parser = QuestionParser()
            questions = parser.parse_content(formatted_text)
            
            if not questions:
                self.error = "No questions found in the provided text"
                self.status = "error"
                return
            
            self.total_questions = len(questions)
            self.add_message(f"📊 Found {self.total_questions} questions to analyze")
            
            # Initialize analyzer and Excel generator
            self.status = "initializing_ai"
            self.add_message("🤖 Initializing AI analyzer...")
            
            analyzer = OllamaAnalyzer(self.config)
            
            # Test connection
            if not analyzer.test_connection():
                self.error = "Cannot connect to Ollama. Make sure Ollama is running and the model is available."
                self.status = "error"
                return
            
            # Setup Excel generator
            excel_config = self.config.copy()
            excel_config['output']['excel_filename'] = f"analysis_{self.session_id}.xlsx"
            # Update output folder based on execution context
            if getattr(sys, 'frozen', False):
                # For bundled executable, use output next to executable
                excel_config['output']['folder'] = os.path.join(os.path.dirname(sys.executable), 'output')
            else:
                # In development, use relative path
                excel_config['output']['folder'] = 'output'
            
            excel_generator = ExcelGenerator(excel_config)
            self.excel_path = excel_generator.get_excel_path()
            
            self.status = "analyzing"
            self.add_message("⚡ Starting question analysis...")
            
            # Process each question
            for i, question in enumerate(questions, 1):
                self.current_question = i
                self.add_message(f"📝 Processing Question {i}/{self.total_questions}")
                
                try:
                    # Format question for analysis
                    formatted_question = parser.format_question_for_analysis(question)
                    
                    # Analyze with Ollama
                    result = analyzer.analyze_question(formatted_question)
                    
                    if result:
                        # Add to Excel
                        if excel_generator.add_analysis_result(result):
                            self.add_message(f"✅ Question {i} analyzed successfully")
                        else:
                            self.add_message(f"❌ Question {i} - Failed to add to Excel")
                    else:
                        self.add_message(f"❌ Question {i} - Analysis failed")
                        
                except Exception as e:
                    self.add_message(f"❌ Question {i} - Error: {str(e)}")
            
            # Finalize Excel
            self.add_message("📊 Finalizing Excel report...")
            excel_generator.finalize_excel()
            
            self.status = "completed"
            self.completed = True
            self.add_message("🎉 Analysis completed successfully!")
            self.add_message(f"📄 Excel file ready for download")
            
        except Exception as e:
            self.error = f"Analysis failed: {str(e)}"
            self.status = "error"
            self.add_message(f"❌ Fatal error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def start_analysis():
    try:
        data = request.json
        subject = data.get('subject', '').strip()
        topic = data.get('topic', '').strip()
        subtopic = data.get('subtopic', '').strip()
        question_text = data.get('question_text', '').strip()
        
        # Validation
        if not all([subject, topic, subtopic, question_text]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if '**QUESTION' not in question_text:
            return jsonify({'error': 'No questions found. Make sure your text contains **QUESTION N** markers'}), 400
        
        # Create new session
        session_id = str(uuid.uuid4())[:8]
        analysis_session = WebAnalysisSession(session_id)
        analysis_sessions[session_id] = analysis_session
        
        # Start analysis in background thread
        thread = threading.Thread(
            target=analysis_session.analyze_questions,
            args=(subject, topic, subtopic, question_text)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'session_id': session_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<session_id>')
def get_progress(session_id):
    session_data = analysis_sessions.get(session_id)
    
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    progress_percent = 0
    if session_data.total_questions > 0:
        progress_percent = int((session_data.current_question / session_data.total_questions) * 100)
    
    return jsonify({
        'status': session_data.status,
        'current_question': session_data.current_question,
        'total_questions': session_data.total_questions,
        'progress_percent': progress_percent,
        'messages': session_data.progress_messages[-10:],  # Last 10 messages
        'completed': session_data.completed,
        'error': session_data.error,
        'has_excel': session_data.excel_path and os.path.exists(session_data.excel_path)
    })

@app.route('/download/<session_id>')
def download_excel(session_id):
    session_data = analysis_sessions.get(session_id)
    
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    if not session_data.excel_path or not os.path.exists(session_data.excel_path):
        return jsonify({'error': 'Excel file not found'}), 404
    
    return send_file(
        session_data.excel_path,
        as_attachment=True,
        download_name=f'upsc_analysis_{session_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/models')
def list_models():
    try:
        config_path = get_resource_path('config/config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        analyzer = OllamaAnalyzer(config)
        
        try:
            available_models = analyzer.get_available_models()
            required_model = config['ollama']['model']
            
            # Format model information
            model_info = []
            for model in available_models:
                model_info.append({
                    'name': model,
                    'is_required': model == required_model,
                    'is_compatible': model in ['gemma2:9b', 'llama3.1:8b', 'mistral:7b', 'gemma:7b']
                })
            
            return jsonify({
                'success': True,
                'models': model_info,
                'required_model': required_model,
                'total_models': len(available_models)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Cannot connect to Ollama',
                'message': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ollama/pull/<model_name>', methods=['POST'])
def pull_model(model_name):
    """Endpoint to trigger model pull (returns command, doesn't execute)"""
    # Validate model name
    allowed_models = ['gemma2:9b', 'llama3.1:8b', 'mistral:7b', 'gemma:7b']
    
    if model_name not in allowed_models:
        return jsonify({
            'success': False,
            'error': 'Model not in allowed list',
            'allowed_models': allowed_models
        }), 400
    
    return jsonify({
        'success': True,
        'model': model_name,
        'command': f'ollama pull {model_name}',
        'message': 'Run this command in your terminal to download the model'
    })

@app.route('/health')
def health_check():
    try:
        # Check if Ollama is accessible
        config_path = get_resource_path('config/config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        analyzer = OllamaAnalyzer(config)
        
        # Get detailed status
        ollama_connected = False
        available_models = []
        model_available = False
        required_model = config['ollama']['model']
        
        try:
            # Test basic connection
            ollama_connected = analyzer.test_connection()
            
            if ollama_connected:
                # Get available models
                available_models = analyzer.get_available_models()
                model_available = required_model in available_models
        except Exception as conn_error:
            ollama_connected = False
        
        # Prepare installation instructions based on OS
        installation_instructions = {
            'windows': {
                'download_url': 'https://ollama.com/download/windows',
                'steps': [
                    'Download Ollama from https://ollama.com/download/windows',
                    'Run the installer',
                    'Open Command Prompt or PowerShell',
                    f'Run: ollama pull {required_model}'
                ]
            },
            'mac': {
                'download_url': 'https://ollama.com/download/mac',
                'steps': [
                    'Download Ollama from https://ollama.com/download/mac',
                    'Install the application',
                    'Open Terminal',
                    f'Run: ollama pull {required_model}'
                ]
            },
            'linux': {
                'download_url': 'https://ollama.com/download/linux',
                'steps': [
                    'Open Terminal',
                    'Run: curl -fsSL https://ollama.com/install.sh | sh',
                    f'Run: ollama pull {required_model}'
                ]
            }
        }
        
        # Determine status and next steps
        if ollama_connected and model_available:
            status = 'ready'
            message = 'Ollama is connected and model is available'
        elif ollama_connected and not model_available:
            status = 'model_missing'
            message = f'Ollama is connected but model {required_model} is not installed'
        else:
            status = 'ollama_not_found'
            message = 'Ollama is not running or not installed'
        
        return jsonify({
            'status': status,
            'message': message,
            'ollama_connected': ollama_connected,
            'model_available': model_available,
            'required_model': required_model,
            'available_models': available_models,
            'installation_instructions': installation_instructions,
            'model_pull_command': f'ollama pull {required_model}',
            'alternative_models': ['llama3.1:8b', 'mistral:7b', 'gemma:7b'] if not model_available else [],
            'app_version': __version__
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'error': str(e)
        }), 500

def open_browser():
    """Open the web browser after a short delay"""
    import webbrowser
    import time
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    if getattr(sys, 'frozen', False):
        # For bundled executable, create output next to the executable
        output_dir = os.path.join(os.path.dirname(sys.executable), 'output')
    else:
        # In development, use current directory
        output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    print("🚀 Starting UPSC Question Quality Analyzer Web Server")
    print("💡 Opening your browser to: http://localhost:5000")
    print("⚠️  Make sure Ollama is running before analyzing questions")
    
    # Start browser opening in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Check if running from PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
    else:
        # Running in normal Python environment
        app.run(debug=True, host='0.0.0.0', port=5000)