"""
PowerAutomation 测试管理器 - 工作流层重构版本

基于原有test_manager_mcp重构，专注于测试工作流编排和智能策略生成，
与适配器层协作提供完整的测试管理解决方案。

作者: PowerAutomation Team
版本: 2.0.0 (重构版本)
日期: 2025-06-18
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# 导入共享接口
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.interfaces import (
    ITestManagerMCP,
    TestStrategy,
    TestPlan,
    ExecutionResult,
    TestCase,
    TestType,
    ExecutionMode,
    create_workflow_adapter,
    EventType,
    create_test_strategy_from_dict,
    create_test_case_from_dict
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestManagerMCP(ITestManagerMCP):
    """
    测试管理器MCP - 工作流层主类
    
    专注于测试工作流编排和智能策略：
    - 测试策略生成和优化
    - 工作流编排和监控
    - AI驱动的测试优化
    - 与适配器层协作
    
    与适配器层通过标准接口协作
    """
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        """
        初始化测试管理器MCP
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.module_path = Path(__file__).parent
        self.strategies_path = self.module_path / "strategies"
        self.workflows_path = self.module_path / "workflows"
        
        # 确保目录存在
        self.strategies_path.mkdir(exist_ok=True)
        self.workflows_path.mkdir(exist_ok=True)
        
        # 初始化通信适配器
        self.communication = create_workflow_adapter()
        
        # 状态信息
        self.active_strategies: Dict[str, TestStrategy] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.strategy_templates: Dict[str, Dict[str, Any]] = {}
        
        # 加载策略模板
        self._load_strategy_templates()
        
        logger.info(f"测试管理器MCP初始化完成: {self.project_root}")
    
    def _load_strategy_templates(self):
        """加载策略模板"""
        self.strategy_templates = {
            "unit_testing": {
                "name": "单元测试策略",
                "description": "专注于单元测试的策略模板",
                "test_types": [TestType.UNIT],
                "execution_mode": ExecutionMode.PARALLEL,
                "max_workers": 4,
                "timeout": 1800,
                "optimization_enabled": True
            },
            "integration_testing": {
                "name": "集成测试策略",
                "description": "专注于集成测试的策略模板",
                "test_types": [TestType.INTEGRATION],
                "execution_mode": ExecutionMode.SEQUENTIAL,
                "max_workers": 2,
                "timeout": 3600,
                "optimization_enabled": True
            },
            "comprehensive": {
                "name": "综合测试策略",
                "description": "包含所有测试类型的综合策略",
                "test_types": [TestType.UNIT, TestType.INTEGRATION, TestType.E2E],
                "execution_mode": ExecutionMode.ADAPTIVE,
                "max_workers": 6,
                "timeout": 7200,
                "optimization_enabled": True
            },
            "performance": {
                "name": "性能测试策略",
                "description": "专注于性能测试的策略模板",
                "test_types": [TestType.PERFORMANCE],
                "execution_mode": ExecutionMode.SEQUENTIAL,
                "max_workers": 1,
                "timeout": 10800,
                "optimization_enabled": False
            }
        }
    
    async def create_test_strategy(self, requirements: Dict[str, Any]) -> TestStrategy:
        """
        创建测试策略
        
        Args:
            requirements: 策略需求字典
            
        Returns:
            创建的测试策略对象
        """
        logger.info(f"开始创建测试策略: {requirements}")
        
        try:
            # 发布策略创建开始事件
            await self.communication.publish_event(
                EventType.STRATEGY_GENERATED,
                {
                    "action": "strategy_creation_started",
                    "requirements": requirements,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # 分析需求并选择模板
            template_name = requirements.get("template", "comprehensive")
            if template_name not in self.strategy_templates:
                template_name = "comprehensive"
            
            template = self.strategy_templates[template_name]
            
            # 创建策略
            strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            strategy = TestStrategy(
                id=strategy_id,
                name=requirements.get("name", template["name"]),
                description=requirements.get("description", template["description"]),
                target_modules=requirements.get("target_modules", []),
                test_types=requirements.get("test_types", template["test_types"]),
                execution_mode=ExecutionMode(requirements.get("execution_mode", template["execution_mode"].value)),
                max_workers=requirements.get("max_workers", template["max_workers"]),
                timeout=requirements.get("timeout", template["timeout"]),
                retry_count=requirements.get("retry_count", 3),
                optimization_enabled=requirements.get("optimization_enabled", template["optimization_enabled"])
            )
            
            # AI优化建议
            strategy.ai_recommendations = await self._generate_ai_recommendations(strategy, requirements)
            
            # 保存策略
            self.active_strategies[strategy_id] = strategy
            strategy_path = self.strategies_path / f"{strategy_id}.json"
            
            with open(strategy_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "id": strategy.id,
                    "name": strategy.name,
                    "description": strategy.description,
                    "target_modules": strategy.target_modules,
                    "test_types": [t.value for t in strategy.test_types],
                    "execution_mode": strategy.execution_mode.value,
                    "max_workers": strategy.max_workers,
                    "timeout": strategy.timeout,
                    "retry_count": strategy.retry_count,
                    "optimization_enabled": strategy.optimization_enabled,
                    "ai_recommendations": strategy.ai_recommendations,
                    "created_at": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 发布策略创建完成事件
            await self.communication.publish_event(
                EventType.STRATEGY_GENERATED,
                {
                    "action": "strategy_creation_completed",
                    "strategy_id": strategy_id,
                    "template_used": template_name,
                    "strategy_path": str(strategy_path)
                }
            )
            
            logger.info(f"测试策略创建完成: {strategy_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"测试策略创建失败: {e}")
            
            # 发布错误事件
            await self.communication.publish_event(
                EventType.ERROR_OCCURRED,
                {
                    "action": "strategy_creation",
                    "error": str(e),
                    "requirements": requirements
                }
            )
            
            raise
    
    async def _generate_ai_recommendations(self, strategy: TestStrategy, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成AI优化建议
        
        Args:
            strategy: 测试策略对象
            requirements: 原始需求
            
        Returns:
            AI建议字典
        """
        recommendations = {
            "optimization_suggestions": [],
            "performance_tips": [],
            "best_practices": [],
            "risk_assessments": []
        }
        
        # 基于策略类型的建议
        if TestType.UNIT in strategy.test_types:
            recommendations["optimization_suggestions"].append("建议使用并行执行提高单元测试效率")
            recommendations["best_practices"].append("确保单元测试的独立性和可重复性")
        
        if TestType.INTEGRATION in strategy.test_types:
            recommendations["performance_tips"].append("集成测试建议使用顺序执行避免资源冲突")
            recommendations["risk_assessments"].append("注意外部依赖可能导致的测试不稳定")
        
        if strategy.max_workers > 4:
            recommendations["performance_tips"].append("高并发执行时注意系统资源限制")
        
        if strategy.timeout > 3600:
            recommendations["risk_assessments"].append("长时间执行可能增加测试失败风险")
        
        # 基于目标模块的建议
        if len(strategy.target_modules) > 10:
            recommendations["optimization_suggestions"].append("大量模块建议分批执行")
        
        return recommendations
    
    async def execute_test_workflow(self, strategy: TestStrategy) -> ExecutionResult:
        """
        执行测试工作流
        
        Args:
            strategy: 测试策略对象
            
        Returns:
            执行结果对象
        """
        logger.info(f"开始执行测试工作流: {strategy.id}")
        
        workflow_id = f"workflow_{strategy.id}_{datetime.now().strftime('%H%M%S')}"
        workflow_start = datetime.now()
        
        try:
            # 记录活动工作流
            self.active_workflows[workflow_id] = {
                "strategy": strategy,
                "start_time": workflow_start,
                "status": "running",
                "current_step": "initialization"
            }
            
            # 发布工作流开始事件
            await self.communication.publish_event(
                EventType.WORKFLOW_STARTED,
                {
                    "workflow_id": workflow_id,
                    "strategy_id": strategy.id,
                    "timestamp": workflow_start.isoformat()
                }
            )
            
            # 步骤1: 生成测试框架（如果需要）
            if strategy.target_modules:
                self.active_workflows[workflow_id]["current_step"] = "framework_generation"
                
                framework_result = await self.communication.request_framework_generation(
                    strategy.target_modules
                )
                
                if not framework_result or framework_result.get("status") != "success":
                    raise Exception("测试框架生成失败")
            
            # 步骤2: 创建测试计划
            self.active_workflows[workflow_id]["current_step"] = "plan_creation"
            test_plan = await self._create_test_plan(strategy)
            
            # 步骤3: 执行测试
            self.active_workflows[workflow_id]["current_step"] = "test_execution"
            
            execution_result = await self.communication.request_test_execution({
                "plan_id": test_plan.id,
                "strategy_id": strategy.id,
                "test_cases": [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "description": tc.description,
                        "test_type": tc.test_type.value,
                        "module_name": tc.module_name,
                        "file_path": tc.file_path,
                        "function_name": tc.function_name
                    }
                    for tc in test_plan.test_cases
                ],
                "execution_order": test_plan.execution_order,
                "configuration": {
                    "max_workers": strategy.max_workers,
                    "timeout": strategy.timeout,
                    "retry_count": strategy.retry_count
                }
            })
            
            if not execution_result:
                raise Exception("测试执行请求失败")
            
            # 步骤4: 处理执行结果
            self.active_workflows[workflow_id]["current_step"] = "result_processing"
            
            # 创建执行结果对象（简化版本，实际应该从适配器层获取完整结果）
            workflow_end = datetime.now()
            total_duration = (workflow_end - workflow_start).total_seconds()
            
            final_result = ExecutionResult(
                plan_id=test_plan.id,
                strategy_id=strategy.id,
                status=execution_result.get("status", "unknown"),
                total_tests=len(test_plan.test_cases),
                passed_tests=execution_result.get("passed_tests", 0),
                failed_tests=execution_result.get("failed_tests", 0),
                skipped_tests=execution_result.get("skipped_tests", 0),
                error_tests=execution_result.get("error_tests", 0),
                total_duration=total_duration,
                start_time=workflow_start,
                end_time=workflow_end,
                test_results=[]  # 实际应该包含详细的测试结果
            )
            
            # 更新工作流状态
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["result"] = final_result
            self.active_workflows[workflow_id]["current_step"] = "completed"
            
            # 保存工作流记录
            workflow_path = self.workflows_path / f"{workflow_id}.json"
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "workflow_id": workflow_id,
                    "strategy_id": strategy.id,
                    "start_time": workflow_start.isoformat(),
                    "end_time": workflow_end.isoformat(),
                    "total_duration": total_duration,
                    "status": "completed",
                    "result_summary": {
                        "total_tests": final_result.total_tests,
                        "passed_tests": final_result.passed_tests,
                        "failed_tests": final_result.failed_tests,
                        "success_rate": final_result.success_rate
                    }
                }, f, ensure_ascii=False, indent=2)
            
            # 发布工作流完成事件
            await self.communication.publish_event(
                EventType.WORKFLOW_COMPLETED,
                {
                    "workflow_id": workflow_id,
                    "strategy_id": strategy.id,
                    "status": "completed",
                    "success_rate": final_result.success_rate,
                    "duration": total_duration
                }
            )
            
            logger.info(f"测试工作流执行完成: {workflow_id}, 成功率: {final_result.success_rate:.1f}%")
            return final_result
            
        except Exception as e:
            logger.error(f"测试工作流执行失败: {e}")
            
            # 更新工作流状态
            if workflow_id in self.active_workflows:
                self.active_workflows[workflow_id]["status"] = "failed"
                self.active_workflows[workflow_id]["error"] = str(e)
            
            # 发布错误事件
            await self.communication.publish_event(
                EventType.ERROR_OCCURRED,
                {
                    "workflow_id": workflow_id,
                    "strategy_id": strategy.id,
                    "error": str(e),
                    "current_step": self.active_workflows.get(workflow_id, {}).get("current_step", "unknown")
                }
            )
            
            raise
    
    async def _create_test_plan(self, strategy: TestStrategy) -> TestPlan:
        """
        根据策略创建测试计划
        
        Args:
            strategy: 测试策略对象
            
        Returns:
            测试计划对象
        """
        plan_id = f"plan_{strategy.id}_{datetime.now().strftime('%H%M%S')}"
        
        # 生成测试用例（简化版本）
        test_cases = []
        execution_order = []
        
        for i, module in enumerate(strategy.target_modules):
            for test_type in strategy.test_types:
                test_case = TestCase(
                    id=f"test_{module}_{test_type.value}_{i}",
                    name=f"{module} {test_type.value} 测试",
                    description=f"针对模块 {module} 的 {test_type.value} 测试",
                    test_type=test_type,
                    module_name=module,
                    file_path=f"/tests/{module}/test_{test_type.value}.py",
                    function_name=f"test_{module}_{test_type.value}"
                )
                test_cases.append(test_case)
                execution_order.append(test_case.id)
        
        # 如果没有指定模块，创建默认测试用例
        if not strategy.target_modules:
            for test_type in strategy.test_types:
                test_case = TestCase(
                    id=f"test_default_{test_type.value}",
                    name=f"默认 {test_type.value} 测试",
                    description=f"默认的 {test_type.value} 测试用例",
                    test_type=test_type,
                    module_name="default",
                    file_path=f"/tests/test_{test_type.value}.py",
                    function_name=f"test_default_{test_type.value}"
                )
                test_cases.append(test_case)
                execution_order.append(test_case.id)
        
        # 根据执行模式调整执行顺序
        if strategy.execution_mode == ExecutionMode.SEQUENTIAL:
            # 顺序执行，保持原有顺序
            pass
        elif strategy.execution_mode == ExecutionMode.PARALLEL:
            # 并行执行，可以打乱顺序
            import random
            random.shuffle(execution_order)
        elif strategy.execution_mode == ExecutionMode.ADAPTIVE:
            # 自适应执行，按优先级排序
            test_cases.sort(key=lambda tc: tc.priority, reverse=True)
            execution_order = [tc.id for tc in test_cases]
        
        # 估算执行时间
        estimated_duration = len(test_cases) * 30  # 每个测试用例平均30秒
        if strategy.execution_mode == ExecutionMode.PARALLEL:
            estimated_duration = estimated_duration // min(strategy.max_workers, len(test_cases))
        
        test_plan = TestPlan(
            id=plan_id,
            strategy_id=strategy.id,
            test_cases=test_cases,
            execution_order=execution_order,
            estimated_duration=estimated_duration,
            created_at=datetime.now(),
            created_by="test_manager_mcp"
        )
        
        return test_plan
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        获取工作流状态
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流状态字典
        """
        if workflow_id in self.active_workflows:
            workflow_info = self.active_workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": workflow_info["status"],
                "current_step": workflow_info["current_step"],
                "start_time": workflow_info["start_time"].isoformat(),
                "strategy_id": workflow_info["strategy"].id,
                "duration": (datetime.now() - workflow_info["start_time"]).total_seconds()
            }
        
        # 尝试从文件加载历史工作流
        workflow_path = self.workflows_path / f"{workflow_id}.json"
        if workflow_path.exists():
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {"error": "工作流未找到"}
    
    async def optimize_test_execution(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        优化测试执行
        
        Args:
            context: 优化上下文
            
        Returns:
            优化建议字典
        """
        logger.info(f"开始优化测试执行: {context}")
        
        optimization_results = {
            "recommendations": [],
            "performance_improvements": [],
            "resource_optimizations": [],
            "risk_mitigations": []
        }
        
        # 分析历史执行数据
        execution_history = context.get("execution_history", [])
        if execution_history:
            avg_duration = sum(h.get("duration", 0) for h in execution_history) / len(execution_history)
            avg_success_rate = sum(h.get("success_rate", 0) for h in execution_history) / len(execution_history)
            
            if avg_duration > 300:
                optimization_results["performance_improvements"].append("建议增加并行执行工作线程")
            
            if avg_success_rate < 90:
                optimization_results["risk_mitigations"].append("建议增加测试重试次数")
        
        # 分析当前系统资源
        current_load = context.get("system_load", {})
        if current_load.get("cpu_usage", 0) > 80:
            optimization_results["resource_optimizations"].append("建议降低并行执行数量")
        
        if current_load.get("memory_usage", 0) > 80:
            optimization_results["resource_optimizations"].append("建议优化测试内存使用")
        
        # 基于测试类型的优化建议
        test_types = context.get("test_types", [])
        if "performance" in test_types:
            optimization_results["recommendations"].append("性能测试建议使用独立环境")
        
        if "integration" in test_types:
            optimization_results["recommendations"].append("集成测试建议使用数据库事务回滚")
        
        return optimization_results
    
    def get_manager_status(self) -> Dict[str, Any]:
        """
        获取管理器状态
        
        Returns:
            管理器状态字典
        """
        return {
            "status": "active",
            "project_root": str(self.project_root),
            "active_strategies": len(self.active_strategies),
            "active_workflows": len(self.active_workflows),
            "strategy_templates": list(self.strategy_templates.keys()),
            "paths": {
                "strategies": str(self.strategies_path),
                "workflows": str(self.workflows_path)
            }
        }


# 创建全局管理器实例
_global_manager = None

def get_test_manager_mcp(project_root: str = "/opt/powerautomation") -> TestManagerMCP:
    """获取全局测试管理器MCP实例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = TestManagerMCP(project_root)
    return _global_manager


if __name__ == "__main__":
    # 测试管理器MCP
    async def test_manager():
        manager = TestManagerMCP()
        
        # 创建测试策略
        strategy = await manager.create_test_strategy({
            "name": "示例测试策略",
            "template": "unit_testing",
            "target_modules": ["module1", "module2"]
        })
        print(f"策略创建完成: {strategy.id}")
        
        # 获取管理器状态
        status = manager.get_manager_status()
        print(f"管理器状态: {status}")
    
    asyncio.run(test_manager())

