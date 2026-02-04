"""
YOLOv8 Training Script for Circle Label Detection

This script trains a YOLOv8 model to detect circular labels in equipment layout images.
Optimized for Apple Silicon (MPS) acceleration.
"""

from pathlib import Path

from ultralytics import YOLO


def train_model(
    data_yaml: str | Path = "dataset/data.yaml",
    model_name: str = "yolov8n.pt",
    epochs: int = 100,
    batch_size: int = 16,
    img_size: int = 640,
    output_dir: str | Path = "models",
    device: str | None = None,
    patience: int = 20,
    **kwargs
) -> Path:
    """
    Train a YOLOv8 model for circle label detection.
    
    Args:
        data_yaml: Path to dataset configuration file
        model_name: Base model to fine-tune (yolov8n/s/m/l/x.pt)
        epochs: Number of training epochs
        batch_size: Batch size for training
        img_size: Input image size
        output_dir: Directory to save trained model
        device: Device to train on ('cpu', 'mps', 'cuda', or None for auto)
        patience: Early stopping patience
        **kwargs: Additional arguments for YOLO training
    
    Returns:
        Path to the best trained model weights
    """
    data_yaml = Path(data_yaml)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Verify dataset exists
    if not data_yaml.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found: {data_yaml}\n"
            "Run label_tool.py first to create the dataset."
        )
    
    # Load pre-trained model
    print(f"Loading base model: {model_name}")
    model = YOLO(model_name)
    
    # Prepare training arguments
    train_args = {
        "data": str(data_yaml),
        "epochs": epochs,
        "batch": batch_size,
        "imgsz": img_size,
        "patience": patience,
        "project": str(output_dir),
        "name": "circle_detector",
        "exist_ok": True,
        "pretrained": True,
        "optimizer": "AdamW",
        "lr0": 0.001,
        "lrf": 0.01,
        "momentum": 0.937,
        "weight_decay": 0.0005,
        "warmup_epochs": 3.0,
        "warmup_momentum": 0.8,
        "warmup_bias_lr": 0.1,
        "close_mosaic": 10,
        "save": True,
        "save_period": 10,
        "verbose": True,
    }
    
    # Set device
    if device:
        train_args["device"] = device
    
    # Add any additional arguments
    train_args.update(kwargs)
    
    # Start training
    print(f"\nStarting training with {epochs} epochs...")
    print(f"Dataset: {data_yaml}")
    print(f"Output: {output_dir}")
    
    results = model.train(**train_args)
    
    # Get path to best weights
    best_weights = output_dir / "circle_detector" / "weights" / "best.pt"
    
    # Copy best weights to main models directory
    final_path = output_dir / "best.pt"
    if best_weights.exists():
        import shutil
        shutil.copy2(best_weights, final_path)
        print(f"\nBest model saved to: {final_path}")
    
    return final_path


def validate_model(
    model_path: str | Path,
    data_yaml: str | Path = "dataset/data.yaml",
    device: str | None = None
) -> dict:
    """
    Validate a trained model on the validation set.
    
    Args:
        model_path: Path to trained model weights
        data_yaml: Path to dataset configuration
        device: Device to run validation on
    
    Returns:
        Dictionary with validation metrics
    """
    model = YOLO(str(model_path))
    
    val_args = {
        "data": str(data_yaml),
        "verbose": True,
    }
    
    if device:
        val_args["device"] = device
    
    results = model.val(**val_args)
    
    return {
        "mAP50": results.box.map50,
        "mAP50-95": results.box.map,
        "precision": results.box.mp,
        "recall": results.box.mr,
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train YOLOv8 circle label detector")
    parser.add_argument("--data", type=str, default="dataset/data.yaml", help="Dataset config path")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model (yolov8n/s/m/l/x)")
    parser.add_argument("--epochs", type=int, default=100, help="Training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--img-size", type=int, default=640, help="Image size")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu/mps/cuda)")
    parser.add_argument("--output", type=str, default="models", help="Output directory")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience")
    parser.add_argument("--validate-only", type=str, default=None, help="Validate existing model")
    
    args = parser.parse_args()
    
    if args.validate_only:
        # Validation mode
        print(f"Validating model: {args.validate_only}")
        metrics = validate_model(args.validate_only, args.data, args.device)
        
        print("\nValidation Results:")
        print(f"  mAP@50:     {metrics['mAP50']:.4f}")
        print(f"  mAP@50-95:  {metrics['mAP50-95']:.4f}")
        print(f"  Precision:  {metrics['precision']:.4f}")
        print(f"  Recall:     {metrics['recall']:.4f}")
    else:
        # Training mode
        best_path = train_model(
            data_yaml=args.data,
            model_name=args.model,
            epochs=args.epochs,
            batch_size=args.batch,
            img_size=args.img_size,
            output_dir=args.output,
            device=args.device,
            patience=args.patience,
        )
        
        print(f"\nTraining complete! Best model: {best_path}")
        
        # Validate the trained model
        print("\nValidating trained model...")
        metrics = validate_model(best_path, args.data, args.device)
        
        print("\nFinal Validation Results:")
        print(f"  mAP@50:     {metrics['mAP50']:.4f}")
        print(f"  mAP@50-95:  {metrics['mAP50-95']:.4f}")
        print(f"  Precision:  {metrics['precision']:.4f}")
        print(f"  Recall:     {metrics['recall']:.4f}")
