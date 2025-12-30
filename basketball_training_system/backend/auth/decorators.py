"""
Authentication decorators for Basketball Training System.
认证装饰器 - 用于API权限控制

Features:
- login_required: 需要登录
- role_required: 需要特定角色
- teacher_required: 需要教师角色
- student_required: 需要学生角色
"""

from functools import wraps
from flask import request, jsonify, current_app, g

from .models import UserRole


def login_required(f):
    """
    登录验证装饰器
    
    验证请求中是否包含有效的会话ID
    会话ID可以通过以下方式传递：
    - HTTP Header: X-Session-ID
    - Cookie: session_id
    - Query Parameter: session_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取认证服务
        auth_service = current_app.config.get('auth_service')
        if auth_service is None:
            return jsonify({
                'success': False,
                'error': '认证服务未初始化'
            }), 500
        
        # 获取会话ID
        session_id = (
            request.headers.get('X-Session-ID') or
            request.cookies.get('session_id') or
            request.args.get('session_id')
        )
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '请先登录'
            }), 401
        
        # 验证会话
        user = auth_service.get_user_by_session(session_id)
        if user is None:
            return jsonify({
                'success': False,
                'error': '会话已过期，请重新登录'
            }), 401
        
        # 将用户信息存储到g对象中
        g.current_user = user
        g.session_id = session_id
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*roles):
    """
    角色验证装饰器
    
    验证当前用户是否具有指定角色
    
    Args:
        roles: 允许的角色列表 (UserRole 或 字符串)
    
    Usage:
        @role_required(UserRole.TEACHER)
        def teacher_only_view():
            ...
        
        @role_required('teacher', 'admin')
        def admin_or_teacher_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            user = g.current_user
            
            # 转换角色参数
            allowed_roles = []
            for role in roles:
                if isinstance(role, UserRole):
                    allowed_roles.append(role)
                elif isinstance(role, str):
                    try:
                        allowed_roles.append(UserRole(role))
                    except ValueError:
                        pass
            
            # 检查用户角色
            if user.role not in allowed_roles:
                role_names = {
                    UserRole.TEACHER: '教师',
                    UserRole.STUDENT: '学生'
                }
                required_roles = ', '.join(role_names.get(r, r.value) for r in allowed_roles)
                return jsonify({
                    'success': False,
                    'error': f'权限不足，需要 {required_roles} 角色'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def teacher_required(f):
    """
    教师角色验证装饰器
    
    只允许教师访问
    """
    @wraps(f)
    @role_required(UserRole.TEACHER)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function


def student_required(f):
    """
    学生角色验证装饰器
    
    只允许学生访问
    """
    @wraps(f)
    @role_required(UserRole.STUDENT)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    获取当前登录用户
    
    Returns:
        当前用户对象，如果未登录则返回None
    """
    return getattr(g, 'current_user', None)


def is_teacher():
    """检查当前用户是否为教师"""
    user = get_current_user()
    return user is not None and user.is_teacher()


def is_student():
    """检查当前用户是否为学生"""
    user = get_current_user()
    return user is not None and user.is_student()
