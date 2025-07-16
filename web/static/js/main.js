/**
 * GameMarket Crawler Dashboard - 主要JavaScript文件
 */

// 全局变量
window.dashboard = {
  config: {
    refreshInterval: 300000, // 5分钟自动刷新
    apiEndpoints: {
      stats: '/api/stats/summary',
      games: '/api/games/latest',
      cache: '/api/cache/clear'
    }
  },
  charts: {},
  timers: {}
};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
  initializeDashboard();
});

/**
 * 初始化仪表板
 */
function initializeDashboard() {
  // 初始化工具提示
  initTooltips();

  // 初始化响应式表格
  initResponsiveTables();

  // 设置自动刷新
  setupAutoRefresh();

  // 初始化键盘快捷键
  setupKeyboardShortcuts();

  // 初始化页面动画
  initPageAnimations();

  console.log('Dashboard initialized successfully');
}

/**
 * 初始化Bootstrap工具提示
 */
function initTooltips() {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * 初始化响应式表格
 */
function initResponsiveTables() {
  const tables = document.querySelectorAll('.table-responsive');
  tables.forEach(table => {
    if (table.scrollWidth > table.clientWidth) {
      table.classList.add('shadow-sm');
    }
  });
}

/**
 * 设置自动刷新
 */
function setupAutoRefresh() {
  // 清除现有的定时器
  if (window.dashboard.timers.autoRefresh) {
    clearInterval(window.dashboard.timers.autoRefresh);
  }

  // 设置新的定时器
  window.dashboard.timers.autoRefresh = setInterval(() => {
    if (typeof updatePageData === 'function') {
      updatePageData();
    }
  }, window.dashboard.config.refreshInterval);
}

/**
 * 设置键盘快捷键
 */
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', function (event) {
    // Ctrl/Cmd + R: 刷新数据
    if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
      event.preventDefault();
      if (typeof updatePageData === 'function') {
        updatePageData();
      } else {
        location.reload();
      }
    }

    // Ctrl/Cmd + /: 显示快捷键帮助
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
      event.preventDefault();
      showKeyboardHelp();
    }

    // Escape: 关闭模态框
    if (event.key === 'Escape') {
      const modals = document.querySelectorAll('.modal.show');
      modals.forEach(modal => {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
          bsModal.hide();
        }
      });
    }
  });
}

/**
 * 初始化页面动画
 */
function initPageAnimations() {
  // 为卡片添加进入动画
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
    card.classList.add('fade-in');
  });

  // 为按钮添加hover效果
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', function () {
      this.style.transform = 'translateY(-2px)';
    });

    button.addEventListener('mouseleave', function () {
      this.style.transform = 'translateY(0)';
    });
  });
}

/**
 * 显示键盘快捷键帮助
 */
function showKeyboardHelp() {
  const helpContent = `
        <div class="row">
            <div class="col-12">
                <h6 class="text-primary mb-3">
                    <i class="fas fa-keyboard me-2"></i>键盘快捷键
                </h6>
                <table class="table table-sm">
                    <tbody>
                        <tr>
                            <td><kbd>Ctrl</kbd> + <kbd>R</kbd></td>
                            <td>刷新页面数据</td>
                        </tr>
                        <tr>
                            <td><kbd>Ctrl</kbd> + <kbd>/</kbd></td>
                            <td>显示快捷键帮助</td>
                        </tr>
                        <tr>
                            <td><kbd>Esc</kbd></td>
                            <td>关闭模态框</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

  showModal('键盘快捷键', helpContent);
}

/**
 * 显示通用模态框
 */
function showModal(title, content, size = 'modal-md') {
  // 检查是否已存在通用模态框
  let modal = document.getElementById('genericModal');
  if (!modal) {
    // 创建模态框HTML
    const modalHTML = `
            <div class="modal fade" id="genericModal" tabindex="-1">
                <div class="modal-dialog ${size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="genericModalTitle"></h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="genericModalBody"></div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

    // 添加到页面
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    modal = document.getElementById('genericModal');
  }

  // 设置内容
  document.getElementById('genericModalTitle').textContent = title;
  document.getElementById('genericModalBody').innerHTML = content;

  // 显示模态框
  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();
}

/**
 * API请求工具函数
 */
const API = {
  /**
   * 发送GET请求
   */
  get: async function (url, options = {}) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API GET request failed:', error);
      throw error;
    }
  },

  /**
   * 发送POST请求
   */
  post: async function (url, data = {}, options = {}) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        body: JSON.stringify(data),
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API POST request failed:', error);
      throw error;
    }
  }
};

/**
 * 数据格式化工具
 */
const DataFormatter = {
  /**
   * 格式化数字
   */
  formatNumber: function (num, decimals = 0) {
    if (num === null || num === undefined) return 'N/A';
    return new Intl.NumberFormat('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num);
  },

  /**
   * 格式化货币
   */
  formatCurrency: function (amount, currency = 'CNY') {
    if (amount === null || amount === undefined) return 'N/A';
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2
    }).format(amount);
  },

  /**
   * 格式化日期
   */
  formatDate: function (date, options = {}) {
    if (!date) return 'N/A';
    const defaultOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Intl.DateTimeFormat('zh-CN', { ...defaultOptions, ...options }).format(new Date(date));
  },

  /**
   * 格式化文件大小
   */
  formatFileSize: function (bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
};

/**
 * 图表工具函数
 */
const ChartUtils = {
  /**
   * 默认图表颜色
   */
  colors: [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ],

  /**
   * 获取响应式图表选项
   */
  getResponsiveOptions: function (title) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: title,
          font: {
            size: 16,
            weight: 'bold'
          }
        },
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    };
  },

  /**
   * 销毁图表
   */
  destroyChart: function (chartId) {
    if (window.dashboard.charts[chartId]) {
      window.dashboard.charts[chartId].destroy();
      delete window.dashboard.charts[chartId];
    }
  }
};

/**
 * 本地存储工具
 */
const Storage = {
  /**
   * 设置本地存储
   */
  set: function (key, value, expiry = null) {
    const item = {
      value: value,
      timestamp: Date.now(),
      expiry: expiry
    };
    localStorage.setItem(key, JSON.stringify(item));
  },

  /**
   * 获取本地存储
   */
  get: function (key) {
    const item = localStorage.getItem(key);
    if (!item) return null;

    try {
      const parsed = JSON.parse(item);

      // 检查是否过期
      if (parsed.expiry && Date.now() > parsed.expiry) {
        localStorage.removeItem(key);
        return null;
      }

      return parsed.value;
    } catch (error) {
      console.error('Error parsing localStorage item:', error);
      return null;
    }
  },

  /**
   * 删除本地存储
   */
  remove: function (key) {
    localStorage.removeItem(key);
  },

  /**
   * 清空本地存储
   */
  clear: function () {
    localStorage.clear();
  }
};

/**
 * 错误处理工具
 */
const ErrorHandler = {
  /**
   * 处理API错误
   */
  handleApiError: function (error, userMessage = '操作失败，请稍后重试') {
    console.error('API Error:', error);

    let message = userMessage;
    if (error.message) {
      message += `: ${error.message}`;
    }

    showToast(message, 'error');
  },

  /**
   * 处理网络错误
   */
  handleNetworkError: function (error) {
    console.error('Network Error:', error);
    showToast('网络连接失败，请检查网络状态', 'error');
  },

  /**
   * 处理图表错误
   */
  handleChartError: function (chartId, error) {
    console.error(`Chart Error (${chartId}):`, error);
    const container = document.getElementById(chartId + 'Loading');
    if (container) {
      container.innerHTML = `
                <div class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <p>图表加载失败</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">
                        <i class="fas fa-sync me-1"></i>重新加载
                    </button>
                </div>
            `;
    }
  }
};

/**
 * 页面离开前清理
 */
window.addEventListener('beforeunload', function () {
  // 清理定时器
  Object.values(window.dashboard.timers).forEach(timer => {
    if (timer) clearInterval(timer);
  });

  // 销毁图表
  Object.values(window.dashboard.charts).forEach(chart => {
    if (chart && typeof chart.destroy === 'function') {
      chart.destroy();
    }
  });
});

/**
 * 导出全局函数供模板使用
 */
window.showModal = showModal;
window.API = API;
window.DataFormatter = DataFormatter;
window.ChartUtils = ChartUtils;
window.Storage = Storage;
window.ErrorHandler = ErrorHandler; 