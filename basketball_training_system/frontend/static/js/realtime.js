/**
 * Basketball Training System - Realtime Detection JavaScript
 * 篮球训练辅助系统 - 实时检测JavaScript
 */

// Global state
let isWebcamActive = false;
let isDetecting = false;
let webcamStream = null;
let animationFrameId = null;
let lastFrameTime = 0;
let frameCount = 0;
let fpsValue = 0;
let shotCount = 0;
let analysisResults = [];

// Skeleton connections for drawing
const SKELETON_CONNECTIONS = [
    ['left_shoulder', 'right_shoulder'],
    ['left_shoulder', 'left_elbow'],
    ['left_elbow', 'left_wrist'],
    ['right_shoulder', 'right_elbow'],
    ['right_elbow', 'right_wrist'],
    ['left_shoulder', 'left_hip'],
    ['right_shoulder', 'right_hip'],
    ['left_hip', 'right_hip'],
    ['left_hip', 'left_knee'],
    ['left_knee', 'left_ankle'],
    ['right_hip', 'right_knee'],
    ['right_knee', 'right_ankle'],
    ['nose', 'left_eye'],
    ['nose', 'right_eye'],
    ['left_eye', 'left_ear'],
    ['right_eye', 'right_ear']
];

// Colors
const COLORS = {
    skeleton: '#00ff00',
    keypoint: '#ff0000',
    basketball: '#ffa500',
    player: '#00ff00',
    text: '#ffffff',
    good: '#28a745',
    warning: '#ffc107',
    bad: '#dc3545'
};

document.addEventListener('DOMContentLoaded', () => {
    initModeTabs();
    initWebcamControls();
    initVideoUpload();
    initSettings();
});

/**
 * Initialize mode tabs (webcam/video)
 */
function initModeTabs() {
    const tabs = document.querySelectorAll('.mode-tab');
    const webcamMode = document.getElementById('webcamMode');
    const videoMode = document.getElementById('videoMode');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const mode = tab.dataset.mode;
            if (mode === 'webcam') {
                webcamMode.style.display = 'block';
                videoMode.style.display = 'none';
                // Stop video if playing
                const videoElement = document.getElementById('videoElement');
                if (videoElement) videoElement.pause();
            } else {
                webcamMode.style.display = 'none';
                videoMode.style.display = 'block';
                // Stop webcam if active
                if (isWebcamActive) {
                    stopWebcam();
                }
            }
        });
    });
}

/**
 * Initialize webcam controls
 */
function initWebcamControls() {
    const startBtn = document.getElementById('startWebcam');
    const stopBtn = document.getElementById('stopWebcam');
    const toggleBtn = document.getElementById('toggleDetection');
    const recordingIndicator = document.getElementById('recordingIndicator');
    
    startBtn.addEventListener('click', async () => {
        await startWebcam();
    });
    
    stopBtn.addEventListener('click', () => {
        stopWebcam();
    });
    
    toggleBtn.addEventListener('click', () => {
        if (isDetecting) {
            stopDetection();
            toggleBtn.textContent = '🔍 开始检测';
            recordingIndicator.classList.remove('active');
        } else {
            startDetection();
            toggleBtn.textContent = '⏸ 暂停检测';
            recordingIndicator.classList.add('active');
        }
    });
}

/**
 * Start webcam stream
 */
async function startWebcam() {
    const video = document.getElementById('webcamElement');
    const canvas = document.getElementById('canvasOverlay');
    const startBtn = document.getElementById('startWebcam');
    const stopBtn = document.getElementById('stopWebcam');
    const toggleBtn = document.getElementById('toggleDetection');
    
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        });
        
        video.srcObject = webcamStream;
        
        video.onloadedmetadata = () => {
            video.play();
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            isWebcamActive = true;
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            toggleBtn.disabled = false;
            
            showToast('摄像头已启动');
        };
    } catch (err) {
        console.error('Error accessing webcam:', err);
        showToast('无法访问摄像头: ' + err.message);
    }
}

/**
 * Stop webcam stream
 */
function stopWebcam() {
    const video = document.getElementById('webcamElement');
    const startBtn = document.getElementById('startWebcam');
    const stopBtn = document.getElementById('stopWebcam');
    const toggleBtn = document.getElementById('toggleDetection');
    const recordingIndicator = document.getElementById('recordingIndicator');
    
    if (isDetecting) {
        stopDetection();
    }
    
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        webcamStream = null;
    }
    
    isWebcamActive = false;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    toggleBtn.disabled = true;
    toggleBtn.textContent = '🔍 开始检测';
    recordingIndicator.classList.remove('active');
    
    // Clear canvas
    const canvas = document.getElementById('canvasOverlay');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    showToast('摄像头已停止');
}

/**
 * Start detection loop
 */
function startDetection() {
    isDetecting = true;
    lastFrameTime = performance.now();
    frameCount = 0;
    detectFrame();
}

/**
 * Stop detection loop
 */
function stopDetection() {
    isDetecting = false;
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

/**
 * Detection loop - capture and analyze frames
 */
async function detectFrame() {
    if (!isDetecting || !isWebcamActive) return;
    
    const video = document.getElementById('webcamElement');
    const canvas = document.getElementById('canvasOverlay');
    const ctx = canvas.getContext('2d');
    
    // Capture frame
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(video, 0, 0);
    
    // Convert to blob and send for analysis
    tempCanvas.toBlob(async (blob) => {
        try {
            const formData = new FormData();
            formData.append('file', blob, 'frame.jpg');
            formData.append('shooting_hand', document.getElementById('shootingHand').value);
            
            const response = await fetch('/api/analyze/frame', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                drawResults(ctx, canvas, result);
                updateStats(result);
            }
        } catch (err) {
            console.error('Analysis error:', err);
        }
        
        // Calculate FPS
        frameCount++;
        const now = performance.now();
        if (now - lastFrameTime >= 1000) {
            fpsValue = frameCount;
            frameCount = 0;
            lastFrameTime = now;
            document.getElementById('fps').textContent = fpsValue;
        }
        
        // Continue detection loop (throttle to ~10 FPS for performance)
        if (isDetecting) {
            setTimeout(() => {
                animationFrameId = requestAnimationFrame(detectFrame);
            }, 100);
        }
    }, 'image/jpeg', 0.8);
}

/**
 * Draw detection results on canvas
 */
function drawResults(ctx, canvas, result) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const detections = result.detections || [];
    const poses = result.poses || [];
    const analysis = result.analysis || {};
    
    // Draw detections (basketball, player)
    detections.forEach(det => {
        const bbox = det.bbox;
        if (bbox) {
            const color = det.class_name.toLowerCase().includes('ball') ? 
                COLORS.basketball : COLORS.player;
            
            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.strokeRect(bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]);
            
            // Label
            ctx.fillStyle = color;
            ctx.font = '16px Arial';
            const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;
            ctx.fillText(label, bbox[0], bbox[1] - 5);
        }
    });
    
    // Draw poses (skeleton)
    poses.forEach(pose => {
        const keypoints = pose.keypoints || {};
        
        // Draw skeleton lines
        ctx.strokeStyle = COLORS.skeleton;
        ctx.lineWidth = 2;
        
        SKELETON_CONNECTIONS.forEach(([start, end]) => {
            const startKp = keypoints[start];
            const endKp = keypoints[end];
            
            if (startKp && endKp && 
                startKp.confidence > 0.3 && endKp.confidence > 0.3) {
                ctx.beginPath();
                ctx.moveTo(startKp.x, startKp.y);
                ctx.lineTo(endKp.x, endKp.y);
                ctx.stroke();
            }
        });
        
        // Draw keypoints
        Object.entries(keypoints).forEach(([name, kp]) => {
            if (kp.confidence > 0.3) {
                ctx.beginPath();
                ctx.arc(kp.x, kp.y, 5, 0, 2 * Math.PI);
                ctx.fillStyle = COLORS.keypoint;
                ctx.fill();
            }
        });
    });
    
    // Draw analysis info overlay
    if (analysis.action_type) {
        drawAnalysisOverlay(ctx, canvas, analysis);
    }
}

/**
 * Draw analysis overlay on canvas
 */
function drawAnalysisOverlay(ctx, canvas, analysis) {
    const padding = 10;
    const boxWidth = 220;
    const boxHeight = 100;
    
    // Semi-transparent background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(padding, padding, boxWidth, boxHeight);
    
    // Action type
    const actionNames = {
        'idle': '待机',
        'shooting': '投篮',
        'dribbling': '运球',
        'passing': '传球',
        'unknown': '未知'
    };
    
    ctx.fillStyle = COLORS.text;
    ctx.font = 'bold 18px Arial';
    ctx.fillText(`动作: ${actionNames[analysis.action_type] || analysis.action_type}`, 
        padding + 10, padding + 25);
    
    // Confidence
    ctx.font = '14px Arial';
    ctx.fillText(`置信度: ${(analysis.confidence * 100).toFixed(0)}%`, 
        padding + 10, padding + 50);
    
    // Quality score if available
    const details = analysis.details || {};
    if (details.quality_score !== undefined) {
        const quality = details.quality_score;
        const qualityColor = quality >= 0.8 ? COLORS.good : 
                            quality >= 0.6 ? COLORS.warning : COLORS.bad;
        ctx.fillStyle = qualityColor;
        ctx.fillText(`姿势评分: ${(quality * 100).toFixed(0)}%`, 
            padding + 10, padding + 75);
    }
}

/**
 * Update statistics display
 */
function updateStats(result) {
    const detections = result.detections || [];
    const poses = result.poses || [];
    const analysis = result.analysis || {};
    const details = analysis.details || {};
    
    // Update counts
    document.getElementById('detectCount').textContent = detections.length;
    document.getElementById('poseCount').textContent = poses.length;
    
    // Update action
    const actionNames = {
        'idle': '待机',
        'shooting': '投篮',
        'dribbling': '运球',
        'passing': '传球',
        'unknown': '未知'
    };
    document.getElementById('currentAction').textContent = 
        actionNames[analysis.action_type] || '未知';
    
    // Update phase indicator
    const phases = document.querySelectorAll('.phase');
    phases.forEach(p => p.classList.remove('active'));
    if (details.phase) {
        const activePhase = document.querySelector(`.phase[data-phase="${details.phase}"]`);
        if (activePhase) activePhase.classList.add('active');
    }
    
    // Track shots
    if (analysis.action_type === 'shooting' && details.phase === 'release') {
        // Simple shot detection (could be improved with proper tracking)
        shotCount++;
        document.getElementById('shotCount').textContent = shotCount;
    }
    
    // Update angles
    if (details.elbow_angle !== null && details.elbow_angle !== undefined) {
        document.getElementById('elbowAngle').textContent = 
            `${details.elbow_angle.toFixed(0)}°`;
    }
    if (details.knee_angle !== null && details.knee_angle !== undefined) {
        document.getElementById('kneeAngle').textContent = 
            `${details.knee_angle.toFixed(0)}°`;
    }
    
    // Update feedback
    updateFeedback(details);
}

/**
 * Update feedback display
 */
function updateFeedback(details) {
    const feedbackList = document.getElementById('feedbackList');
    const feedback = details.feedback || [];
    
    if (feedback.length === 0) {
        feedbackList.innerHTML = '<li class="info">检测中，等待动作...</li>';
        return;
    }
    
    feedbackList.innerHTML = '';
    feedback.slice(0, 5).forEach(msg => {
        const li = document.createElement('li');
        li.textContent = msg;
        
        // Classify feedback
        if (msg.includes('✓') || msg.includes('良好') || msg.includes('优秀')) {
            li.className = 'good';
        } else if (msg.includes('⚠') || msg.includes('需要') || msg.includes('建议')) {
            li.className = 'warning';
        } else {
            li.className = 'info';
        }
        
        feedbackList.appendChild(li);
    });
}

/**
 * Initialize video upload and analysis
 */
function initVideoUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const videoInput = document.getElementById('videoInput');
    const videoContainer = document.getElementById('videoContainer');
    const videoControls = document.getElementById('videoControls');
    const videoElement = document.getElementById('videoElement');
    const analyzeBtn = document.getElementById('analyzeVideo');
    
    // Click to upload
    uploadZone.addEventListener('click', () => {
        videoInput.click();
    });
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleVideoFile(files[0]);
        }
    });
    
    // File input change
    videoInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleVideoFile(e.target.files[0]);
        }
    });
    
    // Analyze button
    analyzeBtn.addEventListener('click', async () => {
        await analyzeUploadedVideo();
    });
}

/**
 * Handle video file selection
 */
function handleVideoFile(file) {
    const allowedTypes = ['video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo'];
    
    if (!allowedTypes.includes(file.type) && 
        !file.name.match(/\.(mp4|webm|mov|avi|mkv)$/i)) {
        showToast('请上传支持的视频格式 (MP4, WebM, MOV, AVI)');
        return;
    }
    
    const videoElement = document.getElementById('videoElement');
    const uploadZone = document.getElementById('uploadZone');
    const videoContainer = document.getElementById('videoContainer');
    const videoControls = document.getElementById('videoControls');
    
    // Create URL and load video
    const url = URL.createObjectURL(file);
    videoElement.src = url;
    videoElement.dataset.filename = file.name;
    videoElement.dataset.file = file;
    
    // Store file for later upload
    window.currentVideoFile = file;
    
    // Show video
    uploadZone.style.display = 'none';
    videoContainer.style.display = 'block';
    videoControls.style.display = 'flex';
    
    showToast('视频已加载，点击"分析视频"开始处理');
}

/**
 * Analyze uploaded video
 */
async function analyzeUploadedVideo() {
    const file = window.currentVideoFile;
    if (!file) {
        showToast('请先选择视频文件');
        return;
    }
    
    const analyzeBtn = document.getElementById('analyzeVideo');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const playBtn = document.getElementById('playAnalyzed');
    const downloadBtn = document.getElementById('downloadAnalyzed');
    
    analyzeBtn.disabled = true;
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('shooting_hand', document.getElementById('shootingHand').value);
        formData.append('output_annotated', 'true');
        
        // Simulate progress (actual API doesn't stream progress)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            if (progress <= 90) {
                progressBar.style.width = `${progress}%`;
            }
        }, 500);
        
        const response = await fetch('/api/analyze/video', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        if (response.ok) {
            const result = await response.json();
            
            // Store results
            analysisResults = result;
            
            // Update stats with results
            displayVideoAnalysisResults(result);
            
            // Enable playback (if annotated video available)
            if (result.annotated_video_url) {
                playBtn.disabled = false;
                downloadBtn.disabled = false;
            }
            
            showToast('视频分析完成！');
        } else {
            const error = await response.json();
            throw new Error(error.error || '分析失败');
        }
    } catch (err) {
        console.error('Video analysis error:', err);
        showToast('分析失败: ' + err.message);
    } finally {
        analyzeBtn.disabled = false;
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 1000);
    }
}

/**
 * Display video analysis results
 */
function displayVideoAnalysisResults(result) {
    const stats = result.statistics || {};
    
    // Update stats display
    document.getElementById('shotCount').textContent = stats.total_shots || 0;
    
    if (stats.average_elbow_angle) {
        document.getElementById('elbowAngle').textContent = 
            `${stats.average_elbow_angle.toFixed(0)}°`;
    }
    if (stats.average_knee_angle) {
        document.getElementById('kneeAngle').textContent = 
            `${stats.average_knee_angle.toFixed(0)}°`;
    }
    
    // Update feedback
    const feedbackList = document.getElementById('feedbackList');
    const feedback = result.feedback || [];
    const improvements = result.improvements || [];
    const areasToWork = result.areas_to_work || [];
    
    feedbackList.innerHTML = '';
    
    improvements.forEach(msg => {
        const li = document.createElement('li');
        li.textContent = '✓ ' + msg;
        li.className = 'good';
        feedbackList.appendChild(li);
    });
    
    areasToWork.forEach(msg => {
        const li = document.createElement('li');
        li.textContent = '⚠ ' + msg;
        li.className = 'warning';
        feedbackList.appendChild(li);
    });
    
    if (feedbackList.children.length === 0) {
        feedbackList.innerHTML = '<li class="info">分析完成，继续训练以获取更多反馈</li>';
    }
}

/**
 * Initialize settings controls
 */
function initSettings() {
    const confSlider = document.getElementById('confThreshold');
    const confValue = document.getElementById('confValue');
    
    confSlider.addEventListener('input', (e) => {
        confValue.textContent = e.target.value;
    });
}
