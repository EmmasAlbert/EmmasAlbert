"""
篮球检测模块
使用YOLOv8进行篮球和人员检测
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from ultralytics import YOLO


class BasketballDetector:
    """篮球检测器类"""
    
    def __init__(self, model_path: str = "yolov8n.pt", 
                 conf_threshold: float = 0.25,
                 iou_threshold: float = 0.45,
                 device: str = "cpu"):
        """
        初始化篮球检测器
        
        Args:
            model_path: YOLOv8模型路径
            conf_threshold: 置信度阈值
            iou_threshold: NMS IOU阈值
            device: 运行设备 ('cpu' 或 'cuda')
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        # 加载模型
        try:
            self.model = YOLO(model_path)
            print(f"成功加载模型: {model_path}")
        except Exception as e:
            print(f"警告: 无法加载模型 {model_path}, 将在首次使用时自动下载")
            print(f"错误信息: {e}")
            self.model = None
        
        # COCO数据集类别（YOLOv8默认）
        self.target_classes = {
            0: "person",      # 人
            32: "sports ball" # 运动球（包括篮球）
        }
    
    def detect(self, frame: np.ndarray, classes: List[int] = None) -> List[Dict]:
        """
        检测帧中的目标
        
        Args:
            frame: 输入图像帧
            classes: 要检测的类别列表，None表示检测所有目标类别
        
        Returns:
            检测结果列表，每个结果包含: {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int,
                'class_name': str
            }
        """
        if self.model is None:
            # 首次使用时加载模型
            self.model = YOLO(self.model_path)
        
        # 如果未指定类别，使用目标类别
        if classes is None:
            classes = list(self.target_classes.keys())
        
        # 执行检测
        results = self.model(frame, 
                            conf=self.conf_threshold,
                            iou=self.iou_threshold,
                            classes=classes,
                            device=self.device,
                            verbose=False)
        
        detections = []
        
        # 解析结果
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id]
                
                detections.append({
                    'bbox': [float(x1), float(y1), float(x2), float(y2)],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': class_name
                })
        
        return detections
    
    def detect_basketball_and_players(self, frame: np.ndarray) -> Tuple[List[Dict], List[Dict]]:
        """
        检测篮球和球员
        
        Args:
            frame: 输入图像帧
        
        Returns:
            (basketball_detections, player_detections): 篮球检测结果和球员检测结果
        """
        all_detections = self.detect(frame)
        
        basketball_detections = []
        player_detections = []
        
        for det in all_detections:
            if det['class_id'] == 32:  # sports ball
                basketball_detections.append(det)
            elif det['class_id'] == 0:  # person
                player_detections.append(det)
        
        return basketball_detections, player_detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        在帧上绘制检测结果
        
        Args:
            frame: 输入图像帧
            detections: 检测结果列表
        
        Returns:
            绘制后的图像帧
        """
        frame_draw = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            confidence = det['confidence']
            class_name = det['class_name']
            
            # 根据类别选择颜色
            if class_name == "person":
                color = (0, 255, 0)  # 绿色
            elif class_name == "sports ball":
                color = (0, 0, 255)  # 红色
            else:
                color = (255, 0, 0)  # 蓝色
            
            # 绘制边界框
            cv2.rectangle(frame_draw, (x1, y1), (x2, y2), color, 2)
            
            # 绘制标签
            label = f"{class_name}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame_draw, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame_draw, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame_draw
