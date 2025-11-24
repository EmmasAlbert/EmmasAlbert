"""
投篮动作分析模块
"""
import numpy as np
from typing import Dict, List, Tuple
from .pose_estimator import PoseEstimator


class ShotAnalyzer:
    """投篮动作分析器"""
    
    def __init__(self, pose_estimator: PoseEstimator, config: Dict = None):
        """
        初始化投篮分析器
        
        Args:
            pose_estimator: 姿态估计器实例
            config: 配置字典
        """
        self.pose_estimator = pose_estimator
        self.config = config or {}
        
        # 投篮动作阈值
        self.thresholds = self.config.get('shot_analysis', {}).get('shooting_thresholds', {})
        self.elbow_angle_min = self.thresholds.get('elbow_angle_min', 60)
        self.elbow_angle_max = self.thresholds.get('elbow_angle_max', 110)
        self.release_height_ratio = self.thresholds.get('release_height_ratio', 1.3)
    
    def analyze_shooting_form(self, keypoints: np.ndarray) -> Dict:
        """
        分析投篮姿势
        
        Args:
            keypoints: 关键点数组 (17, 3)
        
        Returns:
            分析结果字典: {
                'elbow_angle': float,
                'release_height': float,
                'body_alignment': float,
                'shooting_hand': str,
                'form_score': float,
                'feedback': List[str]
            }
        """
        result = {
            'elbow_angle': None,
            'release_height': None,
            'body_alignment': None,
            'shooting_hand': None,
            'form_score': 0.0,
            'feedback': []
        }
        
        # 判断投篮手（根据手腕高度）
        left_wrist = self.pose_estimator.get_keypoint(keypoints, "left_wrist")
        right_wrist = self.pose_estimator.get_keypoint(keypoints, "right_wrist")
        
        if left_wrist[2] > 0.5 and right_wrist[2] > 0.5:
            shooting_hand = "left" if left_wrist[1] < right_wrist[1] else "right"
        elif left_wrist[2] > 0.5:
            shooting_hand = "left"
        elif right_wrist[2] > 0.5:
            shooting_hand = "right"
        else:
            result['feedback'].append("无法检测到手腕，请确保手臂可见")
            return result
        
        result['shooting_hand'] = shooting_hand
        
        # 获取关键点
        if shooting_hand == "right":
            shoulder = self.pose_estimator.get_keypoint(keypoints, "right_shoulder")
            elbow = self.pose_estimator.get_keypoint(keypoints, "right_elbow")
            wrist = self.pose_estimator.get_keypoint(keypoints, "right_wrist")
        else:
            shoulder = self.pose_estimator.get_keypoint(keypoints, "left_shoulder")
            elbow = self.pose_estimator.get_keypoint(keypoints, "left_elbow")
            wrist = self.pose_estimator.get_keypoint(keypoints, "left_wrist")
        
        # 检查关键点可见性
        if min(shoulder[2], elbow[2], wrist[2]) < 0.5:
            result['feedback'].append("投篮手臂关键点不够清晰，请调整角度")
            return result
        
        # 计算肘部角度
        elbow_angle = self.pose_estimator.calculate_angle(
            (shoulder[0], shoulder[1]),
            (elbow[0], elbow[1]),
            (wrist[0], wrist[1])
        )
        result['elbow_angle'] = elbow_angle
        
        # 计算出手高度
        nose = self.pose_estimator.get_keypoint(keypoints, "nose")
        body_height = self.pose_estimator.get_body_height(keypoints)
        
        if body_height > 0:
            release_height = abs(wrist[1] - nose[1]) / body_height
            result['release_height'] = release_height
        
        # 计算身体对齐度（肩膀水平度）
        left_shoulder = self.pose_estimator.get_keypoint(keypoints, "left_shoulder")
        right_shoulder = self.pose_estimator.get_keypoint(keypoints, "right_shoulder")
        
        if min(left_shoulder[2], right_shoulder[2]) > 0.5:
            shoulder_angle = abs(np.degrees(np.arctan2(
                right_shoulder[1] - left_shoulder[1],
                right_shoulder[0] - left_shoulder[0]
            )))
            result['body_alignment'] = shoulder_angle
        
        # 评分和反馈
        score = 0
        max_score = 3
        
        # 1. 肘部角度评估
        if self.elbow_angle_min <= elbow_angle <= self.elbow_angle_max:
            score += 1
            result['feedback'].append(f"✓ 肘部角度良好 ({elbow_angle:.1f}°)")
        else:
            result['feedback'].append(f"✗ 肘部角度需调整 ({elbow_angle:.1f}°, 建议{self.elbow_angle_min}-{self.elbow_angle_max}°)")
        
        # 2. 出手高度评估
        if result['release_height'] is not None:
            if result['release_height'] >= self.release_height_ratio - 0.3:
                score += 1
                result['feedback'].append("✓ 出手高度适当")
            else:
                result['feedback'].append("✗ 建议提高出手点")
        
        # 3. 身体对齐评估
        if result['body_alignment'] is not None:
            if result['body_alignment'] < 15:  # 肩膀相对水平
                score += 1
                result['feedback'].append("✓ 身体对齐良好")
            else:
                result['feedback'].append("✗ 注意保持肩膀水平")
        
        result['form_score'] = (score / max_score) * 100
        
        return result
    
    def is_shooting_moment(self, keypoints: np.ndarray, 
                          basketball_position: Tuple[float, float] = None) -> bool:
        """
        判断是否为投篮瞬间
        
        Args:
            keypoints: 关键点数组
            basketball_position: 篮球位置 (x, y)
        
        Returns:
            是否为投篮瞬间
        """
        # 获取手腕位置
        left_wrist = self.pose_estimator.get_keypoint(keypoints, "left_wrist")
        right_wrist = self.pose_estimator.get_keypoint(keypoints, "right_wrist")
        
        # 至少一个手腕可见
        if max(left_wrist[2], right_wrist[2]) < 0.5:
            return False
        
        # 获取较高的手腕（投篮手）
        wrist = left_wrist if left_wrist[1] < right_wrist[1] else right_wrist
        
        # 获取头部位置
        nose = self.pose_estimator.get_keypoint(keypoints, "nose")
        
        if nose[2] < 0.5:
            return False
        
        # 手腕高于头部
        if wrist[1] < nose[1]:
            # 如果有篮球位置信息，检查篮球是否在手附近
            if basketball_position is not None:
                ball_x, ball_y = basketball_position
                distance = np.sqrt((wrist[0] - ball_x)**2 + (wrist[1] - ball_y)**2)
                return distance < 100  # 像素距离阈值
            return True
        
        return False
    
    def generate_report(self, analysis_results: List[Dict]) -> Dict:
        """
        生成训练报告
        
        Args:
            analysis_results: 多次投篮分析结果列表
        
        Returns:
            报告字典
        """
        if not analysis_results:
            return {
                'total_shots': 0,
                'average_score': 0,
                'summary': "暂无数据"
            }
        
        total_shots = len(analysis_results)
        valid_results = [r for r in analysis_results if r['form_score'] > 0]
        
        if not valid_results:
            return {
                'total_shots': total_shots,
                'average_score': 0,
                'summary': "无有效投篮数据"
            }
        
        # 计算平均分
        average_score = np.mean([r['form_score'] for r in valid_results])
        
        # 统计常见问题
        feedback_counts = {}
        for result in valid_results:
            for feedback in result['feedback']:
                if '✗' in feedback:
                    feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1
        
        # 生成建议
        suggestions = []
        if feedback_counts:
            top_issues = sorted(feedback_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            suggestions = [issue[0] for issue in top_issues]
        
        return {
            'total_shots': total_shots,
            'valid_shots': len(valid_results),
            'average_score': average_score,
            'score_distribution': {
                'excellent': len([r for r in valid_results if r['form_score'] >= 80]),
                'good': len([r for r in valid_results if 60 <= r['form_score'] < 80]),
                'needs_improvement': len([r for r in valid_results if r['form_score'] < 60])
            },
            'common_issues': suggestions,
            'summary': self._generate_summary(average_score)
        }
    
    def _generate_summary(self, average_score: float) -> str:
        """生成总结评语"""
        if average_score >= 80:
            return "优秀！投篮动作规范，继续保持。"
        elif average_score >= 60:
            return "良好，投篮动作基本规范，注意改进细节。"
        else:
            return "需要改进，建议重点关注反馈中的问题点。"
