"""
Database Models for Basketball Training System.
数据库模型 - 定义MySQL表结构

Tables:
- users: 用户信息表
- sessions: 登录会话表
- training_sessions: 训练记录表
- training_plans: 训练计划表
- feedback: 教师反馈表
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(Enum):
    """用户角色枚举"""
    TEACHER = "teacher"
    STUDENT = "student"


@dataclass
class DBUser:
    """
    用户数据库模型
    
    对应 users 表
    """
    id: int = 0
    user_id: str = ""
    username: str = ""
    password_hash: str = ""
    role: str = "student"
    real_name: str = ""
    class_name: str = ""
    grade: str = ""
    school: str = ""
    student_id: str = ""
    teacher_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """转换为字典"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'real_name': self.real_name,
            'class_name': self.class_name,
            'grade': self.grade,
            'school': self.school,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data


@dataclass
class DBSession:
    """
    登录会话数据库模型
    
    对应 sessions 表
    """
    id: int = 0
    session_id: str = ""
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


@dataclass
class DBTrainingSession:
    """
    训练记录数据库模型
    
    对应 training_sessions 表
    """
    id: int = 0
    session_id: str = ""
    user_id: str = ""
    date: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    total_shots: int = 0
    shooting_percentage: float = 0.0
    average_elbow_angle: Optional[float] = None
    average_knee_angle: Optional[float] = None
    form_quality_score: float = 0.0
    raw_data: str = "[]"  # JSON string
    improvements: str = "[]"  # JSON string
    areas_to_work: str = "[]"  # JSON string
    
    def to_dict(self) -> dict:
        """转换为字典"""
        import json
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'duration_seconds': self.duration_seconds,
            'total_shots': self.total_shots,
            'shooting_percentage': self.shooting_percentage,
            'average_elbow_angle': self.average_elbow_angle,
            'average_knee_angle': self.average_knee_angle,
            'form_quality_score': self.form_quality_score,
            'raw_data': json.loads(self.raw_data) if self.raw_data else [],
            'improvements': json.loads(self.improvements) if self.improvements else [],
            'areas_to_work': json.loads(self.areas_to_work) if self.areas_to_work else []
        }


@dataclass
class DBTrainingPlan:
    """
    训练计划数据库模型
    
    对应 training_plans 表
    """
    id: int = 0
    user_id: str = ""
    plan_name: str = ""
    plan_type: str = ""  # daily, weekly, monthly
    target: str = ""
    status: str = "active"  # active, completed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_name': self.plan_name,
            'plan_type': self.plan_type,
            'target': self.target,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class DBFeedback:
    """
    教师反馈数据库模型
    
    对应 feedback 表
    """
    id: int = 0
    student_id: str = ""
    teacher_id: str = ""
    teacher_name: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_read: bool = False
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher_name,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_read': self.is_read
        }


# SQL语句用于创建表
CREATE_TABLES_SQL = """
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) UNIQUE NOT NULL,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role ENUM('teacher', 'student') DEFAULT 'student',
    real_name VARCHAR(64) DEFAULT '',
    class_name VARCHAR(64) DEFAULT '',
    grade VARCHAR(32) DEFAULT '',
    school VARCHAR(128) DEFAULT '',
    student_id VARCHAR(64) DEFAULT '',
    teacher_id VARCHAR(64) DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME DEFAULT NULL,
    INDEX idx_username (username),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_school_class (school, class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 登录会话表
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(128) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 训练记录表
CREATE TABLE IF NOT EXISTS training_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_seconds FLOAT DEFAULT 0,
    total_shots INT DEFAULT 0,
    shooting_percentage FLOAT DEFAULT 0,
    average_elbow_angle FLOAT DEFAULT NULL,
    average_knee_angle FLOAT DEFAULT NULL,
    form_quality_score FLOAT DEFAULT 0,
    raw_data JSON,
    improvements JSON,
    areas_to_work JSON,
    INDEX idx_user_id (user_id),
    INDEX idx_date (date),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 训练计划表
CREATE TABLE IF NOT EXISTS training_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    plan_name VARCHAR(128) NOT NULL,
    plan_type ENUM('daily', 'weekly', 'monthly') DEFAULT 'daily',
    target TEXT,
    status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATE DEFAULT NULL,
    completed_at DATETIME DEFAULT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 教师反馈表
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(64) NOT NULL,
    teacher_id VARCHAR(64) NOT NULL,
    teacher_name VARCHAR(64) DEFAULT '',
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    INDEX idx_student_id (student_id),
    INDEX idx_teacher_id (teacher_id),
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 教师管理班级关联表
CREATE TABLE IF NOT EXISTS teacher_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id VARCHAR(64) NOT NULL,
    class_name VARCHAR(64) NOT NULL,
    school VARCHAR(128) DEFAULT '',
    UNIQUE KEY idx_teacher_class (teacher_id, class_name, school),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
