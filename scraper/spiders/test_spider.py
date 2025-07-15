# -*- coding: utf-8 -*-
"""
测试爬虫 - 用于验证基本功能
"""

import scrapy
from datetime import datetime
from scraper.items import SteamGameItem
from loguru import logger


class TestSpider(scrapy.Spider):
    """测试爬虫"""
    name = "test"
    allowed_domains = ["example.com"]
    start_urls = ["https://httpbin.org/get"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CLOSESPIDER_ITEMCOUNT": 3,  # 只爬取3条数据用于测试
    }

    def parse(self, response):
        """解析测试页面"""
        logger.info(f"测试爬虫开始工作: {response.url}")
        
        # 创建测试数据
        test_items = [
            {
                'rank': 1,
                'rank_type': 'test',
                'name': '测试游戏1',
                'app_id': 'test001',
                'price': '¥99',
                'developer': '测试开发商',
                'crawl_time': datetime.now().isoformat(),
                'crawl_date': datetime.now().strftime('%Y-%m-%d'),
                'status': '测试数据'
            },
            {
                'rank': 2,
                'rank_type': 'test',
                'name': '测试游戏2',
                'app_id': 'test002',
                'price': '¥199',
                'developer': '测试开发商2',
                'crawl_time': datetime.now().isoformat(),
                'crawl_date': datetime.now().strftime('%Y-%m-%d'),
                'status': '测试数据'
            },
            {
                'rank': 3,
                'rank_type': 'test',
                'name': '测试游戏3',
                'app_id': 'test003',
                'price': '¥299',
                'developer': '测试开发商3',
                'crawl_time': datetime.now().isoformat(),
                'crawl_date': datetime.now().strftime('%Y-%m-%d'),
                'status': '测试数据'
            }
        ]
        
        for i, test_data in enumerate(test_items):
            item = SteamGameItem()
            # 正确设置字段
            item['rank'] = test_data['rank']
            item['rank_type'] = test_data['rank_type']
            item['name'] = test_data['name']
            item['app_id'] = test_data['app_id']
            item['price'] = test_data['price']
            item['developer'] = test_data['developer']
            item['crawl_time'] = test_data['crawl_time']
            item['crawl_date'] = test_data['crawl_date']
            
            logger.info(f"生成测试数据 {i+1}: {item['name']} (排名: {item['rank']})")
            yield item
        
        logger.info("测试爬虫完成") 