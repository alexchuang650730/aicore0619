#!/usr/bin/env python3
"""
Product Orchestrator V3 管理界面 Web 服务器

提供admin测试和管理Product Orchestrator V3的Web界面
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import threading
import time

# 添加项目路径
project_root = Path("/opt/powerautomation")
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量存储orchestrator实例
orchestrator_instance = None
active_workflows = {}
workflow_history = []

class MockProductOrchestrator:
    """模拟Product Orchestrator用于演示"""
    
    def __init__(self):
        self.workflows = {}
        self.workflow_counter = 0
    
    async def create_and_execute_workflow(self, requirements):
        """创建并执行工作流"""
        self.workflow_counter += 1
        workflow_id = f"workflow_{self.workflow_counter}_{int(time.time())}"
        
        # 模拟工作流执行
        workflow_data = {
            "workflow_id": workflow_id,
            "name": requirements.get("name", "Unnamed Project"),
            "description": requirements.get("description", ""),
            "complexity": requirements.get("complexity", "medium"),
            "status": "completed",
            "progress": 1.0,
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "execution_result": {
                "success": True,
                "generated_files": [
                    f"{requirements.get('name', 'project').lower().replace(' ', '_')}/src/main.py",
                    f"{requirements.get('name', 'project').lower().replace(' ', '_')}/README.md",
                    f"{requirements.get('name', 'project').lower().replace(' ', '_')}/requirements.txt"
                ],
                "deployment_url": f"https://demo-{workflow_id}.example.com",
                "documentation_url": f"https://docs-{workflow_id}.example.com"
            },
            "dependency_analysis": {
                "dependency_graph": {
                    "requirement_analysis": [],
                    "architecture_design": ["requirement_analysis"],
                    "code_implementation": ["architecture_design"],
                    "test_verification": ["code_implementation"],
                    "deployment_release": ["code_implementation"],
                    "monitoring_operations": ["deployment_release"]
                },
                "critical_path": ["requirement_analysis", "architecture_design", "code_implementation", "deployment_release", "monitoring_operations"],
                "cycles": []
            },
            "workflow_steps": [
                {"name": "需求分析", "status": "completed", "duration": 2.5},
                {"name": "架构设计", "status": "completed", "duration": 3.2},
                {"name": "编码实现", "status": "completed", "duration": 8.7},
                {"name": "测试验证", "status": "completed", "duration": 4.1},
                {"name": "部署发布", "status": "completed", "duration": 2.8},
                {"name": "监控运维", "status": "completed", "duration": 1.5}
            ]
        }
        
        self.workflows[workflow_id] = workflow_data
        return workflow_data
    
    async def get_workflow_status(self, workflow_id):
        """获取工作流状态"""
        return self.workflows.get(workflow_id, {"error": "Workflow not found"})
    
    async def list_active_workflows(self):
        """列出活跃工作流"""
        return list(self.workflows.values())

# 初始化模拟orchestrator
orchestrator_instance = MockProductOrchestrator()

@app.route('/')
def index():
    """主页"""
    return render_template('admin_dashboard.html')

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """获取所有工作流"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        workflows = loop.run_until_complete(orchestrator_instance.list_active_workflows())
        loop.close()
        
        return jsonify({
            "success": True,
            "workflows": workflows,
            "total": len(workflows)
        })
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """创建新工作流"""
    try:
        data = request.get_json()
        
        # 验证必需字段
        if not data.get('name'):
            return jsonify({"success": False, "error": "Name is required"}), 400
        
        # 设置默认值
        requirements = {
            "name": data.get('name'),
            "description": data.get('description', ''),
            "complexity": data.get('complexity', 'medium'),
            "priority": data.get('priority', 'medium'),
            "technologies": data.get('technologies', []),
            "target_platform": data.get('target_platform', 'web')
        }
        
        # 执行工作流
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator_instance.create_and_execute_workflow(requirements))
        loop.close()
        
        # 添加到历史记录
        workflow_history.append(result)
        
        return jsonify({
            "success": True,
            "workflow": result
        })
        
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow_status(workflow_id):
    """获取特定工作流状态"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(orchestrator_instance.get_workflow_status(workflow_id))
        loop.close()
        
        return jsonify({
            "success": True,
            "workflow": status
        })
    except Exception as e:
        logger.error(f"Error getting workflow status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/templates', methods=['GET'])
def get_workflow_templates():
    """获取工作流模板"""
    templates = {
        "software_development": {
            "name": "完整软件开发流程",
            "description": "包含需求分析到监控运维的完整开发流程",
            "complexity": "high",
            "estimated_duration": "2小时",
            "workflows": ["需求分析", "架构设计", "编码实现", "测试验证", "部署发布", "监控运维"]
        },
        "quick_prototype": {
            "name": "快速原型开发",
            "description": "快速创建原型的简化流程",
            "complexity": "low",
            "estimated_duration": "30分钟",
            "workflows": ["需求分析", "编码实现", "测试验证"]
        },
        "documentation_only": {
            "name": "文档和设计",
            "description": "专注于文档和架构设计",
            "complexity": "medium",
            "estimated_duration": "20分钟",
            "workflows": ["需求分析", "架构设计"]
        },
        "ai_model_development": {
            "name": "AI模型开发",
            "description": "AI模型开发的专用流程",
            "complexity": "high",
            "estimated_duration": "1小时",
            "workflows": ["需求分析", "架构设计", "编码实现", "测试验证", "部署发布"]
        }
    }
    
    return jsonify({
        "success": True,
        "templates": templates
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        workflows = loop.run_until_complete(orchestrator_instance.list_active_workflows())
        loop.close()
        
        # 计算统计信息
        total_workflows = len(workflows)
        completed_workflows = len([w for w in workflows if w.get('status') == 'completed'])
        failed_workflows = len([w for w in workflows if w.get('status') == 'failed'])
        running_workflows = len([w for w in workflows if w.get('status') == 'running'])
        
        # 复杂度分布
        complexity_stats = {}
        for workflow in workflows:
            complexity = workflow.get('complexity', 'unknown')
            complexity_stats[complexity] = complexity_stats.get(complexity, 0) + 1
        
        # 平均执行时间（模拟数据）
        avg_execution_time = 15.5  # 秒
        
        stats = {
            "total_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "running_workflows": running_workflows,
            "success_rate": (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            "complexity_distribution": complexity_stats,
            "avg_execution_time": avg_execution_time,
            "last_updated": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "Product Orchestrator V3 Admin Dashboard",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 创建模板目录
    template_dir = Path(__file__).parent / 'templates'
    template_dir.mkdir(exist_ok=True)
    
    logger.info("Starting Product Orchestrator V3 Admin Dashboard...")
    logger.info("Dashboard will be available at: http://localhost:8200")
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=8200,
        debug=True,
        threaded=True
    )

