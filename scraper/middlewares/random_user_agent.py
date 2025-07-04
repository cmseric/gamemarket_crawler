# -*- coding: utf-8 -*-
"""
随机User-Agent中间件
"""

import random
import os
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgentMiddleware(UserAgentMiddleware):
    """随机User-Agent中间件"""
    
    def __init__(self, user_agent_list_file=None):
        super().__init__()
        self.user_agent_list_file = user_agent_list_file or 'config/user_agents.txt'
        self.user_agents = self._load_user_agents()
    
    def _load_user_agents(self):
        """加载User-Agent列表"""
        user_agents = []
        try:
            if os.path.exists(self.user_agent_list_file):
                with open(self.user_agent_list_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            user_agents.append(line)
        except Exception as e:
            print(f"加载User-Agent文件失败: {e}")
        
        # 如果没有加载到User-Agent，使用默认的
        if not user_agents:
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        
        return user_agents
    
    def process_request(self, request, spider):
        """处理请求，设置随机User-Agent"""
        if self.user_agents:
            request.headers['User-Agent'] = random.choice(self.user_agents)
    
    @classmethod
    def from_crawler(cls, crawler):
        """从爬虫设置中创建中间件实例"""
        user_agent_list_file = crawler.settings.get('USER_AGENT_LIST_FILE')
        middleware = cls(user_agent_list_file)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
    
    def spider_opened(self, spider):
        """爬虫开启时的回调"""
        spider.logger.info(f'使用随机User-Agent中间件，共加载 {len(self.user_agents)} 个User-Agent') 