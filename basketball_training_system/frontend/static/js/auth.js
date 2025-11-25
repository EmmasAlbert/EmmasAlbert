// 认证页面JavaScript

const API_BASE = window.location.origin;

// 登录处理
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('loginMessage');
    
    if (!username || !password) {
        showMessage(messageDiv, '请填写用户名和密码', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify({username, password})
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(messageDiv, '登录成功！正在跳转...', 'success');
            
            // 根据角色跳转到不同页面
            const role = data.user.role;
            setTimeout(() => {
                if (role === 'teacher') {
                    window.location.href = '/teacher';
                } else {
                    window.location.href = '/dashboard';
                }
            }, 1000);
        } else {
            showMessage(messageDiv, data.message || '登录失败', 'error');
        }
    } catch (error) {
        console.error('登录错误:', error);
        showMessage(messageDiv, '网络错误，请稍后重试', 'error');
    }
}

// 注册处理
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const fullName = document.getElementById('regFullName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const phone = document.getElementById('regPhone')?.value.trim();
    const schoolCode = document.getElementById('regSchoolCode')?.value.trim();
    const messageDiv = document.getElementById('registerMessage');
    
    // 获取角色
    const roleInput = document.querySelector('input[name="role"]:checked');
    const role = roleInput ? roleInput.value : 'student';
    
    if (!username || !password) {
        showMessage(messageDiv, '用户名和密码不能为空', 'error');
        return;
    }
    
    // 构建请求数据
    const requestData = {
        username,
        password,
        role
    };
    
    if (fullName) requestData.full_name = fullName;
    if (email) requestData.email = email;
    if (phone) requestData.phone = phone;
    if (schoolCode) requestData.school_code = schoolCode;
    
    // 学生专用字段
    if (role === 'student') {
        const age = document.getElementById('regAge')?.value;
        const studentLevel = document.getElementById('regStudentLevel')?.value;
        const studentId = document.getElementById('regStudentId')?.value.trim();
        
        if (age) requestData.age = parseInt(age);
        if (studentLevel) requestData.student_level = studentLevel;
        if (studentId) requestData.student_id = studentId;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(messageDiv, '注册成功！正在跳转到登录页...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showMessage(messageDiv, data.message || '注册失败', 'error');
        }
    } catch (error) {
        console.error('注册错误:', error);
        showMessage(messageDiv, '网络错误，请稍后重试', 'error');
    }
}

// 显示消息
function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    // 3秒后自动隐藏错误消息
    if (type === 'error') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 3000);
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查记住我功能
    const savedUsername = localStorage.getItem('rememberedUsername');
    if (savedUsername && document.getElementById('username')) {
        document.getElementById('username').value = savedUsername;
        document.getElementById('remember').checked = true;
    }
    
    // 监听记住我复选框
    const rememberCheckbox = document.getElementById('remember');
    if (rememberCheckbox) {
        rememberCheckbox.addEventListener('change', function() {
            const username = document.getElementById('username').value;
            if (this.checked && username) {
                localStorage.setItem('rememberedUsername', username);
            } else {
                localStorage.removeItem('rememberedUsername');
            }
        });
    }
    
    // 初始化角色选择切换
    const roleInputs = document.querySelectorAll('input[name="role"]');
    roleInputs.forEach(input => {
        input.addEventListener('change', toggleRoleFields);
    });
});

// 切换角色字段显示
function toggleRoleFields() {
    const studentFields = document.getElementById('studentFields');
    if (studentFields) {
        const isStudent = document.querySelector('input[name="role"]:checked')?.value === 'student';
        studentFields.style.display = isStudent ? 'block' : 'none';
    }
}
