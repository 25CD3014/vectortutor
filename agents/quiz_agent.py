"""
Quiz Agent
Creates adaptive MCQs (easy/medium/hard) from PDF content using Groq API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import GroqClient
from utils.memory import KnowledgeMemory
from typing import List, Dict, Optional


class QuizAgent:
    def __init__(self, groq_client: GroqClient, memory: KnowledgeMemory):
        """Initialize Quiz Agent"""
        self.groq = groq_client
        self.memory = memory
    
    def generate_quiz(self, document_id: int, num_questions: int = 10,
                     difficulty: Optional[str] = None, topic: Optional[str] = None) -> List[Dict]:
        """
        Generate quiz questions from a document
        
        Args:
            document_id: ID of the document in memory
            num_questions: Number of questions to generate
            difficulty: Optional difficulty level (easy/medium/hard)
            topic: Optional topic to focus on
            
        Returns:
            List of generated quiz questions
        """
        # Get document content
        document = self.memory.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        content = document["content"]
        content_chunk = content[:12000] if len(content) > 12000 else content
        
        # Generate quiz questions
        if difficulty:
            questions = self._generate_by_difficulty(content_chunk, num_questions, difficulty, topic)
        else:
            # Generate mix of difficulties
            easy_count = num_questions // 3
            medium_count = num_questions // 3
            hard_count = num_questions - easy_count - medium_count
            
            questions = []
            if easy_count > 0:
                questions.extend(self._generate_by_difficulty(content_chunk, easy_count, "easy", topic))
            if medium_count > 0:
                questions.extend(self._generate_by_difficulty(content_chunk, medium_count, "medium", topic))
            if hard_count > 0:
                questions.extend(self._generate_by_difficulty(content_chunk, hard_count, "hard", topic))
        
        # Store questions in memory
        stored_questions = []
        for q in questions[:num_questions]:
            quiz_id = self.memory.add_quiz(
                document_id=document_id,
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                difficulty=q["difficulty"],
                topic=q.get("topic")
            )
            stored_questions.append({
                "id": quiz_id,
                **q
            })
        
        return stored_questions
    
    def _generate_by_difficulty(self, content: str, count: int, 
                                   difficulty: str, topic: Optional[str] = None) -> List[Dict]:
        """Generate quiz questions of a specific difficulty"""
        system_prompt = f"""You are a quiz generation expert. Create {difficulty} level multiple-choice questions that test understanding of the material.
{difficulty.upper()} level questions should:
- {"Test basic recall and understanding" if difficulty == "easy" else "Test application and analysis" if difficulty == "medium" else "Test synthesis, evaluation, and deep understanding"}
- Have 4 options (A, B, C, D)
- Have one clearly correct answer
- Have plausible distractors (wrong answers)
- Be clear and unambiguous"""
        
        topic_filter = f"Focus on the topic: {topic}. " if topic else ""
        
        prompt = f"""Generate {count} {difficulty} level multiple-choice questions from this content:

{content}

{topic_filter}Create questions with:
- Clear question text
- 4 options labeled A, B, C, D
- One correct answer (specify which option: 0=A, 1=B, 2=C, 3=D)
- Appropriate difficulty level: {difficulty}
- Relevant topic

Return in this JSON format:
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "difficulty": "{difficulty}",
            "topic": "Topic name"
        }}
    ]
}}"""
        
        try:
            response = self.groq.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            questions = response.get("questions", [])
            
            # Validate and fix questions
            validated_questions = []
            for q in questions:
                if self._validate_question(q):
                    validated_questions.append(q)
            
            # Generate more if needed
            if len(validated_questions) < count:
                additional = self._generate_additional(content, count - len(validated_questions), difficulty, topic)
                validated_questions.extend(additional)
            
            return validated_questions[:count]
        except Exception as e:
            # Fallback generation
            return self._generate_simple_questions(content, count, difficulty)
    
    def _validate_question(self, question: Dict) -> bool:
        """Validate a question has all required fields"""
        required = ["question", "options", "correct_answer", "difficulty"]
        if not all(key in question for key in required):
            return False
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            return False
        if question["correct_answer"] not in [0, 1, 2, 3]:
            return False
        return True
    
    def _generate_additional(self, content: str, count: int, difficulty: str, 
                           topic: Optional[str] = None) -> List[Dict]:
        """Generate additional questions"""
        prompt = f"""Generate {count} more {difficulty} level questions from:

{content[:8000]}

Make them unique and different from previous questions."""
        
        try:
            response = self.groq.generate_json(prompt=prompt, temperature=0.7)
            questions = response.get("questions", [])
            return [q for q in questions if self._validate_question(q)]
        except:
            return []
    
    def _generate_simple_questions(self, content: str, count: int, difficulty: str) -> List[Dict]:
        """Fallback: generate simple questions"""
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 30]
        questions = []
        
        for i, sentence in enumerate(sentences[:count]):
            question = f"Which statement is true about: {sentence[:60]}...?"
            options = [
                sentence[:100],
                "This is not mentioned in the text.",
                "The opposite is true.",
                "None of the above."
            ]
            questions.append({
                "question": question,
                "options": options,
                "correct_answer": 0,
                "difficulty": difficulty,
                "topic": "General"
            })
        
        return questions
    
    def get_quizzes(self, document_id: Optional[int] = None, 
                   difficulty: Optional[str] = None) -> List[Dict]:
        """Retrieve quiz questions from memory"""
        return self.memory.get_quizzes(document_id, difficulty)
    
    def submit_answer(self, quiz_id: int, user_answer: int) -> bool:
        """Submit an answer and record the attempt"""
        quizzes = self.memory.get_quizzes()
        quiz = next((q for q in quizzes if q["id"] == quiz_id), None)
        
        if not quiz:
            return False
        
        is_correct = (user_answer == quiz["correct_answer"])
        self.memory.record_quiz_attempt(quiz_id, user_answer, is_correct)
        return is_correct

