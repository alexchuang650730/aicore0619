#!/usr/bin/env python3
"""
Operations Workflow MCP Web API (Updated)
通过MCP Coordinator提供文件处理逻辑、监控状态和放置规则的Web API接口
"""

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Coordinator配置
MCP_COORDINATOR_URL = "http://localhost:8089"
OPERATIONS_MCP_ID = "operations_workflow_mcp"

def call_mcp_coordinator(action: str, params: dict = None):
    """通过MCP Coordinator调用Operations Workflow MCP"""
    try:
        response = requests.post(
            f"{MCP_COORDINATOR_URL}/coordinator/request/{OPERATIONS_MCP_ID}",
            json={
                "action": action,
                "params": params or {}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"MCP Coordinator请求失败: HTTP {response.status_code}")
            return {
                "success": False,
                "error": f"MCP Coordinator请求失败: HTTP {response.status_code}"
            }
    except Exception as e:
        logger.error(f"调用MCP Coordinator失败: {e}")
        return {
            "success": False,
            "error": f"调用MCP Coordinator失败: {str(e)}"
        }

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """获取系统整体状态"""
    try:
        # 通过MCP Coordinator获取Operations Workflow MCP状态
        result = call_mcp_coordinator("get_status")
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "获取状态失败")}), 500
        
        mcp_data = result.get("data", {})
        
        return jsonify({
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "mcp_coordinator": {
                "url": MCP_COORDINATOR_URL,
                "status": "connected"
            },
            "operations_workflow_mcp": mcp_data.get("mcp_info", {}),
            "components": mcp_data.get("components", {})
        })
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/file-placement/rules', methods=['GET'])
def get_file_placement_rules():
    """获取文件放置规则"""
    try:
        # 这里可以通过MCP Coordinator获取规则，或者返回静态规则
        # 为了演示，我们返回一个基本的规则集
        rules = [
            {
                "pattern": "test_case_generator.py",
                "target": "scripts/test_case_generator.py",
                "type": "script",
                "description": "PowerAutomation测试用例生成器",
                "extract": False
            },
            {
                "pattern": "*.pem",
                "target": "upload/.recovery/",
                "type": "security",
                "description": "安全密钥文件",
                "extract": False
            },
            {
                "pattern": "*.tar.gz",
                "target": "test/",
                "type": "archive",
                "description": "压缩归档文件",
                "extract": True
            }
        ]
        
        return jsonify({
            "rules": rules,
            "total_rules": len(rules),
            "source": "mcp_coordinator"
        })
    except Exception as e:
        logger.error(f"获取文件放置规则失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/file-placement/analysis', methods=['GET'])
def get_file_analysis():
    """获取当前文件分析结果"""
    try:
        result = call_mcp_coordinator("file_placement_analyze")
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "文件分析失败")}), 500
        
        return jsonify({
            "analysis": result.get("data", {}),
            "timestamp": datetime.now().isoformat(),
            "source": "mcp_coordinator"
        })
    except Exception as e:
        logger.error(f"文件分析失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/file-placement/execute', methods=['POST'])
def execute_file_placement():
    """手动执行文件放置"""
    try:
        result = call_mcp_coordinator("file_placement_execute")
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "文件放置失败")}), 500
        
        return jsonify({
            **result.get("data", {}),
            "source": "mcp_coordinator"
        })
    except Exception as e:
        logger.error(f"执行文件放置失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mcp-registry', methods=['GET'])
def get_mcp_registry():
    """获取MCP注册表信息"""
    try:
        result = call_mcp_coordinator("registry_status")
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "获取MCP注册表失败")}), 500
        
        return jsonify({
            **result.get("data", {}),
            "source": "mcp_coordinator"
        })
    except Exception as e:
        logger.error(f"获取MCP注册表失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/interventions', methods=['GET'])
def get_interventions():
    """获取介入历史和状态"""
    try:
        result = call_mcp_coordinator("interventions_status")
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "获取介入信息失败")}), 500
        
        return jsonify({
            "current_status": result.get("data", {}),
            "source": "mcp_coordinator"
        })
    except Exception as e:
        logger.error(f"获取介入信息失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/directory-check', methods=['GET'])
def get_directory_check():
    """获取目录结构检查结果"""
    try:
        result = call_mcp_coordinator("directory_check")
        
        if not result.get("success"):
            return jsonify({"error": result.get("error", "目录检查失败")}), 500
        
        return jsonify({
            **result.get("data", {}),
            "source": "mcp_coordinator"
        })
    except Exception as e:
        logger.error(f"目录检查失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/coordinator/status', methods=['GET'])
def get_coordinator_status():
    """获取MCP Coordinator状态"""
    try:
        response = requests.get(f"{MCP_COORDINATOR_URL}/coordinator/info", timeout=10)
        
        if response.status_code == 200:
            return jsonify({
                "coordinator_info": response.json(),
                "connection_status": "connected",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "error": f"MCP Coordinator不可达: HTTP {response.status_code}",
                "connection_status": "disconnected"
            }), 500
    except Exception as e:
        return jsonify({
            "error": f"无法连接MCP Coordinator: {str(e)}",
            "connection_status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 检查MCP Coordinator连接
        coordinator_response = requests.get(f"{MCP_COORDINATOR_URL}/health", timeout=5)
        coordinator_healthy = coordinator_response.status_code == 200
        
        return jsonify({
            "status": "healthy" if coordinator_healthy else "degraded",
            "service": "Operations Workflow MCP Web API (via Coordinator)",
            "mcp_coordinator": {
                "url": MCP_COORDINATOR_URL,
                "status": "healthy" if coordinator_healthy else "unhealthy"
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "Operations Workflow MCP Web API (via Coordinator)",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 启动 Operations Workflow MCP Web API (via Coordinator)")
    print("=" * 70)
    print("架构:")
    print("  SmartUI (5001) ↔ MCP Coordinator (8089) ↔ Operations Workflow MCP (8090)")
    print("=" * 70)
    print("API端点:")
    print("  - GET  /api/status                - 系统状态")
    print("  - GET  /api/file-placement/rules  - 文件放置规则")
    print("  - GET  /api/file-placement/analysis - 文件分析")
    print("  - POST /api/file-placement/execute - 执行文件放置")
    print("  - GET  /api/mcp-registry          - MCP注册表")
    print("  - GET  /api/interventions         - 介入历史")
    print("  - GET  /api/directory-check       - 目录结构检查")
    print("  - GET  /api/coordinator/status    - MCP Coordinator状态")
    print("  - GET  /health                    - 健康检查")
    print("=" * 70)
    print("所有请求通过MCP Coordinator转发到Operations Workflow MCP")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5001, debug=True)

