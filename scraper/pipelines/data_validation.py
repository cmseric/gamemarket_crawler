# -*- coding: utf-8 -*-
"""
数据验证管道
"""

import re
from datetime import datetime
from scrapy.exceptions import DropItem
from loguru import logger


class DataValidationPipeline:
    """数据验证管道"""
    
    def __init__(self):
        """初始化验证器"""
        self.required_fields = {
            'steam_top_sellers': ['name', 'app_id', 'crawl_time', 'crawl_date'],
            'steam_popular': ['name', 'app_id', 'crawl_time', 'crawl_date'],
        }
        
        self.field_validators = {
            'name': self._validate_name,
            'app_id': self._validate_app_id,
            'price': self._validate_price,
            'discount_percent': self._validate_discount,
            'positive_rate': self._validate_positive_rate,
            'total_reviews': self._validate_reviews,
            'crawl_time': self._validate_datetime,
            'crawl_date': self._validate_date,
        }
    
    def process_item(self, item, spider):
        """验证数据项"""
        try:
            # 获取爬虫特定的必填字段
            required_fields = self.required_fields.get(spider.name, ['name', 'crawl_time', 'crawl_date'])
            
            # 验证必填字段
            for field in required_fields:
                if not self._validate_required_field(item, field):
                    raise DropItem(f"缺少必填字段: {field}")
            
            # 验证字段格式
            for field, value in item.items():
                if field in self.field_validators and value is not None:
                    if not self.field_validators[field](value):
                        logger.warning(f"字段 {field} 格式无效: {value}")
                        # 对于非关键字段，只记录警告，不丢弃数据
                        if field in required_fields:
                            raise DropItem(f"字段 {field} 格式无效: {value}")
            
            logger.debug(f"数据验证通过: {item.get('name', 'Unknown')}")
            return item
            
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            raise DropItem(f"数据验证失败: {e}")
    
    def _validate_required_field(self, item, field):
        """验证必填字段是否存在且不为空"""
        return field in item and item[field] is not None and str(item[field]).strip() != ''
    
    def _validate_name(self, value):
        """验证游戏名称"""
        if not isinstance(value, str):
            return False
        return len(value.strip()) >= 1 and len(value.strip()) <= 200
    
    def _validate_app_id(self, value):
        """验证Steam应用ID"""
        if not isinstance(value, str):
            return False
        return bool(re.match(r'^\d+$', str(value)))
    
    def _validate_price(self, value):
        """验证价格格式"""
        if not isinstance(value, str):
            return False
        # 支持免费、价格、折扣价格等格式
        price_patterns = [
            r'^免费$',
            r'^¥\s*\d+(\.\d{2})?$',
            r'^\$\s*\d+(\.\d{2})?$',
            r'^\d+(\.\d{2})?\s*元$',
            r'^\d+(\.\d{2})?\s*USD$',
        ]
        return any(re.match(pattern, value.strip()) for pattern in price_patterns)
    
    def _validate_discount(self, value):
        """验证折扣百分比"""
        if not isinstance(value, str):
            return False
        try:
            discount = int(value)
            return 0 <= discount <= 100
        except ValueError:
            return False
    
    def _validate_positive_rate(self, value):
        """验证好评率"""
        if not isinstance(value, str):
            return False
        try:
            rate = int(value)
            return 0 <= rate <= 100
        except ValueError:
            return False
    
    def _validate_reviews(self, value):
        """验证评论数量"""
        if not isinstance(value, str):
            return False
        try:
            reviews = int(value.replace(',', ''))
            return reviews >= 0
        except ValueError:
            return False
    
    def _validate_datetime(self, value):
        """验证日期时间格式"""
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def _validate_date(self, value):
        """验证日期格式"""
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False 