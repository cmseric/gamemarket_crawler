#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB连接测试脚本
"""

import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from loguru import logger


class MongoDBConnectionTester:
    """MongoDB连接测试器"""
    
    def __init__(self, uri=None, database=None):
        """初始化测试器"""
        self.uri = uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.database_name = database or os.getenv('MONGODB_DATABASE', 'gamemarket')
        self.client = None
        self.db = None
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志配置"""
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            f"tests/logs/mongodb_test_{datetime.now().strftime('%Y%m%d')}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
            level="DEBUG",
            rotation="1 day",
            retention="7 days"
        )
    
    def test_connection(self):
        """测试MongoDB连接"""
        logger.info("开始测试MongoDB连接...")
        logger.info(f"连接URI: {self.uri}")
        logger.info(f"数据库名: {self.database_name}")
        
        try:
            # 创建客户端连接
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,  # 5秒超时
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # 测试连接
            self.client.admin.command('ping')
            logger.success("✅ MongoDB连接成功!")
            
            # 获取数据库
            self.db = self.client[self.database_name]
            logger.info(f"✅ 数据库 '{self.database_name}' 连接成功!")
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB连接失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 连接测试出现未知错误: {e}")
            return False
    
    def test_database_operations(self):
        """测试数据库操作"""
        if self.db is None:
            logger.error("❌ 数据库未连接，无法进行操作测试")
            return False
        
        logger.info("开始测试数据库操作...")
        
        try:
            # 测试集合操作
            collection_name = "test_collection"
            collection = self.db[collection_name]
            
            # 测试插入操作
            test_doc = {
                "test_field": "test_value",
                "timestamp": datetime.now(),
                "test_type": "connection_test"
            }
            
            result = collection.insert_one(test_doc)
            logger.success(f"✅ 插入测试文档成功，ID: {result.inserted_id}")
            
            # 测试查询操作
            found_doc = collection.find_one({"_id": result.inserted_id})
            if found_doc:
                logger.success("✅ 查询测试文档成功")
            else:
                logger.error("❌ 查询测试文档失败")
                return False
            
            # 测试更新操作
            update_result = collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"test_field": "updated_value"}}
            )
            if update_result.modified_count > 0:
                logger.success("✅ 更新测试文档成功")
            else:
                logger.error("❌ 更新测试文档失败")
                return False
            
            # 测试删除操作
            delete_result = collection.delete_one({"_id": result.inserted_id})
            if delete_result.deleted_count > 0:
                logger.success("✅ 删除测试文档成功")
            else:
                logger.error("❌ 删除测试文档失败")
                return False
            
            # 清理测试集合
            self.db.drop_collection(collection_name)
            logger.info("✅ 清理测试集合完成")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库操作测试失败: {e}")
            return False
    
    def test_collections(self):
        """测试现有集合"""
        if self.db is None:
            logger.error("❌ 数据库未连接，无法检查集合")
            return False
        
        try:
            collections = self.db.list_collection_names()
            logger.info(f"📊 数据库中的集合: {collections}")
            
            if collections:
                for collection_name in collections:
                    collection = self.db[collection_name]
                    count = collection.count_documents({})
                    logger.info(f"  - {collection_name}: {count} 条文档")
            else:
                logger.info("📊 数据库中没有集合")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 检查集合失败: {e}")
            return False
    
    def test_performance(self):
        """测试连接性能"""
        if self.db is None:
            logger.error("❌ 数据库未连接，无法进行性能测试")
            return False
        
        logger.info("开始性能测试...")
        
        try:
            # 测试连接延迟
            start_time = time.time()
            self.db.command('ping')
            ping_time = (time.time() - start_time) * 1000
            logger.info(f"⏱️ 连接延迟: {ping_time:.2f}ms")
            
            # 测试批量插入性能
            test_collection = self.db["performance_test"]
            test_docs = []
            
            for i in range(100):
                test_docs.append({
                    "index": i,
                    "data": f"test_data_{i}",
                    "timestamp": datetime.now()
                })
            
            start_time = time.time()
            result = test_collection.insert_many(test_docs)
            insert_time = time.time() - start_time
            
            logger.info(f"⏱️ 批量插入100条文档耗时: {insert_time:.3f}秒")
            logger.info(f"⏱️ 平均每条文档: {(insert_time/100)*1000:.2f}ms")
            
            # 测试查询性能
            start_time = time.time()
            count = test_collection.count_documents({})
            query_time = time.time() - start_time
            
            logger.info(f"⏱️ 查询文档数量耗时: {query_time:.3f}秒")
            logger.info(f"📊 实际文档数量: {count}")
            
            # 清理测试数据
            test_collection.drop()
            logger.info("✅ 清理性能测试数据完成")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 性能测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 50)
        logger.info("🚀 开始MongoDB连接测试")
        logger.info("=" * 50)
        
        # 创建日志目录
        os.makedirs("tests/logs", exist_ok=True)
        
        test_results = {}
        
        # 测试1: 连接测试
        test_results['connection'] = self.test_connection()
        
        if test_results['connection']:
            # 测试2: 数据库操作测试
            test_results['operations'] = self.test_database_operations()
            
            # 测试3: 集合检查
            test_results['collections'] = self.test_collections()
            
            # 测试4: 性能测试
            test_results['performance'] = self.test_performance()
        
        # 输出测试结果
        logger.info("=" * 50)
        logger.info("📋 测试结果汇总")
        logger.info("=" * 50)
        
        for test_name, result in test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            logger.info(f"{test_name}: {status}")
        
        # 关闭连接
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB连接已关闭")
        
        # 计算总体结果
        all_passed = all(test_results.values())
        if all_passed:
            logger.success("🎉 所有测试都通过了!")
        else:
            logger.error("💥 部分测试失败，请检查MongoDB配置")
        
        return all_passed


def main():
    """主函数"""
    # 创建测试器实例
    tester = MongoDBConnectionTester()
    
    # 运行所有测试
    success = tester.run_all_tests()
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 