"""
Word Document Engine - Extract text from .docx files
"""

from typing import Optional
from dataclasses import dataclass
from pathlib import Path
from docx import Document
from loguru import logger


@dataclass
class DocxResult:
    """Word document extraction result"""
    success: bool
    text: str
    filename: str
    error: Optional[str] = None


def extract_text_from_docx(docx_path: str) -> DocxResult:
    """
    Extract text from Word document
    
    Args:
        docx_path: Path to .docx file
        
    Returns:
        DocxResult with extracted text
    """
    try:
        path = Path(docx_path)
        
        if not path.exists():
            return DocxResult(False, "", str(path), "File not found")
        
        if path.suffix.lower() != '.docx':
            return DocxResult(False, "", str(path), "Not a .docx file")
        
        # Extract text from all paragraphs
        doc = Document(path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
        
        if not text.strip():
            return DocxResult(False, "", str(path), "No text found in document")
        
        logger.info(f"✅ Extracted {len(text)} chars from {path.name}")
        
        return DocxResult(
            success=True,
            text=text.strip(),
            filename=str(path)
        )
    
    except Exception as e:
        logger.error(f"Word extraction failed: {e}")
        return DocxResult(False, "", str(docx_path), f"Error: {e}")