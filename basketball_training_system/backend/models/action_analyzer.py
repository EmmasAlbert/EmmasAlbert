"""
Action Analyzer Module for Basketball Training.

This module analyzes basketball actions (shooting, dribbling, defense)
by combining object detection and pose estimation results.
"""

import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

import numpy as np

from .detector import Detection
from .pose_estimator import Pose


class ActionType(Enum):
    """Types of basketball actions."""
    IDLE = "idle"
    SHOOTING = "shooting"
    DRIBBLING = "dribbling"
    PASSING = "passing"
    DEFENDING = "defending"
    UNKNOWN = "unknown"


class ShootingPhase(Enum):
    """Phases of a shooting motion."""
    PREPARATION = "preparation"
    LOADING = "loading"
    RELEASE = "release"
    FOLLOW_THROUGH = "follow_through"


@dataclass
class ActionAnalysisResult:
    """Result of action analysis."""
    action_type: ActionType
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class ShootingAnalysis:
    """Detailed analysis of a shooting action."""
    phase: ShootingPhase
    elbow_angle: Optional[float] = None
    shoulder_angle: Optional[float] = None
    knee_angle: Optional[float] = None
    wrist_elevation: Optional[float] = None
    ball_height: Optional[float] = None
    release_detected: bool = False
    quality_score: float = 0.0
    feedback: List[str] = field(default_factory=list)


class ActionAnalyzer:
    """
    Analyzer for basketball actions using detection and pose data.
    
    Combines object detection (basketball position) and pose estimation
    (player body position) to identify and analyze basketball actions.
    """
    
    # Ideal shooting form parameters (can be customized)
    IDEAL_SHOOTING_FORM = {
        'elbow_angle_range': (85, 105),  # degrees at release
        'shoulder_angle_range': (80, 120),  # degrees
        'knee_angle_range': (140, 170),  # degrees at release
        'wrist_above_shoulder': True
    }
    
    def __init__(
        self,
        history_length: int = 30,
        shooting_hand: str = 'right'
    ):
        """
        Initialize the action analyzer.
        
        Args:
            history_length: Number of frames to keep in history.
            shooting_hand: Default shooting hand ('left' or 'right').
        """
        self.history_length = history_length
        self.shooting_hand = shooting_hand
        
        # History buffers for temporal analysis
        self.pose_history: deque = deque(maxlen=history_length)
        self.ball_history: deque = deque(maxlen=history_length)
        self.action_history: deque = deque(maxlen=history_length)
        
        # State tracking
        self.current_action = ActionType.IDLE
        self.shooting_in_progress = False
        self.last_release_frame = -1
    
    def analyze_frame(
        self,
        poses: List[Pose],
        ball_detection: Optional[Detection],
        frame_number: int = 0
    ) -> ActionAnalysisResult:
        """
        Analyze a single frame to determine current action.
        
        Args:
            poses: List of detected poses.
            ball_detection: Basketball detection (if any).
            frame_number: Current frame number.
            
        Returns:
            ActionAnalysisResult with detected action and details.
        """
        # Update history
        self.pose_history.append(poses)
        self.ball_history.append(ball_detection)
        
        if not poses:
            return ActionAnalysisResult(
                action_type=ActionType.UNKNOWN,
                confidence=0.0,
                details={'reason': 'No pose detected'}
            )
        
        # Get primary player (closest to ball or largest bbox)
        primary_pose = self._get_primary_player(poses, ball_detection)
        
        # Analyze possible actions
        shooting_conf = self._analyze_shooting_posture(primary_pose, ball_detection)
        dribbling_conf = self._analyze_dribbling(primary_pose, ball_detection)
        
        # Determine most likely action
        if shooting_conf > 0.6:
            action_type = ActionType.SHOOTING
            confidence = shooting_conf
            details = self._get_shooting_details(primary_pose, ball_detection, frame_number)
        elif dribbling_conf > 0.5:
            action_type = ActionType.DRIBBLING
            confidence = dribbling_conf
            details = {'ball_near_hands': True}
        else:
            action_type = ActionType.IDLE
            confidence = 0.8
            details = {}
        
        result = ActionAnalysisResult(
            action_type=action_type,
            confidence=confidence,
            details=details
        )
        
        self.action_history.append(result)
        self.current_action = action_type
        
        return result
    
    def _get_primary_player(
        self,
        poses: List[Pose],
        ball_detection: Optional[Detection]
    ) -> Pose:
        """Get the primary player to analyze (closest to ball or largest)."""
        if len(poses) == 1:
            return poses[0]
        
        if ball_detection:
            # Find player closest to ball
            ball_center = ball_detection.center
            min_dist = float('inf')
            closest_pose = poses[0]
            
            for pose in poses:
                # Use wrist position for distance calculation
                wrist = pose.keypoints.get(f'{self.shooting_hand}_wrist')
                if wrist and wrist.confidence > 0.3:
                    dist = np.sqrt(
                        (wrist.x - ball_center[0])**2 +
                        (wrist.y - ball_center[1])**2
                    )
                    if dist < min_dist:
                        min_dist = dist
                        closest_pose = pose
            
            return closest_pose
        
        # Return pose with largest bounding box
        return max(poses, key=lambda p: (p.bbox[2] - p.bbox[0]) * (p.bbox[3] - p.bbox[1]))
    
    def _analyze_shooting_posture(
        self,
        pose: Pose,
        ball_detection: Optional[Detection]
    ) -> float:
        """
        Analyze if pose indicates shooting posture.
        
        Returns confidence score for shooting action.
        """
        score = 0.0
        factors = 0
        
        # Check wrist elevation
        wrist = pose.keypoints.get(f'{self.shooting_hand}_wrist')
        shoulder = pose.keypoints.get(f'{self.shooting_hand}_shoulder')
        
        if wrist and shoulder and wrist.confidence > 0.3 and shoulder.confidence > 0.3:
            factors += 1
            # Wrist above shoulder suggests shooting
            if wrist.y < shoulder.y:
                score += 1.0
            elif wrist.y < shoulder.y + 50:  # Near shoulder level
                score += 0.5
        
        # Check elbow angle
        elbow = pose.keypoints.get(f'{self.shooting_hand}_elbow')
        if wrist and elbow and shoulder:
            if all(kp.confidence > 0.3 for kp in [wrist, elbow, shoulder]):
                factors += 1
                # Calculate elbow angle
                v1 = np.array([shoulder.x - elbow.x, shoulder.y - elbow.y])
                v2 = np.array([wrist.x - elbow.x, wrist.y - elbow.y])
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
                
                # Shooting typically has elbow angle between 70-120 degrees
                if 70 <= angle <= 120:
                    score += 1.0
                elif 50 <= angle <= 140:
                    score += 0.5
        
        # Check ball position relative to player
        if ball_detection and wrist:
            factors += 1
            ball_center = ball_detection.center
            dist = np.sqrt((wrist.x - ball_center[0])**2 + (wrist.y - ball_center[1])**2)
            
            # Ball should be near hands for shooting
            if dist < 100:
                score += 1.0
            elif dist < 200:
                score += 0.5
        
        return score / max(factors, 1)
    
    def _analyze_dribbling(
        self,
        pose: Pose,
        ball_detection: Optional[Detection]
    ) -> float:
        """Analyze if pose indicates dribbling."""
        if not ball_detection:
            return 0.0
        
        score = 0.0
        
        # Check ball is below waist level
        hip = pose.keypoints.get(f'{self.shooting_hand}_hip')
        if hip and hip.confidence > 0.3:
            ball_y = ball_detection.center[1]
            if ball_y > hip.y:  # Ball below hip
                score += 0.5
        
        # Check ball history for bouncing pattern
        if len(self.ball_history) >= 5:
            ball_positions = [
                b.center[1] for b in self.ball_history if b is not None
            ]
            if len(ball_positions) >= 5:
                # Check for oscillation (dribbling pattern)
                diffs = np.diff(ball_positions)
                sign_changes = np.sum(np.abs(np.diff(np.sign(diffs))) > 0)
                if sign_changes >= 2:
                    score += 0.5
        
        return score
    
    def _get_shooting_details(
        self,
        pose: Pose,
        ball_detection: Optional[Detection],
        frame_number: int
    ) -> Dict[str, Any]:
        """Get detailed shooting analysis."""
        details = {}
        
        # Determine shooting phase
        phase = self._determine_shooting_phase(pose, ball_detection)
        details['phase'] = phase.value
        
        # Get arm angles
        side = self.shooting_hand
        wrist = pose.keypoints.get(f'{side}_wrist')
        elbow = pose.keypoints.get(f'{side}_elbow')
        shoulder = pose.keypoints.get(f'{side}_shoulder')
        hip = pose.keypoints.get(f'{side}_hip')
        
        if all(kp and kp.confidence > 0.3 for kp in [wrist, elbow, shoulder]):
            # Elbow angle
            v1 = np.array([shoulder.x - elbow.x, shoulder.y - elbow.y])
            v2 = np.array([wrist.x - elbow.x, wrist.y - elbow.y])
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            elbow_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
            details['elbow_angle'] = round(elbow_angle, 1)
        
        if all(kp and kp.confidence > 0.3 for kp in [elbow, shoulder, hip]):
            # Shoulder angle
            v1 = np.array([hip.x - shoulder.x, hip.y - shoulder.y])
            v2 = np.array([elbow.x - shoulder.x, elbow.y - shoulder.y])
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            shoulder_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
            details['shoulder_angle'] = round(shoulder_angle, 1)
        
        # Get knee angle
        knee = pose.keypoints.get(f'{side}_knee')
        ankle = pose.keypoints.get(f'{side}_ankle')
        
        if all(kp and kp.confidence > 0.3 for kp in [hip, knee, ankle]):
            v1 = np.array([hip.x - knee.x, hip.y - knee.y])
            v2 = np.array([ankle.x - knee.x, ankle.y - knee.y])
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            knee_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
            details['knee_angle'] = round(knee_angle, 1)
        
        # Ball height
        if ball_detection:
            details['ball_position'] = ball_detection.center
        
        return details
    
    def _determine_shooting_phase(
        self,
        pose: Pose,
        ball_detection: Optional[Detection]
    ) -> ShootingPhase:
        """Determine current phase of shooting motion."""
        wrist = pose.keypoints.get(f'{self.shooting_hand}_wrist')
        shoulder = pose.keypoints.get(f'{self.shooting_hand}_shoulder')
        
        if not wrist or not shoulder:
            return ShootingPhase.PREPARATION
        
        if wrist.confidence < 0.3 or shoulder.confidence < 0.3:
            return ShootingPhase.PREPARATION
        
        # Use wrist position relative to shoulder to determine phase
        wrist_elevation = shoulder.y - wrist.y
        
        if wrist_elevation < 0:  # Wrist below shoulder
            return ShootingPhase.PREPARATION
        elif wrist_elevation < 50:
            return ShootingPhase.LOADING
        elif wrist_elevation < 150:
            return ShootingPhase.RELEASE
        else:
            return ShootingPhase.FOLLOW_THROUGH
    
    def analyze_shooting_form(self, pose: Pose) -> ShootingAnalysis:
        """
        Perform detailed analysis of shooting form.
        
        Args:
            pose: Pose at shooting release moment.
            
        Returns:
            ShootingAnalysis with quality score and feedback.
        """
        analysis = ShootingAnalysis(
            phase=self._determine_shooting_phase(pose, None)
        )
        
        side = self.shooting_hand
        quality_factors = []
        
        # Get keypoints
        wrist = pose.keypoints.get(f'{side}_wrist')
        elbow = pose.keypoints.get(f'{side}_elbow')
        shoulder = pose.keypoints.get(f'{side}_shoulder')
        hip = pose.keypoints.get(f'{side}_hip')
        knee = pose.keypoints.get(f'{side}_knee')
        ankle = pose.keypoints.get(f'{side}_ankle')
        
        # Analyze elbow angle
        if all(kp and kp.confidence > 0.3 for kp in [wrist, elbow, shoulder]):
            v1 = np.array([shoulder.x - elbow.x, shoulder.y - elbow.y])
            v2 = np.array([wrist.x - elbow.x, wrist.y - elbow.y])
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            analysis.elbow_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
            
            min_angle, max_angle = self.IDEAL_SHOOTING_FORM['elbow_angle_range']
            if min_angle <= analysis.elbow_angle <= max_angle:
                quality_factors.append(1.0)
                analysis.feedback.append("✓ 肘部角度良好")
            else:
                deviation = min(abs(analysis.elbow_angle - min_angle), abs(analysis.elbow_angle - max_angle))
                quality_factors.append(max(0, 1 - deviation / 30))
                if analysis.elbow_angle < min_angle:
                    analysis.feedback.append("⚠ 肘部弯曲过多，尝试稍微伸展手臂")
                else:
                    analysis.feedback.append("⚠ 肘部过于伸直，保持适度弯曲")
        
        # Analyze shoulder angle
        if all(kp and kp.confidence > 0.3 for kp in [elbow, shoulder, hip]):
            v1 = np.array([hip.x - shoulder.x, hip.y - shoulder.y])
            v2 = np.array([elbow.x - shoulder.x, elbow.y - shoulder.y])
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            analysis.shoulder_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
            
            min_angle, max_angle = self.IDEAL_SHOOTING_FORM['shoulder_angle_range']
            if min_angle <= analysis.shoulder_angle <= max_angle:
                quality_factors.append(1.0)
                analysis.feedback.append("✓ 肩部位置正确")
            else:
                quality_factors.append(0.5)
                analysis.feedback.append("⚠ 调整肩部角度以获得更好的力量传递")
        
        # Analyze knee bend
        if all(kp and kp.confidence > 0.3 for kp in [hip, knee, ankle]):
            v1 = np.array([hip.x - knee.x, hip.y - knee.y])
            v2 = np.array([ankle.x - knee.x, ankle.y - knee.y])
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            analysis.knee_angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
            
            min_angle, max_angle = self.IDEAL_SHOOTING_FORM['knee_angle_range']
            if min_angle <= analysis.knee_angle <= max_angle:
                quality_factors.append(1.0)
                analysis.feedback.append("✓ 腿部弯曲适当")
            else:
                quality_factors.append(0.6)
                if analysis.knee_angle < min_angle:
                    analysis.feedback.append("⚠ 膝盖弯曲过深，稍微站直一些")
                else:
                    analysis.feedback.append("⚠ 膝盖弯曲不足，增加腿部力量支撑")
        
        # Analyze wrist elevation
        if wrist and shoulder and wrist.confidence > 0.3 and shoulder.confidence > 0.3:
            analysis.wrist_elevation = shoulder.y - wrist.y
            if analysis.wrist_elevation > 0:
                quality_factors.append(1.0)
                analysis.feedback.append("✓ 手腕高度正确")
            else:
                quality_factors.append(0.3)
                analysis.feedback.append("⚠ 手腕需要抬高到肩膀以上")
        
        # Calculate overall quality score
        if quality_factors:
            analysis.quality_score = sum(quality_factors) / len(quality_factors)
        
        return analysis
    
    def detect_release_frame(self) -> Optional[int]:
        """
        Detect the shooting release frame from history.
        
        Returns:
            Frame index of detected release, or None.
        """
        if len(self.ball_history) < 5:
            return None
        
        ball_positions = []
        for i, ball in enumerate(self.ball_history):
            if ball is not None:
                ball_positions.append((i, ball.center[1]))
        
        if len(ball_positions) < 3:
            return None
        
        # Look for upward velocity change (ball leaving hands)
        for i in range(1, len(ball_positions) - 1):
            prev_y = ball_positions[i-1][1]
            curr_y = ball_positions[i][1]
            next_y = ball_positions[i+1][1]
            
            # Ball accelerating upward (y decreasing in image coordinates)
            if curr_y < prev_y and next_y < curr_y:
                # This might be release point
                return ball_positions[i][0]
        
        return None
    
    def get_training_summary(self) -> Dict[str, Any]:
        """
        Get summary of analyzed training session.
        
        Returns:
            Dictionary with session statistics.
        """
        shooting_actions = [
            a for a in self.action_history
            if a.action_type == ActionType.SHOOTING
        ]
        
        summary = {
            'total_frames_analyzed': len(self.action_history),
            'shooting_frames': len(shooting_actions),
            'average_confidence': np.mean([a.confidence for a in shooting_actions]) if shooting_actions else 0,
        }
        
        # Extract angle statistics
        elbow_angles = [
            a.details.get('elbow_angle')
            for a in shooting_actions
            if a.details.get('elbow_angle') is not None
        ]
        
        if elbow_angles:
            summary['elbow_angle_stats'] = {
                'mean': np.mean(elbow_angles),
                'std': np.std(elbow_angles),
                'min': np.min(elbow_angles),
                'max': np.max(elbow_angles)
            }
        
        return summary
    
    def reset(self) -> None:
        """Reset analyzer state for new session."""
        self.pose_history.clear()
        self.ball_history.clear()
        self.action_history.clear()
        self.current_action = ActionType.IDLE
        self.shooting_in_progress = False
        self.last_release_frame = -1
