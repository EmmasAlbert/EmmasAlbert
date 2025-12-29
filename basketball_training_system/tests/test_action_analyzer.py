"""
Unit tests for action analyzer module.
"""

import pytest
import numpy as np

from basketball_training_system.backend.models.action_analyzer import (
    ActionAnalyzer,
    ActionType,
    ShootingPhase,
    ActionAnalysisResult,
    ShootingAnalysis
)
from basketball_training_system.backend.models.pose_estimator import Pose, Keypoint
from basketball_training_system.backend.models.detector import Detection


class TestActionType:
    """Tests for ActionType enum."""
    
    def test_action_types_exist(self):
        """Test all expected action types exist."""
        assert ActionType.IDLE.value == 'idle'
        assert ActionType.SHOOTING.value == 'shooting'
        assert ActionType.DRIBBLING.value == 'dribbling'
        assert ActionType.UNKNOWN.value == 'unknown'


class TestShootingPhase:
    """Tests for ShootingPhase enum."""
    
    def test_shooting_phases_exist(self):
        """Test all expected shooting phases exist."""
        assert ShootingPhase.PREPARATION.value == 'preparation'
        assert ShootingPhase.LOADING.value == 'loading'
        assert ShootingPhase.RELEASE.value == 'release'
        assert ShootingPhase.FOLLOW_THROUGH.value == 'follow_through'


class TestActionAnalyzer:
    """Tests for ActionAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = ActionAnalyzer()
        
        assert analyzer.history_length == 30
        assert analyzer.shooting_hand == 'right'
        assert analyzer.current_action == ActionType.IDLE
    
    def test_analyzer_custom_initialization(self):
        """Test analyzer with custom parameters."""
        analyzer = ActionAnalyzer(history_length=50, shooting_hand='left')
        
        assert analyzer.history_length == 50
        assert analyzer.shooting_hand == 'left'
    
    def test_analyze_frame_no_poses(self):
        """Test analyzing frame with no poses detected."""
        analyzer = ActionAnalyzer()
        
        result = analyzer.analyze_frame(poses=[], ball_detection=None)
        
        assert result.action_type == ActionType.UNKNOWN
        assert result.confidence == 0.0
    
    def test_analyze_frame_with_pose(self):
        """Test analyzing frame with pose detected."""
        analyzer = ActionAnalyzer()
        
        # Create a simple pose
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 200, 0.9),
            'right_elbow': Keypoint('right_elbow', 250, 250, 0.9),
            'right_wrist': Keypoint('right_wrist', 280, 200, 0.9),
            'right_hip': Keypoint('right_hip', 200, 350, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 100, 400, 500), confidence=0.9)
        
        result = analyzer.analyze_frame(poses=[pose], ball_detection=None)
        
        assert result.action_type in [ActionType.IDLE, ActionType.SHOOTING, ActionType.UNKNOWN]
        assert 0 <= result.confidence <= 1
    
    def test_get_primary_player_single(self):
        """Test getting primary player with single pose."""
        analyzer = ActionAnalyzer()
        
        keypoints = {'right_wrist': Keypoint('right_wrist', 100, 100, 0.9)}
        pose = Pose(keypoints=keypoints, bbox=(50, 50, 200, 300), confidence=0.9)
        
        result = analyzer._get_primary_player([pose], None)
        
        assert result == pose
    
    def test_get_primary_player_with_ball(self):
        """Test getting primary player closest to ball."""
        analyzer = ActionAnalyzer()
        
        pose1_keypoints = {'right_wrist': Keypoint('right_wrist', 100, 100, 0.9)}
        pose1 = Pose(keypoints=pose1_keypoints, bbox=(50, 50, 200, 300), confidence=0.9)
        
        pose2_keypoints = {'right_wrist': Keypoint('right_wrist', 400, 400, 0.9)}
        pose2 = Pose(keypoints=pose2_keypoints, bbox=(350, 350, 500, 600), confidence=0.9)
        
        # Ball near pose1
        ball = Detection(0, 'basketball', 0.9, (80, 80, 120, 120), (100, 100))
        
        result = analyzer._get_primary_player([pose1, pose2], ball)
        
        # Should return pose1 as it's closer to the ball
        assert result == pose1
    
    def test_analyze_shooting_posture_wrist_above(self):
        """Test shooting posture analysis with wrist above shoulder."""
        analyzer = ActionAnalyzer()
        
        # Wrist above shoulder - shooting posture
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 220, 100, 0.9),  # Above shoulder
            'right_elbow': Keypoint('right_elbow', 230, 150, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 50, 350, 400), confidence=0.9)
        
        score = analyzer._analyze_shooting_posture(pose, None)
        
        assert score > 0  # Should have positive shooting score
    
    def test_analyze_shooting_posture_wrist_below(self):
        """Test shooting posture analysis with wrist below shoulder."""
        analyzer = ActionAnalyzer()
        
        # Wrist below shoulder - not shooting
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 220, 400, 0.9),  # Below shoulder
            'right_elbow': Keypoint('right_elbow', 230, 300, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 100, 350, 500), confidence=0.9)
        
        score = analyzer._analyze_shooting_posture(pose, None)
        
        assert score < 0.5  # Should have lower shooting score
    
    def test_determine_shooting_phase_preparation(self):
        """Test determining preparation phase."""
        analyzer = ActionAnalyzer()
        
        # Wrist below shoulder
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 220, 300, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 100, 350, 500), confidence=0.9)
        
        phase = analyzer._determine_shooting_phase(pose, None)
        
        assert phase == ShootingPhase.PREPARATION
    
    def test_determine_shooting_phase_release(self):
        """Test determining release phase."""
        analyzer = ActionAnalyzer()
        
        # Wrist well above shoulder
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 200, 0.9),
            'right_wrist': Keypoint('right_wrist', 220, 80, 0.9)  # 120 pixels above shoulder
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 50, 350, 400), confidence=0.9)
        
        phase = analyzer._determine_shooting_phase(pose, None)
        
        assert phase in [ShootingPhase.RELEASE, ShootingPhase.FOLLOW_THROUGH]
    
    def test_analyze_shooting_form(self):
        """Test detailed shooting form analysis."""
        analyzer = ActionAnalyzer()
        
        keypoints = {
            'right_shoulder': Keypoint('right_shoulder', 200, 200, 0.9),
            'right_elbow': Keypoint('right_elbow', 250, 170, 0.9),
            'right_wrist': Keypoint('right_wrist', 280, 100, 0.9),
            'right_hip': Keypoint('right_hip', 200, 350, 0.9),
            'right_knee': Keypoint('right_knee', 200, 450, 0.9),
            'right_ankle': Keypoint('right_ankle', 200, 550, 0.9)
        }
        
        pose = Pose(keypoints=keypoints, bbox=(100, 50, 400, 600), confidence=0.9)
        
        analysis = analyzer.analyze_shooting_form(pose)
        
        assert isinstance(analysis, ShootingAnalysis)
        assert 0 <= analysis.quality_score <= 1
        assert isinstance(analysis.feedback, list)
    
    def test_get_training_summary(self):
        """Test getting training summary."""
        analyzer = ActionAnalyzer()
        
        # Add some mock history
        for _ in range(5):
            result = ActionAnalysisResult(
                action_type=ActionType.SHOOTING,
                confidence=0.8,
                details={'elbow_angle': 95.0}
            )
            analyzer.action_history.append(result)
        
        summary = analyzer.get_training_summary()
        
        assert 'total_frames_analyzed' in summary
        assert 'shooting_frames' in summary
        assert summary['shooting_frames'] == 5
    
    def test_reset(self):
        """Test resetting analyzer state."""
        analyzer = ActionAnalyzer()
        
        # Add some history
        analyzer.pose_history.append([])
        analyzer.ball_history.append(None)
        analyzer.current_action = ActionType.SHOOTING
        
        analyzer.reset()
        
        assert len(analyzer.pose_history) == 0
        assert len(analyzer.ball_history) == 0
        assert analyzer.current_action == ActionType.IDLE
