#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker MongoDB连接测试脚本
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


def check_docker_available():
    """检查Docker是否可用"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker可用")
            return True
        else:
            print("❌ Docker不可用")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker未安装或不可用")
        return False


def start_mongodb_container():
    """启动MongoDB容器"""
    container_name = "mongodb-test"
    
    # 检查容器是否已存在
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--filter', f'name={container_name}'],
                              capture_output=True, text=True, timeout=10)
        
        if container_name in result.stdout:
            # 容器已存在，启动它
            print(f"🔄 启动现有容器: {container_name}")
            subprocess.run(['docker', 'start', container_name], check=True)
        else:
            # 创建新容器
            print(f"🔄 创建并启动MongoDB容器: {container_name}")
            subprocess.run([
                'docker', 'run', '-d',
                '--name', container_name,
                '-p', '27017:27017',
                'mongo:latest'
            ], check=True)
        
        # 等待容器启动
        print("⏳ 等待MongoDB服务启动...")
        time.sleep(5)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动MongoDB容器失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动容器时出现错误: {e}")
        return False


def stop_mongodb_container():
    """停止MongoDB容器"""
    container_name = "mongodb-test"
    
    try:
        print(f"🔄 停止MongoDB容器: {container_name}")
        subprocess.run(['docker', 'stop', container_name], check=True)
        print("✅ MongoDB容器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 停止容器失败: {e}")
    except Exception as e:
        print(f"❌ 停止容器时出现错误: {e}")


def test_mongodb_connection():
    """测试MongoDB连接"""
    print("=" * 50)
    print("🚀 开始测试Docker MongoDB连接")
    print("=" * 50)
    
    # 检查Docker
    if not check_docker_available():
        print("\n💡 请安装Docker Desktop或确保Docker服务正在运行")
        return False
    
    # 启动MongoDB容器
    if not start_mongodb_container():
        return False
    
    # 连接配置
    uri = "mongodb://localhost:27017"
    database_name = "gamemarket"
    
    print(f"\n连接URI: {uri}")
    print(f"数据库名: {database_name}")
    
    try:
        # 创建客户端连接
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=10000,  # 10秒超时
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
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
            "test_type": "docker_connection_test"
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
        print("\n💡 请检查Docker容器是否正常启动")
        return False
        
    except Exception as e:
        print(f"❌ 连接测试出现未知错误: {e}")
        return False
    finally:
        # 停止容器
        stop_mongodb_container()


def main():
    """主函数"""
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 