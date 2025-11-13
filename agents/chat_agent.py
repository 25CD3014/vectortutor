"""
Chat Agent
Answers doubts and questions from PDF context using Groq API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import GroqClient
from utils.memory import KnowledgeMemory
from typing import Optional, List, Dict


class ChatAgent:
    def __init__(self, groq_client: GroqClient, memory: KnowledgeMemory):
        """Initialize Chat Agent"""
        self.groq = groq_client
        self.memory = memory
    
    def answer_question(self, document_id: int, question: str, 
                       use_history: bool = True) -> Dict:
        """
        Answer a question based on document content
        
        Args:
            document_id: ID of the document
            question: User's question
            use_history: Whether to use chat history for context
            
        Returns:
            Dictionary with answer and metadata
        """
        # Get document content
        document = self.memory.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        content = document["content"]
        # Use relevant chunk (first 10000 chars, can be improved with better chunking)
        context = content[:10000] if len(content) > 10000 else content
        
        # Get chat history if requested
        history_context = ""
        if use_history:
            history = self.memory.get_chat_history(document_id, limit=5)
            if history:
                history_context = "\n\nPrevious Q&A:\n"
                for h in reversed(history[:3]):  # Last 3 Q&As
                    history_context += f"Q: {h['question']}\nA: {h['answer'][:200]}...\n\n"
        
        # Generate answer using Groq
        answer = self._generate_answer(context, question, history_context)
        
        # Store in chat history
        self.memory.add_chat_message(document_id, question, answer)
        
        return {
            "question": question,
            "answer": answer,
            "document_id": document_id,
            "source": "document_content"
        }
    
    def _generate_answer(self, context: str, question: str, 
                       history_context: str = "") -> str:
        """Generate answer using Groq API"""
        system_prompt = """You are a helpful tutor assistant for VectorTutor. Answer questions based on the provided document content.
- Be accurate and cite information from the document
- If the answer isn't in the document, say so clearly
- Provide clear, concise explanations
- Use examples when helpful
- Be encouraging and supportive"""
        
        prompt = f"""Based on the following document content, answer the user's question:

Document Content:
{context}

{history_context}

User Question: {question}

Provide a clear, accurate answer based on the document content. If the answer is not in the provided content, state that clearly."""
        
        try:
            answer = self.groq.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            return answer
        except Exception as e:
            return f"I encountered an error while generating an answer: {str(e)}. Please try rephrasing your question."
    
    def get_chat_history(self, document_id: Optional[int] = None, 
                        limit: int = 50) -> List[Dict]:
        """Retrieve chat history"""
        return self.memory.get_chat_history(document_id, limit)
    
    def summarize_notes(self, document_id: int, focus_topic: Optional[str] = None) -> str:
        """
        Generate a summary of notes from the document
        
        Args:
            document_id: ID of the document
            focus_topic: Optional topic to focus the summary on
            
        Returns:
            Summary text
        """
        document = self.memory.get_document(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        content = document["content"]
        content_chunk = content[:15000] if len(content) > 15000 else content
        
        system_prompt = """You are a note summarization expert. Create clear, organized summaries that:
- Highlight key concepts and main ideas
- Organize information logically
- Use bullet points and headings for clarity
- Include important definitions and examples
- Are concise but comprehensive"""
        
        topic_filter = f"Focus the summary on: {focus_topic}. " if focus_topic else ""
        
        prompt = f"""Create a comprehensive summary of the following notes:

{content_chunk}

{topic_filter}Organize the summary with:
- Main topics and headings
- Key concepts and definitions
- Important points and examples
- Clear structure for easy review"""
        
        try:
            summary = self.groq.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2000
            )
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}"

