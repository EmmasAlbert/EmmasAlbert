"""
Unit tests for pose estimator module.
"""

import pytest
import numpy as np

from basketball_training_system.backend.models.pose_estimator import (
    PoseEstimator,
    Pose,
    Keypoint,
    create_pose_estimator
)


class TestKeypoint:
    """Tests for Keypoint dataclass."""
    
    def test_keypoint_creation(self):
        """Test Keypoint object creation."""
        kp = Keypoint(
            name='right_elbow',
            x=150.5,
            y=200.3,
            confidence=0.92
        )
        
        assert kp.name == 'right_elbow'
        assert kp.x == 150.5
        assert kp.y == 200.3
        assert kp.confidence == 0.92


class TestPose:
    """Tests for Pose dataclass."""
    
    def test_pose_creation(self):
        """Test Pose object creation."""
        keypoints = {
            'right_elbow': Keypoint('right_elbow', 150, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 180, 250, 0.85)
        }
        
        pose = Pose(
            keypoints=keypoints,
            bbox=(100, 50, 300, 400),
            confidence=0.88,
            person_id=1
        )
        
        assert len(pose.keypoints) == 2
        assert pose.bbox == (100, 50, 300, 400)
        assert pose.confidence == 0.88
        assert pose.person_id == 1


class TestPoseEstimator:
    """Tests for PoseEstimator class."""
    
    def test_estimator_initialization(self):
        """Test pose estimator initialization."""
        estimator = PoseEstimator()
        assert estimator is not None
        assert estimator.conf_threshold == 0.5
    
    def test_keypoint_names(self):
        """Test COCO keypoint names are defined."""
        assert len(PoseEstimator.KEYPOINT_NAMES) == 17
        assert 'nose' in PoseEstimator.KEYPOINT_NAMES
        assert 'right_elbow' in PoseEstimator.KEYPOINT_NAMES
        assert 'left_knee' in PoseEstimator.KEYPOINT_NAMES
    
    def test_skeleton_connections(self):
        """Test skeleton connections are defined."""
        assert len(PoseEstimator.SKELETON) > 0
        # All indices should be within keypoint range
        for start, end in PoseEstimator.SKELETON:
            assert 0 <= start < 17
            assert 0 <= end < 17
    
    def test_calculate_angle(self):
        """Test angle calculation between keypoints."""
        estimator = PoseEstimator()
        
        # Create a pose with known keypoints forming a 90-degree angle
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 0, 0, 0.9),
            'right_elbow': Keypoint('right_elbow', 100, 0, 0.9),
            'right_wrist': Keypoint('right_wrist', 100, 100, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(0, 0, 200, 200), confidence=0.9)
        
        angle = estimator.calculate_angle(
            pose, 'right_shoulder', 'right_elbow', 'right_wrist'
        )
        
        assert angle is not None
        assert abs(angle - 90) < 1  # Should be approximately 90 degrees
    
    def test_calculate_angle_missing_keypoint(self):
        """Test angle calculation returns None for missing keypoints."""
        estimator = PoseEstimator()
        
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 0, 0, 0.9),
            'right_elbow': Keypoint('right_elbow', 100, 0, 0.9)
            # Missing right_wrist
        }
        
        pose = Pose(keypoints=keypoints, bbox=(0, 0, 200, 200), confidence=0.9)
        
        angle = estimator.calculate_angle(
            pose, 'right_shoulder', 'right_elbow', 'right_wrist'
        )
        
        assert angle is None
    
    def test_calculate_angle_low_confidence(self):
        """Test angle calculation returns None for low confidence keypoints."""
        estimator = PoseEstimator()
        
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 0, 0, 0.9),
            'right_elbow': Keypoint('right_elbow', 100, 0, 0.1),  # Low confidence
            'right_wrist': Keypoint('right_wrist', 100, 100, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(0, 0, 200, 200), confidence=0.9)
        
        angle = estimator.calculate_angle(
            pose, 'right_shoulder', 'right_elbow', 'right_wrist'
        )
        
        assert angle is None
    
    def test_get_shooting_arm_angles_right(self):
        """Test getting shooting arm angles for right hand."""
        estimator = PoseEstimator()
        
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 150, 0.9),
            'right_elbow': Keypoint('right_elbow', 250, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 280, 150, 0.9),
            'right_hip': Keypoint('right_hip', 200, 300, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 100, 400, 500), confidence=0.9)
        
        angles = estimator.get_shooting_arm_angles(pose, 'right')
        
        assert 'elbow_angle' in angles
        assert 'shoulder_angle' in angles
        assert 'wrist_elevation' in angles
    
    def test_get_knee_bend_angle(self):
        """Test knee bend angle calculation."""
        estimator = PoseEstimator()
        
        keypoints = {
            'right_hip': Keypoint('right_hip', 200, 200, 0.9),
            'right_knee': Keypoint('right_knee', 200, 350, 0.9),
            'right_ankle': Keypoint('right_ankle', 200, 500, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 100, 400, 600), confidence=0.9)
        
        angle = estimator.get_knee_bend_angle(pose, 'right')
        
        assert angle is not None
        assert abs(angle - 180) < 1  # Straight leg
    
    def test_draw_pose(self):
        """Test drawing pose on frame."""
        estimator = PoseEstimator()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 300, 150, 0.9),
            'right_elbow': Keypoint('right_elbow', 350, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 380, 150, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(200, 100, 450, 400), confidence=0.9)
        
        result = estimator.draw_pose(frame, pose)
        
        assert result.shape == frame.shape
        # Check that some pixels were modified
        assert not np.array_equal(result, frame)


class TestCreatePoseEstimator:
    """Tests for create_pose_estimator factory function."""
    
    def test_create_default_estimator(self):
        """Test creating estimator with defaults."""
        estimator = create_pose_estimator()
        assert isinstance(estimator, PoseEstimator)
