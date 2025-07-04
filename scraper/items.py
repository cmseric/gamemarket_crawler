# -*- coding: utf-8 -*-
"""
数据项定义
"""

import scrapy
from scrapy import Field


class SteamGameItem(scrapy.Item):
    """Steam游戏数据项"""
    # 基本信息
    name = Field()                    # 游戏名称
    app_id = Field()                  # Steam应用ID
    price = Field()                   # 当前价格
    original_price = Field()          # 原价
    discount_percent = Field()        # 折扣百分比
    
    # 统计数据
    peak_players = Field()            # 峰值在线人数
    current_players = Field()         # 当前在线人数
    positive_rate = Field()           # 好评率
    total_reviews = Field()           # 总评论数
    
    # 详细信息
    developer = Field()               # 开发商
    publisher = Field()               # 发行商
    release_date = Field()            # 发行日期
    genres = Field()                  # 游戏类型
    tags = Field()                    # 标签
    
    # 系统信息
    crawl_time = Field()              # 爬取时间
    crawl_date = Field()              # 爬取日期


class MobileGameItem(scrapy.Item):
    """手游数据项"""
    # 基本信息
    name = Field()                    # 游戏名称
    package_name = Field()            # 包名
    price = Field()                   # 价格
    currency = Field()                # 货币单位
    
    # 统计数据
    downloads = Field()               # 下载量
    rating = Field()                  # 评分
    rating_count = Field()            # 评分数量
    iap_avg = Field()                 # 内购平均收入
    
    # 详细信息
    developer = Field()               # 开发商
    publisher = Field()               # 发行商
    release_date = Field()            # 发行日期
    category = Field()                # 分类
    size = Field()                    # 应用大小
    
    # 平台信息
    platform = Field()                # 平台 (iOS/Android)
    store = Field()                   # 商店 (AppStore/GooglePlay/TapTap)
    
    # 系统信息
    crawl_time = Field()              # 爬取时间
    crawl_date = Field()              # 爬取日期


class GameReviewItem(scrapy.Item):
    """游戏评论数据项"""
    # 评论信息
    review_id = Field()               # 评论ID
    game_id = Field()                 # 游戏ID
    game_name = Field()               # 游戏名称
    platform = Field()                # 平台
    
    # 用户信息
    user_id = Field()                 # 用户ID (脱敏)
    user_name = Field()               # 用户名 (脱敏)
    
    # 评论内容
    rating = Field()                  # 评分
    title = Field()                   # 评论标题
    content = Field()                 # 评论内容
    helpful_count = Field()           # 有用数量
    
    # 情感分析
    sentiment_score = Field()         # 情感得分
    sentiment_label = Field()         # 情感标签 (positive/negative/neutral)
    keywords = Field()                # 关键词
    
    # 时间信息
    review_date = Field()             # 评论日期
    crawl_time = Field()              # 爬取时间 