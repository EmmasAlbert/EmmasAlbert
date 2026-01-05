"""
Unit tests for video processor module.
"""

import pytest
import numpy as np
import os
import tempfile

from basketball_training_system.backend.utils.video_processor import (
    VideoProcessor,
    VideoInfo
)


class TestVideoInfo:
    """Tests for VideoInfo dataclass."""
    
    def test_video_info_creation(self):
        """Test VideoInfo object creation."""
        info = VideoInfo(
            path='test.mp4',
            width=1920,
            height=1080,
            fps=30.0,
            frame_count=900,
            duration=30.0
        )
        
        assert info.path == 'test.mp4'
        assert info.width == 1920
        assert info.height == 1080
        assert info.fps == 30.0
        assert info.frame_count == 900
        assert info.duration == 30.0


class TestVideoProcessor:
    """Tests for VideoProcessor class."""
    
    def test_processor_initialization(self):
        """Test video processor initialization."""
        processor = VideoProcessor()
        
        assert processor.cap is None
        assert processor.writer is None
        assert processor.video_info is None
    
    def test_load_nonexistent_video(self):
        """Test loading nonexistent video raises error."""
        processor = VideoProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.load_video('nonexistent_video.mp4')
    
    def test_iterate_frames_without_load(self):
        """Test iterating frames without loading video raises error."""
        processor = VideoProcessor()
        
        with pytest.raises(ValueError):
            list(processor.iterate_frames())
    
    def test_get_frame_without_load(self):
        """Test getting frame without loading video returns None."""
        processor = VideoProcessor()
        
        result = processor.get_frame(0)
        assert result is None
    
    def test_create_writer_without_load(self):
        """Test creating writer without loading video raises error."""
        processor = VideoProcessor()
        
        with pytest.raises(ValueError):
            processor.create_writer('output.mp4')
    
    def test_write_frame_without_writer(self):
        """Test writing frame without writer raises error."""
        processor = VideoProcessor()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError):
            processor.write_frame(frame)
    
    def test_close_empty_processor(self):
        """Test closing processor without resources."""
        processor = VideoProcessor()
        
        # Should not raise
        processor.close()
        
        assert processor.cap is None
        assert processor.writer is None
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with VideoProcessor() as processor:
            assert processor is not None
        
        # After context exit, should be cleaned up
        assert processor.cap is None


class TestVideoProcessorWithTestVideo:
    """Tests requiring a test video file."""
    
    @pytest.fixture
    def create_test_video(self):
        """Create a simple test video file."""
        import cv2
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            video_path = f.name
        
        # Create a simple video with 30 frames
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))
        
        for i in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:, :, 0] = i * 8  # Varying blue channel
            writer.write(frame)
        
        writer.release()
        
        yield video_path
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
    
    def test_load_video(self, create_test_video):
        """Test loading a video file."""
        processor = VideoProcessor()
        
        info = processor.load_video(create_test_video)
        
        assert info.width == 640
        assert info.height == 480
        assert info.fps == 30.0
        assert info.frame_count == 30
        
        processor.close()
    
    def test_iterate_frames(self, create_test_video):
        """Test iterating through video frames."""
        processor = VideoProcessor()
        processor.load_video(create_test_video)
        
        frames = list(processor.iterate_frames())
        
        assert len(frames) == 30
        assert all(isinstance(f[1], np.ndarray) for f in frames)
        
        processor.close()
    
    def test_iterate_frames_with_skip(self, create_test_video):
        """Test iterating with frame skipping."""
        processor = VideoProcessor()
        processor.load_video(create_test_video)
        
        frames = list(processor.iterate_frames(skip_frames=1))
        
        # Should get every other frame
        assert len(frames) == 15
        
        processor.close()
    
    def test_iterate_frames_with_max(self, create_test_video):
        """Test iterating with max frames limit."""
        processor = VideoProcessor()
        processor.load_video(create_test_video)
        
        frames = list(processor.iterate_frames(max_frames=10))
        
        assert len(frames) == 10
        
        processor.close()
    
    def test_get_frame(self, create_test_video):
        """Test getting specific frame."""
        processor = VideoProcessor()
        processor.load_video(create_test_video)
        
        frame = processor.get_frame(15)
        
        assert frame is not None
        assert frame.shape == (480, 640, 3)
        
        processor.close()
