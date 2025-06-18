#!/usr/bin/env python3
"""
Developer Flow MCP - 开发者工作流MCP
负责管理开发者的完整工作流程，包括代码开发、质量检查、dashboard监控等
运行在8097端口
"""

import asyncio
import json
import requests
import subprocess
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
import sqlite3
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    """工作流阶段"""
    PLANNING = "planning"
    CODING = "coding"
    TESTING = "testing"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"

class DeveloperStatus(Enum):
    """开发者状态"""
    IDLE = "idle"
    ACTIVE = "active"
    CODING = "coding"
    REVIEWING = "reviewing"
    DEBUGGING = "debugging"

@dataclass
class DeveloperSession:
    """开发者会话"""
    developer_id: str
    session_id: str
    start_time: datetime
    last_activity: datetime
    current_stage: WorkflowStage
    status: DeveloperStatus
    current_branch: str
    files_modified: List[str]
    commits_count: int
    quality_score: float

@dataclass
class WorkflowTask:
    """工作流任务"""
    task_id: str
    developer_id: str
    stage: WorkflowStage
    description: str
    created_time: datetime
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    result: Optional[Dict] = None

class DeveloperFlowMCP:
    """开发者工作流MCP"""
    
    def __init__(self):
        self.mcp_id = "developer_flow_mcp"
        self.version = "1.0.0"
        self.status = "running"
        self.port = 8097
        
        # MCP协调器配置
        self.coordinator_url = "http://localhost:8089"
        
        # 注册的组件MCP
        self.registered_mcps = {}
        
        # 开发者会话管理
        self.active_sessions = {}
        
        # 工作流任务队列
        self.task_queue = []
        self.completed_tasks = []
        
        # 统计信息
        self.workflow_stats = {
            "total_sessions": 0,
            "active_developers": 0,
            "tasks_completed": 0,
            "average_quality_score": 0.0,
            "total_commits": 0
        }
        
        # 初始化数据库
        self._init_database()
        
        logger.info(f"✅ {self.mcp_id} 初始化完成")
        logger.info(f"📍 服务端口: {self.port}")
    
    def _init_database(self):
        """初始化SQLite数据库"""
        db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 创建开发者会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS developer_sessions (
                    session_id TEXT PRIMARY KEY,
                    developer_id TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    current_stage TEXT,
                    status TEXT,
                    current_branch TEXT,
                    commits_count INTEGER DEFAULT 0,
                    quality_score REAL DEFAULT 0.0
                )
            ''')
            
            # 创建工作流任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_tasks (
                    task_id TEXT PRIMARY KEY,
                    developer_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    description TEXT,
                    created_time TEXT NOT NULL,
                    completed_time TEXT,
                    status TEXT NOT NULL,
                    result TEXT
                )
            ''')
            
            # 创建活动日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    developer_id TEXT NOT NULL,
                    session_id TEXT,
                    activity_type TEXT NOT NULL,
                    description TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            logger.info("📊 数据库初始化完成")
    
    def register_component_mcp(self, mcp_id: str, mcp_url: str, capabilities: List[str]) -> Dict[str, Any]:
        """注册组件MCP"""
        try:
            # 验证MCP健康状态
            health_response = requests.get(f"{mcp_url}/health", timeout=5)
            if health_response.status_code != 200:
                return {"success": False, "error": f"MCP {mcp_id} 健康检查失败"}
            
            # 注册MCP
            self.registered_mcps[mcp_id] = {
                "url": mcp_url,
                "capabilities": capabilities,
                "registered_time": datetime.now().isoformat(),
                "status": "active"
            }
            
            logger.info(f"✅ 组件MCP注册成功: {mcp_id}")
            return {
                "success": True,
                "message": f"MCP {mcp_id} 注册成功",
                "registered_mcps": list(self.registered_mcps.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ 注册MCP {mcp_id} 失败: {e}")
            return {"success": False, "error": str(e)}
    
    def start_developer_session(self, developer_id: str, branch_name: str = "main") -> Dict[str, Any]:
        """启动开发者会话"""
        try:
            session_id = f"session_{developer_id}_{int(time.time())}"
            
            session = DeveloperSession(
                developer_id=developer_id,
                session_id=session_id,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                current_stage=WorkflowStage.PLANNING,
                status=DeveloperStatus.ACTIVE,
                current_branch=branch_name,
                files_modified=[],
                commits_count=0,
                quality_score=100.0
            )
            
            self.active_sessions[session_id] = session
            self.workflow_stats["total_sessions"] += 1
            self.workflow_stats["active_developers"] = len(self.active_sessions)
            
            # 记录到数据库
            self._save_session_to_db(session)
            
            # 记录活动日志
            self._log_activity(developer_id, session_id, "session_start", f"开发者会话启动: {branch_name}")
            
            logger.info(f"🚀 开发者会话启动: {developer_id} -> {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "developer_id": developer_id,
                "current_stage": session.current_stage.value,
                "status": session.status.value
            }
            
        except Exception as e:
            logger.error(f"❌ 启动开发者会话失败: {e}")
            return {"success": False, "error": str(e)}
    
    def update_session_activity(self, session_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新会话活动"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "会话不存在"}
            
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now()
            
            # 更新会话数据
            if "stage" in activity_data:
                session.current_stage = WorkflowStage(activity_data["stage"])
            
            if "status" in activity_data:
                session.status = DeveloperStatus(activity_data["status"])
            
            if "files_modified" in activity_data:
                session.files_modified = activity_data["files_modified"]
            
            if "commits_count" in activity_data:
                session.commits_count = activity_data["commits_count"]
                self.workflow_stats["total_commits"] += 1
            
            if "quality_score" in activity_data:
                session.quality_score = activity_data["quality_score"]
            
            # 更新数据库
            self._update_session_in_db(session)
            
            # 记录活动日志
            self._log_activity(
                session.developer_id, 
                session_id, 
                "activity_update", 
                f"会话活动更新: {activity_data}"
            )
            
            return {
                "success": True,
                "session": asdict(session),
                "updated_fields": list(activity_data.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ 更新会话活动失败: {e}")
            return {"success": False, "error": str(e)}
    
    def create_workflow_task(self, developer_id: str, stage: str, description: str) -> Dict[str, Any]:
        """创建工作流任务"""
        try:
            task_id = f"task_{developer_id}_{stage}_{int(time.time())}"
            
            task = WorkflowTask(
                task_id=task_id,
                developer_id=developer_id,
                stage=WorkflowStage(stage),
                description=description,
                created_time=datetime.now(),
                status="pending"
            )
            
            self.task_queue.append(task)
            
            # 保存到数据库
            self._save_task_to_db(task)
            
            logger.info(f"📋 工作流任务创建: {task_id} - {description}")
            
            return {
                "success": True,
                "task_id": task_id,
                "stage": stage,
                "status": "pending"
            }
            
        except Exception as e:
            logger.error(f"❌ 创建工作流任务失败: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_task_with_mcp(self, task_id: str, mcp_id: str, action: str, params: Dict) -> Dict[str, Any]:
        """通过MCP执行任务"""
        try:
            # 查找任务
            task = None
            for t in self.task_queue:
                if t.task_id == task_id:
                    task = t
                    break
            
            if not task:
                return {"success": False, "error": "任务不存在"}
            
            # 检查MCP是否注册
            if mcp_id not in self.registered_mcps:
                return {"success": False, "error": f"MCP {mcp_id} 未注册"}
            
            mcp_info = self.registered_mcps[mcp_id]
            task.status = "in_progress"
            
            # 调用MCP执行任务
            mcp_request = {
                "action": action,
                "params": params
            }
            
            response = requests.post(
                f"{mcp_info['url']}/mcp/request",
                json=mcp_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                task.status = "completed"
                task.result = result
                
                # 移动到完成队列
                self.task_queue.remove(task)
                self.completed_tasks.append(task)
                self.workflow_stats["tasks_completed"] += 1
                
                # 更新数据库
                self._update_task_in_db(task)
                
                logger.info(f"✅ 任务执行成功: {task_id} via {mcp_id}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "mcp_id": mcp_id,
                    "result": result
                }
            else:
                task.status = "failed"
                task.result = {"error": f"MCP调用失败: HTTP {response.status_code}"}
                self._update_task_in_db(task)
                
                return {"success": False, "error": f"MCP调用失败: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ 执行任务失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_developer_dashboard_data(self, developer_id: str) -> Dict[str, Any]:
        """获取开发者dashboard数据"""
        try:
            # 获取活跃会话
            active_session = None
            for session in self.active_sessions.values():
                if session.developer_id == developer_id:
                    active_session = session
                    break
            
            # 获取最近任务
            recent_tasks = [
                asdict(task) for task in self.completed_tasks[-10:]
                if task.developer_id == developer_id
            ]
            
            # 获取统计数据
            db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # 获取会话统计
                cursor.execute('''
                    SELECT COUNT(*), AVG(quality_score), SUM(commits_count)
                    FROM developer_sessions 
                    WHERE developer_id = ? AND start_time > datetime('now', '-7 days')
                ''', (developer_id,))
                
                session_stats = cursor.fetchone()
                
                # 获取最近活动
                cursor.execute('''
                    SELECT activity_type, description, timestamp
                    FROM activity_logs 
                    WHERE developer_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 20
                ''', (developer_id,))
                
                recent_activities = cursor.fetchall()
            
            dashboard_data = {
                "developer_id": developer_id,
                "current_session": asdict(active_session) if active_session else None,
                "session_stats": {
                    "sessions_this_week": session_stats[0] or 0,
                    "average_quality_score": session_stats[1] or 0.0,
                    "total_commits": session_stats[2] or 0
                },
                "recent_tasks": recent_tasks,
                "recent_activities": [
                    {
                        "type": activity[0],
                        "description": activity[1],
                        "timestamp": activity[2]
                    }
                    for activity in recent_activities
                ],
                "workflow_stats": self.workflow_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            return {"success": True, "dashboard_data": dashboard_data}
            
        except Exception as e:
            logger.error(f"❌ 获取dashboard数据失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_session_to_db(self, session: DeveloperSession):
        """保存会话到数据库"""
        db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO developer_sessions 
                (session_id, developer_id, start_time, current_stage, status, current_branch, commits_count, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.developer_id,
                session.start_time.isoformat(),
                session.current_stage.value,
                session.status.value,
                session.current_branch,
                session.commits_count,
                session.quality_score
            ))
            conn.commit()
    
    def _update_session_in_db(self, session: DeveloperSession):
        """更新数据库中的会话"""
        db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE developer_sessions 
                SET current_stage = ?, status = ?, commits_count = ?, quality_score = ?
                WHERE session_id = ?
            ''', (
                session.current_stage.value,
                session.status.value,
                session.commits_count,
                session.quality_score,
                session.session_id
            ))
            conn.commit()
    
    def _save_task_to_db(self, task: WorkflowTask):
        """保存任务到数据库"""
        db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workflow_tasks 
                (task_id, developer_id, stage, description, created_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task.task_id,
                task.developer_id,
                task.stage.value,
                task.description,
                task.created_time.isoformat(),
                task.status
            ))
            conn.commit()
    
    def _update_task_in_db(self, task: WorkflowTask):
        """更新数据库中的任务"""
        db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE workflow_tasks 
                SET status = ?, completed_time = ?, result = ?
                WHERE task_id = ?
            ''', (
                task.status,
                datetime.now().isoformat(),
                json.dumps(task.result) if task.result else None,
                task.task_id
            ))
            conn.commit()
    
    def _log_activity(self, developer_id: str, session_id: str, activity_type: str, description: str):
        """记录活动日志"""
        db_path = "/home/ubuntu/kilocode_integrated_repo/mcp/workflow/developer_flow_mcp/developer_flow.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO activity_logs 
                (developer_id, session_id, activity_type, description, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                developer_id,
                session_id,
                activity_type,
                description,
                datetime.now().isoformat()
            ))
            conn.commit()

# Flask应用创建
def create_developer_flow_server():
    """创建Developer Flow MCP服务器"""
    app = Flask(__name__)
    CORS(app)
    
    # 创建MCP实例
    dev_flow = DeveloperFlowMCP()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            "mcp_id": "developer_flow_mcp",
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "active_sessions": len(dev_flow.active_sessions),
            "registered_mcps": len(dev_flow.registered_mcps)
        })
    
    @app.route('/mcp/info', methods=['GET'])
    def mcp_info():
        """MCP基本信息"""
        return jsonify({
            "mcp_id": "developer_flow_mcp",
            "version": "1.0.0",
            "capabilities": [
                "developer_session_management",
                "workflow_task_orchestration",
                "component_mcp_registration",
                "developer_dashboard_data",
                "activity_logging"
            ],
            "description": "Developer Flow MCP - 开发者工作流管理",
            "registered_mcps": list(dev_flow.registered_mcps.keys())
        })
    
    @app.route('/mcp/request', methods=['POST'])
    def mcp_request():
        """标准MCP请求处理"""
        try:
            data = request.get_json()
            action = data.get('action')
            params = data.get('params', {})
            
            if action == 'register_component_mcp':
                result = dev_flow.register_component_mcp(
                    params.get('mcp_id'),
                    params.get('mcp_url'),
                    params.get('capabilities', [])
                )
            
            elif action == 'start_developer_session':
                result = dev_flow.start_developer_session(
                    params.get('developer_id'),
                    params.get('branch_name', 'main')
                )
            
            elif action == 'update_session_activity':
                result = dev_flow.update_session_activity(
                    params.get('session_id'),
                    params.get('activity_data', {})
                )
            
            elif action == 'create_workflow_task':
                result = dev_flow.create_workflow_task(
                    params.get('developer_id'),
                    params.get('stage'),
                    params.get('description')
                )
            
            elif action == 'execute_task_with_mcp':
                result = dev_flow.execute_task_with_mcp(
                    params.get('task_id'),
                    params.get('mcp_id'),
                    params.get('mcp_action'),
                    params.get('mcp_params', {})
                )
            
            elif action == 'get_dashboard_data':
                result = dev_flow.get_developer_dashboard_data(
                    params.get('developer_id')
                )
            
            else:
                result = {
                    "success": False,
                    "error": f"未知操作: {action}"
                }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"❌ 处理MCP请求失败: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/sessions', methods=['GET'])
    def get_active_sessions():
        """获取活跃会话"""
        sessions = [asdict(session) for session in dev_flow.active_sessions.values()]
        return jsonify({
            "success": True,
            "active_sessions": sessions,
            "total_count": len(sessions)
        })
    
    @app.route('/api/stats', methods=['GET'])
    def get_workflow_stats():
        """获取工作流统计"""
        return jsonify({
            "success": True,
            "workflow_stats": dev_flow.workflow_stats,
            "registered_mcps": dev_flow.registered_mcps
        })
    
    return app, dev_flow

if __name__ == '__main__':
    logger.info("🚀 启动 Developer Flow MCP...")
    
    app, dev_flow_instance = create_developer_flow_server()
    
    logger.info(f"📍 服务地址: http://0.0.0.0:{dev_flow_instance.port}")
    logger.info("🎯 等待组件MCP注册...")
    
    app.run(host='0.0.0.0', port=dev_flow_instance.port, debug=False)

