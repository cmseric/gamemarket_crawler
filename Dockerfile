FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install
RUN playwright install firefox
RUN playwright install webkit
RUN playwright install chromium

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/{logs,export,resources}

# 创建非root用户
RUN useradd -m -u 1000 crawler
RUN chown -R crawler:crawler /app
USER crawler

# 暴露端口（如果需要Web界面）
EXPOSE 8000

# 启动命令
CMD ["python", "run_crawler.py"] 