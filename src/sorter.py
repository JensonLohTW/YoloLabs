"""
Sorting Module for arranging detected labels in reading order.

Implements row-column sorting: top-to-bottom, left-to-right within each row.
"""

from typing import Any

from .detector import BoundingBox


def sort_by_reading_order(
    boxes: list[BoundingBox],
    y_tolerance: int = 20
) -> list[BoundingBox]:
    """
    Sort bounding boxes in reading order: top-to-bottom, left-to-right.
    
    Algorithm:
    1. Group boxes by Y-coordinate with tolerance (same row detection)
    2. Sort rows by average Y position (top-to-bottom)
    3. Within each row, sort by X position (left-to-right)
    4. Flatten to final ordered list
    
    Args:
        boxes: List of BoundingBox objects to sort
        y_tolerance: Maximum Y-coordinate difference to consider boxes in the same row.
                     Boxes with center_y within this tolerance are grouped together.
    
    Returns:
        Sorted list of BoundingBox objects in reading order
    """
    if not boxes:
        return []
    
    if len(boxes) == 1:
        return boxes
    
    # Sort by center_y first to help with grouping
    sorted_by_y = sorted(boxes, key=lambda b: b.center_y)
    
    # Group into rows based on y_tolerance
    rows: list[list[BoundingBox]] = []
    current_row: list[BoundingBox] = [sorted_by_y[0]]
    
    for box in sorted_by_y[1:]:
        # Check if this box belongs to the current row
        row_center_y = sum(b.center_y for b in current_row) / len(current_row)
        
        if abs(box.center_y - row_center_y) <= y_tolerance:
            # Same row
            current_row.append(box)
        else:
            # New row
            rows.append(current_row)
            current_row = [box]
    
    # Don't forget the last row
    if current_row:
        rows.append(current_row)
    
    # Sort rows by average Y position (top-to-bottom)
    rows.sort(key=lambda row: sum(b.center_y for b in row) / len(row))
    
    # Sort boxes within each row by X position (left-to-right)
    sorted_boxes = []
    for row in rows:
        row_sorted = sorted(row, key=lambda b: b.center_x)
        sorted_boxes.extend(row_sorted)
    
    return sorted_boxes


def sort_with_data(
    boxes: list[BoundingBox],
    data: list[Any],
    y_tolerance: int = 20
) -> tuple[list[BoundingBox], list[Any]]:
    """
    Sort bounding boxes and their associated data in reading order.
    
    Args:
        boxes: List of BoundingBox objects
        data: List of associated data (e.g., OCR text) - must match boxes length
        y_tolerance: Y-coordinate tolerance for row grouping
    
    Returns:
        Tuple of (sorted_boxes, sorted_data)
    
    Raises:
        ValueError: If boxes and data have different lengths
    """
    if len(boxes) != len(data):
        raise ValueError(
            f"boxes and data must have same length: {len(boxes)} != {len(data)}"
        )
    
    if not boxes:
        return [], []
    
    # Create pairs and sort
    pairs = list(zip(boxes, data))
    
    # Sort by center_y first
    sorted_by_y = sorted(pairs, key=lambda p: p[0].center_y)
    
    # Group into rows
    rows: list[list[tuple[BoundingBox, Any]]] = []
    current_row: list[tuple[BoundingBox, Any]] = [sorted_by_y[0]]
    
    for pair in sorted_by_y[1:]:
        row_center_y = sum(p[0].center_y for p in current_row) / len(current_row)
        
        if abs(pair[0].center_y - row_center_y) <= y_tolerance:
            current_row.append(pair)
        else:
            rows.append(current_row)
            current_row = [pair]
    
    if current_row:
        rows.append(current_row)
    
    # Sort rows top-to-bottom
    rows.sort(key=lambda row: sum(p[0].center_y for p in row) / len(row))
    
    # Sort within rows left-to-right
    sorted_pairs = []
    for row in rows:
        row_sorted = sorted(row, key=lambda p: p[0].center_x)
        sorted_pairs.extend(row_sorted)
    
    # Unzip results
    sorted_boxes = [p[0] for p in sorted_pairs]
    sorted_data = [p[1] for p in sorted_pairs]
    
    return sorted_boxes, sorted_data


def estimate_y_tolerance(boxes: list[BoundingBox]) -> int:
    """
    Automatically estimate an appropriate y_tolerance value.
    
    Based on the average height of bounding boxes - boxes in the same row
    typically have centers within half the box height.
    
    Args:
        boxes: List of BoundingBox objects
    
    Returns:
        Estimated y_tolerance value in pixels
    """
    if not boxes:
        return 20  # Default
    
    avg_height = sum(b.height for b in boxes) / len(boxes)
    
    # Use half the average height as tolerance, with min/max bounds
    tolerance = int(avg_height * 0.5)
    
    return max(10, min(tolerance, 100))  # Clamp to [10, 100]


def get_row_info(
    boxes: list[BoundingBox],
    y_tolerance: int = 20
) -> list[dict]:
    """
    Get information about each detected row.
    
    Args:
        boxes: List of BoundingBox objects
        y_tolerance: Y-coordinate tolerance for row grouping
    
    Returns:
        List of dictionaries with row information:
        - row_index: Row number (0-indexed)
        - count: Number of boxes in row
        - avg_y: Average Y-coordinate of row
        - min_x: Leftmost X-coordinate
        - max_x: Rightmost X-coordinate
    """
    if not boxes:
        return []
    
    # Sort and group into rows
    sorted_by_y = sorted(boxes, key=lambda b: b.center_y)
    
    rows: list[list[BoundingBox]] = []
    current_row: list[BoundingBox] = [sorted_by_y[0]]
    
    for box in sorted_by_y[1:]:
        row_center_y = sum(b.center_y for b in current_row) / len(current_row)
        
        if abs(box.center_y - row_center_y) <= y_tolerance:
            current_row.append(box)
        else:
            rows.append(current_row)
            current_row = [box]
    
    if current_row:
        rows.append(current_row)
    
    # Sort rows top-to-bottom
    rows.sort(key=lambda row: sum(b.center_y for b in row) / len(row))
    
    # Build row info
    row_info = []
    for i, row in enumerate(rows):
        info = {
            "row_index": i,
            "count": len(row),
            "avg_y": sum(b.center_y for b in row) / len(row),
            "min_x": min(b.x1 for b in row),
            "max_x": max(b.x2 for b in row),
        }
        row_info.append(info)
    
    return row_info
