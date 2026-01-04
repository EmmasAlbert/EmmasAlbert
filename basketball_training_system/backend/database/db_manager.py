"""
Database Manager for Basketball Training System.
数据库管理器 - MySQL连接和数据操作

Features:
- Connection pool management
- CRUD operations for all tables
- Transaction support
- Automatic table creation
"""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager

try:
    import pymysql
    from pymysql.cursors import DictCursor
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    pymysql = None
    DictCursor = None

from .models import (
    DBUser, DBSession, DBTrainingSession, 
    DBTrainingPlan, DBFeedback, CREATE_TABLES_SQL
)


class DatabaseConfig:
    """数据库配置"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 3306,
        user: str = 'root',
        password: str = '',
        database: str = 'basketball_training',
        charset: str = 'utf8mb4'
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量创建配置"""
        return cls(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', '3306')),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', ''),
            database=os.environ.get('DB_NAME', 'basketball_training'),
            charset=os.environ.get('DB_CHARSET', 'utf8mb4')
        )
    
    def to_dict(self) -> dict:
        """转换为pymysql连接参数"""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'charset': self.charset,
            'cursorclass': DictCursor
        }


class DatabaseManager:
    """
    数据库管理器
    
    提供所有数据库操作的统一接口
    """
    
    _instance: Optional['DatabaseManager'] = None
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        初始化数据库管理器
        
        Args:
            config: 数据库配置，如果为None则从环境变量读取
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql is not installed. Install it with: pip install pymysql")
        
        self.config = config or DatabaseConfig.from_env()
        self._connection = None
        self._initialized = False
    
    @classmethod
    def get_instance(cls, config: Optional[DatabaseConfig] = None) -> 'DatabaseManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance
    
    def connect(self):
        """获取数据库连接"""
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(**self.config.to_dict())
        return self._connection
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def get_cursor(self):
        """获取游标的上下文管理器"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def initialize_database(self) -> None:
        """初始化数据库表"""
        if self._initialized:
            return
        
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # 分割SQL语句并逐个执行
            statements = CREATE_TABLES_SQL.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
            
            conn.commit()
            self._initialized = True
            print("数据库表初始化成功")
        except Exception as e:
            conn.rollback()
            raise Exception(f"数据库初始化失败: {e}")
        finally:
            cursor.close()
    
    # ==================== 用户操作 ====================
    
    def create_user(self, user: DBUser) -> bool:
        """创建用户"""
        with self.get_cursor() as cursor:
            sql = """
                INSERT INTO users (
                    user_id, username, password_hash, role, real_name,
                    class_name, grade, school, student_id, teacher_id,
                    is_active, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(sql, (
                user.user_id, user.username, user.password_hash, user.role,
                user.real_name, user.class_name, user.grade, user.school,
                user.student_id, user.teacher_id, user.is_active, user.created_at
            ))
            return cursor.rowcount > 0
    
    def get_user_by_id(self, user_id: str) -> Optional[DBUser]:
        """通过用户ID获取用户"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    def get_user_by_username(self, username: str) -> Optional[DBUser]:
        """通过用户名获取用户"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户信息"""
        if not updates:
            return False
        
        allowed_fields = [
            'real_name', 'class_name', 'grade', 'school', 'student_id',
            'teacher_id', 'is_active', 'last_login', 'password_hash'
        ]
        
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                values.append(value)
        
        if not set_clauses:
            return False
        
        values.append(user_id)
        
        with self.get_cursor() as cursor:
            sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = %s"
            cursor.execute(sql, values)
            return cursor.rowcount > 0
    
    def get_all_teachers(self) -> List[DBUser]:
        """获取所有教师"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM users WHERE role = 'teacher'"
            cursor.execute(sql)
            return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def get_all_students(self) -> List[DBUser]:
        """获取所有学生"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM users WHERE role = 'student'"
            cursor.execute(sql)
            return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def get_students_by_teacher(self, teacher_id: str) -> List[DBUser]:
        """获取教师管理的所有学生"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM users WHERE role = 'student' AND teacher_id = %s"
            cursor.execute(sql, (teacher_id,))
            return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def get_students_by_class(self, class_name: str, school: str = '') -> List[DBUser]:
        """获取指定班级的学生"""
        with self.get_cursor() as cursor:
            if school:
                sql = "SELECT * FROM users WHERE role = 'student' AND class_name = %s AND school = %s"
                cursor.execute(sql, (class_name, school))
            else:
                sql = "SELECT * FROM users WHERE role = 'student' AND class_name = %s"
                cursor.execute(sql, (class_name,))
            return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def _row_to_user(self, row: dict) -> DBUser:
        """将数据库行转换为用户对象"""
        return DBUser(
            id=row['id'],
            user_id=row['user_id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=row['role'],
            real_name=row['real_name'] or '',
            class_name=row['class_name'] or '',
            grade=row['grade'] or '',
            school=row['school'] or '',
            student_id=row['student_id'] or '',
            teacher_id=row['teacher_id'],
            is_active=row['is_active'],
            created_at=row['created_at'],
            last_login=row['last_login']
        )
    
    # ==================== 会话操作 ====================
    
    def create_session(self, session: DBSession) -> bool:
        """创建登录会话"""
        with self.get_cursor() as cursor:
            sql = """
                INSERT INTO sessions (session_id, user_id, created_at, expires_at)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                session.session_id, session.user_id,
                session.created_at, session.expires_at
            ))
            return cursor.rowcount > 0
    
    def get_session(self, session_id: str) -> Optional[DBSession]:
        """获取会话"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM sessions WHERE session_id = %s"
            cursor.execute(sql, (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return DBSession(
                id=row['id'],
                session_id=row['session_id'],
                user_id=row['user_id'],
                created_at=row['created_at'],
                expires_at=row['expires_at']
            )
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        with self.get_cursor() as cursor:
            sql = "DELETE FROM sessions WHERE session_id = %s"
            cursor.execute(sql, (session_id,))
            return cursor.rowcount > 0
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        with self.get_cursor() as cursor:
            sql = "DELETE FROM sessions WHERE expires_at < %s"
            cursor.execute(sql, (datetime.now(),))
            return cursor.rowcount
    
    # ==================== 训练记录操作 ====================
    
    def create_training_session(self, session: DBTrainingSession) -> bool:
        """创建训练记录"""
        with self.get_cursor() as cursor:
            sql = """
                INSERT INTO training_sessions (
                    session_id, user_id, date, duration_seconds, total_shots,
                    shooting_percentage, average_elbow_angle, average_knee_angle,
                    form_quality_score, raw_data, improvements, areas_to_work
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                session.session_id, session.user_id, session.date,
                session.duration_seconds, session.total_shots,
                session.shooting_percentage, session.average_elbow_angle,
                session.average_knee_angle, session.form_quality_score,
                session.raw_data, session.improvements, session.areas_to_work
            ))
            return cursor.rowcount > 0
    
    def get_training_sessions_by_user(
        self, 
        user_id: str, 
        limit: int = 100
    ) -> List[DBTrainingSession]:
        """获取用户的训练记录"""
        with self.get_cursor() as cursor:
            sql = """
                SELECT * FROM training_sessions 
                WHERE user_id = %s 
                ORDER BY date DESC 
                LIMIT %s
            """
            cursor.execute(sql, (user_id, limit))
            return [self._row_to_training_session(row) for row in cursor.fetchall()]
    
    def get_all_training_sessions(self, limit: int = 100) -> List[DBTrainingSession]:
        """获取所有训练记录"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM training_sessions ORDER BY date DESC LIMIT %s"
            cursor.execute(sql, (limit,))
            return [self._row_to_training_session(row) for row in cursor.fetchall()]
    
    def _row_to_training_session(self, row: dict) -> DBTrainingSession:
        """将数据库行转换为训练记录对象"""
        raw_data = row['raw_data']
        if isinstance(raw_data, str):
            raw_data_str = raw_data
        else:
            raw_data_str = json.dumps(raw_data) if raw_data else '[]'
        
        improvements = row['improvements']
        if isinstance(improvements, str):
            improvements_str = improvements
        else:
            improvements_str = json.dumps(improvements) if improvements else '[]'
        
        areas = row['areas_to_work']
        if isinstance(areas, str):
            areas_str = areas
        else:
            areas_str = json.dumps(areas) if areas else '[]'
        
        return DBTrainingSession(
            id=row['id'],
            session_id=row['session_id'],
            user_id=row['user_id'],
            date=row['date'],
            duration_seconds=row['duration_seconds'] or 0,
            total_shots=row['total_shots'] or 0,
            shooting_percentage=row['shooting_percentage'] or 0,
            average_elbow_angle=row['average_elbow_angle'],
            average_knee_angle=row['average_knee_angle'],
            form_quality_score=row['form_quality_score'] or 0,
            raw_data=raw_data_str,
            improvements=improvements_str,
            areas_to_work=areas_str
        )
    
    # ==================== 训练计划操作 ====================
    
    def create_training_plan(self, plan: DBTrainingPlan) -> int:
        """创建训练计划"""
        with self.get_cursor() as cursor:
            sql = """
                INSERT INTO training_plans (
                    user_id, plan_name, plan_type, target, status, created_at, due_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                plan.user_id, plan.plan_name, plan.plan_type,
                plan.target, plan.status, plan.created_at, plan.due_date
            ))
            return cursor.lastrowid
    
    def get_training_plans_by_user(self, user_id: str) -> List[DBTrainingPlan]:
        """获取用户的训练计划"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM training_plans WHERE user_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            return [self._row_to_training_plan(row) for row in cursor.fetchall()]
    
    def update_training_plan(self, plan_id: int, updates: Dict[str, Any]) -> bool:
        """更新训练计划"""
        if not updates:
            return False
        
        allowed_fields = ['plan_name', 'plan_type', 'target', 'status', 'due_date', 'completed_at']
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                values.append(value)
        
        if not set_clauses:
            return False
        
        values.append(plan_id)
        
        with self.get_cursor() as cursor:
            sql = f"UPDATE training_plans SET {', '.join(set_clauses)} WHERE id = %s"
            cursor.execute(sql, values)
            return cursor.rowcount > 0
    
    def delete_training_plan(self, plan_id: int) -> bool:
        """删除训练计划"""
        with self.get_cursor() as cursor:
            sql = "DELETE FROM training_plans WHERE id = %s"
            cursor.execute(sql, (plan_id,))
            return cursor.rowcount > 0
    
    def _row_to_training_plan(self, row: dict) -> DBTrainingPlan:
        """将数据库行转换为训练计划对象"""
        return DBTrainingPlan(
            id=row['id'],
            user_id=row['user_id'],
            plan_name=row['plan_name'],
            plan_type=row['plan_type'],
            target=row['target'] or '',
            status=row['status'],
            created_at=row['created_at'],
            due_date=row['due_date'],
            completed_at=row['completed_at']
        )
    
    # ==================== 反馈操作 ====================
    
    def create_feedback(self, feedback: DBFeedback) -> int:
        """创建教师反馈"""
        with self.get_cursor() as cursor:
            sql = """
                INSERT INTO feedback (
                    student_id, teacher_id, teacher_name, content, created_at
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                feedback.student_id, feedback.teacher_id,
                feedback.teacher_name, feedback.content, feedback.created_at
            ))
            return cursor.lastrowid
    
    def get_feedback_by_student(self, student_id: str) -> List[DBFeedback]:
        """获取学生收到的反馈"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM feedback WHERE student_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (student_id,))
            return [self._row_to_feedback(row) for row in cursor.fetchall()]
    
    def get_feedback_by_teacher(self, teacher_id: str) -> List[DBFeedback]:
        """获取教师发送的反馈"""
        with self.get_cursor() as cursor:
            sql = "SELECT * FROM feedback WHERE teacher_id = %s ORDER BY created_at DESC"
            cursor.execute(sql, (teacher_id,))
            return [self._row_to_feedback(row) for row in cursor.fetchall()]
    
    def mark_feedback_as_read(self, feedback_id: int) -> bool:
        """标记反馈为已读"""
        with self.get_cursor() as cursor:
            sql = "UPDATE feedback SET is_read = TRUE WHERE id = %s"
            cursor.execute(sql, (feedback_id,))
            return cursor.rowcount > 0
    
    def _row_to_feedback(self, row: dict) -> DBFeedback:
        """将数据库行转换为反馈对象"""
        return DBFeedback(
            id=row['id'],
            student_id=row['student_id'],
            teacher_id=row['teacher_id'],
            teacher_name=row['teacher_name'] or '',
            content=row['content'],
            created_at=row['created_at'],
            is_read=row['is_read']
        )
    
    # ==================== 教师班级管理 ====================
    
    def add_teacher_class(self, teacher_id: str, class_name: str, school: str = '') -> bool:
        """添加教师管理的班级"""
        with self.get_cursor() as cursor:
            sql = """
                INSERT IGNORE INTO teacher_classes (teacher_id, class_name, school)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (teacher_id, class_name, school))
            return cursor.rowcount > 0
    
    def get_teacher_classes(self, teacher_id: str) -> List[Dict[str, str]]:
        """获取教师管理的班级"""
        with self.get_cursor() as cursor:
            sql = "SELECT class_name, school FROM teacher_classes WHERE teacher_id = %s"
            cursor.execute(sql, (teacher_id,))
            return [{'class_name': row['class_name'], 'school': row['school']} for row in cursor.fetchall()]


# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """获取数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config)
    return _db_manager


def init_database(config: Optional[DatabaseConfig] = None) -> DatabaseManager:
    """初始化数据库"""
    manager = get_db_manager(config)
    manager.initialize_database()
    return manager
