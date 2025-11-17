"""
PPE (Personal Protective Equipment) Detection Module
Uses YOLOv11 for detecting safety equipment: helmet, gloves, boots, jacket
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO
import torch

# Required PPE items
REQUIRED_PPE = {
    "helmet": True,
    "gloves": True,
    "boots": True,
    "jacket": True,  # Also detects "vest" as jacket
}

# Confidence threshold for PPE detection
PPE_CONFIDENCE_THRESHOLD = 0.5

# Class mappings for PPE items (YOLO class names may vary)
PPE_CLASS_MAPPINGS = {
    "helmet": ["helmet", "hard-hat", "hardhat", "safety-helmet"],
    "gloves": ["gloves", "glove", "safety-gloves"],
    "boots": ["boots", "boot", "safety-boots", "safety-shoes"],
    "jacket": ["jacket", "vest", "safety-vest", "safety-jacket", "reflective-vest"],
}

# Global model variable
ppe_model = None


def load_ppe_model(model_path=None, use_pretrained=True):
    """
    Load YOLO model for PPE detection.
    
    Args:
        model_path: Path to custom trained model (.pt file). If None, uses pre-trained.
        use_pretrained: If True, uses pre-trained YOLOv11. If False, requires model_path.
    
    Returns:
        YOLO model instance
    """
    global ppe_model
    
    if ppe_model is not None:
        return ppe_model
    
    try:
        if model_path and os.path.exists(model_path):
            print(f"[PPE] Loading custom model from: {model_path}")
            ppe_model = YOLO(model_path)
        elif use_pretrained:
            print("[PPE] Loading pre-trained YOLOv11 model...")
            # Try YOLOv11 first, fallback to YOLOv8
            try:
                ppe_model = YOLO("yolo11n.pt")  # nano version for speed
                print("[PPE] YOLOv11 loaded successfully")
            except:
                print("[PPE] YOLOv11 not available, trying YOLOv8...")
                ppe_model = YOLO("yolo8n.pt")
                print("[PPE] YOLOv8 loaded successfully")
        else:
            raise ValueError("No model path provided and use_pretrained is False")
        
        # Move model to appropriate device
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"[PPE] Model loaded on device: {device}")
        
        return ppe_model
    except Exception as e:
        print(f"[PPE ERROR] Failed to load model: {e}")
        print("[PPE] Attempting to download pre-trained model...")
        try:
            ppe_model = YOLO("yolo11n.pt")
            return ppe_model
        except:
            print("[PPE ERROR] Could not load PPE model. PPE detection will be disabled.")
            return None


def normalize_class_name(class_name):
    """Normalize class name to match our PPE categories."""
    class_name_lower = class_name.lower().replace("_", "-").replace(" ", "-")
    
    # Check each PPE category
    for ppe_item, variants in PPE_CLASS_MAPPINGS.items():
        for variant in variants:
            if variant in class_name_lower or class_name_lower in variant:
                return ppe_item
    
    return None


def detect_ppe_items(frame, model=None, confidence_threshold=PPE_CONFIDENCE_THRESHOLD):
    """
    Detect PPE items in a frame.
    
    Args:
        frame: Input frame (BGR format, OpenCV format)
        model: YOLO model instance (if None, uses global model)
        confidence_threshold: Minimum confidence for detection
    
    Returns:
        dict: {
            "helmet": (detected: bool, confidence: float),
            "gloves": (detected: bool, confidence: float),
            "boots": (detected: bool, confidence: float),
            "jacket": (detected: bool, confidence: float),
            "all_detections": list of all detections
        }
    """
    if model is None:
        model = ppe_model
        if model is None:
            model = load_ppe_model()
    
    if model is None:
        # Return default (all False) if model not available
        return {
            "helmet": (False, 0.0),
            "gloves": (False, 0.0),
            "boots": (False, 0.0),
            "jacket": (False, 0.0),
            "all_detections": [],
        }
    
    try:
        # Run YOLO inference
        results = model(frame, conf=confidence_threshold, verbose=False)
        
        # Initialize detection results
        detections = {
            "helmet": (False, 0.0),
            "gloves": (False, 0.0),
            "boots": (False, 0.0),
            "jacket": (False, 0.0),
            "all_detections": [],
        }
        
        # Process detections
        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            
            for i in range(len(boxes)):
                cls = int(boxes.cls[i])
                conf = float(boxes.conf[i])
                class_name = model.names[cls] if hasattr(model, 'names') else str(cls)
                
                # Normalize class name to our PPE categories
                ppe_item = normalize_class_name(class_name)
                
                if ppe_item and ppe_item in detections:
                    # Update if this detection has higher confidence
                    current_conf = detections[ppe_item][1]
                    if conf > current_conf:
                        detections[ppe_item] = (True, conf)
                
                # Store all detections for debugging
                detections["all_detections"].append({
                    "class": class_name,
                    "ppe_item": ppe_item,
                    "confidence": conf,
                    "box": boxes.xyxy[i].cpu().numpy().tolist() if hasattr(boxes, 'xyxy') else None
                })
        
        return detections
        
    except Exception as e:
        print(f"[PPE ERROR] Detection failed: {e}")
        return {
            "helmet": (False, 0.0),
            "gloves": (False, 0.0),
            "boots": (False, 0.0),
            "jacket": (False, 0.0),
            "all_detections": [],
        }


def check_ppe_compliance(detections, required_items=None, confidence_threshold=PPE_CONFIDENCE_THRESHOLD):
    """
    Check if all required PPE items are detected.
    
    Args:
        detections: Output from detect_ppe_items()
        required_items: Dict of required items (default: REQUIRED_PPE)
        confidence_threshold: Minimum confidence to consider item detected
    
    Returns:
        tuple: (is_compliant: bool, missing_items: list, compliance_dict: dict)
    """
    if required_items is None:
        required_items = REQUIRED_PPE
    
    compliance_dict = {}
    missing_items = []
    
    for item, required in required_items.items():
        if required:
            detected, confidence = detections.get(item, (False, 0.0))
            
            # Check if detected with sufficient confidence
            is_detected = detected and confidence >= confidence_threshold
            compliance_dict[item] = {
                "detected": is_detected,
                "confidence": confidence
            }
            
            if not is_detected:
                missing_items.append(item)
    
    is_compliant = len(missing_items) == 0
    
    return is_compliant, missing_items, compliance_dict


def get_ppe_status_string(detections, compliance_dict):
    """Get a human-readable string of PPE status."""
    status_parts = []
    
    for item in ["helmet", "gloves", "boots", "jacket"]:
        if item in compliance_dict:
            detected = compliance_dict[item]["detected"]
            conf = compliance_dict[item]["confidence"]
            status = "✓" if detected else "✗"
            status_parts.append(f"{status} {item.capitalize()}({conf:.2f})")
    
    return " | ".join(status_parts)


# Initialize model on import (lazy loading - only loads when first used)
def initialize_ppe_model():
    """Initialize PPE model. Call this before first use."""
    if ppe_model is None:
        load_ppe_model()
    return ppe_model is not None

