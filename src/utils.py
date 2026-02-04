"""
Utility functions for visualization and data export.
"""

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pandas as pd

from .detector import BoundingBox


def draw_detections(
    image: np.ndarray,
    boxes: list[BoundingBox],
    texts: Optional[list[str]] = None,
    show_sequence: bool = True,
    box_color: tuple[int, int, int] = (0, 255, 0),  # Green in BGR
    text_color: tuple[int, int, int] = (255, 0, 0),  # Blue in BGR
    font_scale: float = 0.6,
    thickness: int = 2
) -> np.ndarray:
    """
    Draw detection boxes and labels on an image.
    
    Args:
        image: Input image (will be copied, not modified)
        boxes: List of BoundingBox objects
        texts: Optional list of text labels for each box
        show_sequence: Whether to show sequence numbers
        box_color: Color for bounding boxes (BGR)
        text_color: Color for text labels (BGR)
        font_scale: Font scale for text
        thickness: Line thickness for boxes
    
    Returns:
        Annotated image with boxes and labels drawn
    """
    result = image.copy()
    
    for i, box in enumerate(boxes):
        # Draw bounding box
        cv2.rectangle(
            result,
            (box.x1, box.y1),
            (box.x2, box.y2),
            box_color,
            thickness
        )
        
        # Build label text
        label_parts = []
        
        if show_sequence:
            label_parts.append(f"{i + 1}")
        
        if texts and i < len(texts) and texts[i]:
            label_parts.append(texts[i])
        
        if label_parts:
            label = ": ".join(label_parts) if len(label_parts) > 1 else label_parts[0]
            
            # Calculate text position (above the box)
            font = cv2.FONT_HERSHEY_SIMPLEX
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )
            
            # Position text above box, or inside if at top edge
            text_x = box.x1
            text_y = box.y1 - 5
            
            if text_y < text_height + 5:
                text_y = box.y1 + text_height + 5
            
            # Draw background rectangle for text
            bg_x1 = text_x - 2
            bg_y1 = text_y - text_height - 2
            bg_x2 = text_x + text_width + 2
            bg_y2 = text_y + baseline + 2
            
            cv2.rectangle(result, (bg_x1, bg_y1), (bg_x2, bg_y2), (255, 255, 255), -1)
            
            # Draw text
            cv2.putText(
                result,
                label,
                (text_x, text_y),
                font,
                font_scale,
                text_color,
                max(1, thickness - 1)
            )
    
    return result


def export_to_csv(
    boxes: list[BoundingBox],
    texts: list[str],
    output_path: str | Path,
    include_coords: bool = True
) -> Path:
    """
    Export detection results to a CSV file.
    
    Args:
        boxes: List of BoundingBox objects
        texts: List of recognized text for each box
        output_path: Path to save the CSV file
        include_coords: Whether to include coordinate columns
    
    Returns:
        Path to the saved CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = []
    for i, (box, text) in enumerate(zip(boxes, texts)):
        row = {
            "序號": i + 1,
            "識別內容": text,
        }
        
        if include_coords:
            row.update({
                "X": box.center_x,
                "Y": box.center_y,
                "Width": box.width,
                "Height": box.height,
                "Confidence": round(box.confidence, 3),
            })
        
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")  # utf-8-sig for Excel compatibility
    
    return output_path


def export_to_excel(
    boxes: list[BoundingBox],
    texts: list[str],
    output_path: str | Path,
    include_coords: bool = True,
    sheet_name: str = "識別結果"
) -> Path:
    """
    Export detection results to an Excel file.
    
    Args:
        boxes: List of BoundingBox objects
        texts: List of recognized text for each box
        output_path: Path to save the Excel file
        include_coords: Whether to include coordinate columns
        sheet_name: Name of the Excel sheet
    
    Returns:
        Path to the saved Excel file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = []
    for i, (box, text) in enumerate(zip(boxes, texts)):
        row = {
            "序號": i + 1,
            "識別內容": text,
        }
        
        if include_coords:
            row.update({
                "X": box.center_x,
                "Y": box.center_y,
                "Width": box.width,
                "Height": box.height,
                "Confidence": round(box.confidence, 3),
            })
        
        data.append(row)
    
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False, sheet_name=sheet_name)
    
    return output_path


def save_annotated_image(
    image: np.ndarray,
    output_path: str | Path,
    quality: int = 95
) -> Path:
    """
    Save an annotated image to file.
    
    Args:
        image: Image to save
        output_path: Path to save the image
        quality: JPEG quality (1-100)
    
    Returns:
        Path to the saved image
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine file format from extension
    ext = output_path.suffix.lower()
    
    if ext in [".jpg", ".jpeg"]:
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    elif ext == ".png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, 3]
    else:
        params = []
    
    cv2.imwrite(str(output_path), image, params)
    
    return output_path


def resize_for_display(
    image: np.ndarray,
    max_width: int = 1920,
    max_height: int = 1080
) -> np.ndarray:
    """
    Resize image to fit within display bounds while maintaining aspect ratio.
    
    Args:
        image: Input image
        max_width: Maximum width
        max_height: Maximum height
    
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    if w <= max_width and h <= max_height:
        return image
    
    scale = min(max_width / w, max_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def format_results_summary(
    boxes: list[BoundingBox],
    texts: list[str]
) -> str:
    """
    Format detection results as a human-readable summary.
    
    Args:
        boxes: List of BoundingBox objects
        texts: List of recognized text
    
    Returns:
        Formatted summary string
    """
    lines = [
        f"Total labels detected: {len(boxes)}",
        "-" * 40,
    ]
    
    for i, text in enumerate(texts):
        lines.append(f"{i + 1:3d}. {text}")
    
    return "\n".join(lines)
