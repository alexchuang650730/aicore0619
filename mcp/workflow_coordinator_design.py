#!/usr/bin/env python3
"""
WorkflowCoordinator + MCPCoordinator 层级架构设计

解决大workflow MCP vs 小MCP的选择问题，建立清晰的层级决策架构。

架构层级：
1. WorkflowCoordinator (最高层) - 决定是否需要大workflow MCP
2. MCPCoordinator (中间层) - 选择具体的小MCP，管理交互数据  
3. Individual MCPs (执行层) - 执行具体业务逻辑

设计原则：
- 复杂任务 → WorkflowCoordinator → Workflow MCP
- 简单任务 → WorkflowCoordinator → MCPCoordinator → Individual MCP
- 所有交互数据统一由MCPCoordinator管理
"""

import asyncio
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# ============================================================================
# 1. 核心枚举和数据结构
# ============================================================================

class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"           # 单一MCP可处理
    MODERATE = "moderate"       # 需要2-3个MCP协作
    COMPLEX = "complex"         # 需要workflow MCP
    ENTERPRISE = "enterprise"   # 需要企业级workflow

class WorkflowType(Enum):
    """Workflow类型"""
    OCR_PIPELINE = "ocr_pipeline"                    # OCR处理流水线
    DATA_ANALYSIS_WORKFLOW = "data_analysis_workflow" # 数据分析工作流
    DOCUMENT_PROCESSING = "document_processing"       # 文档处理工作流
    MULTI_MODAL_ANALYSIS = "multi_modal_analysis"    # 多模态分析工作流
    AUTOMATION_WORKFLOW = "automation_workflow"      # 自动化工作流

class MCPCategory(Enum):
    """MCP类别"""
    WORKFLOW_MCP = "workflow_mcp"     # 大workflow MCP
    FUNCTIONAL_MCP = "functional_mcp" # 功能性小MCP

class IndividualMCPType(Enum):
    """个体MCP类型"""
    LOCAL_MODEL = "local_model_mcp"
    CLOUD_SEARCH = "cloud_search_mcp"
    CLOUD_EDGE_DATA = "cloud_edge_data_mcp"

@dataclass
class TaskAnalysisResult:
    """任务分析结果"""
    complexity: TaskComplexity
    requires_workflow: bool
    recommended_workflow_type: Optional[WorkflowType]
    recommended_mcp_type: Optional[IndividualMCPType]
    confidence: float
    reasoning: str
    estimated_steps: int
    cross_domain: bool

@dataclass
class RoutingDecision:
    """路由决策"""
    decision_type: str  # "workflow" or "individual_mcp"
    target: Union[WorkflowType, IndividualMCPType]
    confidence: float
    reasoning: str
    fallback_options: List[Union[WorkflowType, IndividualMCPType]]

# ============================================================================
# 2. 任务复杂度分析器
# ============================================================================

class TaskComplexityAnalyzer:
    """
    任务复杂度分析器
    
    分析用户请求的复杂度，判断是否需要workflow MCP
    """
    
    def __init__(self):
        self.workflow_keywords = {
            WorkflowType.OCR_PIPELINE: [
                "批量OCR", "文档处理流程", "图像识别流水线", "多文档分析",
                "OCR后处理", "文档结构化", "表格提取分析"
            ],
            WorkflowType.DATA_ANALYSIS_WORKFLOW: [
                "数据分析流程", "统计分析", "数据挖掘", "报告生成",
                "数据可视化", "趋势分析", "预测建模"
            ],
            WorkflowType.DOCUMENT_PROCESSING: [
                "文档转换", "格式转换", "文档合并", "文档拆分",
                "文档标准化", "文档归档", "文档审核"
            ],
            WorkflowType.MULTI_MODAL_ANALYSIS: [
                "多模态分析", "图文结合", "音视频分析", "综合分析",
                "跨媒体", "多源数据", "融合分析"
            ],
            WorkflowType.AUTOMATION_WORKFLOW: [
                "自动化流程", "批量处理", "定时任务", "工作流",
                "流程自动化", "批量操作", "自动化脚本"
            ]
        }
        
        self.complexity_indicators = {
            TaskComplexity.SIMPLE: [
                "单个", "一张", "简单", "快速", "直接"
            ],
            TaskComplexity.MODERATE: [
                "几个", "多个", "对比", "分析", "处理"
            ],
            TaskComplexity.COMPLEX: [
                "批量", "流程", "工作流", "自动化", "系统",
                "完整", "端到端", "全流程"
            ],
            TaskComplexity.ENTERPRISE: [
                "企业级", "大规模", "生产环境", "集成", "部署",
                "监控", "管理", "运维"
            ]
        }
        
        self.cross_domain_keywords = [
            "结合", "整合", "融合", "综合", "跨", "多种", "不同"
        ]
    
    def analyze_task(self, user_request: str, context: Dict[str, Any] = None) -> TaskAnalysisResult:
        """
        分析任务复杂度
        
        Args:
            user_request: 用户请求
            context: 上下文信息
            
        Returns:
            任务分析结果
        """
        
        request_lower = user_request.lower()
        
        # 1. 检测是否需要workflow
        workflow_type, workflow_confidence = self._detect_workflow_type(request_lower)
        
        # 2. 分析复杂度
        complexity = self._analyze_complexity(request_lower)
        
        # 3. 检测跨域需求
        cross_domain = self._detect_cross_domain(request_lower)
        
        # 4. 估算步骤数
        estimated_steps = self._estimate_steps(request_lower, complexity)
        
        # 5. 决定是否需要workflow
        requires_workflow = self._requires_workflow_decision(
            complexity, workflow_confidence, cross_domain, estimated_steps
        )
        
        # 6. 推荐个体MCP（如果不需要workflow）
        recommended_mcp = None if requires_workflow else self._recommend_individual_mcp(request_lower)
        
        # 7. 生成推理说明
        reasoning = self._generate_reasoning(
            complexity, workflow_type, cross_domain, estimated_steps, requires_workflow
        )
        
        # 8. 计算总体置信度
        overall_confidence = self._calculate_overall_confidence(
            workflow_confidence, complexity, cross_domain
        )
        
        return TaskAnalysisResult(
            complexity=complexity,
            requires_workflow=requires_workflow,
            recommended_workflow_type=workflow_type if requires_workflow else None,
            recommended_mcp_type=recommended_mcp,
            confidence=overall_confidence,
            reasoning=reasoning,
            estimated_steps=estimated_steps,
            cross_domain=cross_domain
        )
    
    def _detect_workflow_type(self, request_lower: str) -> Tuple[Optional[WorkflowType], float]:
        """检测workflow类型"""
        
        best_match = None
        best_score = 0.0
        
        for workflow_type, keywords in self.workflow_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword.lower() in request_lower:
                    score += 1.0
            
            # 归一化分数
            normalized_score = score / len(keywords)
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_match = workflow_type
        
        return best_match, best_score
    
    def _analyze_complexity(self, request_lower: str) -> TaskComplexity:
        """分析复杂度"""
        
        complexity_scores = {}
        
        for complexity, indicators in self.complexity_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in request_lower:
                    score += 1
            complexity_scores[complexity] = score
        
        # 找到得分最高的复杂度
        if complexity_scores[TaskComplexity.ENTERPRISE] > 0:
            return TaskComplexity.ENTERPRISE
        elif complexity_scores[TaskComplexity.COMPLEX] > 0:
            return TaskComplexity.COMPLEX
        elif complexity_scores[TaskComplexity.MODERATE] > 0:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    def _detect_cross_domain(self, request_lower: str) -> bool:
        """检测跨域需求"""
        
        for keyword in self.cross_domain_keywords:
            if keyword in request_lower:
                return True
        
        # 检测多个领域关键词
        domain_keywords = ["ocr", "图像", "文本", "数据", "分析", "处理"]
        domain_count = sum(1 for keyword in domain_keywords if keyword in request_lower)
        
        return domain_count >= 2
    
    def _estimate_steps(self, request_lower: str, complexity: TaskComplexity) -> int:
        """估算处理步骤数"""
        
        base_steps = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MODERATE: 3,
            TaskComplexity.COMPLEX: 5,
            TaskComplexity.ENTERPRISE: 8
        }
        
        steps = base_steps[complexity]
        
        # 根据关键词调整
        step_keywords = ["然后", "接着", "之后", "再", "最后", "步骤"]
        for keyword in step_keywords:
            if keyword in request_lower:
                steps += 1
        
        return min(steps, 10)  # 最多10步
    
    def _requires_workflow_decision(self, 
                                  complexity: TaskComplexity,
                                  workflow_confidence: float,
                                  cross_domain: bool,
                                  estimated_steps: int) -> bool:
        """决定是否需要workflow"""
        
        # 企业级任务必须使用workflow
        if complexity == TaskComplexity.ENTERPRISE:
            return True
        
        # 复杂任务且有workflow匹配
        if complexity == TaskComplexity.COMPLEX and workflow_confidence > 0.3:
            return True
        
        # 跨域且步骤多
        if cross_domain and estimated_steps >= 3:
            return True
        
        # 步骤很多
        if estimated_steps >= 5:
            return True
        
        return False
    
    def _recommend_individual_mcp(self, request_lower: str) -> IndividualMCPType:
        """推荐个体MCP"""
        
        # OCR相关
        if any(keyword in request_lower for keyword in ["ocr", "图像", "识别", "文字"]):
            return IndividualMCPType.CLOUD_SEARCH
        
        # 本地模型相关
        if any(keyword in request_lower for keyword in ["本地", "local", "离线"]):
            return IndividualMCPType.LOCAL_MODEL
        
        # 默认云边协同
        return IndividualMCPType.CLOUD_EDGE_DATA
    
    def _generate_reasoning(self, 
                          complexity: TaskComplexity,
                          workflow_type: Optional[WorkflowType],
                          cross_domain: bool,
                          estimated_steps: int,
                          requires_workflow: bool) -> str:
        """生成推理说明"""
        
        reasons = []
        
        reasons.append(f"任务复杂度: {complexity.value}")
        
        if workflow_type:
            reasons.append(f"检测到workflow类型: {workflow_type.value}")
        
        if cross_domain:
            reasons.append("检测到跨域需求")
        
        reasons.append(f"预估处理步骤: {estimated_steps}")
        
        if requires_workflow:
            reasons.append("建议使用workflow MCP处理")
        else:
            reasons.append("可使用单一MCP处理")
        
        return "; ".join(reasons)
    
    def _calculate_overall_confidence(self, 
                                    workflow_confidence: float,
                                    complexity: TaskComplexity,
                                    cross_domain: bool) -> float:
        """计算总体置信度"""
        
        base_confidence = 0.7
        
        # workflow匹配度加成
        base_confidence += workflow_confidence * 0.2
        
        # 复杂度加成
        complexity_bonus = {
            TaskComplexity.SIMPLE: 0.1,
            TaskComplexity.MODERATE: 0.05,
            TaskComplexity.COMPLEX: 0.0,
            TaskComplexity.ENTERPRISE: -0.05
        }
        base_confidence += complexity_bonus[complexity]
        
        # 跨域检测加成
        if cross_domain:
            base_confidence += 0.1
        
        return min(max(base_confidence, 0.0), 1.0)

# ============================================================================
# 3. WorkflowCoordinator (最高层)
# ============================================================================

class WorkflowCoordinator:
    """
    工作流协调器 (最高层)
    
    负责决定是否需要大workflow MCP，如果不需要则委托给MCPCoordinator
    """
    
    def __init__(self, mcp_coordinator):
        self.mcp_coordinator = mcp_coordinator
        self.task_analyzer = TaskComplexityAnalyzer()
        self.registered_workflows: Dict[WorkflowType, Any] = {}
        self.logger = logging.getLogger("WorkflowCoordinator")
        
        self.logger.info("WorkflowCoordinator初始化完成")
    
    def register_workflow_mcp(self, workflow_type: WorkflowType, workflow_instance: Any):
        """注册workflow MCP"""
        
        self.registered_workflows[workflow_type] = workflow_instance
        self.logger.info(f"注册Workflow MCP: {workflow_type.value}")
    
    async def process_request(self, 
                            user_request: str,
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户请求 (最高层入口)
        
        Args:
            user_request: 用户请求
            context: 上下文信息
            
        Returns:
            处理结果
        """
        
        start_time = time.time()
        
        try:
            # 1. 分析任务复杂度
            analysis_result = self.task_analyzer.analyze_task(user_request, context)
            
            self.logger.info(f"任务分析: {analysis_result.reasoning}")
            
            # 2. 路由决策
            if analysis_result.requires_workflow:
                # 使用workflow MCP处理
                result = await self._process_with_workflow(
                    user_request, analysis_result, context
                )
                result["routing_level"] = "workflow"
                result["selected_workflow"] = analysis_result.recommended_workflow_type.value
            else:
                # 委托给MCPCoordinator处理
                result = await self.mcp_coordinator.process_request(
                    user_request, "auto", context
                )
                result["routing_level"] = "individual_mcp"
                result["recommended_mcp"] = analysis_result.recommended_mcp_type.value if analysis_result.recommended_mcp_type else "auto"
            
            # 3. 添加分析信息
            result["task_analysis"] = {
                "complexity": analysis_result.complexity.value,
                "requires_workflow": analysis_result.requires_workflow,
                "confidence": analysis_result.confidence,
                "reasoning": analysis_result.reasoning,
                "estimated_steps": analysis_result.estimated_steps,
                "cross_domain": analysis_result.cross_domain
            }
            
            result["total_processing_time"] = time.time() - start_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"WorkflowCoordinator处理失败: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "routing_level": "error",
                "total_processing_time": time.time() - start_time
            }
    
    async def _process_with_workflow(self, 
                                   user_request: str,
                                   analysis_result: TaskAnalysisResult,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """使用workflow MCP处理"""
        
        workflow_type = analysis_result.recommended_workflow_type
        
        if workflow_type not in self.registered_workflows:
            # 如果没有注册对应的workflow，降级到MCPCoordinator
            self.logger.warning(f"Workflow MCP未注册: {workflow_type.value}，降级到MCPCoordinator")
            
            result = await self.mcp_coordinator.process_request(
                user_request, "auto", context
            )
            result["fallback_reason"] = f"Workflow MCP未注册: {workflow_type.value}"
            return result
        
        # 执行workflow MCP
        workflow_instance = self.registered_workflows[workflow_type]
        
        workflow_request = {
            "operation": "execute_workflow",
            "params": {
                "user_request": user_request,
                "analysis_result": analysis_result,
                "context": context
            }
        }
        
        if hasattr(workflow_instance, 'execute_workflow') and callable(workflow_instance.execute_workflow):
            result = workflow_instance.execute_workflow(workflow_request)
        else:
            result = {"success": False, "error": "Workflow MCP不支持execute_workflow方法"}
        
        return result
    
    def get_system_overview(self) -> Dict[str, Any]:
        """获取系统总览"""
        
        mcp_status = self.mcp_coordinator.get_system_status()
        
        return {
            "workflow_coordinator": {
                "status": "active",
                "registered_workflows": [wf.value for wf in self.registered_workflows.keys()]
            },
            "mcp_coordinator": mcp_status,
            "architecture": {
                "levels": ["WorkflowCoordinator", "MCPCoordinator", "Individual MCPs"],
                "decision_flow": "WorkflowCoordinator → 分析任务 → 选择层级 → 执行处理"
            }
        }

# ============================================================================
# 4. 使用示例和演示
# ============================================================================

async def demo_hierarchical_architecture():
    """层级架构演示"""
    
    print("🏗️ WorkflowCoordinator + MCPCoordinator 层级架构演示")
    print("=" * 70)
    
    # 导入之前的MCPCoordinator
    from mcp_coordinator_redesign import MCPCoordinator, MCPType
    
    # 初始化MCPCoordinator
    mcp_coordinator = MCPCoordinator()
    
    # 模拟注册个体MCP
    class MockIndividualMCP:
        def __init__(self, name):
            self.name = name
        
        def process(self, request):
            return {
                "success": True,
                "response": f"{self.name} 处理完成",
                "cost": 0.001,
                "quality_score": 0.9
            }
    
    mcp_coordinator.register_mcp(MCPType.LOCAL_MODEL, MockIndividualMCP("LocalModelMCP"))
    mcp_coordinator.register_mcp(MCPType.CLOUD_SEARCH, MockIndividualMCP("CloudSearchMCP"))
    mcp_coordinator.register_mcp(MCPType.CLOUD_EDGE_DATA, MockIndividualMCP("CloudEdgeDataMCP"))
    
    # 初始化WorkflowCoordinator
    workflow_coordinator = WorkflowCoordinator(mcp_coordinator)
    
    # 模拟注册workflow MCP
    class MockWorkflowMCP:
        def __init__(self, name):
            self.name = name
        
        def execute_workflow(self, request):
            return {
                "success": True,
                "response": f"{self.name} workflow执行完成",
                "steps_executed": 5,
                "cost": 0.01,
                "quality_score": 0.95
            }
    
    workflow_coordinator.register_workflow_mcp(
        WorkflowType.OCR_PIPELINE, 
        MockWorkflowMCP("OCR Pipeline Workflow")
    )
    workflow_coordinator.register_workflow_mcp(
        WorkflowType.DATA_ANALYSIS_WORKFLOW,
        MockWorkflowMCP("Data Analysis Workflow")
    )
    
    # 测试不同复杂度的请求
    test_requests = [
        {
            "request": "识别这张图片中的文字",
            "expected": "简单任务 → Individual MCP"
        },
        {
            "request": "批量OCR处理100个文档，然后进行数据分析和报告生成",
            "expected": "复杂任务 → Workflow MCP"
        },
        {
            "request": "使用本地模型进行推理",
            "expected": "简单任务 → Individual MCP"
        },
        {
            "request": "建立完整的文档处理流程，包括OCR、结构化、分析和归档",
            "expected": "复杂任务 → Workflow MCP"
        },
        {
            "request": "对比分析三个数据源的趋势",
            "expected": "中等任务 → Individual MCP"
        }
    ]
    
    for i, test_case in enumerate(test_requests, 1):
        print(f"\n📝 测试 {i}: {test_case['request']}")
        print(f"🎯 预期: {test_case['expected']}")
        print("-" * 50)
        
        result = await workflow_coordinator.process_request(
            user_request=test_case["request"],
            context={"user_id": "demo_user", "priority": "normal"}
        )
        
        if result["success"]:
            print(f"✅ 处理成功")
            print(f"   路由层级: {result['routing_level']}")
            
            if result["routing_level"] == "workflow":
                print(f"   选择Workflow: {result['selected_workflow']}")
            else:
                print(f"   推荐MCP: {result.get('recommended_mcp', 'auto')}")
                if 'routing_info' in result:
                    print(f"   实际选择: {result['routing_info']['selected_mcp'].value}")
            
            print(f"   任务复杂度: {result['task_analysis']['complexity']}")
            print(f"   需要Workflow: {result['task_analysis']['requires_workflow']}")
            print(f"   分析置信度: {result['task_analysis']['confidence']:.2%}")
            print(f"   预估步骤: {result['task_analysis']['estimated_steps']}")
            print(f"   跨域需求: {result['task_analysis']['cross_domain']}")
            print(f"   处理时间: {result['total_processing_time']:.3f}秒")
            print(f"   分析理由: {result['task_analysis']['reasoning']}")
            
        else:
            print(f"❌ 处理失败: {result['error']}")
    
    # 显示系统总览
    print(f"\n📊 系统总览:")
    overview = workflow_coordinator.get_system_overview()
    
    print(f"   WorkflowCoordinator:")
    print(f"     状态: {overview['workflow_coordinator']['status']}")
    print(f"     注册Workflows: {overview['workflow_coordinator']['registered_workflows']}")
    
    print(f"   MCPCoordinator:")
    print(f"     注册MCPs: {overview['mcp_coordinator']['registered_mcps']}")
    
    print(f"   架构层级: {' → '.join(overview['architecture']['levels'])}")
    print(f"   决策流程: {overview['architecture']['decision_flow']}")

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    
    asyncio.run(demo_hierarchical_architecture())

