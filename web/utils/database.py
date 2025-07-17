# -*- coding: utf-8 -*-
"""
数据库管理工具
"""

import json
import os
import redis
import pymongo
import pymysql
from datetime import datetime, timedelta
from loguru import logger
from typing import Dict, List, Any, Optional


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config):
        self.config = config
        self.mysql_conn = None
        self.mongodb_client = None
        self.redis_client = None
        self._init_connections()
    
    def _init_connections(self):
        """初始化数据库连接"""
        try:
            # 从环境变量获取配置，如果config对象没有属性则使用环境变量
            mysql_host = getattr(self.config, 'MYSQL_HOST', None) or os.getenv('MYSQL_HOST', 'localhost')
            mysql_port = getattr(self.config, 'MYSQL_PORT', None) or int(os.getenv('MYSQL_PORT', 3306))
            mysql_user = getattr(self.config, 'MYSQL_USER', None) or os.getenv('MYSQL_USER', 'root')
            mysql_password = getattr(self.config, 'MYSQL_PASSWORD', None) or os.getenv('MYSQL_PASSWORD', '')
            mysql_database = getattr(self.config, 'MYSQL_DATABASE', None) or os.getenv('MYSQL_DATABASE', 'gamemarket')
            
            # MySQL连接
            self.mysql_conn = pymysql.connect(
                host=mysql_host,
                port=mysql_port,
                user=mysql_user,
                password=mysql_password,
                database=mysql_database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info("MySQL连接成功")
        except Exception as e:
            logger.warning(f"MySQL连接失败: {e}")
            self.mysql_conn = None
        
        try:
            # MongoDB连接
            mongodb_uri = getattr(self.config, 'MONGODB_URI', None) or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
            mongodb_database = getattr(self.config, 'MONGODB_DATABASE', None) or os.getenv('MONGODB_DATABASE', 'gamemarket')
            
            self.mongodb_client = pymongo.MongoClient(mongodb_uri)
            self.mongodb_db = self.mongodb_client[mongodb_database]
            logger.info("MongoDB连接成功")
        except Exception as e:
            logger.warning(f"MongoDB连接失败: {e}")
            self.mongodb_client = None
        
        try:
            # Redis连接
            redis_url = getattr(self.config, 'REDIS_URL', None) or os.getenv('REDIS_URL', 'redis://localhost:6379')
            
            self.redis_client = redis.from_url(redis_url)
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def close_connections(self):
        """关闭数据库连接"""
        if self.mysql_conn:
            self.mysql_conn.close()
        if self.mongodb_client:
            self.mongodb_client.close()
        if self.redis_client:
            self.redis_client.close()
    
    def get_mysql_connection(self):
        """获取MySQL连接"""
        if not self.mysql_conn or not self.mysql_conn.open:
            self._init_connections()
        return self.mysql_conn
    
    def get_mongodb_collection(self, collection_name):
        """获取MongoDB集合"""
        if not self.mongodb_client:
            return None
        return self.mongodb_db[collection_name]
    
    def get_redis_client(self):
        """获取Redis客户端"""
        return self.redis_client


class SteamDataQuery:
    """Steam数据查询类"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        try:
            mysql_conn = self.db_manager.get_mysql_connection()
            if not mysql_conn:
                return self._get_mock_summary()
            
            with mysql_conn.cursor() as cursor:
                # 获取基础统计
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_games,
                        COUNT(CASE WHEN price > 0 THEN 1 END) as paid_games,
                        COUNT(CASE WHEN price = 0 THEN 1 END) as free_games,
                        AVG(price) as avg_price,
                        AVG(discount_percent) as avg_discount
                    FROM steam_games 
                    WHERE price IS NOT NULL
                """)
                stats = cursor.fetchone()
                
                # 获取最新更新时间
                cursor.execute("""
                    SELECT MAX(updated_at) as last_update 
                    FROM steam_games
                """)
                last_update = cursor.fetchone()
                
                return {
                    'total_games': stats['total_games'] or 0,
                    'paid_games': stats['paid_games'] or 0,
                    'free_games': stats['free_games'] or 0,
                    'avg_price': float(stats['avg_price'] or 0),
                    'avg_discount': float(stats['avg_discount'] or 0),
                    'last_update': last_update['last_update'].isoformat() if last_update['last_update'] else None
                }
        except Exception as e:
            logger.error(f"获取统计摘要失败: {e}")
            return self._get_mock_summary()
    
    def get_top_games_by_rank(self, rank_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取排行榜游戏"""
        try:
            mysql_conn = self.db_manager.get_mysql_connection()
            if not mysql_conn:
                return self._get_mock_games(limit)
            
            with mysql_conn.cursor() as cursor:
                if rank_type == 'topsellers':
                    query = """
                        SELECT app_id, name, price, discount_percent, 
                               positive_ratio, user_reviews, release_date
                        FROM steam_games 
                        WHERE price > 0 
                        ORDER BY user_reviews DESC 
                        LIMIT %s
                    """
                elif rank_type == 'newreleases':
                    query = """
                        SELECT app_id, name, price, discount_percent, 
                               positive_ratio, user_reviews, release_date
                        FROM steam_games 
                        WHERE release_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                        ORDER BY release_date DESC 
                        LIMIT %s
                    """
                else:  # 默认按价格排序
                    query = """
                        SELECT app_id, name, price, discount_percent, 
                               positive_ratio, user_reviews, release_date
                        FROM steam_games 
                        WHERE price > 0 
                        ORDER BY price DESC 
                        LIMIT %s
                    """
                
                cursor.execute(query, (limit,))
                games = cursor.fetchall()
                
                # 转换数据类型
                for game in games:
                    game['price'] = float(game['price'] or 0)
                    game['discount_percent'] = float(game['discount_percent'] or 0)
                    game['positive_ratio'] = float(game['positive_ratio'] or 0)
                    game['user_reviews'] = int(game['user_reviews'] or 0)
                    if game['release_date']:
                        game['release_date'] = game['release_date'].isoformat()
                
                return games
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}")
            return self._get_mock_games(limit)
    
    def get_price_distribution(self) -> Dict[str, int]:
        """获取价格分布"""
        try:
            mysql_conn = self.db_manager.get_mysql_connection()
            if not mysql_conn:
                return self._get_mock_price_distribution()
            
            with mysql_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN price = 0 THEN '免费'
                            WHEN price <= 10 THEN '0-10元'
                            WHEN price <= 50 THEN '10-50元'
                            WHEN price <= 100 THEN '50-100元'
                            WHEN price <= 200 THEN '100-200元'
                            ELSE '200元以上'
                        END as price_range,
                        COUNT(*) as count
                    FROM steam_games 
                    WHERE price IS NOT NULL
                    GROUP BY price_range
                    ORDER BY 
                        CASE price_range
                            WHEN '免费' THEN 1
                            WHEN '0-10元' THEN 2
                            WHEN '10-50元' THEN 3
                            WHEN '50-100元' THEN 4
                            WHEN '100-200元' THEN 5
                            ELSE 6
                        END
                """)
                results = cursor.fetchall()
                return {row['price_range']: row['count'] for row in results}
        except Exception as e:
            logger.error(f"获取价格分布失败: {e}")
            return self._get_mock_price_distribution()
    
    def get_genre_distribution(self) -> Dict[str, int]:
        """获取游戏类型分布"""
        try:
            # 尝试从MongoDB获取
            collection = self.db_manager.get_mongodb_collection('steam_games')
            if collection:
                pipeline = [
                    {"$unwind": "$genres"},
                    {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
                results = list(collection.aggregate(pipeline))
                return {item['_id']: item['count'] for item in results}
            else:
                return self._get_mock_genre_distribution()
        except Exception as e:
            logger.error(f"获取游戏类型分布失败: {e}")
            return self._get_mock_genre_distribution()
    
    def get_discount_analysis(self) -> Dict[str, Dict[str, Any]]:
        """获取折扣分析"""
        try:
            mysql_conn = self.db_manager.get_mysql_connection()
            if not mysql_conn:
                return self._get_mock_discount_analysis()
            
            with mysql_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN discount_percent = 0 THEN '无折扣'
                            WHEN discount_percent <= 25 THEN '1-25%'
                            WHEN discount_percent <= 50 THEN '26-50%'
                            WHEN discount_percent <= 75 THEN '51-75%'
                            ELSE '76-100%'
                        END as discount_range,
                        COUNT(*) as count,
                        AVG(discount_percent) as avg_discount
                    FROM steam_games 
                    WHERE discount_percent IS NOT NULL
                    GROUP BY discount_range
                    ORDER BY 
                        CASE discount_range
                            WHEN '无折扣' THEN 1
                            WHEN '1-25%' THEN 2
                            WHEN '26-50%' THEN 3
                            WHEN '51-75%' THEN 4
                            ELSE 5
                        END
                """)
                results = cursor.fetchall()
                return {
                    row['discount_range']: {
                        'count': row['count'],
                        'avg_discount': float(row['avg_discount'] or 0)
                    }
                    for row in results
                }
        except Exception as e:
            logger.error(f"获取折扣分析失败: {e}")
            return self._get_mock_discount_analysis()
    
    def get_available_tables(self) -> List[str]:
        """获取可用的数据表"""
        try:
            mysql_conn = self.db_manager.get_mysql_connection()
            if not mysql_conn:
                return ['steam_games', 'steam_reviews', 'steam_tags']
            
            with mysql_conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row[f'Tables_in_{self.db_manager.config.MYSQL_DATABASE}'] 
                         for row in cursor.fetchall()]
                return tables
        except Exception as e:
            logger.error(f"获取数据表失败: {e}")
            return ['steam_games', 'steam_reviews', 'steam_tags']
    
    def get_latest_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最新数据"""
        try:
            mysql_conn = self.db_manager.get_mysql_connection()
            if not mysql_conn:
                return self._get_mock_games(limit)
            
            with mysql_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT app_id, name, price, discount_percent, 
                           positive_ratio, user_reviews, release_date, updated_at
                    FROM steam_games 
                    WHERE updated_at IS NOT NULL
                    ORDER BY updated_at DESC 
                    LIMIT %s
                """, (limit,))
                games = cursor.fetchall()
                
                # 转换数据类型
                for game in games:
                    game['price'] = float(game['price'] or 0)
                    game['discount_percent'] = float(game['discount_percent'] or 0)
                    game['positive_ratio'] = float(game['positive_ratio'] or 0)
                    game['user_reviews'] = int(game['user_reviews'] or 0)
                    if game['release_date']:
                        game['release_date'] = game['release_date'].isoformat()
                    if game['updated_at']:
                        game['updated_at'] = game['updated_at'].isoformat()
                
                return games
        except Exception as e:
            logger.error(f"获取最新数据失败: {e}")
            return self._get_mock_games(limit)
    
    def _get_mock_summary(self) -> Dict[str, Any]:
        """获取模拟统计摘要"""
        return {
            'total_games': 15000,
            'paid_games': 12000,
            'free_games': 3000,
            'avg_price': 25.5,
            'avg_discount': 15.2,
            'last_update': datetime.now().isoformat()
        }
    
    def _get_mock_games(self, limit: int) -> List[Dict[str, Any]]:
        """获取模拟游戏数据"""
        games = []
        for i in range(min(limit, 10)):
            games.append({
                'app_id': 1000000 + i,
                'name': f'示例游戏 {i+1}',
                'price': 29.99 + i * 5,
                'discount_percent': 10 + i * 5,
                'positive_ratio': 85 + i,
                'user_reviews': 1000 + i * 100,
                'release_date': datetime.now().isoformat()
            })
        return games
    
    def _get_mock_price_distribution(self) -> Dict[str, int]:
        """获取模拟价格分布"""
        return {
            '免费': 3000,
            '0-10元': 4000,
            '10-50元': 5000,
            '50-100元': 2000,
            '100-200元': 800,
            '200元以上': 200
        }
    
    def _get_mock_genre_distribution(self) -> Dict[str, int]:
        """获取模拟游戏类型分布"""
        return {
            '动作': 2500,
            '冒险': 2000,
            '策略': 1800,
            '角色扮演': 1500,
            '模拟': 1200,
            '体育': 1000,
            '竞速': 800,
            '独立': 3000,
            '休闲': 1500,
            '其他': 700
        }
    
    def _get_mock_discount_analysis(self) -> Dict[str, Dict[str, Any]]:
        """获取模拟折扣分析"""
        return {
            '无折扣': {'count': 8000, 'avg_discount': 0},
            '1-25%': {'count': 3000, 'avg_discount': 15},
            '26-50%': {'count': 2500, 'avg_discount': 35},
            '51-75%': {'count': 1200, 'avg_discount': 60},
            '76-100%': {'count': 300, 'avg_discount': 85}
        }


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.redis_client = db_manager.get_redis_client()
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def set_cached_data(self, key: str, data: Any, timeout: int = 300) -> bool:
        """设置缓存数据"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.setex(key, timeout, json.dumps(data, default=str))
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def delete_cached_data(self, key: str) -> bool:
        """删除缓存数据"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """清空所有缓存"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False 