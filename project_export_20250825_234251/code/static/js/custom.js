// 建筑项目管理系统 - 自定义JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // 初始化所有功能
    initializeTooltips();
    initializeAnimations();
    initializeFormValidation();
    initializeFileUpload();
    initializeNotifications();
    
    // 初始化工具提示
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // 初始化动画效果
    function initializeAnimations() {
        // 为卡片添加淡入动画
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
        
        // 为按钮添加点击效果
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }
    
    // 初始化表单验证
    function initializeFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // 显示第一个错误字段
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                        showNotification('请检查表单中的错误信息', 'warning');
                    }
                }
                form.classList.add('was-validated');
            });
        });
        
        // 实时验证
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    }
    
    // 初始化文件上传功能
    function initializeFileUpload() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    validateFile(file, input);
                }
            });
        });
        
        // 拖拽上传
        const uploadAreas = document.querySelectorAll('.upload-area');
        uploadAreas.forEach(area => {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.add('dragover'), false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
            });
            
            area.addEventListener('drop', handleDrop, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            const fileInput = e.target.closest('.upload-area').querySelector('input[type="file"]');
            
            if (files.length > 0 && fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        }
        
        function validateFile(file, input) {
            const maxSize = 10 * 1024 * 1024; // 10MB
            const allowedTypes = [
                'application/pdf',
                'image/jpeg', 'image/jpg', 'image/png',
                'image/bmp', 'image/tiff'
            ];

            if (file.size > maxSize) {
                showNotification('文件大小不能超过10MB', 'error');
                input.value = '';
                return false;
            }

            if (!allowedTypes.includes(file.type)) {
                showNotification('仅支持PDF、JPG、PNG、BMP、TIFF格式文件', 'error');
                input.value = '';
                return false;
            }

            return true;
        }
    }
    
    // 初始化通知系统
    function initializeNotifications() {
        // 自动隐藏通知
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (alert.classList.contains('alert-auto-dismiss')) {
                setTimeout(() => {
                    fadeOut(alert);
                }, 3000);
            }
        });
    }
    
    // 显示通知
    function showNotification(message, type = 'info', duration = 3000) {
        const alertTypes = {
            'success': 'alert-success',
            'error': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        };
        
        const alert = document.createElement('div');
        alert.className = `alert ${alertTypes[type]} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alert, container.firstChild);
            
            if (duration > 0) {
                setTimeout(() => {
                    fadeOut(alert);
                }, duration);
            }
        }
    }
    
    // 淡出动画
    function fadeOut(element) {
        element.style.transition = 'opacity 0.5s ease';
        element.style.opacity = '0';
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 500);
    }
    
    // 加载状态管理
    function showLoading(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="loading-spinner"></span> 处理中...';
        button.disabled = true;
        button.dataset.originalText = originalText;
    }
    
    function hideLoading(button) {
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
            delete button.dataset.originalText;
        }
    }
    
    // 确认对话框
    function confirmAction(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }
    
    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 格式化日期
    function formatDate(date) {
        return new Date(date).toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // 全局暴露一些有用的函数
    window.ConstructionPM = {
        showNotification,
        showLoading,
        hideLoading,
        confirmAction,
        formatFileSize,
        formatDate
    };
});

// CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
