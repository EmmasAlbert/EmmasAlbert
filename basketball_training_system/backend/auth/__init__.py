"""
Authentication module for Basketball Training System.
用户认证模块 - 支持教师和学生用户角色

Provides:
- User registration and login
- Role-based access control (Teacher/Student)
- Session management
"""

from .models import User, UserRole
from .auth_service import AuthService
from .decorators import login_required, role_required

__all__ = ['User', 'UserRole', 'AuthService', 'login_required', 'role_required']
