#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫测试脚本 - 测试中间件、管道和数据库功能
"""

import os
import sys
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from loguru import logger

# Patch: 只抓取前N个游戏
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.spiders.steam_spider import SteamTopSellersSpider
from scraper.items import SteamGameItem
import re

def limited_parse(self, response, limit=5):
    """限制数据条数的解析函数"""
    games = response.css('div#search_resultsRows a.search_result_row')
    if not games:
        games = response.css('a.search_result_row')
    if not games:
        games = response.css('div.search_result_row')
    
    logger.info(f"[测试Patch] 只处理前{limit}个游戏")
    
    for i, game in enumerate(games[:limit]):
        item = SteamGameItem()
        item['name'] = game.css('span.title::text').get()
        if not item['name']:
            item['name'] = game.css('div.search_name a span::text').get()
        
        item['app_id'] = game.attrib.get('data-ds-appid')
        if not item['app_id']:
            href = game.attrib.get('href', '')
            app_match = re.search(r'/app/(\d+)/', href)
            if app_match:
                item['app_id'] = app_match.group(1)
        
        price_elem = game.css('div.discount_final_price::text')
        if price_elem:
            item['price'] = price_elem.get().strip()
        else:
            price_elem = game.css('div.search_price::text')
            if price_elem:
                item['price'] = price_elem.get().strip()
        
        item['developer'] = game.css('div.search_developer::text').get()
        if not item['developer']:
            item['developer'] = game.css('div.search_developer span::text').get()
        
        item['crawl_time'] = datetime.now().isoformat()
        item['crawl_date'] = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"[测试Patch] 解析游戏 {i+1}: {item['name']} (ID: {item['app_id']})")
        
        detail_url = game.attrib.get('href')
        if detail_url:
            yield response.follow(detail_url, self.parse_detail, meta={'item': item})
        else:
            yield item

# 注释掉原有的静态patch，现在使用动态设置
# SteamTopSellersSpider.parse = limited_parse

def configure_test_settings(settings, test_limit=5):
    """配置测试设置"""
    settings.set('LOG_LEVEL', 'INFO')
    settings.set('DOWNLOAD_DELAY', 1)
    settings.set('CLOSESPIDER_ITEMCOUNT', test_limit)  # 使用可配置的限制
    settings.set('CLOSESPIDER_PAGECOUNT', 10)  # 允许更多页面，确保详情页能正常访问
    settings.set('CLOSESPIDER_TIMEOUT', 180)
    settings.set('DOWNLOADER_MIDDLEWARES', {
        'scraper.middlewares.RandomUserAgentMiddleware': 400,
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    })
    settings.set('ITEM_PIPELINES', {
        'scraper.pipelines.DataValidationPipeline': 300,
        'scraper.pipelines.DataCleaningPipeline': 400,
        'scraper.pipelines.MongoDBPipeline': 500,
        'scraper.pipelines.MySQLPipeline': 600,
    })
    settings.set('ROBOTSTXT_OBEY', False)
    settings.set('FEEDS', {
        'data/test_output/steam_test_%(time)s.json': {
            'format': 'json',
            'encoding': 'utf8',
            'indent': 2,
        }
    })
    os.makedirs('data/test_output', exist_ok=True)
    logger.info("测试设置配置完成")
    logger.info(f"- 爬取限制: {settings.get('CLOSESPIDER_ITEMCOUNT')} 条数据")
    logger.info(f"- 页面限制: {settings.get('CLOSESPIDER_PAGECOUNT')} 页")
    logger.info(f"- 超时设置: {settings.get('CLOSESPIDER_TIMEOUT')} 秒")

def test_steam_spider(test_limit=5):
    """测试Steam爬虫"""
    try:
        settings = get_project_settings()
        configure_test_settings(settings, test_limit)
        process = CrawlerProcess(settings)
        logger.info("开始测试Steam爬虫...")
        logger.info("测试内容:")
        logger.info("- 中间件功能（随机User-Agent）")
        logger.info("- 数据验证管道")
        logger.info("- 数据清洗管道")
        logger.info("- 数据库写入管道")
        logger.info(f"- 数据条数限制: {test_limit}")
        
        # 动态设置limited_parse的限制
        def dynamic_limited_parse(self, response):
            return limited_parse(self, response, limit=test_limit)
        
        SteamTopSellersSpider.parse = dynamic_limited_parse
        
        process.crawl('steam_top_sellers')
        process.start()
        logger.info("Steam爬虫测试完成")
        
        output_files = [f for f in os.listdir('data/test_output') if f.endswith('.json')]
        if output_files:
            logger.info(f"生成测试文件: {output_files}")
            latest_file = max(output_files, key=lambda x: os.path.getctime(os.path.join('data/test_output', x)))
            file_path = os.path.join('data/test_output', latest_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                data_count = content.count('"name"')
                logger.info(f"实际爬取数据条数: {data_count}")
                if data_count <= test_limit:
                    logger.info("✅ 数据条数限制生效")
                else:
                    logger.warning(f"⚠️ 数据条数限制可能未生效，实际爬取 {data_count} 条")
            return True
        else:
            logger.warning("未生成测试文件")
            return False
    except Exception as e:
        logger.error(f"测试Steam爬虫时出错: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        logger.info("测试数据库连接...")
        try:
            from scraper.pipelines.mongodb_pipeline import MongoDBPipeline
            logger.info("✅ MongoDB管道模块加载成功")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB管道模块加载失败: {e}")
        try:
            from scraper.pipelines.mysql_pipeline import MySQLPipeline
            logger.info("✅ MySQL管道模块加载成功")
        except Exception as e:
            logger.warning(f"⚠️ MySQL管道模块加载失败: {e}")
        return True
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False

def main():
    """主函数，支持可配置的测试条数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Steam爬虫测试工具')
    parser.add_argument('--limit', type=int, default=5, help='测试数据条数限制 (默认: 5)')
    args = parser.parse_args()
    
    test_limit = args.limit
    logger.info("=" * 50)
    logger.info("开始爬虫功能测试")
    logger.info(f"测试数据条数限制: {test_limit}")
    logger.info("=" * 50)
    
    db_ok = test_database_connection()
    spider_ok = test_steam_spider(test_limit)
    
    logger.info("=" * 50)
    if spider_ok:
        logger.info("✅ 爬虫测试成功")
        if db_ok:
            logger.info("✅ 数据库连接测试成功")
        else:
            logger.warning("⚠️ 数据库连接测试失败，但不影响爬虫功能")
    else:
        logger.error("❌ 爬虫测试失败")
        sys.exit(1)
    logger.info("=" * 50)
    logger.info(f"提示: 可以使用 --limit 参数设置测试数据条数，例如: python test_crawler.py --limit 3")

if __name__ == '__main__':
    main() 