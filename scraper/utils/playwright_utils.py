#!/usr/bin/env python3
"""
Playwright 工具模块
提供浏览器自动化、截图、资源管理等功能
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page

class PlaywrightManager:
    """Playwright 管理器"""
    
    def __init__(self, resources_dir: str = "resources"):
        self.resources_dir = resources_dir
        self.browser = None
        self.page = None
        self._ensure_resources_dir()
    
    def _ensure_resources_dir(self):
        """确保资源目录存在"""
        if not os.path.exists(self.resources_dir):
            os.makedirs(self.resources_dir)
            print(f"📁 创建资源目录: {self.resources_dir}")
    
    def get_screenshot_path(self, page_name: str, browser_name: str = "firefox") -> str:
        """生成截图文件路径"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{page_name}_{browser_name}_{timestamp}.png"
        return os.path.join(self.resources_dir, filename)
    
    async def take_screenshot(self, page: Page, page_name: str, browser_name: str = "firefox") -> str:
        """通用截图函数"""
        screenshot_path = self.get_screenshot_path(page_name, browser_name)
        await page.screenshot(path=screenshot_path)
        print(f"📸 截图已保存: {screenshot_path}")
        return screenshot_path
    
    async def launch_browser(self, browser_type: str = "firefox", headless: bool = True) -> Browser:
        """启动浏览器"""
        playwright = await async_playwright().start()
        
        if browser_type.lower() == "firefox":
            self.browser = await playwright.firefox.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
        elif browser_type.lower() == "webkit":
            self.browser = await playwright.webkit.launch(headless=headless)
        elif browser_type.lower() == "chromium":
            self.browser = await playwright.chromium.launch(
                headless=headless,
                args=['--no-sandbox']
            )
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
        
        return self.browser
    
    async def create_page(self) -> Page:
        """创建新页面"""
        if not self.browser:
            raise RuntimeError("请先启动浏览器")
        
        self.page = await self.browser.new_page()
        return self.page
    
    async def navigate_and_screenshot(self, url: str, page_name: str, 
                                    browser_type: str = "firefox", 
                                    timeout: int = 10000) -> Dict[str, Any]:
        """导航到页面并截图"""
        try:
            # 启动浏览器
            await self.launch_browser(browser_type)
            
            # 创建页面
            page = await self.create_page()
            
            # 导航到页面
            print(f"🌐 访问页面: {url}")
            await page.goto(url, timeout=timeout)
            
            # 获取页面信息
            title = await page.title()
            print(f"✅ 页面标题: {title}")
            
            # 截图
            screenshot_path = await self.take_screenshot(page, page_name, browser_type)
            
            return {
                "success": True,
                "title": title,
                "screenshot_path": screenshot_path,
                "url": url
            }
            
        except Exception as e:
            print(f"❌ 页面访问失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
        
        finally:
            await self.close()
    
    async def close(self):
        """关闭浏览器"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()

async def test_playwright_manager():
    """测试 PlaywrightManager"""
    print("🧪 测试 PlaywrightManager...")
    
    manager = PlaywrightManager()
    
    # 测试不同浏览器
    browsers = ["firefox", "webkit", "chromium"]
    
    for browser in browsers:
        print(f"\n🔄 测试 {browser}...")
        result = await manager.navigate_and_screenshot(
            url="https://www.baidu.com",
            page_name="test",
            browser_type=browser
        )
        
        if result["success"]:
            print(f"✅ {browser} 测试成功")
        else:
            print(f"❌ {browser} 测试失败: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    asyncio.run(test_playwright_manager()) 