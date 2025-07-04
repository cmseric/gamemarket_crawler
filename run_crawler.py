#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫运行脚本
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


def run_spider(spider_name, output_format='json'):
    """运行指定爬虫"""
    try:
        # 获取项目设置
        settings = get_project_settings()
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        # 添加爬虫
        process.crawl(spider_name)
        
        logger.info(f"开始运行爬虫: {spider_name}")
        
        # 启动爬虫
        process.start()
        
        logger.info(f"爬虫 {spider_name} 运行完成")
        
    except Exception as e:
        logger.error(f"运行爬虫 {spider_name} 时出错: {e}")
        raise


def list_spiders():
    """列出所有可用的爬虫"""
    from scraper.spiders import steam_spider
    
    spiders = [
        'steam_top_sellers',
        'steam_popular'
    ]
    
    logger.info("可用的爬虫:")
    for spider in spiders:
        logger.info(f"  - {spider}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='游戏市场数据爬虫')
    parser.add_argument('spider', nargs='?', help='要运行的爬虫名称')
    parser.add_argument('--list', action='store_true', help='列出所有可用的爬虫')
    parser.add_argument('--output', default='json', choices=['json', 'csv', 'xml'], help='输出格式')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    logger.info("游戏市场数据爬虫启动")
    
    if args.list:
        list_spiders()
        return
    
    if not args.spider:
        logger.error("请指定要运行的爬虫名称")
        parser.print_help()
        return
    
    # 运行爬虫
    run_spider(args.spider, args.output)


if __name__ == '__main__':
    main() 