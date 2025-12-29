"""
视频处理工具
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional


class VideoProcessor:
    """视频处理类"""
    
    def __init__(self, video_path: str):
        """
        初始化视频处理器
        
        Args:
            video_path: 视频文件路径
        """
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取一帧
        
        Returns:
            (success, frame): 是否成功和帧数据
        """
        return self.cap.read()
    
    def release(self):
        """释放视频资源"""
        if self.cap:
            self.cap.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class VideoWriter:
    """视频写入类"""
    
    def __init__(self, output_path: str, fps: int, width: int, height: int, 
                 codec: str = None):
        """
        初始化视频写入器
        
        Args:
            output_path: 输出视频路径
            fps: 帧率
            width: 视频宽度
            height: 视频高度
            codec: 编码器（默认自动选择适合浏览器的编码器）
        """
        self.output_path = output_path
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 如果未指定编码器，根据系统自动选择最佳编码器
        if codec is None:
            # 尝试使用 H.264 编码器（浏览器最佳支持）
            # 在不同系统上尝试不同的编码器
            codecs_to_try = ['avc1', 'H264', 'X264', 'mp4v']
            self.writer = None
            
            for codec_name in codecs_to_try:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*codec_name)
                    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                    if writer.isOpened():
                        self.writer = writer
                        print(f"使用视频编码器: {codec_name}")
                        break
                    else:
                        writer.release()
                except:
                    continue
            
            if self.writer is None:
                raise ValueError(f"无法创建视频写入器，请检查OpenCV安装: {output_path}")
        else:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            self.writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not self.writer.isOpened():
                raise ValueError(f"无法创建视频写入器: {output_path}")
    
    def write_frame(self, frame: np.ndarray):
        """
        写入一帧
        
        Args:
            frame: 帧数据
        """
        self.writer.write(frame)
    
    def release(self):
        """释放写入器资源"""
        if self.writer:
            self.writer.release()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def resize_frame(frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    调整帧大小
    
    Args:
        frame: 输入帧
        target_size: 目标尺寸 (width, height)
    
    Returns:
        调整后的帧
    """
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)


def draw_bbox(frame: np.ndarray, bbox: list, label: str, 
              color: Tuple[int, int, int] = (0, 255, 0), 
              thickness: int = 2) -> np.ndarray:
    """
    在帧上绘制边界框
    
    Args:
        frame: 输入帧
        bbox: 边界框 [x1, y1, x2, y2]
        label: 标签文字
        color: 颜色 (B, G, R)
        thickness: 线条粗细
    
    Returns:
        绘制后的帧
    """
    x1, y1, x2, y2 = map(int, bbox)
    
    # 绘制矩形
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    
    # 绘制标签背景
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                  (x1 + label_size[0], y1), color, -1)
    
    # 绘制标签文字
    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, (255, 255, 255), 1)
    
    return frame


def draw_keypoints(frame: np.ndarray, keypoints: np.ndarray, 
                   confidence_threshold: float = 0.5) -> np.ndarray:
    """
    在帧上绘制关键点
    
    Args:
        frame: 输入帧
        keypoints: 关键点数组 [N, 3] (x, y, confidence)
        confidence_threshold: 置信度阈值
    
    Returns:
        绘制后的帧
    """
    for i, (x, y, conf) in enumerate(keypoints):
        if conf > confidence_threshold:
            cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
            cv2.putText(frame, str(i), (int(x) + 5, int(y) + 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return frame


class DetectionSmoother:
    """检测结果平滑器，减少闪烁"""
    
    def __init__(self, min_frames_to_show: int = 3, min_frames_to_hide: int = 5):
        """
        初始化平滑器
        
        Args:
            min_frames_to_show: 连续检测到多少帧后才显示
            min_frames_to_hide: 连续未检测到多少帧后才隐藏
        """
        self.min_frames_to_show = min_frames_to_show
        self.min_frames_to_hide = min_frames_to_hide
        self.detection_history = {}  # {object_id: consecutive_frames}
        self.visible_objects = set()  # 当前可见的对象ID
    
    def update(self, detected_objects: dict) -> dict:
        """
        更新检测结果，返回平滑后的结果
        
        Args:
            detected_objects: {object_id: detection_data}
        
        Returns:
            平滑后的检测结果
        """
        current_ids = set(detected_objects.keys())
        
        # 更新检测历史
        for obj_id in detected_objects:
            if obj_id not in self.detection_history:
                self.detection_history[obj_id] = 1
            else:
                self.detection_history[obj_id] += 1
            
            # 连续检测到足够帧数，加入可见集合
            if self.detection_history[obj_id] >= self.min_frames_to_show:
                self.visible_objects.add(obj_id)
        
        # 处理未检测到的对象
        for obj_id in list(self.detection_history.keys()):
            if obj_id not in current_ids:
                self.detection_history[obj_id] -= 1
                
                # 连续未检测到足够帧数，从可见集合移除
                if self.detection_history[obj_id] <= -self.min_frames_to_hide:
                    self.visible_objects.discard(obj_id)
                    del self.detection_history[obj_id]
        
        # 返回应该显示的对象
        smoothed_results = {
            obj_id: detected_objects[obj_id] 
            for obj_id in self.visible_objects 
            if obj_id in detected_objects
        }
        
        return smoothed_results
    
    def reset(self):
        """重置平滑器"""
        self.detection_history.clear()
        self.visible_objects.clear()
