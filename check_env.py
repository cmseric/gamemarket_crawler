#!/usr/bin/env python3
"""
环境状态检查脚本
"""

import sys
import subprocess
from pathlib import Path

def main():
    print("🔍 检查gamemarket_crawler项目环境状态")
    print("=" * 50)
    
    # 检查Python环境
    python_path = sys.executable
    print(f"🐍 Python路径: {python_path}")
    
    # 检查是否在正确的环境中
    if "gamemarket_crawler" in python_path:
        print("✅ 环境状态: 正确 (gamemarket_crawler)")
    else:
        print("❌ 环境状态: 错误 (不在gamemarket_crawler环境中)")
        print("💡 请运行: conda activate gamemarket_crawler")
        return
    
    # 检查关键包
    key_packages = [
        "scrapy", "playwright", "pandas", "pymongo", 
        "redis", "requests", "loguru"
    ]
    
    # 检查playwright浏览器
    try:
        import subprocess
        result = subprocess.run(['playwright', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ playwright浏览器已安装")
        else:
            print("❌ playwright浏览器未安装")
    except Exception:
        print("❌ playwright浏览器检查失败")
    
    print("\n📦 检查关键包:")
    for package in key_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (未安装)")
    
    # 检查项目文件
    project_files = [
        "scraper/spiders/steam_spider.py",
        "run_crawler.py", 
        "requirements.txt",
        "environment.yml"
    ]
    
    print("\n📁 检查项目文件:")
    for file_path in project_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (缺失)")
    
    print("\n🎯 环境设置完成！")
    print("💡 使用以下命令运行爬虫:")
    print("   python run_crawler.py")

if __name__ == "__main__":
    main() 