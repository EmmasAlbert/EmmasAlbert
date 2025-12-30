"""
Basketball Training Assistance System - Main Application

基于YOLOv8的篮球训练辅助系统

This application provides:
- Real-time basketball and player detection
- Pose estimation and shooting form analysis
- Training session management and progress tracking
- Visual feedback and reports
- User authentication with Teacher/Student roles
"""

import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

from basketball_training_system.backend.api.routes import api
from basketball_training_system.backend.api.service import create_service
from basketball_training_system.backend.utils.data_analyzer import DataAnalyzer
from basketball_training_system.backend.auth.auth_service import AuthService
from basketball_training_system.backend.auth.routes import auth_bp


def create_app(config=None):
    """
    Application factory for creating the Flask app.
    
    Args:
        config: Optional configuration dictionary.
        
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
    })
    
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize services
    data_dir = app.config['DATA_DIR']
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize authentication service
    auth_service = AuthService(data_dir=data_dir)
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
    except Exception as e:
        print(f"Warning: Could not initialize analyzer service: {e}")
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
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    config = {
        'MODEL_PATH': args.model,
        'POSE_MODEL_PATH': args.pose_model,
        'DATA_DIR': args.data_dir
    }
    
    app = create_app(config)
    
    print(f"""
    ========================================
    篮球训练辅助系统 - Basketball Training System
    ========================================
    
    访问地址: http://{args.host}:{args.port}
    
    API 文档:
    - POST /api/analyze/video  - 分析训练视频
    - POST /api/analyze/frame  - 分析单帧图像
    - GET  /api/sessions       - 获取训练记录列表
    - GET  /api/progress       - 获取训练进度
    
    ========================================
    """)
    
    app.run(host=args.host, port=args.port, debug=args.debug)
