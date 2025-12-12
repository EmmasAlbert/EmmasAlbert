"""
投篮动作分析模块
"""
import numpy as np
from typing import Dict, List, Tuple
from .pose_estimator import PoseEstimator


class ShotAnalyzer:
    """投篮动作分析器"""
    
    def __init__(self, pose_estimator: PoseEstimator, config: Dict = None, user_info: Dict = None):
        """
        初始化投篮分析器
        
        Args:
            pose_estimator: 姿态估计器实例
            config: 配置字典
            user_info: 用户信息（包含年龄、学段等）
        """
        self.pose_estimator = pose_estimator
        self.config = config or {}
        self.user_info = user_info or {}
        
        # 根据用户信息获取适配的阈值
        self.thresholds = self._get_adapted_thresholds()
        self.elbow_angle_min = self.thresholds.get('elbow_angle_min', 60)
        self.elbow_angle_max = self.thresholds.get('elbow_angle_max', 110)
        self.release_height_ratio = self.thresholds.get('release_height_ratio', 1.3)
        
        # 轨迹跟踪历史（用于检测投篮动作）
        self.wrist_trajectory = []  # 手腕轨迹
        self.ball_trajectory = []   # 篮球轨迹
        self.max_trajectory_length = 10  # 保留最近10帧
    
    def _get_adapted_thresholds(self) -> Dict:
        """
        根据用户年龄/学段获取适配的阈值
        
        Returns:
            适配后的阈值字典
        """
        default_thresholds = self.config.get('shot_analysis', {}).get('shooting_thresholds', {})
        
        # 如果用户信息中有学段信息，使用对应标准
        student_level = self.user_info.get('student_level')
        age = self.user_info.get('age')
        
        if student_level:
            # 使用学段对应的标准
            age_specific = self.config.get('shot_analysis', {}).get('age_specific_thresholds', {})
            if student_level in age_specific:
                level_thresholds = age_specific[student_level].copy()
                # 移除非阈值字段
                level_thresholds.pop('age_range', None)
                level_thresholds.pop('feedback_style', None)
                return level_thresholds
        
        elif age:
            # 根据年龄自动选择标准
            age_specific = self.config.get('shot_analysis', {}).get('age_specific_thresholds', {})
            for level, settings in age_specific.items():
                age_range = settings.get('age_range', [0, 100])
                if age_range[0] <= age <= age_range[1]:
                    level_thresholds = settings.copy()
                    level_thresholds.pop('age_range', None)
                    level_thresholds.pop('feedback_style', None)
                    return level_thresholds
        
        # 默认使用通用标准
        return default_thresholds
    
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
        
        # 计算肘部角度（确保转换为Python float）
        elbow_angle = self.pose_estimator.calculate_angle(
            (shoulder[0], shoulder[1]),
            (elbow[0], elbow[1]),
            (wrist[0], wrist[1])
        )
        result['elbow_angle'] = float(elbow_angle)
        
        # 计算出手高度（确保转换为Python float）
        nose = self.pose_estimator.get_keypoint(keypoints, "nose")
        body_height = self.pose_estimator.get_body_height(keypoints)
        
        if body_height > 0:
            release_height = abs(wrist[1] - nose[1]) / body_height
            result['release_height'] = float(release_height)
        
        # 计算身体对齐度（肩膀水平度）（确保转换为Python float）
        left_shoulder = self.pose_estimator.get_keypoint(keypoints, "left_shoulder")
        right_shoulder = self.pose_estimator.get_keypoint(keypoints, "right_shoulder")
        
        if min(left_shoulder[2], right_shoulder[2]) > 0.5:
            shoulder_angle = abs(np.degrees(np.arctan2(
                right_shoulder[1] - left_shoulder[1],
                right_shoulder[0] - left_shoulder[0]
            )))
            result['body_alignment'] = float(shoulder_angle)
        
        # 改进的评分系统（更合理的权重分配）
        score = 0.0
        
        # 1. 肘部角度评估（40分）
        angle_score = 0
        if self.elbow_angle_min <= elbow_angle <= self.elbow_angle_max:
            angle_score = 40
            result['feedback'].append(f"✓ 肘部角度良好 ({elbow_angle:.1f}°)")
        else:
            # 根据偏离程度给部分分数
            mid_angle = (self.elbow_angle_min + self.elbow_angle_max) / 2
            deviation = abs(elbow_angle - mid_angle)
            max_deviation = (self.elbow_angle_max - self.elbow_angle_min) / 2
            if deviation < max_deviation * 1.5:
                angle_score = max(0, 40 - deviation * 0.5)
                result['feedback'].append(f"△ 肘部角度可接受 ({elbow_angle:.1f}°)")
            else:
                result['feedback'].append(f"✗ 肘部角度需调整 ({elbow_angle:.1f}°, 建议{self.elbow_angle_min}-{self.elbow_angle_max}°)")
        score += angle_score
        
        # 2. 出手高度评估（30分）
        height_score = 0
        if result['release_height'] is not None:
            if result['release_height'] >= self.release_height_ratio - 0.2:
                height_score = 30
                result['feedback'].append("✓ 出手高度适当")
            elif result['release_height'] >= self.release_height_ratio - 0.4:
                height_score = 20
                result['feedback'].append("△ 出手高度基本合格")
            else:
                height_score = 10
                result['feedback'].append("✗ 建议提高出手点")
        else:
            height_score = 15  # 无法检测时给基础分
        score += height_score
        
        # 3. 身体对齐评估（20分）
        alignment_score = 0
        if result['body_alignment'] is not None:
            if result['body_alignment'] < 10:
                alignment_score = 20
                result['feedback'].append("✓ 身体对齐优秀")
            elif result['body_alignment'] < 20:
                alignment_score = 15
                result['feedback'].append("✓ 身体对齐良好")
            elif result['body_alignment'] < 30:
                alignment_score = 10
                result['feedback'].append("△ 身体对齐一般")
            else:
                result['feedback'].append("✗ 注意保持肩膀水平")
        else:
            alignment_score = 10  # 无法检测时给基础分
        score += alignment_score
        
        # 4. 动作完整性加分（10分）
        # 如果所有关键点都可见，说明动作完整
        completeness_score = 10
        score += completeness_score
        
        result['form_score'] = float(min(100, score))
        
        return result
    
    def _estimate_body_scale(self, keypoints: np.ndarray) -> float:
        """
        估算人体在画面中的比例（用于距离自适应）
        
        Returns:
            身体比例系数（肩膀到髋部的像素距离）
        """
        left_shoulder = self.pose_estimator.get_keypoint(keypoints, "left_shoulder")
        right_shoulder = self.pose_estimator.get_keypoint(keypoints, "right_shoulder")
        left_hip = self.pose_estimator.get_keypoint(keypoints, "left_hip")
        right_hip = self.pose_estimator.get_keypoint(keypoints, "right_hip")
        
        # 计算肩膀中点
        if left_shoulder[2] > 0.3 and right_shoulder[2] > 0.3:
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        elif left_shoulder[2] > 0.3:
            shoulder_y = left_shoulder[1]
        elif right_shoulder[2] > 0.3:
            shoulder_y = right_shoulder[1]
        else:
            return 150.0  # 默认值
        
        # 计算髋部中点
        if left_hip[2] > 0.3 and right_hip[2] > 0.3:
            hip_y = (left_hip[1] + right_hip[1]) / 2
        elif left_hip[2] > 0.3:
            hip_y = left_hip[1]
        elif right_hip[2] > 0.3:
            hip_y = right_hip[1]
        else:
            return 150.0  # 默认值
        
        # 肩膀到髋部的距离作为比例
        torso_height = abs(hip_y - shoulder_y)
        return max(50.0, torso_height)  # 至少50像素
    
    def is_shooting_moment(self, keypoints: np.ndarray, 
                          basketball_position: Tuple[float, float] = None) -> bool:
        """
        判断是否为投篮瞬间（改进版 - 支持多角度和距离自适应）
        
        Args:
            keypoints: 关键点数组
            basketball_position: 篮球位置 (x, y)
        
        Returns:
            是否为投篮瞬间
        """
        # 获取关键点
        left_wrist = self.pose_estimator.get_keypoint(keypoints, "left_wrist")
        right_wrist = self.pose_estimator.get_keypoint(keypoints, "right_wrist")
        left_elbow = self.pose_estimator.get_keypoint(keypoints, "left_elbow")
        right_elbow = self.pose_estimator.get_keypoint(keypoints, "right_elbow")
        left_shoulder = self.pose_estimator.get_keypoint(keypoints, "left_shoulder")
        right_shoulder = self.pose_estimator.get_keypoint(keypoints, "right_shoulder")
        nose = self.pose_estimator.get_keypoint(keypoints, "nose")
        
        # 估算身体比例（用于距离自适应）
        body_scale = self._estimate_body_scale(keypoints)
        
        # 至少一个手腕可见
        if max(left_wrist[2], right_wrist[2]) < 0.3:
            return False
        
        # 获取较高的手腕（投篮手）
        if left_wrist[2] > 0.3 and right_wrist[2] > 0.3:
            is_left_higher = left_wrist[1] < right_wrist[1]
            wrist = left_wrist if is_left_higher else right_wrist
            elbow = left_elbow if is_left_higher else right_elbow
            shoulder = left_shoulder if is_left_higher else right_shoulder
        elif left_wrist[2] > 0.3:
            wrist = left_wrist
            elbow = left_elbow
            shoulder = left_shoulder
        else:
            wrist = right_wrist
            elbow = right_elbow
            shoulder = right_shoulder
        
        # 条件1：手腕高于肩膀（相对于body_scale调整阈值）
        wrist_above_shoulder = False
        if shoulder[2] > 0.3:
            # 使用相对高度判断（适应不同距离）
            height_diff = shoulder[1] - wrist[1]
            threshold = body_scale * 0.3  # 30%的躯干高度
            wrist_above_shoulder = height_diff > threshold
        elif nose[2] > 0.3:
            # 如果肩膀不可见，使用头部作为参考
            height_diff = nose[1] - wrist[1]
            threshold = body_scale * 0.1  # 10%的躯干高度
            wrist_above_shoulder = height_diff > -threshold  # 允许稍低于头部
        
        if not wrist_above_shoulder:
            return False
        
        # 条件2：肘部也抬起（确保是投篮而非挥手）
        elbow_raised = False
        if elbow[2] > 0.3 and shoulder[2] > 0.3:
            elbow_diff = shoulder[1] - elbow[1]
            elbow_raised = elbow_diff > body_scale * 0.1  # 肘部高于肩膀10%
        else:
            elbow_raised = True  # 如果肘部不可见，不强制要求
        
        # 条件3：如果有篮球位置，检查距离（使用自适应阈值）
        ball_near_hand = True
        if basketball_position is not None:
            ball_x, ball_y = basketball_position
            distance = np.sqrt((wrist[0] - ball_x)**2 + (wrist[1] - ball_y)**2)
            # 距离阈值根据body_scale自适应
            distance_threshold = body_scale * 1.5  # 1.5倍躯干高度
            ball_near_hand = distance < distance_threshold
        
        # 综合判断：手腕抬起 + 肘部抬起 + 球在附近（如果有球）
        return wrist_above_shoulder and elbow_raised and ball_near_hand
    
    def update_trajectories(self, keypoints: np.ndarray, basketball_position: Tuple[float, float] = None):
        """
        更新轨迹历史
        
        Args:
            keypoints: 关键点数组
            basketball_position: 篮球位置 (x, y)
        """
        # 获取手腕位置
        left_wrist = self.pose_estimator.get_keypoint(keypoints, "left_wrist")
        right_wrist = self.pose_estimator.get_keypoint(keypoints, "right_wrist")
        
        # 选择较高的手腕
        if left_wrist[2] > 0.3 and right_wrist[2] > 0.3:
            wrist = left_wrist if left_wrist[1] < right_wrist[1] else right_wrist
        elif left_wrist[2] > 0.3:
            wrist = left_wrist
        elif right_wrist[2] > 0.3:
            wrist = right_wrist
        else:
            wrist = None
        
        # 更新手腕轨迹
        if wrist is not None:
            self.wrist_trajectory.append((wrist[0], wrist[1]))
            if len(self.wrist_trajectory) > self.max_trajectory_length:
                self.wrist_trajectory.pop(0)
        
        # 更新篮球轨迹
        if basketball_position is not None:
            self.ball_trajectory.append(basketball_position)
            if len(self.ball_trajectory) > self.max_trajectory_length:
                self.ball_trajectory.pop(0)
    
    def detect_shooting_by_trajectory(self) -> bool:
        """
        基于轨迹检测投篮动作（补充方法）
        
        Returns:
            是否检测到投篮
        """
        # 需要至少5帧数据
        if len(self.wrist_trajectory) < 5:
            return False
        
        # 检测手部向上运动
        recent_wrists = self.wrist_trajectory[-5:]
        y_coords = [w[1] for w in recent_wrists]
        
        # 向上运动：Y坐标递减（屏幕坐标系）
        upward_motion = all(y_coords[i] > y_coords[i+1] + 3 for i in range(len(y_coords)-1))
        
        # 或者检测快速上升：前3帧到后2帧的Y坐标变化
        if not upward_motion and len(recent_wrists) >= 5:
            early_avg_y = np.mean([y_coords[0], y_coords[1]])
            late_avg_y = np.mean([y_coords[3], y_coords[4]])
            upward_motion = early_avg_y - late_avg_y > 20  # 上升超过20像素
        
        # 检测篮球抛物线（如果有球的轨迹）
        ball_parabola = False
        if len(self.ball_trajectory) >= 5:
            ball_y_coords = [b[1] for b in self.ball_trajectory[-5:]]
            # 检测先上升后下降的模式
            mid_idx = len(ball_y_coords) // 2
            rising = ball_y_coords[0] > ball_y_coords[mid_idx]  # 前半段上升
            falling = ball_y_coords[mid_idx] > ball_y_coords[-1]  # 后半段下降
            ball_parabola = rising and falling
        
        return upward_motion or ball_parabola
    
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
                'average_elbow_angle': None,
                'shot_details': [],
                'summary': "暂无数据"
            }
        
        total_shots = len(analysis_results)
        valid_results = [r for r in analysis_results if r['form_score'] > 0]
        
        if not valid_results:
            return {
                'total_shots': total_shots,
                'average_score': 0,
                'average_elbow_angle': None,
                'shot_details': [],
                'summary': "无有效投篮数据"
            }
        
        # 计算平均分（转换为Python float）
        average_score = float(np.mean([r['form_score'] for r in valid_results]))
        
        # 计算平均肘部角度（确保有数据，转换为Python float）
        elbow_angles = [r.get('elbow_angle') for r in valid_results if r.get('elbow_angle') is not None]
        average_elbow_angle = float(np.mean(elbow_angles)) if elbow_angles else None
        
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
        
        # 整理每次投篮详情（确保所有值都是JSON可序列化的）
        shot_details = []
        for idx, result in enumerate(valid_results, 1):
            detail = {
                'shot_number': idx,
                'frame_number': result.get('frame_number', idx),
                'timestamp': float(result.get('timestamp', 0)) if result.get('timestamp') is not None else 0,
                'elbow_angle': float(result.get('elbow_angle')) if result.get('elbow_angle') is not None else None,
                'release_height': float(result.get('release_height')) if result.get('release_height') is not None else None,
                'body_alignment': float(result.get('body_alignment')) if result.get('body_alignment') is not None else None,
                'score': float(result.get('form_score', 0)),
                'feedback': result.get('feedback', [])
            }
            shot_details.append(detail)
        
        return {
            'total_shots': total_shots,
            'valid_shots': len(valid_results),
            'average_score': average_score,
            'average_elbow_angle': average_elbow_angle,
            'score_distribution': {
                'excellent': len([r for r in valid_results if r['form_score'] >= 70]),
                'good': len([r for r in valid_results if 50 <= r['form_score'] < 70]),
                'needs_improvement': len([r for r in valid_results if r['form_score'] < 50])
            },
            'common_issues': suggestions,
            'shot_details': shot_details,
            'summary': self._generate_summary(average_score)
        }
    
    def _generate_summary(self, average_score: float) -> str:
        """
        生成总结评语（根据年龄段调整语气）
        """
        # 获取反馈风格
        student_level = self.user_info.get('student_level')
        age_specific = self.config.get('shot_analysis', {}).get('age_specific_thresholds', {})
        
        feedback_style = "指导为主"  # 默认
        if student_level and student_level in age_specific:
            feedback_style = age_specific[student_level].get('feedback_style', '指导为主')
        
        # 根据分数和风格生成评语（调整后的标准）
        if average_score >= 70:
            if feedback_style == "鼓励为主":
                return "太棒了！🎉 你做得非常好，继续加油！"
            elif feedback_style == "指导为主":
                return "优秀！投篮动作规范，继续保持这个水平。"
            else:
                return "优秀！投篮动作规范，已达到较高水平。"
        elif average_score >= 50:
            if feedback_style == "鼓励为主":
                return "不错哦！💪 再多练习就会更好了！"
            elif feedback_style == "指导为主":
                return "良好，投篮动作基本规范，注意改进反馈中的细节。"
            else:
                return "良好，基本掌握技术要领，需进一步精细化调整。"
        elif average_score >= 35:
            if feedback_style == "鼓励为主":
                return "有进步空间！🌟 跟着建议多练习，你会越来越好的！"
            elif feedback_style == "指导为主":
                return "一般，建议重点关注反馈中的问题点，循序渐进。"
            else:
                return "需要改进，建议针对性训练薄弱环节。"
        else:
            if feedback_style == "鼓励为主":
                return "加油！💪 从基础动作开始练习，慢慢来不着急！"
            elif feedback_style == "指导为主":
                return "需要加强，建议从基础动作开始系统训练。"
            else:
                return "需要系统化训练，建议在教练指导下强化基础动作。"
