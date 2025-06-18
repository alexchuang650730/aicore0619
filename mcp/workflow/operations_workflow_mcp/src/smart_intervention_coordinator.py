#!/usr/bin/env python3
"""
Operations Workflow MCP - Smart Intervention Coordinator
智能介入协调器 - 协调各种智能介入操作
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InterventionType(Enum):
    """介入类型"""
    DIRECTORY_STRUCTURE = "directory_structure"
    CODE_QUALITY = "code_quality"
    DEPENDENCY_ISSUE = "dependency_issue"
    CONFIGURATION_ERROR = "configuration_error"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_VULNERABILITY = "security_vulnerability"

class InterventionPriority(Enum):
    """介入优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InterventionStatus(Enum):
    """介入状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class InterventionRequest:
    """介入请求"""
    id: str
    type: InterventionType
    priority: InterventionPriority
    description: str
    source: str  # 来源MCP
    target_mcp: str  # 目标MCP
    parameters: Dict[str, Any]
    created_at: str
    status: InterventionStatus = InterventionStatus.PENDING
    assigned_to: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class SmartInterventionCoordinator:
    """智能介入协调器"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.intervention_queue: List[InterventionRequest] = []
        self.active_interventions: Dict[str, InterventionRequest] = {}
        self.completed_interventions: List[InterventionRequest] = []
        
        # 配置文件路径
        self.config_dir = self.repo_root / "mcp" / "workflow" / "operations_workflow_mcp" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.intervention_log_file = self.config_dir / "intervention_log.json"
        self.coordinator_config_file = self.config_dir / "intervention_coordinator.json"
        
        # 加载配置和历史记录
        self._load_configuration()
        self._load_intervention_history()
        
        logger.info("🎯 Smart Intervention Coordinator 初始化完成")
    
    def _load_configuration(self):
        """加载协调器配置"""
        default_config = {
            "max_concurrent_interventions": 3,
            "intervention_timeout": 300,  # 5分钟
            "auto_retry_failed": True,
            "max_retry_attempts": 3,
            "priority_weights": {
                "critical": 100,
                "high": 75,
                "medium": 50,
                "low": 25
            },
            "mcp_capabilities": {
                "development_intervention_mcp": [
                    "code_quality",
                    "dependency_issue",
                    "configuration_error"
                ],
                "directory_structure_mcp": [
                    "directory_structure"
                ],
                "local_model_mcp": [
                    "performance_issue"
                ]
            }
        }
        
        if self.coordinator_config_file.exists():
            try:
                with open(self.coordinator_config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"❌ 加载配置失败: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self._save_configuration()
    
    def _save_configuration(self):
        """保存协调器配置"""
        try:
            with open(self.coordinator_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ 保存配置失败: {e}")
    
    def _load_intervention_history(self):
        """加载介入历史记录"""
        if self.intervention_log_file.exists():
            try:
                with open(self.intervention_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for item in data.get('completed_interventions', []):
                        intervention = InterventionRequest(
                            id=item['id'],
                            type=InterventionType(item['type']),
                            priority=InterventionPriority(item['priority']),
                            description=item['description'],
                            source=item['source'],
                            target_mcp=item['target_mcp'],
                            parameters=item['parameters'],
                            created_at=item['created_at'],
                            status=InterventionStatus(item['status']),
                            assigned_to=item.get('assigned_to'),
                            started_at=item.get('started_at'),
                            completed_at=item.get('completed_at'),
                            result=item.get('result'),
                            error_message=item.get('error_message')
                        )
                        self.completed_interventions.append(intervention)
                        
                logger.info(f"📋 加载了 {len(self.completed_interventions)} 个历史介入记录")
            except Exception as e:
                logger.error(f"❌ 加载介入历史失败: {e}")
    
    def _save_intervention_history(self):
        """保存介入历史记录"""
        try:
            data = {
                "completed_interventions": [
                    asdict(intervention) for intervention in self.completed_interventions
                ],
                "last_updated": datetime.now().isoformat()
            }
            
            # 转换Enum为字符串
            for item in data["completed_interventions"]:
                item['type'] = item['type'].value if hasattr(item['type'], 'value') else item['type']
                item['priority'] = item['priority'].value if hasattr(item['priority'], 'value') else item['priority']
                item['status'] = item['status'].value if hasattr(item['status'], 'value') else item['status']
            
            with open(self.intervention_log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ 保存介入历史失败: {e}")
    
    def request_intervention(self, intervention_type: InterventionType, 
                           priority: InterventionPriority, description: str,
                           source: str, parameters: Dict[str, Any] = None) -> str:
        """请求介入"""
        
        # 生成介入ID
        intervention_id = f"INT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.intervention_queue)}"
        
        # 确定目标MCP
        target_mcp = self._determine_target_mcp(intervention_type)
        
        # 创建介入请求
        request = InterventionRequest(
            id=intervention_id,
            type=intervention_type,
            priority=priority,
            description=description,
            source=source,
            target_mcp=target_mcp,
            parameters=parameters or {},
            created_at=datetime.now().isoformat()
        )
        
        # 添加到队列
        self.intervention_queue.append(request)
        
        # 按优先级排序
        self._sort_intervention_queue()
        
        logger.info(f"📝 创建介入请求: {intervention_id} ({intervention_type.value})")
        
        return intervention_id
    
    def _determine_target_mcp(self, intervention_type: InterventionType) -> str:
        """确定目标MCP"""
        type_str = intervention_type.value
        
        for mcp_name, capabilities in self.config["mcp_capabilities"].items():
            if type_str in capabilities:
                return mcp_name
        
        # 默认使用development_intervention_mcp
        return "development_intervention_mcp"
    
    def _sort_intervention_queue(self):
        """按优先级排序介入队列"""
        priority_weights = self.config["priority_weights"]
        
        self.intervention_queue.sort(
            key=lambda x: priority_weights.get(x.priority.value, 0),
            reverse=True
        )
    
    async def process_intervention_queue(self):
        """处理介入队列"""
        max_concurrent = self.config["max_concurrent_interventions"]
        
        while self.intervention_queue and len(self.active_interventions) < max_concurrent:
            request = self.intervention_queue.pop(0)
            
            # 开始处理介入
            await self._start_intervention(request)
    
    async def _start_intervention(self, request: InterventionRequest):
        """开始处理介入"""
        try:
            request.status = InterventionStatus.IN_PROGRESS
            request.started_at = datetime.now().isoformat()
            self.active_interventions[request.id] = request
            
            logger.info(f"🚀 开始处理介入: {request.id}")
            
            # 根据介入类型调用相应的处理方法
            if request.type == InterventionType.DIRECTORY_STRUCTURE:
                result = await self._handle_directory_structure_intervention(request)
            elif request.type == InterventionType.CODE_QUALITY:
                result = await self._handle_code_quality_intervention(request)
            elif request.type == InterventionType.DEPENDENCY_ISSUE:
                result = await self._handle_dependency_intervention(request)
            elif request.type == InterventionType.CONFIGURATION_ERROR:
                result = await self._handle_configuration_intervention(request)
            else:
                result = await self._handle_generic_intervention(request)
            
            # 完成介入
            await self._complete_intervention(request, result)
            
        except Exception as e:
            await self._fail_intervention(request, str(e))
    
    async def _handle_directory_structure_intervention(self, request: InterventionRequest) -> Dict[str, Any]:
        """处理目录结构介入"""
        logger.info(f"🗂️ 处理目录结构介入: {request.description}")
        
        # 模拟目录结构修复
        await asyncio.sleep(1)  # 模拟处理时间
        
        return {
            "action": "directory_structure_fix",
            "fixed_issues": ["移动错位文件", "创建缺失目录", "更新文档"],
            "files_affected": 5,
            "success": True
        }
    
    async def _handle_code_quality_intervention(self, request: InterventionRequest) -> Dict[str, Any]:
        """处理代码质量介入"""
        logger.info(f"🔧 处理代码质量介入: {request.description}")
        
        # 模拟代码质量修复
        await asyncio.sleep(2)  # 模拟处理时间
        
        return {
            "action": "code_quality_fix",
            "issues_found": 8,
            "issues_fixed": 6,
            "suggestions": ["添加类型注解", "优化函数复杂度", "移除未使用导入"],
            "success": True
        }
    
    async def _handle_dependency_intervention(self, request: InterventionRequest) -> Dict[str, Any]:
        """处理依赖问题介入"""
        logger.info(f"📦 处理依赖问题介入: {request.description}")
        
        await asyncio.sleep(1.5)
        
        return {
            "action": "dependency_fix",
            "dependencies_updated": 3,
            "conflicts_resolved": 1,
            "success": True
        }
    
    async def _handle_configuration_intervention(self, request: InterventionRequest) -> Dict[str, Any]:
        """处理配置错误介入"""
        logger.info(f"⚙️ 处理配置错误介入: {request.description}")
        
        await asyncio.sleep(1)
        
        return {
            "action": "configuration_fix",
            "configs_updated": 2,
            "validation_passed": True,
            "success": True
        }
    
    async def _handle_generic_intervention(self, request: InterventionRequest) -> Dict[str, Any]:
        """处理通用介入"""
        logger.info(f"🔄 处理通用介入: {request.description}")
        
        await asyncio.sleep(1)
        
        return {
            "action": "generic_intervention",
            "processed": True,
            "success": True
        }
    
    async def _complete_intervention(self, request: InterventionRequest, result: Dict[str, Any]):
        """完成介入"""
        request.status = InterventionStatus.COMPLETED
        request.completed_at = datetime.now().isoformat()
        request.result = result
        
        # 从活跃列表移除，添加到完成列表
        if request.id in self.active_interventions:
            del self.active_interventions[request.id]
        
        self.completed_interventions.append(request)
        
        # 保存历史记录
        self._save_intervention_history()
        
        logger.info(f"✅ 介入完成: {request.id}")
    
    async def _fail_intervention(self, request: InterventionRequest, error_message: str):
        """介入失败"""
        request.status = InterventionStatus.FAILED
        request.completed_at = datetime.now().isoformat()
        request.error_message = error_message
        
        # 从活跃列表移除，添加到完成列表
        if request.id in self.active_interventions:
            del self.active_interventions[request.id]
        
        self.completed_interventions.append(request)
        
        # 保存历史记录
        self._save_intervention_history()
        
        logger.error(f"❌ 介入失败: {request.id} - {error_message}")
    
    def get_intervention_status(self, intervention_id: str) -> Optional[Dict[str, Any]]:
        """获取介入状态"""
        # 检查活跃介入
        if intervention_id in self.active_interventions:
            request = self.active_interventions[intervention_id]
            return asdict(request)
        
        # 检查队列中的介入
        for request in self.intervention_queue:
            if request.id == intervention_id:
                return asdict(request)
        
        # 检查已完成的介入
        for request in self.completed_interventions:
            if request.id == intervention_id:
                return asdict(request)
        
        return None
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """获取协调器状态"""
        return {
            "queue_size": len(self.intervention_queue),
            "active_interventions": len(self.active_interventions),
            "completed_interventions": len(self.completed_interventions),
            "total_processed": len(self.completed_interventions),
            "success_rate": self._calculate_success_rate(),
            "average_processing_time": self._calculate_average_processing_time(),
            "queue_details": [
                {
                    "id": req.id,
                    "type": req.type.value,
                    "priority": req.priority.value,
                    "source": req.source
                } for req in self.intervention_queue
            ],
            "active_details": [
                {
                    "id": req.id,
                    "type": req.type.value,
                    "priority": req.priority.value,
                    "source": req.source,
                    "started_at": req.started_at
                } for req in self.active_interventions.values()
            ]
        }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.completed_interventions:
            return 0.0
        
        successful = sum(1 for req in self.completed_interventions 
                        if req.status == InterventionStatus.COMPLETED)
        
        return (successful / len(self.completed_interventions)) * 100
    
    def _calculate_average_processing_time(self) -> float:
        """计算平均处理时间"""
        if not self.completed_interventions:
            return 0.0
        
        total_time = 0
        count = 0
        
        for req in self.completed_interventions:
            if req.started_at and req.completed_at:
                try:
                    start = datetime.fromisoformat(req.started_at)
                    end = datetime.fromisoformat(req.completed_at)
                    total_time += (end - start).total_seconds()
                    count += 1
                except:
                    continue
        
        return total_time / count if count > 0 else 0.0

if __name__ == "__main__":
    async def test_coordinator():
        """测试协调器"""
        coordinator = SmartInterventionCoordinator()
        
        print("🎯 测试智能介入协调器")
        print("=" * 50)
        
        # 创建测试介入请求
        print("📝 创建测试介入请求...")
        
        req1 = coordinator.request_intervention(
            InterventionType.DIRECTORY_STRUCTURE,
            InterventionPriority.HIGH,
            "修复目录结构违规",
            "operations_workflow_mcp",
            {"target_directory": "/mcp"}
        )
        
        req2 = coordinator.request_intervention(
            InterventionType.CODE_QUALITY,
            InterventionPriority.MEDIUM,
            "修复代码质量问题",
            "development_intervention_mcp",
            {"files": ["test.py", "main.py"]}
        )
        
        req3 = coordinator.request_intervention(
            InterventionType.CONFIGURATION_ERROR,
            InterventionPriority.CRITICAL,
            "修复配置错误",
            "operations_workflow_mcp",
            {"config_file": "config.toml"}
        )
        
        print(f"创建了3个介入请求: {req1}, {req2}, {req3}")
        
        # 显示协调器状态
        print("\n📊 协调器状态:")
        status = coordinator.get_coordinator_status()
        print(f"队列大小: {status['queue_size']}")
        print(f"活跃介入: {status['active_interventions']}")
        
        # 处理介入队列
        print("\n🚀 处理介入队列...")
        await coordinator.process_intervention_queue()
        
        # 等待处理完成
        while coordinator.active_interventions:
            await asyncio.sleep(0.5)
        
        # 显示最终状态
        print("\n✅ 处理完成，最终状态:")
        final_status = coordinator.get_coordinator_status()
        print(f"已完成介入: {final_status['completed_interventions']}")
        print(f"成功率: {final_status['success_rate']:.1f}%")
        print(f"平均处理时间: {final_status['average_processing_time']:.1f}秒")
    
    # 运行测试
    asyncio.run(test_coordinator())

