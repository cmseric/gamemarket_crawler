# 🌐 GameMarket Crawler Web Dashboard

一个美观、现代化的Steam游戏市场数据可视化平台，基于Flask构建，提供实时数据展示、图表分析和管理功能。

## ✨ 功能特性

### 📊 数据概览
- **实时统计卡片**: 总游戏数、独立游戏数、平均价格、数据表数量
- **排行榜统计**: 热销榜与热门榜数据分布
- **数据更新状态**: 最后更新时间、数据新鲜度、完整性指标
- **快速访问导航**: 一键跳转到各个功能模块
- **最新游戏预览**: 动态加载最新爬取的游戏数据

### 🏆 排行榜展示
- **Steam热销榜**: 按销量排序的付费游戏排行
- **Steam热门榜**: 按人气排序的游戏排行
- **游戏卡片**: 精美的卡片式布局，展示游戏详细信息
- **价格信息**: 支持原价、折扣价、折扣百分比显示
- **游戏分类**: 自动标签化游戏类型
- **快速链接**: 直接跳转到Steam商店页面

### 📈 数据分析
- **价格分布分析**: 饼图展示不同价格区间的游戏分布
- **游戏类型分布**: 环形图显示热门游戏类型
- **折扣分析**: 柱状图分析折扣力度分布
- **数据采集趋势**: 线图展示数据采集的时间趋势
- **实时图表**: 支持数据自动刷新和缓存机制

### 🗄️ 数据表管理
- **分表列表**: 展示所有MySQL分表信息
- **表结构查看**: 详细的表字段信息和索引情况
- **数据预览**: 快速预览表中的数据内容
- **统计信息**: 表记录数、存储大小等统计指标
- **数据导出**: 支持CSV格式数据导出

### 🛠️ 系统特性
- **响应式设计**: 完美适配桌面端、平板和手机
- **现代化UI**: 基于Bootstrap 5的现代化界面
- **实时缓存**: Redis缓存提升数据加载速度
- **错误处理**: 完善的错误提示和异常处理
- **键盘快捷键**: 支持Ctrl+R刷新、Ctrl+/帮助等
- **自动刷新**: 可配置的自动数据刷新机制

## 🚀 快速开始

### 1. 环境准备

确保已安装以下依赖：
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- MongoDB 4.4+ (可选)

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 3. 环境配置

创建配置文件或设置环境变量：

```bash
# MySQL配置
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=gamemarket

# Redis配置
export REDIS_URL=redis://localhost:6379

# MongoDB配置 (可选)
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DATABASE=gamemarket

# Flask配置
export FLASK_ENV=development
export FLASK_DEBUG=true
```

### 4. 启动Web应用

```bash
# 开发模式启动
python run_web.py --debug

# 生产模式启动
python run_web.py --env production --host 0.0.0.0 --port 8080

# 使用Gunicorn部署
gunicorn -w 4 -b 0.0.0.0:8080 "web.app:create_app('production')"
```

### 5. 访问应用

打开浏览器访问：
- 开发模式: http://localhost:8080
- 生产模式: http://your-server:8080

## 🐳 Docker部署

### 1. 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看Web应用日志
docker-compose logs -f web
```

### 2. 服务访问地址

- **Web Dashboard**: http://localhost:80
- **Web应用直接访问**: http://localhost:8080
- **数据文件下载**: http://localhost/data/
- **MySQL**: localhost:3306
- **Redis**: localhost:6379
- **MongoDB**: localhost:27017

## 📱 界面预览

### 首页概览
![Dashboard](preview/dashboard.png)
- 数据统计卡片
- 排行榜快速预览
- 系统状态监控

### 排行榜页面
![Rankings](preview/rankings.png)
- 游戏卡片布局
- 价格和折扣信息
- 游戏分类标签

### 数据分析
![Analytics](preview/analytics.png)
- 多维度图表分析
- 实时数据更新
- 交互式图表

### 数据表管理
![Tables](preview/tables.png)
- 分表列表管理
- 表结构查看
- 数据预览和导出

## 🔧 配置选项

### Flask应用配置

```python
# web/config.py
class Config:
    # 基础配置
    SECRET_KEY = 'your-secret-key'
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 8080
    
    # 数据库配置
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'password'
    MYSQL_DATABASE = 'gamemarket'
    
    # 缓存配置
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
```

### 缓存策略

| 数据类型 | 缓存时间 | 缓存键 |
|---------|---------|--------|
| 统计摘要 | 5分钟 | `dashboard_summary` |
| 排行榜数据 | 3分钟 | `rankings_{type}_{limit}` |
| 图表数据 | 10分钟 | `chart_{type}` |
| 最新游戏 | 3分钟 | `latest_games_{limit}_{type}` |

## 🎯 API接口

### 统计接口
```
GET /api/stats/summary
返回: 系统统计摘要信息
```

### 游戏数据接口
```
GET /api/games/latest?limit=20&rank_type=topsellers
返回: 最新游戏数据列表
```

### 图表数据接口
```
GET /api/charts/price-distribution
GET /api/charts/genre-distribution  
GET /api/charts/discount-analysis
GET /api/charts/trending?days=7
返回: 图表数据
```

### 缓存管理接口
```
GET /api/cache/clear?pattern=chart_*
返回: 缓存清除结果
```

## 🛠️ 开发指南

### 项目结构

```
web/
├── __init__.py              # 包初始化
├── app.py                   # Flask应用主文件
├── config.py                # 配置文件
├── utils/
│   └── database.py          # 数据库工具类
├── templates/               # HTML模板
│   ├── base.html           # 基础模板
│   ├── index.html          # 首页
│   ├── rankings.html       # 排行榜
│   ├── analytics.html      # 数据分析
│   └── tables.html         # 数据表管理
└── static/                 # 静态文件
    ├── css/
    │   └── style.css       # 自定义样式
    └── js/
        └── main.js         # 主要JavaScript
```

### 添加新功能

1. **新增页面路由**
```python
@app.route('/new-page')
def new_page():
    return render_template('new_page.html')
```

2. **新增API接口**
```python
@app.route('/api/new-data')
def api_new_data():
    try:
        data = get_new_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

3. **新增数据查询**
```python
class NewDataQuery:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_new_data(self):
        # 实现数据查询逻辑
        pass
```

### 样式定制

修改 `web/static/css/style.css` 来定制界面样式：

```css
/* 自定义主题色 */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    /* 更多变量... */
}

/* 自定义组件样式 */
.custom-card {
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,.08);
}
```

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
```bash
# 检查MySQL服务状态
systemctl status mysql

# 检查连接参数
mysql -h localhost -u root -p
```

2. **Redis连接失败**
```bash
# 检查Redis服务
systemctl status redis

# 测试连接
redis-cli ping
```

3. **Web应用启动失败**
```bash
# 检查依赖
pip list | grep flask

# 查看错误日志
python run_web.py --debug
```

4. **数据不显示**
```bash
# 检查数据表是否存在
mysql -u root -p -e "SHOW TABLES FROM gamemarket;"

# 检查爬虫数据
python run_crawler.py test --output json
```

### 性能优化

1. **启用缓存**
   - 确保Redis服务正常运行
   - 调整缓存过期时间
   - 使用缓存预热

2. **数据库优化**
   - 添加适当的索引
   - 优化查询语句
   - 使用连接池

3. **前端优化**
   - 启用Gzip压缩
   - 使用CDN加速
   - 优化图片资源

## 📞 技术支持

如果遇到问题：

1. 查看应用日志: `data/logs/web_app.log`
2. 检查数据库连接状态
3. 验证配置文件正确性
4. 参考故障排除指南

更多帮助请参考项目主文档或提交Issue。

---

**GameMarket Crawler Web Dashboard** - 让数据可视化更简单！ 🚀 