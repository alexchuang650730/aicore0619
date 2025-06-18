#!/usr/bin/env python3
"""
<<<<<<< HEAD
MCP协调器服务器
在端口8089提供MCP协调器界面
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import json
from datetime import datetime
=======
MCP Coordinator Server
中央协调器 - 运行在8089端口，管理所有MCP通信
"""

import asyncio
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
>>>>>>> e26191443ef6976e959ec2d3a0417cc3c85946bc

app = Flask(__name__)
CORS(app)

<<<<<<< HEAD
# MCP服务注册表
MCP_SERVICES = [
    {
        "name": "KILOCODE MCP",
        "status": "✅ 运行中",
        "port": 8080,
        "description": "兜底创建引擎"
    },
    {
        "name": "RELEASE MANAGER_MCP", 
        "status": "✅ 运行中",
        "port": 8091,
        "description": "发布管理引擎"
    },
    {
        "name": "SMART UI_MCP",
        "status": "✅ 运行中", 
        "port": 8092,
        "description": "智能界面引擎"
    },
    {
        "name": "TEST MANAGER_MCP",
        "status": "✅ 运行中",
        "port": 8093,
        "description": "测试管理引擎"
    },
    {
        "name": "REQUIREMENTS ANALYSIS_MCP",
        "status": "✅ 运行中",
        "port": 8094,
        "description": "需求分析智能引擎"
    },
    {
        "name": "ARCHITECTURE DESIGN_MCP",
        "status": "✅ 运行中", 
        "port": 8095,
        "description": "架构设计智能引擎"
    }
]

# MCP协调器界面HTML
COORDINATOR_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP协调器</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .status {
            font-size: 16px;
            color: #28a745;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 14px;
            color: #666;
        }
        .mcp-list {
            margin-top: 20px;
        }
        .mcp-item {
            display: flex;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .mcp-item:last-child {
            border-bottom: none;
        }
        .mcp-bullet {
            margin-right: 10px;
            font-size: 16px;
        }
        .mcp-name {
            font-weight: bold;
            color: #333;
        }
        .mcp-status {
            margin-left: 10px;
            color: #28a745;
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">MCP协调器</div>
            <div class="status">运行中</div>
            <div class="subtitle">统一工作流协调 | 智能介入管理</div>
        </div>
        
        <div class="mcp-list" id="mcpList">
            <!-- MCP服务列表将通过JavaScript动态加载 -->
        </div>
        
        <button class="refresh-btn" onclick="loadMCPServices()">刷新状态</button>
    </div>

    <script>
        function loadMCPServices() {
            fetch('/coordinator/mcps/api')
                .then(response => response.json())
                .then(data => {
                    const mcpList = document.getElementById('mcpList');
                    mcpList.innerHTML = '';
                    
                    data.services.forEach(service => {
                        const item = document.createElement('div');
                        item.className = 'mcp-item';
                        item.innerHTML = `
                            <span class="mcp-bullet">•</span>
                            <span class="mcp-name">${service.name}:</span>
                            <span class="mcp-status">${service.status}</span>
                        `;
                        mcpList.appendChild(item);
                    });
                })
                .catch(error => {
                    console.error('加载MCP服务失败:', error);
                });
        }
        
        // 页面加载时自动加载MCP服务
        document.addEventListener('DOMContentLoaded', loadMCPServices);
        
        // 每30秒自动刷新
        setInterval(loadMCPServices, 30000);
    </script>
</body>
</html>
"""

@app.route('/coordinator/mcps')
def coordinator_mcps():
    """MCP协调器主界面"""
    return COORDINATOR_HTML

@app.route('/coordinator/mcps/api')
def coordinator_mcps_api():
    """MCP服务API接口"""
    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "services": MCP_SERVICES,
        "total_count": len(MCP_SERVICES)
    })

@app.route('/coordinator/mcps/register', methods=['POST'])
def register_mcp():
    """注册新的MCP服务"""
    try:
        from flask import request
        service_data = request.get_json()
        
        # 检查是否已存在
        existing = next((s for s in MCP_SERVICES if s['name'] == service_data['name']), None)
        if existing:
            existing.update(service_data)
            return jsonify({"success": True, "message": "MCP服务已更新"})
        else:
            MCP_SERVICES.append(service_data)
            return jsonify({"success": True, "message": "MCP服务已注册"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        "service": "MCP Coordinator",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "mcp_count": len(MCP_SERVICES)
    })

if __name__ == '__main__':
    print("🚀 启动MCP协调器服务器...")
    print("📍 服务地址: http://98.81.255.168:8089")
    print("🌐 协调器界面: http://98.81.255.168:8089/coordinator/mcps")
    print("📊 API接口: http://98.81.255.168:8089/coordinator/mcps/api")
=======
class MCPCoordinator:
    """MCP中央协调器"""
    
    def __init__(self):
        self.coordinator_id = "mcp_coordinator"
        self.version = "1.0.0"
        self.status = "running"
        
        # MCP注册表 - 记录所有已注册的MCP
        self.registered_mcps = {
            "operations_workflow_mcp": {
                "url": "http://localhost:8090",
                "status": "unknown",
                "capabilities": [
                    "file_placement",
                    "mcp_registry_management", 
                    "smart_intervention",
                    "directory_structure_management"
                ],
                "last_health_check": None
            }
        }
        
        logger.info(f"✅ MCP Coordinator 初始化完成")
    
    def get_coordinator_info(self):
        """获取协调器信息"""
        return {
            "coordinator_id": self.coordinator_id,
            "version": self.version,
            "status": self.status,
            "registered_mcps": len(self.registered_mcps),
            "endpoints": [
                "/coordinator/info",
                "/coordinator/mcps",
                "/coordinator/request",
                "/coordinator/health-check"
            ]
        }
    
    def register_mcp(self, mcp_id: str, mcp_config: dict):
        """注册MCP"""
        self.registered_mcps[mcp_id] = {
            **mcp_config,
            "registered_at": datetime.now().isoformat(),
            "status": "registered"
        }
        logger.info(f"✅ 注册MCP: {mcp_id}")
        return True
    
    def health_check_mcp(self, mcp_id: str):
        """检查MCP健康状态"""
        if mcp_id not in self.registered_mcps:
            return {"success": False, "error": f"MCP {mcp_id} 未注册"}
        
        mcp_config = self.registered_mcps[mcp_id]
        try:
            response = requests.get(f"{mcp_config['url']}/health", timeout=5)
            if response.status_code == 200:
                self.registered_mcps[mcp_id]["status"] = "healthy"
                self.registered_mcps[mcp_id]["last_health_check"] = datetime.now().isoformat()
                return {"success": True, "status": "healthy", "data": response.json()}
            else:
                self.registered_mcps[mcp_id]["status"] = "unhealthy"
                return {"success": False, "status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            self.registered_mcps[mcp_id]["status"] = "unreachable"
            return {"success": False, "status": "unreachable", "error": str(e)}
    
    def forward_request(self, mcp_id: str, action: str, params: dict = None):
        """转发请求到指定MCP"""
        if mcp_id not in self.registered_mcps:
            return {"success": False, "error": f"MCP {mcp_id} 未注册"}
        
        mcp_config = self.registered_mcps[mcp_id]
        
        try:
            # 构造MCP请求
            mcp_request = {
                "action": action,
                "params": params or {},
                "coordinator_id": self.coordinator_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # 发送请求到MCP
            response = requests.post(
                f"{mcp_config['url']}/mcp/request",
                json=mcp_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ 转发请求成功: {mcp_id}.{action}")
                return result
            else:
                logger.error(f"❌ 转发请求失败: {mcp_id}.{action} - HTTP {response.status_code}")
                return {
                    "success": False,
                    "error": f"MCP请求失败: HTTP {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ 转发请求异常: {mcp_id}.{action} - {e}")
            return {
                "success": False,
                "error": f"请求转发异常: {str(e)}"
            }
    
    def health_check_all(self):
        """检查所有MCP健康状态"""
        results = {}
        for mcp_id in self.registered_mcps:
            results[mcp_id] = self.health_check_mcp(mcp_id)
        return results

# 全局协调器实例
coordinator = MCPCoordinator()

# ============================================================================
# Flask API 端点
# ============================================================================

@app.route('/coordinator/info', methods=['GET'])
def get_coordinator_info():
    """获取协调器信息"""
    return jsonify(coordinator.get_coordinator_info())

@app.route('/coordinator/mcps', methods=['GET'])
def get_registered_mcps():
    """获取已注册的MCP列表"""
    return jsonify({
        "registered_mcps": coordinator.registered_mcps,
        "total": len(coordinator.registered_mcps)
    })

@app.route('/coordinator/register', methods=['POST'])
def register_mcp():
    """注册新的MCP"""
    try:
        data = request.get_json()
        mcp_id = data.get('mcp_id')
        mcp_config = data.get('config', {})
        
        if not mcp_id:
            return jsonify({"success": False, "error": "缺少mcp_id"}), 400
        
        success = coordinator.register_mcp(mcp_id, mcp_config)
        return jsonify({"success": success, "mcp_id": mcp_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/coordinator/request/<mcp_id>', methods=['POST'])
def forward_mcp_request(mcp_id):
    """转发请求到指定MCP"""
    try:
        data = request.get_json()
        action = data.get('action')
        params = data.get('params', {})
        
        if not action:
            return jsonify({"success": False, "error": "缺少action参数"}), 400
        
        result = coordinator.forward_request(mcp_id, action, params)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"转发请求失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/coordinator/health-check', methods=['GET'])
def health_check_all():
    """检查所有MCP健康状态"""
    results = coordinator.health_check_all()
    return jsonify({
        "coordinator_status": "healthy",
        "mcp_health_checks": results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/coordinator/health-check/<mcp_id>', methods=['GET'])
def health_check_mcp(mcp_id):
    """检查指定MCP健康状态"""
    result = coordinator.health_check_mcp(mcp_id)
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    """协调器健康检查"""
    return jsonify({
        "status": "healthy",
        "coordinator_id": coordinator.coordinator_id,
        "version": coordinator.version,
        "registered_mcps": len(coordinator.registered_mcps),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 启动 MCP Coordinator")
    print("=" * 60)
    print(f"协调器ID: {coordinator.coordinator_id}")
    print(f"版本: {coordinator.version}")
    print(f"已注册MCP: {len(coordinator.registered_mcps)}")
    print("=" * 60)
    print("协调器端点:")
    print("  - GET  /coordinator/info           - 协调器信息")
    print("  - GET  /coordinator/mcps           - 已注册MCP列表")
    print("  - POST /coordinator/register       - 注册新MCP")
    print("  - POST /coordinator/request/<mcp_id> - 转发MCP请求")
    print("  - GET  /coordinator/health-check   - 检查所有MCP健康状态")
    print("  - GET  /health                     - 协调器健康检查")
    print("=" * 60)
    print("运行在端口: 8089")
>>>>>>> e26191443ef6976e959ec2d3a0417cc3c85946bc
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8089, debug=False)

<<<<<<< HEAD
=======


# ============================================================================
# Web API 端点 - 为前端界面提供直接访问
# ============================================================================

@app.route('/api/operations-status', methods=['GET'])
def get_operations_status():
    """获取Operations Workflow MCP状态"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_status", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/file-placement-status', methods=['GET'])
def get_file_placement_status():
    """获取文件放置状态"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_file_placement_status", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflow-status', methods=['GET'])
def get_workflow_status():
    """获取六大工作流状态"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_workflow_status", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/github-sync', methods=['GET'])
def get_github_sync():
    """获取GitHub同步信息"""
    try:
        # 通过GitHub MCP获取信息
        result = coordinator.forward_request(
            "github_mcp", 
            "get_repo_info", 
            {}
        )
        
        if result.get("success"):
            # 转换为前端需要的格式
            repo_data = result.get("data", {})
            return jsonify({
                "success": True,
                "data": {
                    "repo_name": repo_data.get("repo_name", "unknown"),
                    "current_branch": repo_data.get("current_branch", "unknown"),
                    "last_sync": repo_data.get("last_sync", "unknown"),
                    "sync_status": repo_data.get("sync_status", "unknown"),
                    "webhook_status": repo_data.get("webhook_status", "正常监听"),
                    "auto_deploy": repo_data.get("auto_deploy", "启用"),
                    "code_quality": repo_data.get("code_quality", "通过")
                }
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mcp-registry', methods=['GET'])
def get_mcp_registry():
    """获取MCP注册表信息"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_mcp_registry_status", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/intervention-stats', methods=['GET'])
def get_intervention_stats():
    """获取智能介入统计"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_intervention_stats", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/directory-structure', methods=['GET'])
def get_directory_structure():
    """获取目录结构状态"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_directory_structure_status", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recent-operations', methods=['GET'])
def get_recent_operations():
    """获取最近操作记录"""
    try:
        result = coordinator.forward_request(
            "operations_workflow_mcp", 
            "get_recent_operations", 
            {}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================================================
# GitHub MCP 注册
# ============================================================================

def register_github_mcp():
    """注册GitHub MCP到协调器"""
    github_mcp_config = {
        "url": "http://localhost:8091",
        "status": "unknown",
        "capabilities": [
            "git_repo_info",
            "branch_management", 
            "commit_history",
            "sync_status_monitoring"
        ],
        "last_health_check": None
    }
    
    coordinator.register_mcp("github_mcp", github_mcp_config)
    logger.info("✅ GitHub MCP 已注册到协调器")

# 启动时注册GitHub MCP
register_github_mcp()

>>>>>>> e26191443ef6976e959ec2d3a0417cc3c85946bc
