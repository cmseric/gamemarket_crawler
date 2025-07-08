import scrapy

class TestSpider(scrapy.Spider):
    name = "test"
    start_urls = ["https://example.com"]
    
    def parse(self, response):
        self.log(f"成功访问: {response.url}") 