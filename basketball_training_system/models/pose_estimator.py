"""
姿态估计模块
使用YOLOv8-Pose进行人体姿态估计
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple
from ultralytics import YOLO


class PoseEstimator:
    """姿态估计器类"""
    
    # COCO关键点定义
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]
    
    # 骨架连接定义
    SKELETON = [
        [16, 14], [14, 12], [17, 15], [15, 13], [12, 13],
        [6, 12], [7, 13], [6, 7], [6, 8], [7, 9],
        [8, 10], [9, 11], [2, 3], [1, 2], [1, 3],
        [2, 4], [3, 5], [4, 6], [5, 7]
    ]
    
    def __init__(self, model_path: str = "yolov8n-pose.pt",
                 conf_threshold: float = 0.3,
                 keypoint_threshold: float = 0.5,
                 device: str = "cpu"):
        """
        初始化姿态估计器
        
        Args:
            model_path: YOLOv8-Pose模型路径
            conf_threshold: 置信度阈值
            keypoint_threshold: 关键点置信度阈值
            device: 运行设备 ('cpu' 或 'cuda')
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.keypoint_threshold = keypoint_threshold
        self.device = device
        
        # 加载模型
        try:
            self.model = YOLO(model_path)
            print(f"成功加载姿态估计模型: {model_path}")
        except Exception as e:
            print(f"警告: 无法加载模型 {model_path}, 将在首次使用时自动下载")
            print(f"错误信息: {e}")
            self.model = None
    
    def estimate(self, frame: np.ndarray) -> List[Dict]:
        """
        估计帧中人物的姿态
        
        Args:
            frame: 输入图像帧
        
        Returns:
            姿态估计结果列表，每个结果包含: {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'keypoints': np.ndarray  # shape: (17, 3) - x, y, confidence
            }
        """
        if self.model is None:
            # 首次使用时加载模型
            self.model = YOLO(self.model_path)
        
        # 执行姿态估计
        results = self.model(frame,
                            conf=self.conf_threshold,
                            device=self.device,
                            verbose=False)
        
        poses = []
        
        # 解析结果
        for result in results:
            if result.keypoints is None:
                continue
                
            boxes = result.boxes
            keypoints = result.keypoints
            
            for i in range(len(boxes)):
                box = boxes[i]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                
                # 获取关键点 (17, 3) - x, y, confidence
                kpts = keypoints[i].data[0].cpu().numpy()
                
                poses.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': confidence,
                    'keypoints': kpts
                })
        
        return poses
    
    def get_keypoint(self, keypoints: np.ndarray, keypoint_name: str) -> Tuple[float, float, float]:
        """
        获取指定关键点
        
        Args:
            keypoints: 关键点数组
            keypoint_name: 关键点名称
        
        Returns:
            (x, y, confidence)
        """
        if keypoint_name not in self.KEYPOINT_NAMES:
            raise ValueError(f"未知的关键点名称: {keypoint_name}")
        
        idx = self.KEYPOINT_NAMES.index(keypoint_name)
        return tuple(keypoints[idx])
    
    def calculate_angle(self, point1: Tuple[float, float], 
                       point2: Tuple[float, float], 
                       point3: Tuple[float, float]) -> float:
        """
        计算三点之间的角度
        
        Args:
            point1: 第一个点 (x, y)
            point2: 中心点 (x, y)
            point3: 第三个点 (x, y)
        
        Returns:
            角度值（度）
        """
        x1, y1 = point1[:2]
        x2, y2 = point2[:2]
        x3, y3 = point3[:2]
        
        # 计算向量
        vector1 = np.array([x1 - x2, y1 - y2])
        vector2 = np.array([x3 - x2, y3 - y2])
        
        # 计算角度
        cos_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def draw_pose(self, frame: np.ndarray, poses: List[Dict]) -> np.ndarray:
        """
        在帧上绘制姿态
        
        Args:
            frame: 输入图像帧
            poses: 姿态估计结果列表
        
        Returns:
            绘制后的图像帧
        """
        frame_draw = frame.copy()
        
        for pose in poses:
            keypoints = pose['keypoints']
            
            # 绘制骨架
            for connection in self.SKELETON:
                pt1_idx = connection[0] - 1  # 索引从0开始
                pt2_idx = connection[1] - 1
                
                if pt1_idx >= len(keypoints) or pt2_idx >= len(keypoints):
                    continue
                
                x1, y1, conf1 = keypoints[pt1_idx]
                x2, y2, conf2 = keypoints[pt2_idx]
                
                if conf1 > self.keypoint_threshold and conf2 > self.keypoint_threshold:
                    cv2.line(frame_draw, (int(x1), int(y1)), (int(x2), int(y2)),
                            (255, 0, 255), 2)
            
            # 绘制关键点
            for i, (x, y, conf) in enumerate(keypoints):
                if conf > self.keypoint_threshold:
                    cv2.circle(frame_draw, (int(x), int(y)), 4, (0, 255, 0), -1)
                    cv2.circle(frame_draw, (int(x), int(y)), 5, (0, 0, 255), 1)
        
        return frame_draw
    
    def get_body_height(self, keypoints: np.ndarray) -> float:
        """
        计算身体高度（从头到脚踝的平均距离）
        
        Args:
            keypoints: 关键点数组
        
        Returns:
            身体高度（像素）
        """
        nose = self.get_keypoint(keypoints, "nose")
        left_ankle = self.get_keypoint(keypoints, "left_ankle")
        right_ankle = self.get_keypoint(keypoints, "right_ankle")
        
        if nose[2] < self.keypoint_threshold:
            return 0.0
        
        # 使用可见的脚踝
        ankle_y = []
        if left_ankle[2] > self.keypoint_threshold:
            ankle_y.append(left_ankle[1])
        if right_ankle[2] > self.keypoint_threshold:
            ankle_y.append(right_ankle[1])
        
        if not ankle_y:
            return 0.0
        
        avg_ankle_y = np.mean(ankle_y)
        height = abs(avg_ankle_y - nose[1])
        
        return height
