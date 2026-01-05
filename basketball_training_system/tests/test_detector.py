"""
Unit tests for detector module.
"""

import pytest
import numpy as np

from basketball_training_system.backend.models.detector import (
    BasketballDetector,
    Detection,
    create_detector
)


class TestDetection:
    """Tests for Detection dataclass."""
    
    def test_detection_creation(self):
        """Test Detection object creation."""
        det = Detection(
            class_id=0,
            class_name='basketball',
            confidence=0.95,
            bbox=(100, 100, 200, 200),
            center=(150, 150)
        )
        
        assert det.class_id == 0
        assert det.class_name == 'basketball'
        assert det.confidence == 0.95
        assert det.bbox == (100, 100, 200, 200)
        assert det.center == (150, 150)


class TestBasketballDetector:
    """Tests for BasketballDetector class."""
    
    def test_detector_initialization(self):
        """Test detector initialization without model."""
        detector = BasketballDetector(model_path='nonexistent.pt')
        assert detector is not None
        assert detector.conf_threshold == 0.5
    
    def test_detector_custom_threshold(self):
        """Test detector with custom confidence threshold."""
        detector = BasketballDetector(conf_threshold=0.7)
        assert detector.conf_threshold == 0.7
    
    def test_detect_empty_frame(self):
        """Test detection on empty frame returns empty list."""
        detector = BasketballDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Should return empty list when model not loaded
        detections = detector.detect(frame)
        assert isinstance(detections, list)
    
    def test_draw_detections(self):
        """Test drawing detections on frame."""
        detector = BasketballDetector()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        detections = [
            Detection(0, 'basketball', 0.9, (100, 100, 150, 150), (125, 125)),
            Detection(1, 'person', 0.85, (200, 100, 350, 400), (275, 250))
        ]
        
        result = detector.draw_detections(frame, detections)
        
        assert result.shape == frame.shape
        # Check that some pixels were modified (drawing occurred)
        assert not np.array_equal(result, frame)
    
    def test_is_relevant_class_coco(self):
        """Test relevant class filtering for COCO model."""
        detector = BasketballDetector()
        detector.is_custom_model = False
        
        assert detector._is_relevant_class(0, 'person') == True
        assert detector._is_relevant_class(32, 'sports ball') == True
        assert detector._is_relevant_class(2, 'car') == False
    
    def test_is_relevant_class_custom(self):
        """Test relevant class filtering for custom model."""
        detector = BasketballDetector()
        detector.is_custom_model = True
        
        assert detector._is_relevant_class(0, 'basketball') == True
        assert detector._is_relevant_class(1, 'player') == True
        assert detector._is_relevant_class(99, 'other') == False


class TestCreateDetector:
    """Tests for create_detector factory function."""
    
    def test_create_default_detector(self):
        """Test creating detector with defaults."""
        detector = create_detector()
        assert isinstance(detector, BasketballDetector)
    
    def test_create_detector_with_options(self):
        """Test creating detector with custom options."""
        detector = create_detector(
            model_type='yolov8s',
            conf_threshold=0.6,
            iou_threshold=0.5
        )
        assert detector.conf_threshold == 0.6
        assert detector.iou_threshold == 0.5
