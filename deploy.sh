#!/bin/bash

# 游戏市场数据爬虫服务器部署脚本
# 适用于 Ubuntu/CentOS 系统

set -e

echo "🚀 开始部署游戏市场数据爬虫服务..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root权限运行此脚本"
    exit 1
fi

# 系统信息
OS=$(grep -oP '(?<=^ID=).+' /etc/os-release | tr -d '"')
echo "📋 检测到操作系统: $OS"

# 更新系统包
echo "📦 更新系统包..."
if [ "$OS" = "ubuntu" ]; then
    apt update && apt upgrade -y
elif [ "$OS" = "centos" ]; then
    yum update -y
fi

# 安装基础依赖
echo "🔧 安装基础依赖..."
if [ "$OS" = "ubuntu" ]; then
    apt install -y python3 python3-pip python3-venv git curl wget unzip
    apt install -y build-essential python3-dev
elif [ "$OS" = "centos" ]; then
    yum install -y python3 python3-pip git curl wget unzip
    yum groupinstall -y "Development Tools"
fi

# 创建应用目录
APP_DIR="/opt/gamemarket_crawler"
echo "📁 创建应用目录: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# 克隆代码（如果是从git部署）
if [ -n "$1" ]; then
    echo "📥 从Git仓库克隆代码..."
    git clone $1 .
else
    echo "📁 使用本地代码部署..."
    # 假设代码已经在当前目录
    cp -r . $APP_DIR/
fi

# 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
echo "📦 安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
playwright install
playwright install firefox
playwright install webkit
playwright install chromium

# 创建数据目录
echo "📊 创建数据目录..."
mkdir -p $APP_DIR/data/{logs,export,resources}

# 创建配置文件
echo "⚙️ 创建配置文件..."
cat > $APP_DIR/config/production.py << EOF
# 生产环境配置
import os

# 数据库配置
DATABASE = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'crawler'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'gamemarket'),
}

# Redis配置
REDIS = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
}

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = '$APP_DIR/data/logs/crawler.log'

# 爬虫配置
CRAWLER_SETTINGS = {
    'DOWNLOAD_DELAY': 2,
    'CONCURRENT_REQUESTS': 8,
    'ROBOTSTXT_OBEY': False,
    'CLOSESPIDER_ITEMCOUNT': 100,
}
EOF

# 创建服务用户
echo "👤 创建服务用户..."
useradd -r -s /bin/false -d $APP_DIR crawler
chown -R crawler:crawler $APP_DIR

# 创建systemd服务
echo "🔧 创建systemd服务..."
cat > /etc/systemd/system/gamemarket-crawler.service << EOF
[Unit]
Description=Game Market Crawler Service
After=network.target

[Service]
Type=simple
User=crawler
Group=crawler
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python run_crawler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建定时任务脚本
echo "⏰ 创建定时任务脚本..."
cat > $APP_DIR/scripts/cron_crawler.sh << 'EOF'
#!/bin/bash

# 游戏市场数据爬虫定时任务脚本
# 每周二更新，根据Steam官方更新时间调整

APP_DIR="/opt/gamemarket_crawler"
LOG_FILE="$APP_DIR/data/logs/cron.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 开始执行定时爬虫任务..." >> $LOG_FILE

# 激活虚拟环境
source $APP_DIR/venv/bin/activate

# 运行Steam热销榜爬虫
echo "[$DATE] 运行Steam热销榜爬虫..." >> $LOG_FILE
cd $APP_DIR
python run_crawler.py steam_top_sellers --output json >> $LOG_FILE 2>&1

# 运行Steam热门榜爬虫
echo "[$DATE] 运行Steam热门榜爬虫..." >> $LOG_FILE
python run_crawler.py steam_popular --output json >> $LOG_FILE 2>&1

echo "[$DATE] 定时爬虫任务完成" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
EOF

chmod +x $APP_DIR/scripts/cron_crawler.sh
chown crawler:crawler $APP_DIR/scripts/cron_crawler.sh

# 创建定时任务配置
echo "⏰ 配置定时任务..."
# Steam通常在周二下午2点（UTC+8）更新，即UTC 6:00
cat > /tmp/crawler_cron << EOF
# 每周二上午6:00 UTC执行（北京时间14:00）
0 6 * * 2 /opt/gamemarket_crawler/scripts/cron_crawler.sh

# 备用时间：每周二上午8:00 UTC执行（北京时间16:00）
0 8 * * 2 /opt/gamemarket_crawler/scripts/cron_crawler.sh
EOF

# 安装定时任务
crontab -u crawler /tmp/crawler_cron
rm /tmp/crawler_cron

# 重新加载systemd
systemctl daemon-reload

# 启用服务
systemctl enable gamemarket-crawler

echo "✅ 部署完成！"
echo ""
echo "📋 服务信息："
echo "   应用目录: $APP_DIR"
echo "   服务用户: crawler"
echo "   日志目录: $APP_DIR/data/logs/"
echo "   数据目录: $APP_DIR/data/export/"
echo ""
echo "🔧 服务管理命令："
echo "   启动服务: systemctl start gamemarket-crawler"
echo "   停止服务: systemctl stop gamemarket-crawler"
echo "   查看状态: systemctl status gamemarket-crawler"
echo "   查看日志: journalctl -u gamemarket-crawler -f"
echo ""
echo "⏰ 定时任务："
echo "   查看定时任务: crontab -u crawler -l"
echo "   编辑定时任务: crontab -u crawler -e"
echo ""
echo "📊 数据文件位置："
echo "   爬虫日志: $APP_DIR/data/logs/crawler.log"
echo "   定时任务日志: $APP_DIR/data/logs/cron.log"
echo "   导出数据: $APP_DIR/data/export/" 