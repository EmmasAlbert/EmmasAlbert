"""
Visualization Module for Basketball Training System.

Provides visualization tools for training data analysis and feedback.
"""

from typing import List, Dict, Any, Optional, Tuple
import os
from datetime import datetime

import cv2
import numpy as np

# Try to import matplotlib for charts
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class Visualizer:
    """
    Visualization tools for basketball training analysis.
    
    Provides:
    - Frame annotation with detections and poses
    - Training progress charts
    - Angle distribution plots
    - Performance dashboards
    """
    
    # Color schemes
    COLORS = {
        'basketball': (0, 165, 255),  # Orange
        'player': (0, 255, 0),        # Green
        'skeleton': (255, 255, 0),    # Cyan
        'text': (255, 255, 255),      # White
        'good': (0, 255, 0),          # Green
        'warning': (0, 255, 255),     # Yellow
        'bad': (0, 0, 255)            # Red
    }
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize visualizer.
        
        Args:
            output_dir: Directory to save visualizations.
        """
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
    
    def annotate_frame(
        self,
        frame: np.ndarray,
        detections: Optional[List[Dict]] = None,
        poses: Optional[List[Dict]] = None,
        analysis: Optional[Dict] = None,
        show_angles: bool = True,
        show_feedback: bool = True
    ) -> np.ndarray:
        """
        Annotate frame with detections, poses, and analysis.
        
        Args:
            frame: BGR image as numpy array.
            detections: List of detection dictionaries.
            poses: List of pose dictionaries.
            analysis: Analysis result dictionary.
            show_angles: Whether to show angle measurements.
            show_feedback: Whether to show feedback text.
            
        Returns:
            Annotated frame.
        """
        result = frame.copy()
        
        # Draw detections
        if detections:
            for det in detections:
                bbox = det.get('bbox') or det.get('bounding_box')
                if bbox:
                    x1, y1, x2, y2 = bbox
                    class_name = det.get('class_name', det.get('class', 'object'))
                    color = self.COLORS.get(class_name.lower(), (255, 255, 255))
                    
                    cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
                    
                    label = class_name
                    if 'confidence' in det:
                        label += f" {det['confidence']:.2f}"
                    
                    cv2.putText(
                        result, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
                    )
        
        # Draw poses
        if poses:
            for pose in poses:
                result = self._draw_pose(result, pose, show_angles)
        
        # Draw analysis feedback
        if analysis and show_feedback:
            result = self._draw_feedback(result, analysis)
        
        return result
    
    def _draw_pose(
        self,
        frame: np.ndarray,
        pose: Dict,
        show_angles: bool
    ) -> np.ndarray:
        """Draw pose skeleton on frame."""
        result = frame.copy()
        
        keypoints = pose.get('keypoints', {})
        
        # Skeleton connections
        skeleton = [
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_elbow'),
            ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'),
            ('right_elbow', 'right_wrist'),
            ('left_shoulder', 'left_hip'),
            ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            ('left_hip', 'left_knee'),
            ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'),
            ('right_knee', 'right_ankle')
        ]
        
        # Draw skeleton lines
        for start, end in skeleton:
            if start in keypoints and end in keypoints:
                start_kp = keypoints[start]
                end_kp = keypoints[end]
                
                if start_kp.get('confidence', 1) > 0.3 and end_kp.get('confidence', 1) > 0.3:
                    pt1 = (int(start_kp['x']), int(start_kp['y']))
                    pt2 = (int(end_kp['x']), int(end_kp['y']))
                    cv2.line(result, pt1, pt2, self.COLORS['skeleton'], 2)
        
        # Draw keypoints
        for name, kp in keypoints.items():
            if kp.get('confidence', 1) > 0.3:
                pt = (int(kp['x']), int(kp['y']))
                cv2.circle(result, pt, 5, (0, 0, 255), -1)
        
        # Draw angles if requested
        if show_angles and 'angles' in pose:
            y_offset = pose.get('bbox', [0, 50, 0, 0])[1] - 10
            for angle_name, angle_value in pose['angles'].items():
                if angle_value is not None:
                    text = f"{angle_name}: {angle_value:.1f}°"
                    cv2.putText(
                        result, text, (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        self.COLORS['text'], 2
                    )
                    y_offset += 25
        
        return result
    
    def _draw_feedback(
        self,
        frame: np.ndarray,
        analysis: Dict
    ) -> np.ndarray:
        """Draw analysis feedback on frame."""
        result = frame.copy()
        
        # Draw action type
        action = analysis.get('action_type', 'unknown')
        confidence = analysis.get('confidence', 0)
        
        action_text = f"动作: {self._translate_action(action)} ({confidence:.0%})"
        cv2.putText(
            result, action_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            self.COLORS['text'], 2
        )
        
        # Draw quality score if available
        quality = analysis.get('details', {}).get('quality_score')
        if quality is not None:
            color = self._get_quality_color(quality)
            quality_text = f"姿势评分: {quality:.0%}"
            cv2.putText(
                result, quality_text, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                color, 2
            )
        
        # Draw feedback messages
        feedback = analysis.get('details', {}).get('feedback', [])
        y = 100
        for msg in feedback[:5]:  # Limit to 5 messages
            cv2.putText(
                result, msg, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                self.COLORS['text'], 1
            )
            y += 25
        
        return result
    
    def _translate_action(self, action: str) -> str:
        """Translate action type to Chinese."""
        translations = {
            'idle': '待机',
            'shooting': '投篮',
            'dribbling': '运球',
            'passing': '传球',
            'defending': '防守',
            'unknown': '未知'
        }
        return translations.get(action.lower(), action)
    
    def _get_quality_color(self, quality: float) -> Tuple[int, int, int]:
        """Get color based on quality score."""
        if quality >= 0.8:
            return self.COLORS['good']
        elif quality >= 0.6:
            return self.COLORS['warning']
        else:
            return self.COLORS['bad']
    
    def create_progress_chart(
        self,
        sessions_data: List[Dict],
        output_path: Optional[str] = None,
        metric: str = 'form_quality_score'
    ) -> Optional[str]:
        """
        Create a progress chart over training sessions.
        
        Args:
            sessions_data: List of session statistics.
            output_path: Path to save chart image.
            metric: Metric to plot.
            
        Returns:
            Path to saved chart, or None if matplotlib unavailable.
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        if not sessions_data:
            return None
        
        # Extract data
        dates = [s.get('date', i) for i, s in enumerate(sessions_data)]
        values = [s.get('statistics', {}).get(metric, 0) for s in sessions_data]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(len(values)), values, 'b-o', linewidth=2, markersize=8)
        
        # Add trend line
        if len(values) >= 2:
            z = np.polyfit(range(len(values)), values, 1)
            p = np.poly1d(z)
            ax.plot(range(len(values)), p(range(len(values))), 'r--', alpha=0.5)
        
        ax.set_xlabel('训练次数', fontsize=12)
        ax.set_ylabel(self._get_metric_label(metric), fontsize=12)
        ax.set_title('训练进度', fontsize=14)
        ax.grid(True, alpha=0.3)
        
        # Save figure
        if output_path is None and self.output_dir:
            output_path = os.path.join(self.output_dir, f'progress_{metric}.png')
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        plt.close()
        return None
    
    def create_angle_distribution(
        self,
        angles: List[float],
        angle_type: str = 'elbow',
        output_path: Optional[str] = None,
        ideal_range: Optional[Tuple[float, float]] = None
    ) -> Optional[str]:
        """
        Create angle distribution histogram.
        
        Args:
            angles: List of angle measurements.
            angle_type: Type of angle for labeling.
            output_path: Path to save chart.
            ideal_range: Ideal angle range to highlight.
            
        Returns:
            Path to saved chart, or None if matplotlib unavailable.
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        if not angles:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create histogram
        n, bins, patches = ax.hist(angles, bins=20, color='blue', alpha=0.7, edgecolor='black')
        
        # Highlight ideal range
        if ideal_range:
            ax.axvspan(ideal_range[0], ideal_range[1], alpha=0.2, color='green', label='理想范围')
        
        ax.axvline(np.mean(angles), color='red', linestyle='--', label=f'平均值: {np.mean(angles):.1f}°')
        
        ax.set_xlabel(f'{self._get_angle_label(angle_type)} (度)', fontsize=12)
        ax.set_ylabel('频次', fontsize=12)
        ax.set_title(f'{self._get_angle_label(angle_type)}分布', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save figure
        if output_path is None and self.output_dir:
            output_path = os.path.join(self.output_dir, f'{angle_type}_distribution.png')
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        
        plt.close()
        return None
    
    def create_dashboard(
        self,
        session_stats: Dict,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a comprehensive training dashboard.
        
        Args:
            session_stats: Session statistics dictionary.
            output_path: Path to save dashboard image.
            
        Returns:
            Path to saved dashboard, or None if matplotlib unavailable.
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        fig = plt.figure(figsize=(14, 10))
        
        # Create grid
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Quality score gauge (simplified as bar)
        ax1 = fig.add_subplot(gs[0, 0])
        quality = session_stats.get('form_quality_score', 0)
        colors = ['#ff4444', '#ffaa00', '#44ff44']
        ax1.barh(0, quality, color=colors[min(int(quality * 3), 2)], height=0.5)
        ax1.barh(0, 1, color='lightgray', height=0.5, alpha=0.3)
        ax1.set_xlim(0, 1)
        ax1.set_ylim(-0.5, 0.5)
        ax1.set_title('姿势评分', fontsize=12)
        ax1.text(quality/2, 0, f'{quality:.0%}', ha='center', va='center', fontsize=16, fontweight='bold')
        ax1.axis('off')
        
        # 2. Shot count
        ax2 = fig.add_subplot(gs[0, 1])
        shots = session_stats.get('total_shots', 0)
        ax2.text(0.5, 0.5, str(shots), ha='center', va='center', fontsize=48, fontweight='bold')
        ax2.text(0.5, 0.1, '投篮次数', ha='center', va='center', fontsize=14)
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        
        # 3. Key angles summary
        ax3 = fig.add_subplot(gs[0, 2])
        elbow = session_stats.get('average_elbow_angle')
        knee = session_stats.get('average_knee_angle')
        
        labels = []
        values = []
        if elbow is not None:
            labels.append('肘部角度')
            values.append(elbow)
        if knee is not None:
            labels.append('膝盖角度')
            values.append(knee)
        
        if values:
            ax3.barh(labels, values, color=['#4488ff', '#44cc88'])
            ax3.set_xlabel('角度 (度)')
            ax3.set_title('关键角度', fontsize=12)
        else:
            ax3.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=14)
            ax3.axis('off')
        
        # 4. Improvements text
        ax4 = fig.add_subplot(gs[1, :2])
        improvements = session_stats.get('improvements', [])
        areas = session_stats.get('areas_to_work', [])
        
        text_lines = ['优点:', '']
        for imp in improvements:
            text_lines.append(f'  ✓ {imp}')
        text_lines.extend(['', '需改进:', ''])
        for area in areas:
            text_lines.append(f'  • {area}')
        
        ax4.text(0.05, 0.95, '\n'.join(text_lines), ha='left', va='top',
                fontsize=11, family='sans-serif', transform=ax4.transAxes)
        ax4.set_title('训练反馈', fontsize=12)
        ax4.axis('off')
        
        # 5. Session info
        ax5 = fig.add_subplot(gs[1, 2])
        session_id = session_stats.get('session_id', 'N/A')
        date = session_stats.get('date', datetime.now())
        
        info_text = f"""
训练ID: {session_id}
日期: {date}
时长: {session_stats.get('duration_seconds', 0):.0f} 秒
"""
        ax5.text(0.1, 0.9, info_text, ha='left', va='top',
                fontsize=10, transform=ax5.transAxes)
        ax5.set_title('训练信息', fontsize=12)
        ax5.axis('off')
        
        # Overall title
        fig.suptitle('篮球训练分析报告', fontsize=16, fontweight='bold')
        
        # Save figure
        if output_path is None and self.output_dir:
            output_path = os.path.join(self.output_dir, 'dashboard.png')
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            return output_path
        
        plt.close()
        return None
    
    def _get_metric_label(self, metric: str) -> str:
        """Get Chinese label for metric."""
        labels = {
            'form_quality_score': '姿势评分',
            'average_elbow_angle': '平均肘部角度',
            'average_knee_angle': '平均膝盖角度',
            'shooting_percentage': '投篮命中率',
            'total_shots': '投篮次数'
        }
        return labels.get(metric, metric)
    
    def _get_angle_label(self, angle_type: str) -> str:
        """Get Chinese label for angle type."""
        labels = {
            'elbow': '肘部角度',
            'knee': '膝盖角度',
            'shoulder': '肩部角度',
            'wrist': '手腕高度'
        }
        return labels.get(angle_type, angle_type)
    
    def create_video_overlay(
        self,
        frame: np.ndarray,
        info: Dict[str, Any]
    ) -> np.ndarray:
        """
        Create informational overlay for video output.
        
        Args:
            frame: Original frame.
            info: Information to display.
            
        Returns:
            Frame with overlay.
        """
        result = frame.copy()
        height, width = result.shape[:2]
        
        # Create semi-transparent overlay area
        overlay = result.copy()
        cv2.rectangle(overlay, (10, 10), (250, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, result, 0.5, 0, result)
        
        # Add text information
        y = 35
        for key, value in info.items():
            if value is not None:
                if isinstance(value, float):
                    text = f"{key}: {value:.2f}"
                else:
                    text = f"{key}: {value}"
                cv2.putText(
                    result, text, (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1
                )
                y += 25
        
        # Add timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        cv2.putText(
            result, timestamp, (width - 100, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (255, 255, 255), 1
        )
        
        return result
