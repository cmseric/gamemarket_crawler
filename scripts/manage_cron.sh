#!/bin/bash

# 定时任务管理脚本
# 用于管理Steam数据爬虫的定时任务

APP_DIR="/opt/gamemarket_crawler"
CRON_LOG="$APP_DIR/data/logs/cron.log"

# Steam更新时间参考（UTC时间）
# Steam通常在周二下午更新，北京时间14:00-16:00
# 对应UTC时间：06:00-08:00

show_help() {
    echo "🎮 Steam数据爬虫定时任务管理"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  install    安装定时任务"
    echo "  uninstall  卸载定时任务"
    echo "  status     查看定时任务状态"
    echo "  test       测试爬虫运行"
    echo "  logs       查看定时任务日志"
    echo "  update     更新定时任务时间"
    echo ""
    echo "示例:"
    echo "  $0 install    # 安装定时任务"
    echo "  $0 status     # 查看状态"
    echo "  $0 test       # 测试运行"
}

install_cron() {
    echo "⏰ 安装定时任务..."
    
    # 创建定时任务脚本
    cat > $APP_DIR/scripts/cron_crawler.sh << 'EOF'
#!/bin/bash

# Steam数据爬虫定时任务
# 每周二执行，根据Steam官方更新时间调整

APP_DIR="/opt/gamemarket_crawler"
LOG_FILE="$APP_DIR/data/logs/cron.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 🚀 开始执行Steam数据爬虫定时任务..." >> $LOG_FILE

# 激活虚拟环境
source $APP_DIR/venv/bin/activate

# 运行Steam热销榜爬虫
echo "[$DATE] 📊 运行Steam热销榜爬虫..." >> $LOG_FILE
cd $APP_DIR
python run_crawler.py steam_top_sellers --output json >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "[$DATE] ✅ Steam热销榜爬虫执行成功" >> $LOG_FILE
else
    echo "[$DATE] ❌ Steam热销榜爬虫执行失败" >> $LOG_FILE
fi

# 运行Steam热门榜爬虫
echo "[$DATE] 📊 运行Steam热门榜爬虫..." >> $LOG_FILE
python run_crawler.py steam_popular --output json >> $LOG_FILE 2>&1
if [ $? -eq 0 ]; then
    echo "[$DATE] ✅ Steam热门榜爬虫执行成功" >> $LOG_FILE
else
    echo "[$DATE] ❌ Steam热门榜爬虫执行失败" >> $LOG_FILE
fi

echo "[$DATE] 🎉 定时爬虫任务完成" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
EOF

    chmod +x $APP_DIR/scripts/cron_crawler.sh
    chown crawler:crawler $APP_DIR/scripts/cron_crawler.sh

    # 创建定时任务配置
    cat > /tmp/crawler_cron << EOF
# Steam数据爬虫定时任务
# 每周二执行，根据Steam官方更新时间调整

# 主要执行时间：每周二上午6:00 UTC（北京时间14:00）
0 6 * * 2 /opt/gamemarket_crawler/scripts/cron_crawler.sh

# 备用执行时间：每周二上午8:00 UTC（北京时间16:00）
0 8 * * 2 /opt/gamemarket_crawler/scripts/cron_crawler.sh

# 测试时间：每天凌晨2:00 UTC（北京时间10:00）- 仅用于测试
# 0 2 * * * /opt/gamemarket_crawler/scripts/cron_crawler.sh
EOF

    # 安装定时任务
    crontab -u crawler /tmp/crawler_cron
    rm /tmp/crawler_cron

    echo "✅ 定时任务安装完成！"
    echo "📅 执行时间：每周二 06:00 UTC 和 08:00 UTC"
    echo "📊 日志文件：$LOG_FILE"
}

uninstall_cron() {
    echo "🗑️ 卸载定时任务..."
    crontab -u crawler -r
    echo "✅ 定时任务已卸载"
}

status_cron() {
    echo "📋 定时任务状态："
    echo ""
    crontab -u crawler -l
    echo ""
    echo "📊 最近执行日志："
    if [ -f "$CRON_LOG" ]; then
        tail -20 "$CRON_LOG"
    else
        echo "暂无日志文件"
    fi
}

test_crawler() {
    echo "🧪 测试爬虫运行..."
    
    # 激活虚拟环境
    source $APP_DIR/venv/bin/activate
    
    # 测试运行
    cd $APP_DIR
    python run_crawler.py test --output json
    
    echo "✅ 测试完成"
}

show_logs() {
    echo "📊 查看定时任务日志..."
    if [ -f "$CRON_LOG" ]; then
        tail -f "$CRON_LOG"
    else
        echo "暂无日志文件"
    fi
}

update_cron() {
    echo "🕐 更新定时任务时间..."
    echo ""
    echo "请选择新的执行时间："
    echo "1. 每周二 06:00 UTC（北京时间14:00）- 推荐"
    echo "2. 每周二 08:00 UTC（北京时间16:00）"
    echo "3. 每周二 10:00 UTC（北京时间18:00）"
    echo "4. 自定义时间"
    echo ""
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            TIME1="0 6 * * 2"
            TIME2="0 8 * * 2"
            ;;
        2)
            TIME1="0 8 * * 2"
            TIME2="0 10 * * 2"
            ;;
        3)
            TIME1="0 10 * * 2"
            TIME2="0 12 * * 2"
            ;;
        4)
            echo "请输入自定义时间（cron格式，如：0 6 * * 2）："
            read TIME1
            TIME2="0 8 * * 2"
            ;;
        *)
            echo "❌ 无效选择"
            exit 1
            ;;
    esac
    
    # 更新定时任务
    cat > /tmp/crawler_cron << EOF
# Steam数据爬虫定时任务
# 每周二执行，根据Steam官方更新时间调整

# 主要执行时间
$TIME1 /opt/gamemarket_crawler/scripts/cron_crawler.sh

# 备用执行时间
$TIME2 /opt/gamemarket_crawler/scripts/cron_crawler.sh
EOF

    crontab -u crawler /tmp/crawler_cron
    rm /tmp/crawler_cron
    
    echo "✅ 定时任务时间已更新"
}

# 主逻辑
case "$1" in
    install)
        install_cron
        ;;
    uninstall)
        uninstall_cron
        ;;
    status)
        status_cron
        ;;
    test)
        test_crawler
        ;;
    logs)
        show_logs
        ;;
    update)
        update_cron
        ;;
    *)
        show_help
        ;;
esac 