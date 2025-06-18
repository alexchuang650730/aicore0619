#!/usr/bin/env python3
"""
Test Manager MCP Server
为Test Manager MCP提供HTTP API接口
运行在8097端口
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import logging
from datetime import datetime
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp.workflow.test_manager_mcp.test_manager_mcp import TestManagerMCP

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化Test Manager MCP
test_manager_mcp = TestManagerMCP()

@app.route('/api/status', methods=['GET'])
def api_status():
    """获取Test Manager MCP状态"""
    return jsonify({
        "success": True,
        "service_id": test_manager_mcp.service_id,
        "version": test_manager_mcp.version,
        "status": test_manager_mcp.status,
        "message": "Test Manager MCP运行正常",
        "capabilities": [
            "测试发现",
            "测试执行", 
            "测试报告生成",
            "测试策略推荐"
        ],
        "endpoints": [
            "/api/status",
            "/api/discover_tests",
            "/api/execute_tests",
            "/mcp/request"
        ]
    })

@app.route('/api/discover_tests', methods=['POST'])
def api_discover_tests():
    """发现项目测试"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        
        logger.info(f"🔍 发现测试: {project_info.get('name', 'Unknown Project')}")
        
        # 调用Test Manager MCP的测试发现功能
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            test_manager_mcp.discover_tests_by_project(project_info)
        )
        loop.close()
        
        return jsonify({
            "success": True,
            "action": "discover_tests",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"测试发现失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "discover_tests"
        }), 500

@app.route('/api/execute_tests', methods=['POST'])
def api_execute_tests():
    """执行测试计划"""
    try:
        data = request.get_json()
        test_plan = data.get('test_plan', {})
        project_info = data.get('project_info', {})
        
        logger.info(f"🧪 执行测试: {project_info.get('name', 'Unknown Project')}")
        
        # 调用Test Manager MCP的测试执行功能
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            test_manager_mcp.execute_test_plan(test_plan, project_info)
        )
        loop.close()
        
        return jsonify({
            "success": True,
            "action": "execute_tests",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "execute_tests"
        }), 500

@app.route('/mcp/request', methods=['POST'])
def mcp_request():
    """标准MCP请求接口"""
    try:
        data = request.get_json()
        action = data.get('action', '')
        params = data.get('params', {})
        
        logger.info(f"📨 MCP请求: {action}")
        
        if action == 'full_test_cycle':
            # 执行完整测试周期
            project_info = params.get('project_info', {})
            
            # 1. 发现测试
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            discovery_result = loop.run_until_complete(
                test_manager_mcp.discover_tests_by_project(project_info)
            )
            
            # 2. 执行测试
            test_plan = discovery_result.get('test_plan', discovery_result.get('fallback_plan', {}))
            execution_result = loop.run_until_complete(
                test_manager_mcp.execute_test_plan(test_plan, project_info)
            )
            loop.close()
            
            return jsonify({
                "success": True,
                "results": {
                    "discovery": discovery_result,
                    "execution": execution_result
                },
                "timestamp": datetime.now().isoformat()
            })
            
        elif action == 'discover_tests':
            project_info = params.get('project_info', {})
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                test_manager_mcp.discover_tests_by_project(project_info)
            )
            loop.close()
            
            return jsonify({
                "success": True,
                "results": result,
                "timestamp": datetime.now().isoformat()
            })
            
        elif action == 'execute_tests':
            test_plan = params.get('test_plan', {})
            project_info = params.get('project_info', {})
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                test_manager_mcp.execute_test_plan(test_plan, project_info)
            )
            loop.close()
            
            return jsonify({
                "success": True,
                "results": result,
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            return jsonify({
                "success": False,
                "error": f"不支持的操作: {action}",
                "supported_actions": [
                    "full_test_cycle",
                    "discover_tests", 
                    "execute_tests"
                ]
            }), 400
            
    except Exception as e:
        logger.error(f"MCP请求处理失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "test_manager_mcp",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("🚀 启动 Test Manager MCP Server...")
    logger.info("📍 服务地址: http://0.0.0.0:8097")
    logger.info("🧪 提供测试管理服务")
    
    app.run(host='0.0.0.0', port=8097, debug=False)

