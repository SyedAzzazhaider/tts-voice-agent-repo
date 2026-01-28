"""
Module 4: Language Detection (Team Member Version - Simplified)
"""

from dataclasses import dataclass
from typing import Optional
from langdetect import detect
from loguru import logger

URDU_RANGE = range(0x0600, 0x06FF)

@dataclass
class LanguageDetectionResult:
    """Language detection result"""
    success: bool
    language: str
    confidence: float
    method: str
    error: Optional[str] = None

def is_urdu_unicode(text):
    """Check if >30% of chars are Urdu"""
    urdu_chars = sum(1 for c in text if ord(c) in URDU_RANGE)
    return urdu_chars / max(len(text), 1) > 0.3

def detect_language(text: str) -> LanguageDetectionResult:
    """
    Detect language: 'ur' or 'en'
    
    Returns:
        LanguageDetectionResult with language code
    """
    try:
        if is_urdu_unicode(text):
            logger.info("Detected Urdu via Unicode")
            return LanguageDetectionResult(
                success=True,
                language="ur",
                confidence=90.0,
                method="unicode"
            )
        
        lang = detect(text)
        detected = "ur" if lang == "ur" else "en"
        logger.info(f"Detected {detected} via library")
        
        return LanguageDetectionResult(
            success=True,
            language=detected,
            confidence=85.0,
            method="library"
        )
    
    except Exception as e:
        logger.warning(f"Detection failed, defaulting to English: {e}")
        return LanguageDetectionResult(
            success=True,
            language="en",
            confidence=50.0,
            method="fallback"
        )

def quick_detect(text: str) -> str:
    """Quick detection - returns just language code"""
    result = detect_language(text)
    return result.language