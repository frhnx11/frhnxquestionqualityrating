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

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from question_parser import QuestionParser
from ollama_analyzer import OllamaAnalyzer
from excel_generator import ExcelGenerator

app = Flask(__name__)
app.secret_key = 'upsc_analyzer_secret_key_2024'

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
        with open('config/config.json', 'r') as f:
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

@app.route('/health')
def health_check():
    try:
        # Check if Ollama is accessible
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        
        analyzer = OllamaAnalyzer(config)
        ollama_status = analyzer.test_connection()
        
        return jsonify({
            'status': 'healthy',
            'ollama_connected': ollama_status,
            'model': config['ollama']['model']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    print("🚀 Starting UPSC Question Quality Analyzer Web Server")
    print("💡 Open your browser and go to: http://localhost:5000")
    print("⚠️  Make sure Ollama is running before analyzing questions")
    
    app.run(debug=True, host='0.0.0.0', port=5000)