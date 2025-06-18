#!/bin/bash

# SmartUI Enhanced 停止脚本

echo "🛑 停止 SmartUI Enhanced 服务"
echo "=================================="

# 检查PID文件
if [ -f "smartui_enhanced.pid" ]; then
    PID=$(cat smartui_enhanced.pid)
    
    if ps -p $PID > /dev/null; then
        echo "停止进程 $PID..."
        kill $PID
        
        # 等待进程结束
        sleep 2
        
        if ps -p $PID > /dev/null; then
            echo "强制停止进程..."
            kill -9 $PID
        fi
        
        echo "✅ 服务已停止"
    else
        echo "⚠️ 进程 $PID 不存在"
    fi
    
    # 删除PID文件
    rm smartui_enhanced.pid
else
    echo "⚠️ 未找到PID文件，尝试查找进程..."
    
    # 查找并停止相关进程
    pkill -f "main_server.py"
    
    if [ $? -eq 0 ]; then
        echo "✅ 已停止相关进程"
    else
        echo "⚠️ 未找到运行中的服务"
    fi
fi

echo "SmartUI Enhanced 服务已停止"

