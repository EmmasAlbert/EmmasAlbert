"""
REST API Routes for Basketball Training System.

Provides endpoints for video analysis, session management, and data retrieval.
"""

import os
import uuid
import tempfile
from typing import Optional
from datetime import datetime

from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@api.route('/analyze/video', methods=['POST'])
def analyze_video():
    """
    Analyze an uploaded basketball training video.
    
    Request:
        - file: Video file (mp4, avi, mov, mkv, webm)
        - shooting_hand: 'left' or 'right' (optional, default: 'right')
        - skip_frames: Number of frames to skip (optional, default: 0)
    
    Response:
        - session_id: Unique identifier for this analysis
        - statistics: Session statistics
        - feedback: Training feedback
    """
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'不支持的文件格式。支持: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    try:
        # Get analysis parameters
        shooting_hand = request.form.get('shooting_hand', 'right')
        skip_frames = int(request.form.get('skip_frames', 0))
        
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        video_path = os.path.join(temp_dir, f'{session_id}_{filename}')
        file.save(video_path)
        
        # Get analyzer from app context
        analyzer_service = current_app.config.get('analyzer_service')
        
        if analyzer_service is None:
            # Return mock response if service not available
            return jsonify({
                'session_id': session_id,
                'status': 'completed',
                'message': '分析服务未配置，返回示例数据',
                'statistics': {
                    'total_shots': 0,
                    'form_quality_score': 0.0,
                    'average_elbow_angle': None,
                    'average_knee_angle': None
                },
                'feedback': ['请确保系统正确配置后重试']
            })
        
        # Perform analysis
        results = analyzer_service.analyze_video(
            video_path=video_path,
            session_id=session_id,
            shooting_hand=shooting_hand,
            skip_frames=skip_frames
        )
        
        # Clean up temp file
        if os.path.exists(video_path):
            os.remove(video_path)
        
        return jsonify({
            'session_id': session_id,
            'status': 'completed',
            'statistics': results.get('statistics', {}),
            'feedback': results.get('feedback', []),
            'details': results.get('details', {})
        })
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@api.route('/analyze/frame', methods=['POST'])
def analyze_frame():
    """
    Analyze a single frame/image.
    
    Request:
        - file: Image file (jpg, png)
        - shooting_hand: 'left' or 'right' (optional)
    
    Response:
        - detections: List of detected objects
        - poses: List of detected poses
        - analysis: Action analysis results
    """
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    try:
        import numpy as np
        import cv2
        
        # Read image
        file_bytes = file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': '无法读取图像文件'}), 400
        
        shooting_hand = request.form.get('shooting_hand', 'right')
        
        # Get analyzer from app context
        analyzer_service = current_app.config.get('analyzer_service')
        
        if analyzer_service is None:
            return jsonify({
                'status': 'completed',
                'message': '分析服务未配置',
                'detections': [],
                'poses': [],
                'analysis': {}
            })
        
        # Perform analysis
        results = analyzer_service.analyze_frame(frame, shooting_hand)
        
        return jsonify({
            'status': 'completed',
            'detections': results.get('detections', []),
            'poses': results.get('poses', []),
            'analysis': results.get('analysis', {})
        })
        
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@api.route('/sessions', methods=['GET'])
def list_sessions():
    """
    List all training sessions.
    
    Query Parameters:
        - limit: Maximum number of sessions to return (default: 20)
        - offset: Offset for pagination (default: 0)
    
    Response:
        - sessions: List of session summaries
        - total: Total number of sessions
    """
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    data_analyzer = current_app.config.get('data_analyzer')
    
    if data_analyzer is None:
        return jsonify({
            'sessions': [],
            'total': 0
        })
    
    sessions = data_analyzer.sessions[offset:offset + limit]
    
    return jsonify({
        'sessions': [
            {
                'session_id': s['session_id'],
                'date': s['date'],
                'total_shots': s['statistics']['total_shots'],
                'form_quality_score': s['statistics']['form_quality_score']
            }
            for s in sessions
        ],
        'total': len(data_analyzer.sessions)
    })


@api.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id: str):
    """
    Get details of a specific session.
    
    Path Parameters:
        - session_id: Session identifier
    
    Response:
        - Session details including statistics and raw data
    """
    data_analyzer = current_app.config.get('data_analyzer')
    
    if data_analyzer is None:
        return jsonify({'error': '数据分析服务未配置'}), 500
    
    session = next(
        (s for s in data_analyzer.sessions if s['session_id'] == session_id),
        None
    )
    
    if session is None:
        return jsonify({'error': '训练记录未找到'}), 404
    
    return jsonify(session)


@api.route('/sessions/<session_id>/report', methods=['GET'])
def get_session_report(session_id: str):
    """
    Get formatted report for a session.
    
    Path Parameters:
        - session_id: Session identifier
    
    Query Parameters:
        - format: 'text' or 'json' (default: 'text')
    
    Response:
        - Formatted report
    """
    format_type = request.args.get('format', 'text')
    
    data_analyzer = current_app.config.get('data_analyzer')
    
    if data_analyzer is None:
        return jsonify({'error': '数据分析服务未配置'}), 500
    
    session = next(
        (s for s in data_analyzer.sessions if s['session_id'] == session_id),
        None
    )
    
    if session is None:
        return jsonify({'error': '训练记录未找到'}), 404
    
    # Generate report
    report = data_analyzer.generate_report(format=format_type)
    
    if format_type == 'json':
        return jsonify({'report': report})
    else:
        return report, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@api.route('/progress', methods=['GET'])
def get_progress():
    """
    Get training progress over time.
    
    Query Parameters:
        - sessions: Number of sessions to analyze (default: 10)
    
    Response:
        - Progress report with trends and recommendations
    """
    num_sessions = request.args.get('sessions', 10, type=int)
    
    data_analyzer = current_app.config.get('data_analyzer')
    
    if data_analyzer is None:
        return jsonify({'error': '数据分析服务未配置'}), 500
    
    progress = data_analyzer.calculate_progress(num_sessions)
    
    return jsonify({
        'sessions_analyzed': progress.sessions_analyzed,
        'total_shots': progress.total_shots,
        'average_form_score': progress.average_form_score,
        'trend': progress.form_score_trend,
        'improvements': progress.key_improvements,
        'recommendations': progress.recommendations
    })


@api.route('/export', methods=['GET'])
def export_data():
    """
    Export training data.
    
    Query Parameters:
        - format: 'csv' or 'json' (default: 'json')
    
    Response:
        - Data file download
    """
    format_type = request.args.get('format', 'json')
    
    data_analyzer = current_app.config.get('data_analyzer')
    
    if data_analyzer is None:
        return jsonify({'error': '数据分析服务未配置'}), 500
    
    # Create temp file
    temp_dir = tempfile.gettempdir()
    filename = f'training_data.{format_type}'
    output_path = os.path.join(temp_dir, filename)
    
    data_analyzer.export_data(output_path, format=format_type)
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename
    )


@api.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Get or update system settings.
    
    GET Response:
        - Current settings
    
    POST Request:
        - Settings to update
    
    POST Response:
        - Updated settings
    """
    settings_store = current_app.config.get('settings', {})
    
    if request.method == 'GET':
        return jsonify(settings_store)
    
    # POST - update settings
    new_settings = request.get_json()
    
    if not new_settings:
        return jsonify({'error': '无效的设置数据'}), 400
    
    # Update settings
    allowed_keys = ['shooting_hand', 'skip_frames', 'conf_threshold', 'show_angles']
    for key in allowed_keys:
        if key in new_settings:
            settings_store[key] = new_settings[key]
    
    current_app.config['settings'] = settings_store
    
    return jsonify(settings_store)
