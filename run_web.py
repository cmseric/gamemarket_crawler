#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameMarket Crawler Web应用启动脚本
"""

import os
import sys
import argparse
from web.app import create_app

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='GameMarket Crawler Web Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='监听端口 (默认: 8080)')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--env', default='development', 
                       choices=['development', 'production', 'testing'],
                       help='运行环境 (默认: development)')
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = args.env
    if args.debug:
        os.environ['FLASK_DEBUG'] = 'true'
    
    print(f"🚀 启动GameMarket Crawler Web Dashboard")
    print(f"📍 环境: {args.env}")
    print(f"🌐 地址: http://{args.host}:{args.port}")
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
    print("-" * 50)
    
    try:
        # 创建Flask应用
        app = create_app(args.env)
        
        # 启动应用
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Web应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 