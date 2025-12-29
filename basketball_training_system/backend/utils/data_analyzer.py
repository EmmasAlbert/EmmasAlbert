"""
Data Analyzer Module for Basketball Training System.

Provides statistical analysis and insights from training data.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
import os
from datetime import datetime

import numpy as np


@dataclass
class SessionStatistics:
    """Statistics for a training session."""
    session_id: str
    date: datetime
    duration_seconds: float
    total_shots: int
    shooting_percentage: float
    average_elbow_angle: Optional[float]
    average_knee_angle: Optional[float]
    form_quality_score: float
    improvements: List[str]
    areas_to_work: List[str]


@dataclass
class ProgressReport:
    """Progress report comparing multiple sessions."""
    sessions_analyzed: int
    date_range: Tuple[datetime, datetime]
    total_shots: int
    average_form_score: float
    form_score_trend: str  # 'improving', 'stable', 'declining'
    key_improvements: List[str]
    recommendations: List[str]


class DataAnalyzer:
    """
    Analyzer for basketball training data.
    
    Provides:
    - Session statistics calculation
    - Progress tracking over time
    - Performance trend analysis
    - Training recommendations
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize data analyzer.
        
        Args:
            data_dir: Directory to store/load session data.
        """
        self.data_dir = data_dir
        self.sessions: List[Dict[str, Any]] = []
        
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
            self._load_sessions()
    
    def _load_sessions(self) -> None:
        """Load saved session data from disk."""
        if not self.data_dir:
            return
        
        sessions_file = os.path.join(self.data_dir, 'sessions.json')
        if os.path.exists(sessions_file):
            with open(sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sessions = data.get('sessions', [])
    
    def _save_sessions(self) -> None:
        """Save session data to disk."""
        if not self.data_dir:
            return
        
        sessions_file = os.path.join(self.data_dir, 'sessions.json')
        with open(sessions_file, 'w', encoding='utf-8') as f:
            json.dump({'sessions': self.sessions}, f, indent=2, default=str)
    
    def analyze_session(
        self,
        shooting_data: List[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> SessionStatistics:
        """
        Analyze a single training session.
        
        Args:
            shooting_data: List of shooting analysis dictionaries.
            session_id: Optional session identifier.
            
        Returns:
            SessionStatistics with computed metrics.
        """
        if not session_id:
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Extract angles
        elbow_angles = [
            d['elbow_angle'] for d in shooting_data
            if d.get('elbow_angle') is not None
        ]
        knee_angles = [
            d['knee_angle'] for d in shooting_data
            if d.get('knee_angle') is not None
        ]
        quality_scores = [
            d['quality_score'] for d in shooting_data
            if d.get('quality_score') is not None
        ]
        
        # Calculate statistics
        avg_elbow = np.mean(elbow_angles) if elbow_angles else None
        avg_knee = np.mean(knee_angles) if knee_angles else None
        avg_quality = np.mean(quality_scores) if quality_scores else 0.0
        
        # Determine improvements and areas to work on
        improvements = []
        areas_to_work = []
        
        if avg_elbow is not None:
            if 85 <= avg_elbow <= 105:
                improvements.append("肘部角度控制良好")
            elif avg_elbow < 85:
                areas_to_work.append("尝试减少肘部弯曲")
            else:
                areas_to_work.append("注意保持适当的肘部弯曲")
        
        if avg_knee is not None:
            if 140 <= avg_knee <= 170:
                improvements.append("腿部发力姿势正确")
            elif avg_knee < 140:
                areas_to_work.append("减少膝盖弯曲幅度")
            else:
                areas_to_work.append("增加膝盖弯曲以获得更好的力量")
        
        if avg_quality >= 0.8:
            improvements.append("整体投篮姿势优秀")
        elif avg_quality >= 0.6:
            improvements.append("投篮姿势基本正确")
        else:
            areas_to_work.append("需要加强基本投篮姿势训练")
        
        # Calculate shooting percentage (if available)
        made_shots = sum(1 for d in shooting_data if d.get('made', False))
        shooting_pct = made_shots / len(shooting_data) * 100 if shooting_data else 0.0
        
        stats = SessionStatistics(
            session_id=session_id,
            date=datetime.now(),
            duration_seconds=sum(d.get('duration', 0) for d in shooting_data),
            total_shots=len(shooting_data),
            shooting_percentage=shooting_pct,
            average_elbow_angle=avg_elbow,
            average_knee_angle=avg_knee,
            form_quality_score=avg_quality,
            improvements=improvements,
            areas_to_work=areas_to_work
        )
        
        # Save session data
        self.sessions.append({
            'session_id': session_id,
            'date': datetime.now().isoformat(),
            'statistics': {
                'total_shots': stats.total_shots,
                'shooting_percentage': stats.shooting_percentage,
                'average_elbow_angle': avg_elbow,
                'average_knee_angle': avg_knee,
                'form_quality_score': avg_quality
            },
            'raw_data': shooting_data
        })
        self._save_sessions()
        
        return stats
    
    def calculate_progress(
        self,
        num_sessions: int = 10
    ) -> ProgressReport:
        """
        Calculate progress over recent sessions.
        
        Args:
            num_sessions: Number of recent sessions to analyze.
            
        Returns:
            ProgressReport with trend analysis.
        """
        recent_sessions = self.sessions[-num_sessions:] if self.sessions else []
        
        if len(recent_sessions) < 2:
            return ProgressReport(
                sessions_analyzed=len(recent_sessions),
                date_range=(datetime.now(), datetime.now()),
                total_shots=sum(s['statistics']['total_shots'] for s in recent_sessions),
                average_form_score=np.mean([
                    s['statistics']['form_quality_score']
                    for s in recent_sessions
                ]) if recent_sessions else 0.0,
                form_score_trend='stable',
                key_improvements=[],
                recommendations=["需要更多训练数据来分析进步趋势"]
            )
        
        # Parse dates
        dates = [
            datetime.fromisoformat(s['date'])
            for s in recent_sessions
        ]
        
        # Calculate form score trend
        scores = [s['statistics']['form_quality_score'] for s in recent_sessions]
        
        # Simple linear regression for trend
        x = np.arange(len(scores))
        if len(scores) >= 2:
            slope = np.polyfit(x, scores, 1)[0]
            if slope > 0.01:
                trend = 'improving'
            elif slope < -0.01:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        # Identify improvements
        key_improvements = []
        recommendations = []
        
        if len(recent_sessions) >= 2:
            first_half = recent_sessions[:len(recent_sessions)//2]
            second_half = recent_sessions[len(recent_sessions)//2:]
            
            # Compare elbow angles
            first_elbow = np.mean([
                s['statistics']['average_elbow_angle']
                for s in first_half
                if s['statistics']['average_elbow_angle'] is not None
            ]) if any(s['statistics']['average_elbow_angle'] for s in first_half) else None
            
            second_elbow = np.mean([
                s['statistics']['average_elbow_angle']
                for s in second_half
                if s['statistics']['average_elbow_angle'] is not None
            ]) if any(s['statistics']['average_elbow_angle'] for s in second_half) else None
            
            if first_elbow and second_elbow:
                ideal_elbow = 95  # Center of ideal range
                if abs(second_elbow - ideal_elbow) < abs(first_elbow - ideal_elbow):
                    key_improvements.append("肘部角度控制有明显改善")
        
        # Generate recommendations based on recent data
        latest = recent_sessions[-1]['statistics'] if recent_sessions else {}
        
        if latest.get('form_quality_score', 0) < 0.6:
            recommendations.append("建议关注基本投篮姿势的训练")
        
        if latest.get('average_elbow_angle') and (
            latest['average_elbow_angle'] < 80 or latest['average_elbow_angle'] > 110
        ):
            recommendations.append("重点改善肘部角度控制")
        
        if trend == 'improving':
            recommendations.append("继续保持当前训练方法")
        elif trend == 'declining':
            recommendations.append("建议回顾基本动作要领")
        
        return ProgressReport(
            sessions_analyzed=len(recent_sessions),
            date_range=(min(dates), max(dates)),
            total_shots=sum(s['statistics']['total_shots'] for s in recent_sessions),
            average_form_score=np.mean(scores),
            form_score_trend=trend,
            key_improvements=key_improvements,
            recommendations=recommendations
        )
    
    def compare_sessions(
        self,
        session_id_1: str,
        session_id_2: str
    ) -> Dict[str, Any]:
        """
        Compare two training sessions.
        
        Args:
            session_id_1: First session ID.
            session_id_2: Second session ID.
            
        Returns:
            Dictionary with comparison results.
        """
        session1 = next(
            (s for s in self.sessions if s['session_id'] == session_id_1),
            None
        )
        session2 = next(
            (s for s in self.sessions if s['session_id'] == session_id_2),
            None
        )
        
        if not session1 or not session2:
            return {'error': 'Session not found'}
        
        stats1 = session1['statistics']
        stats2 = session2['statistics']
        
        comparison = {
            'session_1': {
                'id': session_id_1,
                'date': session1['date'],
                'stats': stats1
            },
            'session_2': {
                'id': session_id_2,
                'date': session2['date'],
                'stats': stats2
            },
            'differences': {
                'form_score_change': stats2['form_quality_score'] - stats1['form_quality_score'],
                'shots_change': stats2['total_shots'] - stats1['total_shots']
            },
            'improvements': []
        }
        
        if stats2['form_quality_score'] > stats1['form_quality_score']:
            comparison['improvements'].append('投篮姿势质量提高')
        
        if (stats1.get('average_elbow_angle') and stats2.get('average_elbow_angle')):
            ideal = 95
            if abs(stats2['average_elbow_angle'] - ideal) < abs(stats1['average_elbow_angle'] - ideal):
                comparison['improvements'].append('肘部角度更接近理想值')
        
        return comparison
    
    def get_angle_distribution(
        self,
        angle_type: str = 'elbow'
    ) -> Dict[str, Any]:
        """
        Get distribution of angles across all sessions.
        
        Args:
            angle_type: 'elbow' or 'knee'.
            
        Returns:
            Dictionary with distribution data.
        """
        angles = []
        
        for session in self.sessions:
            raw_data = session.get('raw_data', [])
            for shot in raw_data:
                angle = shot.get(f'{angle_type}_angle')
                if angle is not None:
                    angles.append(angle)
        
        if not angles:
            return {'error': 'No data available'}
        
        return {
            'count': len(angles),
            'mean': np.mean(angles),
            'std': np.std(angles),
            'min': np.min(angles),
            'max': np.max(angles),
            'percentiles': {
                '25': np.percentile(angles, 25),
                '50': np.percentile(angles, 50),
                '75': np.percentile(angles, 75)
            },
            'histogram': np.histogram(angles, bins=10)
        }
    
    def generate_report(
        self,
        format: str = 'text'
    ) -> str:
        """
        Generate a comprehensive training report.
        
        Args:
            format: Output format ('text' or 'json').
            
        Returns:
            Formatted report string.
        """
        progress = self.calculate_progress()
        
        if format == 'json':
            return json.dumps({
                'sessions_analyzed': progress.sessions_analyzed,
                'total_shots': progress.total_shots,
                'average_form_score': progress.average_form_score,
                'trend': progress.form_score_trend,
                'improvements': progress.key_improvements,
                'recommendations': progress.recommendations
            }, ensure_ascii=False, indent=2)
        
        # Text format
        lines = [
            "=" * 50,
            "篮球训练分析报告",
            "=" * 50,
            "",
            f"分析训练次数: {progress.sessions_analyzed}",
            f"总投篮次数: {progress.total_shots}",
            f"平均姿势评分: {progress.average_form_score:.2f}",
            f"进步趋势: {self._translate_trend(progress.form_score_trend)}",
            "",
            "主要改进:",
        ]
        
        for improvement in progress.key_improvements:
            lines.append(f"  ✓ {improvement}")
        
        if not progress.key_improvements:
            lines.append("  (继续训练以获得更多数据)")
        
        lines.extend([
            "",
            "训练建议:",
        ])
        
        for rec in progress.recommendations:
            lines.append(f"  • {rec}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _translate_trend(self, trend: str) -> str:
        """Translate trend to Chinese."""
        translations = {
            'improving': '持续进步 ↑',
            'stable': '保持稳定 →',
            'declining': '有所下降 ↓'
        }
        return translations.get(trend, trend)
    
    def export_data(
        self,
        output_path: str,
        format: str = 'csv'
    ) -> None:
        """
        Export training data to file.
        
        Args:
            output_path: Output file path.
            format: Export format ('csv' or 'json').
        """
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2, default=str)
        elif format == 'csv':
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'session_id', 'date', 'total_shots', 'shooting_percentage',
                    'average_elbow_angle', 'average_knee_angle', 'form_quality_score'
                ])
                
                for session in self.sessions:
                    stats = session['statistics']
                    writer.writerow([
                        session['session_id'],
                        session['date'],
                        stats['total_shots'],
                        stats['shooting_percentage'],
                        stats.get('average_elbow_angle', ''),
                        stats.get('average_knee_angle', ''),
                        stats['form_quality_score']
                    ])
