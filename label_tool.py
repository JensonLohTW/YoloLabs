"""
Automatic Label Generation Tool using Hough Circle Detection

This tool provides semi-automated labeling for YOLO training by detecting
circles in images and creating initial bounding box annotations.
"""

import random
import shutil
from pathlib import Path

import cv2
import numpy as np


def detect_circles_hough(
    image: np.ndarray,
    dp: float = 1.2,
    min_dist: int = 50,
    param1: int = 50,
    param2: int = 30,
    min_radius: int = 20,
    max_radius: int = 100
) -> list[tuple[int, int, int]]:
    """
    Detect circles using Hough Circle Transform.
    
    Args:
        image: Input BGR image
        dp: Inverse ratio of accumulator resolution to image resolution
        min_dist: Minimum distance between circle centers
        param1: Higher threshold for Canny edge detector
        param2: Threshold for center detection
        min_radius: Minimum circle radius
        max_radius: Maximum circle radius
    
    Returns:
        List of (center_x, center_y, radius) tuples
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Detect circles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=dp,
        minDist=min_dist,
        param1=param1,
        param2=param2,
        minRadius=min_radius,
        maxRadius=max_radius
    )
    
    if circles is None:
        return []
    
    # Convert to list of tuples
    circles = np.round(circles[0, :]).astype(int)
    return [(int(c[0]), int(c[1]), int(c[2])) for c in circles]


def circle_to_yolo_bbox(
    cx: int, cy: int, radius: int,
    img_width: int, img_height: int,
    padding_ratio: float = 0.1
) -> tuple[float, float, float, float]:
    """
    Convert a circle to YOLO format bounding box.
    
    YOLO format: <class_id> <x_center> <y_center> <width> <height>
    All values normalized to [0, 1]
    
    Args:
        cx, cy: Circle center coordinates
        radius: Circle radius
        img_width, img_height: Image dimensions
        padding_ratio: Extra padding around the circle (ratio of radius)
    
    Returns:
        Tuple of (x_center, y_center, width, height) normalized to [0, 1]
    """
    # Add padding to make sure we capture the full circle
    padded_radius = radius * (1 + padding_ratio)
    
    # Calculate bounding box (use square for circles)
    box_size = padded_radius * 2
    
    # Normalize to [0, 1]
    x_center = cx / img_width
    y_center = cy / img_height
    width = box_size / img_width
    height = box_size / img_height
    
    # Clamp to valid range
    x_center = max(0.0, min(1.0, x_center))
    y_center = max(0.0, min(1.0, y_center))
    width = max(0.0, min(1.0, width))
    height = max(0.0, min(1.0, height))
    
    return x_center, y_center, width, height


def generate_labels_for_image(
    image_path: Path,
    output_label_path: Path,
    class_id: int = 0,
    **hough_params
) -> int:
    """
    Generate YOLO label file for a single image.
    
    Args:
        image_path: Path to input image
        output_label_path: Path to save label file
        class_id: Class ID for the labels
        **hough_params: Parameters for Hough Circle detection
    
    Returns:
        Number of circles detected
    """
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return 0
    
    h, w = image.shape[:2]
    
    # Detect circles
    circles = detect_circles_hough(image, **hough_params)
    
    if not circles:
        print(f"Warning: No circles found in {image_path.name}")
        return 0
    
    # Write YOLO format labels
    output_label_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_label_path, 'w') as f:
        for cx, cy, radius in circles:
            x_c, y_c, bw, bh = circle_to_yolo_bbox(cx, cy, radius, w, h)
            f.write(f"{class_id} {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}\n")
    
    print(f"Generated {len(circles)} labels for {image_path.name}")
    return len(circles)


def visualize_detections(
    image_path: Path,
    label_path: Path,
    output_path: Path
) -> None:
    """
    Visualize YOLO labels on an image for verification.
    
    Args:
        image_path: Path to input image
        label_path: Path to YOLO label file
        output_path: Path to save visualization
    """
    image = cv2.imread(str(image_path))
    if image is None:
        return
    
    h, w = image.shape[:2]
    
    if not label_path.exists():
        return
    
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            
            _, x_c, y_c, bw, bh = map(float, parts)
            
            # Convert normalized coords to pixel coords
            cx = int(x_c * w)
            cy = int(y_c * h)
            box_w = int(bw * w)
            box_h = int(bh * h)
            
            x1 = cx - box_w // 2
            y1 = cy - box_h // 2
            x2 = cx + box_w // 2
            y2 = cy + box_h // 2
            
            # Draw rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)


def create_yolo_dataset(
    input_dir: Path,
    output_dir: Path,
    train_ratio: float = 0.8,
    **hough_params
) -> dict:
    """
    Create a complete YOLO dataset from a directory of images.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory to create dataset in
        train_ratio: Ratio of images for training (rest goes to validation)
        **hough_params: Parameters for Hough Circle detection
    
    Returns:
        Dictionary with statistics about the created dataset
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    # Find all images
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    images = [
        p for p in input_dir.iterdir()
        if p.suffix.lower() in image_extensions
    ]
    
    if not images:
        print(f"No images found in {input_dir}")
        return {"total_images": 0, "total_labels": 0}
    
    # Shuffle and split
    random.shuffle(images)
    split_idx = int(len(images) * train_ratio)
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    # Create directories
    train_img_dir = output_dir / "images" / "train"
    val_img_dir = output_dir / "images" / "val"
    train_label_dir = output_dir / "labels" / "train"
    val_label_dir = output_dir / "labels" / "val"
    
    for d in [train_img_dir, val_img_dir, train_label_dir, val_label_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Process images
    stats = {
        "train_images": len(train_images),
        "val_images": len(val_images),
        "train_labels": 0,
        "val_labels": 0,
    }
    
    # Process training images
    for img_path in train_images:
        # Copy image
        dst_img = train_img_dir / img_path.name
        shutil.copy2(img_path, dst_img)
        
        # Generate label
        label_name = img_path.stem + ".txt"
        dst_label = train_label_dir / label_name
        
        count = generate_labels_for_image(img_path, dst_label, **hough_params)
        stats["train_labels"] += count
    
    # Process validation images
    for img_path in val_images:
        # Copy image
        dst_img = val_img_dir / img_path.name
        shutil.copy2(img_path, dst_img)
        
        # Generate label
        label_name = img_path.stem + ".txt"
        dst_label = val_label_dir / label_name
        
        count = generate_labels_for_image(img_path, dst_label, **hough_params)
        stats["val_labels"] += count
    
    # Create data.yaml
    data_yaml = output_dir / "data.yaml"
    with open(data_yaml, 'w') as f:
        f.write(f"path: {output_dir.absolute()}\n")
        f.write("train: images/train\n")
        f.write("val: images/val\n\n")
        f.write("names:\n")
        f.write("  0: circle_label\n\n")
        f.write("nc: 1\n")
    
    print(f"\nDataset created at {output_dir}")
    print(f"Training: {stats['train_images']} images, {stats['train_labels']} labels")
    print(f"Validation: {stats['val_images']} images, {stats['val_labels']} labels")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate YOLO labels from images with circles")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input image directory")
    parser.add_argument("--output", "-o", type=str, default="dataset", help="Output dataset directory")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Training set ratio")
    parser.add_argument("--min-dist", type=int, default=50, help="Minimum distance between circles")
    parser.add_argument("--param1", type=int, default=50, help="Canny edge threshold")
    parser.add_argument("--param2", type=int, default=30, help="Circle detection threshold")
    parser.add_argument("--min-radius", type=int, default=20, help="Minimum circle radius")
    parser.add_argument("--max-radius", type=int, default=100, help="Maximum circle radius")
    parser.add_argument("--visualize", "-v", action="store_true", help="Create visualization images")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    hough_params = {
        "min_dist": args.min_dist,
        "param1": args.param1,
        "param2": args.param2,
        "min_radius": args.min_radius,
        "max_radius": args.max_radius,
    }
    
    stats = create_yolo_dataset(
        input_dir,
        output_dir,
        train_ratio=args.train_ratio,
        **hough_params
    )
    
    # Optionally create visualizations
    if args.visualize:
        viz_dir = output_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        for split in ["train", "val"]:
            img_dir = output_dir / "images" / split
            label_dir = output_dir / "labels" / split
            
            for img_path in img_dir.iterdir():
                if img_path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp'}:
                    label_path = label_dir / (img_path.stem + ".txt")
                    viz_path = viz_dir / f"{split}_{img_path.name}"
                    visualize_detections(img_path, label_path, viz_path)
        
        print(f"\nVisualizations saved to {viz_dir}")
