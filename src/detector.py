"""
Circle Label Detector using YOLOv8

This module provides functionality to detect circular labels in equipment layout images.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass
class BoundingBox:
    """Represents a detected bounding box with its properties."""
    x1: int  # Top-left x
    y1: int  # Top-left y
    x2: int  # Bottom-right x
    y2: int  # Bottom-right y
    confidence: float
    class_id: int = 0
    
    @property
    def center_x(self) -> int:
        """Get the center x coordinate."""
        return (self.x1 + self.x2) // 2
    
    @property
    def center_y(self) -> int:
        """Get the center y coordinate."""
        return (self.y1 + self.y2) // 2
    
    @property
    def width(self) -> int:
        """Get the width of the bounding box."""
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        """Get the height of the bounding box."""
        return self.y2 - self.y1
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "center_x": self.center_x,
            "center_y": self.center_y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
        }


class CircleDetector:
    """
    YOLO-based circle label detector.
    
    This class wraps YOLOv8 for detecting circular labels in equipment layout images.
    """
    
    def __init__(self, model_path: str | Path, confidence_threshold: float = 0.5):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to the trained YOLO model weights (.pt file)
            confidence_threshold: Minimum confidence for detections (0-1)
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Load the YOLO model
        self.model = YOLO(str(self.model_path))
    
    def detect(
        self, 
        image: np.ndarray | str | Path,
        device: Optional[str] = None
    ) -> list[BoundingBox]:
        """
        Detect circular labels in an image.
        
        Args:
            image: Input image as numpy array or path to image file
            device: Device to run inference on ('cpu', 'mps', 'cuda', or None for auto)
        
        Returns:
            List of BoundingBox objects for detected labels
        """
        # Load image if path is provided
        if isinstance(image, (str, Path)):
            image = cv2.imread(str(image))
            if image is None:
                raise ValueError(f"Could not load image: {image}")
        
        # Run inference
        inference_args = {
            "conf": self.confidence_threshold,
            "verbose": False,
        }
        if device:
            inference_args["device"] = device
        
        results = self.model(image, **inference_args)
        
        # Parse results
        boxes = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy()) if box.cls is not None else 0
                    
                    boxes.append(BoundingBox(
                        x1=int(xyxy[0]),
                        y1=int(xyxy[1]),
                        x2=int(xyxy[2]),
                        y2=int(xyxy[3]),
                        confidence=conf,
                        class_id=cls
                    ))
        
        return boxes
    
    def detect_from_file(
        self, 
        image_path: str | Path,
        device: Optional[str] = None
    ) -> tuple[np.ndarray, list[BoundingBox]]:
        """
        Detect circular labels from an image file.
        
        Args:
            image_path: Path to the image file
            device: Device to run inference on
        
        Returns:
            Tuple of (original image, list of BoundingBox objects)
        """
        image_path = Path(image_path)
        image = cv2.imread(str(image_path))
        
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        boxes = self.detect(image, device=device)
        return image, boxes
    
    def crop_roi(
        self, 
        image: np.ndarray, 
        box: BoundingBox,
        padding: int = 0
    ) -> np.ndarray:
        """
        Crop a region of interest from the image.
        
        Args:
            image: Source image
            box: Bounding box defining the ROI
            padding: Extra padding around the box (in pixels)
        
        Returns:
            Cropped image region
        """
        h, w = image.shape[:2]
        
        x1 = max(0, box.x1 - padding)
        y1 = max(0, box.y1 - padding)
        x2 = min(w, box.x2 + padding)
        y2 = min(h, box.y2 + padding)
        
        return image[y1:y2, x1:x2].copy()
