// 教师控制台脚本

const API_BASE = window.location.origin;
let currentTeacher = null;
let selectedStudent = null;
let schoolClasses = [];

document.addEventListener('DOMContentLoaded', function() {
    checkTeacherLogin();
    initEventListeners();
});

function checkTeacherLogin() {
    fetch(`${API_BASE}/api/user/info`, {
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.user.role === 'teacher') {
            currentTeacher = data.user;
            document.getElementById('teacherName').textContent = 
                `${currentTeacher.full_name || currentTeacher.username} 老师`;
            loadClasses();
            loadStudents();
        } else {
            window.location.href = '/dashboard';
        }
    })
    .catch(err => {
        console.error('获取用户信息错误:', err);
        window.location.href = '/';
    });
}

function initEventListeners() {
    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // 搜索
    document.getElementById('searchBtn').addEventListener('click', searchStudents);
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') searchStudents();
    });
    
    // 班级筛选
    document.getElementById('classFilter').addEventListener('change', function() {
        loadStudents(this.value || null);
    });
}

function logout() {
    fetch(`${API_BASE}/api/logout`, {
        method: 'POST',
        credentials: 'include'
    })
    .then(() => {
        window.location.href = '/';
    });
}

async function loadClasses() {
    if (!currentTeacher.school_code) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/schools/${currentTeacher.school_code}/classes`);
        const data = await response.json();
        
        if (data.success) {
            schoolClasses = data.classes;
            const select = document.getElementById('classFilter');
            select.innerHTML = '<option value="">全部班级</option>';
            
            data.classes.forEach(cls => {
                select.innerHTML += `<option value="${cls.id}">${cls.grade || ''} ${cls.class_name}</option>`;
            });
        }
    } catch (err) {
        console.error('加载班级错误:', err);
    }
}

async function loadStudents(classId = null) {
    const studentList = document.getElementById('studentList');
    studentList.innerHTML = '<p class="loading">加载中...</p>';
    
    try {
        let url = `${API_BASE}/api/teacher/students`;
        if (classId) {
            url += `?class_id=${classId}`;
        }
        
        const response = await fetch(url, { credentials: 'include' });
        const data = await response.json();
        
        if (data.success) {
            displayStudentList(data.students);
        } else {
            studentList.innerHTML = `<p class="loading">${data.message}</p>`;
        }
    } catch (err) {
        console.error('加载学生列表错误:', err);
        studentList.innerHTML = '<p class="loading">加载失败</p>';
    }
}

async function searchStudents() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (query.length < 2) {
        alert('请输入至少2个字符');
        return;
    }
    
    const studentList = document.getElementById('studentList');
    studentList.innerHTML = '<p class="loading">搜索中...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/teacher/search?q=${encodeURIComponent(query)}`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayStudentList(data.students);
        } else {
            studentList.innerHTML = `<p class="loading">${data.message}</p>`;
        }
    } catch (err) {
        console.error('搜索错误:', err);
        studentList.innerHTML = '<p class="loading">搜索失败</p>';
    }
}

function displayStudentList(students) {
    const studentList = document.getElementById('studentList');
    
    if (students.length === 0) {
        studentList.innerHTML = '<p class="loading">暂无学生数据</p>';
        return;
    }
    
    studentList.innerHTML = students.map(student => `
        <div class="student-card" onclick="selectStudent(${student.id})" id="student-${student.id}">
            <div class="student-name">${student.full_name || student.username}</div>
            <div class="student-info">
                ${student.student_id ? `学号: ${student.student_id} | ` : ''}
                ${student.class_name || '未分班'} ${student.grade || ''}
            </div>
            <div class="student-stats">
                <span class="stat">📊 ${student.session_count || 0} 次训练</span>
                <span class="stat">⭐ ${student.avg_score ? student.avg_score.toFixed(1) : '-'} 分</span>
            </div>
        </div>
    `).join('');
}

async function selectStudent(studentId) {
    // 更新选中状态
    document.querySelectorAll('.student-card').forEach(card => {
        card.classList.remove('active');
    });
    document.getElementById(`student-${studentId}`).classList.add('active');
    
    // 加载学生详情
    try {
        const response = await fetch(`${API_BASE}/api/teacher/student/${studentId}/stats`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            selectedStudent = data.stats.student;
            displayStudentDetail(data.stats);
        }
    } catch (err) {
        console.error('加载学生详情错误:', err);
    }
}

function displayStudentDetail(stats) {
    const detailDiv = document.getElementById('studentDetail');
    const student = stats.student;
    
    // 分数颜色类
    const getScoreClass = (score) => {
        if (score >= 80) return 'score-excellent';
        if (score >= 60) return 'score-good';
        return 'score-low';
    };
    
    let historyHtml = '';
    if (stats.recent_sessions && stats.recent_sessions.length > 0) {
        historyHtml = `
            <table class="history-table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>投篮次数</th>
                        <th>平均分</th>
                    </tr>
                </thead>
                <tbody>
                    ${stats.recent_sessions.map(session => `
                        <tr>
                            <td>${new Date(session.session_date).toLocaleDateString('zh-CN')}</td>
                            <td>${session.total_shots}</td>
                            <td class="${getScoreClass(session.average_score)}">${session.average_score.toFixed(1)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else {
        historyHtml = '<p style="color:#999;text-align:center;">暂无训练记录</p>';
    }
    
    detailDiv.innerHTML = `
        <div class="detail-header">
            <div class="detail-avatar">👤</div>
            <div class="detail-info">
                <h2>${student.full_name || student.username}</h2>
                <p>学号: ${student.student_id || '未填写'} | ${student.class_name || '未分班'} ${student.grade || ''}</p>
                <p>年龄: ${student.age || '-'}岁 | 学段: ${getLevelName(student.student_level)}</p>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${stats.total_sessions || 0}</div>
                <div class="stat-label">训练次数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.total_shots || 0}</div>
                <div class="stat-label">总投篮数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.avg_score ? stats.avg_score.toFixed(1) : '-'}</div>
                <div class="stat-label">平均分</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${stats.best_score ? stats.best_score.toFixed(1) : '-'}</div>
                <div class="stat-label">最高分</div>
            </div>
        </div>
        
        <div class="history-section">
            <h3>📋 最近训练记录</h3>
            ${historyHtml}
        </div>
        
        <div class="feedback-section-teacher">
            <h3>
                💬 训练建议
                <button class="btn btn-primary add-feedback-btn" onclick="openFeedbackModal()">添加反馈</button>
            </h3>
            <p style="color:#666;">点击"添加反馈"可以给学生提供训练建议和指导。</p>
        </div>
    `;
}

function getLevelName(level) {
    const names = {
        'primary': '小学',
        'junior': '初中',
        'senior': '高中'
    };
    return names[level] || '未知';
}

function openFeedbackModal() {
    if (!selectedStudent) {
        alert('请先选择一个学生');
        return;
    }
    
    document.getElementById('feedbackStudentName').textContent = 
        `学生: ${selectedStudent.full_name || selectedStudent.username}`;
    document.getElementById('feedbackText').value = '';
    document.getElementById('feedbackModal').style.display = 'flex';
}

function closeFeedbackModal() {
    document.getElementById('feedbackModal').style.display = 'none';
}

async function submitFeedback() {
    const feedbackText = document.getElementById('feedbackText').value.trim();
    
    if (!feedbackText) {
        alert('请输入反馈内容');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/teacher/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                student_id: selectedStudent.id,
                feedback: feedbackText
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('反馈已提交！');
            closeFeedbackModal();
        } else {
            alert('提交失败: ' + result.message);
        }
    } catch (err) {
        console.error('提交反馈错误:', err);
        alert('提交失败，请重试');
    }
}
