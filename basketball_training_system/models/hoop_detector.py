"""
篮筐检测模块
使用颜色检测和轮廓识别来检测篮筐
"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional


class HoopDetector:
    """篮筐检测器类"""
    
    def __init__(self):
        """初始化篮筐检测器"""
        # 橙色篮筐的HSV颜色范围
        self.orange_lower = np.array([5, 100, 100])
        self.orange_upper = np.array([25, 255, 255])
        
        # 红色篮筐的HSV颜色范围（备用）
        self.red_lower1 = np.array([0, 100, 100])
        self.red_upper1 = np.array([10, 255, 255])
        self.red_lower2 = np.array([160, 100, 100])
        self.red_upper2 = np.array([180, 255, 255])
    
    def detect(self, frame: np.ndarray, method: str = "color") -> List[Dict]:
        """
        检测帧中的篮筐
        
        Args:
            frame: 输入图像帧
            method: 检测方法 ('color' 或 'contour')
        
        Returns:
            检测结果列表，每个结果包含: {
                'bbox': [x1, y1, x2, y2],
                'center': [cx, cy],
                'confidence': float,
                'type': 'hoop'
            }
        """
        if method == "color":
            return self._detect_by_color(frame)
        else:
            return self._detect_by_contour(frame)
    
    def _detect_by_color(self, frame: np.ndarray) -> List[Dict]:
        """
        基于颜色的篮筐检测
        
        Args:
            frame: 输入图像帧
        
        Returns:
            检测结果列表
        """
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 创建橙色掩码
        mask_orange = cv2.inRange(hsv, self.orange_lower, self.orange_upper)
        
        # 创建红色掩码
        mask_red1 = cv2.inRange(hsv, self.red_lower1, self.red_upper1)
        mask_red2 = cv2.inRange(hsv, self.red_lower2, self.red_upper2)
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
        
        # 合并掩码
        mask = cv2.bitwise_or(mask_orange, mask_red)
        
        # 形态学操作去噪
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 过滤小区域
            if area < 500:
                continue
            
            # 获取边界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 篮筐通常是圆形或椭圆形，宽高比接近1
            aspect_ratio = float(w) / h if h > 0 else 0
            if 0.5 < aspect_ratio < 2.0:
                cx = x + w // 2
                cy = y + h // 2
                
                # 计算置信度（基于面积和形状）
                circularity = 4 * np.pi * area / (cv2.arcLength(contour, True) ** 2 + 1e-6)
                confidence = min(circularity, 1.0)
                
                detections.append({
                    'bbox': [x, y, x + w, y + h],
                    'center': [cx, cy],
                    'confidence': confidence,
                    'type': 'hoop'
                })
        
        # 按置信度排序，返回最可能的篮筐
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        return detections[:3]  # 最多返回3个候选
    
    def _detect_by_contour(self, frame: np.ndarray) -> List[Dict]:
        """
        基于轮廓的篮筐检测
        
        Args:
            frame: 输入图像帧
        
        Returns:
            检测结果列表
        """
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area < 1000:
                continue
            
            # 拟合椭圆
            if len(contour) >= 5:
                try:
                    ellipse = cv2.fitEllipse(contour)
                    (cx, cy), (ma, MA), angle = ellipse
                    
                    # 篮筐应该是相对圆的椭圆
                    if MA > 0:
                        eccentricity = ma / MA
                        if 0.6 < eccentricity < 1.0:
                            x, y, w, h = cv2.boundingRect(contour)
                            
                            detections.append({
                                'bbox': [x, y, x + w, y + h],
                                'center': [int(cx), int(cy)],
                                'confidence': eccentricity,
                                'type': 'hoop'
                            })
                except:
                    pass
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        在帧上绘制篮筐检测结果
        
        Args:
            frame: 输入图像帧
            detections: 检测结果列表
        
        Returns:
            绘制后的图像帧
        """
        frame_draw = frame.copy()
        
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = map(int, det['bbox'])
            cx, cy = det['center']
            confidence = det['confidence']
            
            # 绘制边界框（蓝色）
            cv2.rectangle(frame_draw, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # 绘制中心点
            cv2.circle(frame_draw, (cx, cy), 5, (255, 0, 0), -1)
            
            # 绘制标签
            label = f"Hoop: {confidence:.2f}"
            cv2.putText(frame_draw, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        return frame_draw
    
    def get_closest_hoop(self, detections: List[Dict], 
                        reference_point: Tuple[int, int]) -> Optional[Dict]:
        """
        获取离参考点最近的篮筐
        
        Args:
            detections: 检测结果列表
            reference_point: 参考点 (x, y)
        
        Returns:
            最近的篮筐检测结果
        """
        if not detections:
            return None
        
        ref_x, ref_y = reference_point
        min_distance = float('inf')
        closest_hoop = None
        
        for det in detections:
            cx, cy = det['center']
            distance = np.sqrt((cx - ref_x)**2 + (cy - ref_y)**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_hoop = det
        
        return closest_hoop
