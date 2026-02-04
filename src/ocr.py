"""
OCR Module for extracting text from circular labels using PaddleOCR.

Handles multi-line text extraction and merging for labels like "AV" + "C101" -> "AV C101"
Updated for PaddleOCR v3.4+ API with dict-like result objects.
"""

import os
import re

import cv2
import numpy as np
from paddleocr import PaddleOCR


class LabelOCR:
    """
    PaddleOCR-based text extractor for circular labels.
    
    Optimized for multi-line labels with text like "AV" on line 1 and "C101" on line 2.
    Uses PaddleOCR v3.4+ API.
    """
    
    def __init__(self, lang: str = "en", device: str = "cpu"):
        """
        Initialize the OCR engine.
        
        Args:
            lang: OCR language ('en', 'ch' for Chinese+English, etc.)
            device: Device to use ('cpu', 'gpu')
        """
        # Suppress PaddleOCR connectivity check
        os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
        
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang=lang,
            device=device,
        )
    
    def extract_text(
        self, 
        roi_image: np.ndarray,
        preprocess: bool = True
    ) -> str:
        """
        Extract text from a cropped label image (ROI).
        
        Args:
            roi_image: Cropped image of a single label
            preprocess: Whether to apply image preprocessing
        
        Returns:
            Merged text string from all detected text lines
        """
        if roi_image is None or roi_image.size == 0:
            return ""
        
        # Preprocess image if enabled
        if preprocess:
            roi_image = self._preprocess(roi_image)
        
        # Run OCR using v3.4 API
        try:
            results = self.ocr.predict(roi_image)
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
        
        # Extract text from results
        # V3.4 returns dict-like OCRResult objects
        texts = []
        if results:
            for res in results:
                # Access as dictionary keys
                rec_texts = res.get('rec_texts', [])
                dt_polys = res.get('dt_polys', [])
                
                if rec_texts:
                    # Get corresponding y-coordinates for sorting
                    for i, text in enumerate(rec_texts):
                        if text and text.strip():
                            # Get average y-coordinate from polygon
                            avg_y = 0
                            if i < len(dt_polys):
                                poly = dt_polys[i]
                                avg_y = sum(p[1] for p in poly) / len(poly)
                            texts.append((avg_y, text.strip()))
        
        # Sort by y-coordinate (top to bottom)
        texts.sort(key=lambda x: x[0])
        text_list = [item[1] for item in texts]
        
        # Merge lines and clean up
        merged = self.merge_lines(text_list)
        return self._clean_text(merged)
    
    def merge_lines(self, texts: list[str]) -> str:
        """
        Merge multiple text lines into a single string.
        
        For labels like:
            Line 1: "AV"
            Line 2: "C101"
        Result: "AV C101"
        
        Args:
            texts: List of text strings from each line
        
        Returns:
            Single merged string with space separator
        """
        if not texts:
            return ""
        
        # Filter empty strings and strip whitespace
        cleaned = [t.strip() for t in texts if t and t.strip()]
        
        # Join with space
        return " ".join(cleaned)
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Applies:
        - Upscaling for small images
        - Contrast enhancement
        """
        # Ensure image is large enough
        h, w = image.shape[:2]
        min_size = 100
        
        if h < min_size or w < min_size:
            scale = max(min_size / h, min_size / w, 2.0)
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)
        
        # Convert back to BGR for PaddleOCR
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean OCR output by removing noise and unwanted characters.
        
        Args:
            text: Raw OCR text
        
        Returns:
            Cleaned text string
        """
        if not text:
            return ""
        
        # Remove common OCR artifacts
        # Keep alphanumeric, space, and common label characters
        cleaned = re.sub(r'[^\w\s\-_]', '', text)
        
        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Convert to uppercase for consistency
        cleaned = cleaned.upper()
        
        return cleaned
    
    def batch_extract(
        self, 
        images: list[np.ndarray],
        preprocess: bool = True
    ) -> list[str]:
        """
        Extract text from multiple ROI images.
        
        Args:
            images: List of cropped label images
            preprocess: Whether to apply preprocessing
        
        Returns:
            List of extracted text strings
        """
        return [self.extract_text(img, preprocess) for img in images]
