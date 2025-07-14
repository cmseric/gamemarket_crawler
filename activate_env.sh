#!/bin/bash

# 激活gamemarket_crawler环境
echo "正在激活gamemarket_crawler环境..."
conda activate gamemarket_crawler

# 显示当前环境信息
echo "当前Python环境: $(which python)"
echo "Python版本: $(python --version)"
echo "已安装的包:"
pip list | head -10

echo "环境激活完成！" 