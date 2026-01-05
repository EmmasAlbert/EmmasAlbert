/**
 * Basketball Training System - History Page JavaScript
 * 篮球训练辅助系统 - 历史记录页面JavaScript
 */

let currentPage = 1;
const perPage = 10;

document.addEventListener('DOMContentLoaded', () => {
    loadProgress();
    loadSessions();
    initExport();
    initModal();
});

/**
 * Load training progress overview
 */
async function loadProgress() {
    try {
        const response = await apiRequest('/progress?sessions=10');
        const data = await response.json();
        
        // Update progress cards
        document.getElementById('sessionsCount').textContent = data.sessions_analyzed || 0;
        document.getElementById('totalShotsAll').textContent = data.total_shots || 0;
        document.getElementById('avgScoreAll').textContent = formatPercent(data.average_form_score);
        document.getElementById('trendIndicator').textContent = translateTrend(data.trend);
        
        // Update trend color
        const trendElement = document.getElementById('trendIndicator');
        if (data.trend === 'improving') {
            trendElement.style.color = 'var(--success-color)';
        } else if (data.trend === 'declining') {
            trendElement.style.color = 'var(--danger-color)';
        }
        
        // Update recommendations
        const recommendationsList = document.getElementById('recommendationsList');
        const recommendations = data.recommendations || [];
        
        if (recommendations.length > 0) {
            recommendationsList.innerHTML = recommendations
                .map(rec => `<p>💡 ${rec}</p>`)
                .join('');
        } else {
            recommendationsList.innerHTML = '<p>继续训练以获取个性化建议</p>';
        }
        
    } catch (error) {
        console.error('Failed to load progress:', error);
        document.getElementById('recommendationsList').innerHTML = 
            '<p>无法加载进度数据</p>';
    }
}

/**
 * Load training sessions list
 */
async function loadSessions(page = 1) {
    currentPage = page;
    const tableBody = document.getElementById('sessionsTableBody');
    
    try {
        const offset = (page - 1) * perPage;
        const response = await apiRequest(`/sessions?limit=${perPage}&offset=${offset}`);
        const data = await response.json();
        
        const sessions = data.sessions || [];
        const total = data.total || 0;
        
        if (sessions.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="loading-text">暂无训练记录</td>
                </tr>
            `;
            return;
        }
        
        tableBody.innerHTML = sessions.map(session => `
            <tr>
                <td>${session.session_id}</td>
                <td>${formatDate(session.date)}</td>
                <td>${session.total_shots}</td>
                <td>${formatPercent(session.form_quality_score)}</td>
                <td>
                    <button class="btn btn-secondary" onclick="viewSession('${session.session_id}')">
                        查看
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Update pagination
        updatePagination(total);
        
    } catch (error) {
        console.error('Failed to load sessions:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="loading-text">加载失败</td>
            </tr>
        `;
    }
}

/**
 * Update pagination controls
 */
function updatePagination(total) {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(total / perPage);
    
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    if (currentPage > 1) {
        html += `<button onclick="loadSessions(${currentPage - 1})">上一页</button>`;
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `<button class="active">${i}</button>`;
        } else {
            html += `<button onclick="loadSessions(${i})">${i}</button>`;
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        html += `<button onclick="loadSessions(${currentPage + 1})">下一页</button>`;
    }
    
    pagination.innerHTML = html;
}

/**
 * View session details
 */
async function viewSession(sessionId) {
    const modal = document.getElementById('sessionModal');
    const sessionDetail = document.getElementById('sessionDetail');
    
    sessionDetail.innerHTML = '<p>加载中...</p>';
    modal.style.display = 'flex';
    
    try {
        const response = await apiRequest(`/sessions/${sessionId}`);
        const session = await response.json();
        
        const stats = session.statistics || {};
        
        let html = `
            <div class="session-detail">
                <p><strong>训练ID:</strong> ${session.session_id}</p>
                <p><strong>日期:</strong> ${formatDate(session.date)}</p>
                <hr>
                <h4>统计数据</h4>
                <p><strong>投篮次数:</strong> ${stats.total_shots}</p>
                <p><strong>姿势评分:</strong> ${formatPercent(stats.form_quality_score)}</p>
                <p><strong>平均肘部角度:</strong> ${formatAngle(stats.average_elbow_angle)}</p>
                <p><strong>平均膝盖角度:</strong> ${formatAngle(stats.average_knee_angle)}</p>
            </div>
        `;
        
        sessionDetail.innerHTML = html;
        
    } catch (error) {
        sessionDetail.innerHTML = '<p>加载失败</p>';
    }
}

/**
 * Initialize export functionality
 */
function initExport() {
    const exportBtn = document.getElementById('exportBtn');
    const exportFormat = document.getElementById('exportFormat');
    
    exportBtn.addEventListener('click', () => {
        const format = exportFormat.value;
        window.location.href = `/api/export?format=${format}`;
    });
}

/**
 * Initialize modal
 */
function initModal() {
    const modal = document.getElementById('sessionModal');
    const closeBtn = document.getElementById('closeModal');
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}
