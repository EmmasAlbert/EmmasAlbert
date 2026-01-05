"""
Database Module for Basketball Training System.
数据库模块 - 支持MySQL数据存储

Provides:
- MySQL database connection management
- User, session, training data persistence
- Migration from JSON to MySQL
"""

from .db_manager import DatabaseManager, get_db_manager
from .models import DBUser, DBSession, DBTrainingSession, DBTrainingPlan, DBFeedback

__all__ = [
    'DatabaseManager',
    'get_db_manager',
    'DBUser',
    'DBSession',
    'DBTrainingSession',
    'DBTrainingPlan',
    'DBFeedback'
]
