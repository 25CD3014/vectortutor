"""
Flashcard Agent
Generates Q&A flashcards from PDF content using Groq API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import GroqClient
from utils.memory import KnowledgeMemory
from typing import List, Dict, Optional


class FlashcardAgent:
    def __init__(self, groq_client: GroqClient, memory: KnowledgeMemory):
        """Initialize Flashcard Agent"""
        self.groq = groq_client
        self.memory = memory
    
    def generate_flashcards(self, document_id: int, num_flashcards: int = 10, 
                           topic: Optional[str] = None) -> List[Dict]:
        """
        Generate flashcards from a document
        
        Args:
            document_id: ID of the document in memory
            num_flashcards: Number of flashcards to generate
            topic: Optional topic to focus on
            
        Returns:
            List of generated flashcards
        """
        # Get document content
        document = self.memory.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        content = document["content"]
        # Use first 12000 chars for processing
        content_chunk = content[:12000] if len(content) > 12000 else content
        
        # Generate flashcards using Groq
        flashcards_data = self._generate_with_groq(content_chunk, num_flashcards, topic)
        
        # Store flashcards in memory
        stored_flashcards = []
        for fc in flashcards_data:
            flashcard_id = self.memory.add_flashcard(
                document_id=document_id,
                question=fc["question"],
                answer=fc["answer"],
                topic=fc.get("topic"),
                difficulty=fc.get("difficulty", "medium")
            )
            stored_flashcards.append({
                "id": flashcard_id,
                **fc
            })
        
        return stored_flashcards
    
    def _generate_with_groq(self, content: str, num_flashcards: int, 
                           topic: Optional[str] = None) -> List[Dict]:
        """Generate flashcards using Groq API"""
        system_prompt = """You are a flashcard generation expert. Create clear, concise question-answer pairs that help students learn effectively. 
Each flashcard should:
- Have a clear, specific question
- Have a comprehensive but concise answer
- Cover important concepts from the material
- Be suitable for active recall practice"""
        
        topic_filter = f"Focus on the topic: {topic}. " if topic else ""
        
        prompt = f"""Generate {num_flashcards} flashcards from the following content:

{content}

{topic_filter}Create flashcards with:
- Clear, specific questions
- Comprehensive but concise answers
- Relevant topics
- Appropriate difficulty level (easy/medium/hard)

Return the flashcards in this JSON format:
{{
    "flashcards": [
        {{
            "question": "Question text here",
            "answer": "Answer text here",
            "topic": "Topic name",
            "difficulty": "medium"
        }}
    ]
}}"""
        
        try:
            response = self.groq.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            flashcards = response.get("flashcards", [])
            
            # Ensure we have the right number
            if len(flashcards) < num_flashcards:
                # Generate more if needed
                additional = num_flashcards - len(flashcards)
                more_flashcards = self._generate_additional(content, additional, topic)
                flashcards.extend(more_flashcards)
            
            return flashcards[:num_flashcards]
        except Exception as e:
            # Fallback: generate simple flashcards
            return self._generate_simple_flashcards(content, num_flashcards)
    
    def _generate_additional(self, content: str, count: int, topic: Optional[str] = None) -> List[Dict]:
        """Generate additional flashcards"""
        prompt = f"""Generate {count} more flashcards from this content:

{content[:8000]}

Create unique flashcards different from previous ones."""
        
        try:
            response = self.groq.generate_json(
                prompt=prompt,
                temperature=0.7
            )
            return response.get("flashcards", [])
        except:
            return []
    
    def _generate_simple_flashcards(self, content: str, num_flashcards: int) -> List[Dict]:
        """Fallback method to generate simple flashcards"""
        # Split content into sentences and create basic Q&A pairs
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        flashcards = []
        
        for i, sentence in enumerate(sentences[:num_flashcards]):
            # Create a simple question-answer pair
            question = f"What is mentioned about: {sentence[:50]}...?"
            answer = sentence[:200]
            flashcards.append({
                "question": question,
                "answer": answer,
                "topic": "General",
                "difficulty": "medium"
            })
        
        return flashcards
    
    def get_flashcards(self, document_id: Optional[int] = None) -> List[Dict]:
        """Retrieve flashcards from memory"""
        return self.memory.get_flashcards(document_id)

