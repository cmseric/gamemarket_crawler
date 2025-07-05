#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地MongoDB连接测试脚本
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def test_mongodb_connection():
    """测试本地MongoDB连接"""
    print("=" * 50)
    print("🚀 开始测试本地MongoDB连接")
    print("=" * 50)
    
    # 连接配置
    uri = "mongodb://localhost:27017"
    database_name = "gamemarket"
    
    print(f"连接URI: {uri}")
    print(f"数据库名: {database_name}")
    
    try:
        # 创建客户端连接
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=3000,  # 3秒超时
            connectTimeoutMS=3000,
            socketTimeoutMS=3000
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
            "test_type": "connection_test"
        }
        
        result = collection.insert_one(test_doc)
        print(f"✅ 插入测试文档成功，ID: {result.inserted_id}")
        
        # 测试查询
        found_doc = collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ 查询测试文档成功")
        else:
            print("❌ 查询测试文档失败")
            return False
        
        # 测试更新
        update_result = collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"test_field": "updated_value"}}
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
        print("\n💡 请确保MongoDB服务正在运行:")
        print("   - Windows: 启动MongoDB服务")
        print("   - Linux/Mac: sudo systemctl start mongod")
        print("   - Docker: docker run -d -p 27017:27017 mongo:latest")
        return False
        
    except Exception as e:
        print(f"❌ 连接测试出现未知错误: {e}")
        return False


def main():
    """主函数"""
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 