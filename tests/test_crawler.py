#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫测试脚本
"""

import os
import sys
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from loguru import logger


def test_steam_spider():
    """测试Steam爬虫"""
    try:
        # 获取项目设置
        settings = get_project_settings()
        
        # 修改设置用于测试
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('DOWNLOAD_DELAY', 1)  # 测试时减少延迟
        settings.set('CLOSESPIDER_PAGECOUNT', 2)  # 限制爬取页数
        settings.set('FEEDS', {
            'data/test_output/steam_test_%(time)s.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
            }
        })
        
        # 创建输出目录
        os.makedirs('data/test_output', exist_ok=True)
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        logger.info("开始测试Steam爬虫...")
        
        # 运行爬虫
        process.crawl('steam_top_sellers')
        process.start()
        
        logger.info("Steam爬虫测试完成")
        
        # 检查输出文件
        output_files = [f for f in os.listdir('data/test_output') if f.endswith('.json')]
        if output_files:
            logger.info(f"生成测试文件: {output_files}")
            return True
        else:
            logger.warning("未生成测试文件")
            return False
            
    except Exception as e:
        logger.error(f"测试Steam爬虫时出错: {e}")
        return False


def main():
    """主函数"""
    logger.info("开始爬虫测试")
    
    # 测试Steam爬虫
    success = test_steam_spider()
    
    if success:
        logger.info("✅ 爬虫测试成功")
    else:
        logger.error("❌ 爬虫测试失败")
        sys.exit(1)


if __name__ == '__main__':
    main() 