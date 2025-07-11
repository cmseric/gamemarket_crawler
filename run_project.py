#!/usr/bin/env python3
"""
游戏市场爬虫项目启动脚本
自动激活conda环境并运行爬虫
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """检查当前Python环境"""
    python_path = sys.executable
    print(f"当前Python路径: {python_path}")
    
    # 检查是否在正确的环境中
    if "gamemarket_crawler" in python_path:
        print("✅ 已在gamemarket_crawler环境中")
        return True
    else:
        print("❌ 不在gamemarket_crawler环境中")
        return False

def activate_environment():
    """激活conda环境"""
    try:
        # 获取conda路径
        conda_path = subprocess.check_output(["which", "conda"], text=True).strip()
        print(f"找到conda: {conda_path}")
        
        # 激活环境
        activate_cmd = f"source {conda_path.replace('bin/conda', 'etc/profile.d/conda.sh')} && conda activate gamemarket_crawler"
        
        # 运行激活命令
        result = subprocess.run(
            f"bash -c '{activate_cmd} && python -c \"import sys; print(sys.executable)\"'",
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✅ 环境激活成功")
            return True
        else:
            print(f"❌ 环境激活失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 激活环境时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("游戏市场爬虫项目环境检查")
    print("=" * 50)
    
    # 检查当前环境
    if not check_environment():
        print("\n尝试激活gamemarket_crawler环境...")
        if not activate_environment():
            print("\n请手动激活环境:")
            print("conda activate gamemarket_crawler")
            return
    
    # 检查项目文件
    project_files = [
        "scraper/spiders/steam_spider.py",
        "run_crawler.py",
        "requirements.txt"
    ]
    
    print("\n检查项目文件:")
    for file_path in project_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (缺失)")
    
    print("\n环境设置完成！")
    print("您现在可以运行爬虫项目了。")

if __name__ == "__main__":
    main() 