"""
Main Pipeline for Circle Label Detection and OCR

Complete inference pipeline that:
1. Detects circular labels using YOLO
2. Extracts text using PaddleOCR
3. Sorts results in reading order
4. Outputs annotated images and data files
"""

from pathlib import Path
from typing import Optional

import cv2

from src.detector import BoundingBox, CircleDetector
from src.ocr import LabelOCR
from src.sorter import estimate_y_tolerance, sort_with_data
from src.utils import (
    draw_detections,
    export_to_csv,
    export_to_excel,
    format_results_summary,
    save_annotated_image,
)


class CircleLabelPipeline:
    """
    Complete pipeline for circle label detection and OCR.
    """
    
    def __init__(
        self,
        model_path: str | Path,
        confidence_threshold: float = 0.5,
        y_tolerance: Optional[int] = None,
        ocr_device: str = "cpu",
        ocr_lang: str = "en"
    ):
        """
        Initialize the pipeline.
        
        Args:
            model_path: Path to trained YOLO model
            confidence_threshold: Detection confidence threshold
            y_tolerance: Y-coordinate tolerance for row grouping (None for auto)
            ocr_device: Device for OCR ('cpu', 'gpu')
            ocr_lang: OCR language ('en', 'ch', etc.)
        """
        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold
        self.y_tolerance = y_tolerance
        
        # Initialize detector
        self.detector = CircleDetector(
            model_path=self.model_path,
            confidence_threshold=confidence_threshold
        )
        
        # Initialize OCR
        self.ocr = LabelOCR(
            lang=ocr_lang,
            device=ocr_device
        )
    
    def process_image(
        self,
        image_path: str | Path,
        output_dir: Optional[str | Path] = None,
        device: Optional[str] = None
    ) -> dict:
        """
        Process a single image through the complete pipeline.
        
        Args:
            image_path: Path to input image
            output_dir: Directory to save results (optional)
            device: Device for YOLO inference
        
        Returns:
            Dictionary with processing results
        """
        image_path = Path(image_path)
        
        # Load image and detect circles
        image, boxes = self.detector.detect_from_file(image_path, device=device)
        
        if not boxes:
            return {
                "image_path": str(image_path),
                "num_detections": 0,
                "boxes": [],
                "texts": [],
                "message": "No circles detected"
            }
        
        # Extract text from each detected circle
        texts = []
        for box in boxes:
            roi = self.detector.crop_roi(image, box, padding=5)
            text = self.ocr.extract_text(roi)
            texts.append(text)
        
        # Determine y_tolerance
        tolerance = self.y_tolerance
        if tolerance is None:
            tolerance = estimate_y_tolerance(boxes)
        
        # Sort by reading order
        sorted_boxes, sorted_texts = sort_with_data(boxes, texts, y_tolerance=tolerance)
        
        result = {
            "image_path": str(image_path),
            "num_detections": len(sorted_boxes),
            "boxes": sorted_boxes,
            "texts": sorted_texts,
            "y_tolerance_used": tolerance,
        }
        
        # Save outputs if output_dir specified
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Draw and save annotated image
            annotated = draw_detections(image, sorted_boxes, sorted_texts)
            img_out_path = output_dir / f"annotated_{image_path.name}"
            save_annotated_image(annotated, img_out_path)
            result["annotated_image"] = str(img_out_path)
            
            # Save CSV
            csv_path = output_dir / f"{image_path.stem}_results.csv"
            export_to_csv(sorted_boxes, sorted_texts, csv_path)
            result["csv_path"] = str(csv_path)
        
        return result
    
    def process_directory(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        device: Optional[str] = None,
        export_combined: bool = True
    ) -> list[dict]:
        """
        Process all images in a directory.
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save results
            device: Device for YOLO inference
            export_combined: Whether to export combined Excel file
        
        Returns:
            List of result dictionaries for each image
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        images = sorted([
            p for p in input_dir.iterdir()
            if p.suffix.lower() in image_extensions
        ])
        
        if not images:
            print(f"No images found in {input_dir}")
            return []
        
        results = []
        all_boxes = []
        all_texts = []
        image_names = []
        
        for i, image_path in enumerate(images):
            print(f"Processing [{i+1}/{len(images)}]: {image_path.name}")
            
            result = self.process_image(image_path, output_dir, device)
            results.append(result)
            
            # Collect for combined export
            if result["boxes"]:
                for box, text in zip(result["boxes"], result["texts"]):
                    all_boxes.append(box)
                    all_texts.append(text)
                    image_names.append(image_path.name)
            
            print(f"  Detected: {result['num_detections']} labels")
        
        # Export combined results
        if export_combined and all_boxes:
            combined_csv = output_dir / "combined_results.csv"
            combined_xlsx = output_dir / "combined_results.xlsx"
            
            export_to_csv(all_boxes, all_texts, combined_csv)
            export_to_excel(all_boxes, all_texts, combined_xlsx)
            
            print(f"\nCombined results saved to:")
            print(f"  CSV:   {combined_csv}")
            print(f"  Excel: {combined_xlsx}")
        
        # Print summary
        total_detections = sum(r["num_detections"] for r in results)
        print(f"\nTotal: {len(images)} images, {total_detections} labels detected")
        
        return results


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Circle Label Detection and OCR Pipeline"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="models/best.pt",
        help="Path to trained YOLO model"
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Process a single image"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Input directory with images"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="result_images",
        help="Output directory for results"
    )
    parser.add_argument(
        "--confidence", "-c",
        type=float,
        default=0.5,
        help="Detection confidence threshold"
    )
    parser.add_argument(
        "--y-tolerance",
        type=int,
        default=None,
        help="Y-coordinate tolerance for row grouping (auto if not set)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Device for inference (cpu/mps/cuda)"
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="en",
        help="OCR language (en/ch)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.image and not args.input:
        parser.error("Either --image or --input must be specified")
    
    # Check model exists
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        print("Please train a model first using train.py")
        return 1
    
    # Initialize pipeline
    pipeline = CircleLabelPipeline(
        model_path=args.model,
        confidence_threshold=args.confidence,
        y_tolerance=args.y_tolerance,
        ocr_device="cpu",  # Safe default for Mac
        ocr_lang=args.lang
    )
    
    # Process single image or directory
    if args.image:
        result = pipeline.process_image(
            args.image,
            output_dir=args.output,
            device=args.device
        )
        
        print(f"\nDetected {result['num_detections']} labels:")
        for i, text in enumerate(result['texts']):
            print(f"  {i+1}. {text}")
        
        if 'annotated_image' in result:
            print(f"\nAnnotated image: {result['annotated_image']}")
        if 'csv_path' in result:
            print(f"CSV results: {result['csv_path']}")
    
    else:
        results = pipeline.process_directory(
            input_dir=args.input,
            output_dir=args.output,
            device=args.device
        )
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
