"""
Basketball Training Assistance System - Main Application

基于YOLOv8的篮球训练辅助系统

This application provides:
- Real-time basketball and player detection
- Pose estimation and shooting form analysis
- Training session management and progress tracking
- Visual feedback and reports
- User authentication with Teacher/Student roles
- MySQL database storage support
"""

import os
import logging
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

from basketball_training_system.backend.api.routes import api
from basketball_training_system.backend.api.service import create_service
from basketball_training_system.backend.utils.data_analyzer import DataAnalyzer
from basketball_training_system.backend.auth.auth_service import AuthService
from basketball_training_system.backend.auth.routes import auth_bp, teacher_bp, student_bp

# Try to import database auth service
try:
    from basketball_training_system.backend.auth import AuthServiceDB, DB_AUTH_AVAILABLE
except ImportError:
    AuthServiceDB = None
    DB_AUTH_AVAILABLE = False

# Try to import Flask-WTF for CSRF protection
try:
    from flask_wtf.csrf import CSRFProtect
    CSRF_AVAILABLE = True
except ImportError:
    CSRFProtect = None
    CSRF_AVAILABLE = False


def create_app(config=None, use_database=False, db_config=None, enable_csrf=True):
    """
    Application factory for creating the Flask app.
    
    Args:
        config: Optional configuration dictionary.
        use_database: Whether to use MySQL database for storage.
        db_config: Database configuration dictionary.
        enable_csrf: Whether to enable CSRF protection (default: True).
        
    Returns:
        Configured Flask application.
    """
    app = Flask(
        __name__,
        template_folder='basketball_training_system/frontend/templates',
        static_folder='basketball_training_system/frontend/static'
    )
    
    # Default configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'basketball-training-secret-key'),
        'MAX_CONTENT_LENGTH': 500 * 1024 * 1024,  # 500MB max upload
        'DATA_DIR': os.environ.get('DATA_DIR', 'data'),
        'MODEL_PATH': os.environ.get('MODEL_PATH', None),
        'POSE_MODEL_PATH': os.environ.get('POSE_MODEL_PATH', None),
        'USE_DATABASE': use_database or os.environ.get('USE_DATABASE', 'false').lower() == 'true',
        'WTF_CSRF_ENABLED': enable_csrf and CSRF_AVAILABLE,
        'WTF_CSRF_CHECK_DEFAULT': False,  # We use custom CSRF handling for API
        'SESSION_COOKIE_SECURE': os.environ.get('SECURE_COOKIES', 'false').lower() == 'true',
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
    })
    
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Enable CSRF protection if available
    if enable_csrf and CSRF_AVAILABLE:
        csrf = CSRFProtect(app)
        # Exempt API routes from CSRF (they use session tokens instead)
        csrf.exempt(api)
        csrf.exempt(auth_bp)
        csrf.exempt(teacher_bp)
        csrf.exempt(student_bp)
        logger.info("✓ CSRF 保护已启用")
    
    # Initialize services
    data_dir = app.config['DATA_DIR']
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize authentication service
    if app.config['USE_DATABASE'] and DB_AUTH_AVAILABLE:
        # Use MySQL database storage
        try:
            if db_config is None:
                db_config = {
                    'host': os.environ.get('DB_HOST', 'localhost'),
                    'port': int(os.environ.get('DB_PORT', '3306')),
                    'user': os.environ.get('DB_USER', 'root'),
                    'password': os.environ.get('DB_PASSWORD', ''),
                    'database': os.environ.get('DB_NAME', 'basketball_training'),
                }
            auth_service = AuthServiceDB(db_config=db_config)
            logger.info("✓ 使用 MySQL 数据库存储")
        except Exception as e:
            logger.warning(f"⚠ 无法连接数据库，回退到 JSON 文件存储: {e}")
            auth_service = AuthService(data_dir=data_dir)
    else:
        # Use JSON file storage (default)
        auth_service = AuthService(data_dir=data_dir)
        logger.info("✓ 使用 JSON 文件存储")
    
    app.config['auth_service'] = auth_service
    
    # Create analyzer service (may fail if ultralytics not installed)
    try:
        analyzer_service = create_service(
            model_path=app.config['MODEL_PATH'],
            pose_model_path=app.config['POSE_MODEL_PATH'],
            data_dir=data_dir
        )
        app.config['analyzer_service'] = analyzer_service
        app.config['data_analyzer'] = analyzer_service.data_analyzer
        logger.info("✓ 分析服务初始化成功")
    except Exception as e:
        logger.warning(f"⚠ 无法初始化分析服务: {e}")
        app.config['analyzer_service'] = None
        app.config['data_analyzer'] = DataAnalyzer(data_dir=data_dir)
    
    # Default settings
    app.config['settings'] = {
        'shooting_hand': 'right',
        'skip_frames': 0,
        'conf_threshold': 0.5,
        'show_angles': True
    }
    
    # Register blueprints
    app.register_blueprint(api)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    
    # Frontend routes
    @app.route('/')
    def index():
        """Serve the main application page."""
        return render_template('index.html')
    
    @app.route('/login')
    def login_page():
        """Serve the login page."""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Serve the registration page."""
        return render_template('register.html')
    
    @app.route('/analysis')
    def analysis():
        """Serve the analysis page."""
        return render_template('analysis.html')
    
    @app.route('/realtime')
    def realtime():
        """Serve the realtime detection page."""
        return render_template('realtime.html')
    
    @app.route('/history')
    def history():
        """Serve the training history page."""
        return render_template('history.html')
    
    @app.route('/settings')
    def settings_page():
        """Serve the settings page."""
        return render_template('settings.html')
    
    @app.route('/teacher')
    def teacher_dashboard():
        """Serve the teacher dashboard page."""
        return render_template('teacher_dashboard.html')
    
    @app.route('/student')
    def student_dashboard():
        """Serve the student dashboard page."""
        return render_template('student_dashboard.html')
    
    @app.route('/student/profile')
    def student_profile():
        """Serve the student profile page."""
        return render_template('student_profile.html')
    
    return app


# Create default app instance
app = create_app()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Basketball Training Assistance System')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--model', help='Path to custom detection model')
    parser.add_argument('--pose-model', help='Path to custom pose model')
    parser.add_argument('--data-dir', default='data', help='Directory for data storage')
    
    # Database options
    parser.add_argument('--use-database', action='store_true', help='Use MySQL database for storage')
    parser.add_argument('--db-host', default='localhost', help='Database host')
    parser.add_argument('--db-port', type=int, default=3306, help='Database port')
    parser.add_argument('--db-user', default='root', help='Database user')
    parser.add_argument('--db-password', default='', help='Database password')
    parser.add_argument('--db-name', default='basketball_training', help='Database name')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    config = {
        'MODEL_PATH': args.model,
        'POSE_MODEL_PATH': args.pose_model,
        'DATA_DIR': args.data_dir
    }
    
    # Database config
    db_config = None
    if args.use_database:
        db_config = {
            'host': args.db_host,
            'port': args.db_port,
            'user': args.db_user,
            'password': args.db_password,
            'database': args.db_name,
        }
    
    app = create_app(config, use_database=args.use_database, db_config=db_config)
    
    storage_mode = "MySQL 数据库" if args.use_database else "JSON 文件"
    
    print(f"""
    ========================================
    篮球训练辅助系统 - Basketball Training System
    ========================================
    
    访问地址: http://{args.host}:{args.port}
    数据存储: {storage_mode}
    
    API 文档:
    - POST /api/analyze/video  - 分析训练视频
    - POST /api/analyze/frame  - 分析单帧图像
    - GET  /api/sessions       - 获取训练记录列表
    - GET  /api/progress       - 获取训练进度
    
    ========================================
    """)
    
    app.run(host=args.host, port=args.port, debug=args.debug)
