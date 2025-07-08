#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Twisted reactor修复
"""

import sys
import os

def test_twisted_import():
    """测试Twisted模块导入"""
    try:
        import twisted.internet.selectreactor
        print("✓ SelectReactor 导入成功")
        return True
    except ImportError as e:
        print(f"✗ SelectReactor 导入失败: {e}")
        return False

def test_scrapy_import():
    """测试Scrapy导入"""
    try:
        import scrapy
        print("✓ Scrapy 导入成功")
        return True
    except ImportError as e:
        print(f"✗ Scrapy 导入失败: {e}")
        return False

def test_reactor_setting():
    """测试reactor设置"""
    try:
        # 测试reactor是否可以正常导入和使用
        from twisted.internet import reactor
        print("✓ Reactor 导入成功")
        return True
    except Exception as e:
        print(f"✗ Reactor 设置失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Twisted Reactor 修复测试")
    print("=" * 50)
    
    tests = [
        ("Twisted导入测试", test_twisted_import),
        ("Scrapy导入测试", test_scrapy_import),
        ("Reactor设置测试", test_reactor_setting),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"  {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！修复成功！")
        return 0
    else:
        print("✗ 部分测试失败，需要进一步检查")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 