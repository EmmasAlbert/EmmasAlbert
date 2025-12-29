"""
数据库管理模块
支持教师-学生角色系统
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
        
        # 学校表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_code TEXT UNIQUE NOT NULL,
                school_name TEXT NOT NULL,
                province TEXT,
                city TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 班级表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER NOT NULL,
                class_name TEXT NOT NULL,
                grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools (id)
            )
        ''')
        
        # 用户表（支持教师和学生角色）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                email TEXT,
                full_name TEXT,
                age INTEGER,
                student_level TEXT,
                school_id INTEGER,
                class_id INTEGER,
                student_id TEXT,
                avatar_url TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools (id),
                FOREIGN KEY (class_id) REFERENCES classes (id)
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
        
        # 教师反馈表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                session_id INTEGER,
                feedback_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users (id),
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (session_id) REFERENCES training_sessions (id)
            )
        ''')
        
        # 教师邀请码表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_invite_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                school_id INTEGER,
                created_by INTEGER,
                used_by INTEGER,
                is_used BOOLEAN DEFAULT 0,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools (id),
                FOREIGN KEY (created_by) REFERENCES users (id),
                FOREIGN KEY (used_by) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 初始化示例数据（仅在开发环境）
        self._init_demo_data()
    
    def _init_demo_data(self):
        """初始化示例数据（用于演示和测试）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 检查是否已有学校数据
        cursor.execute('SELECT COUNT(*) FROM schools')
        if cursor.fetchone()[0] == 0:
            # 插入示例学校
            cursor.execute('''
                INSERT INTO schools (school_code, school_name, province, city)
                VALUES ('DEMO001', '示范学校', '广东省', '广州市')
            ''')
            
            # 获取学校ID
            school_id = cursor.lastrowid
            
            # 插入示例班级
            cursor.execute('''
                INSERT INTO classes (school_id, class_name, grade)
                VALUES (?, '一班', '初一')
            ''', (school_id,))
            
            cursor.execute('''
                INSERT INTO classes (school_id, class_name, grade)
                VALUES (?, '二班', '初一')
            ''', (school_id,))
            
            cursor.execute('''
                INSERT INTO classes (school_id, class_name, grade)
                VALUES (?, '一班', '初二')
            ''', (school_id,))
            
            conn.commit()
        
        # 检查是否已有教师邀请码
        cursor.execute('SELECT COUNT(*) FROM teacher_invite_codes')
        if cursor.fetchone()[0] == 0:
            # 插入默认教师邀请码（用于演示）
            # 在实际环境中，邀请码应该由管理员生成
            import secrets
            
            # 获取示范学校ID
            cursor.execute("SELECT id FROM schools WHERE school_code = 'DEMO001'")
            school_row = cursor.fetchone()
            school_id = school_row[0] if school_row else None
            
            # 生成默认邀请码
            default_codes = [
                ('TEACHER2025', school_id),  # 通用教师邀请码
                ('DEMO_TEACHER', school_id),  # 示范教师邀请码
            ]
            
            for code, sid in default_codes:
                try:
                    cursor.execute('''
                        INSERT INTO teacher_invite_codes (code, school_id, is_used)
                        VALUES (?, ?, 0)
                    ''', (code, sid))
                except Exception:
                    pass  # 忽略重复插入错误
            
            conn.commit()
            print("✓ 已创建默认教师邀请码: TEACHER2025, DEMO_TEACHER")
        
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
            'role': "TEXT DEFAULT 'student'",
            'age': 'INTEGER',
            'student_level': 'TEXT',
            'school_id': 'INTEGER',
            'class_id': 'INTEGER',
            'student_id': 'TEXT',
            'avatar_url': 'TEXT',
            'phone': 'TEXT',
            'full_name': 'TEXT',
            'email': 'TEXT',
            'last_login': 'TIMESTAMP'
        }
        
        # 添加缺失的列
        for column_name, column_def in new_columns.items():
            if column_name not in existing_columns:
                try:
                    cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}')
                    print(f"✓ 数据库迁移: 添加列 users.{column_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ 数据库迁移失败: {column_name} - {e}")
    
    def _hash_password(self, password: str) -> str:
        """对密码进行哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ========== 学校管理 ==========
    
    def create_school(self, school_code: str, school_name: str,
                     province: str = None, city: str = None) -> Optional[int]:
        """创建学校"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO schools (school_code, school_name, province, city)
                VALUES (?, ?, ?, ?)
            ''', (school_code, school_name, province, city))
            
            school_id = cursor.lastrowid
            conn.commit()
            return school_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_school_by_code(self, school_code: str) -> Optional[Dict]:
        """根据学校代码获取学校信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM schools WHERE school_code = ?', (school_code,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_all_schools(self) -> List[Dict]:
        """获取所有学校"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM schools ORDER BY school_name')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== 班级管理 ==========
    
    def create_class(self, school_id: int, class_name: str, grade: str = None) -> int:
        """创建班级"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO classes (school_id, class_name, grade)
            VALUES (?, ?, ?)
        ''', (school_id, class_name, grade))
        
        class_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return class_id
    
    def get_classes_by_school(self, school_id: int) -> List[Dict]:
        """获取学校的所有班级"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM classes WHERE school_id = ?
            ORDER BY grade, class_name
        ''', (school_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== 用户管理 ==========
    
    def create_user(self, username: str, password: str, 
                   role: str = 'student',
                   email: str = None, full_name: str = None,
                   age: int = None, student_level: str = None,
                   school_id: int = None, class_id: int = None,
                   student_id: str = None, phone: str = None) -> Optional[int]:
        """
        创建新用户（教师或学生）
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
                INSERT INTO users (username, password_hash, role, email, full_name, 
                                 age, student_level, school_id, class_id, student_id, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, role, email, full_name, 
                 age, student_level, school_id, class_id, student_id, phone))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """验证用户登录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        password_hash = self._hash_password(password)
        cursor.execute('''
            SELECT u.*, s.school_name, s.school_code, c.class_name, c.grade
            FROM users u
            LEFT JOIN schools s ON u.school_id = s.id
            LEFT JOIN classes c ON u.class_id = c.id
            WHERE u.username = ? AND u.password_hash = ?
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
            # 移除密码哈希
            user_info.pop('password_hash', None)
            conn.close()
            return user_info
        
        conn.close()
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """根据ID获取用户信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.*, s.school_name, s.school_code, c.class_name, c.grade
            FROM users u
            LEFT JOIN schools s ON u.school_id = s.id
            LEFT JOIN classes c ON u.class_id = c.id
            WHERE u.id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user_info = dict(row)
            user_info.pop('password_hash', None)
            return user_info
        return None
    
    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """更新用户资料"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['email', 'full_name', 'age', 'student_level', 
                         'school_id', 'class_id', 'student_id', 'avatar_url', 'phone']
        
        updates = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return True
    
    def bind_school(self, user_id: int, school_code: str, class_id: int = None) -> bool:
        """绑定学校"""
        school = self.get_school_by_code(school_code)
        if not school:
            return False
        
        return self.update_user_profile(user_id, school_id=school['id'], class_id=class_id)
    
    # ========== 教师功能 ==========
    
    def get_students_by_school(self, school_id: int, class_id: int = None) -> List[Dict]:
        """获取学校/班级的学生列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if class_id:
            cursor.execute('''
                SELECT u.*, c.class_name, c.grade
                FROM users u
                LEFT JOIN classes c ON u.class_id = c.id
                WHERE u.school_id = ? AND u.class_id = ? AND u.role = 'student'
                ORDER BY u.full_name, u.username
            ''', (school_id, class_id))
        else:
            cursor.execute('''
                SELECT u.*, c.class_name, c.grade
                FROM users u
                LEFT JOIN classes c ON u.class_id = c.id
                WHERE u.school_id = ? AND u.role = 'student'
                ORDER BY c.grade, c.class_name, u.full_name, u.username
            ''', (school_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            user_info = dict(row)
            user_info.pop('password_hash', None)
            result.append(user_info)
        
        return result
    
    def search_students(self, school_id: int, query: str) -> List[Dict]:
        """搜索学生（按学号或姓名）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT u.*, c.class_name, c.grade,
                   (SELECT COUNT(*) FROM training_sessions ts WHERE ts.user_id = u.id) as session_count,
                   (SELECT AVG(average_score) FROM training_sessions ts WHERE ts.user_id = u.id) as avg_score
            FROM users u
            LEFT JOIN classes c ON u.class_id = c.id
            WHERE u.school_id = ? AND u.role = 'student'
              AND (u.student_id LIKE ? OR u.full_name LIKE ? OR u.username LIKE ?)
            ORDER BY u.full_name, u.username
        ''', (school_id, search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            user_info = dict(row)
            user_info.pop('password_hash', None)
            result.append(user_info)
        
        return result
    
    def get_student_stats(self, student_id: int) -> Dict:
        """获取学生训练统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 获取总训练次数和平均分
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                SUM(total_shots) as total_shots,
                AVG(average_score) as avg_score,
                MAX(average_score) as best_score
            FROM training_sessions
            WHERE user_id = ?
        ''', (student_id,))
        
        stats = dict(cursor.fetchone())
        
        # 获取最近5次训练
        cursor.execute('''
            SELECT * FROM training_sessions
            WHERE user_id = ?
            ORDER BY session_date DESC
            LIMIT 5
        ''', (student_id,))
        
        stats['recent_sessions'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return stats
    
    def add_teacher_feedback(self, teacher_id: int, student_id: int, 
                            feedback_text: str, session_id: int = None) -> int:
        """添加教师反馈"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teacher_feedback (teacher_id, student_id, session_id, feedback_text)
            VALUES (?, ?, ?, ?)
        ''', (teacher_id, student_id, session_id, feedback_text))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_student_feedback(self, student_id: int, limit: int = 10) -> List[Dict]:
        """获取学生收到的教师反馈"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tf.*, u.full_name as teacher_name, u.username as teacher_username
            FROM teacher_feedback tf
            JOIN users u ON tf.teacher_id = u.id
            WHERE tf.student_id = ?
            ORDER BY tf.created_at DESC
            LIMIT ?
        ''', (student_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # ========== 训练记录管理 ==========
    
    def create_training_session(self, user_id: int, video_path: str = None,
                                duration: int = 0, notes: str = None) -> int:
        """创建训练记录"""
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
        """更新训练记录"""
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
        """添加投篮分析记录"""
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
        """获取用户训练历史"""
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
        """获取训练记录的所有分析结果"""
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
    
    # ========== 教师邀请码管理 ==========
    
    def verify_teacher_invite_code(self, code: str) -> Optional[Dict]:
        """
        验证教师邀请码
        
        Returns:
            Dict with code info if valid, None if invalid
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tic.*, s.school_name, s.school_code
            FROM teacher_invite_codes tic
            LEFT JOIN schools s ON tic.school_id = s.id
            WHERE tic.code = ? AND tic.is_used = 0
              AND (tic.expires_at IS NULL OR tic.expires_at > CURRENT_TIMESTAMP)
        ''', (code,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def use_teacher_invite_code(self, code: str, user_id: int) -> bool:
        """
        使用教师邀请码（标记为已使用）
        
        Args:
            code: 邀请码
            user_id: 使用者的用户ID
            
        Returns:
            True if successful, False otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE teacher_invite_codes
                SET is_used = 1, used_by = ?, used_at = CURRENT_TIMESTAMP
                WHERE code = ? AND is_used = 0
            ''', (user_id, code))
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            return affected > 0
        except Exception as e:
            conn.close()
            print(f"使用邀请码失败: {e}")
            return False
    
    def create_teacher_invite_code(self, school_id: int = None, 
                                   created_by: int = None,
                                   expires_days: int = 30) -> str:
        """
        创建新的教师邀请码
        
        Args:
            school_id: 关联的学校ID
            created_by: 创建者的用户ID（管理员或教师）
            expires_days: 有效期（天数），默认30天
            
        Returns:
            生成的邀请码
        """
        import secrets
        from datetime import datetime, timedelta
        
        # 生成随机邀请码
        code = f"TCH{secrets.token_hex(4).upper()}"
        
        # 计算过期时间
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teacher_invite_codes (code, school_id, created_by, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (code, school_id, created_by, expires_at))
        
        conn.commit()
        conn.close()
        
        return code
    
    def get_teacher_invite_codes(self, school_id: int = None, 
                                include_used: bool = False) -> List[Dict]:
        """获取教师邀请码列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT tic.*, s.school_name, 
                   u1.username as creator_username,
                   u2.username as user_username
            FROM teacher_invite_codes tic
            LEFT JOIN schools s ON tic.school_id = s.id
            LEFT JOIN users u1 ON tic.created_by = u1.id
            LEFT JOIN users u2 ON tic.used_by = u2.id
            WHERE 1=1
        '''
        params = []
        
        if school_id:
            query += ' AND tic.school_id = ?'
            params.append(school_id)
        
        if not include_used:
            query += ' AND tic.is_used = 0'
        
        query += ' ORDER BY tic.created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
