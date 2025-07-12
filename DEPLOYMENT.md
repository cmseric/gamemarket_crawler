# 🚀 游戏市场数据爬虫部署指南

## 📋 部署方案

本项目提供两种部署方案：

1. **传统部署** - 直接在服务器上安装
2. **Docker部署** - 使用容器化部署（推荐）

## 🐳 Docker部署（推荐）

### 前置要求
- Docker
- Docker Compose

### 快速部署
```bash
# 1. 克隆项目
git clone <your-repo-url>
cd gamemarket_crawler

# 2. 启动服务
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f crawler
```

### 服务访问
- **数据文件**: http://your-server/data/
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

## 🖥️ 传统部署

### 前置要求
- Ubuntu 20.04+ 或 CentOS 8+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### 自动部署
```bash
# 1. 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/deploy.sh

# 2. 执行部署
sudo bash deploy.sh

# 3. 启动服务
sudo systemctl start gamemarket-crawler

# 4. 安装定时任务
sudo bash scripts/manage_cron.sh install
```

### 手动部署
```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# 2. 创建应用目录
sudo mkdir -p /opt/gamemarket_crawler
sudo chown $USER:$USER /opt/gamemarket_crawler

# 3. 复制项目文件
cp -r . /opt/gamemarket_crawler/

# 4. 创建虚拟环境
cd /opt/gamemarket_crawler
python3 -m venv venv
source venv/bin/activate

# 5. 安装Python依赖
pip install -r requirements.txt

# 6. 安装Playwright
playwright install
playwright install firefox webkit chromium

# 7. 创建数据目录
mkdir -p data/{logs,export,resources}
```

## ⏰ 定时任务配置

### Steam更新时间
Steam通常在**每周二下午**更新数据：
- **北京时间**: 14:00-16:00
- **UTC时间**: 06:00-08:00

### 安装定时任务
```bash
# 安装定时任务
sudo bash scripts/manage_cron.sh install

# 查看定时任务状态
sudo bash scripts/manage_cron.sh status

# 测试爬虫
sudo bash scripts/manage_cron.sh test

# 查看日志
sudo bash scripts/manage_cron.sh logs
```

### 自定义执行时间
```bash
# 更新定时任务时间
sudo bash scripts/manage_cron.sh update
```

## 📊 数据存储

### 文件结构
```
/opt/gamemarket_crawler/
├── data/
│   ├── logs/          # 日志文件
│   ├── export/        # 导出数据
│   └── resources/     # 截图等资源
├── config/            # 配置文件
└── scripts/           # 管理脚本
```

### 数据格式
- **JSON**: 结构化数据，易于处理
- **CSV**: 表格格式，适合Excel
- **XML**: 标记语言格式

## 🔧 服务管理

### 传统部署
```bash
# 启动服务
sudo systemctl start gamemarket-crawler

# 停止服务
sudo systemctl stop gamemarket-crawler

# 重启服务
sudo systemctl restart gamemarket-crawler

# 查看状态
sudo systemctl status gamemarket-crawler

# 查看日志
sudo journalctl -u gamemarket-crawler -f
```

### Docker部署
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec crawler bash
```

## 📈 监控和维护

### 日志监控
```bash
# 查看爬虫日志
tail -f /opt/gamemarket_crawler/data/logs/crawler.log

# 查看定时任务日志
tail -f /opt/gamemarket_crawler/data/logs/cron.log

# 查看系统日志
journalctl -u gamemarket-crawler -f
```

### 数据备份
```bash
# 备份数据目录
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/gamemarket_crawler/data/

# 备份数据库
mysqldump -u crawler -p gamemarket > backup_$(date +%Y%m%d).sql
```

### 性能优化
1. **调整并发数**: 修改 `settings.py` 中的 `CONCURRENT_REQUESTS`
2. **调整延迟**: 修改 `DOWNLOAD_DELAY` 避免被封
3. **使用代理**: 配置代理池避免IP限制
4. **数据库优化**: 定期清理旧数据

## 🛠️ 故障排除

### 常见问题

1. **爬虫无法启动**
   ```bash
   # 检查Python环境
   python3 --version
   pip list | grep scrapy
   
   # 检查依赖
   pip install -r requirements.txt
   ```

2. **定时任务不执行**
   ```bash
   # 检查cron服务
   sudo systemctl status cron
   
   # 检查定时任务
   sudo crontab -u crawler -l
   
   # 手动测试
   sudo bash scripts/manage_cron.sh test
   ```

3. **数据库连接失败**
   ```bash
   # 检查MySQL服务
   sudo systemctl status mysql
   
   # 检查连接
   mysql -u crawler -p -h localhost
   ```

4. **Docker容器启动失败**
   ```bash
   # 查看容器日志
   docker-compose logs crawler
   
   # 重新构建镜像
   docker-compose build --no-cache
   ```

### 日志分析
```bash
# 查看错误日志
grep -i error /opt/gamemarket_crawler/data/logs/crawler.log

# 查看最近的爬虫活动
tail -50 /opt/gamemarket_crawler/data/logs/crawler.log

# 查看定时任务执行情况
grep "开始执行" /opt/gamemarket_crawler/data/logs/cron.log
```

## 🔐 安全建议

1. **防火墙配置**
   ```bash
   # 只开放必要端口
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP (如果使用Web界面)
   sudo ufw enable
   ```

2. **数据库安全**
   ```bash
   # 修改默认密码
   mysql -u root -p
   ALTER USER 'crawler'@'localhost' IDENTIFIED BY 'strong_password';
   ```

3. **文件权限**
   ```bash
   # 设置正确的文件权限
   sudo chown -R crawler:crawler /opt/gamemarket_crawler
   sudo chmod 755 /opt/gamemarket_crawler/scripts/
   ```

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 检查系统资源使用情况
3. 确认网络连接正常
4. 验证配置文件正确

更多帮助请参考项目文档或提交Issue。 