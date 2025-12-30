"""
Authentication API Routes for Basketball Training System.
认证API路由 - 用户注册、登录、管理

Endpoints:
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/logout - 用户登出
- GET /api/auth/profile - 获取当前用户信息
- PUT /api/auth/profile - 更新用户信息
- GET /api/auth/teachers - 获取教师列表（用于学生注册）
- GET /api/auth/students - 获取学生列表（教师查看）
- GET /api/auth/students/<class_name> - 获取班级学生列表
"""

from flask import Blueprint, request, jsonify, current_app, g, make_response

from .decorators import login_required, teacher_required, get_current_user
from .models import UserRole

# 创建蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    
    Request Body:
        - username: 用户名 (必填)
        - password: 密码 (必填，至少6位)
        - role: 角色 ('teacher' 或 'student') (必填)
        - real_name: 真实姓名
        - class_name: 班级名称
        - grade: 年级
        - school: 学校
        - teacher_id: 所属教师ID（学生注册时可选）
    
    Response:
        - success: 是否成功
        - message: 提示信息
        - user: 用户信息（成功时）
    """
    auth_service = current_app.config.get('auth_service')
    if auth_service is None:
        return jsonify({
            'success': False,
            'error': '认证服务未初始化'
        }), 500
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '请求数据为空'
        }), 400
    
    # 验证必填字段
    required_fields = ['username', 'password', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'error': f'缺少必填字段: {field}'
            }), 400
    
    result = auth_service.register(
        username=data['username'],
        password=data['password'],
        role=data['role'],
        real_name=data.get('real_name', ''),
        class_name=data.get('class_name', ''),
        grade=data.get('grade', ''),
        school=data.get('school', ''),
        teacher_id=data.get('teacher_id')
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    Request Body:
        - username: 用户名
        - password: 密码
    
    Response:
        - success: 是否成功
        - session_id: 会话ID（成功时）
        - user: 用户信息（成功时）
    """
    auth_service = current_app.config.get('auth_service')
    if auth_service is None:
        return jsonify({
            'success': False,
            'error': '认证服务未初始化'
        }), 500
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '请求数据为空'
        }), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'error': '用户名和密码不能为空'
        }), 400
    
    result = auth_service.login(username, password)
    
    if result['success']:
        response = make_response(jsonify(result))
        # 设置Cookie - 在开发环境中secure=False，生产环境应设为True
        # secure标志确保cookie只在HTTPS连接中传输
        is_secure = current_app.config.get('SESSION_COOKIE_SECURE', False)
        response.set_cookie(
            'session_id',
            result['session_id'],
            max_age=7*24*60*60,  # 7天
            httponly=True,
            samesite='Lax',
            secure=is_secure
        )
        return response
    else:
        return jsonify(result), 401


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    用户登出
    
    需要登录状态
    """
    auth_service = current_app.config.get('auth_service')
    session_id = g.session_id
    
    result = auth_service.logout(session_id)
    
    response = make_response(jsonify(result))
    response.delete_cookie('session_id')
    return response


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    获取当前用户信息
    
    需要登录状态
    """
    user = get_current_user()
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    更新当前用户信息
    
    Request Body:
        - real_name: 真实姓名
        - class_name: 班级
        - grade: 年级
        - school: 学校
        - password: 新密码（可选）
    """
    auth_service = current_app.config.get('auth_service')
    user = get_current_user()
    
    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'error': '请求数据为空'
        }), 400
    
    result = auth_service.update_user(user.user_id, data)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@auth_bp.route('/teachers', methods=['GET'])
def get_teachers():
    """
    获取教师列表
    
    用于学生注册时选择所属教师
    """
    auth_service = current_app.config.get('auth_service')
    if auth_service is None:
        return jsonify({
            'success': False,
            'error': '认证服务未初始化'
        }), 500
    
    teachers = auth_service.get_all_teachers()
    
    return jsonify({
        'success': True,
        'teachers': [
            {
                'user_id': t.user_id,
                'username': t.username,
                'real_name': t.real_name,
                'school': t.school,
                'managed_classes': t.managed_classes
            }
            for t in teachers
        ]
    })


@auth_bp.route('/students', methods=['GET'])
@teacher_required
def get_students():
    """
    获取学生列表（教师专用）
    
    教师可以查看自己管理的所有学生
    
    Query Parameters:
        - class_name: 按班级筛选（可选）
        - all: 是否查看所有学生（可选，默认只看自己的学生）
    """
    auth_service = current_app.config.get('auth_service')
    user = get_current_user()
    
    class_name = request.args.get('class_name')
    view_all = request.args.get('all', 'false').lower() == 'true'
    
    if class_name:
        students = auth_service.get_students_by_class(class_name)
    elif view_all:
        students = auth_service.get_all_students()
    else:
        students = auth_service.get_students_by_teacher(user.user_id)
    
    return jsonify({
        'success': True,
        'students': [s.to_dict() for s in students],
        'count': len(students)
    })


@auth_bp.route('/students/<student_id>/assign', methods=['POST'])
@teacher_required
def assign_student(student_id):
    """
    将学生分配给当前教师
    
    Path Parameters:
        - student_id: 学生ID
    """
    auth_service = current_app.config.get('auth_service')
    teacher = get_current_user()
    
    result = auth_service.assign_student_to_teacher(student_id, teacher.user_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    检查认证状态
    
    用于前端判断用户是否已登录
    """
    auth_service = current_app.config.get('auth_service')
    if auth_service is None:
        return jsonify({
            'authenticated': False,
            'error': '认证服务未初始化'
        })
    
    session_id = (
        request.headers.get('X-Session-ID') or
        request.cookies.get('session_id') or
        request.args.get('session_id')
    )
    
    if not session_id:
        return jsonify({
            'authenticated': False
        })
    
    user = auth_service.get_user_by_session(session_id)
    
    if user is None:
        return jsonify({
            'authenticated': False
        })
    
    return jsonify({
        'authenticated': True,
        'user': user.to_dict()
    })
