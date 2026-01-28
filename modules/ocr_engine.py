# """
# OCR Engine - Extract text from images using EasyOCR and Tesseract
# Supports English and Urdu with automatic language detection
# """

# from typing import Optional
# from dataclasses import dataclass
# from pathlib import Path
# import io

# import easyocr
# import pytesseract
# from PIL import Image
# import cv2
# import numpy as np
# from loguru import logger


# @dataclass
# class OCRResult:
#     """OCR extraction result"""
#     success: bool
#     text: str
#     confidence: float
#     language: str = 'mixed'
#     error: Optional[str] = None


# class OCREngine:
#     """OCR Engine with EasyOCR (primary) and Tesseract (fallback)"""

#     SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
#     MAX_SIZE_MB = 10

#     def __init__(self, use_easyocr: bool = True):
#         """
#         Initialize OCR Engine

#         Args:
#             use_easyocr: Use EasyOCR (better for Urdu), fallback to Tesseract
#         """
#         self.use_easyocr = use_easyocr
#         self.reader = None

#         if use_easyocr:
#             try:
#                 self.reader = easyocr.Reader(['en', 'ur'], gpu=False)
#                 logger.info("✅ EasyOCR initialized (en, ur)")
#             except Exception as e:
#                 logger.warning(f"EasyOCR init failed, using Tesseract: {e}")
#                 self.use_easyocr = False

#         if not self.use_easyocr:
#             self._verify_tesseract()

#     def extract(self, image_path: str, language: str = 'mixed') -> OCRResult:
#         """Extract text from image file"""
#         try:
#             path = Path(image_path)

#             # Validate
#             if not path.exists():
#                 return self._error(f"File not found: {path}")
#             if path.suffix.lower() not in self.SUPPORTED_FORMATS:
#                 return self._error(f"Unsupported format: {path.suffix}")
#             if path.stat().st_size > self.MAX_SIZE_MB * 1024 * 1024:
#                 return self._error("File too large (max 10MB)")

#             # Load and preprocess
#             image = Image.open(path)
#             image = self._preprocess(image)

#             # Extract
#             if self.use_easyocr and self.reader:
#                 return self._extract_easyocr(image)
#             else:
#                 return self._extract_tesseract(image, language)

#         except Exception as e:
#             return self._error(f"OCR failed: {e}")

#     def extract_from_bytes(self, image_bytes: bytes, language: str = 'mixed') -> OCRResult:
#         """Extract text from image bytes"""
#         try:
#             image = Image.open(io.BytesIO(image_bytes))
#             image = self._preprocess(image)

#             if self.use_easyocr and self.reader:
#                 return self._extract_easyocr(image)
#             else:
#                 return self._extract_tesseract(image, language)

#         except Exception as e:
#             return self._error(f"OCR failed: {e}")

#     def _extract_easyocr(self, image: Image.Image) -> OCRResult:
#         """Extract using EasyOCR"""
#         img_array = np.array(image)
#         results = self.reader.readtext(img_array, detail=1)

#         if not results:
#             return self._error("No text detected")

#         text = ' '.join([item[1] for item in results])
#         confidence = sum([item[2] for item in results]) / len(results) * 100

#         return OCRResult(
#             success=True,
#             text=text.strip(),
#             confidence=round(confidence, 1)
#         )

#     def _extract_tesseract(self, image: Image.Image, language: str) -> OCRResult:
#         """Extract using Tesseract"""
#         lang_map = {'en': 'eng', 'ur': 'urd', 'mixed': 'eng+urd'}
#         lang_code = lang_map.get(language, 'eng+urd')

#         configs = ['--psm 3', '--psm 6', '--psm 11']

#         for config in configs:
#             text = pytesseract.image_to_string(
#                 image, lang=lang_code, config=config
#             )
#             if text.strip():
#                 data = pytesseract.image_to_data(
#                     image,
#                     lang=lang_code,
#                     output_type=pytesseract.Output.DICT
#                 )
#                 confidences = [
#                     int(c) for c in data['conf'] if int(c) > 0
#                 ]
#                 avg_conf = (
#                     sum(confidences) / len(confidences)
#                     if confidences else 0
#                 )

#                 return OCRResult(
#                     success=True,
#                     text=text.strip(),
#                     confidence=round(avg_conf, 1),
#                     language=language
#                 )

#         return self._error("No text detected")

#     def _preprocess(self, image: Image.Image) -> Image.Image:
#         """Preprocess image for better OCR"""
#         try:
#             img_cv = cv2.cvtColor(
#                 np.array(image), cv2.COLOR_RGB2BGR
#             )
#             gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

#             thresh = cv2.adaptiveThreshold(
#                 gray, 255,
#                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                 cv2.THRESH_BINARY,
#                 11, 2
#             )

#             denoised = cv2.fastNlMeansDenoising(
#                 thresh, None, 10, 7, 21
#             )

#             return Image.fromarray(denoised)
#         except Exception:
#             return image

#     def _verify_tesseract(self):
#         """Verify Tesseract installation"""
#         try:
#             pytesseract.get_tesseract_version()
#             logger.info("✅ Tesseract OCR found")
#         except Exception:
#             logger.error("❌ Tesseract not installed")

#     def _error(self, message: str) -> OCRResult:
#         """Create error result"""
#         logger.warning(f"OCR error: {message}")
#         return OCRResult(
#             success=False,
#             text="",
#             confidence=0.0,
#             error=message
#         )


# # Quick function
# def extract_text_from_image(image_path: str, language: str = 'mixed') -> OCRResult:
#     """Quick OCR extraction"""
#     engine = OCREngine()
#     return engine.extract(image_path, language)



"""
OCR Engine - Extract text from images using EasyOCR and Tesseract
Supports English and Urdu with automatic language detection
"""

from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import io

import easyocr
import pytesseract
from PIL import Image
import cv2
import numpy as np
from loguru import logger


@dataclass
class OCRResult:
    """OCR extraction result"""
    success: bool
    text: str
    confidence: float
    char_count: int = 0  # ADDED
    language: str = 'mixed'
    error: Optional[str] = None


class OCREngine:
    """OCR Engine with EasyOCR (primary) and Tesseract (fallback)"""

    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    MAX_SIZE_MB = 10

    def __init__(self, use_easyocr: bool = True):
        """
        Initialize OCR Engine

        Args:
            use_easyocr: Use EasyOCR (better for Urdu), fallback to Tesseract
        """
        self.use_easyocr = use_easyocr
        self.reader = None

        if use_easyocr:
            try:
                self.reader = easyocr.Reader(['en', 'ur'], gpu=False)
                logger.info("✅ EasyOCR initialized (en, ur)")
            except Exception as e:
                logger.warning(f"EasyOCR init failed, using Tesseract: {e}")
                self.use_easyocr = False

        if not self.use_easyocr:
            self._verify_tesseract()

    def extract(self, image_path: str, language: str = 'mixed') -> OCRResult:
        """Extract text from image file"""
        try:
            path = Path(image_path)

            # Validate
            if not path.exists():
                return self._error(f"File not found: {path}")
            if path.suffix.lower() not in self.SUPPORTED_FORMATS:
                return self._error(f"Unsupported format: {path.suffix}")
            if path.stat().st_size > self.MAX_SIZE_MB * 1024 * 1024:
                return self._error("File too large (max 10MB)")

            # Load and preprocess
            image = Image.open(path)
            image = self._preprocess(image)

            # Extract
            if self.use_easyocr and self.reader:
                return self._extract_easyocr(image)
            else:
                return self._extract_tesseract(image, language)

        except Exception as e:
            return self._error(f"OCR failed: {e}")

    def extract_from_bytes(self, image_bytes: bytes, language: str = 'mixed') -> OCRResult:
        """Extract text from image bytes"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = self._preprocess(image)

            if self.use_easyocr and self.reader:
                return self._extract_easyocr(image)
            else:
                return self._extract_tesseract(image, language)

        except Exception as e:
            return self._error(f"OCR failed: {e}")

    def _extract_easyocr(self, image: Image.Image) -> OCRResult:
        """Extract using EasyOCR"""
        img_array = np.array(image)
        results = self.reader.readtext(img_array, detail=1)

        if not results:
            return self._error("No text detected")

        text = ' '.join([item[1] for item in results])
        confidence = sum([item[2] for item in results]) / len(results) * 100

        return OCRResult(
            success=True,
            text=text.strip(),
            confidence=round(confidence, 1),
            char_count=len(text.strip())  # ADDED
        )

    def _extract_tesseract(self, image: Image.Image, language: str) -> OCRResult:
        """Extract using Tesseract"""
        lang_map = {'en': 'eng', 'ur': 'urd', 'mixed': 'eng+urd'}
        lang_code = lang_map.get(language, 'eng+urd')

        configs = ['--psm 3', '--psm 6', '--psm 11']

        for config in configs:
            text = pytesseract.image_to_string(
                image, lang=lang_code, config=config
            )
            if text.strip():
                data = pytesseract.image_to_data(
                    image,
                    lang=lang_code,
                    output_type=pytesseract.Output.DICT
                )
                confidences = [
                    int(c) for c in data['conf'] if int(c) > 0
                ]
                avg_conf = (
                    sum(confidences) / len(confidences)
                    if confidences else 0
                )

                return OCRResult(
                    success=True,
                    text=text.strip(),
                    confidence=round(avg_conf, 1),
                    char_count=len(text.strip()),  # ADDED
                    language=language
                )

        return self._error("No text detected")

    def _preprocess(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR"""
        try:
            img_cv = cv2.cvtColor(
                np.array(image), cv2.COLOR_RGB2BGR
            )
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )

            denoised = cv2.fastNlMeansDenoising(
                thresh, None, 10, 7, 21
            )

            return Image.fromarray(denoised)
        except Exception:
            return image

    def _verify_tesseract(self):
        """Verify Tesseract installation"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("✅ Tesseract OCR found")
        except Exception:
            logger.error("❌ Tesseract not installed")

    def _error(self, message: str) -> OCRResult:
        """Create error result"""
        logger.warning(f"OCR error: {message}")
        return OCRResult(
            success=False,
            text="",
            confidence=0.0,
            char_count=0,  # ADDED
            error=message
        )


# Quick function
def extract_text_from_image(image_path: str, language: str = 'mixed') -> OCRResult:
    """Quick OCR extraction"""
    engine = OCREngine()
    return engine.extract(image_path, language)
