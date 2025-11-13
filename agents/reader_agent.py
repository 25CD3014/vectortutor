"""
Reader Agent
Extracts and structures PDF content using Groq API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import GroqClient
from utils.memory import KnowledgeMemory
from utils.pdf_utils import extract_text_from_pdf, extract_pdf_metadata
from typing import Dict, Optional


class ReaderAgent:
    def __init__(self, groq_client: GroqClient, memory: KnowledgeMemory):
        """Initialize Reader Agent"""
        self.groq = groq_client
        self.memory = memory
    
    def process_pdf(self, pdf_path: str, filename: str) -> Dict:
        """
        Process a PDF file: extract text, structure it, and store in memory
        
        Args:
            pdf_path: Path to PDF file
            filename: Original filename
            
        Returns:
            Dictionary with document ID and processing results
        """
        # Extract raw text and metadata
        raw_text = extract_text_from_pdf(pdf_path)
        metadata = extract_pdf_metadata(pdf_path)
        
        # Structure the content using Groq
        structured_content = self._structure_content(raw_text)
        
        # Store in memory
        doc_id = self.memory.add_document(
            filename=filename,
            content=raw_text,
            metadata={**metadata, **structured_content}
        )
        
        return {
            "document_id": doc_id,
            "filename": filename,
            "metadata": metadata,
            "structured_content": structured_content,
            "text_length": len(raw_text)
        }
    
    def _structure_content(self, text: str) -> Dict:
        """
        Use Groq to structure and summarize PDF content
        
        Args:
            text: Raw extracted text from PDF
            
        Returns:
            Structured content dictionary
        """
        # Truncate text if too long (keep first 15000 chars for processing)
        truncated_text = text[:15000] if len(text) > 15000 else text
        
        system_prompt = """You are a content structuring assistant. Analyze the provided text and extract:
1. Main topics/themes
2. Key concepts
3. Important definitions
4. Summary of content

Respond with a structured analysis."""
        
        prompt = f"""Analyze and structure the following text from a PDF document:

{truncated_text}

Provide a structured analysis including:
- Main topics (list of 3-5 main topics)
- Key concepts (list of important concepts)
- Important definitions (if any)
- Brief summary (2-3 sentences)

Format your response clearly with headings."""
        
        try:
            structured_analysis = self.groq.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2000
            )
            
            # Extract topics using another call
            topics = self._extract_topics(text[:10000])
            
            return {
                "structured_analysis": structured_analysis,
                "topics": topics,
                "word_count": len(text.split())
            }
        except Exception as e:
            return {
                "error": str(e),
                "word_count": len(text.split())
            }
    
    def _extract_topics(self, text: str) -> list:
        """Extract main topics from text"""
        prompt = f"""Extract the main topics from this text. Return only a comma-separated list of 3-5 main topics:

{text[:5000]}"""
        
        try:
            response = self.groq.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=200
            )
            # Parse topics from response
            topics = [t.strip() for t in response.replace("\n", ",").split(",") if t.strip()]
            return topics[:5]  # Limit to 5 topics
        except:
            return []

