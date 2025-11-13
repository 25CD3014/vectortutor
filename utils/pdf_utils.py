"""
PDF Utilities
Handles PDF text extraction using PyMuPDF (fitz)
"""
import fitz  # PyMuPDF
from typing import Dict, List


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def extract_pdf_metadata(pdf_path: str) -> Dict:
    """
    Extract metadata from PDF
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Dictionary with PDF metadata
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        page_count = len(doc)
        doc.close()
        
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "page_count": page_count
        }
    except Exception as e:
        return {"error": str(e)}


def extract_text_by_pages(pdf_path: str, max_chars: int = 10000) -> List[Dict]:
    """
    Extract text from PDF split by pages (useful for chunking)
    
    Args:
        pdf_path: Path to PDF file
        max_chars: Maximum characters per chunk
        
    Returns:
        List of dictionaries with page number and text
    """
    try:
        doc = fitz.open(pdf_path)
        chunks = []
        current_chunk = ""
        current_page = 1
        
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            
            if len(current_chunk) + len(page_text) <= max_chars:
                current_chunk += page_text + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        "page": current_page,
                        "text": current_chunk.strip()
                    })
                current_chunk = page_text
                current_page = page_num
        
        if current_chunk:
            chunks.append({
                "page": current_page,
                "text": current_chunk.strip()
            })
        
        doc.close()
        return chunks
    except Exception as e:
        raise Exception(f"Error extracting PDF chunks: {str(e)}")

