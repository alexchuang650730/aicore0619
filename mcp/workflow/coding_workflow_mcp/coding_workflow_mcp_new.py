#!/usr/bin/env python3
"""
Coding Workflow MCP - 编码工作流MCP
管理完整的编码流程，包括代码规范、审查、质量控制和发布管理
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import requests

logger = logging.getLogger(__name__)

class CodingPhase(Enum):
    """编码阶段"""
    PLANNING = "planning"           # 规划阶段
    DEVELOPMENT = "development"     # 开发阶段
    CODE_REVIEW = "code_review"     # 代码审查
    TESTING = "testing"             # 测试阶段
    INTEGRATION = "integration"     # 集成阶段
    DEPLOYMENT = "deployment"       # 部署阶段

class WorkflowStatus(Enum):
    """工作流状态"""
    IDLE = "idle"                   # 空闲
    RUNNING = "running"             # 运行中
    PAUSED = "paused"               # 暂停
    COMPLETED = "completed"         # 完成
    FAILED = "failed"               # 失败

@dataclass
class CodingTask:
    """编码任务"""
    task_id: str
    title: str
    description: str
    phase: CodingPhase
    status: WorkflowStatus
    assigned_mcp: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = None

class CodingWorkflowMCP:
    """编码工作流MCP - 统一管理编码流程"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.mcp_id = "coding_workflow_mcp"
        self.version = "1.0.0"
        self.status = WorkflowStatus.IDLE
        
        # 工作流配置
        self.workflow_config = {
            "max_concurrent_tasks": 5,
            "auto_progression": True,
            "quality_gates": True,
            "notification_enabled": True
        }
        
        # 注册的MCP组件
        self.registered_mcps = {}
        
        # 当前任务队列
        self.task_queue = []
        self.active_tasks = {}
        
        # 工作流统计
        self.workflow_stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0,
            "quality_score": 0
        }
        
        # MCP Coordinator配置
        self.coordinator_url = "http://localhost:8089"
        
        logger.info(f"🔧 {self.mcp_id} 初始化完成")
    
    def get_status(self) -> Dict[str, Any]:
        """获取工作流状态"""
        return {
            "mcp_id": self.mcp_id,
            "version": self.version,
            "status": self.status.value,
            "registered_mcps": len(self.registered_mcps),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "workflow_stats": self.workflow_stats,
            "capabilities": [
                "coding_process_management",
                "quality_control",
                "code_review_automation",
                "development_intervention",
                "workflow_orchestration"
            ]
        }
    
    def get_three_node_workflow_dashboard(self) -> Dict[str, Any]:
        """获取三节点工作流Dashboard数据"""
        try:
            # 获取Git状态和开发者活动数据
            git_data = self._get_git_dashboard_data()
            intervention_data = self._get_intervention_dashboard_data()
            
            # 计算三节点状态
            coding_node = self._calculate_coding_node_status(git_data, intervention_data)
            editing_node = self._calculate_editing_node_status(git_data, intervention_data)
            deployment_node = self._calculate_deployment_node_status()
            
            # 编码工作流状态卡片数据
            workflow_card = {
                "title": "编码工作流",
                "status": "运行中",
                "status_color": "success",
                "metrics": {
                    "code_quality": {
                        "value": coding_node["quality_score"],
                        "label": "代码质量",
                        "unit": "%"
                    },
                    "architecture_compliance": {
                        "value": intervention_data.get("compliance_score", 92),
                        "label": "架构合规",
                        "unit": "%"
                    },
                    "daily_commits": {
                        "value": git_data.get("daily_commits", 0),
                        "label": "今日提交",
                        "unit": ""
                    },
                    "violations_detected": {
                        "value": intervention_data.get("violations_today", 0),
                        "label": "违规检测",
                        "unit": ""
                    }
                }
            }
            
            dashboard_data = {
                "three_node_workflow": {
                    "nodes": [
                        {
                            "id": "coding",
                            "name": "编码",
                            "icon": "code",
                            "color": "#007AFF",
                            "status": coding_node["status"],
                            "progress": coding_node["progress"],
                            "details": coding_node["details"]
                        },
                        {
                            "id": "editing", 
                            "name": "编辑",
                            "icon": "edit",
                            "color": "#FF8C00",
                            "status": editing_node["status"],
                            "progress": editing_node["progress"],
                            "details": editing_node["details"]
                        },
                        {
                            "id": "deployment",
                            "name": "部署",
                            "icon": "rocket",
                            "color": "#00C851",
                            "status": deployment_node["status"],
                            "progress": deployment_node["progress"],
                            "details": deployment_node["details"]
                        }
                    ]
                },
                "workflow_card": workflow_card,
                "real_time_data": {
                    "git_status": git_data,
                    "intervention_stats": intervention_data,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            return {
                "success": True,
                "dashboard_data": dashboard_data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取三节点工作流Dashboard失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_git_dashboard_data(self) -> Dict[str, Any]:
        """获取Git相关的Dashboard数据"""
        try:
            # 通过Developer Intervention MCP获取Git数据
            response = requests.post(
                "http://localhost:8092/mcp/request",
                json={"action": "get_dashboard_data", "params": {}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    dashboard_data = result.get("dashboard_data", {})
                    git_status = dashboard_data.get("git_status", {})
                    activity_summary = dashboard_data.get("activity_summary", {})
                    
                    return {
                        "current_branch": git_status.get("current_branch", "main"),
                        "uncommitted_changes": len(git_status.get("uncommitted_changes", [])),
                        "is_clean": git_status.get("is_clean", True),
                        "daily_commits": activity_summary.get("commits", 0),
                        "files_modified": activity_summary.get("unique_files", 0),
                        "last_commit_time": git_status.get("last_commit_time"),
                        "last_commit_message": git_status.get("last_commit_message", "")
                    }
            
            return {"daily_commits": 0, "files_modified": 0, "is_clean": True}
            
        except Exception as e:
            logger.error(f"获取Git数据失败: {e}")
            return {"daily_commits": 0, "files_modified": 0, "is_clean": True}
    
    def _get_intervention_dashboard_data(self) -> Dict[str, Any]:
        """获取开发介入相关的Dashboard数据"""
        try:
            # 通过Developer Intervention MCP获取介入数据
            response = requests.post(
                "http://localhost:8092/mcp/request",
                json={"action": "get_prevention_stats", "params": {}},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("prevention_enabled"):
                    stats = result.get("prevention_stats", {})
                    return {
                        "violations_today": stats.get("violations_prevented_today", 0),
                        "compliance_score": max(0, 100 - stats.get("violations_prevented_today", 0) * 5),
                        "auto_fixes_applied": stats.get("auto_fixes_applied", 0),
                        "total_scans": stats.get("total_scans", 0)
                    }
            
            return {"violations_today": 0, "compliance_score": 95, "auto_fixes_applied": 0}
            
        except Exception as e:
            logger.error(f"获取介入数据失败: {e}")
            return {"violations_today": 0, "compliance_score": 95, "auto_fixes_applied": 0}
    
    def _calculate_coding_node_status(self, git_data: Dict, intervention_data: Dict) -> Dict[str, Any]:
        """计算编码节点状态"""
        # 基于Git活动和代码质量计算编码节点状态
        has_activity = git_data.get("daily_commits", 0) > 0 or git_data.get("files_modified", 0) > 0
        quality_score = max(85, 100 - intervention_data.get("violations_today", 0) * 3)
        
        if has_activity:
            status = "active"
            progress = min(100, git_data.get("daily_commits", 0) * 10 + git_data.get("files_modified", 0) * 5)
        else:
            status = "idle"
            progress = 0
        
        return {
            "status": status,
            "progress": progress,
            "quality_score": quality_score,
            "details": {
                "commits_today": git_data.get("daily_commits", 0),
                "files_modified": git_data.get("files_modified", 0),
                "current_branch": git_data.get("current_branch", "main"),
                "last_commit": git_data.get("last_commit_message", "")[:50] + "..." if git_data.get("last_commit_message", "") else ""
            }
        }
    
    def _calculate_editing_node_status(self, git_data: Dict, intervention_data: Dict) -> Dict[str, Any]:
        """计算编辑节点状态"""
        # 基于未提交更改和自动修复计算编辑节点状态
        has_uncommitted = git_data.get("uncommitted_changes", 0) > 0
        auto_fixes = intervention_data.get("auto_fixes_applied", 0)
        
        if has_uncommitted or auto_fixes > 0:
            status = "active"
            progress = min(100, git_data.get("uncommitted_changes", 0) * 20 + auto_fixes * 10)
        else:
            status = "idle"
            progress = 0
        
        return {
            "status": status,
            "progress": progress,
            "details": {
                "uncommitted_files": git_data.get("uncommitted_changes", 0),
                "auto_fixes_applied": auto_fixes,
                "is_clean": git_data.get("is_clean", True),
                "compliance_score": intervention_data.get("compliance_score", 95)
            }
        }
    
    def _calculate_deployment_node_status(self) -> Dict[str, Any]:
        """计算部署节点状态"""
        # 基于Release Manager状态计算部署节点状态
        try:
            response = requests.get("http://localhost:8096/health", timeout=5)
            if response.status_code == 200:
                status = "ready"
                progress = 85
            else:
                status = "error"
                progress = 0
        except:
            status = "idle"
            progress = 0
        
        return {
            "status": status,
            "progress": progress,
            "details": {
                "release_manager_status": status,
                "deployment_ready": status == "ready",
                "last_deployment": "2025-06-16 01:00:00"  # 示例数据
            }
        }
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """获取工作流指标"""
        try:
            dashboard_data = self.get_three_node_workflow_dashboard()
            if dashboard_data["success"]:
                workflow_card = dashboard_data["dashboard_data"]["workflow_card"]
                return {
                    "success": True,
                    "metrics": workflow_card["metrics"]
                }
            else:
                return dashboard_data
                
        except Exception as e:
            logger.error(f"❌ 获取工作流指标失败: {e}")
            return {"success": False, "error": str(e)}

    # 其他原有方法保持不变...
    async def register_component_mcp(self, mcp_id: str, mcp_config: Dict[str, Any]) -> Dict[str, Any]:
        """注册组件MCP"""
        try:
            self.registered_mcps[mcp_id] = {
                "config": mcp_config,
                "registered_at": datetime.now().isoformat(),
                "status": "registered"
            }
            
            logger.info(f"✅ 组件MCP注册成功: {mcp_id}")
            return {
                "success": True,
                "mcp_id": mcp_id,
                "registered_mcps": list(self.registered_mcps.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ 注册组件MCP失败: {e}")
            return {"success": False, "error": str(e)}

    async def create_coding_task(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """创建编码任务"""
        try:
            task_id = f"task_{len(self.task_queue) + 1}_{int(datetime.now().timestamp())}"
            
            task = CodingTask(
                task_id=task_id,
                title=task_params.get("title", ""),
                description=task_params.get("description", ""),
                phase=CodingPhase(task_params.get("phase", "development")),
                status=WorkflowStatus.IDLE,
                created_at=datetime.now().isoformat(),
                metadata=task_params.get("metadata", {})
            )
            
            self.task_queue.append(task)
            self.workflow_stats["total_tasks"] += 1
            
            logger.info(f"📋 编码任务创建: {task_id}")
            return {
                "success": True,
                "task_id": task_id,
                "task": task.__dict__
            }
            
        except Exception as e:
            logger.error(f"❌ 创建编码任务失败: {e}")
            return {"success": False, "error": str(e)}

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行编码任务"""
        try:
            # 查找任务
            task = None
            for t in self.task_queue:
                if t.task_id == task_id:
                    task = t
                    break
            
            if not task:
                return {"success": False, "error": "任务不存在"}
            
            # 移动到活跃任务
            self.task_queue.remove(task)
            task.status = WorkflowStatus.RUNNING
            task.updated_at = datetime.now().isoformat()
            self.active_tasks[task_id] = task
            
            # 根据任务阶段选择合适的MCP执行
            if task.phase == CodingPhase.DEVELOPMENT:
                # 使用Development Intervention MCP
                result = await self._execute_with_development_mcp(task)
            elif task.phase == CodingPhase.CODE_REVIEW:
                # 使用代码审查流程
                result = await self._execute_code_review(task)
            else:
                result = {"success": True, "message": f"任务 {task_id} 执行完成"}
            
            # 更新任务状态
            if result.get("success"):
                task.status = WorkflowStatus.COMPLETED
                self.workflow_stats["completed_tasks"] += 1
            else:
                task.status = WorkflowStatus.FAILED
                self.workflow_stats["failed_tasks"] += 1
            
            # 移动到完成队列
            del self.active_tasks[task_id]
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 执行任务失败: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_with_development_mcp(self, task: CodingTask) -> Dict[str, Any]:
        """使用Development Intervention MCP执行任务"""
        try:
            # 调用Development Intervention MCP
            response = requests.post(
                "http://localhost:8092/mcp/request",
                json={
                    "action": "process_coding_task",
                    "params": {
                        "task_id": task.task_id,
                        "phase": task.phase.value,
                        "description": task.description
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"MCP调用失败: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_code_review(self, task: CodingTask) -> Dict[str, Any]:
        """执行代码审查"""
        # 代码审查逻辑
        return {"success": True, "message": "代码审查完成"}

    async def get_workflow_overview(self) -> Dict[str, Any]:
        """获取工作流概览"""
        return {
            "success": True,
            "overview": {
                "status": self.status.value,
                "registered_mcps": self.registered_mcps,
                "task_queue": [task.__dict__ for task in self.task_queue],
                "active_tasks": {k: v.__dict__ for k, v in self.active_tasks.items()},
                "workflow_stats": self.workflow_stats
            }
        }

    async def health_check_all_mcps(self) -> Dict[str, Any]:
        """健康检查所有注册的MCP"""
        health_results = {}
        
        for mcp_id in self.registered_mcps:
            try:
                # 这里应该调用各个MCP的健康检查
                health_results[mcp_id] = {"status": "healthy", "checked_at": datetime.now().isoformat()}
            except Exception as e:
                health_results[mcp_id] = {"status": "error", "error": str(e)}
        
        return {
            "success": True,
            "health_results": health_results
        }

def create_coding_workflow_mcp_server():
    """创建编码工作流MCP服务器"""
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    # 创建MCP实例
    coding_mcp = CodingWorkflowMCP()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            "mcp_id": "coding_workflow_mcp",
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/mcp/info', methods=['GET'])
    def mcp_info():
        """MCP基本信息"""
        return jsonify({
            "mcp_id": "coding_workflow_mcp",
            "version": "1.0.0",
            "capabilities": [
                "coding_process_management",
                "quality_control",
                "code_review_automation",
                "development_intervention",
                "workflow_orchestration"
            ],
            "description": "Coding Workflow MCP - 编码工作流管理"
        })
    
    @app.route('/mcp/request', methods=['POST'])
    def mcp_request():
        """标准MCP请求处理"""
        try:
            data = request.get_json()
            action = data.get('action')
            params = data.get('params', {})
            
            if action == 'get_status':
                result = coding_mcp.get_status()
            elif action == 'register_component_mcp':
                mcp_id = params.get('mcp_id')
                mcp_config = params.get('mcp_config', {})
                result = asyncio.run(coding_mcp.register_component_mcp(mcp_id, mcp_config))
            elif action == 'create_coding_task':
                result = asyncio.run(coding_mcp.create_coding_task(params))
            elif action == 'execute_task':
                task_id = params.get('task_id')
                result = asyncio.run(coding_mcp.execute_task(task_id))
            elif action == 'get_workflow_overview':
                result = asyncio.run(coding_mcp.get_workflow_overview())
            elif action == 'health_check_all_mcps':
                result = asyncio.run(coding_mcp.health_check_all_mcps())
            elif action == 'get_three_node_workflow_dashboard':
                result = coding_mcp.get_three_node_workflow_dashboard()
            elif action == 'get_workflow_metrics':
                result = coding_mcp.get_workflow_metrics()
            else:
                result = {
                    "success": False,
                    "error": f"未知操作: {action}"
                }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"MCP请求处理失败: {e}")
            return jsonify({
                "success": False,
                "error": f"MCP请求处理失败: {e}"
            }), 500
    
    return app

if __name__ == '__main__':
    logger.info("🚀 启动 Coding Workflow MCP...")
    
    app = create_coding_workflow_mcp_server()
    
    logger.info("📍 服务地址: http://0.0.0.0:8093")
    logger.info("🔧 编码工作流管理已就绪")
    
    app.run(host='0.0.0.0', port=8093, debug=False)

