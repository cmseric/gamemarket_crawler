# -*- coding: utf-8 -*-
"""
数据清洗管道
"""

import re
from datetime import datetime
from scrapy.exceptions import DropItem


class DataCleaningPipeline:
    """数据清洗管道"""
    
    def process_item(self, item, spider):
        """清洗数据项"""
        # 清理字符串字段
        for field in item.fields:
            if field in item and isinstance(item[field], str):
                item[field] = self._clean_string(item[field])
        
        # 验证必要字段
        if not self._validate_required_fields(item):
            raise DropItem(f"缺少必要字段: {item}")
        
        # 数据格式化
        self._format_data(item)
        
        return item
    
    def _clean_string(self, text):
        """清理字符串"""
        if not text:
            return text
        
        # 去除首尾空白
        text = text.strip()
        
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff\-\.\,\!\?\(\)\[\]\{\}]', '', text)
        
        return text
    
    def _validate_required_fields(self, item):
        """验证必要字段"""
        required_fields = ['name', 'crawl_time', 'crawl_date']
        
        for field in required_fields:
            if field not in item or not item[field]:
                return False
        
        return True
    
    def _format_data(self, item):
        """格式化数据"""
        # 格式化价格
        if 'price' in item and item['price']:
            item['price'] = self._format_price(item['price'])
        
        # 格式化数字字段
        numeric_fields = ['peak_players', 'current_players', 'positive_rate', 'total_reviews']
        for field in numeric_fields:
            if field in item and item[field]:
                item[field] = self._format_number(item[field])
        
        # 格式化日期
        if 'release_date' in item and item['release_date']:
            item['release_date'] = self._format_date(item['release_date'])
    
    def _format_price(self, price_str):
        """格式化价格"""
        if not price_str:
            return price_str
        
        # 提取数字
        match = re.search(r'[\d,]+\.?\d*', price_str)
        if match:
            return match.group()
        
        return price_str
    
    def _format_number(self, num_str):
        """格式化数字"""
        if not num_str:
            return num_str
        
        # 提取数字
        match = re.search(r'[\d,]+', str(num_str))
        if match:
            return match.group().replace(',', '')
        
        return num_str
    
    def _format_date(self, date_str):
        """格式化日期"""
        if not date_str:
            return date_str
        
        # 尝试解析常见日期格式
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return date_str 