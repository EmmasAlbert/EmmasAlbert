"""
数据库管理模块
"""
import sqlite3
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/basketball_training.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 确保数据库目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库表
        self._init_tables()
    
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使用Row对象以便通过列名访问
        return conn
    
    def _init_tables(self):
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                full_name TEXT,
                age INTEGER,              -- 年龄（针对中小学生）
                student_level TEXT,       -- 学段：primary/junior/senior
                school_name TEXT,         -- 学校名称
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # 数据库迁移：检查并添加缺失的列
        self._migrate_users_table(cursor)
        
        # 训练记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                video_path TEXT,
                duration INTEGER,
                total_shots INTEGER DEFAULT 0,
                successful_shots INTEGER DEFAULT 0,
                average_score REAL DEFAULT 0.0,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 投篮分析表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shot_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                timestamp REAL,
                elbow_angle REAL,
                release_height REAL,
                body_alignment REAL,
                shooting_hand TEXT,
                form_score REAL,
                feedback TEXT,
                FOREIGN KEY (session_id) REFERENCES training_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _migrate_users_table(self, cursor):
        """
        数据库迁移：为旧版本的users表添加缺失的列
        """
        # 获取现有列
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        print(f"[DEBUG] 数据库现有列: {existing_columns}")
        
        # 需要添加的列及其定义
        new_columns = {
            'age': 'INTEGER',
            'student_level': 'TEXT',
            'school_name': 'TEXT',
            'full_name': 'TEXT',
            'email': 'TEXT',
            'last_login': 'TIMESTAMP'
        }
        
        # 添加缺失的列
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                    print(f"✓ 数据库迁移: 添加列 users.{column_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ 数据库迁移失败: {column_name} - {e}")
    
    def _hash_password(self, password: str) -> str:
        """
        对密码进行哈希
        
        Args:
            password: 明文密码
        
        Returns:
            哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    # 用户管理方法
    def create_user(self, username: str, password: str, 
                   email: str = None, full_name: str = None,
                   age: int = None, student_level: str = None,
                   school_name: str = None) -> Optional[int]:
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            full_name: 全名
        
        Returns:
            用户ID，如果用户名已存在则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self._hash_password(password)
            
            # 根据年龄自动判断学段（如果未提供）
            if age and not student_level:
                if age <= 12:
                    student_level = 'primary'
                elif age <= 15:
                    student_level = 'junior'
                else:
                    student_level = 'senior'
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, full_name, 
                                 age, student_level, school_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, email, full_name, 
                 age, student_level, school_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """
        验证用户登录
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            用户信息字典，如果验证失败则返回None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        password_hash = self._hash_password(password)
        cursor.execute('''
            SELECT id, username, email, full_name, age, student_level, 
                   school_name, created_at
            FROM users
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        
        if row:
            # 更新最后登录时间
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row['id'],))
            conn.commit()
            
            user_info = dict(row)
            conn.close()
            return user_info
        
        conn.close()
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, full_name, age, student_level,
                   school_name, created_at, last_login
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # 训练记录管理方法
    def create_training_session(self, user_id: int, video_path: str = None,
                                duration: int = 0, notes: str = None) -> int:
        """
        创建训练记录
        
        Args:
            user_id: 用户ID
            video_path: 视频路径
            duration: 训练时长（秒）
            notes: 备注
        
        Returns:
            训练记录ID
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO training_sessions (user_id, video_path, duration, notes)
            VALUES (?, ?, ?, ?)
        ''', (user_id, video_path, duration, notes))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_training_session(self, session_id: int, 
                               total_shots: int = None,
                               successful_shots: int = None,
                               average_score: float = None):
        """
        更新训练记录
        
        Args:
            session_id: 训练记录ID
            total_shots: 总投篮次数
            successful_shots: 成功投篮次数
            average_score: 平均分数
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if total_shots is not None:
            updates.append("total_shots = ?")
            params.append(total_shots)
        
        if successful_shots is not None:
            updates.append("successful_shots = ?")
            params.append(successful_shots)
        
        if average_score is not None:
            updates.append("average_score = ?")
            params.append(average_score)
        
        if updates:
            params.append(session_id)
            query = f"UPDATE training_sessions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def add_shot_analysis(self, session_id: int, timestamp: float,
                         analysis_result: Dict):
        """
        添加投篮分析记录
        
        Args:
            session_id: 训练记录ID
            timestamp: 时间戳
            analysis_result: 分析结果字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shot_analysis 
            (session_id, timestamp, elbow_angle, release_height, body_alignment,
             shooting_hand, form_score, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            timestamp,
            analysis_result.get('elbow_angle'),
            analysis_result.get('release_height'),
            analysis_result.get('body_alignment'),
            analysis_result.get('shooting_hand'),
            analysis_result.get('form_score'),
            '\n'.join(analysis_result.get('feedback', []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_user_training_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        获取用户训练历史
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
        
        Returns:
            训练记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM training_sessions
            WHERE user_id = ?
            ORDER BY session_date DESC
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_session_analysis(self, session_id: int) -> List[Dict]:
        """
        获取训练记录的所有分析结果
        
        Args:
            session_id: 训练记录ID
        
        Returns:
            分析结果列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM shot_analysis
            WHERE session_id = ?
            ORDER BY timestamp
        ''', (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
