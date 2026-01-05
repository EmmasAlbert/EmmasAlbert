"""
Database-based Authentication Service for Basketball Training System.
基于MySQL数据库的认证服务

Features:
- User registration with role assignment
- Login/logout functionality
- Session management
- MySQL database persistence
"""

import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets

# Import database modules
DB_AVAILABLE = False
DatabaseManager = None
DatabaseConfig = None
get_db_manager = None
DBUser = None
DBSession = None
DBTrainingPlan = None
DBFeedback = None

try:
    from ..database.db_manager import DatabaseManager, DatabaseConfig, get_db_manager
    from ..database.models import DBUser, DBSession, DBTrainingPlan, DBFeedback
    DB_AVAILABLE = True
except ImportError:
    pass


class AuthServiceDB:
    """
    基于数据库的认证服务类
    
    提供用户注册、登录、会话管理等功能，数据存储在MySQL数据库中
    """
    
    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        初始化认证服务
        
        Args:
            db_config: 数据库配置字典，包含 host, port, user, password, database 等
        """
        if not DB_AVAILABLE:
            raise ImportError("Database module not available. Please install pymysql.")
        
        if db_config:
            config = DatabaseConfig(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                user=db_config.get('user', 'root'),
                password=db_config.get('password', ''),
                database=db_config.get('database', 'basketball_training')
            )
            self.db = DatabaseManager(config)
        else:
            self.db = get_db_manager()
        
        # 初始化数据库表
        self.db.initialize_database()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希处理"""
        salt = "basketball_training_salt"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    @staticmethod
    def generate_user_id() -> str:
        """生成唯一用户ID"""
        return secrets.token_hex(8)
    
    @staticmethod
    def generate_session_id() -> str:
        """生成唯一会话ID"""
        return secrets.token_hex(32)
    
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
        # 验证用户名是否已存在
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return {
                'success': False,
                'error': '用户名已存在'
            }
        
        # 验证角色
        if role not in ('teacher', 'student'):
            return {
                'success': False,
                'error': '无效的用户角色，请选择 teacher 或 student'
            }
        
        # 验证密码强度
        if len(password) < 6:
            return {
                'success': False,
                'error': '密码长度至少6位'
            }
        
        # 如果是学生，验证教师ID
        if role == 'student' and teacher_id:
            teacher = self.db.get_user_by_id(teacher_id)
            if teacher is None:
                return {
                    'success': False,
                    'error': '指定的教师不存在'
                }
            if teacher.role != 'teacher':
                return {
                    'success': False,
                    'error': '指定的用户不是教师'
                }
        
        # 创建用户
        user = DBUser(
            user_id=self.generate_user_id(),
            username=username,
            password_hash=self.hash_password(password),
            role=role,
            real_name=real_name,
            class_name=class_name,
            grade=grade,
            school=school,
            teacher_id=teacher_id,
            created_at=datetime.now()
        )
        
        # 保存用户
        success = self.db.create_user(user)
        if not success:
            return {
                'success': False,
                'error': '创建用户失败'
            }
        
        # 如果学生关联了教师，更新教师的管理班级
        if role == 'student' and teacher_id and class_name:
            self.db.add_teacher_class(teacher_id, class_name, school)
        
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
        user = self.db.get_user_by_username(username)
        
        if user is None:
            return {
                'success': False,
                'error': '用户名或密码错误'
            }
        
        # 验证密码
        if user.password_hash != self.hash_password(password):
            return {
                'success': False,
                'error': '用户名或密码错误'
            }
        
        # 检查用户是否激活
        if not user.is_active:
            return {
                'success': False,
                'error': '账户已被禁用，请联系管理员'
            }
        
        # 创建会话
        session = DBSession(
            session_id=self.generate_session_id(),
            user_id=user.user_id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7)  # 7天有效期
        )
        
        # 更新最后登录时间
        self.db.update_user(user.user_id, {'last_login': datetime.now()})
        
        # 保存会话
        self.db.create_session(session)
        
        # 获取教师管理的班级
        managed_classes = []
        if user.role == 'teacher':
            classes = self.db.get_teacher_classes(user.user_id)
            managed_classes = [c['class_name'] for c in classes]
        
        user_dict = user.to_dict()
        if user.role == 'teacher':
            user_dict['managed_classes'] = managed_classes
        
        return {
            'success': True,
            'message': '登录成功',
            'session_id': session.session_id,
            'user': user_dict
        }
    
    def logout(self, session_id: str) -> Dict[str, Any]:
        """
        用户登出
        
        Args:
            session_id: 会话ID
            
        Returns:
            登出结果字典
        """
        self.db.delete_session(session_id)
        return {
            'success': True,
            'message': '已登出'
        }
    
    def get_user_by_session(self, session_id: str):
        """
        通过会话ID获取用户
        
        Args:
            session_id: 会话ID
            
        Returns:
            DBUser对象，如果会话无效则返回None
        """
        session = self.db.get_session(session_id)
        if session is None or session.is_expired():
            return None
        
        return self.db.get_user_by_id(session.user_id)
    
    def get_user_by_id(self, user_id: str):
        """
        通过用户ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            DBUser对象
        """
        return self.db.get_user_by_id(user_id)
    
    def get_students_by_teacher(self, teacher_id: str) -> List:
        """
        获取教师管理的所有学生
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            学生列表
        """
        return self.db.get_students_by_teacher(teacher_id)
    
    def get_students_by_class(self, class_name: str) -> List:
        """
        获取指定班级的所有学生
        
        Args:
            class_name: 班级名称
            
        Returns:
            学生列表
        """
        return self.db.get_students_by_class(class_name)
    
    def get_all_teachers(self) -> List:
        """获取所有教师"""
        return self.db.get_all_teachers()
    
    def get_all_students(self) -> List:
        """获取所有学生"""
        return self.db.get_all_students()
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            updates: 要更新的字段
            
        Returns:
            更新结果字典
        """
        user = self.db.get_user_by_id(user_id)
        if user is None:
            return {
                'success': False,
                'error': '用户不存在'
            }
        
        # 如果更新密码
        if 'password' in updates:
            updates['password_hash'] = self.hash_password(updates.pop('password'))
        
        success = self.db.update_user(user_id, updates)
        
        if success:
            user = self.db.get_user_by_id(user_id)
            return {
                'success': True,
                'message': '更新成功',
                'user': user.to_dict() if user else {}
            }
        
        return {
            'success': False,
            'error': '更新失败'
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
        student = self.db.get_user_by_id(student_id)
        teacher = self.db.get_user_by_id(teacher_id)
        
        if student is None or student.role != 'student':
            return {
                'success': False,
                'error': '学生不存在'
            }
        
        if teacher is None or teacher.role != 'teacher':
            return {
                'success': False,
                'error': '教师不存在'
            }
        
        # 更新学生的教师ID
        self.db.update_user(student_id, {'teacher_id': teacher_id})
        
        # 更新教师管理的班级
        if student.class_name:
            self.db.add_teacher_class(teacher_id, student.class_name, student.school)
        
        return {
            'success': True,
            'message': f'已将学生 {student.real_name or student.username} 分配给教师 {teacher.real_name or teacher.username}'
        }
    
    # ==================== 训练计划操作 ====================
    
    def get_user_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的训练计划
        
        Args:
            user_id: 用户ID
            
        Returns:
            训练计划列表
        """
        plans = self.db.get_training_plans_by_user(user_id)
        return [plan.to_dict() for plan in plans]
    
    def save_user_plan(self, user_id: str, plan: Dict[str, Any]) -> int:
        """
        保存用户的训练计划
        
        Args:
            user_id: 用户ID
            plan: 训练计划
            
        Returns:
            计划ID
        """
        db_plan = DBTrainingPlan(
            user_id=user_id,
            plan_name=plan.get('plan_name', ''),
            plan_type=plan.get('plan_type', 'daily'),
            target=plan.get('target', ''),
            status=plan.get('status', 'active'),
            created_at=datetime.now(),
            due_date=plan.get('due_date')
        )
        return self.db.create_training_plan(db_plan)
    
    def save_user_plans(self, user_id: str, plans: List[Dict[str, Any]]) -> None:
        """
        保存用户的所有训练计划（兼容JSON版本的接口）
        
        Args:
            user_id: 用户ID
            plans: 训练计划列表
        """
        for plan in plans:
            if not plan.get('id'):
                self.save_user_plan(user_id, plan)
    
    def update_training_plan(self, plan_id: int, updates: Dict[str, Any]) -> bool:
        """更新训练计划"""
        return self.db.update_training_plan(plan_id, updates)
    
    def delete_training_plan(self, plan_id: int) -> bool:
        """删除训练计划"""
        return self.db.delete_training_plan(plan_id)
    
    # ==================== 反馈操作 ====================
    
    def add_feedback(self, user_id: str, feedback: Dict[str, Any]) -> int:
        """
        为用户添加反馈
        
        Args:
            user_id: 学生用户ID
            feedback: 反馈内容
            
        Returns:
            反馈ID
        """
        db_feedback = DBFeedback(
            student_id=user_id,
            teacher_id=feedback.get('teacher_id', ''),
            teacher_name=feedback.get('teacher_name', ''),
            content=feedback.get('content', ''),
            created_at=datetime.now()
        )
        return self.db.create_feedback(db_feedback)
    
    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户收到的反馈
        
        Args:
            user_id: 用户ID
            
        Returns:
            反馈列表
        """
        feedback_list = self.db.get_feedback_by_student(user_id)
        return [fb.to_dict() for fb in feedback_list]
    
    def mark_feedback_read(self, feedback_id: int) -> bool:
        """标记反馈为已读"""
        return self.db.mark_feedback_as_read(feedback_id)
    
    # ==================== 训练记录操作 ====================
    
    def add_training_session(self, user_id: str, session_id: str) -> bool:
        """
        为学生添加训练记录关联（兼容JSON版本的接口）
        
        Args:
            user_id: 学生ID
            session_id: 训练会话ID
            
        Returns:
            是否成功
        """
        # 在数据库版本中，训练记录直接关联user_id，不需要额外操作
        return True
    
    def get_user_training_sessions(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取用户的训练记录
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            
        Returns:
            训练记录列表
        """
        sessions = self.db.get_training_sessions_by_user(user_id, limit)
        return [s.to_dict() for s in sessions]


def create_db_auth_service(db_config: Optional[Dict[str, Any]] = None) -> AuthServiceDB:
    """
    创建数据库认证服务实例
    
    Args:
        db_config: 数据库配置
        
    Returns:
        AuthServiceDB实例
    """
    return AuthServiceDB(db_config)
