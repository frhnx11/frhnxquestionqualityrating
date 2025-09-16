import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Question:
    subject: str
    topic: str
    subtopic: str
    question_number: int
    question_text: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuestionParser:
    def __init__(self):
        self.question_separator = "=" * 60
        self.question_pattern = r'\*\*QUESTION\s+(\d+)\*\*'
        self.question_text_pattern = r'\*\*Q:\*\*(.*?)(?=\s+A\.|$)'
        self.options_pattern = r'([A-D])\.\s*([^\n]+)'
        self.answer_pattern = r'\*\*Correct Answer:\*\*\s*([A-D])\.\s*([^\n]+)'
        self.explanation_pattern = r'\*\*Explanation:\*\*(.*?)(?=\n\n|\Z)'

    def parse_file(self, file_path: str) -> List[Question]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)

    def parse_content(self, content: str) -> List[Question]:
        # Extract header information (Subject, Topic, Subtopic)
        header_info = self._extract_header_info(content)
        
        # Split content by question separators
        question_blocks = self._split_into_question_blocks(content)
        
        questions = []
        for block in question_blocks:
            question = self._parse_question_block(block, header_info)
            if question:
                questions.append(question)
        
        return questions

    def _extract_header_info(self, content: str) -> Dict[str, str]:
        lines = content.split('\n')
        header_info = {'subject': '', 'topic': '', 'subtopic': ''}
        
        for line in lines[:10]:  # Check first 10 lines for header
            line = line.strip()
            if line.startswith('Subject:'):
                header_info['subject'] = line.replace('Subject:', '').strip()
            elif line.startswith('Topic:'):
                header_info['topic'] = line.replace('Topic:', '').strip()
            elif line.startswith('Subtopic:'):
                header_info['subtopic'] = line.replace('Subtopic:', '').strip()
                break
        
        return header_info

    def _split_into_question_blocks(self, content: str) -> List[str]:
        # Split by separator and filter out empty blocks
        blocks = content.split(self.question_separator)
        question_blocks = []
        
        for block in blocks:
            block = block.strip()
            if block and '**QUESTION' in block:
                question_blocks.append(block)
        
        return question_blocks

    def _parse_question_block(self, block: str, header_info: Dict[str, str]) -> Optional[Question]:
        try:
            # Extract question number
            question_match = re.search(self.question_pattern, block)
            if not question_match:
                return None
            
            question_number = int(question_match.group(1))
            
            # Extract question text
            question_text = self._extract_question_text(block)
            if not question_text:
                return None
            
            # Extract options
            options = self._extract_options(block)
            if len(options) != 4:
                return None
            
            # Extract correct answer and explanation
            answer_info = self._extract_answer_and_explanation(block)
            if not answer_info:
                return None
            
            correct_answer, explanation = answer_info
            
            return Question(
                subject=header_info.get('subject', ''),
                topic=header_info.get('topic', ''),
                subtopic=header_info.get('subtopic', ''),
                question_number=question_number,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation
            )
            
        except Exception as e:
            print(f"Error parsing question block: {e}")
            return None

    def _extract_question_text(self, block: str) -> str:
        # Find text between **Q:** and the first option
        lines = block.split('\n')
        question_lines = []
        in_question = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('**Q:**'):
                question_lines.append(line.replace('**Q:**', '').strip())
                in_question = True
            elif in_question and re.match(r'^\s*[A-D]\.', line):
                break
            elif in_question and line:
                question_lines.append(line)
        
        return ' '.join(question_lines).strip()

    def _extract_options(self, block: str) -> List[str]:
        options = []
        lines = block.split('\n')
        
        for line in lines:
            line = line.strip()
            match = re.match(r'^([A-D])\.\s*(.*)', line)
            if match:
                option_letter, option_text = match.groups()
                options.append(f"{option_letter}. {option_text}")
        
        return options

    def _extract_answer_and_explanation(self, block: str) -> Optional[tuple]:
        # Extract correct answer
        answer_match = re.search(r'\*\*Correct Answer:\*\*\s*([A-D])\.\s*([^\n]+)', block)
        if not answer_match:
            return None
        
        correct_answer = f"{answer_match.group(1)}. {answer_match.group(2)}"
        
        # Extract explanation
        explanation_match = re.search(r'\*\*Explanation:\*\*(.*?)(?=\n\n|\Z)', block, re.DOTALL)
        if not explanation_match:
            return None
        
        explanation = explanation_match.group(1).strip()
        
        return correct_answer, explanation

    def format_question_for_analysis(self, question: Question) -> str:
        """Format question for sending to Ollama"""
        formatted = f"""Subject: {question.subject}
Topic: {question.topic}
Subtopic: {question.subtopic}

Question {question.question_number}: {question.question_text}

Options:
{chr(10).join(question.options)}

Correct Answer: {question.correct_answer}

Explanation: {question.explanation}"""
        
        return formatted