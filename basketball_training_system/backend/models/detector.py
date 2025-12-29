"""
Basketball and Player Detector using YOLOv8.

This module provides real-time detection of basketballs and players
in video frames using the YOLOv8 object detection model.
"""

import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Detection:
    """Represents a single detection result."""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]


class BasketballDetector:
    """
    YOLOv8-based detector for basketball training analysis.
    
    Detects basketballs, players, and basketball hoops in video frames.
    Supports both pre-trained COCO models and custom-trained models.
    """
    
    # Class indices for COCO dataset
    PERSON_CLASS_ID = 0
    SPORTS_BALL_CLASS_ID = 32
    
    # Custom class names for basketball-specific model
    CUSTOM_CLASSES = {
        0: 'basketball',
        1: 'player',
        2: 'hoop',
        3: 'backboard'
    }
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = 'auto'
    ):
        """
        Initialize the basketball detector.
        
        Args:
            model_path: Path to custom YOLOv8 model weights. If None, uses pre-trained model.
            conf_threshold: Confidence threshold for detections.
            iou_threshold: IoU threshold for NMS.
            device: Device to run inference on ('cpu', 'cuda', or 'auto').
        """
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.model = None
        self.model_path = model_path
        self.is_custom_model = model_path is not None and 'basketball' in str(model_path).lower()
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the YOLOv8 model."""
        try:
            from ultralytics import YOLO
            
            if self.model_path and os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
            else:
                # Use pre-trained YOLOv8n for general detection
                self.model = YOLO('yolov8n.pt')
            
            # Set device
            if self.device == 'auto':
                import torch
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                
        except ImportError:
            print("Warning: ultralytics not installed. Using mock detector.")
            self.model = None
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect objects in a single frame.
        
        Args:
            frame: BGR image as numpy array.
            
        Returns:
            List of Detection objects.
        """
        if self.model is None:
            return self._mock_detect(frame)
        
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                # Get class name
                if self.is_custom_model:
                    cls_name = self.CUSTOM_CLASSES.get(cls_id, 'unknown')
                else:
                    cls_name = result.names[cls_id]
                
                # Filter for basketball-relevant classes
                if self._is_relevant_class(cls_id, cls_name):
                    center = ((x1 + x2) // 2, (y1 + y2) // 2)
                    detections.append(Detection(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=center
                    ))
        
        return detections
    
    def _is_relevant_class(self, cls_id: int, cls_name: str) -> bool:
        """Check if detected class is relevant for basketball analysis."""
        if self.is_custom_model:
            return cls_id in self.CUSTOM_CLASSES
        
        # For COCO model, filter for person and sports ball
        relevant_classes = {'person', 'sports ball'}
        return cls_name.lower() in relevant_classes
    
    def _mock_detect(self, frame: np.ndarray) -> List[Detection]:
        """Mock detection for testing without model loaded."""
        # Return empty list when no model is available
        return []
    
    def detect_basketball(self, frame: np.ndarray) -> Optional[Detection]:
        """
        Detect basketball in frame.
        
        Args:
            frame: BGR image as numpy array.
            
        Returns:
            Detection object for basketball, or None if not found.
        """
        detections = self.detect(frame)
        for det in detections:
            if det.class_name.lower() in ['basketball', 'sports ball']:
                return det
        return None
    
    def detect_players(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect all players in frame.
        
        Args:
            frame: BGR image as numpy array.
            
        Returns:
            List of Detection objects for players.
        """
        detections = self.detect(frame)
        return [det for det in detections if det.class_name.lower() in ['player', 'person']]
    
    def detect_with_tracking(
        self,
        frame: np.ndarray,
        tracker_type: str = 'bytetrack'
    ) -> List[Dict[str, Any]]:
        """
        Detect and track objects across frames.
        
        Args:
            frame: BGR image as numpy array.
            tracker_type: Type of tracker ('bytetrack' or 'botsort').
            
        Returns:
            List of tracked detections with IDs.
        """
        if self.model is None:
            return []
        
        results = self.model.track(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            tracker=f"{tracker_type}.yaml",
            persist=True,
            verbose=False
        )
        
        tracked_objects = []
        for result in results:
            boxes = result.boxes
            if boxes.id is not None:
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    track_id = int(boxes.id[i])
                    
                    if self.is_custom_model:
                        cls_name = self.CUSTOM_CLASSES.get(cls_id, 'unknown')
                    else:
                        cls_name = result.names[cls_id]
                    
                    if self._is_relevant_class(cls_id, cls_name):
                        tracked_objects.append({
                            'track_id': track_id,
                            'class_id': cls_id,
                            'class_name': cls_name,
                            'confidence': conf,
                            'bbox': (x1, y1, x2, y2),
                            'center': ((x1 + x2) // 2, (y1 + y2) // 2)
                        })
        
        return tracked_objects
    
    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        show_confidence: bool = True,
        show_labels: bool = True
    ) -> np.ndarray:
        """
        Draw detection boxes on frame.
        
        Args:
            frame: BGR image as numpy array.
            detections: List of Detection objects.
            show_confidence: Whether to show confidence scores.
            show_labels: Whether to show class labels.
            
        Returns:
            Frame with drawn detections.
        """
        result_frame = frame.copy()
        
        colors = {
            'basketball': (0, 165, 255),  # Orange
            'sports ball': (0, 165, 255),
            'player': (0, 255, 0),        # Green
            'person': (0, 255, 0),
            'hoop': (255, 0, 0),          # Blue
            'backboard': (255, 255, 0)    # Cyan
        }
        
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            color = colors.get(det.class_name.lower(), (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            if show_labels:
                label = det.class_name
                if show_confidence:
                    label += f" {det.confidence:.2f}"
                
                (label_w, label_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                cv2.rectangle(
                    result_frame,
                    (x1, y1 - label_h - 10),
                    (x1 + label_w, y1),
                    color, -1
                )
                cv2.putText(
                    result_frame, label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1
                )
            
            # Draw center point
            cv2.circle(result_frame, det.center, 4, color, -1)
        
        return result_frame


def create_detector(
    model_type: str = 'yolov8n',
    custom_weights: Optional[str] = None,
    **kwargs
) -> BasketballDetector:
    """
    Factory function to create a basketball detector.
    
    Args:
        model_type: Type of YOLOv8 model ('yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x').
        custom_weights: Path to custom trained weights.
        **kwargs: Additional arguments for BasketballDetector.
        
    Returns:
        Configured BasketballDetector instance.
    """
    model_path = custom_weights if custom_weights else f"{model_type}.pt"
    return BasketballDetector(model_path=model_path, **kwargs)
