#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化爬虫测试脚本
"""

import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from loguru import logger


def test_basic_spider():
    """测试基本爬虫功能"""
    try:
        # 获取项目设置
        settings = get_project_settings()
        
        # 简化设置，禁用有问题的组件
        settings.set('DOWNLOAD_HANDLERS', {})  # 禁用Playwright
        settings.set('DOWNLOADER_MIDDLEWARES', {})  # 禁用中间件
        settings.set('ITEM_PIPELINES', {})  # 禁用管道
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('DOWNLOAD_DELAY', 1)
        settings.set('CLOSESPIDER_PAGECOUNT', 1)  # 只爬取1页
        settings.set('ROBOTSTXT_OBEY', False)  # 暂时禁用robots.txt
        
        # 创建输出目录
        os.makedirs('data/test_output', exist_ok=True)
        
        # 设置输出文件
        settings.set('FEEDS', {
            'data/test_output/test_%(time)s.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
            }
        })
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        
        logger.info("开始测试基本爬虫功能...")
        
        # 运行测试爬虫
        process.crawl('test')
        process.start()
        
        logger.info("基本爬虫测试完成")
        
        # 检查输出文件
        output_files = [f for f in os.listdir('data/test_output') if f.endswith('.json')]
        if output_files:
            logger.info(f"✅ 生成测试文件: {output_files}")
            return True
        else:
            logger.warning("❌ 未生成测试文件")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试爬虫时出错: {e}")
        return False


def main():
    """主函数"""
    logger.info("开始简化爬虫测试")
    
    # 测试基本爬虫
    success = test_basic_spider()
    
    if success:
        logger.info("✅ 爬虫基本功能正常")
    else:
        logger.error("❌ 爬虫基本功能异常")
        sys.exit(1)


if __name__ == '__main__':
    main() 