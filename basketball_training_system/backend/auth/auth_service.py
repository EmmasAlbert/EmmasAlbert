"""
Authentication Service for Basketball Training System.
认证服务 - 处理用户注册、登录、会话管理

Features:
- User registration with role assignment
- Login/logout functionality
- Session management
- User data persistence (JSON file storage)
- Secure password hashing with bcrypt
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .models import User, UserRole, UserSession, PasswordPolicy

# 设置日志
logger = logging.getLogger(__name__)


class AuthService:
    """
    认证服务类
    
    提供用户注册、登录、会话管理等功能
    """
    
    def __init__(self, data_dir: str = 'data'):
        """
        初始化认证服务
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.sessions_file = os.path.join(data_dir, 'sessions.json')
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 加载用户和会话数据
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, UserSession] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """从文件加载用户和会话数据"""
        # 加载用户数据
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_data in data.get('users', []):
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user
                logger.info(f"已加载 {len(self.users)} 个用户")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"无法加载用户数据: {e}")
        
        # 加载会话数据
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = UserSession.from_dict(session_data)
                        if not session.is_expired():
                            self.sessions[session.session_id] = session
                logger.info(f"已加载 {len(self.sessions)} 个活跃会话")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"无法加载会话数据: {e}")
    
    def _save_users(self) -> None:
        """保存用户数据到文件"""
        data = {
            'users': [user.to_dict(include_sensitive=True) for user in self.users.values()]
        }
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_sessions(self) -> None:
        """保存会话数据到文件"""
        # 清理过期会话
        valid_sessions = {
            sid: session for sid, session in self.sessions.items()
            if not session.is_expired()
        }
        self.sessions = valid_sessions
        
        data = {
            'sessions': [session.to_dict() for session in self.sessions.values()]
        }
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def register(
        self,
        username: str,
        password: str,
        role: str,
        real_name: str = "",
        class_name: str = "",
        grade: str = "",
        school: str = "",
        teacher_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            role: 角色 ('teacher' 或 'student')
            real_name: 真实姓名
            class_name: 班级名称
            grade: 年级
            school: 学校
            teacher_id: 所属教师ID（学生注册时）
            
        Returns:
            注册结果字典
        """
        # 验证用户名格式
        if not username or len(username) < 3:
            return {
                'success': False,
                'error': '用户名至少3个字符'
            }
        
        if len(username) > 32:
            return {
                'success': False,
                'error': '用户名不能超过32个字符'
            }
        
        # 验证用户名是否已存在
        for user in self.users.values():
            if user.username == username:
                logger.warning(f"注册失败: 用户名 {username} 已存在")
                return {
                    'success': False,
                    'error': '用户名已存在'
                }
        
        # 验证角色
        try:
            user_role = UserRole(role)
        except ValueError:
            return {
                'success': False,
                'error': '无效的用户角色，请选择 teacher 或 student'
            }
        
        # 验证密码强度（使用密码策略）
        is_valid, error_msg = PasswordPolicy.validate(password)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg
            }
        
        # 如果是学生，验证教师ID
        if user_role == UserRole.STUDENT and teacher_id:
            if teacher_id not in self.users:
                return {
                    'success': False,
                    'error': '指定的教师不存在'
                }
            teacher = self.users[teacher_id]
            if not teacher.is_teacher():
                return {
                    'success': False,
                    'error': '指定的用户不是教师'
                }
        
        # 创建用户
        user = User(
            user_id=User.generate_user_id(),
            username=username,
            password_hash=User.hash_password(password),
            role=user_role,
            real_name=real_name,
            class_name=class_name,
            grade=grade,
            school=school,
            teacher_id=teacher_id
        )
        
        # 保存用户
        self.users[user.user_id] = user
        self._save_users()
        
        # 如果学生关联了教师，更新教师的管理班级
        if user_role == UserRole.STUDENT and teacher_id and class_name:
            teacher = self.users[teacher_id]
            if class_name not in teacher.managed_classes:
                teacher.managed_classes.append(class_name)
                self._save_users()
        
        logger.info(f"用户注册成功: {username} (角色: {role})")
        
        return {
            'success': True,
            'message': '注册成功',
            'user': user.to_dict()
        }
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            登录结果字典，包含会话信息
        """
        # 查找用户
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if user is None:
            logger.warning(f"登录失败: 用户名 {username} 不存在")
            return {
                'success': False,
                'error': '用户名或密码错误'
            }
        
        # 验证密码
        if not user.verify_password(password):
            logger.warning(f"登录失败: 用户 {username} 密码错误")
            return {
                'success': False,
                'error': '用户名或密码错误'
            }
        
        # 检查用户是否激活
        if not user.is_active:
            logger.warning(f"登录失败: 用户 {username} 已被禁用")
            return {
                'success': False,
                'error': '账户已被禁用，请联系管理员'
            }
        
        # 创建会话
        session = UserSession(
            session_id=UserSession.generate_session_id(),
            user_id=user.user_id,
            expires_at=datetime.now() + timedelta(days=7)  # 7天有效期
        )
        
        # 更新最后登录时间
        user.last_login = datetime.now()
        self._save_users()
        
        # 保存会话
        self.sessions[session.session_id] = session
        self._save_sessions()
        
        logger.info(f"用户登录成功: {username}")
        
        return {
            'success': True,
            'message': '登录成功',
            'session_id': session.session_id,
            'user': user.to_dict()
        }
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """
        用户登出
        
        Args:
            session_id: 会话ID
            
        Returns:
            登出结果字典
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            logger.info(f"会话已登出: {session_id[:8]}...")
        
        return {
            'success': True,
            'message': '已登出'
        }
    
    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """
        通过会话ID获取用户
        
        Args:
            session_id: 会话ID
            
        Returns:
            User对象，如果会话无效则返回None
        """
        session = self.sessions.get(session_id)
        if session is None or session.is_expired():
            return None
        
        return self.users.get(session.user_id)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        通过用户ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User对象
        """
        return self.users.get(user_id)
    
    def get_students_by_teacher(self, teacher_id: str) -> List[User]:
        """
        获取教师管理的所有学生
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            学生列表
        """
        return [
            user for user in self.users.values()
            if user.is_student() and user.teacher_id == teacher_id
        ]
    
    def get_students_by_class(self, class_name: str) -> List[User]:
        """
        获取指定班级的所有学生
        
        Args:
            class_name: 班级名称
            
        Returns:
            学生列表
        """
        return [
            user for user in self.users.values()
            if user.is_student() and user.class_name == class_name
        ]
    
    def get_all_teachers(self) -> List[User]:
        """获取所有教师"""
        return [user for user in self.users.values() if user.is_teacher()]
    
    def get_all_students(self) -> List[User]:
        """获取所有学生"""
        return [user for user in self.users.values() if user.is_student()]
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            updates: 要更新的字段
            
        Returns:
            更新结果字典
        """
        user = self.users.get(user_id)
        if user is None:
            return {
                'success': False,
                'error': '用户不存在'
            }
        
        # 允许更新的字段
        allowed_fields = ['real_name', 'class_name', 'grade', 'school', 'is_active', 'student_id', 'teacher_id']
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        # 如果更新密码
        if 'password' in updates:
            user.password_hash = User.hash_password(updates['password'])
        
        self._save_users()
        
        return {
            'success': True,
            'message': '更新成功',
            'user': user.to_dict()
        }
    
    def assign_student_to_teacher(self, student_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        将学生分配给教师
        
        Args:
            student_id: 学生ID
            teacher_id: 教师ID
            
        Returns:
            操作结果字典
        """
        student = self.users.get(student_id)
        teacher = self.users.get(teacher_id)
        
        if student is None or not student.is_student():
            return {
                'success': False,
                'error': '学生不存在'
            }
        
        if teacher is None or not teacher.is_teacher():
            return {
                'success': False,
                'error': '教师不存在'
            }
        
        student.teacher_id = teacher_id
        
        # 更新教师管理的班级
        if student.class_name and student.class_name not in teacher.managed_classes:
            teacher.managed_classes.append(student.class_name)
        
        self._save_users()
        
        return {
            'success': True,
            'message': f'已将学生 {student.real_name or student.username} 分配给教师 {teacher.real_name or teacher.username}'
        }
    
    def add_training_session(self, user_id: str, session_id: str) -> bool:
        """
        为学生添加训练记录
        
        Args:
            user_id: 学生ID
            session_id: 训练会话ID
            
        Returns:
            是否成功
        """
        user = self.users.get(user_id)
        if user is None or not user.is_student():
            return False
        
        if session_id not in user.training_sessions:
            user.training_sessions.append(session_id)
            self._save_users()
        
        return True
    
    def get_user_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的训练计划
        
        Args:
            user_id: 用户ID
            
        Returns:
            训练计划列表
        """
        plans_file = os.path.join(self.data_dir, f'plans_{user_id}.json')
        if os.path.exists(plans_file):
            try:
                with open(plans_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('plans', [])
            except (json.JSONDecodeError, KeyError):
                pass
        return []
    
    def save_user_plans(self, user_id: str, plans: List[Dict[str, Any]]) -> None:
        """
        保存用户的训练计划
        
        Args:
            user_id: 用户ID
            plans: 训练计划列表
        """
        plans_file = os.path.join(self.data_dir, f'plans_{user_id}.json')
        with open(plans_file, 'w', encoding='utf-8') as f:
            json.dump({'plans': plans}, f, ensure_ascii=False, indent=2)
    
    def add_feedback(self, user_id: str, feedback: Dict[str, Any]) -> None:
        """
        为用户添加反馈
        
        Args:
            user_id: 用户ID
            feedback: 反馈内容
        """
        feedback_file = os.path.join(self.data_dir, f'feedback_{user_id}.json')
        existing = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing = data.get('feedback', [])
            except (json.JSONDecodeError, KeyError):
                pass
        
        existing.append(feedback)
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump({'feedback': existing}, f, ensure_ascii=False, indent=2)
    
    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户收到的反馈
        
        Args:
            user_id: 用户ID
            
        Returns:
            反馈列表
        """
        feedback_file = os.path.join(self.data_dir, f'feedback_{user_id}.json')
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('feedback', [])
            except (json.JSONDecodeError, KeyError):
                pass
        return []
