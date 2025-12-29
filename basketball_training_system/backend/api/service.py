"""
Analyzer Service for Basketball Training System.

Integrates detector, pose estimator, and action analyzer into a unified service.
"""

import os
from typing import Dict, Any, List, Optional

import cv2
import numpy as np

from ..models.detector import BasketballDetector, Detection
from ..models.pose_estimator import PoseEstimator, Pose
from ..models.action_analyzer import ActionAnalyzer, ActionType
from ..utils.video_processor import VideoProcessor
from ..utils.data_analyzer import DataAnalyzer
from ..utils.visualizer import Visualizer


class AnalyzerService:
    """
    Main service class that coordinates all analysis components.
    
    Provides a unified interface for:
    - Video analysis
    - Frame analysis
    - Training session management
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        pose_model_path: Optional[str] = None,
        data_dir: Optional[str] = None,
        conf_threshold: float = 0.5,
        device: str = 'auto'
    ):
        """
        Initialize the analyzer service.
        
        Args:
            model_path: Path to custom detection model.
            pose_model_path: Path to custom pose model.
            data_dir: Directory for storing session data.
            conf_threshold: Confidence threshold for detections.
            device: Device to run inference on.
        """
        self.detector = BasketballDetector(
            model_path=model_path,
            conf_threshold=conf_threshold,
            device=device
        )
        
        self.pose_estimator = PoseEstimator(
            model_path=pose_model_path,
            conf_threshold=conf_threshold,
            device=device
        )
        
        self.action_analyzer = ActionAnalyzer()
        self.data_analyzer = DataAnalyzer(data_dir=data_dir)
        self.visualizer = Visualizer(output_dir=data_dir)
        self.video_processor = VideoProcessor()
    
    def analyze_frame(
        self,
        frame: np.ndarray,
        shooting_hand: str = 'right'
    ) -> Dict[str, Any]:
        """
        Analyze a single frame.
        
        Args:
            frame: BGR image as numpy array.
            shooting_hand: 'left' or 'right'.
            
        Returns:
            Dictionary with detections, poses, and analysis.
        """
        self.action_analyzer.shooting_hand = shooting_hand
        
        # Detect basketball and players
        detections = self.detector.detect(frame)
        
        # Estimate poses
        poses = self.pose_estimator.estimate(frame)
        
        # Find basketball detection
        ball_detection = None
        for det in detections:
            if det.class_name.lower() in ['basketball', 'sports ball']:
                ball_detection = det
                break
        
        # Analyze action
        analysis = self.action_analyzer.analyze_frame(
            poses=poses,
            ball_detection=ball_detection
        )
        
        # Convert to serializable format
        result = {
            'detections': [
                {
                    'class_name': d.class_name,
                    'confidence': d.confidence,
                    'bbox': d.bbox,
                    'center': d.center
                }
                for d in detections
            ],
            'poses': [
                {
                    'bbox': p.bbox,
                    'confidence': p.confidence,
                    'keypoints': {
                        name: {
                            'x': kp.x,
                            'y': kp.y,
                            'confidence': kp.confidence
                        }
                        for name, kp in p.keypoints.items()
                    }
                }
                for p in poses
            ],
            'analysis': {
                'action_type': analysis.action_type.value,
                'confidence': analysis.confidence,
                'details': analysis.details
            }
        }
        
        return result
    
    def analyze_video(
        self,
        video_path: str,
        session_id: str,
        shooting_hand: str = 'right',
        skip_frames: int = 0,
        output_video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a complete training video.
        
        Args:
            video_path: Path to video file.
            session_id: Unique session identifier.
            shooting_hand: 'left' or 'right'.
            skip_frames: Number of frames to skip between analyses.
            output_video_path: Optional path for annotated output video.
            
        Returns:
            Dictionary with session statistics and feedback.
        """
        self.action_analyzer.shooting_hand = shooting_hand
        self.action_analyzer.reset()
        
        # Load video
        video_info = self.video_processor.load_video(video_path)
        
        if output_video_path:
            self.video_processor.create_writer(output_video_path)
        
        shooting_data = []
        frame_results = []
        
        for frame_num, frame in self.video_processor.iterate_frames(skip_frames=skip_frames):
            # Analyze frame
            result = self.analyze_frame(frame, shooting_hand)
            frame_results.append(result)
            
            # Collect shooting data
            if result['analysis']['action_type'] == 'shooting':
                details = result['analysis']['details']
                shooting_data.append({
                    'frame': frame_num,
                    'elbow_angle': details.get('elbow_angle'),
                    'knee_angle': details.get('knee_angle'),
                    'shoulder_angle': details.get('shoulder_angle'),
                    'quality_score': result['analysis']['confidence'],
                    'phase': details.get('phase')
                })
            
            # Write annotated frame if output requested
            if output_video_path:
                annotated = self.visualizer.annotate_frame(
                    frame,
                    detections=result['detections'],
                    poses=result['poses'],
                    analysis=result['analysis']
                )
                self.video_processor.write_frame(annotated)
        
        # Clean up
        self.video_processor.close()
        
        # Analyze session statistics
        session_stats = self.data_analyzer.analyze_session(
            shooting_data=shooting_data,
            session_id=session_id
        )
        
        return {
            'statistics': {
                'total_shots': session_stats.total_shots,
                'shooting_percentage': session_stats.shooting_percentage,
                'average_elbow_angle': session_stats.average_elbow_angle,
                'average_knee_angle': session_stats.average_knee_angle,
                'form_quality_score': session_stats.form_quality_score
            },
            'feedback': session_stats.improvements + session_stats.areas_to_work,
            'improvements': session_stats.improvements,
            'areas_to_work': session_stats.areas_to_work,
            'details': {
                'video_info': {
                    'width': video_info.width,
                    'height': video_info.height,
                    'fps': video_info.fps,
                    'duration': video_info.duration
                },
                'frames_analyzed': len(frame_results)
            }
        }
    
    def get_annotated_frame(
        self,
        frame: np.ndarray,
        shooting_hand: str = 'right',
        show_angles: bool = True,
        show_feedback: bool = True
    ) -> np.ndarray:
        """
        Get an annotated frame with all analysis visualizations.
        
        Args:
            frame: BGR image as numpy array.
            shooting_hand: 'left' or 'right'.
            show_angles: Whether to show angle measurements.
            show_feedback: Whether to show feedback text.
            
        Returns:
            Annotated frame.
        """
        result = self.analyze_frame(frame, shooting_hand)
        
        return self.visualizer.annotate_frame(
            frame,
            detections=result['detections'],
            poses=result['poses'],
            analysis=result['analysis'],
            show_angles=show_angles,
            show_feedback=show_feedback
        )
    
    def analyze_shooting_form(
        self,
        frame: np.ndarray,
        shooting_hand: str = 'right'
    ) -> Dict[str, Any]:
        """
        Perform detailed shooting form analysis on a single frame.
        
        Args:
            frame: BGR image as numpy array.
            shooting_hand: 'left' or 'right'.
            
        Returns:
            Detailed shooting form analysis.
        """
        poses = self.pose_estimator.estimate(frame)
        
        if not poses:
            return {
                'error': '未检测到人体姿态',
                'quality_score': 0.0,
                'feedback': ['请确保人物完整出现在画面中']
            }
        
        self.action_analyzer.shooting_hand = shooting_hand
        analysis = self.action_analyzer.analyze_shooting_form(poses[0])
        
        return {
            'phase': analysis.phase.value,
            'elbow_angle': analysis.elbow_angle,
            'shoulder_angle': analysis.shoulder_angle,
            'knee_angle': analysis.knee_angle,
            'wrist_elevation': analysis.wrist_elevation,
            'quality_score': analysis.quality_score,
            'feedback': analysis.feedback
        }


def create_service(
    model_path: Optional[str] = None,
    pose_model_path: Optional[str] = None,
    data_dir: Optional[str] = None,
    **kwargs
) -> AnalyzerService:
    """
    Factory function to create an analyzer service.
    
    Args:
        model_path: Path to custom detection model.
        pose_model_path: Path to custom pose model.
        data_dir: Directory for storing session data.
        **kwargs: Additional arguments for AnalyzerService.
        
    Returns:
        Configured AnalyzerService instance.
    """
    return AnalyzerService(
        model_path=model_path,
        pose_model_path=pose_model_path,
        data_dir=data_dir,
        **kwargs
    )
