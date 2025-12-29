"""
Pose Estimation Module using YOLOv8-Pose.

This module provides human pose estimation for analyzing
basketball player movements and shooting techniques.
"""

import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import math

import cv2
import numpy as np


@dataclass
class Keypoint:
    """Represents a single body keypoint."""
    name: str
    x: float
    y: float
    confidence: float


@dataclass
class Pose:
    """Represents a complete human pose."""
    keypoints: Dict[str, Keypoint]
    bbox: Tuple[int, int, int, int]
    confidence: float
    person_id: Optional[int] = None


class PoseEstimator:
    """
    YOLOv8-Pose based human pose estimator for basketball training.
    
    Estimates 17 body keypoints following COCO keypoint format:
    - nose, left_eye, right_eye, left_ear, right_ear
    - left_shoulder, right_shoulder, left_elbow, right_elbow
    - left_wrist, right_wrist, left_hip, right_hip
    - left_knee, right_knee, left_ankle, right_ankle
    """
    
    # COCO keypoint names
    KEYPOINT_NAMES = [
        'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
        'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
        'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
    ]
    
    # Skeleton connections for visualization
    SKELETON = [
        (0, 1), (0, 2), (1, 3), (2, 4),  # Head
        (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # Arms
        (5, 11), (6, 12), (11, 12),  # Torso
        (11, 13), (13, 15), (12, 14), (14, 16)  # Legs
    ]
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = 0.5,
        device: str = 'auto'
    ):
        """
        Initialize the pose estimator.
        
        Args:
            model_path: Path to custom YOLOv8-pose model. If None, uses pre-trained.
            conf_threshold: Confidence threshold for detections.
            device: Device to run inference on.
        """
        self.conf_threshold = conf_threshold
        self.device = device
        self.model = None
        self.model_path = model_path
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the YOLOv8-pose model."""
        try:
            from ultralytics import YOLO
            
            if self.model_path and os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
            else:
                # Use pre-trained YOLOv8n-pose for pose estimation
                self.model = YOLO('yolov8n-pose.pt')
            
            if self.device == 'auto':
                import torch
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                
        except ImportError:
            print("Warning: ultralytics not installed. Using mock estimator.")
            self.model = None
    
    def estimate(self, frame: np.ndarray) -> List[Pose]:
        """
        Estimate poses in a single frame.
        
        Args:
            frame: BGR image as numpy array.
            
        Returns:
            List of Pose objects.
        """
        if self.model is None:
            return []
        
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False
        )
        
        poses = []
        for result in results:
            if result.keypoints is None:
                continue
                
            boxes = result.boxes
            keypoints_data = result.keypoints
            
            for i, (box, kpts) in enumerate(zip(boxes, keypoints_data)):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                
                # Parse keypoints
                kpts_xy = kpts.xy[0].cpu().numpy()  # Shape: (17, 2)
                kpts_conf = kpts.conf[0].cpu().numpy() if kpts.conf is not None else np.ones(17)
                
                keypoints = {}
                for j, name in enumerate(self.KEYPOINT_NAMES):
                    keypoints[name] = Keypoint(
                        name=name,
                        x=float(kpts_xy[j, 0]),
                        y=float(kpts_xy[j, 1]),
                        confidence=float(kpts_conf[j])
                    )
                
                poses.append(Pose(
                    keypoints=keypoints,
                    bbox=(x1, y1, x2, y2),
                    confidence=conf,
                    person_id=i
                ))
        
        return poses
    
    def estimate_with_tracking(self, frame: np.ndarray) -> List[Pose]:
        """
        Estimate poses with person tracking.
        
        Args:
            frame: BGR image as numpy array.
            
        Returns:
            List of Pose objects with tracking IDs.
        """
        if self.model is None:
            return []
        
        results = self.model.track(
            frame,
            conf=self.conf_threshold,
            tracker='bytetrack.yaml',
            persist=True,
            verbose=False
        )
        
        poses = []
        for result in results:
            if result.keypoints is None:
                continue
                
            boxes = result.boxes
            keypoints_data = result.keypoints
            
            track_ids = boxes.id.cpu().numpy() if boxes.id is not None else range(len(boxes))
            
            for i, (box, kpts, track_id) in enumerate(zip(boxes, keypoints_data, track_ids)):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                
                kpts_xy = kpts.xy[0].cpu().numpy()
                kpts_conf = kpts.conf[0].cpu().numpy() if kpts.conf is not None else np.ones(17)
                
                keypoints = {}
                for j, name in enumerate(self.KEYPOINT_NAMES):
                    keypoints[name] = Keypoint(
                        name=name,
                        x=float(kpts_xy[j, 0]),
                        y=float(kpts_xy[j, 1]),
                        confidence=float(kpts_conf[j])
                    )
                
                poses.append(Pose(
                    keypoints=keypoints,
                    bbox=(x1, y1, x2, y2),
                    confidence=conf,
                    person_id=int(track_id)
                ))
        
        return poses
    
    def calculate_angle(
        self,
        pose: Pose,
        point1: str,
        point2: str,
        point3: str
    ) -> Optional[float]:
        """
        Calculate angle between three keypoints.
        
        Args:
            pose: Pose object containing keypoints.
            point1: Name of first keypoint.
            point2: Name of vertex keypoint.
            point3: Name of third keypoint.
            
        Returns:
            Angle in degrees, or None if keypoints not detected.
        """
        kp1 = pose.keypoints.get(point1)
        kp2 = pose.keypoints.get(point2)
        kp3 = pose.keypoints.get(point3)
        
        if not all([kp1, kp2, kp3]):
            return None
        
        # Check confidence threshold
        min_conf = 0.3
        if any(kp.confidence < min_conf for kp in [kp1, kp2, kp3]):
            return None
        
        # Calculate vectors
        v1 = np.array([kp1.x - kp2.x, kp1.y - kp2.y])
        v2 = np.array([kp3.x - kp2.x, kp3.y - kp2.y])
        
        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        
        return np.degrees(angle)
    
    def get_shooting_arm_angles(self, pose: Pose, shooting_hand: str = 'right') -> Dict[str, Optional[float]]:
        """
        Get key angles for shooting arm analysis.
        
        Args:
            pose: Pose object.
            shooting_hand: 'left' or 'right'.
            
        Returns:
            Dictionary with elbow and shoulder angles.
        """
        if shooting_hand == 'right':
            shoulder = 'right_shoulder'
            elbow = 'right_elbow'
            wrist = 'right_wrist'
            hip = 'right_hip'
        else:
            shoulder = 'left_shoulder'
            elbow = 'left_elbow'
            wrist = 'left_wrist'
            hip = 'left_hip'
        
        return {
            'elbow_angle': self.calculate_angle(pose, shoulder, elbow, wrist),
            'shoulder_angle': self.calculate_angle(pose, hip, shoulder, elbow),
            'wrist_elevation': self._calculate_wrist_elevation(pose, wrist, shoulder)
        }
    
    def _calculate_wrist_elevation(
        self,
        pose: Pose,
        wrist: str,
        shoulder: str
    ) -> Optional[float]:
        """Calculate wrist elevation relative to shoulder."""
        wrist_kp = pose.keypoints.get(wrist)
        shoulder_kp = pose.keypoints.get(shoulder)
        
        if not wrist_kp or not shoulder_kp:
            return None
        
        if wrist_kp.confidence < 0.3 or shoulder_kp.confidence < 0.3:
            return None
        
        # Positive means wrist is above shoulder (in image coordinates, y increases downward)
        return shoulder_kp.y - wrist_kp.y
    
    def get_knee_bend_angle(self, pose: Pose, side: str = 'right') -> Optional[float]:
        """
        Get knee bend angle for shooting stance analysis.
        
        Args:
            pose: Pose object.
            side: 'left' or 'right'.
            
        Returns:
            Knee angle in degrees.
        """
        hip = f'{side}_hip'
        knee = f'{side}_knee'
        ankle = f'{side}_ankle'
        
        return self.calculate_angle(pose, hip, knee, ankle)
    
    def draw_pose(
        self,
        frame: np.ndarray,
        pose: Pose,
        show_angles: bool = False,
        color: Tuple[int, int, int] = (0, 255, 0)
    ) -> np.ndarray:
        """
        Draw pose skeleton on frame.
        
        Args:
            frame: BGR image as numpy array.
            pose: Pose object to draw.
            show_angles: Whether to show joint angles.
            color: Color for skeleton lines.
            
        Returns:
            Frame with drawn pose.
        """
        result_frame = frame.copy()
        
        # Draw skeleton lines
        for start_idx, end_idx in self.SKELETON:
            start_name = self.KEYPOINT_NAMES[start_idx]
            end_name = self.KEYPOINT_NAMES[end_idx]
            
            start_kp = pose.keypoints.get(start_name)
            end_kp = pose.keypoints.get(end_name)
            
            if start_kp and end_kp:
                if start_kp.confidence > 0.3 and end_kp.confidence > 0.3:
                    start_pt = (int(start_kp.x), int(start_kp.y))
                    end_pt = (int(end_kp.x), int(end_kp.y))
                    cv2.line(result_frame, start_pt, end_pt, color, 2)
        
        # Draw keypoints
        for name, kp in pose.keypoints.items():
            if kp.confidence > 0.3:
                pt = (int(kp.x), int(kp.y))
                cv2.circle(result_frame, pt, 4, (0, 0, 255), -1)
        
        # Draw angles if requested
        if show_angles:
            angles = self.get_shooting_arm_angles(pose)
            y_offset = pose.bbox[1] - 10
            for name, angle in angles.items():
                if angle is not None:
                    text = f"{name}: {angle:.1f}"
                    cv2.putText(
                        result_frame, text,
                        (pose.bbox[0], y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 1
                    )
                    y_offset -= 20
        
        return result_frame
    
    def draw_poses(
        self,
        frame: np.ndarray,
        poses: List[Pose],
        show_angles: bool = False
    ) -> np.ndarray:
        """
        Draw multiple poses on frame.
        
        Args:
            frame: BGR image as numpy array.
            poses: List of Pose objects.
            show_angles: Whether to show joint angles.
            
        Returns:
            Frame with drawn poses.
        """
        result_frame = frame.copy()
        
        colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        
        for i, pose in enumerate(poses):
            color = colors[i % len(colors)]
            result_frame = self.draw_pose(result_frame, pose, show_angles, color)
        
        return result_frame


def create_pose_estimator(
    model_type: str = 'yolov8n-pose',
    **kwargs
) -> PoseEstimator:
    """
    Factory function to create a pose estimator.
    
    Args:
        model_type: Type of YOLOv8-pose model.
        **kwargs: Additional arguments for PoseEstimator.
        
    Returns:
        Configured PoseEstimator instance.
    """
    model_path = f"{model_type}.pt"
    return PoseEstimator(model_path=model_path, **kwargs)
