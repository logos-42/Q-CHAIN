/**
 * 量子区块链前端主JavaScript文件
 */

// 全局变量
const API_BASE_URL = '';

// 工具函数
const utils = {
    /**
     * 获取短哈希显示
     * @param {string} hash 完整哈希值
     * @param {number} length 截取长度
     * @returns {string} 格式化后的哈希字符串
     */
    shortHash: function(hash, length = 10) {
        if (!hash) return '无哈希值';
        return hash.substring(0, length) + '...';
    },
    
    /**
     * 格式化时间戳为本地时间字符串
     * @param {number} timestamp Unix时间戳（秒）
     * @returns {string} 格式化的日期时间字符串
     */
    formatTimestamp: function(timestamp) {
        if (!timestamp) return '无时间戳';
        return new Date(timestamp * 1000).toLocaleString();
    },
    
    /**
     * 复制文本到剪贴板
     * @param {string} text 要复制的文本
     */
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(function() {
            // 复制成功
            showToast('复制成功!', 'success');
        }, function() {
            // 复制失败
            showToast('复制失败，请手动复制', 'danger');
        });
    }
};

/**
 * 显示提示消息
 * @param {string} message 消息内容
 * @param {string} type 消息类型 (success, info, warning, danger)
 * @param {number} duration 持续时间（毫秒）
 */
function showToast(message, type = 'info', duration = 3000) {
    // 创建toast元素
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // 设置toast内容
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // 添加到文档
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        container.appendChild(toastEl);
    } else {
        toastContainer.appendChild(toastEl);
    }
    
    // 初始化和显示toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: duration
    });
    toast.show();
    
    // 自动移除
    setTimeout(() => {
        toastEl.remove();
    }, duration + 500);
}

/**
 * 页面加载完成后初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    // 为哈希值添加点击复制功能
    document.querySelectorAll('.hash-value').forEach(el => {
        if (el.getAttribute('data-copyable') !== 'false') {
            el.style.cursor = 'pointer';
            el.setAttribute('title', '点击复制');
            el.addEventListener('click', function() {
                utils.copyToClipboard(this.textContent.trim());
            });
        }
    });
    
    // 添加回到顶部按钮
    if (document.body.scrollHeight > window.innerHeight * 1.5) {
        const backToTopBtn = document.createElement('button');
        backToTopBtn.className = 'btn btn-primary btn-sm position-fixed bottom-0 end-0 m-3 rounded-circle';
        backToTopBtn.innerHTML = '↑';
        backToTopBtn.style.width = '40px';
        backToTopBtn.style.height = '40px';
        backToTopBtn.style.display = 'none';
        backToTopBtn.setAttribute('title', '回到顶部');
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
        
        document.body.appendChild(backToTopBtn);
        
        // 监听滚动显示/隐藏按钮
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
    }
}); 