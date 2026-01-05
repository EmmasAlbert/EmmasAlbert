"""
Authentication module for Basketball Training System.
用户认证模块 - 支持教师和学生用户角色

Provides:
- User registration and login
- Role-based access control (Teacher/Student)
- Session management
- JSON file storage (AuthService)
- MySQL database storage (AuthServiceDB)
"""

from .models import User, UserRole
from .auth_service import AuthService
from .decorators import login_required, role_required

# Try to import database-based auth service
try:
    from .auth_service_db import AuthServiceDB, create_db_auth_service
    DB_AUTH_AVAILABLE = True
except ImportError:
    AuthServiceDB = None
    create_db_auth_service = None
    DB_AUTH_AVAILABLE = False

__all__ = [
    'User', 
    'UserRole', 
    'AuthService', 
    'login_required', 
    'role_required',
    'AuthServiceDB',
    'create_db_auth_service',
    'DB_AUTH_AVAILABLE'
]
