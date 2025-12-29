"""
Unit tests for data analyzer module.
"""

import pytest
import numpy as np
import os
import tempfile
import json
from datetime import datetime

from basketball_training_system.backend.utils.data_analyzer import (
    DataAnalyzer,
    SessionStatistics,
    ProgressReport
)


class TestSessionStatistics:
    """Tests for SessionStatistics dataclass."""
    
    def test_session_statistics_creation(self):
        """Test SessionStatistics object creation."""
        stats = SessionStatistics(
            session_id='test123',
            date=datetime.now(),
            duration_seconds=300.0,
            total_shots=20,
            shooting_percentage=45.0,
            average_elbow_angle=95.0,
            average_knee_angle=155.0,
            form_quality_score=0.75,
            improvements=['Good elbow angle'],
            areas_to_work=['Improve knee bend']
        )
        
        assert stats.session_id == 'test123'
        assert stats.total_shots == 20
        assert stats.form_quality_score == 0.75


class TestDataAnalyzer:
    """Tests for DataAnalyzer class."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization without data dir."""
        analyzer = DataAnalyzer()
        
        assert analyzer.sessions == []
        assert analyzer.data_dir is None
    
    def test_analyzer_with_temp_dir(self):
        """Test analyzer initialization with temp directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = DataAnalyzer(data_dir=temp_dir)
            
            assert analyzer.data_dir == temp_dir
            assert os.path.exists(temp_dir)
    
    def test_analyze_empty_session(self):
        """Test analyzing session with no data."""
        analyzer = DataAnalyzer()
        
        stats = analyzer.analyze_session(shooting_data=[], session_id='test')
        
        assert stats.total_shots == 0
        assert stats.form_quality_score == 0.0
        assert stats.session_id == 'test'
    
    def test_analyze_session_with_data(self):
        """Test analyzing session with shooting data."""
        analyzer = DataAnalyzer()
        
        shooting_data = [
            {'elbow_angle': 90, 'knee_angle': 150, 'quality_score': 0.8},
            {'elbow_angle': 95, 'knee_angle': 155, 'quality_score': 0.85},
            {'elbow_angle': 100, 'knee_angle': 160, 'quality_score': 0.9}
        ]
        
        stats = analyzer.analyze_session(shooting_data=shooting_data)
        
        assert stats.total_shots == 3
        assert stats.average_elbow_angle == pytest.approx(95.0)
        assert stats.average_knee_angle == pytest.approx(155.0)
        assert stats.form_quality_score == pytest.approx(0.85)
    
    def test_analyze_session_generates_feedback(self):
        """Test that session analysis generates appropriate feedback."""
        analyzer = DataAnalyzer()
        
        # Good form data
        shooting_data = [
            {'elbow_angle': 95, 'knee_angle': 155, 'quality_score': 0.9}
            for _ in range(5)
        ]
        
        stats = analyzer.analyze_session(shooting_data=shooting_data)
        
        assert len(stats.improvements) > 0 or len(stats.areas_to_work) > 0
    
    def test_calculate_progress_no_data(self):
        """Test progress calculation with no sessions."""
        analyzer = DataAnalyzer()
        
        progress = analyzer.calculate_progress()
        
        assert progress.sessions_analyzed == 0
        assert progress.form_score_trend == 'stable'
    
    def test_calculate_progress_with_sessions(self):
        """Test progress calculation with multiple sessions."""
        analyzer = DataAnalyzer()
        
        # Add mock sessions with improving scores
        for i in range(5):
            analyzer.sessions.append({
                'session_id': f'session_{i}',
                'date': datetime.now().isoformat(),
                'statistics': {
                    'total_shots': 10,
                    'shooting_percentage': 0,
                    'average_elbow_angle': 95,
                    'average_knee_angle': 155,
                    'form_quality_score': 0.6 + i * 0.05  # Improving
                },
                'raw_data': []
            })
        
        progress = analyzer.calculate_progress(num_sessions=5)
        
        assert progress.sessions_analyzed == 5
        assert progress.form_score_trend == 'improving'
    
    def test_compare_sessions(self):
        """Test comparing two sessions."""
        analyzer = DataAnalyzer()
        
        analyzer.sessions = [
            {
                'session_id': 'session_1',
                'date': datetime.now().isoformat(),
                'statistics': {
                    'total_shots': 10,
                    'form_quality_score': 0.6,
                    'average_elbow_angle': 90
                }
            },
            {
                'session_id': 'session_2',
                'date': datetime.now().isoformat(),
                'statistics': {
                    'total_shots': 15,
                    'form_quality_score': 0.8,
                    'average_elbow_angle': 95
                }
            }
        ]
        
        comparison = analyzer.compare_sessions('session_1', 'session_2')
        
        assert 'differences' in comparison
        assert comparison['differences']['form_score_change'] == pytest.approx(0.2)
    
    def test_compare_nonexistent_session(self):
        """Test comparing with nonexistent session returns error."""
        analyzer = DataAnalyzer()
        
        comparison = analyzer.compare_sessions('fake_1', 'fake_2')
        
        assert 'error' in comparison
    
    def test_get_angle_distribution_no_data(self):
        """Test getting angle distribution with no data."""
        analyzer = DataAnalyzer()
        
        result = analyzer.get_angle_distribution('elbow')
        
        assert 'error' in result
    
    def test_get_angle_distribution_with_data(self):
        """Test getting angle distribution with data."""
        analyzer = DataAnalyzer()
        
        analyzer.sessions = [
            {
                'session_id': 'test',
                'raw_data': [
                    {'elbow_angle': 90},
                    {'elbow_angle': 95},
                    {'elbow_angle': 100}
                ]
            }
        ]
        
        result = analyzer.get_angle_distribution('elbow')
        
        assert result['count'] == 3
        assert result['mean'] == pytest.approx(95.0)
    
    def test_generate_report_text(self):
        """Test generating text report."""
        analyzer = DataAnalyzer()
        
        report = analyzer.generate_report(format='text')
        
        assert '篮球训练分析报告' in report
    
    def test_generate_report_json(self):
        """Test generating JSON report."""
        analyzer = DataAnalyzer()
        
        report = analyzer.generate_report(format='json')
        
        data = json.loads(report)
        assert 'sessions_analyzed' in data
    
    def test_export_data_json(self):
        """Test exporting data to JSON."""
        analyzer = DataAnalyzer()
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            analyzer.export_data(output_path, format='json')
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                data = json.load(f)
                assert isinstance(data, list)
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_export_data_csv(self):
        """Test exporting data to CSV."""
        analyzer = DataAnalyzer()
        
        analyzer.sessions = [
            {
                'session_id': 'test_1',
                'date': datetime.now().isoformat(),
                'statistics': {
                    'total_shots': 10,
                    'shooting_percentage': 50,
                    'average_elbow_angle': 95,
                    'average_knee_angle': 155,
                    'form_quality_score': 0.8
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        
        try:
            analyzer.export_data(output_path, format='csv')
            
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert 'session_id' in content
                assert 'test_1' in content
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
