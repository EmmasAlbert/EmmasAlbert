/**
 * Basketball Training System - Main JavaScript
 * 篮球训练辅助系统 - 主要JavaScript文件
 */

// API Base URL
const API_BASE = '/api';

/**
 * Make API request
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} - Response promise
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
            }
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '请求失败');
        }
        
        return response;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {number} duration - Duration in ms
 */
function showToast(message, duration = 3000) {
    let toast = document.getElementById('toast');
    
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';
        toast.innerHTML = '<span class="toast-message" id="toastMessage"></span>';
        document.body.appendChild(toast);
    }
    
    const toastMessage = document.getElementById('toastMessage');
    toastMessage.textContent = message;
    toast.style.display = 'block';
    
    setTimeout(() => {
        toast.style.display = 'none';
    }, duration);
}

/**
 * Format date string
 * @param {string} dateStr - ISO date string
 * @returns {string} - Formatted date
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format percentage
 * @param {number} value - Value between 0 and 1
 * @returns {string} - Formatted percentage
 */
function formatPercent(value) {
    if (value === null || value === undefined) return '-';
    return `${(value * 100).toFixed(0)}%`;
}

/**
 * Format angle
 * @param {number} value - Angle in degrees
 * @returns {string} - Formatted angle
 */
function formatAngle(value) {
    if (value === null || value === undefined) return '-';
    return `${value.toFixed(1)}°`;
}

/**
 * Translate trend to Chinese with emoji
 * @param {string} trend - Trend string
 * @returns {string} - Translated trend
 */
function translateTrend(trend) {
    const translations = {
        'improving': '进步 ↑',
        'stable': '稳定 →',
        'declining': '下降 ↓'
    };
    return translations[trend] || trend;
}

/**
 * Check API health
 * @returns {Promise<boolean>} - True if API is healthy
 */
async function checkApiHealth() {
    try {
        const response = await apiRequest('/health');
        const data = await response.json();
        return data.status === 'healthy';
    } catch {
        return false;
    }
}

/**
 * Load settings from API
 * @returns {Promise<object>} - Settings object
 */
async function loadSettings() {
    try {
        const response = await apiRequest('/settings');
        return await response.json();
    } catch {
        return {
            shooting_hand: 'right',
            skip_frames: 0,
            conf_threshold: 0.5,
            show_angles: true
        };
    }
}

/**
 * Save settings to API
 * @param {object} settings - Settings object
 * @returns {Promise<object>} - Updated settings
 */
async function saveSettings(settings) {
    const response = await apiRequest('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    });
    return await response.json();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Check API health
    const isHealthy = await checkApiHealth();
    
    // Update status indicators if present
    const apiStatus = document.getElementById('apiStatus');
    if (apiStatus) {
        apiStatus.textContent = isHealthy ? '正常' : '离线';
        apiStatus.style.background = isHealthy ? 'var(--success-color)' : 'var(--danger-color)';
        apiStatus.style.color = 'white';
    }
    
    const modelStatus = document.getElementById('modelStatus');
    if (modelStatus) {
        modelStatus.textContent = isHealthy ? '已加载' : '未加载';
        modelStatus.style.background = isHealthy ? 'var(--success-color)' : 'var(--warning-color)';
        modelStatus.style.color = 'white';
    }
});
