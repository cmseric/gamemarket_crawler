#!/usr/bin/env python3
"""
简单的Playwright测试脚本
用于验证浏览器自动化功能
"""

import asyncio
import sys
import os
from datetime import datetime
from playwright.async_api import async_playwright

def ensure_resources_dir():
    """确保resources目录存在"""
    resources_dir = "resources"
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
        print(f"📁 创建资源目录: {resources_dir}")
    return resources_dir

def get_screenshot_path(browser_name, page_name="page"):
    """生成截图文件路径"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{page_name}_{browser_name}_{timestamp}.png"
    return os.path.join("resources", filename)

async def take_screenshot(page, browser_name, page_name="page"):
    """通用截图函数"""
    screenshot_path = get_screenshot_path(browser_name, page_name)
    await page.screenshot(path=screenshot_path)
    print(f"📸 截图已保存: {screenshot_path}")
    return screenshot_path

async def test_with_firefox():
    """使用Firefox进行测试 - 更稳定"""
    print("🧪 使用Firefox进行Playwright测试...")
    
    # 确保资源目录存在
    ensure_resources_dir()
    
    try:
        async with async_playwright() as p:
            # 使用Firefox，通常更稳定
            browser = await p.firefox.launch(
                headless=True,  # 无头模式更稳定
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            page = await browser.new_page()
            
            try:
                # 访问一个简单的页面
                print("🌐 访问百度首页...")
                await page.goto('https://www.baidu.com/', timeout=10000)
                
                # 获取页面标题
                title = await page.title()
                print(f"✅ 页面标题: {title}")
                
                # 使用通用截图函数
                await take_screenshot(page, "firefox", "baidu")
                
                return True
                
            except Exception as e:
                print(f"❌ Firefox测试过程中出错: {e}")
                return False
            
            finally:
                await browser.close()
        
    except Exception as e:
        print(f"💥 Firefox测试失败: {e}")
        return False

async def test_with_webkit():
    """使用WebKit进行测试 - 备选方案"""
    print("🧪 使用WebKit进行Playwright测试...")
    
    # 确保资源目录存在
    ensure_resources_dir()
    
    try:
        async with async_playwright() as p:
            # 使用WebKit
            browser = await p.webkit.launch(
                headless=True
            )
            page = await browser.new_page()
            
            try:
                # 访问一个简单的页面
                print("🌐 访问百度首页...")
                await page.goto('https://www.baidu.com/', timeout=10000)
                
                # 获取页面标题
                title = await page.title()
                print(f"✅ 页面标题: {title}")
                
                # 使用通用截图函数
                await take_screenshot(page, "webkit", "baidu")
                
                return True
                
            except Exception as e:
                print(f"❌ WebKit测试过程中出错: {e}")
                return False
            
            finally:
                await browser.close()
        
    except Exception as e:
        print(f"💥 WebKit测试失败: {e}")
        return False

async def test_minimal_chromium():
    """最小化Chromium测试"""
    print("🧪 尝试最小化Chromium测试...")
    
    # 确保资源目录存在
    ensure_resources_dir()
    
    try:
        async with async_playwright() as p:
            # 使用最简单的配置
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            page = await browser.new_page()
            
            try:
                # 访问一个简单的页面
                print("🌐 访问百度首页...")
                await page.goto('https://www.baidu.com/', timeout=10000)
                
                # 获取页面标题
                title = await page.title()
                print(f"✅ 页面标题: {title}")
                
                # 使用通用截图函数
                await take_screenshot(page, "chromium", "baidu")
                
                return True
                
            except Exception as e:
                print(f"❌ Chromium测试过程中出错: {e}")
                return False
            
            finally:
                await browser.close()
        
    except Exception as e:
        print(f"💥 Chromium测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Playwright兼容性测试...")
    
    # 按优先级尝试不同的浏览器引擎
    browsers = [
        ("Firefox", test_with_firefox),
        ("WebKit", test_with_webkit),
        ("Chromium", test_minimal_chromium)
    ]
    
    for browser_name, test_func in browsers:
        print(f"\n🔄 尝试使用 {browser_name}...")
        try:
            success = await test_func()
            if success:
                print(f"🎉 {browser_name} 测试成功！")
                return
            else:
                print(f"❌ {browser_name} 测试失败")
        except Exception as e:
            print(f"💥 {browser_name} 测试异常: {e}")
    
    print("\n💥 所有浏览器引擎都失败了")
    print("💡 建议:")
    print("1. 重新安装Playwright: playwright install")
    print("2. 检查系统权限")
    print("3. 尝试使用不同的浏览器引擎")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n💥 测试过程中发生未预期的错误: {e}")
        print("💡 请检查Playwright安装: playwright install") 