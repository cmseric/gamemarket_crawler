# -*- coding: utf-8 -*-
"""
MongoDB存储管道
"""

import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from scrapy.exceptions import DropItem
from loguru import logger


class MongoDBPipeline:
    """MongoDB存储管道"""
    
    def __init__(self, mongodb_uri, mongodb_database):
        """初始化MongoDB连接"""
        self.mongodb_uri = mongodb_uri
        self.mongodb_database = mongodb_database
        self.client = None
        self.db = None
        self.collections = {}
    
    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫设置中创建管道实例"""
        mongodb_uri = crawler.settings.get('MONGODB_URI', 'mongodb://localhost:27017')
        mongodb_database = crawler.settings.get('MONGODB_DATABASE', 'gamemarket')
        return cls(mongodb_uri, mongodb_database)
    
    def open_spider(self, spider):
        """爬虫开始时连接数据库"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.mongodb_database]
            
            # 为不同爬虫创建不同的集合
            collection_name = f"{spider.name}_{datetime.now().strftime('%Y%m')}"
            self.collections[spider.name] = self.db[collection_name]
            
            # 创建索引
            self._create_indexes(spider.name)
            
            logger.info(f"MongoDB连接成功: {self.mongodb_uri}/{self.mongodb_database}")
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise DropItem(f"MongoDB连接失败: {e}")
    
    def close_spider(self, spider):
        """爬虫结束时关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")
    
    def process_item(self, item, spider):
        """处理数据项并存储到MongoDB"""
        try:
            # 获取对应的集合
            collection = self.collections.get(spider.name)
            if not collection:
                logger.error(f"未找到爬虫 {spider.name} 对应的集合")
                return item
            
            # 准备存储的数据
            data = dict(item)
            
            # 添加元数据
            data['_spider'] = spider.name
            data['_crawl_time'] = datetime.now()
            data['_created_at'] = datetime.now()
            
            # 根据爬虫类型设置不同的主键
            if spider.name == 'steam_top_sellers' or spider.name == 'steam_popular':
                # Steam游戏使用app_id作为主键
                if 'app_id' in data and data['app_id']:
                    data['_id'] = data['app_id']
                else:
                    # 如果没有app_id，使用名称和时间组合
                    data['_id'] = f"{data.get('name', 'unknown')}_{data.get('crawl_date', 'unknown')}"
            
            # 尝试插入数据
            try:
                collection.insert_one(data)
                logger.debug(f"成功存储到MongoDB: {data.get('name', 'Unknown')}")
                
            except DuplicateKeyError:
                # 如果主键重复，更新现有记录
                update_data = {k: v for k, v in data.items() if not k.startswith('_')}
                update_data['_updated_at'] = datetime.now()
                
                collection.update_one(
                    {'_id': data['_id']},
                    {'$set': update_data}
                )
                logger.debug(f"更新MongoDB记录: {data.get('name', 'Unknown')}")
            
            return item
            
        except Exception as e:
            logger.error(f"存储到MongoDB失败: {e}")
            # 不丢弃数据，继续传递给下一个管道
            return item
    
    def _create_indexes(self, spider_name):
        """创建数据库索引"""
        collection = self.collections[spider_name]
        
        try:
            # 创建复合索引
            if spider_name in ['steam_top_sellers', 'steam_popular']:
                # Steam游戏索引
                collection.create_index([('name', 1), ('crawl_date', -1)])
                collection.create_index([('app_id', 1)])
                collection.create_index([('crawl_date', -1)])
                collection.create_index([('developer', 1)])
                collection.create_index([('price', 1)])
                
                # 文本搜索索引
                collection.create_index([('name', 'text'), ('developer', 'text')])
            
            logger.info(f"为爬虫 {spider_name} 创建索引成功")
            
        except Exception as e:
            logger.warning(f"创建索引失败: {e}")
    
    def get_collection_stats(self, spider_name):
        """获取集合统计信息"""
        try:
            collection = self.collections.get(spider_name)
            if collection:
                stats = {
                    'total_documents': collection.count_documents({}),
                    'today_documents': collection.count_documents({
                        'crawl_date': datetime.now().strftime('%Y-%m-%d')
                    }),
                    'collection_name': collection.name
                }
                return stats
        except Exception as e:
            logger.error(f"获取集合统计失败: {e}")
        return None 