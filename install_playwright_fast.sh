#!/bin/bash

echo "🚀 快速安装Playwright和所有浏览器引擎..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未找到，请先安装pip3"
    exit 1
fi

echo "📦 安装Playwright..."
pip3 install playwright

echo "🔧 安装浏览器引擎..."
playwright install

echo "🔧 安装特定浏览器引擎..."
playwright install firefox
playwright install webkit
playwright install chromium

echo "✅ Playwright安装完成！"
echo "🧪 运行测试: python3 test_playwright_simple.py" 