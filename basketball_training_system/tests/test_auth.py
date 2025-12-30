"""
Tests for Authentication Module.
认证模块测试
"""

import os
import json
import tempfile
import shutil
import pytest
from datetime import datetime, timedelta

from basketball_training_system.backend.auth.models import User, UserRole, UserSession
from basketball_training_system.backend.auth.auth_service import AuthService


class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self):
        """Test creating a user."""
        user = User(
            user_id="test123",
            username="testuser",
            password_hash=User.hash_password("password123"),
            role=UserRole.STUDENT,
            real_name="测试用户"
        )
        
        assert user.user_id == "test123"
        assert user.username == "testuser"
        assert user.role == UserRole.STUDENT
        assert user.real_name == "测试用户"
        assert user.is_student()
        assert not user.is_teacher()
    
    def test_teacher_creation(self):
        """Test creating a teacher user."""
        user = User(
            user_id="teacher123",
            username="teacher",
            password_hash=User.hash_password("password"),
            role=UserRole.TEACHER,
            real_name="张老师"
        )
        
        assert user.is_teacher()
        assert not user.is_student()
    
    def test_password_hashing(self):
        """Test password hashing."""
        password = "secure_password"
        hash1 = User.hash_password(password)
        hash2 = User.hash_password(password)
        
        assert hash1 == hash2
        assert hash1 != password
    
    def test_password_verification(self):
        """Test password verification."""
        password = "my_password"
        user = User(
            user_id="test",
            username="test",
            password_hash=User.hash_password(password),
            role=UserRole.STUDENT
        )
        
        assert user.verify_password(password)
        assert not user.verify_password("wrong_password")
    
    def test_user_to_dict(self):
        """Test converting user to dictionary."""
        user = User(
            user_id="test123",
            username="testuser",
            password_hash="hash",
            role=UserRole.STUDENT,
            real_name="测试",
            class_name="三年级1班"
        )
        
        data = user.to_dict()
        
        assert data['user_id'] == "test123"
        assert data['username'] == "testuser"
        assert data['role'] == "student"
        assert data['real_name'] == "测试"
        assert 'password_hash' not in data
        
        # Test with sensitive data
        data_sensitive = user.to_dict(include_sensitive=True)
        assert 'password_hash' in data_sensitive
    
    def test_user_from_dict(self):
        """Test creating user from dictionary."""
        data = {
            'user_id': 'test123',
            'username': 'testuser',
            'password_hash': 'hash',
            'role': 'teacher',
            'real_name': '张老师',
            'school': '北京小学'
        }
        
        user = User.from_dict(data)
        
        assert user.user_id == 'test123'
        assert user.username == 'testuser'
        assert user.role == UserRole.TEACHER
        assert user.school == '北京小学'


class TestUserSession:
    """Tests for UserSession model."""
    
    def test_session_creation(self):
        """Test creating a session."""
        session = UserSession(
            session_id="session123",
            user_id="user123"
        )
        
        assert session.session_id == "session123"
        assert session.user_id == "user123"
        assert not session.is_expired()
    
    def test_session_expiration(self):
        """Test session expiration."""
        # Expired session
        expired_session = UserSession(
            session_id="session1",
            user_id="user1",
            expires_at=datetime.now() - timedelta(hours=1)
        )
        assert expired_session.is_expired()
        
        # Valid session
        valid_session = UserSession(
            session_id="session2",
            user_id="user2",
            expires_at=datetime.now() + timedelta(days=7)
        )
        assert not valid_session.is_expired()
    
    def test_generate_session_id(self):
        """Test session ID generation."""
        id1 = UserSession.generate_session_id()
        id2 = UserSession.generate_session_id()
        
        assert id1 != id2
        assert len(id1) == 64  # 32 bytes hex = 64 characters


class TestAuthService:
    """Tests for AuthService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def auth_service(self, temp_dir):
        """Create an AuthService instance with temp directory."""
        return AuthService(data_dir=temp_dir)
    
    def test_register_student(self, auth_service):
        """Test student registration."""
        result = auth_service.register(
            username="student1",
            password="password123",
            role="student",
            real_name="小明",
            class_name="三年级1班",
            grade="小学三年级"
        )
        
        assert result['success']
        assert result['user']['username'] == "student1"
        assert result['user']['role'] == "student"
    
    def test_register_teacher(self, auth_service):
        """Test teacher registration."""
        result = auth_service.register(
            username="teacher1",
            password="password123",
            role="teacher",
            real_name="张老师",
            school="北京小学"
        )
        
        assert result['success']
        assert result['user']['username'] == "teacher1"
        assert result['user']['role'] == "teacher"
    
    def test_register_duplicate_username(self, auth_service):
        """Test registering with duplicate username."""
        auth_service.register(
            username="testuser",
            password="password123",
            role="student"
        )
        
        result = auth_service.register(
            username="testuser",
            password="password456",
            role="student"
        )
        
        assert not result['success']
        assert '用户名已存在' in result['error']
    
    def test_register_weak_password(self, auth_service):
        """Test registration with weak password."""
        result = auth_service.register(
            username="testuser",
            password="123",
            role="student"
        )
        
        assert not result['success']
        assert '密码' in result['error']
    
    def test_login_success(self, auth_service):
        """Test successful login."""
        auth_service.register(
            username="testuser",
            password="password123",
            role="student"
        )
        
        result = auth_service.login("testuser", "password123")
        
        assert result['success']
        assert 'session_id' in result
        assert result['user']['username'] == "testuser"
    
    def test_login_wrong_password(self, auth_service):
        """Test login with wrong password."""
        auth_service.register(
            username="testuser",
            password="password123",
            role="student"
        )
        
        result = auth_service.login("testuser", "wrongpassword")
        
        assert not result['success']
        assert '用户名或密码错误' in result['error']
    
    def test_login_nonexistent_user(self, auth_service):
        """Test login with nonexistent user."""
        result = auth_service.login("nonexistent", "password")
        
        assert not result['success']
    
    def test_logout(self, auth_service):
        """Test logout."""
        auth_service.register(
            username="testuser",
            password="password123",
            role="student"
        )
        
        login_result = auth_service.login("testuser", "password123")
        session_id = login_result['session_id']
        
        # User should be findable before logout
        user = auth_service.get_user_by_session(session_id)
        assert user is not None
        
        # Logout
        auth_service.logout(session_id)
        
        # User should not be findable after logout
        user = auth_service.get_user_by_session(session_id)
        assert user is None
    
    def test_get_user_by_session(self, auth_service):
        """Test getting user by session ID."""
        auth_service.register(
            username="testuser",
            password="password123",
            role="student",
            real_name="测试"
        )
        
        login_result = auth_service.login("testuser", "password123")
        session_id = login_result['session_id']
        
        user = auth_service.get_user_by_session(session_id)
        
        assert user is not None
        assert user.username == "testuser"
        assert user.real_name == "测试"
    
    def test_get_students_by_teacher(self, auth_service):
        """Test getting students assigned to a teacher."""
        # Create teacher
        teacher_result = auth_service.register(
            username="teacher1",
            password="password123",
            role="teacher"
        )
        teacher_id = teacher_result['user']['user_id']
        
        # Create students
        auth_service.register(
            username="student1",
            password="password123",
            role="student",
            teacher_id=teacher_id
        )
        auth_service.register(
            username="student2",
            password="password123",
            role="student",
            teacher_id=teacher_id
        )
        auth_service.register(
            username="student3",
            password="password123",
            role="student"  # No teacher
        )
        
        students = auth_service.get_students_by_teacher(teacher_id)
        
        assert len(students) == 2
        assert all(s.teacher_id == teacher_id for s in students)
    
    def test_update_user(self, auth_service):
        """Test updating user information."""
        result = auth_service.register(
            username="testuser",
            password="password123",
            role="student"
        )
        user_id = result['user']['user_id']
        
        update_result = auth_service.update_user(user_id, {
            'real_name': '新名字',
            'school': '新学校'
        })
        
        assert update_result['success']
        assert update_result['user']['real_name'] == '新名字'
        assert update_result['user']['school'] == '新学校'
    
    def test_data_persistence(self, temp_dir):
        """Test that data is persisted to files."""
        # Create service and register user
        service1 = AuthService(data_dir=temp_dir)
        service1.register(
            username="testuser",
            password="password123",
            role="student",
            real_name="测试用户"
        )
        
        # Create new service instance (simulating restart)
        service2 = AuthService(data_dir=temp_dir)
        
        # User should still exist
        users = list(service2.users.values())
        assert len(users) == 1
        assert users[0].username == "testuser"
        assert users[0].real_name == "测试用户"


class TestRoleBasedAccess:
    """Tests for role-based access control."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def auth_service(self, temp_dir):
        """Create an AuthService instance with temp directory."""
        return AuthService(data_dir=temp_dir)
    
    def test_teacher_can_view_all_students(self, auth_service):
        """Test that teachers can view all students."""
        # Create teacher
        auth_service.register(
            username="teacher",
            password="password123",
            role="teacher"
        )
        
        # Create multiple students
        for i in range(5):
            auth_service.register(
                username=f"student{i}",
                password="password123",
                role="student"
            )
        
        students = auth_service.get_all_students()
        assert len(students) == 5
    
    def test_get_students_by_class(self, auth_service):
        """Test getting students by class."""
        # Create students in different classes
        auth_service.register(
            username="student1",
            password="password123",
            role="student",
            class_name="三年级1班"
        )
        auth_service.register(
            username="student2",
            password="password123",
            role="student",
            class_name="三年级1班"
        )
        auth_service.register(
            username="student3",
            password="password123",
            role="student",
            class_name="三年级2班"
        )
        
        class1_students = auth_service.get_students_by_class("三年级1班")
        class2_students = auth_service.get_students_by_class("三年级2班")
        
        assert len(class1_students) == 2
        assert len(class2_students) == 1
