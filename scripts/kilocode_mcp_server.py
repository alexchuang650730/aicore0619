#!/usr/bin/env python3
"""
KiloCode MCP 服务启动器
在98.81.255.168:8080提供服务
"""

import sys
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# 添加adapter路径
sys.path.append('/opt/powerautomation/shared_core/mcptool/adapters/kilocode_mcp_v2')

try:
    from kilocode_mcp import KiloCodeMCP
    print("✅ 成功导入KiloCode MCP")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    # 使用本地版本
    sys.path.append('/home/ubuntu/adapter/kilocode_mcp')
    from kilocode_mcp import KiloCodeMCP
    print("✅ 使用本地版本KiloCode MCP")

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 初始化KiloCode MCP
kilocode_mcp = KiloCodeMCP()

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return jsonify({
        "service": "KiloCode MCP",
        "version": kilocode_mcp.version,
        "status": "running",
        "ip": "98.81.255.168",
        "port": 8080,
        "endpoints": {
            "health": "/health",
            "create": "/create", 
            "capabilities": "/capabilities",
            "test": "/test"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "service": "KiloCode MCP",
        "status": "healthy",
        "version": kilocode_mcp.version,
        "ip": "98.81.255.168",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    """获取能力信息"""
    try:
        capabilities = kilocode_mcp.get_capabilities()
        routing_info = kilocode_mcp.get_routing_info()
        
        return jsonify({
            "success": True,
            "capabilities": capabilities,
            "routing_info": routing_info,
            "service_info": {
                "name": kilocode_mcp.name,
                "version": kilocode_mcp.version,
                "ip": "98.81.255.168",
                "port": 8080
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/create', methods=['POST'])
def create_fallback():
    """兜底创建接口"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "success": False,
                "error": "请提供JSON格式的请求数据"
            }), 400
        
        # 运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(kilocode_mcp.process_request(request_data))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "service": "KiloCode MCP"
        }), 500

@app.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    """测试接口"""
    if request.method == 'GET':
        # GET请求返回测试说明
        return jsonify({
            "message": "KiloCode MCP 测试接口",
            "usage": {
                "method": "POST",
                "content_type": "application/json",
                "body": {
                    "content": "要创建的内容描述",
                    "workflow_type": "工作流类型 (可选)",
                    "context": "上下文信息 (可选)"
                }
            },
            "examples": [
                {
                    "name": "PPT创建",
                    "request": {
                        "content": "为华为终端业务创建年终汇报PPT",
                        "workflow_type": "requirements_analysis"
                    }
                },
                {
                    "name": "贪吃蛇游戏",
                    "request": {
                        "content": "创建贪吃蛇游戏",
                        "workflow_type": "coding_implementation"
                    }
                },
                {
                    "name": "Python脚本",
                    "request": {
                        "content": "创建数据处理脚本",
                        "workflow_type": "coding_implementation"
                    }
                }
            ]
        })
    
    else:
        # POST请求执行测试
        try:
            request_data = request.get_json() or {}
            
            # 默认测试请求
            if not request_data.get('content'):
                request_data = {
                    "content": "测试KiloCode MCP功能",
                    "workflow_type": "coding_implementation",
                    "context": {"test": True}
                }
            
            # 执行创建
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(kilocode_mcp.process_request(request_data))
            loop.close()
            
            return jsonify({
                "test_result": "success",
                "request": request_data,
                "response": result,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({
                "test_result": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500

if __name__ == "__main__":
    print("🚀 启动KiloCode MCP服务")
    print(f"📍 服务地址: http://98.81.255.168:8080")
    print(f"🔧 版本: {kilocode_mcp.version}")
    print("📋 可用接口:")
    print("   GET  / - 服务信息")
    print("   GET  /health - 健康检查")
    print("   GET  /capabilities - 能力查询")
    print("   POST /create - 兜底创建")
    print("   GET/POST /test - 测试接口")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8080, debug=False)

