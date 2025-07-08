# -*- coding: utf-8 -*-
"""
Steam游戏数据爬虫
"""

import scrapy
import re
from datetime import datetime
from urllib.parse import urljoin
from scraper.items import SteamGameItem
from loguru import logger


class SteamTopSellersSpider(scrapy.Spider):
    """Steam畅销游戏爬虫"""
    name = "steam_top_sellers"
    allowed_domains = ["steampowered.com"]
    start_urls = ["https://store.steampowered.com/search/?filter=topsellers"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 3,  # 合规延迟
        "PLAYWRIGHT_ENABLED": True,
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 30000,
    }

    def parse(self, response):
        """解析游戏列表页"""
        logger.info(f"开始解析Steam畅销游戏页面: {response.url}")
        
        # 尝试多种CSS选择器
        games = response.css('div#search_resultsRows a.search_result_row')
        if not games:
            games = response.css('a.search_result_row')
        if not games:
            games = response.css('div.search_result_row')
        
        logger.info(f"找到 {len(games)} 个游戏")
        
        for i, game in enumerate(games):
            item = SteamGameItem()
            
            # 基本信息
            item['name'] = game.css('span.title::text').get()
            if not item['name']:
                item['name'] = game.css('div.search_name a span::text').get()
            
            item['app_id'] = game.attrib.get('data-ds-appid')
            if not item['app_id']:
                # 从URL中提取app_id
                href = game.attrib.get('href', '')
                app_match = re.search(r'/app/(\d+)/', href)
                if app_match:
                    item['app_id'] = app_match.group(1)
            
            # 价格信息
            price_elem = game.css('div.discount_final_price::text')
            if price_elem:
                item['price'] = price_elem.get().strip()
            else:
                # 尝试其他价格选择器
                price_elem = game.css('div.search_price::text')
                if price_elem:
                    item['price'] = price_elem.get().strip()
            
            original_price_elem = game.css('div.discount_original_price::text')
            if original_price_elem:
                item['original_price'] = original_price_elem.get().strip()
            
            # 折扣信息
            discount_elem = game.css('div.discount_pct::text')
            if discount_elem:
                discount_text = discount_elem.get()
                if discount_text:
                    match = re.search(r'-(\d+)%', discount_text)
                    if match:
                        item['discount_percent'] = match.group(1)
            
            # 开发商
            item['developer'] = game.css('div.search_developer::text').get()
            if not item['developer']:
                item['developer'] = game.css('div.search_developer span::text').get()
            
            # 爬取时间
            item['crawl_time'] = datetime.now().isoformat()
            item['crawl_date'] = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"解析游戏 {i+1}: {item['name']} (ID: {item['app_id']})")
            
            # 进入详情页获取更多信息
            detail_url = game.attrib.get('href')
            if detail_url:
                yield response.follow(
                    detail_url, 
                    self.parse_detail, 
                    meta={'item': item}
                )
            else:
                # 如果没有详情页，直接yield当前数据
                yield item

    def parse_detail(self, response):
        """解析游戏详情页"""
        item = response.meta['item']
        logger.info(f"解析详情页: {item['name']}")
        
        # 发行商
        publisher_elem = response.css('div.dev_row:contains("发行商") a::text')
        if publisher_elem:
            item['publisher'] = publisher_elem.get()
        else:
            # 尝试其他选择器
            publisher_elem = response.css('div.dev_row a::text')
            if publisher_elem:
                item['publisher'] = publisher_elem.get()
        
        # 发行日期
        release_date_elem = response.css('div.date::text')
        if release_date_elem:
            item['release_date'] = release_date_elem.get().strip()
        
        # 游戏类型
        genres = response.css('a.genre::text').getall()
        if genres:
            item['genres'] = [genre.strip() for genre in genres]
        
        # 标签
        tags = response.css('a.app_tag::text').getall()
        if tags:
            item['tags'] = [tag.strip() for tag in tags[:10]]  # 限制标签数量
        
        # 评分信息
        positive_rate_elem = response.css('span.game_review_summary::text')
        if positive_rate_elem:
            positive_text = positive_rate_elem.get()
            if positive_text:
                # 提取好评率数字
                match = re.search(r'(\d+)%', positive_text)
                if match:
                    item['positive_rate'] = match.group(1)
        
        # 评论数量
        reviews_elem = response.css('span.responsive_hidden::text')
        if reviews_elem:
            reviews_text = reviews_elem.get()
            if reviews_text:
                # 提取评论数量
                match = re.search(r'(\d+(?:,\d+)*)', reviews_text)
                if match:
                    item['total_reviews'] = match.group(1).replace(',', '')
        
        logger.info(f"详情页解析完成: {item['name']}")
        yield item


class SteamPopularSpider(scrapy.Spider):
    """Steam热门游戏爬虫"""
    name = "steam_popular"
    allowed_domains = ["steampowered.com"]
    start_urls = ["https://store.steampowered.com/search/?filter=popularnew"]
    
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "PLAYWRIGHT_ENABLED": True,
    }

    def parse(self, response):
        """解析热门游戏列表"""
        logger.info(f"开始解析Steam热门游戏页面: {response.url}")
        
        # 尝试多种CSS选择器
        games = response.css('div#search_resultsRows a.search_result_row')
        if not games:
            games = response.css('a.search_result_row')
        if not games:
            games = response.css('div.search_result_row')
        
        logger.info(f"找到 {len(games)} 个游戏")
        
        for i, game in enumerate(games):
            item = SteamGameItem()
            
            # 基本信息
            item['name'] = game.css('span.title::text').get()
            if not item['name']:
                item['name'] = game.css('div.search_name a span::text').get()
            
            item['app_id'] = game.attrib.get('data-ds-appid')
            if not item['app_id']:
                # 从URL中提取app_id
                href = game.attrib.get('href', '')
                app_match = re.search(r'/app/(\d+)/', href)
                if app_match:
                    item['app_id'] = app_match.group(1)
            
            # 价格信息
            price_elem = game.css('div.discount_final_price::text')
            if price_elem:
                item['price'] = price_elem.get().strip()
            else:
                # 尝试其他价格选择器
                price_elem = game.css('div.search_price::text')
                if price_elem:
                    item['price'] = price_elem.get().strip()
            
            # 开发商
            item['developer'] = game.css('div.search_developer::text').get()
            if not item['developer']:
                item['developer'] = game.css('div.search_developer span::text').get()
            
            # 爬取时间
            item['crawl_time'] = datetime.now().isoformat()
            item['crawl_date'] = datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"解析游戏 {i+1}: {item['name']} (ID: {item['app_id']})")
            
            # 进入详情页
            detail_url = game.attrib.get('href')
            if detail_url:
                yield response.follow(
                    detail_url, 
                    self.parse_detail, 
                    meta={'item': item}
                )
            else:
                # 如果没有详情页，直接yield当前数据
                yield item

    def parse_detail(self, response):
        """解析游戏详情页"""
        item = response.meta['item']
        logger.info(f"解析详情页: {item['name']}")
        
        # 发行商
        publisher_elem = response.css('div.dev_row:contains("发行商") a::text')
        if publisher_elem:
            item['publisher'] = publisher_elem.get()
        else:
            # 尝试其他选择器
            publisher_elem = response.css('div.dev_row a::text')
            if publisher_elem:
                item['publisher'] = publisher_elem.get()
        
        # 发行日期
        release_date_elem = response.css('div.date::text')
        if release_date_elem:
            item['release_date'] = release_date_elem.get().strip()
        
        # 游戏类型
        genres = response.css('a.genre::text').getall()
        if genres:
            item['genres'] = [genre.strip() for genre in genres]
        
        logger.info(f"详情页解析完成: {item['name']}")
        yield item 