/**
 * Basketball Training System - Analysis Page JavaScript
 * 篮球训练辅助系统 - 分析页面JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    initVideoUpload();
    initImageUpload();
});

/**
 * Initialize video upload functionality
 */
function initVideoUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const videoInput = document.getElementById('videoInput');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const selectedFile = document.getElementById('selectedFile');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsContent = document.getElementById('resultsContent');
    
    let currentFile = null;
    
    // Click to select file
    selectFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        videoInput.click();
    });
    
    uploadArea.addEventListener('click', () => {
        videoInput.click();
    });
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // File input change
    videoInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Remove file
    removeFile.addEventListener('click', () => {
        currentFile = null;
        videoInput.value = '';
        selectedFile.style.display = 'none';
        analyzeBtn.disabled = true;
    });
    
    // Handle file selection
    function handleFileSelect(file) {
        const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm'];
        const allowedExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];
        
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedExtensions.includes(extension)) {
            showToast('请上传支持的视频格式 (MP4, AVI, MOV, MKV, WebM)');
            return;
        }
        
        currentFile = file;
        fileName.textContent = file.name;
        selectedFile.style.display = 'flex';
        analyzeBtn.disabled = false;
    }
    
    // Analyze button click
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;
        
        const shootingHand = document.getElementById('shootingHand').value;
        const skipFrames = document.getElementById('skipFrames').value;
        
        // Show loading
        resultsSection.style.display = 'block';
        loadingIndicator.style.display = 'block';
        resultsContent.style.display = 'none';
        analyzeBtn.disabled = true;
        
        try {
            const formData = new FormData();
            formData.append('file', currentFile);
            formData.append('shooting_hand', shootingHand);
            formData.append('skip_frames', skipFrames);
            
            const response = await fetch('/api/analyze/video', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                displayResults(result);
            } else {
                throw new Error(result.error || '分析失败');
            }
        } catch (error) {
            showToast(error.message);
            loadingIndicator.style.display = 'none';
        } finally {
            analyzeBtn.disabled = false;
        }
    });
    
    // Display analysis results
    function displayResults(result) {
        loadingIndicator.style.display = 'none';
        resultsContent.style.display = 'block';
        
        const stats = result.statistics || {};
        
        // Update statistics
        document.getElementById('totalShots').textContent = stats.total_shots || 0;
        document.getElementById('qualityScore').textContent = formatPercent(stats.form_quality_score);
        document.getElementById('avgElbow').textContent = formatAngle(stats.average_elbow_angle);
        document.getElementById('avgKnee').textContent = formatAngle(stats.average_knee_angle);
        
        // Update improvements
        const improvementsList = document.getElementById('improvementsList');
        improvementsList.innerHTML = '';
        const improvements = result.improvements || [];
        if (improvements.length > 0) {
            improvements.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                improvementsList.appendChild(li);
            });
        } else {
            improvementsList.innerHTML = '<li>继续训练以获取更多反馈</li>';
        }
        
        // Update areas to work
        const areasList = document.getElementById('areasToWorkList');
        areasList.innerHTML = '';
        const areas = result.areas_to_work || [];
        if (areas.length > 0) {
            areas.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                areasList.appendChild(li);
            });
        } else {
            areasList.innerHTML = '<li>保持当前训练方法</li>';
        }
        
        showToast('分析完成！');
    }
}

/**
 * Initialize image upload functionality
 */
function initImageUpload() {
    const imageUploadArea = document.getElementById('imageUploadArea');
    const imageInput = document.getElementById('imageInput');
    const selectImageBtn = document.getElementById('selectImageBtn');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const imageAnalysisResult = document.getElementById('imageAnalysisResult');
    
    // Click to select image
    selectImageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        imageInput.click();
    });
    
    imageUploadArea.addEventListener('click', () => {
        imageInput.click();
    });
    
    // Drag and drop
    imageUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        imageUploadArea.classList.add('dragover');
    });
    
    imageUploadArea.addEventListener('dragleave', () => {
        imageUploadArea.classList.remove('dragover');
    });
    
    imageUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        imageUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageSelect(files[0]);
        }
    });
    
    // File input change
    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageSelect(e.target.files[0]);
        }
    });
    
    // Handle image selection
    async function handleImageSelect(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
        
        if (!allowedTypes.includes(file.type)) {
            showToast('请上传 JPG 或 PNG 格式的图片');
            return;
        }
        
        // Preview image
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
        
        // Analyze image
        imageAnalysisResult.innerHTML = '<p>正在分析...</p>';
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('shooting_hand', document.getElementById('shootingHand')?.value || 'right');
            
            const response = await fetch('/api/analyze/frame', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                displayImageResults(result);
            } else {
                throw new Error(result.error || '分析失败');
            }
        } catch (error) {
            imageAnalysisResult.innerHTML = `<p style="color: var(--danger-color);">分析失败: ${error.message}</p>`;
        }
    }
    
    // Display image analysis results
    function displayImageResults(result) {
        const analysis = result.analysis || {};
        const detections = result.detections || [];
        const poses = result.poses || [];
        
        let html = '<h4>分析结果</h4>';
        
        // Detection info
        html += `<p><strong>检测到的对象:</strong> ${detections.length} 个</p>`;
        detections.forEach(det => {
            html += `<p>- ${det.class_name} (置信度: ${(det.confidence * 100).toFixed(0)}%)</p>`;
        });
        
        // Pose info
        html += `<p><strong>检测到的姿态:</strong> ${poses.length} 个</p>`;
        
        // Action analysis
        if (analysis.action_type) {
            const actionNames = {
                'idle': '待机',
                'shooting': '投篮',
                'dribbling': '运球',
                'unknown': '未知'
            };
            html += `<p><strong>动作类型:</strong> ${actionNames[analysis.action_type] || analysis.action_type}</p>`;
            html += `<p><strong>置信度:</strong> ${(analysis.confidence * 100).toFixed(0)}%</p>`;
        }
        
        // Details
        if (analysis.details) {
            const details = analysis.details;
            if (details.elbow_angle) {
                html += `<p><strong>肘部角度:</strong> ${details.elbow_angle.toFixed(1)}°</p>`;
            }
            if (details.knee_angle) {
                html += `<p><strong>膝盖角度:</strong> ${details.knee_angle.toFixed(1)}°</p>`;
            }
            if (details.phase) {
                const phases = {
                    'preparation': '准备',
                    'loading': '蓄力',
                    'release': '出手',
                    'follow_through': '跟随'
                };
                html += `<p><strong>投篮阶段:</strong> ${phases[details.phase] || details.phase}</p>`;
            }
        }
        
        imageAnalysisResult.innerHTML = html;
    }
}
