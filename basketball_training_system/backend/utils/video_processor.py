"""
Video Processing Utility for Basketball Training System.

Handles video file loading, frame extraction, and processing pipeline.
"""

import os
import time
from typing import Generator, Tuple, Optional, List, Callable, Any, Dict
from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class VideoInfo:
    """Information about a video file."""
    path: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float  # seconds


class VideoProcessor:
    """
    Video processing utility for basketball training analysis.
    
    Provides methods for:
    - Loading and processing video files
    - Frame extraction and iteration
    - Video writing with annotations
    - Real-time camera capture
    """
    
    def __init__(self):
        """Initialize video processor."""
        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.video_info: Optional[VideoInfo] = None
    
    def load_video(self, video_path: str) -> VideoInfo:
        """
        Load a video file for processing.
        
        Args:
            video_path: Path to video file.
            
        Returns:
            VideoInfo with video metadata.
            
        Raises:
            FileNotFoundError: If video file doesn't exist.
            ValueError: If video cannot be opened.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.video_info = VideoInfo(
            path=video_path,
            width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            fps=fps,
            frame_count=int(frame_count),
            duration=frame_count / max(fps, 1)
        )
        
        return self.video_info
    
    def load_camera(self, camera_id: int = 0) -> VideoInfo:
        """
        Initialize camera for real-time capture.
        
        Args:
            camera_id: Camera device ID (default 0).
            
        Returns:
            VideoInfo with camera properties.
        """
        self.cap = cv2.VideoCapture(camera_id)
        
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open camera: {camera_id}")
        
        self.video_info = VideoInfo(
            path=f"camera:{camera_id}",
            width=int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            fps=self.cap.get(cv2.CAP_PROP_FPS) or 30.0,
            frame_count=-1,  # Unknown for camera
            duration=-1
        )
        
        return self.video_info
    
    def iterate_frames(
        self,
        skip_frames: int = 0,
        max_frames: Optional[int] = None,
        resize: Optional[Tuple[int, int]] = None
    ) -> Generator[Tuple[int, np.ndarray], None, None]:
        """
        Iterate through video frames.
        
        Args:
            skip_frames: Number of frames to skip between yields.
            max_frames: Maximum number of frames to yield.
            resize: Optional (width, height) to resize frames.
            
        Yields:
            Tuple of (frame_number, frame).
        """
        if self.cap is None:
            raise ValueError("No video loaded. Call load_video() first.")
        
        frame_number = 0
        yielded_count = 0
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
            
            if frame_number % (skip_frames + 1) == 0:
                if resize:
                    frame = cv2.resize(frame, resize)
                
                yield frame_number, frame
                yielded_count += 1
                
                if max_frames and yielded_count >= max_frames:
                    break
            
            frame_number += 1
    
    def get_frame(self, frame_number: int) -> Optional[np.ndarray]:
        """
        Get a specific frame by number.
        
        Args:
            frame_number: Frame number to retrieve.
            
        Returns:
            Frame as numpy array, or None if not available.
        """
        if self.cap is None:
            return None
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        
        return frame if ret else None
    
    def create_writer(
        self,
        output_path: str,
        fps: Optional[float] = None,
        size: Optional[Tuple[int, int]] = None,
        codec: str = 'mp4v'
    ) -> None:
        """
        Create video writer for output.
        
        Args:
            output_path: Path for output video.
            fps: Frames per second (uses source fps if None).
            size: Output size (uses source size if None).
            codec: FourCC codec code.
        """
        if self.video_info is None:
            raise ValueError("No video loaded. Call load_video() first.")
        
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out_fps = fps or self.video_info.fps
        out_size = size or (self.video_info.width, self.video_info.height)
        
        self.writer = cv2.VideoWriter(output_path, fourcc, out_fps, out_size)
    
    def write_frame(self, frame: np.ndarray) -> None:
        """Write a frame to output video."""
        if self.writer is None:
            raise ValueError("No writer created. Call create_writer() first.")
        
        self.writer.write(frame)
    
    def process_video(
        self,
        processor_func: Callable[[np.ndarray, int], np.ndarray],
        output_path: Optional[str] = None,
        skip_frames: int = 0,
        show_progress: bool = True,
        callback: Optional[Callable[[int, int], None]] = None
    ) -> List[np.ndarray]:
        """
        Process entire video with a custom function.
        
        Args:
            processor_func: Function that takes (frame, frame_number) and returns processed frame.
            output_path: Optional path to save processed video.
            skip_frames: Number of frames to skip.
            show_progress: Whether to print progress.
            callback: Optional callback(current_frame, total_frames).
            
        Returns:
            List of processed frames.
        """
        if self.cap is None:
            raise ValueError("No video loaded.")
        
        if output_path:
            self.create_writer(output_path)
        
        results = []
        total_frames = self.video_info.frame_count if self.video_info else 0
        start_time = time.time()
        
        for frame_num, frame in self.iterate_frames(skip_frames=skip_frames):
            processed = processor_func(frame, frame_num)
            results.append(processed)
            
            if output_path:
                self.write_frame(processed)
            
            if callback:
                callback(frame_num, total_frames)
            
            if show_progress and frame_num % 100 == 0:
                elapsed = time.time() - start_time
                fps = frame_num / max(elapsed, 0.001)
                print(f"Processed frame {frame_num}/{total_frames} ({fps:.1f} fps)")
        
        if output_path:
            self.close_writer()
        
        return results
    
    def extract_key_frames(
        self,
        interval: float = 1.0,
        output_dir: Optional[str] = None
    ) -> List[Tuple[float, np.ndarray]]:
        """
        Extract key frames at regular intervals.
        
        Args:
            interval: Time interval in seconds between key frames.
            output_dir: Optional directory to save frames as images.
            
        Returns:
            List of (timestamp, frame) tuples.
        """
        if self.cap is None or self.video_info is None:
            raise ValueError("No video loaded.")
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        key_frames = []
        fps = self.video_info.fps
        frame_interval = int(fps * interval)
        
        for frame_num, frame in self.iterate_frames(skip_frames=frame_interval-1):
            timestamp = frame_num / fps
            key_frames.append((timestamp, frame))
            
            if output_dir:
                filename = f"frame_{frame_num:06d}_{timestamp:.2f}s.jpg"
                cv2.imwrite(os.path.join(output_dir, filename), frame)
        
        return key_frames
    
    def close(self) -> None:
        """Release video capture and writer resources."""
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.close_writer()
        self.video_info = None
    
    def close_writer(self) -> None:
        """Release video writer resources."""
        if self.writer:
            self.writer.release()
            self.writer = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def concatenate_videos(
    video_paths: List[str],
    output_path: str,
    transition_frames: int = 0
) -> None:
    """
    Concatenate multiple videos into one.
    
    Args:
        video_paths: List of input video paths.
        output_path: Output video path.
        transition_frames: Number of black frames between videos.
    """
    if not video_paths:
        raise ValueError("No video paths provided")
    
    # Get properties from first video
    cap = cv2.VideoCapture(video_paths[0])
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for i, video_path in enumerate(video_paths):
        cap = cv2.VideoCapture(video_path)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize if necessary
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
            
            writer.write(frame)
        
        cap.release()
        
        # Add transition frames
        if transition_frames > 0 and i < len(video_paths) - 1:
            black_frame = np.zeros((height, width, 3), dtype=np.uint8)
            for _ in range(transition_frames):
                writer.write(black_frame)
    
    writer.release()


def extract_clip(
    video_path: str,
    output_path: str,
    start_time: float,
    end_time: float
) -> None:
    """
    Extract a clip from a video.
    
    Args:
        video_path: Input video path.
        output_path: Output clip path.
        start_time: Start time in seconds.
        end_time: End time in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    for frame_num in range(start_frame, end_frame):
        ret, frame = cap.read()
        if not ret:
            break
        writer.write(frame)
    
    cap.release()
    writer.release()
