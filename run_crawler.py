#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏市场数据爬虫运行脚本（整合版）
"""

import os
import sys
import argparse
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from loguru import logger


def setup_logging():
    """设置日志"""
    # 创建日志目录
    os.makedirs('data/logs', exist_ok=True)
    
    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        f"data/logs/crawler_{datetime.now().strftime('%Y%m%d')}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days"
    )


def configure_settings(settings, spider_name, output_format='json'):
    """配置爬虫设置"""
    # 启用Playwright（已在settings.py中配置）
    # 启用中间件
    settings.set('DOWNLOADER_MIDDLEWARES', {
        'scraper.middlewares.RandomUserAgentMiddleware': 400,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    })
    
    # 启用数据验证、清洗和数据库管道
    settings.set('ITEM_PIPELINES', {
        'scraper.pipelines.DataValidationPipeline': 300,
        'scraper.pipelines.DataCleaningPipeline': 400,
        'scraper.pipelines.MySQLPipeline': 500,
        'scraper.pipelines.MongoDBPipeline': 600,
    })
    
    # 基本设置
    settings.set('ROBOTSTXT_OBEY', False)  # 暂时禁用robots.txt
    settings.set('LOG_LEVEL', 'INFO')
    settings.set('DOWNLOAD_DELAY', 1)
    settings.set('CLOSESPIDER_ITEMCOUNT', 5)  # 限制爬取5条数据
    
    # 创建输出目录
    os.makedirs('data/export', exist_ok=True)
    
    # 设置输出文件
    settings.set('FEEDS', {
        f'data/export/{spider_name}_%(time)s.{output_format}': {
            'format': output_format,
            'encoding': 'utf8',
            'indent': 2,
        }
    })


def run_spider(spider_name, output_format='json'):
    """运行指定爬虫"""
    try:
        # 获取项目设置
        settings = get_project_settings()
        
        # 配置设置
        configure_settings(settings, spider_name, output_format)
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        logger.info(f"开始运行爬虫: {spider_name}")
        
        # 添加爬虫
        process.crawl(spider_name)
        
        # 启动爬虫
        process.start()
        
        logger.info(f"爬虫 {spider_name} 运行完成")
        
    except Exception as e:
        logger.error(f"运行爬虫 {spider_name} 时出错: {e}")
        raise


def get_available_spiders():
    """获取所有可用的爬虫"""
    return [
        {'id': 'test', 'name': '测试爬虫', 'description': '用于测试基本功能'},
        {'id': 'steam_top_sellers', 'name': 'Steam热销榜', 'description': '爬取Steam热销游戏数据'},
        {'id': 'steam_popular', 'name': 'Steam热门榜', 'description': '爬取Steam热门游戏数据'}
    ]


def get_output_formats():
    """获取可用的输出格式"""
    return [
        {'id': 'json', 'name': 'JSON格式', 'description': '结构化数据，易于处理'},
        {'id': 'csv', 'name': 'CSV格式', 'description': '表格格式，适合Excel打开'},
        {'id': 'xml', 'name': 'XML格式', 'description': '标记语言格式'}
    ]


def display_menu(title, options):
    """显示菜单"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")
    
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option['name']}")
        print(f"     {option['description']}")
        print()
    
    return len(options)


def get_user_choice(max_options, prompt="请选择 (1-{}): ".format):
    """获取用户选择"""
    while True:
        try:
            choice = input(prompt(max_options)).strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= max_options:
                return choice_num
            else:
                print(f"❌ 请输入 1-{max_options} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            print("\n\n👋 用户取消操作")
            sys.exit(0)


def interactive_selection():
    """交互式选择界面"""
    print("🎮 游戏市场数据爬虫")
    print("="*50)
    
    # 选择爬虫
    spiders = get_available_spiders()
    max_spiders = display_menu("选择要运行的爬虫", spiders)
    spider_choice = get_user_choice(max_spiders, "请选择爬虫 (1-{}): ".format)
    selected_spider = spiders[spider_choice - 1]
    
    print(f"✅ 已选择: {selected_spider['name']}")
    
    # 选择输出格式
    formats = get_output_formats()
    max_formats = display_menu("选择输出格式", formats)
    format_choice = get_user_choice(max_formats, "请选择格式 (1-{}): ".format)
    selected_format = formats[format_choice - 1]
    
    print(f"✅ 已选择: {selected_format['name']}")
    
    # 确认运行
    print(f"\n📋 运行配置:")
    print(f"   爬虫: {selected_spider['name']}")
    print(f"   输出格式: {selected_format['name']}")
    print(f"   输出目录: data/export/")
    
    confirm = input("\n🚀 确认开始运行? (y/N): ").strip().lower()
    if confirm in ['y', 'yes', '是']:
        return selected_spider['id'], selected_format['id']
    else:
        print("❌ 已取消运行")
        return None, None


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    logger.info("游戏市场数据爬虫启动（交互式版本）")
    
    try:
        # 交互式选择
        spider_name, output_format = interactive_selection()
        
        if spider_name and output_format:
            # 运行爬虫
            run_spider(spider_name, output_format)
        else:
            print("👋 再见！")
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        print(f"❌ 程序运行出错: {e}")


if __name__ == '__main__':
    main() 