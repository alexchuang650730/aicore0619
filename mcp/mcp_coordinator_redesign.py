#!/usr/bin/env python3
"""
MCP协调器架构重设计

基于交互数据统一管理的原则，重新设计MCPCoordinator架构，
确保所有交互数据由中央协调器统一掌控，各MCP专注业务逻辑。

设计原则：
1. MCPCoordinator统一管理所有交互数据
2. 各MCP只负责业务逻辑处理，不存储交互数据
3. 智慧路由基于全局交互数据进行决策
4. 统一的数据格式和访问接口
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# ============================================================================
# 1. 核心数据结构定义
# ============================================================================

class MCPType(Enum):
    """MCP类型枚举"""
    LOCAL_MODEL = "local_model_mcp"
    CLOUD_SEARCH = "cloud_search_mcp"
    CLOUD_EDGE_DATA = "cloud_edge_data_mcp"

class InteractionType(Enum):
    """交互类型枚举"""
    OCR_REQUEST = "ocr_request"
    MODEL_INFERENCE = "model_inference"
    DATA_PROCESSING = "data_processing"
    ROUTING_DECISION = "routing_decision"
    SYSTEM_MONITORING = "system_monitoring"

class ProcessingLocation(Enum):
    """处理位置"""
    LOCAL_ONLY = "local_only"
    CLOUD_ONLY = "cloud_only"
    HYBRID = "hybrid"

@dataclass
class InteractionRecord:
    """交互记录数据结构"""
    id: str
    session_id: str
    timestamp: str
    interaction_type: InteractionType
    mcp_type: MCPType
    user_request: str
    mcp_response: str
    processing_location: ProcessingLocation
    performance_metrics: Dict[str, Any]
    routing_decision: Dict[str, Any]
    context: Dict[str, Any]
    tags: List[str]

@dataclass
class MCPPerformanceMetrics:
    """MCP性能指标"""
    mcp_type: MCPType
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    average_cost: float
    quality_score: float
    last_updated: str

@dataclass
class RoutingDecisionRecord:
    """路由决策记录"""
    decision_id: str
    timestamp: str
    user_request: str
    selected_mcp: MCPType
    processing_location: ProcessingLocation
    decision_factors: Dict[str, Any]
    confidence: float
    alternative_options: List[Dict[str, Any]]
    execution_result: Dict[str, Any]

# ============================================================================
# 2. 交互数据管理器
# ============================================================================

class InteractionDataManager:
    """
    交互数据管理器
    
    统一管理所有MCP的交互数据，提供数据存储、查询、分析功能
    """
    
    def __init__(self, base_dir: str = "/home/ubuntu/powerautomation/interaction_data"):
        self.base_dir = Path(base_dir)
        self.setup_directory_structure()
        self.interaction_records: List[InteractionRecord] = []
        self.routing_decisions: List[RoutingDecisionRecord] = []
        self.mcp_metrics: Dict[MCPType, MCPPerformanceMetrics] = {}
        self.logger = logging.getLogger("InteractionDataManager")
        
        # 初始化MCP性能指标
        self._initialize_mcp_metrics()
    
    def setup_directory_structure(self):
        """设置目录结构"""
        directories = [
            "interactions/ocr_requests",
            "interactions/model_inference", 
            "interactions/data_processing",
            "routing/decisions",
            "routing/performance",
            "analytics/patterns",
            "analytics/optimization",
            "exports/reports",
            "exports/datasets"
        ]
        
        for directory in directories:
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)
    
    def _initialize_mcp_metrics(self):
        """初始化MCP性能指标"""
        for mcp_type in MCPType:
            self.mcp_metrics[mcp_type] = MCPPerformanceMetrics(
                mcp_type=mcp_type,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                average_response_time=0.0,
                average_cost=0.0,
                quality_score=0.0,
                last_updated=datetime.now().isoformat()
            )
    
    def record_interaction(self, 
                          session_id: str,
                          interaction_type: InteractionType,
                          mcp_type: MCPType,
                          user_request: str,
                          mcp_response: str,
                          processing_location: ProcessingLocation,
                          performance_metrics: Dict[str, Any],
                          routing_decision: Dict[str, Any] = None,
                          context: Dict[str, Any] = None,
                          tags: List[str] = None) -> str:
        """
        记录交互数据
        
        Args:
            session_id: 会话ID
            interaction_type: 交互类型
            mcp_type: MCP类型
            user_request: 用户请求
            mcp_response: MCP响应
            processing_location: 处理位置
            performance_metrics: 性能指标
            routing_decision: 路由决策信息
            context: 上下文信息
            tags: 标签
            
        Returns:
            交互记录ID
        """
        
        # 生成交互记录ID
        interaction_id = self._generate_interaction_id(session_id, mcp_type)
        
        # 创建交互记录
        record = InteractionRecord(
            id=interaction_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            interaction_type=interaction_type,
            mcp_type=mcp_type,
            user_request=user_request,
            mcp_response=mcp_response,
            processing_location=processing_location,
            performance_metrics=performance_metrics or {},
            routing_decision=routing_decision or {},
            context=context or {},
            tags=tags or []
        )
        
        # 存储记录
        self.interaction_records.append(record)
        
        # 更新MCP性能指标
        self._update_mcp_metrics(mcp_type, performance_metrics)
        
        # 持久化存储
        self._save_interaction_record(record)
        
        self.logger.info(f"记录交互数据: {interaction_id} ({mcp_type.value})")
        
        return interaction_id
    
    def record_routing_decision(self,
                               user_request: str,
                               selected_mcp: MCPType,
                               processing_location: ProcessingLocation,
                               decision_factors: Dict[str, Any],
                               confidence: float,
                               alternative_options: List[Dict[str, Any]] = None,
                               execution_result: Dict[str, Any] = None) -> str:
        """
        记录路由决策
        
        Args:
            user_request: 用户请求
            selected_mcp: 选择的MCP
            processing_location: 处理位置
            decision_factors: 决策因素
            confidence: 置信度
            alternative_options: 备选方案
            execution_result: 执行结果
            
        Returns:
            决策记录ID
        """
        
        decision_id = self._generate_decision_id()
        
        decision_record = RoutingDecisionRecord(
            decision_id=decision_id,
            timestamp=datetime.now().isoformat(),
            user_request=user_request,
            selected_mcp=selected_mcp,
            processing_location=processing_location,
            decision_factors=decision_factors,
            confidence=confidence,
            alternative_options=alternative_options or [],
            execution_result=execution_result or {}
        )
        
        self.routing_decisions.append(decision_record)
        self._save_routing_decision(decision_record)
        
        self.logger.info(f"记录路由决策: {decision_id} -> {selected_mcp.value}")
        
        return decision_id
    
    def _generate_interaction_id(self, session_id: str, mcp_type: MCPType) -> str:
        """生成交互记录ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{session_id}_{mcp_type.value}_{time.time()}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"int_{timestamp}_{hash_suffix}"
    
    def _generate_decision_id(self) -> str:
        """生成决策记录ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"dec_{timestamp}_{hash_suffix}"
    
    def _update_mcp_metrics(self, mcp_type: MCPType, performance_metrics: Dict[str, Any]):
        """更新MCP性能指标"""
        
        metrics = self.mcp_metrics[mcp_type]
        
        # 更新请求计数
        metrics.total_requests += 1
        
        # 更新成功/失败计数
        if performance_metrics.get("success", True):
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        # 更新平均响应时间
        response_time = performance_metrics.get("response_time", 0.0)
        if response_time > 0:
            total_time = metrics.average_response_time * (metrics.total_requests - 1) + response_time
            metrics.average_response_time = total_time / metrics.total_requests
        
        # 更新平均成本
        cost = performance_metrics.get("cost", 0.0)
        if cost > 0:
            total_cost = metrics.average_cost * (metrics.successful_requests - 1) + cost
            metrics.average_cost = total_cost / max(1, metrics.successful_requests)
        
        # 更新质量评分
        quality = performance_metrics.get("quality_score", 0.0)
        if quality > 0:
            total_quality = metrics.quality_score * (metrics.successful_requests - 1) + quality
            metrics.quality_score = total_quality / max(1, metrics.successful_requests)
        
        metrics.last_updated = datetime.now().isoformat()
    
    def _save_interaction_record(self, record: InteractionRecord):
        """保存交互记录到文件"""
        
        # 根据交互类型选择目录
        type_dir = {
            InteractionType.OCR_REQUEST: "ocr_requests",
            InteractionType.MODEL_INFERENCE: "model_inference",
            InteractionType.DATA_PROCESSING: "data_processing"
        }.get(record.interaction_type, "general")
        
        file_path = self.base_dir / "interactions" / type_dir / f"{record.id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(record), f, indent=2, ensure_ascii=False, default=str)
    
    def _save_routing_decision(self, decision: RoutingDecisionRecord):
        """保存路由决策到文件"""
        
        file_path = self.base_dir / "routing" / "decisions" / f"{decision.decision_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(decision), f, indent=2, ensure_ascii=False, default=str)
    
    def get_mcp_performance(self, mcp_type: MCPType = None) -> Union[MCPPerformanceMetrics, Dict[MCPType, MCPPerformanceMetrics]]:
        """获取MCP性能指标"""
        
        if mcp_type:
            return self.mcp_metrics[mcp_type]
        else:
            return self.mcp_metrics.copy()
    
    def get_interaction_history(self, 
                               session_id: str = None,
                               mcp_type: MCPType = None,
                               interaction_type: InteractionType = None,
                               limit: int = 100) -> List[InteractionRecord]:
        """获取交互历史"""
        
        filtered_records = self.interaction_records
        
        if session_id:
            filtered_records = [r for r in filtered_records if r.session_id == session_id]
        
        if mcp_type:
            filtered_records = [r for r in filtered_records if r.mcp_type == mcp_type]
        
        if interaction_type:
            filtered_records = [r for r in filtered_records if r.interaction_type == interaction_type]
        
        # 按时间倒序排列，返回最新的记录
        filtered_records.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_records[:limit]
    
    def get_routing_analytics(self) -> Dict[str, Any]:
        """获取路由分析数据"""
        
        if not self.routing_decisions:
            return {"total_decisions": 0}
        
        # 统计各MCP的选择次数
        mcp_selection_count = {}
        location_count = {}
        confidence_scores = []
        
        for decision in self.routing_decisions:
            mcp_type = decision.selected_mcp
            location = decision.processing_location
            
            mcp_selection_count[mcp_type] = mcp_selection_count.get(mcp_type, 0) + 1
            location_count[location] = location_count.get(location, 0) + 1
            confidence_scores.append(decision.confidence)
        
        return {
            "total_decisions": len(self.routing_decisions),
            "mcp_selection_distribution": {k.value: v for k, v in mcp_selection_count.items()},
            "location_distribution": {k.value: v for k, v in location_count.items()},
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "confidence_range": {
                "min": min(confidence_scores),
                "max": max(confidence_scores)
            }
        }
    
    def export_analytics_report(self) -> Dict[str, Any]:
        """导出分析报告"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_interactions": len(self.interaction_records),
                "total_routing_decisions": len(self.routing_decisions)
            },
            "mcp_performance": {k.value: asdict(v) for k, v in self.mcp_metrics.items()},
            "routing_analytics": self.get_routing_analytics(),
            "interaction_patterns": self._analyze_interaction_patterns()
        }
        
        # 保存报告
        report_path = self.base_dir / "exports" / "reports" / f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return report
    
    def _analyze_interaction_patterns(self) -> Dict[str, Any]:
        """分析交互模式"""
        
        if not self.interaction_records:
            return {}
        
        # 按小时统计交互量
        hourly_distribution = {}
        interaction_type_distribution = {}
        
        for record in self.interaction_records:
            # 提取小时
            hour = datetime.fromisoformat(record.timestamp).hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
            
            # 统计交互类型
            int_type = record.interaction_type.value
            interaction_type_distribution[int_type] = interaction_type_distribution.get(int_type, 0) + 1
        
        return {
            "hourly_distribution": hourly_distribution,
            "interaction_type_distribution": interaction_type_distribution,
            "peak_hour": max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else None
        }

# ============================================================================
# 3. MCPCoordinator重新设计
# ============================================================================

class MCPCoordinator:
    """
    MCP协调器
    
    统一管理所有MCP，掌控交互数据，实现智慧路由
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.interaction_manager = InteractionDataManager()
        self.registered_mcps: Dict[MCPType, Any] = {}
        self.current_session_id = self._generate_session_id()
        self.logger = logging.getLogger("MCPCoordinator")
        
        # 智慧路由相关
        self.routing_history: List[Dict[str, Any]] = []
        
        self.logger.info("MCPCoordinator初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "routing": {
                "enable_smart_routing": True,
                "learning_enabled": True,
                "fallback_enabled": True
            },
            "data_management": {
                "auto_export_interval": 3600,  # 1小时
                "max_memory_records": 10000,
                "enable_analytics": True
            },
            "performance": {
                "response_time_threshold": 30.0,
                "quality_threshold": 0.8,
                "cost_threshold": 0.01
            }
        }
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{hash_suffix}"
    
    def register_mcp(self, mcp_type: MCPType, mcp_instance: Any):
        """注册MCP实例"""
        
        self.registered_mcps[mcp_type] = mcp_instance
        self.logger.info(f"注册MCP: {mcp_type.value}")
    
    async def process_request(self, 
                            user_request: str,
                            request_type: str = "auto",
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_request: 用户请求
            request_type: 请求类型
            context: 上下文信息
            
        Returns:
            处理结果
        """
        
        start_time = time.time()
        
        try:
            # 1. 智慧路由决策
            routing_result = await self._make_routing_decision(user_request, request_type, context)
            
            # 2. 执行MCP处理
            mcp_result = await self._execute_mcp_request(
                routing_result["selected_mcp"],
                user_request,
                routing_result["processing_location"],
                context
            )
            
            # 3. 记录交互数据
            interaction_id = self.interaction_manager.record_interaction(
                session_id=self.current_session_id,
                interaction_type=self._classify_interaction_type(request_type),
                mcp_type=routing_result["selected_mcp"],
                user_request=user_request,
                mcp_response=mcp_result.get("response", ""),
                processing_location=routing_result["processing_location"],
                performance_metrics={
                    "response_time": time.time() - start_time,
                    "success": mcp_result.get("success", False),
                    "cost": mcp_result.get("cost", 0.0),
                    "quality_score": mcp_result.get("quality_score", 0.0)
                },
                routing_decision=routing_result,
                context=context
            )
            
            # 4. 更新路由决策记录
            self.interaction_manager.record_routing_decision(
                user_request=user_request,
                selected_mcp=routing_result["selected_mcp"],
                processing_location=routing_result["processing_location"],
                decision_factors=routing_result["decision_factors"],
                confidence=routing_result["confidence"],
                execution_result=mcp_result
            )
            
            return {
                "success": True,
                "interaction_id": interaction_id,
                "result": mcp_result,
                "routing_info": routing_result,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"请求处理失败: {e}")
            
            # 记录失败的交互
            self.interaction_manager.record_interaction(
                session_id=self.current_session_id,
                interaction_type=InteractionType.SYSTEM_MONITORING,
                mcp_type=MCPType.LOCAL_MODEL,  # 默认
                user_request=user_request,
                mcp_response=f"错误: {str(e)}",
                processing_location=ProcessingLocation.LOCAL_ONLY,
                performance_metrics={
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                },
                context=context
            )
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _make_routing_decision(self, 
                                   user_request: str,
                                   request_type: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """智慧路由决策"""
        
        # 基于历史数据和当前请求特征进行路由决策
        # 这里可以集成之前设计的智慧路由算法
        
        # 简化的决策逻辑（实际应该更复杂）
        if "ocr" in user_request.lower() or "图像" in user_request:
            selected_mcp = MCPType.CLOUD_SEARCH
            processing_location = ProcessingLocation.CLOUD_ONLY
        elif "本地" in user_request or "local" in user_request.lower():
            selected_mcp = MCPType.LOCAL_MODEL
            processing_location = ProcessingLocation.LOCAL_ONLY
        else:
            selected_mcp = MCPType.CLOUD_EDGE_DATA
            processing_location = ProcessingLocation.HYBRID
        
        return {
            "selected_mcp": selected_mcp,
            "processing_location": processing_location,
            "confidence": 0.8,
            "decision_factors": {
                "request_analysis": user_request[:100],
                "historical_performance": "good",
                "current_load": "normal"
            }
        }
    
    async def _execute_mcp_request(self,
                                 mcp_type: MCPType,
                                 user_request: str,
                                 processing_location: ProcessingLocation,
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """执行MCP请求"""
        
        if mcp_type not in self.registered_mcps:
            raise ValueError(f"MCP未注册: {mcp_type.value}")
        
        mcp_instance = self.registered_mcps[mcp_type]
        
        # 构建MCP请求
        mcp_request = {
            "operation": "process",
            "params": {
                "user_request": user_request,
                "processing_location": processing_location.value,
                "context": context
            }
        }
        
        # 执行MCP处理
        if hasattr(mcp_instance, 'process') and callable(mcp_instance.process):
            result = mcp_instance.process(mcp_request)
        else:
            result = {"success": False, "error": "MCP不支持process方法"}
        
        return result
    
    def _classify_interaction_type(self, request_type: str) -> InteractionType:
        """分类交互类型"""
        
        type_mapping = {
            "ocr": InteractionType.OCR_REQUEST,
            "inference": InteractionType.MODEL_INFERENCE,
            "data": InteractionType.DATA_PROCESSING
        }
        
        return type_mapping.get(request_type, InteractionType.OCR_REQUEST)
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        
        return {
            "coordinator_status": "active",
            "registered_mcps": [mcp.value for mcp in self.registered_mcps.keys()],
            "current_session": self.current_session_id,
            "performance_metrics": self.interaction_manager.get_mcp_performance(),
            "routing_analytics": self.interaction_manager.get_routing_analytics()
        }
    
    def export_interaction_data(self) -> str:
        """导出交互数据"""
        
        report = self.interaction_manager.export_analytics_report()
        return f"交互数据已导出，报告包含 {report['summary']['total_interactions']} 条交互记录"

# ============================================================================
# 4. 使用示例
# ============================================================================

async def demo_mcp_coordinator():
    """MCPCoordinator演示"""
    
    print("🎛️ MCPCoordinator 统一交互数据管理演示")
    print("=" * 60)
    
    # 初始化协调器
    coordinator = MCPCoordinator()
    
    # 模拟注册MCP（实际应该是真实的MCP实例）
    class MockMCP:
        def __init__(self, name):
            self.name = name
        
        def process(self, request):
            return {
                "success": True,
                "response": f"{self.name} 处理完成",
                "cost": 0.001,
                "quality_score": 0.9
            }
    
    coordinator.register_mcp(MCPType.LOCAL_MODEL, MockMCP("LocalModelMCP"))
    coordinator.register_mcp(MCPType.CLOUD_SEARCH, MockMCP("CloudSearchMCP"))
    coordinator.register_mcp(MCPType.CLOUD_EDGE_DATA, MockMCP("CloudEdgeDataMCP"))
    
    # 模拟用户请求
    test_requests = [
        "请帮我识别这张图片中的文字",
        "使用本地模型进行推理",
        "分析这些数据的趋势",
        "OCR处理这个文档"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📝 请求 {i}: {request}")
        
        result = await coordinator.process_request(
            user_request=request,
            context={"user_id": "demo_user", "priority": "normal"}
        )
        
        if result["success"]:
            print(f"✅ 处理成功")
            print(f"   交互ID: {result['interaction_id']}")
            print(f"   选择MCP: {result['routing_info']['selected_mcp'].value}")
            print(f"   处理位置: {result['routing_info']['processing_location'].value}")
            print(f"   处理时间: {result['processing_time']:.3f}秒")
        else:
            print(f"❌ 处理失败: {result['error']}")
    
    # 显示系统状态
    print(f"\n📊 系统状态:")
    status = coordinator.get_system_status()
    print(f"   注册MCP: {status['registered_mcps']}")
    print(f"   当前会话: {status['current_session']}")
    
    # 显示性能指标
    print(f"\n📈 性能指标:")
    for mcp_type, metrics in status['performance_metrics'].items():
        print(f"   {mcp_type.value}:")
        print(f"     总请求: {metrics.total_requests}")
        print(f"     成功率: {metrics.successful_requests}/{metrics.total_requests}")
        print(f"     平均响应时间: {metrics.average_response_time:.3f}秒")
    
    # 导出数据
    export_result = coordinator.export_interaction_data()
    print(f"\n💾 {export_result}")

if __name__ == "__main__":
    asyncio.run(demo_mcp_coordinator())

