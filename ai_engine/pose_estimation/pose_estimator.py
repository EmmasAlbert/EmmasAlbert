"""
姿态估计模块
基于MediaPipe进行人体姿态检测和分析
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional

class PoseEstimator:
    """姿态估计器"""
    
    def __init__(self):
        """初始化姿态估计器"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict]:
        """
        检测人体姿态
        
        Args:
            frame: 视频帧
            
        Returns:
            姿态关键点信息
        """
        # 转换颜色空间
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 检测姿态
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
        
        # 提取关键点
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            })
        
        return {
            "landmarks": landmarks,
            "world_landmarks": results.pose_world_landmarks
        }
    
    def calculate_angle(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        point3: Tuple[float, float]
    ) -> float:
        """
        计算三点之间的角度
        
        Args:
            point1: 第一个点
            point2: 中间点（角的顶点）
            point3: 第三个点
            
        Returns:
            角度（度）
        """
        # 创建向量
        vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        # 计算角度
        cos_angle = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def analyze_shooting_pose(self, landmarks: List[Dict]) -> Dict:
        """
        分析投篮姿态
        
        Args:
            landmarks: 关键点列表
            
        Returns:
            姿态分析结果
        """
        if not landmarks or len(landmarks) < 33:
            return {
                "valid": False,
                "message": "No valid pose detected"
            }
        
        # MediaPipe关键点索引
        # 11: 左肩, 12: 右肩
        # 13: 左肘, 14: 右肘
        # 15: 左腕, 16: 右腕
        # 23: 左髋, 24: 右髋
        # 25: 左膝, 26: 右膝
        # 27: 左踝, 28: 右踝
        
        # 使用右侧关键点（假设右手投篮）
        shoulder = (landmarks[12]["x"], landmarks[12]["y"])
        elbow = (landmarks[14]["x"], landmarks[14]["y"])
        wrist = (landmarks[16]["x"], landmarks[16]["y"])
        hip = (landmarks[24]["x"], landmarks[24]["y"])
        knee = (landmarks[26]["x"], landmarks[26]["y"])
        ankle = (landmarks[28]["x"], landmarks[28]["y"])
        
        # 计算关键角度
        elbow_angle = self.calculate_angle(shoulder, elbow, wrist)
        shoulder_angle = self.calculate_angle(hip, shoulder, elbow)
        knee_angle = self.calculate_angle(hip, knee, ankle)
        hip_angle = self.calculate_angle(shoulder, hip, knee)
        
        angles = {
            "elbow": elbow_angle,
            "shoulder": shoulder_angle,
            "knee": knee_angle,
            "hip": hip_angle
        }
        
        # 评估姿态
        issues = []
        suggestions = []
        score = 100
        
        # 肘部角度检查（理想：90度左右）
        if elbow_angle < 80:
            issues.append("手肘角度偏小")
            suggestions.append("加大手肘弯曲至90度左右")
            score -= 10
        elif elbow_angle > 110:
            issues.append("手肘角度过大")
            suggestions.append("适当减小手肘弯曲角度")
            score -= 5
        
        # 膝盖角度检查（理想：120-140度）
        if knee_angle > 160:
            issues.append("膝盖弯曲不足")
            suggestions.append("降低重心，增加膝盖弯曲")
            score -= 15
        elif knee_angle < 100:
            issues.append("膝盖弯曲过度")
            suggestions.append("适当提高重心")
            score -= 10
        
        # 髋部角度检查
        if hip_angle > 170:
            issues.append("身体过于直立")
            suggestions.append("适当前倾，保持身体平衡")
            score -= 5
        
        return {
            "valid": True,
            "angles": angles,
            "pose_score": max(0, score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def draw_pose(
        self,
        frame: np.ndarray,
        landmarks: Optional[Dict]
    ) -> np.ndarray:
        """
        在图像上绘制姿态
        
        Args:
            frame: 视频帧
            landmarks: 姿态关键点
            
        Returns:
            绘制了姿态的图像
        """
        if not landmarks:
            return frame
        
        # TODO: 实现姿态绘制
        return frame
    
    def analyze_video(self, video_path: str) -> Dict:
        """
        分析完整视频的姿态
        
        Args:
            video_path: 视频路径
            
        Returns:
            分析结果
        """
        cap = cv2.VideoCapture(video_path)
        
        all_poses = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 每5帧分析一次
            if frame_count % 5 == 0:
                pose = self.detect_pose(frame)
                if pose:
                    analysis = self.analyze_shooting_pose(pose["landmarks"])
                    all_poses.append(analysis)
            
            frame_count += 1
        
        cap.release()
        
        # 计算平均得分
        valid_poses = [p for p in all_poses if p.get("valid")]
        avg_score = 0
        if valid_poses:
            avg_score = sum(p["pose_score"] for p in valid_poses) / len(valid_poses)
        
        # 收集所有问题
        all_issues = []
        for pose in valid_poses:
            all_issues.extend(pose.get("issues", []))
        
        # 统计最常见的问题
        from collections import Counter
        common_issues = Counter(all_issues).most_common(3)
        
        return {
            "total_frames": frame_count,
            "analyzed_frames": len(all_poses),
            "valid_frames": len(valid_poses),
            "avg_pose_score": avg_score,
            "common_issues": [issue for issue, count in common_issues],
            "detailed_poses": all_poses[:10]  # 只返回前10帧详情
        }


def main():
    """测试函数"""
    estimator = PoseEstimator()
    
    # 测试图像检测
    test_image = np.zeros((720, 1280, 3), dtype=np.uint8)
    pose = estimator.detect_pose(test_image)
    print(f"Pose detected: {pose is not None}")


if __name__ == "__main__":
    main()
