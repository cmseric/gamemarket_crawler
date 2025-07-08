# -*- coding: utf-8 -*-
"""
MySQL存储管道
"""

import os
import re
from datetime import datetime
from decimal import Decimal
import pymysql
from pymysql.err import IntegrityError, OperationalError
from scrapy.exceptions import DropItem
from loguru import logger


class MySQLPipeline:
    """MySQL存储管道"""
    
    def __init__(self, mysql_host, mysql_port, mysql_user, mysql_password, mysql_database):
        """初始化MySQL连接参数"""
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.mysql_database = mysql_database
        self.connection = None
        self.cursor = None
    
    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫设置中创建管道实例"""
        mysql_host = crawler.settings.get('MYSQL_HOST', 'localhost')
        mysql_port = crawler.settings.get('MYSQL_PORT', 3306)
        mysql_user = crawler.settings.get('MYSQL_USER', 'root')
        mysql_password = crawler.settings.get('MYSQL_PASSWORD', '')
        mysql_database = crawler.settings.get('MYSQL_DATABASE', 'gamemarket')
        return cls(mysql_host, mysql_port, mysql_user, mysql_password, mysql_database)
    
    def open_spider(self, spider):
        """爬虫开始时连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user=self.mysql_user,
                password=self.mysql_password,
                database=self.mysql_database,
                charset='utf8mb4',
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            
            # 创建表结构
            self._create_tables(spider.name)
            
            logger.info(f"MySQL连接成功: {self.mysql_host}:{self.mysql_port}/{self.mysql_database}")
            
        except Exception as e:
            logger.error(f"MySQL连接失败: {e}")
            raise DropItem(f"MySQL连接失败: {e}")
    
    def close_spider(self, spider):
        """爬虫结束时关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            logger.info("MySQL连接已关闭")
    
    def process_item(self, item, spider):
        """处理数据项并存储到MySQL"""
        try:
            if spider.name in ['steam_top_sellers', 'steam_popular']:
                return self._process_steam_item(item, spider)
            else:
                logger.warning(f"未知的爬虫类型: {spider.name}")
                return item
                
        except Exception as e:
            logger.error(f"存储到MySQL失败: {e}")
            # 不丢弃数据，继续传递给下一个管道
            return item
    
    def _process_steam_item(self, item, spider):
        """处理Steam游戏数据"""
        try:
            # 检查数据库连接
            if not self.cursor or not self.connection:
                logger.error("数据库连接未建立，跳过数据处理")
                return item
            
            # 准备数据
            data = {
                'app_id': item.get('app_id'),
                'name': item.get('name'),
                'price': self._parse_price(item.get('price')),
                'original_price': self._parse_price(item.get('original_price')),
                'discount_percent': self._parse_int(item.get('discount_percent')),
                'developer': item.get('developer'),
                'publisher': item.get('publisher'),
                'release_date': self._parse_date(item.get('release_date')),
                'positive_rate': self._parse_int(item.get('positive_rate')),
                'total_reviews': self._parse_int(item.get('total_reviews')),
                'genres': self._parse_list(item.get('genres')),
                'tags': self._parse_list(item.get('tags')),
                'crawl_date': item.get('crawl_date'),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # 检查是否已存在记录
            self.cursor.execute(
                "SELECT id FROM steam_games WHERE app_id = %s",
                (data['app_id'],)
            )
            existing_record = self.cursor.fetchone()
            
            if existing_record:
                # 更新现有记录
                self._update_steam_game(data)
                logger.debug(f"更新MySQL记录: {data['name']}")
            else:
                # 插入新记录
                self._insert_steam_game(data)
                logger.debug(f"插入MySQL记录: {data['name']}")
            
            return item
            
        except Exception as e:
            logger.error(f"处理Steam数据失败: {e}")
            return item
    
    def _create_tables(self, spider_name):
        """创建数据库表"""
        try:
            # 检查数据库连接
            if not self.cursor or not self.connection:
                logger.error("数据库连接未建立，无法创建表")
                return
            
            # Steam游戏表
            steam_games_table = """
            CREATE TABLE IF NOT EXISTS steam_games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                app_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10,2) NULL,
                original_price DECIMAL(10,2) NULL,
                discount_percent INT NULL,
                developer VARCHAR(255) NULL,
                publisher VARCHAR(255) NULL,
                release_date DATE NULL,
                positive_rate INT NULL,
                total_reviews INT NULL,
                genres TEXT NULL,
                tags TEXT NULL,
                crawl_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_app_id (app_id),
                INDEX idx_name (name),
                INDEX idx_developer (developer),
                INDEX idx_crawl_date (crawl_date),
                INDEX idx_price (price),
                INDEX idx_discount (discount_percent)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            self.cursor.execute(steam_games_table)
            self.connection.commit()
            
            logger.info("MySQL表结构创建成功")
            
        except Exception as e:
            logger.error(f"创建表结构失败: {e}")
            if self.connection:
                self.connection.rollback()
    
    def _insert_steam_game(self, data):
        """插入Steam游戏数据"""
        if not self.cursor or not self.connection:
            logger.error("数据库连接未建立，无法插入数据")
            return
            
        sql = """
        INSERT INTO steam_games (
            app_id, name, price, original_price, discount_percent,
            developer, publisher, release_date, positive_rate, total_reviews,
            genres, tags, crawl_date, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        self.cursor.execute(sql, (
            data['app_id'], data['name'], data['price'], data['original_price'],
            data['discount_percent'], data['developer'], data['publisher'],
            data['release_date'], data['positive_rate'], data['total_reviews'],
            data['genres'], data['tags'], data['crawl_date'],
            data['created_at'], data['updated_at']
        ))
        self.connection.commit()
    
    def _update_steam_game(self, data):
        """更新Steam游戏数据"""
        if not self.cursor or not self.connection:
            logger.error("数据库连接未建立，无法更新数据")
            return
            
        sql = """
        UPDATE steam_games SET
            name = %s, price = %s, original_price = %s, discount_percent = %s,
            developer = %s, publisher = %s, release_date = %s, positive_rate = %s,
            total_reviews = %s, genres = %s, tags = %s, crawl_date = %s,
            updated_at = %s
        WHERE app_id = %s
        """
        
        self.cursor.execute(sql, (
            data['name'], data['price'], data['original_price'], data['discount_percent'],
            data['developer'], data['publisher'], data['release_date'], data['positive_rate'],
            data['total_reviews'], data['genres'], data['tags'], data['crawl_date'],
            data['updated_at'], data['app_id']
        ))
        self.connection.commit()
    
    def _parse_price(self, price_str):
        """解析价格字符串为数字"""
        if not price_str:
            return None
        
        # 提取数字
        match = re.search(r'[\d,]+\.?\d*', str(price_str))
        if match:
            try:
                return Decimal(match.group().replace(',', ''))
            except:
                return None
        return None
    
    def _parse_int(self, value):
        """解析字符串为整数"""
        if not value:
            return None
        try:
            return int(str(value).replace(',', ''))
        except:
            return None
    
    def _parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            date_patterns = [
                '%Y-%m-%d',
                '%Y年%m月%d日',
                '%Y/%m/%d'
            ]
            
            for pattern in date_patterns:
                try:
                    return datetime.strptime(date_str, pattern).date()
                except:
                    continue
            
            return None
        except:
            return None
    
    def _parse_list(self, value):
        """解析列表为JSON字符串"""
        if not value:
            return None
        
        if isinstance(value, list):
            return ','.join(value)
        elif isinstance(value, str):
            return value
        else:
            return str(value)
    
    def get_table_stats(self, table_name='steam_games'):
        """获取表统计信息"""
        try:
            # 检查数据库连接
            if not self.cursor or not self.connection:
                logger.error("数据库连接未建立，无法获取表统计")
                return None
                
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            result = self.cursor.fetchone()
            total_count = result[0] if result else 0
            
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE crawl_date = %s", 
                              (datetime.now().strftime('%Y-%m-%d'),))
            result = self.cursor.fetchone()
            today_count = result[0] if result else 0
            
            return {
                'total_records': total_count,
                'today_records': today_count,
                'table_name': table_name
            }
        except Exception as e:
            logger.error(f"获取表统计失败: {e}")
            return None 