#!/bin/bash

echo "启动项目识别智能评分系统..."

# 检查Python版本
python --version

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 创建必要的目录
mkdir -p backend/logs
mkdir -p backend/database

# 启动应用
echo "启动FastAPI服务器..."
cd backend
python app_simple.py