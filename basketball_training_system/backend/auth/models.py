"""
User models for Basketball Training System.
用户模型 - 支持教师和学生角色

Features:
- Teacher role: Management capabilities (view all students, manage classes)
- Student role: Training and practice features
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import hashlib
import secrets


class UserRole(Enum):
    """用户角色枚举"""
    TEACHER = "teacher"  # 教师 - 管理功能
    STUDENT = "student"  # 学生 - 训练功能


@dataclass
class User:
    """
    用户模型
    
    Attributes:
        user_id: 唯一用户ID
        username: 用户名
        password_hash: 密码哈希
        role: 用户角色（教师/学生）
        real_name: 真实姓名
        class_name: 班级名称（学生）或负责班级（教师）
        created_at: 创建时间
        last_login: 最后登录时间
        is_active: 是否激活
    """
    user_id: str
    username: str
    password_hash: str
    role: UserRole
    real_name: str = ""
    class_name: str = ""
    grade: str = ""  # 年级
    school: str = ""  # 学校
    student_id: str = ""  # 学号
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    # 教师特有字段
    managed_classes: List[str] = field(default_factory=list)  # 管理的班级列表
    # 学生特有字段
    teacher_id: Optional[str] = None  # 所属教师ID
    training_sessions: List[str] = field(default_factory=list)  # 训练记录ID列表
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希处理
        
        Args:
            password: 明文密码
            
        Returns:
            密码哈希值
        """
        salt = "basketball_training_salt"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    @staticmethod
    def generate_user_id() -> str:
        """生成唯一用户ID"""
        return secrets.token_hex(8)
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            
        Returns:
            密码是否正确
        """
        return self.password_hash == self.hash_password(password)
    
    def is_teacher(self) -> bool:
        """是否为教师"""
        return self.role == UserRole.TEACHER
    
    def is_student(self) -> bool:
        """是否为学生"""
        return self.role == UserRole.STUDENT
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典
        
        Args:
            include_sensitive: 是否包含敏感信息（密码哈希）
            
        Returns:
            用户信息字典
        """
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role.value,
            'real_name': self.real_name,
            'class_name': self.class_name,
            'grade': self.grade,
            'school': self.school,
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
        }
        
        if self.is_teacher():
            data['managed_classes'] = self.managed_classes
        else:
            data['teacher_id'] = self.teacher_id
            data['training_sessions'] = self.training_sessions
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        从字典创建用户对象
        
        Args:
            data: 用户信息字典
            
        Returns:
            User对象
        """
        role = UserRole(data.get('role', 'student'))
        
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now()
            
        last_login = data.get('last_login')
        if isinstance(last_login, str):
            last_login = datetime.fromisoformat(last_login)
        
        return cls(
            user_id=data.get('user_id', cls.generate_user_id()),
            username=data['username'],
            password_hash=data.get('password_hash', ''),
            role=role,
            real_name=data.get('real_name', ''),
            class_name=data.get('class_name', ''),
            grade=data.get('grade', ''),
            school=data.get('school', ''),
            student_id=data.get('student_id', ''),
            created_at=created_at,
            last_login=last_login,
            is_active=data.get('is_active', True),
            managed_classes=data.get('managed_classes', []),
            teacher_id=data.get('teacher_id'),
            training_sessions=data.get('training_sessions', [])
        )


@dataclass
class UserSession:
    """
    用户会话模型
    
    Attributes:
        session_id: 会话ID
        user_id: 用户ID
        created_at: 创建时间
        expires_at: 过期时间
    """
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    @staticmethod
    def generate_session_id() -> str:
        """生成唯一会话ID"""
        return secrets.token_hex(32)
    
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserSession':
        """从字典创建会话对象"""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        expires_at = data.get('expires_at')
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            
        return cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            created_at=created_at or datetime.now(),
            expires_at=expires_at
        )
