"""
YOLOv8目标检测模块
用于检测篮球、篮筐等对象
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional

class BasketballDetector:
    """篮球检测器"""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        初始化检测器
        
        Args:
            model_path: YOLOv8模型路径
        """
        self.model = YOLO(model_path)
        self.basketball_class = "sports ball"  # COCO数据集中篮球的类别
        self.hoop_confidence = 0.5
        
    def detect_basketball(self, frame: np.ndarray) -> List[Dict]:
        """
        检测篮球
        
        Args:
            frame: 视频帧
            
        Returns:
            检测结果列表，每个结果包含：
            - bbox: 边界框 [x1, y1, x2, y2]
            - confidence: 置信度
            - center: 中心点坐标 [x, y]
        """
        results = self.model(frame, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # 获取类别名称
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                
                if class_name == self.basketball_class:
                    bbox = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    
                    # 计算中心点
                    center_x = (bbox[0] + bbox[2]) / 2
                    center_y = (bbox[1] + bbox[3]) / 2
                    
                    detections.append({
                        "bbox": bbox.tolist(),
                        "confidence": confidence,
                        "center": [center_x, center_y]
                    })
        
        return detections
    
    def detect_hoop(self, frame: np.ndarray) -> Optional[Dict]:
        """
        检测篮筐
        
        Args:
            frame: 视频帧
            
        Returns:
            篮筐检测结果
        """
        # TODO: 使用自定义训练的模型检测篮筐
        # 这里返回示例数据
        return {
            "bbox": [300, 100, 380, 150],
            "confidence": 0.85,
            "center": [340, 125]
        }
    
    def track_trajectory(
        self, 
        detections: List[List[Dict]], 
        fps: int = 30
    ) -> List[Dict]:
        """
        追踪篮球轨迹
        
        Args:
            detections: 多帧检测结果
            fps: 视频帧率
            
        Returns:
            轨迹数据列表
        """
        trajectories = []
        
        if not detections:
            return trajectories
        
        # 简单的轨迹追踪（基于位置连续性）
        current_trajectory = []
        
        for frame_detections in detections:
            if frame_detections:
                # 选择置信度最高的检测
                best_detection = max(
                    frame_detections, 
                    key=lambda x: x["confidence"]
                )
                current_trajectory.append(best_detection["center"])
            else:
                # 如果检测中断，保存当前轨迹
                if len(current_trajectory) > 5:  # 至少5帧
                    trajectories.append({
                        "points": current_trajectory,
                        "duration": len(current_trajectory) / fps
                    })
                current_trajectory = []
        
        # 保存最后一条轨迹
        if len(current_trajectory) > 5:
            trajectories.append({
                "points": current_trajectory,
                "duration": len(current_trajectory) / fps
            })
        
        return trajectories
    
    def is_shot_made(
        self,
        ball_trajectory: List[Tuple[float, float]],
        hoop_position: Tuple[float, float],
        threshold: float = 50.0
    ) -> bool:
        """
        判断投篮是否命中
        
        Args:
            ball_trajectory: 篮球轨迹点列表
            hoop_position: 篮筐位置
            threshold: 命中判定阈值（像素）
            
        Returns:
            是否命中
        """
        if not ball_trajectory or not hoop_position:
            return False
        
        # 检查轨迹最低点是否接近篮筐
        min_distance = float('inf')
        
        for point in ball_trajectory:
            distance = np.sqrt(
                (point[0] - hoop_position[0]) ** 2 + 
                (point[1] - hoop_position[1]) ** 2
            )
            min_distance = min(min_distance, distance)
        
        return min_distance < threshold
    
    def calculate_shot_angle(
        self, 
        trajectory: List[Tuple[float, float]]
    ) -> Optional[float]:
        """
        计算出手角度
        
        Args:
            trajectory: 轨迹点列表
            
        Returns:
            出手角度（度）
        """
        if len(trajectory) < 3:
            return None
        
        # 取前3个点计算初始角度
        p1 = np.array(trajectory[0])
        p2 = np.array(trajectory[2])
        
        # 计算角度
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]  # 注意：图像坐标系y轴向下
        
        angle = np.arctan2(-dy, dx) * 180 / np.pi
        return angle if angle >= 0 else angle + 180

    def analyze_video(self, video_path: str) -> Dict:
        """
        分析完整视频
        
        Args:
            video_path: 视频路径
            
        Returns:
            分析结果
        """
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        all_detections = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每3帧检测一次（优化性能）
            if frame_count % 3 == 0:
                detections = self.detect_basketball(frame)
                all_detections.append(detections)
            
            frame_count += 1
        
        cap.release()
        
        # 追踪轨迹
        trajectories = self.track_trajectory(all_detections, fps)
        
        return {
            "total_frames": frame_count,
            "fps": fps,
            "trajectories": trajectories,
            "total_shots": len(trajectories)
        }


def main():
    """测试函数"""
    detector = BasketballDetector()
    
    # 测试图像检测
    test_image = np.zeros((720, 1280, 3), dtype=np.uint8)
    detections = detector.detect_basketball(test_image)
    print(f"Detected {len(detections)} basketballs")


if __name__ == "__main__":
    main()
