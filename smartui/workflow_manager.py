"""
智慧UI工作流管理器
管理編碼、部署、測試三大工作流
支持工作流的創建、執行、監控和管理
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """工作流類型"""
    CODING = "coding"
    DEPLOYMENT = "deployment"
    TESTING = "testing"

class WorkflowStatus(Enum):
    """工作流狀態"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class WorkflowStep:
    """工作流步驟"""
    id: str
    name: str
    type: str
    config: Dict[str, Any]
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class Workflow:
    """工作流數據模型"""
    id: Optional[int] = None
    project_id: int = 0
    name: str = ""
    type: WorkflowType = WorkflowType.CODING
    description: str = ""
    steps: List[WorkflowStep] = None
    config: Dict[str, Any] = None
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.config is None:
            self.config = {}

class WorkflowManager:
    """智慧UI工作流管理器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.sync_engine = None
        
        # 預定義工作流模板
        self.workflow_templates = {
            WorkflowType.CODING: {
                "name": "智能編碼工作流",
                "description": "AI輔助的智能編碼工作流",
                "steps": [
                    {
                        "id": "code_analysis",
                        "name": "代碼分析",
                        "type": "analysis",
                        "config": {"ai_enabled": True, "quality_check": True}
                    },
                    {
                        "id": "code_generation",
                        "name": "代碼生成",
                        "type": "generation",
                        "config": {"template_based": True, "ai_suggestions": True}
                    },
                    {
                        "id": "code_review",
                        "name": "代碼審查",
                        "type": "review",
                        "config": {"automated_review": True, "peer_review": False}
                    },
                    {
                        "id": "git_commit",
                        "name": "Git提交",
                        "type": "git",
                        "config": {"auto_commit": False, "commit_message_ai": True}
                    }
                ]
            },
            WorkflowType.DEPLOYMENT: {
                "name": "智能部署工作流",
                "description": "自動化CI/CD部署工作流",
                "steps": [
                    {
                        "id": "build_preparation",
                        "name": "構建準備",
                        "type": "preparation",
                        "config": {"dependency_check": True, "environment_setup": True}
                    },
                    {
                        "id": "build_process",
                        "name": "構建過程",
                        "type": "build",
                        "config": {"parallel_build": True, "optimization": True}
                    },
                    {
                        "id": "deployment_staging",
                        "name": "部署到測試環境",
                        "type": "deploy",
                        "config": {"environment": "staging", "rollback_enabled": True}
                    },
                    {
                        "id": "deployment_production",
                        "name": "部署到生產環境",
                        "type": "deploy",
                        "config": {"environment": "production", "blue_green": True}
                    }
                ]
            },
            WorkflowType.TESTING: {
                "name": "智能測試工作流",
                "description": "全面的自動化測試工作流",
                "steps": [
                    {
                        "id": "unit_testing",
                        "name": "單元測試",
                        "type": "test",
                        "config": {"coverage_threshold": 80, "parallel_execution": True}
                    },
                    {
                        "id": "integration_testing",
                        "name": "集成測試",
                        "type": "test",
                        "config": {"api_testing": True, "database_testing": True}
                    },
                    {
                        "id": "performance_testing",
                        "name": "性能測試",
                        "type": "test",
                        "config": {"load_testing": True, "stress_testing": True}
                    },
                    {
                        "id": "security_testing",
                        "name": "安全測試",
                        "type": "test",
                        "config": {"vulnerability_scan": True, "penetration_test": False}
                    }
                ]
            }
        }
    
    def set_sync_engine(self, sync_engine):
        """設置同步引擎"""
        self.sync_engine = sync_engine
    
    def create_workflow(self, project_id: int, name: str, workflow_type: WorkflowType,
                       description: str = "", custom_steps: List[Dict] = None) -> Optional[Workflow]:
        """創建新工作流"""
        try:
            # 獲取模板或使用自定義步驟
            if custom_steps:
                steps = [WorkflowStep(**step) for step in custom_steps]
            else:
                template = self.workflow_templates.get(workflow_type)
                if template:
                    steps = [WorkflowStep(**step) for step in template["steps"]]
                    if not description:
                        description = template["description"]
                else:
                    steps = []
            
            # 創建工作流配置
            config = {
                "auto_execute": False,
                "notification_enabled": True,
                "retry_on_failure": True,
                "max_retries": 3
            }
            
            now = datetime.now()
            
            # 保存到數據庫
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            workflow_data = {
                "steps": [step.__dict__ for step in steps],
                "config": config
            }
            
            cursor.execute("""
                INSERT INTO workflows (project_id, name, type, config, status, created_at, updated_at, last_sync)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id, name, workflow_type.value, json.dumps(workflow_data),
                WorkflowStatus.DRAFT.value, now, now, now
            ))
            
            workflow_id = cursor.lastrowid
            conn.commit()
            
            # 創建工作流對象
            workflow = Workflow(
                id=workflow_id,
                project_id=project_id,
                name=name,
                type=workflow_type,
                description=description,
                steps=steps,
                config=config,
                status=WorkflowStatus.DRAFT,
                created_at=now,
                updated_at=now,
                last_sync=now
            )
            
            # 添加到同步隊列
            if self.sync_engine:
                self.sync_engine.add_sync_record(
                    "workflows", workflow_id, "insert", self._workflow_to_dict(workflow)
                )
            
            logger.info(f"工作流創建成功: {name} ({workflow_type.value})")
            return workflow
            
        except Exception as e:
            logger.error(f"創建工作流失敗: {e}")
            return None
    
    def get_workflow_by_id(self, workflow_id: int) -> Optional[Workflow]:
        """根據ID獲取工作流"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_workflow(row)
            return None
            
        except Exception as e:
            logger.error(f"獲取工作流失敗: {e}")
            return None
    
    def get_workflows_by_project(self, project_id: int) -> List[Workflow]:
        """獲取項目的所有工作流"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM workflows 
                WHERE project_id = ? 
                ORDER BY created_at DESC
            """, (project_id,))
            
            rows = cursor.fetchall()
            return [self._row_to_workflow(row) for row in rows]
            
        except Exception as e:
            logger.error(f"獲取項目工作流失敗: {e}")
            return []
    
    def get_workflows_by_type(self, workflow_type: WorkflowType) -> List[Workflow]:
        """根據類型獲取工作流"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM workflows 
                WHERE type = ? 
                ORDER BY created_at DESC
            """, (workflow_type.value,))
            
            rows = cursor.fetchall()
            return [self._row_to_workflow(row) for row in rows]
            
        except Exception as e:
            logger.error(f"獲取工作流失敗: {e}")
            return []
    
    def update_workflow_status(self, workflow_id: int, status: WorkflowStatus) -> bool:
        """更新工作流狀態"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                UPDATE workflows 
                SET status = ?, updated_at = ?, last_sync = ?
                WHERE id = ?
            """, (status.value, now, now, workflow_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                
                # 添加到同步隊列
                if self.sync_engine:
                    self.sync_engine.add_sync_record(
                        "workflows", workflow_id, "update",
                        {"status": status.value, "updated_at": now, "last_sync": now}
                    )
                
                logger.info(f"工作流 {workflow_id} 狀態更新為 {status.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"更新工作流狀態失敗: {e}")
            return False
    
    def execute_workflow(self, workflow_id: int) -> bool:
        """執行工作流"""
        workflow = self.get_workflow_by_id(workflow_id)
        if not workflow:
            logger.error(f"工作流 {workflow_id} 不存在")
            return False
        
        if workflow.status != WorkflowStatus.ACTIVE:
            logger.error(f"工作流 {workflow_id} 狀態不是active，無法執行")
            return False
        
        try:
            # 更新狀態為運行中
            self.update_workflow_status(workflow_id, WorkflowStatus.RUNNING)
            
            # 執行工作流步驟
            success = self._execute_workflow_steps(workflow)
            
            # 更新最終狀態
            final_status = WorkflowStatus.COMPLETED if success else WorkflowStatus.FAILED
            self.update_workflow_status(workflow_id, final_status)
            
            logger.info(f"工作流 {workflow_id} 執行{'成功' if success else '失敗'}")
            return success
            
        except Exception as e:
            logger.error(f"執行工作流失敗: {e}")
            self.update_workflow_status(workflow_id, WorkflowStatus.FAILED)
            return False
    
    def _execute_workflow_steps(self, workflow: Workflow) -> bool:
        """執行工作流步驟"""
        logger.info(f"開始執行工作流: {workflow.name}")
        
        for step in workflow.steps:
            logger.info(f"執行步驟: {step.name}")
            
            # 這裡是步驟執行的模擬
            # 實際實現中會根據步驟類型調用相應的執行器
            success = self._execute_step(step, workflow)
            
            if not success:
                logger.error(f"步驟 {step.name} 執行失敗")
                return False
        
        logger.info(f"工作流 {workflow.name} 所有步驟執行完成")
        return True
    
    def _execute_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """執行單個步驟"""
        # 這是步驟執行的模擬實現
        # 實際實現中會根據步驟類型調用相應的處理器
        
        step_processors = {
            "analysis": self._process_analysis_step,
            "generation": self._process_generation_step,
            "review": self._process_review_step,
            "git": self._process_git_step,
            "preparation": self._process_preparation_step,
            "build": self._process_build_step,
            "deploy": self._process_deploy_step,
            "test": self._process_test_step
        }
        
        processor = step_processors.get(step.type)
        if processor:
            return processor(step, workflow)
        else:
            logger.warning(f"未知的步驟類型: {step.type}")
            return True  # 暫時返回成功
    
    def _process_analysis_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理分析步驟"""
        logger.info(f"執行代碼分析: {step.config}")
        return True
    
    def _process_generation_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理生成步驟"""
        logger.info(f"執行代碼生成: {step.config}")
        return True
    
    def _process_review_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理審查步驟"""
        logger.info(f"執行代碼審查: {step.config}")
        return True
    
    def _process_git_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理Git步驟"""
        logger.info(f"執行Git操作: {step.config}")
        return True
    
    def _process_preparation_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理準備步驟"""
        logger.info(f"執行構建準備: {step.config}")
        return True
    
    def _process_build_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理構建步驟"""
        logger.info(f"執行構建過程: {step.config}")
        return True
    
    def _process_deploy_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理部署步驟"""
        logger.info(f"執行部署操作: {step.config}")
        return True
    
    def _process_test_step(self, step: WorkflowStep, workflow: Workflow) -> bool:
        """處理測試步驟"""
        logger.info(f"執行測試: {step.config}")
        return True
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """獲取工作流統計信息"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            # 總工作流數
            cursor.execute("SELECT COUNT(*) FROM workflows")
            total_workflows = cursor.fetchone()[0]
            
            # 按類型統計
            cursor.execute("""
                SELECT type, COUNT(*) as count
                FROM workflows
                GROUP BY type
            """)
            type_stats = dict(cursor.fetchall())
            
            # 按狀態統計
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM workflows
                GROUP BY status
            """)
            status_stats = dict(cursor.fetchall())
            
            return {
                "total_workflows": total_workflows,
                "type_distribution": type_stats,
                "status_distribution": status_stats
            }
            
        except Exception as e:
            logger.error(f"獲取工作流統計失敗: {e}")
            return {}
    
    def _row_to_workflow(self, row) -> Workflow:
        """數據庫行轉工作流對象"""
        config_data = json.loads(row['config']) if row['config'] else {}
        steps_data = config_data.get('steps', [])
        steps = [WorkflowStep(**step) for step in steps_data]
        
        return Workflow(
            id=row['id'],
            project_id=row['project_id'],
            name=row['name'],
            type=WorkflowType(row['type']),
            steps=steps,
            config=config_data.get('config', {}),
            status=WorkflowStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None
        )
    
    def _workflow_to_dict(self, workflow: Workflow) -> Dict[str, Any]:
        """工作流對象轉字典"""
        return {
            "project_id": workflow.project_id,
            "name": workflow.name,
            "type": workflow.type.value,
            "config": json.dumps({
                "steps": [step.__dict__ for step in workflow.steps],
                "config": workflow.config
            }),
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "last_sync": workflow.last_sync.isoformat() if workflow.last_sync else None
        }

