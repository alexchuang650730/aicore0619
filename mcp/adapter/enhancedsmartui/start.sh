#!/bin/bash

# SmartUI Enhanced 启动脚本

echo "🚀 启动 SmartUI Enhanced 服务"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip3 install -r requirements.txt

# 创建日志目录
mkdir -p logs

# 启动服务
echo "🔧 启动主服务器..."
python3 main_server.py &
SERVER_PID=$!

echo "✅ SmartUI Enhanced 已启动"
echo "服务地址: http://localhost:5002"
echo "健康检查: http://localhost:5002/health"
echo "进程ID: $SERVER_PID"

# 保存PID到文件
echo $SERVER_PID > smartui_enhanced.pid

echo "使用 './stop.sh' 停止服务"

