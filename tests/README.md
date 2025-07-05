# MongoDB连接测试脚本

这个目录包含了多个用于测试MongoDB连接的脚本，适用于不同的使用场景。

## 📁 测试脚本列表

### 1. `test_mongodb_connection.py` - 完整功能测试脚本
**功能**: 最完整的MongoDB连接测试脚本，包含详细的日志记录和性能测试。

**特点**:
- 使用loguru进行结构化日志记录
- 包含连接测试、数据库操作测试、集合检查和性能测试
- 支持环境变量配置
- 自动创建日志目录和文件

**使用方法**:
```bash
python tests/test_mongodb_connection.py
```

### 2. `test_mongodb_local.py` - 本地MongoDB测试脚本
**功能**: 专门用于测试本地MongoDB连接的简化版本。

**特点**:
- 简化的输出格式
- 专注于本地连接测试
- 更快的超时设置

**使用方法**:
```bash
python tests/test_mongodb_local.py
```

### 3. `test_mongodb_docker.py` - Docker MongoDB测试脚本
**功能**: 自动启动Docker容器并测试MongoDB连接。

**特点**:
- 自动检查Docker可用性
- 自动创建和启动MongoDB容器
- 测试完成后自动清理容器
- 适合没有本地MongoDB安装的环境

**使用方法**:
```bash
python tests/test_mongodb_docker.py
```

### 4. `test_mongodb_simple.py` - 简单测试脚本（推荐）
**功能**: 最简单的MongoDB连接测试脚本，包含详细的安装指导。

**特点**:
- 清晰的输出格式
- 详细的安装和配置指导
- 环境变量检测
- 错误诊断和解决方案

**使用方法**:
```bash
python tests/test_mongodb_simple.py
```

## 🔧 环境配置

### 环境变量
- `MONGODB_URI`: MongoDB连接字符串（可选）
- `MONGODB_DATABASE`: 数据库名称（可选，默认为gamemarket）

### 默认配置
如果没有设置环境变量，脚本将使用以下默认值：
- 连接URI: `mongodb://localhost:27017`
- 数据库名: `gamemarket`

## 📋 测试内容

所有测试脚本都会执行以下测试：

1. **连接测试**: 验证MongoDB服务器连接
2. **数据库操作测试**: 
   - 插入文档
   - 查询文档
   - 更新文档
   - 删除文档
3. **集合检查**: 列出数据库中的所有集合
4. **性能测试** (仅完整版本): 测试连接延迟和批量操作性能

## 🚀 快速开始

### 方法1: 使用Docker（推荐）
```bash
# 1. 安装Docker Desktop
# 2. 启动Docker Desktop
# 3. 运行测试
python tests/test_mongodb_docker.py
```

### 方法2: 使用本地MongoDB
```bash
# 1. 安装MongoDB
# 2. 启动MongoDB服务
# 3. 运行测试
python tests/test_mongodb_simple.py
```

### 方法3: 使用MongoDB Atlas
```bash
# 1. 设置环境变量
export MONGODB_URI="your_atlas_connection_string"
export MONGODB_DATABASE="your_database_name"

# 2. 运行测试
python tests/test_mongodb_simple.py
```

## 📊 测试结果示例

### 成功测试
```
==================================================
🚀 开始测试MongoDB连接
==================================================
连接URI: mongodb://localhost:27017
数据库名: gamemarket

🔄 尝试连接MongoDB...
✅ MongoDB连接成功!
✅ 数据库 'gamemarket' 连接成功!

开始测试基本操作...
✅ 插入测试文档成功，ID: 60f1a2b3c4d5e6f7g8h9i0j1
✅ 查询测试文档成功
✅ 更新测试文档成功
✅ 删除测试文档成功
✅ 清理测试集合完成

📊 数据库中的集合: []

🔌 MongoDB连接已关闭

==================================================
🎉 所有测试都通过了!
==================================================
```

### 失败测试
```
❌ MongoDB连接失败: localhost:27017: [WinError 10061] 由于目标计算机积极拒绝，无法连接。

💡 可能的原因:
   1. MongoDB服务未启动
   2. 连接地址或端口错误
   3. 网络连接问题
   4. 防火墙阻止连接
```

## 🔍 故障排除

### 常见问题

1. **连接被拒绝**
   - 确保MongoDB服务正在运行
   - 检查端口27017是否被占用
   - 验证防火墙设置

2. **DNS解析超时**
   - 检查网络连接
   - 验证MongoDB Atlas连接字符串
   - 尝试使用IP地址而不是域名

3. **Docker相关错误**
   - 确保Docker Desktop正在运行
   - 检查Docker服务状态
   - 验证Docker权限

### 调试步骤

1. **检查MongoDB服务状态**
   ```bash
   # Windows
   netstat -an | findstr 27017
   
   # Linux/macOS
   sudo systemctl status mongod
   ```

2. **测试网络连接**
   ```bash
   # 测试端口连接
   telnet localhost 27017
   ```

3. **检查环境变量**
   ```bash
   # Windows
   echo %MONGODB_URI%
   
   # Linux/macOS
   echo $MONGODB_URI
   ```

## 📝 日志文件

测试脚本会在以下位置生成日志文件：
- `tests/logs/mongodb_test_YYYYMMDD.log` - 详细测试日志
- 控制台输出 - 实时测试结果

## 🤝 贡献

如果您发现任何问题或有改进建议，请：
1. 检查现有问题
2. 创建新的issue
3. 提交pull request

## 📄 许可证

本项目遵循MIT许可证。 