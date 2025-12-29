"""
使用示例 - 展示如何使用系统的各个组件
"""
import cv2
import numpy as np
from pathlib import Path

from models.basketball_detector import BasketballDetector
from models.pose_estimator import PoseEstimator
from models.shot_analyzer import ShotAnalyzer
from models.hoop_detector import HoopDetector
from utils.config_loader import load_config
from utils.logger import setup_logger

def example_image_detection():
    """示例1: 单张图像检测"""
    print("\n" + "="*60)
    print("示例1: 单张图像检测")
    print("="*60)
    
    # 初始化
    logger = setup_logger('example')
    config = load_config()
    
    # 创建检测器
    detector = BasketballDetector()
    pose_estimator = PoseEstimator()
    hoop_detector = HoopDetector()
    
    # 加载测试图像（这里使用示例图像）
    # 实际使用时替换为真实图像路径
    logger.info("提示: 请将测试图像放在 data/raw/ 目录下")
    
    # 创建示例图像（黑色背景）
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.putText(frame, "Basketball Training System", (400, 360),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    # 检测篮球和人
    ball_dets, player_dets = detector.detect_basketball_and_players(frame)
    logger.info(f"检测到 {len(ball_dets)} 个篮球, {len(player_dets)} 个人")
    
    # 检测篮筐
    hoop_dets = hoop_detector.detect(frame)
    logger.info(f"检测到 {len(hoop_dets)} 个篮筐")
    
    # 姿态估计
    poses = pose_estimator.estimate(frame)
    logger.info(f"检测到 {len(poses)} 个姿态")
    
    print("✓ 图像检测示例完成")

def example_video_processing():
    """示例2: 视频处理"""
    print("\n" + "="*60)
    print("示例2: 视频处理（需要提供视频文件）")
    print("="*60)
    
    logger = setup_logger('example')
    
    # 这里只展示流程，实际需要真实视频文件
    logger.info("视频处理流程:")
    logger.info("1. 加载视频文件")
    logger.info("2. 逐帧检测篮球、人员、篮筐")
    logger.info("3. 进行姿态估计")
    logger.info("4. 分析投篮动作")
    logger.info("5. 生成分析报告")
    
    print("✓ 视频处理示例流程说明完成")

def example_shot_analysis():
    """示例3: 投篮动作分析"""
    print("\n" + "="*60)
    print("示例3: 投篮动作分析")
    print("="*60)
    
    logger = setup_logger('example')
    config = load_config()
    
    # 创建分析器
    pose_estimator = PoseEstimator()
    analyzer = ShotAnalyzer(pose_estimator, config)
    
    # 模拟关键点数据（17个关键点，每个3个值: x, y, confidence）
    # 这里创建一个标准投篮姿势的示例数据
    keypoints = np.array([
        [640, 200, 0.9],   # 0: nose
        [630, 190, 0.8],   # 1: left_eye
        [650, 190, 0.8],   # 2: right_eye
        [620, 195, 0.7],   # 3: left_ear
        [660, 195, 0.7],   # 4: right_ear
        [600, 250, 0.9],   # 5: left_shoulder
        [680, 250, 0.9],   # 6: right_shoulder
        [580, 320, 0.9],   # 7: left_elbow
        [720, 320, 0.9],   # 8: right_elbow
        [560, 230, 0.9],   # 9: left_wrist (投篮手)
        [740, 380, 0.8],   # 10: right_wrist
        [600, 400, 0.8],   # 11: left_hip
        [680, 400, 0.8],   # 12: right_hip
        [600, 550, 0.7],   # 13: left_knee
        [680, 550, 0.7],   # 14: right_knee
        [600, 700, 0.6],   # 15: left_ankle
        [680, 700, 0.6],   # 16: right_ankle
    ])
    
    # 分析投篮姿势
    analysis = analyzer.analyze_shooting_form(keypoints)
    
    logger.info("投篮分析结果:")
    logger.info(f"  投篮手: {analysis['shooting_hand']}")
    logger.info(f"  肘部角度: {analysis['elbow_angle']:.1f}°")
    logger.info(f"  姿势得分: {analysis['form_score']:.1f}/100")
    logger.info("  反馈建议:")
    for feedback in analysis['feedback']:
        logger.info(f"    {feedback}")
    
    print("✓ 投篮分析示例完成")

def example_database_usage():
    """示例4: 数据库使用"""
    print("\n" + "="*60)
    print("示例4: 数据库使用")
    print("="*60)
    
    from backend.database import Database
    
    logger = setup_logger('example')
    
    # 创建数据库实例
    db = Database('data/example_test.db')
    
    # 创建测试用户
    user_id = db.create_user(
        username='test_user',
        password='test_password',
        email='test@example.com',
        full_name='测试用户'
    )
    
    if user_id:
        logger.info(f"✓ 创建用户成功，ID: {user_id}")
        
        # 创建训练记录
        session_id = db.create_training_session(
            user_id=user_id,
            video_path='data/raw/test_video.mp4',
            notes='测试训练'
        )
        logger.info(f"✓ 创建训练记录成功，ID: {session_id}")
        
        # 更新训练记录
        db.update_training_session(
            session_id=session_id,
            total_shots=10,
            average_score=75.5
        )
        logger.info("✓ 更新训练记录成功")
        
        # 获取训练历史
        history = db.get_user_training_history(user_id)
        logger.info(f"✓ 获取训练历史: {len(history)} 条记录")
    else:
        logger.info("用户已存在或创建失败")
    
    print("✓ 数据库使用示例完成")

def main():
    """主函数 - 运行所有示例"""
    print("\n" + "🏀"*30)
    print("YOLOv8篮球训练辅助系统 - 使用示例")
    print("🏀"*30)
    
    try:
        # 运行各个示例
        example_image_detection()
        example_video_processing()
        example_shot_analysis()
        example_database_usage()
        
        print("\n" + "="*60)
        print("✓ 所有示例运行完成！")
        print("="*60)
        
        print("\n提示:")
        print("1. 使用 'python run.py' 启动完整的Web系统")
        print("2. 访问 http://localhost:5000 使用Web界面")
        print("3. 将真实的篮球训练视频放在 data/raw/ 目录进行测试")
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
