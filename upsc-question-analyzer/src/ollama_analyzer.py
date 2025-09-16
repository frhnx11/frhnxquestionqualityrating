import ollama
import json
import time
import re
import os
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    subject: str
    topic: str
    subtopic: str
    question_complete: str
    answer_explanation: str
    rating: int
    conceptual_depth: str
    answer_accuracy: str
    topic_relevance: str
    improved_version: str

class OllamaAnalyzer:
    def __init__(self, config: Dict):
        # Ollama configuration
        self.model = config['ollama']['model']
        self.base_url = config['ollama']['base_url']
        self.timeout = config['ollama']['timeout']
            
        self.max_retries = config['analysis']['max_retries']
        self.retry_delay = config['analysis']['retry_delay']
        
        # Load system prompt
        # Get the correct path for bundled or development environment
        if getattr(sys, 'frozen', False):
            # Running as bundled executable
            prompt_path = os.path.join(sys._MEIPASS, 'config', 'system_prompt_enhanced.txt')
        else:
            # Running in development
            prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'system_prompt_enhanced.txt')
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()
    
    def analyze_question(self, question_text: str) -> Optional[AnalysisResult]:
        """Analyze a single question using Ollama"""
        for attempt in range(self.max_retries):
            try:
                # Create the analysis prompt
                analysis_prompt = f"""
{self.system_prompt}

Now analyze this question:

{question_text}

Please provide your analysis in the exact table format specified above. Make sure to fill ALL columns completely.
"""
                
                # Send to Ollama
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {
                            'role': 'user',
                            'content': analysis_prompt
                        }
                    ],
                    options={'temperature': 0.1}
                )
                analysis_text = response['message']['content']
                result = self._parse_analysis_response(analysis_text, question_text)
                
                if result:
                    return result
                else:
                    print(f"Failed to parse analysis response (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                
            except Exception as e:
                print(f"Error analyzing question (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        return None
    
    def _parse_analysis_response(self, response_text: str, original_question: str) -> Optional[AnalysisResult]:
        """Parse the AI response into structured data"""
        try:
            # Look for table format in response
            lines = response_text.split('\n')
            
            # Find the table data row (skip headers)
            data_row = None
            for line in lines:
                if '|' in line and not line.strip().startswith('|---') and 'Subject' not in line:
                    # This might be our data row
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last
                    if len(cells) >= 9:  # We need at least 9 columns
                        data_row = cells
                        break
            
            if not data_row:
                # Try alternative parsing approach
                return self._parse_fallback_format(response_text, original_question)
            
            # Extract data from table row
            try:
                rating = int(re.search(r'(\d+)', data_row[5]).group(1)) if re.search(r'(\d+)', data_row[5]) else 0
            except:
                rating = 0
            
            return AnalysisResult(
                subject=data_row[0][:100],  # Limit length
                topic=data_row[1][:100],
                subtopic=data_row[2][:100],
                question_complete=data_row[3][:2000],  # Complete question text
                answer_explanation=data_row[4][:2000],  # Complete answer and explanation
                rating=rating,
                conceptual_depth=data_row[6][:500],
                answer_accuracy=data_row[7][:500],
                topic_relevance=data_row[8][:500],
                improved_version=data_row[9][:2000] if len(data_row) > 9 else "N/A"
            )
            
        except Exception as e:
            print(f"Error parsing table format: {e}")
            return self._parse_fallback_format(response_text, original_question)
    
    def _parse_fallback_format(self, response_text: str, original_question: str) -> Optional[AnalysisResult]:
        """Fallback parsing when table format fails"""
        try:
            # Extract key information using regex patterns
            patterns = {
                'subject': r'Subject:?\s*([^\n]+)',
                'topic': r'Topic:?\s*([^\n]+)',
                'subtopic': r'Subtopic:?\s*([^\n]+)',
                'rating': r'Rating.*?(\d+)',
                'conceptual_depth': r'Conceptual Depth:?\s*([^\n]+(?:\n[^A-Z\n][^\n]*)*)',
                'answer_accuracy': r'Answer Accuracy:?\s*([^\n]+(?:\n[^A-Z\n][^\n]*)*)',
                'topic_relevance': r'Topic.*?Relevance:?\s*([^\n]+(?:\n[^A-Z\n][^\n]*)*)'
            }
            
            extracted = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, response_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    extracted[key] = match.group(1).strip()
                else:
                    extracted[key] = "Not found"
            
            # Extract rating as integer
            try:
                rating = int(re.search(r'(\d+)', extracted.get('rating', '0')).group(1))
            except:
                rating = 0
            
            # Create basic analysis result
            return AnalysisResult(
                subject=extracted.get('subject', 'Unknown')[:100],
                topic=extracted.get('topic', 'Unknown')[:100],
                subtopic=extracted.get('subtopic', 'Unknown')[:100],
                question_complete=original_question[:2000],
                answer_explanation="Analysis response parsing incomplete"[:2000],
                rating=rating,
                conceptual_depth=extracted.get('conceptual_depth', 'Unable to parse')[:500],
                answer_accuracy=extracted.get('answer_accuracy', 'Unable to parse')[:500],
                topic_relevance=extracted.get('topic_relevance', 'Unable to parse')[:500],
                improved_version="N/A - Parsing incomplete"
            )
            
        except Exception as e:
            print(f"Fallback parsing failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if Ollama is accessible"""
        try:
            # Test Ollama connection
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': 'Test connection'}],
                options={'temperature': 0}
            )
            return True
        except Exception as e:
            print(f"Ollama connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            # Get Ollama models
            models = ollama.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error getting available models: {e}")
            return []