// 个人资料页面脚本

const API_BASE = window.location.origin;
let currentUser = null;

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
    initEventListeners();
});

function checkLoginStatus() {
    fetch(`${API_BASE}/api/user/info`, {
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentUser = data.user;
            displayUserInfo();
            loadFeedback();
        } else {
            window.location.href = '/';
        }
    })
    .catch(err => {
        console.error('获取用户信息错误:', err);
        window.location.href = '/';
    });
}

function displayUserInfo() {
    // 显示用户名
    document.getElementById('username').value = currentUser.username;
    document.getElementById('displayName').textContent = currentUser.full_name || currentUser.username;
    
    // 显示角色
    const roleNames = { 'student': '学生', 'teacher': '教师' };
    document.getElementById('userRole').textContent = roleNames[currentUser.role] || '学生';
    
    // 填充表单
    document.getElementById('fullName').value = currentUser.full_name || '';
    document.getElementById('studentId').value = currentUser.student_id || '';
    document.getElementById('age').value = currentUser.age || '';
    document.getElementById('phone').value = currentUser.phone || '';
    document.getElementById('email').value = currentUser.email || '';
    
    // 显示头像
    if (currentUser.avatar_url) {
        document.getElementById('avatarImg').src = currentUser.avatar_url;
    }
    
    // 显示学校信息
    displaySchoolInfo();
    
    // 如果是教师，隐藏反馈区域
    if (currentUser.role === 'teacher') {
        document.getElementById('feedbackSection').style.display = 'none';
    }
}

function displaySchoolInfo() {
    const schoolInfo = document.getElementById('schoolInfo');
    
    if (currentUser.school_name) {
        schoolInfo.classList.add('bound');
        schoolInfo.innerHTML = `
            <p class="school-name">🏫 ${currentUser.school_name}</p>
            <p>学校代码: ${currentUser.school_code || '-'}</p>
            <p>班级: ${currentUser.class_name || '未选择'} ${currentUser.grade || ''}</p>
        `;
    } else {
        schoolInfo.classList.remove('bound');
        schoolInfo.innerHTML = '<p class="not-bound">未绑定学校，请输入学校代码进行绑定</p>';
    }
}

function initEventListeners() {
    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // 保存资料
    document.getElementById('profileForm').addEventListener('submit', saveProfile);
    
    // 学校代码变化时加载班级
    document.getElementById('schoolCode').addEventListener('blur', loadClasses);
    
    // 绑定学校
    document.getElementById('bindSchoolBtn').addEventListener('click', bindSchool);
    
    // 头像上传
    document.querySelector('.avatar-wrapper').addEventListener('click', function() {
        document.getElementById('avatarInput').click();
    });
    
    document.getElementById('avatarInput').addEventListener('change', uploadAvatar);
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

async function saveProfile(e) {
    e.preventDefault();
    
    const data = {
        full_name: document.getElementById('fullName').value,
        student_id: document.getElementById('studentId').value,
        age: parseInt(document.getElementById('age').value) || null,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/user/profile`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('资料保存成功！');
            checkLoginStatus(); // 重新加载用户信息
        } else {
            alert('保存失败: ' + result.message);
        }
    } catch (err) {
        console.error('保存错误:', err);
        alert('保存失败，请重试');
    }
}

async function loadClasses() {
    const schoolCode = document.getElementById('schoolCode').value.trim();
    
    if (!schoolCode) {
        document.getElementById('classSelectGroup').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/schools/${schoolCode}/classes`);
        const data = await response.json();
        
        if (data.success && data.classes.length > 0) {
            const select = document.getElementById('classSelect');
            select.innerHTML = '<option value="">请选择班级</option>';
            
            data.classes.forEach(cls => {
                select.innerHTML += `<option value="${cls.id}">${cls.grade || ''} ${cls.class_name}</option>`;
            });
            
            document.getElementById('classSelectGroup').style.display = 'block';
        } else {
            document.getElementById('classSelectGroup').style.display = 'none';
        }
    } catch (err) {
        console.error('加载班级错误:', err);
    }
}

async function bindSchool() {
    const schoolCode = document.getElementById('schoolCode').value.trim();
    const classId = document.getElementById('classSelect').value;
    
    if (!schoolCode) {
        alert('请输入学校代码');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/user/bind-school`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({
                school_code: schoolCode,
                class_id: classId || null
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('学校绑定成功！');
            checkLoginStatus(); // 重新加载用户信息
        } else {
            alert('绑定失败: ' + result.message);
        }
    } catch (err) {
        console.error('绑定错误:', err);
        alert('绑定失败，请重试');
    }
}

async function uploadAvatar(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // 这里简单处理，实际应该上传到服务器
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('avatarImg').src = e.target.result;
        // TODO: 上传到服务器并保存URL
        alert('头像已更新（本地预览）');
    };
    reader.readAsDataURL(file);
}

async function loadFeedback() {
    if (currentUser.role === 'teacher') return;
    
    try {
        const response = await fetch(`${API_BASE}/api/student/feedback`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success && data.feedback.length > 0) {
            const feedbackList = document.getElementById('feedbackList');
            feedbackList.innerHTML = data.feedback.map(fb => `
                <div class="feedback-item">
                    <div class="teacher-name">👨‍🏫 ${fb.teacher_name || fb.teacher_username}</div>
                    <div class="feedback-text">${fb.feedback_text}</div>
                    <div class="feedback-date">${new Date(fb.created_at).toLocaleString('zh-CN')}</div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('加载反馈错误:', err);
    }
}
