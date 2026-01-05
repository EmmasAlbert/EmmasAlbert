/**
 * Basketball Training System - Settings Page JavaScript
 * 篮球训练辅助系统 - 设置页面JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    loadCurrentSettings();
    initSettingsForm();
    initRangeSlider();
});

/**
 * Load current settings from API
 */
async function loadCurrentSettings() {
    try {
        const settings = await loadSettings();
        
        // Apply settings to form
        document.getElementById('defaultHand').value = settings.shooting_hand || 'right';
        document.getElementById('defaultSkipFrames').value = settings.skip_frames || 0;
        document.getElementById('confThreshold').value = settings.conf_threshold || 0.5;
        document.getElementById('confThresholdValue').textContent = settings.conf_threshold || 0.5;
        document.getElementById('showAngles').checked = settings.show_angles !== false;
        
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

/**
 * Initialize settings form
 */
function initSettingsForm() {
    const form = document.getElementById('settingsForm');
    const resetBtn = document.getElementById('resetBtn');
    
    // Form submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const settings = {
            shooting_hand: document.getElementById('defaultHand').value,
            skip_frames: parseInt(document.getElementById('defaultSkipFrames').value),
            conf_threshold: parseFloat(document.getElementById('confThreshold').value),
            show_angles: document.getElementById('showAngles').checked
        };
        
        try {
            await saveSettings(settings);
            showToast('设置已保存');
        } catch (error) {
            showToast('保存失败: ' + error.message);
        }
    });
    
    // Reset button
    resetBtn.addEventListener('click', () => {
        // Reset to defaults
        document.getElementById('defaultHand').value = 'right';
        document.getElementById('defaultSkipFrames').value = 0;
        document.getElementById('confThreshold').value = 0.5;
        document.getElementById('confThresholdValue').textContent = '0.5';
        document.getElementById('showAngles').checked = true;
        
        // Reset ideal ranges
        document.getElementById('elbowMin').value = 85;
        document.getElementById('elbowMax').value = 105;
        document.getElementById('shoulderMin').value = 80;
        document.getElementById('shoulderMax').value = 120;
        document.getElementById('kneeMin').value = 140;
        document.getElementById('kneeMax').value = 170;
        
        showToast('设置已重置为默认值');
    });
}

/**
 * Initialize range slider
 */
function initRangeSlider() {
    const confThreshold = document.getElementById('confThreshold');
    const confThresholdValue = document.getElementById('confThresholdValue');
    
    confThreshold.addEventListener('input', () => {
        confThresholdValue.textContent = confThreshold.value;
    });
}
