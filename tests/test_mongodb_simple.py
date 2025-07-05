#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单MongoDB连接测试脚本
包含详细的安装和配置指导
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def print_installation_guide():
    """打印安装指导"""
    print("=" * 60)
    print("📋 MongoDB安装和配置指导")
    print("=" * 60)
    print()
    print("🔧 方法1: 使用Docker (推荐)")
    print("   1. 安装Docker Desktop: https://www.docker.com/products/docker-desktop")
    print("   2. 启动Docker Desktop")
    print("   3. 运行命令: docker run -d -p 27017:27017 --name mongodb-test mongo:latest")
    print("   4. 验证容器运行: docker ps")
    print()
    print("🔧 方法2: 直接安装MongoDB")
    print("   Windows:")
    print("   1. 下载MongoDB Community Server: https://www.mongodb.com/try/download/community")
    print("   2. 安装并启动MongoDB服务")
    print("   3. 验证服务运行: netstat -an | findstr 27017")
    print()
    print("   Linux (Ubuntu/Debian):")
    print("   1. sudo apt update")
    print("   2. sudo apt install mongodb")
    print("   3. sudo systemctl start mongod")
    print("   4. sudo systemctl enable mongod")
    print()
    print("   macOS:")
    print("   1. brew install mongodb-community")
    print("   2. brew services start mongodb-community")
    print()
    print("🔧 方法3: 使用MongoDB Atlas (云服务)")
    print("   1. 注册MongoDB Atlas: https://www.mongodb.com/atlas")
    print("   2. 创建免费集群")
    print("   3. 获取连接字符串")
    print("   4. 设置环境变量: MONGODB_URI=your_connection_string")
    print()
    print("=" * 60)


def test_mongodb_connection():
    """测试MongoDB连接"""
    print("=" * 50)
    print("🚀 开始测试MongoDB连接")
    print("=" * 50)
    
    # 连接配置
    uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    database_name = os.getenv('MONGODB_DATABASE', 'gamemarket')
    
    print(f"连接URI: {uri}")
    print(f"数据库名: {database_name}")
    print()
    
    try:
        # 创建客户端连接
        print("🔄 尝试连接MongoDB...")
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,  # 5秒超时
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB连接成功!")
        
        # 获取数据库
        db = client[database_name]
        print(f"✅ 数据库 '{database_name}' 连接成功!")
        
        # 测试基本操作
        print("\n开始测试基本操作...")
        
        # 测试集合操作
        collection_name = "test_collection"
        collection = db[collection_name]
        
        # 测试插入
        test_doc = {
            "test_field": "test_value",
            "timestamp": datetime.now(),
            "test_type": "simple_connection_test",
            "description": "这是一个测试文档"
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ 插入测试文档成功，ID: {result.inserted_id}")
        
        # 测试查询
        found_doc = collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ 查询测试文档成功")
            print(f"   文档内容: {found_doc}")
        else:
            print("❌ 查询测试文档失败")
            return False
        
        # 测试更新
        update_result = collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"test_field": "updated_value", "updated_at": datetime.now()}}
        )
        if update_result.modified_count > 0:
            print("✅ 更新测试文档成功")
        else:
            print("❌ 更新测试文档失败")
            return False
        
        # 测试删除
        delete_result = collection.delete_one({"_id": result.inserted_id})
        if delete_result.deleted_count > 0:
            print("✅ 删除测试文档成功")
        else:
            print("❌ 删除测试文档失败")
            return False
        
        # 清理测试集合
        db.drop_collection(collection_name)
        print("✅ 清理测试集合完成")
        
        # 检查现有集合
        collections = db.list_collection_names()
        print(f"\n📊 数据库中的集合: {collections}")
        
        if collections:
            for collection_name in collections:
                collection = db[collection_name]
                count = collection.count_documents({})
                print(f"  - {collection_name}: {count} 条文档")
        else:
            print("📊 数据库中没有集合")
        
        # 关闭连接
        client.close()
        print("\n🔌 MongoDB连接已关闭")
        
        print("\n" + "=" * 50)
        print("🎉 所有测试都通过了!")
        print("=" * 50)
        
        return True
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ MongoDB连接失败: {e}")
        print("\n💡 可能的原因:")
        print("   1. MongoDB服务未启动")
        print("   2. 连接地址或端口错误")
        print("   3. 网络连接问题")
        print("   4. 防火墙阻止连接")
        return False
        
    except Exception as e:
        print(f"❌ 连接测试出现未知错误: {e}")
        return False


def main():
    """主函数"""
    print("🔍 MongoDB连接测试工具")
    print("这个工具将测试MongoDB连接和基本操作")
    print()
    
    # 检查环境变量
    mongodb_uri = os.getenv('MONGODB_URI')
    if mongodb_uri:
        print(f"✅ 检测到环境变量 MONGODB_URI: {mongodb_uri}")
    else:
        print("ℹ️  未设置 MONGODB_URI 环境变量，将使用默认值: mongodb://localhost:27017")
    
    print()
    
    # 运行测试
    success = test_mongodb_connection()
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ 测试失败，请参考以下安装指导:")
        print("=" * 60)
        print_installation_guide()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 