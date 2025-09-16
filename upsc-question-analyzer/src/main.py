#!/usr/bin/env python3
"""
UPSC Question Quality Analysis Tool
Analyzes UPSC questions using Ollama and generates Excel reports
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Optional
import signal

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from question_parser import QuestionParser, Question
from ollama_analyzer import OllamaAnalyzer, AnalysisResult
from excel_generator import ExcelGenerator
from progress_tracker import ProgressTracker, SimpleProgressTracker

class UPSCAnalyzer:
    def __init__(self, config_path: str = 'config/config.json'):
        self.config = self._load_config(config_path)
        self.parser = QuestionParser()
        self.analyzer = OllamaAnalyzer(self.config)
        self.excel_generator = None
        self.progress_tracker = None
        self.interrupted = False
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            "ollama": {
                "model": "llama3.1:8b",
                "base_url": "http://localhost:11434",
                "timeout": 120
            },
            "input": {
                "folder": "input",
                "file_pattern": "*.txt"
            },
            "output": {
                "folder": "output",
                "excel_filename": "analysis_results.xlsx"
            },
            "analysis": {
                "batch_size": 5,
                "max_retries": 3,
                "retry_delay": 2
            },
            "excel": {
                "auto_save_interval": 30,
                "sheet_name": "UPSC Question Analysis"
            }
        }
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signal"""
        print("\n\n⚠️  Interrupt received. Finishing current analysis and saving results...")
        self.interrupted = True
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        # Check if Ollama is running
        print(f"   Testing Ollama connection (model: {self.config['ollama']['model']})...")
        if not self.analyzer.test_connection():
            print("❌ Ollama connection failed!")
            print("   Make sure Ollama is running and the model is available.")
            print(f"   Try running: ollama pull {self.config['ollama']['model']}")
            return False
        print("✅ Ollama connection successful")
        
        # Check input folder
        input_folder = self.config['input']['folder']
        if not os.path.exists(input_folder):
            print(f"❌ Input folder '{input_folder}' does not exist!")
            return False
        print(f"✅ Input folder '{input_folder}' found")
        
        # Check for input files
        input_files = self._find_input_files()
        if not input_files:
            print(f"❌ No .txt files found in '{input_folder}' folder!")
            print("   Please add your question file to the input folder.")
            return False
        print(f"✅ Found {len(input_files)} input file(s)")
        
        return True
    
    def _find_input_files(self) -> List[str]:
        """Find all .txt files in input folder"""
        input_folder = self.config['input']['folder']
        txt_files = []
        
        for file in os.listdir(input_folder):
            if file.endswith('.txt'):
                txt_files.append(os.path.join(input_folder, file))
        
        return txt_files
    
    def analyze_file(self, file_path: str, use_rich_display: bool = True) -> bool:
        """Analyze questions from a single file"""
        try:
            print(f"\n📄 Processing file: {file_path}")
            
            # Parse questions
            questions = self.parser.parse_file(file_path)
            if not questions:
                print("❌ No questions found in file!")
                return False
            
            print(f"📊 Found {len(questions)} questions to analyze")
            
            # Setup Excel generator
            self.excel_generator = ExcelGenerator(self.config)
            excel_path = self.excel_generator.get_excel_path()
            
            # Setup progress tracker
            if use_rich_display:
                try:
                    self.progress_tracker = ProgressTracker(len(questions), excel_path)
                except Exception:
                    # Fallback to simple tracker
                    self.progress_tracker = SimpleProgressTracker(len(questions), excel_path)
            else:
                self.progress_tracker = SimpleProgressTracker(len(questions), excel_path)
            
            # Start live display if available
            live_display = None
            if hasattr(self.progress_tracker, 'start_live_display'):
                try:
                    live_display = self.progress_tracker.start_live_display()
                    live_display.start()
                except Exception as e:
                    print(f"Could not start live display: {e}")
                    live_display = None
            
            # Process questions
            success_count = 0
            for i, question in enumerate(questions, 1):
                if self.interrupted:
                    print(f"\n⚠️  Processing interrupted at question {i}/{len(questions)}")
                    break
                
                try:
                    # Update progress
                    self.progress_tracker.update_current_question(question.question_text, i)
                    if live_display:
                        self.progress_tracker.update_display(live_display)
                    
                    # Format question for analysis
                    formatted_question = self.parser.format_question_for_analysis(question)
                    
                    # Analyze with Ollama
                    result = self.analyzer.analyze_question(formatted_question)
                    
                    if result:
                        # Add to Excel
                        if self.excel_generator.add_analysis_result(result):
                            self.progress_tracker.mark_success()
                            success_count += 1
                        else:
                            self.progress_tracker.mark_error("Failed to add to Excel")
                    else:
                        self.progress_tracker.mark_error("Analysis failed")
                        
                except Exception as e:
                    self.progress_tracker.mark_error(f"Exception: {str(e)}")
                
                if live_display:
                    self.progress_tracker.update_display(live_display)
            
            # Stop live display
            if live_display:
                live_display.stop()
            
            # Finalize Excel
            self.excel_generator.finalize_excel()
            
            # Print summary
            self.progress_tracker.print_final_summary()
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error analyzing file: {e}")
            return False
    
    def analyze_all_files(self, use_rich_display: bool = True) -> bool:
        """Analyze all files in input folder"""
        input_files = self._find_input_files()
        
        if not input_files:
            print("❌ No input files found!")
            return False
        
        success = True
        for file_path in input_files:
            if not self.analyze_file(file_path, use_rich_display):
                success = False
        
        return success
    
    def list_available_models(self):
        """List available Ollama models"""
        print("🤖 Available Ollama models:")
        models = self.analyzer.get_available_models()
        
        if models:
            for model in models:
                current = " (current)" if model == self.config['ollama']['model'] else ""
                print(f"   • {model}{current}")
        else:
            print("   No models found or Ollama not running")
    
    def get_status(self):
        """Get current system status"""
        print("📊 System Status:")
        print(f"   Ollama Model: {self.config['ollama']['model']}")
        print(f"   Input Folder: {self.config['input']['folder']}")
        print(f"   Output Folder: {self.config['output']['folder']}")
        
        # Check Ollama
        if self.analyzer.test_connection():
            print("   Ollama Status: ✅ Connected")
        else:
            print("   Ollama Status: ❌ Not connected")
        
        # Check input files
        input_files = self._find_input_files()
        print(f"   Input Files: {len(input_files)} found")
        
        # Check output files
        output_folder = self.config['output']['folder']
        if os.path.exists(output_folder):
            output_files = [f for f in os.listdir(output_folder) if f.endswith('.xlsx')]
            print(f"   Output Files: {len(output_files)} Excel files")
        else:
            print("   Output Files: Output folder not created yet")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='UPSC Question Quality Analyzer')
    parser.add_argument('--config', '-c', default='config/config.json',
                       help='Configuration file path')
    parser.add_argument('--file', '-f', help='Analyze specific file')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable rich display (use simple text output)')
    parser.add_argument('--models', action='store_true',
                       help='List available Ollama models')
    parser.add_argument('--status', action='store_true',
                       help='Show system status')
    
    args = parser.parse_args()
    
    # Change to project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        analyzer = UPSCAnalyzer(args.config)
        
        if args.models:
            analyzer.list_available_models()
            return
        
        if args.status:
            analyzer.get_status()
            return
        
        # Check prerequisites
        if not analyzer.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
            sys.exit(1)
        
        print("\n🚀 Starting UPSC Question Analysis...")
        
        # Analyze files
        use_rich = not args.no_display
        
        if args.file:
            # Analyze specific file
            file_path = args.file
            if not os.path.exists(file_path):
                file_path = os.path.join(analyzer.config['input']['folder'], args.file)
            
            if os.path.exists(file_path):
                success = analyzer.analyze_file(file_path, use_rich)
            else:
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
        else:
            # Analyze all files
            success = analyzer.analyze_all_files(use_rich)
        
        if success:
            print("\n🎉 Analysis completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Analysis completed with errors.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()