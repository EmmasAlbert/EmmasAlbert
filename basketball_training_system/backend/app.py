"""
Flask后端主应用
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict
from flask import Flask, request, jsonify, session, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import Database
from utils.config_loader import load_config
from utils.logger import setup_logger

# 初始化Flask应用
# 设置正确的模板和静态文件目录 - 使用绝对路径
_current_file = os.path.abspath(__file__)
_backend_dir = os.path.dirname(_current_file)
_project_root = os.path.dirname(_backend_dir)
template_dir = os.path.join(_project_root, 'frontend', 'templates')
static_dir = os.path.join(_project_root, 'frontend', 'static')

# 打印路径信息用于调试
print(f"[DEBUG] Template dir: {template_dir}")
print(f"[DEBUG] Static dir: {static_dir}")
print(f"[DEBUG] Template dir exists: {os.path.exists(template_dir)}")
print(f"[DEBUG] Static dir exists: {os.path.exists(static_dir)}")

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir,
            static_url_path='/static')
app.secret_key = 'basketball_training_secret_key_2025'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
CORS(app)

# 加载配置
config = load_config()
logger = setup_logger('backend', log_file='logs/backend.log')

# 初始化数据库 - 使用绝对路径
_db_path = os.path.join(_project_root, 'data', 'basketball_training.db')
print(f"[DEBUG] Database path: {_db_path}")
db = Database(db_path=_db_path)

# 初始化模型（延迟加载）
basketball_detector = None
pose_estimator = None
shot_analyzer = None
hoop_detector = None

# 上传文件配置
UPLOAD_FOLDER = 'data/raw'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_models():
    """初始化模型"""
    global basketball_detector, pose_estimator, shot_analyzer, hoop_detector
    
    if basketball_detector is None:
        logger.info("初始化检测模型...")
        
        # 延迟导入，避免启动时加载所有依赖
        from models.basketball_detector import BasketballDetector
        from models.pose_estimator import PoseEstimator
        from models.shot_analyzer import ShotAnalyzer
        from models.hoop_detector import HoopDetector
        
        basketball_detector = BasketballDetector(
            model_path=config['model']['yolo']['model_path'],
            conf_threshold=config['model']['yolo']['conf_threshold'],
            device=config['model']['yolo']['device']
        )
        
        pose_estimator = PoseEstimator(
            model_path=config['model']['pose']['model_path'],
            conf_threshold=config['model']['pose']['conf_threshold'],
            device=config['model']['pose']['device']
        )
        
        shot_analyzer = ShotAnalyzer(pose_estimator, config)
        hoop_detector = HoopDetector()
        
        logger.info("模型初始化完成")


# ========== 用户认证API ==========

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册（支持教师和学生）"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'student')  # 默认为学生
        email = data.get('email')
        full_name = data.get('full_name')
        age = data.get('age')
        student_level = data.get('student_level')
        school_code = data.get('school_code')
        class_id = data.get('class_id')
        student_id = data.get('student_id')
        phone = data.get('phone')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        # 验证角色
        if role not in ['student', 'teacher']:
            return jsonify({'success': False, 'message': '角色无效'}), 400
        
        # 如果提供了学校代码，查找学校ID
        school_id = None
        if school_code:
            school = db.get_school_by_code(school_code)
            if school:
                school_id = school['id']
            else:
                return jsonify({'success': False, 'message': '学校代码不存在'}), 400
        
        user_id = db.create_user(
            username=username, 
            password=password, 
            role=role,
            email=email, 
            full_name=full_name,
            age=age, 
            student_level=student_level,
            school_id=school_id,
            class_id=class_id,
            student_id=student_id,
            phone=phone
        )
        
        if user_id:
            logger.info(f"新用户注册: {username} (角色: {role})")
            return jsonify({'success': True, 'message': '注册成功', 'user_id': user_id})
        else:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
            
    except Exception as e:
        logger.error(f"注册错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        user_info = db.verify_user(username, password)
        
        if user_info:
            session['user_id'] = user_info['id']
            session['username'] = user_info['username']
            session['role'] = user_info.get('role', 'student')
            logger.info(f"用户登录: {username} (角色: {user_info.get('role')})")
            return jsonify({'success': True, 'message': '登录成功', 'user': user_info})
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
            
    except Exception as e:
        logger.error(f"登录错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """获取当前用户信息"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    user_info = db.get_user_by_id(session['user_id'])
    return jsonify({'success': True, 'user': user_info})


@app.route('/api/user/profile', methods=['PUT'])
def update_profile():
    """更新用户个人资料"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.json
        
        # 允许更新的字段
        allowed_fields = ['email', 'full_name', 'age', 'phone', 
                         'student_id', 'avatar_url']
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if update_data:
            db.update_user_profile(session['user_id'], **update_data)
            logger.info(f"用户更新资料: {session['username']}")
            return jsonify({'success': True, 'message': '资料更新成功'})
        else:
            return jsonify({'success': False, 'message': '没有可更新的字段'}), 400
            
    except Exception as e:
        logger.error(f"更新资料错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/user/bind-school', methods=['POST'])
def bind_school():
    """绑定学校"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.json
        school_code = data.get('school_code')
        class_id = data.get('class_id')
        
        if not school_code:
            return jsonify({'success': False, 'message': '请提供学校代码'}), 400
        
        success = db.bind_school(session['user_id'], school_code, class_id)
        
        if success:
            logger.info(f"用户绑定学校: {session['username']} -> {school_code}")
            return jsonify({'success': True, 'message': '学校绑定成功'})
        else:
            return jsonify({'success': False, 'message': '学校代码无效'}), 400
            
    except Exception as e:
        logger.error(f"绑定学校错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 学校和班级API ==========

@app.route('/api/schools', methods=['GET'])
def get_schools():
    """获取所有学校列表"""
    schools = db.get_all_schools()
    return jsonify({'success': True, 'schools': schools})


@app.route('/api/schools/<school_code>/classes', methods=['GET'])
def get_school_classes(school_code):
    """获取学校的班级列表"""
    school = db.get_school_by_code(school_code)
    if not school:
        return jsonify({'success': False, 'message': '学校不存在'}), 404
    
    classes = db.get_classes_by_school(school['id'])
    return jsonify({'success': True, 'classes': classes})


@app.route('/api/schools', methods=['POST'])
def create_school():
    """创建学校（仅管理员）"""
    try:
        data = request.json
        school_code = data.get('school_code')
        school_name = data.get('school_name')
        province = data.get('province')
        city = data.get('city')
        
        if not school_code or not school_name:
            return jsonify({'success': False, 'message': '学校代码和名称不能为空'}), 400
        
        school_id = db.create_school(school_code, school_name, province, city)
        
        if school_id:
            return jsonify({'success': True, 'message': '学校创建成功', 'school_id': school_id})
        else:
            return jsonify({'success': False, 'message': '学校代码已存在'}), 400
            
    except Exception as e:
        logger.error(f"创建学校错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/classes', methods=['POST'])
def create_class():
    """创建班级（教师可用）"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if user.get('role') != 'teacher':
            return jsonify({'success': False, 'message': '只有教师可以创建班级'}), 403
        
        data = request.json
        school_id = data.get('school_id') or user.get('school_id')
        class_name = data.get('class_name')
        grade = data.get('grade')
        
        if not school_id or not class_name:
            return jsonify({'success': False, 'message': '学校ID和班级名称不能为空'}), 400
        
        class_id = db.create_class(school_id, class_name, grade)
        return jsonify({'success': True, 'message': '班级创建成功', 'class_id': class_id})
        
    except Exception as e:
        logger.error(f"创建班级错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 教师功能API ==========

@app.route('/api/teacher/students', methods=['GET'])
def get_teacher_students():
    """获取教师所属学校的学生列表"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if user.get('role') != 'teacher':
            return jsonify({'success': False, 'message': '只有教师可以访问此功能'}), 403
        
        if not user.get('school_id'):
            return jsonify({'success': False, 'message': '请先绑定学校'}), 400
        
        class_id = request.args.get('class_id', type=int)
        students = db.get_students_by_school(user['school_id'], class_id)
        
        return jsonify({'success': True, 'students': students})
        
    except Exception as e:
        logger.error(f"获取学生列表错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/teacher/search', methods=['GET'])
def search_students():
    """搜索学生（按学号或姓名）"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if user.get('role') != 'teacher':
            return jsonify({'success': False, 'message': '只有教师可以访问此功能'}), 403
        
        if not user.get('school_id'):
            return jsonify({'success': False, 'message': '请先绑定学校'}), 400
        
        query = request.args.get('q', '')
        if len(query) < 2:
            return jsonify({'success': False, 'message': '搜索关键词至少2个字符'}), 400
        
        students = db.search_students(user['school_id'], query)
        
        return jsonify({'success': True, 'students': students})
        
    except Exception as e:
        logger.error(f"搜索学生错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/teacher/student/<int:student_id>/stats', methods=['GET'])
def get_student_stats(student_id):
    """获取学生训练统计"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if user.get('role') != 'teacher':
            return jsonify({'success': False, 'message': '只有教师可以访问此功能'}), 403
        
        # 验证学生属于同一学校
        student = db.get_user_by_id(student_id)
        if not student or student.get('school_id') != user.get('school_id'):
            return jsonify({'success': False, 'message': '无权访问该学生数据'}), 403
        
        stats = db.get_student_stats(student_id)
        stats['student'] = student
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logger.error(f"获取学生统计错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/teacher/student/<int:student_id>/history', methods=['GET'])
def get_student_training_history(student_id):
    """获取学生训练历史"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if user.get('role') != 'teacher':
            return jsonify({'success': False, 'message': '只有教师可以访问此功能'}), 403
        
        # 验证学生属于同一学校
        student = db.get_user_by_id(student_id)
        if not student or student.get('school_id') != user.get('school_id'):
            return jsonify({'success': False, 'message': '无权访问该学生数据'}), 403
        
        limit = request.args.get('limit', 20, type=int)
        history = db.get_user_training_history(student_id, limit)
        
        return jsonify({'success': True, 'history': history, 'student': student})
        
    except Exception as e:
        logger.error(f"获取学生训练历史错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/teacher/feedback', methods=['POST'])
def add_feedback():
    """添加教师反馈"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        user = db.get_user_by_id(session['user_id'])
        if user.get('role') != 'teacher':
            return jsonify({'success': False, 'message': '只有教师可以添加反馈'}), 403
        
        data = request.json
        student_id = data.get('student_id')
        session_id = data.get('session_id')
        feedback_text = data.get('feedback')
        
        if not student_id or not feedback_text:
            return jsonify({'success': False, 'message': '学生ID和反馈内容不能为空'}), 400
        
        # 验证学生属于同一学校
        student = db.get_user_by_id(student_id)
        if not student or student.get('school_id') != user.get('school_id'):
            return jsonify({'success': False, 'message': '无权给该学生添加反馈'}), 403
        
        feedback_id = db.add_teacher_feedback(
            session['user_id'], student_id, feedback_text, session_id
        )
        
        logger.info(f"教师 {session['username']} 给学生 {student_id} 添加反馈")
        return jsonify({'success': True, 'message': '反馈添加成功', 'feedback_id': feedback_id})
        
    except Exception as e:
        logger.error(f"添加反馈错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/student/feedback', methods=['GET'])
def get_my_feedback():
    """获取学生收到的教师反馈"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        limit = request.args.get('limit', 10, type=int)
        feedback = db.get_student_feedback(session['user_id'], limit)
        
        return jsonify({'success': True, 'feedback': feedback})
        
    except Exception as e:
        logger.error(f"获取反馈错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 视频处理API ==========

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': '没有上传文件'}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 添加时间戳避免重名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{session['user_id']}_{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            logger.info(f"视频上传成功: {filename}")
            return jsonify({
                'success': True,
                'message': '上传成功',
                'filename': filename,
                'filepath': filepath
            })
        else:
            return jsonify({'success': False, 'message': '不支持的文件格式'}), 400
            
    except Exception as e:
        logger.error(f"上传错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/process/video', methods=['POST'])
def process_video():
    """处理视频 - 进行篮球检测和姿态分析"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        init_models()
        
        data = request.json
        video_path = data.get('video_path')
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'success': False, 'message': '视频文件不存在'}), 400
        
        # 获取用户信息（用于年龄适配）
        user_info = db.get_user_by_id(session['user_id'])
        
        # 创建训练记录
        session_id = db.create_training_session(
            user_id=session['user_id'],
            video_path=video_path
        )
        
        # 处理视频（传入用户信息）
        results = process_video_file(video_path, session_id, user_info)
        
        # 更新训练记录
        db.update_training_session(
            session_id=session_id,
            total_shots=results['total_shots'],
            average_score=results['average_score']
        )
        
        logger.info(f"视频处理完成: session_id={session_id}")
        
        return jsonify({
            'success': True,
            'message': '处理完成',
            'session_id': session_id,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"视频处理错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


def process_video_file(video_path: str, session_id: int, user_info: dict = None) -> dict:
    """
    处理视频文件，进行检测和分析
    
    Args:
        video_path: 视频文件路径
        session_id: 训练记录ID
        user_info: 用户信息
    
    Returns:
        处理结果字典
    """
    # 延迟导入
    import cv2
    import numpy as np
    from utils.video_utils import VideoProcessor, VideoWriter
    
    # 打开视频
    video_processor = VideoProcessor(video_path)
    
    # 创建输出视频
    output_path = f"outputs/videos/session_{session_id}_analyzed.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    video_writer = VideoWriter(
        output_path,
        video_processor.fps,
        video_processor.width,
        video_processor.height
    )
    
    shot_analyses = []
    frame_count = 0
    
    try:
        while True:
            success, frame = video_processor.read_frame()
            if not success:
                break
            
            frame_count += 1
            timestamp = frame_count / video_processor.fps
            
            # 每5帧处理一次
            if frame_count % 5 == 0:
                # 检测篮球和人
                basketball_detections, player_detections = basketball_detector.detect_basketball_and_players(frame)
                
                # 检测篮筐
                hoop_detections = hoop_detector.detect(frame)
                
                # 姿态估计
                poses = pose_estimator.estimate(frame)
                
                # 绘制检测结果
                frame = basketball_detector.draw_detections(frame, basketball_detections + player_detections)
                frame = hoop_detector.draw_detections(frame, hoop_detections)
                frame = pose_estimator.draw_pose(frame, poses)
                
                # 创建适配用户年龄的分析器
                from models.shot_analyzer import ShotAnalyzer
                user_adapted_analyzer = ShotAnalyzer(pose_estimator, config, user_info)
                
                # 分析投篮动作
                if poses and len(poses) > 0:
                    for pose in poses:
                        # 检查是否为投篮瞬间
                        basketball_pos = None
                        if basketball_detections:
                            ball = basketball_detections[0]
                            basketball_pos = (
                                (ball['bbox'][0] + ball['bbox'][2]) / 2,
                                (ball['bbox'][1] + ball['bbox'][3]) / 2
                            )
                        
                        if user_adapted_analyzer.is_shooting_moment(pose['keypoints'], basketball_pos):
                            analysis = user_adapted_analyzer.analyze_shooting_form(pose['keypoints'])
                            
                            if analysis['form_score'] > 0:
                                shot_analyses.append(analysis)
                                db.add_shot_analysis(session_id, timestamp, analysis)
                                
                                # 在画面上显示分析结果
                                y_offset = 30
                                for feedback in analysis['feedback'][:3]:
                                    cv2.putText(frame, feedback, (10, y_offset),
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                                    y_offset += 25
            
            # 写入帧
            video_writer.write_frame(frame)
    
    finally:
        video_processor.release()
        video_writer.release()
    
    # 生成报告（使用适配的分析器）
    if 'user_adapted_analyzer' in locals():
        report = user_adapted_analyzer.generate_report(shot_analyses)
    else:
        from models.shot_analyzer import ShotAnalyzer
        temp_analyzer = ShotAnalyzer(pose_estimator, config, user_info)
        report = temp_analyzer.generate_report(shot_analyses)
    
    return {
        'total_shots': report['total_shots'],
        'valid_shots': report.get('valid_shots', 0),
        'average_score': report['average_score'],
        'output_video': output_path,
        'report': report
    }


@app.route('/api/camera/frame', methods=['POST'])
def process_camera_frame():
    """处理摄像头帧"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        init_models()
        
        # 延迟导入
        import cv2
        import numpy as np
        import base64
        
        # 接收base64编码的图像
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': '没有图像数据'}), 400
        
        # 解码图像
        image_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 检测篮球和人
        basketball_detections, player_detections = basketball_detector.detect_basketball_and_players(frame)
        
        # 检测篮筐
        hoop_detections = hoop_detector.detect(frame)
        
        # 姿态估计
        poses = pose_estimator.estimate(frame)
        
        # 分析投篮（如果有姿态）
        analysis_result = None
        if poses and len(poses) > 0:
            pose = poses[0]
            basketball_pos = None
            if basketball_detections:
                ball = basketball_detections[0]
                basketball_pos = (
                    (ball['bbox'][0] + ball['bbox'][2]) / 2,
                    (ball['bbox'][1] + ball['bbox'][3]) / 2
                )
            
            if shot_analyzer.is_shooting_moment(pose['keypoints'], basketball_pos):
                analysis_result = shot_analyzer.analyze_shooting_form(pose['keypoints'])
        
        # 绘制检测结果
        frame = basketball_detector.draw_detections(frame, basketball_detections + player_detections)
        frame = hoop_detector.draw_detections(frame, hoop_detections)
        frame = pose_estimator.draw_pose(frame, poses)
        
        # 如果有分析结果，绘制反馈
        if analysis_result:
            y_offset = 30
            for feedback in analysis_result['feedback'][:3]:
                cv2.putText(frame, feedback, (10, y_offset),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y_offset += 25
        
        # 编码返回
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{frame_base64}',
            'detections': {
                'basketball': len(basketball_detections),
                'players': len(player_detections),
                'hoops': len(hoop_detections),
                'poses': len(poses)
            },
            'analysis': analysis_result
        })
        
    except Exception as e:
        logger.error(f"摄像头帧处理错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 训练历史API ==========

@app.route('/api/training/history', methods=['GET'])
def get_training_history():
    """获取训练历史"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        limit = request.args.get('limit', 10, type=int)
        history = db.get_user_training_history(session['user_id'], limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"获取训练历史错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/training/session/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """获取训练记录详情"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        analysis = db.get_session_analysis(session_id)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"获取训练详情错误: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 页面路由 ==========

@app.route('/')
def index():
    """主页 - 登录页"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """注册页面"""
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """主界面（需要登录）"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/profile')
def profile_page():
    """个人资料页面"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('profile.html')

@app.route('/teacher')
def teacher_dashboard():
    """教师控制台"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = db.get_user_by_id(session['user_id'])
    if user.get('role') != 'teacher':
        return redirect(url_for('dashboard'))
    
    return render_template('teacher.html')

@app.route('/outputs/<path:filename>')
def serve_output(filename):
    """提供输出文件（处理后的视频等）"""
    output_dir = os.path.join(_project_root, 'outputs', 'videos')
    return send_from_directory(output_dir, filename)

@app.route('/debug/paths')
def debug_paths():
    """调试路由 - 显示路径信息"""
    import os
    return jsonify({
        'template_folder': app.template_folder,
        'static_folder': app.static_folder,
        'template_exists': os.path.exists(app.template_folder),
        'static_exists': os.path.exists(app.static_folder),
        'static_css_exists': os.path.exists(os.path.join(app.static_folder, 'css', 'style.css')),
        'static_js_exists': os.path.exists(os.path.join(app.static_folder, 'js', 'main.js')),
        'static_css_auth_exists': os.path.exists(os.path.join(app.static_folder, 'css', 'auth.css')),
        'static_js_auth_exists': os.path.exists(os.path.join(app.static_folder, 'js', 'auth.js')),
        'working_dir': os.getcwd(),
        'file_location': __file__
    })


if __name__ == '__main__':
    logger.info("启动Basketball Training System后端服务...")
    app.run(
        host=config['server']['host'],
        port=config['server']['port'],
        debug=config['server']['debug']
    )
