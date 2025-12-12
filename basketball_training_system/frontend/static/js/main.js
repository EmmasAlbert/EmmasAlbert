// 全局变量
let currentUser = null;
let cameraStream = null;
let cameraInterval = null;

// API基础URL
const API_BASE = window.location.origin;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initFunctionTabs();
    initCameraControls();
    initVideoUpload();
    checkLoginStatus();
});

// ========== 认证相关 ==========

// 检查登录状态
function checkLoginStatus() {
    fetch(`${API_BASE}/api/user/info`, {
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentUser = data.user;
                showMainSection();
            } else {
                // 未登录，跳转到登录页
                window.location.href = '/';
            }
        })
        .catch(err => {
            console.log('未登录，跳转到登录页');
            window.location.href = '/';
        });
}

// 登出
function logout() {
    fetch(`${API_BASE}/api/logout`, {
        method: 'POST',
        credentials: 'include'
    })
        .then(() => {
            currentUser = null;
            stopCamera();
            window.location.href = '/';
        });
}

// 显示主功能区
function showMainSection() {
    document.getElementById('mainSection').style.display = 'block';
    
    // 显示欢迎信息，包括学段信息
    let welcomeText = `欢迎, ${currentUser.full_name || currentUser.username}`;
    if (currentUser.age) {
        welcomeText += ` (${currentUser.age}岁)`;
    }
    if (currentUser.student_level) {
        const levelNames = {
            'primary': '小学',
            'junior': '初中',
            'senior': '高中'
        };
        welcomeText += ` [${levelNames[currentUser.student_level]}]`;
    }
    
    document.getElementById('welcomeMsg').textContent = welcomeText;
    document.getElementById('logoutBtn').style.display = 'inline-block';
    document.getElementById('logoutBtn').onclick = logout;
    
    // 显示个人资料链接
    document.getElementById('profileLink').style.display = 'inline-block';
    
    // 如果是教师，显示教师控制台链接
    if (currentUser.role === 'teacher') {
        document.getElementById('teacherLink').style.display = 'inline-block';
    }
    
    loadTrainingHistory();
}

// 显示消息
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
}

// ========== 标签页切换 ==========

function initFunctionTabs() {
    document.querySelectorAll('.func-tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const func = this.getAttribute('data-func');
            
            document.querySelectorAll('.func-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.function-panel').forEach(p => p.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(func + 'Mode').classList.add('active');
            
            if (func === 'history') {
                loadTrainingHistory();
            }
        });
    });
}

// ========== 摄像头功能 ==========

function initCameraControls() {
    document.getElementById('startCameraBtn').addEventListener('click', startCamera);
    document.getElementById('stopCameraBtn').addEventListener('click', stopCamera);
}

async function startCamera() {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {width: 1280, height: 720}
        });
        
        const video = document.getElementById('cameraVideo');
        video.srcObject = cameraStream;
        
        document.getElementById('startCameraBtn').style.display = 'none';
        document.getElementById('stopCameraBtn').style.display = 'inline-block';
        
        // 开始定期捕获和处理帧
        cameraInterval = setInterval(captureAndProcessFrame, 1000); // 每秒处理一次
        
    } catch (err) {
        alert('无法访问摄像头: ' + err.message);
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    if (cameraInterval) {
        clearInterval(cameraInterval);
        cameraInterval = null;
    }
    
    const video = document.getElementById('cameraVideo');
    video.srcObject = null;
    
    document.getElementById('startCameraBtn').style.display = 'inline-block';
    document.getElementById('stopCameraBtn').style.display = 'none';
    
    document.getElementById('cameraFeedback').textContent = '摄像头已关闭';
}

async function captureAndProcessFrame() {
    const video = document.getElementById('cameraVideo');
    const canvas = document.getElementById('cameraCanvas');
    const context = canvas.getContext('2d');
    
    // 只在首次设置canvas尺寸
    if (canvas.width === 0) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    }
    
    // 捕获当前帧
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg');
    
    try {
        const response = await fetch(`${API_BASE}/api/camera/frame`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({image: imageData})
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 更新检测信息
            document.getElementById('ballCount').textContent = data.detections.basketball;
            document.getElementById('personCount').textContent = data.detections.players;
            document.getElementById('hoopCount').textContent = data.detections.hoops;
            
            // 在canvas上绘制处理后的图像（叠加层）
            const img = new Image();
            img.onload = function() {
                // 清除canvas
                context.clearRect(0, 0, canvas.width, canvas.height);
                // 绘制处理后的图像
                context.drawImage(img, 0, 0, canvas.width, canvas.height);
                // 显示canvas叠加层
                canvas.style.display = 'block';
                
                // 短暂显示后隐藏，让原始视频流继续显示
                setTimeout(() => {
                    canvas.style.display = 'none';
                }, 800);
            };
            img.src = data.image;
            
            // 更新分析反馈
            if (data.analysis) {
                const feedbackDiv = document.getElementById('cameraFeedback');
                feedbackDiv.innerHTML = `
                    <strong>投篮分析 (得分: ${data.analysis.form_score.toFixed(1)}/100)</strong><br>
                    ${data.analysis.feedback.join('<br>')}
                `;
            } else {
                document.getElementById('cameraFeedback').textContent = '正在监测中...';
            }
        }
    } catch (err) {
        console.error('处理帧错误:', err);
    }
}

// ========== 视频上传功能 ==========

function initVideoUpload() {
    const fileInput = document.getElementById('videoFileInput');
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            document.getElementById('videoFileName').textContent = `已选择: ${file.name}`;
            document.getElementById('uploadBtn').style.display = 'inline-block';
        }
    });
    
    document.getElementById('uploadBtn').addEventListener('click', uploadAndProcessVideo);
}

async function uploadAndProcessVideo() {
    const fileInput = document.getElementById('videoFileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('请先选择视频文件');
        return;
    }
    
    const progressContainer = document.querySelector('.progress-container');
    const progressFill = document.getElementById('uploadProgress');
    const statusText = document.getElementById('uploadStatus');
    
    progressContainer.style.display = 'block';
    document.getElementById('uploadBtn').disabled = true;
    
    // 上传文件
    const formData = new FormData();
    formData.append('video', file);
    
    try {
        statusText.textContent = '正在上传视频...';
        progressFill.style.width = '30%';
        
        const uploadResponse = await fetch(`${API_BASE}/api/upload`, {
            method: 'POST',
            body: formData
        });
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadData.success) {
            throw new Error(uploadData.message);
        }
        
        progressFill.style.width = '60%';
        statusText.textContent = '正在分析视频...';
        
        // 处理视频
        const processResponse = await fetch(`${API_BASE}/api/process/video`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({video_path: uploadData.filepath})
        });
        
        const processData = await processResponse.json();
        
        if (!processData.success) {
            throw new Error(processData.message);
        }
        
        progressFill.style.width = '100%';
        statusText.textContent = '分析完成！';
        
        // 显示结果
        displayVideoResults(processData.results);
        
    } catch (err) {
        alert('处理失败: ' + err.message);
        statusText.textContent = '处理失败';
    } finally {
        document.getElementById('uploadBtn').disabled = false;
        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
        }, 2000);
    }
}

function displayVideoResults(results) {
    const resultsDiv = document.getElementById('videoResults');
    const report = results.report;
    
    // 显示视频分析区域
    const analysisSection = document.getElementById('videoAnalysisSection');
    analysisSection.style.display = 'grid';
    
    // 如果有输出视频，加载它
    if (results.output_video) {
        const videoEl = document.getElementById('analyzedVideo');
        videoEl.src = `/outputs/${results.output_video.split('/').pop()}`;
        videoEl.load();
    }
    
    // 更新统计数据
    document.getElementById('totalShots').textContent = report.total_shots;
    document.getElementById('validShots').textContent = report.valid_shots || 0;
    document.getElementById('avgScore').textContent = report.average_score.toFixed(1);
    
    // 计算平均肘部角度
    if (report.shots && report.shots.length > 0) {
        const avgAngle = report.shots.reduce((sum, shot) => sum + (shot.elbow_angle || 0), 0) / report.shots.length;
        document.getElementById('avgElbowAngle').textContent = avgAngle.toFixed(1) + '°';
    }
    
    let scoreClass = 'score-needs-improvement';
    if (report.average_score >= 80) scoreClass = 'score-excellent';
    else if (report.average_score >= 60) scoreClass = 'score-good';
    
    // 生成投篮时间线
    let shotTimelineHtml = '';
    if (report.shots && report.shots.length > 0) {
        shotTimelineHtml = `
        <div class="detail-analysis-card">
            <h3>⏱️ 投篮时间线</h3>
            <div class="shot-timeline">
                ${report.shots.map((shot, index) => {
                    let badgeClass = 'needs-improvement';
                    if (shot.score >= 80) badgeClass = 'excellent';
                    else if (shot.score >= 60) badgeClass = 'good';
                    return `<span class="shot-badge ${badgeClass}">
                        #${index + 1}: ${shot.score.toFixed(0)}分
                    </span>`;
                }).join('')}
            </div>
        </div>
        `;
    }
    
    // 生成建议列表
    let suggestionsHtml = '';
    if (report.common_issues && report.common_issues.length > 0) {
        suggestionsHtml = `
        <div class="suggestions-card">
            <h3>💡 改进建议</h3>
            ${report.common_issues.map(issue => `
                <div class="suggestion-item">
                    <span class="suggestion-icon">📌</span>
                    <span class="suggestion-text">${issue}</span>
                </div>
            `).join('')}
        </div>
        `;
    }
    
    resultsDiv.innerHTML = `
        <div class="result-card">
            <h3>📋 分析报告</h3>
            <p><strong>总投篮次数:</strong> ${report.total_shots}</p>
            <p><strong>有效投篮:</strong> ${report.valid_shots}</p>
            <p><strong>平均得分:</strong> <span class="score-badge ${scoreClass}">${report.average_score.toFixed(1)}分</span></p>
            <p><strong>评语:</strong> ${report.summary}</p>
        </div>
        
        ${shotTimelineHtml}
        
        <div class="result-card">
            <h3>📊 得分分布</h3>
            <p>✅ 优秀 (≥80分): <strong>${report.score_distribution.excellent}</strong> 次</p>
            <p>👍 良好 (60-79分): <strong>${report.score_distribution.good}</strong> 次</p>
            <p>📈 需改进 (<60分): <strong>${report.score_distribution.needs_improvement}</strong> 次</p>
        </div>
        
        ${suggestionsHtml}
    `;
}

// ========== 训练历史 ==========

async function loadTrainingHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '加载中...';
    
    try {
        const response = await fetch(`${API_BASE}/api/training/history?limit=20`);
        const data = await response.json();
        
        if (data.success && data.history.length > 0) {
            historyList.innerHTML = data.history.map(session => {
                const date = new Date(session.session_date);
                const dateStr = date.toLocaleString('zh-CN');
                
                let scoreClass = 'score-needs-improvement';
                if (session.average_score >= 80) scoreClass = 'score-excellent';
                else if (session.average_score >= 60) scoreClass = 'score-good';
                
                return `
                    <div class="history-item" onclick="viewSessionDetails(${session.id})">
                        <h4>训练记录 #${session.id}</h4>
                        <p>📅 时间: ${dateStr}</p>
                        <p>🏀 投篮次数: ${session.total_shots}</p>
                        <p>📊 平均得分: <span class="score-badge ${scoreClass}">${session.average_score.toFixed(1)}分</span></p>
                        ${session.notes ? `<p>📝 备注: ${session.notes}</p>` : ''}
                    </div>
                `;
            }).join('');
        } else {
            historyList.innerHTML = '<p>暂无训练记录</p>';
        }
    } catch (err) {
        historyList.innerHTML = '<p>加载失败</p>';
        console.error('加载训练历史错误:', err);
    }
}

async function viewSessionDetails(sessionId) {
    try {
        const response = await fetch(`${API_BASE}/api/training/session/${sessionId}`);
        const data = await response.json();
        
        if (data.success) {
            // 可以在这里添加更详细的查看逻辑
            alert(`训练记录 #${sessionId}\n共 ${data.analysis.length} 次投篮分析`);
        }
    } catch (err) {
        console.error('加载训练详情错误:', err);
    }
}
