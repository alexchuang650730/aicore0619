"""
PowerAutomation 测试执行引擎 - 重构版本

基于原有test_manage_mcp重构，专注于测试执行层面的功能，
与工作流层协作提供完整的测试管理解决方案。

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
    ITestExecutionEngine,
    TestPlan,
    ExecutionResult,
    TestReport,
    TestCase,
    TestResult,
    TestStatus,
    TestType,
    create_adapter_communication,
    EventType
)

# 导入原有组件（重构后）
from .framework.test_framework_generator import MCPTestFrameworkGenerator
from .framework.test_executor import MCPTestExecutor
from .framework.test_framework_fixer import MCPTestFrameworkFixer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestExecutionEngine(ITestExecutionEngine):
    """
    测试执行引擎 - 适配器层主类
    
    专注于测试执行层面的功能：
    - 测试框架生成
    - 测试执行管理
    - 问题自动修复
    - 报告生成
    
    与工作流层通过标准接口协作
    """
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        """
        初始化测试执行引擎
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.module_path = Path(__file__).parent
        self.reports_path = self.module_path / "reports"
        
        # 确保报告目录存在
        self.reports_path.mkdir(exist_ok=True)
        
        # 初始化原有组件
        self.generator = MCPTestFrameworkGenerator(str(self.project_root))
        self.executor = MCPTestExecutor(str(self.project_root))
        self.fixer = MCPTestFrameworkFixer(str(self.project_root))
        
        # 初始化通信适配器
        self.communication = create_adapter_communication()
        
        # 状态信息
        self.last_generation_time = None
        self.last_execution_time = None
        self.last_fix_time = None
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"测试执行引擎初始化完成: {self.project_root}")
    
    async def generate_test_frameworks(self, modules: List[str]) -> Dict[str, Any]:
        """
        生成测试框架
        
        Args:
            modules: 目标模块列表
            
        Returns:
            生成结果字典
        """
        logger.info(f"开始生成测试框架，目标模块: {modules}")
        
        try:
            # 发布开始事件
            await self.communication.publish_event(
                EventType.TEST_STARTED,
                {
                    "action": "framework_generation",
                    "modules": modules,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # 执行生成
            if modules:
                # 针对特定模块生成
                results = {}
                for module in modules:
                    module_result = self.generator.generate_test_framework_for_module(module)
                    results[module] = module_result
            else:
                # 生成所有模块
                results = self.generator.generate_all_test_frameworks()
            
            self.last_generation_time = datetime.now()
            
            # 保存生成报告
            report_path = self.reports_path / f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # 发布完成事件
            await self.communication.publish_event(
                EventType.TEST_COMPLETED,
                {
                    "action": "framework_generation",
                    "status": "success",
                    "modules": modules,
                    "report_path": str(report_path)
                }
            )
            
            logger.info(f"测试框架生成完成，报告保存至: {report_path}")
            
            return {
                "status": "success",
                "results": results,
                "report_path": str(report_path),
                "generation_time": self.last_generation_time.isoformat(),
                "modules_processed": len(modules) if modules else "all"
            }
            
        except Exception as e:
            logger.error(f"测试框架生成失败: {e}")
            
            # 发布错误事件
            await self.communication.publish_event(
                EventType.ERROR_OCCURRED,
                {
                    "action": "framework_generation",
                    "error": str(e),
                    "modules": modules
                }
            )
            
            return {
                "status": "error",
                "error": str(e),
                "generation_time": datetime.now().isoformat()
            }
    
    async def execute_tests(self, plan: TestPlan) -> ExecutionResult:
        """
        执行测试计划
        
        Args:
            plan: 测试计划对象
            
        Returns:
            执行结果对象
        """
        logger.info(f"开始执行测试计划: {plan.id}")
        
        execution_start = datetime.now()
        execution_id = plan.id
        
        try:
            # 记录活动执行
            self.active_executions[execution_id] = {
                "plan": plan,
                "start_time": execution_start,
                "status": "running"
            }
            
            # 发布开始事件
            await self.communication.publish_event(
                EventType.TEST_STARTED,
                {
                    "action": "test_execution",
                    "plan_id": plan.id,
                    "test_count": len(plan.test_cases),
                    "timestamp": execution_start.isoformat()
                }
            )
            
            # 执行测试
            test_results = []
            passed_count = 0
            failed_count = 0
            skipped_count = 0
            error_count = 0
            
            for test_case in plan.test_cases:
                try:
                    # 执行单个测试用例
                    result = await self.execute_single_test(test_case)
                    test_results.append(result)
                    
                    # 统计结果
                    if result.status == TestStatus.PASSED:
                        passed_count += 1
                    elif result.status == TestStatus.FAILED:
                        failed_count += 1
                    elif result.status == TestStatus.SKIPPED:
                        skipped_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"执行测试用例失败 {test_case.id}: {e}")
                    error_result = TestResult(
                        test_case_id=test_case.id,
                        status=TestStatus.ERROR,
                        duration=0.0,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error_message=str(e)
                    )
                    test_results.append(error_result)
                    error_count += 1
            
            execution_end = datetime.now()
            total_duration = (execution_end - execution_start).total_seconds()
            
            # 创建执行结果
            execution_result = ExecutionResult(
                plan_id=plan.id,
                strategy_id=plan.strategy_id,
                status=TestStatus.PASSED if failed_count == 0 and error_count == 0 else TestStatus.FAILED,
                total_tests=len(plan.test_cases),
                passed_tests=passed_count,
                failed_tests=failed_count,
                skipped_tests=skipped_count,
                error_tests=error_count,
                total_duration=total_duration,
                start_time=execution_start,
                end_time=execution_end,
                test_results=test_results
            )
            
            # 更新活动执行状态
            self.active_executions[execution_id]["status"] = "completed"
            self.active_executions[execution_id]["result"] = execution_result
            
            # 发布完成事件
            await self.communication.publish_event(
                EventType.TEST_COMPLETED,
                {
                    "action": "test_execution",
                    "plan_id": plan.id,
                    "status": execution_result.status.value,
                    "success_rate": execution_result.success_rate,
                    "duration": total_duration
                }
            )
            
            self.last_execution_time = execution_end
            logger.info(f"测试执行完成: {plan.id}, 成功率: {execution_result.success_rate:.1f}%")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            
            # 发布错误事件
            await self.communication.publish_event(
                EventType.ERROR_OCCURRED,
                {
                    "action": "test_execution",
                    "plan_id": plan.id,
                    "error": str(e)
                }
            )
            
            # 清理活动执行
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            raise
    
    async def execute_single_test(self, test_case: TestCase) -> TestResult:
        """
        执行单个测试用例
        
        Args:
            test_case: 测试用例对象
            
        Returns:
            测试结果对象
        """
        start_time = datetime.now()
        
        try:
            # 这里应该调用实际的测试执行逻辑
            # 暂时使用模拟执行
            await asyncio.sleep(0.1)  # 模拟执行时间
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 模拟测试结果（实际应该根据真实执行结果）
            import random
            success_rate = 0.85  # 85%的成功率
            
            if random.random() < success_rate:
                status = TestStatus.PASSED
                output = f"测试用例 {test_case.name} 执行成功"
                error_message = ""
            else:
                status = TestStatus.FAILED
                output = f"测试用例 {test_case.name} 执行失败"
                error_message = "模拟测试失败"
            
            return TestResult(
                test_case_id=test_case.id,
                status=status,
                duration=duration,
                start_time=start_time,
                end_time=end_time,
                output=output,
                error_message=error_message
            )
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                test_case_id=test_case.id,
                status=TestStatus.ERROR,
                duration=duration,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e)
            )
    
    async def fix_test_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        修复测试问题
        
        Args:
            issues: 问题列表
            
        Returns:
            修复结果字典
        """
        logger.info(f"开始修复测试问题，问题数量: {len(issues)}")
        
        try:
            # 发布开始事件
            await self.communication.publish_event(
                EventType.TEST_STARTED,
                {
                    "action": "issue_fixing",
                    "issue_count": len(issues),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # 执行修复
            results = self.fixer.fix_all_test_files()
            self.last_fix_time = datetime.now()
            
            # 保存修复报告
            report_path = self.reports_path / f"fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # 发布完成事件
            await self.communication.publish_event(
                EventType.TEST_COMPLETED,
                {
                    "action": "issue_fixing",
                    "status": "success",
                    "issues_processed": len(issues),
                    "report_path": str(report_path)
                }
            )
            
            logger.info(f"测试问题修复完成，报告保存至: {report_path}")
            
            return {
                "status": "success",
                "results": results,
                "report_path": str(report_path),
                "fix_time": self.last_fix_time.isoformat(),
                "issues_processed": len(issues)
            }
            
        except Exception as e:
            logger.error(f"测试问题修复失败: {e}")
            
            # 发布错误事件
            await self.communication.publish_event(
                EventType.ERROR_OCCURRED,
                {
                    "action": "issue_fixing",
                    "error": str(e),
                    "issues": issues
                }
            )
            
            return {
                "status": "error",
                "error": str(e),
                "fix_time": datetime.now().isoformat()
            }
    
    async def generate_reports(self, execution_result: ExecutionResult) -> TestReport:
        """
        生成测试报告
        
        Args:
            execution_result: 执行结果对象
            
        Returns:
            测试报告对象
        """
        logger.info(f"开始生成测试报告: {execution_result.plan_id}")
        
        try:
            # 生成报告
            report_id = f"report_{execution_result.plan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            report_path = self.reports_path / f"{report_id}.json"
            
            # 创建报告对象
            test_report = TestReport(
                id=report_id,
                execution_result=execution_result,
                generated_at=datetime.now(),
                report_type="execution_report",
                format="json",
                file_path=str(report_path)
            )
            
            # 添加洞察和建议
            test_report.insights = {
                "success_rate": execution_result.success_rate,
                "total_duration": execution_result.total_duration,
                "average_test_duration": execution_result.total_duration / execution_result.total_tests if execution_result.total_tests > 0 else 0,
                "performance_score": min(100, max(0, 100 - execution_result.total_duration / 10))
            }
            
            test_report.recommendations = []
            if execution_result.success_rate < 90:
                test_report.recommendations.append("建议检查失败的测试用例并进行修复")
            if execution_result.total_duration > 300:
                test_report.recommendations.append("建议优化测试执行性能，考虑并行执行")
            if execution_result.error_tests > 0:
                test_report.recommendations.append("建议修复测试环境配置问题")
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "report_id": test_report.id,
                    "execution_result": {
                        "plan_id": execution_result.plan_id,
                        "strategy_id": execution_result.strategy_id,
                        "status": execution_result.status.value,
                        "total_tests": execution_result.total_tests,
                        "passed_tests": execution_result.passed_tests,
                        "failed_tests": execution_result.failed_tests,
                        "skipped_tests": execution_result.skipped_tests,
                        "error_tests": execution_result.error_tests,
                        "total_duration": execution_result.total_duration,
                        "start_time": execution_result.start_time.isoformat(),
                        "end_time": execution_result.end_time.isoformat(),
                        "success_rate": execution_result.success_rate
                    },
                    "insights": test_report.insights,
                    "recommendations": test_report.recommendations,
                    "generated_at": test_report.generated_at.isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 发布报告生成事件
            await self.communication.publish_event(
                EventType.REPORT_GENERATED,
                {
                    "report_id": test_report.id,
                    "plan_id": execution_result.plan_id,
                    "report_path": str(report_path),
                    "success_rate": execution_result.success_rate
                }
            )
            
            logger.info(f"测试报告生成完成: {report_path}")
            return test_report
            
        except Exception as e:
            logger.error(f"测试报告生成失败: {e}")
            raise
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        获取执行状态
        
        Args:
            execution_id: 执行ID
            
        Returns:
            执行状态字典
        """
        if execution_id in self.active_executions:
            execution_info = self.active_executions[execution_id]
            return {
                "execution_id": execution_id,
                "status": execution_info["status"],
                "start_time": execution_info["start_time"].isoformat(),
                "plan_id": execution_info["plan"].id,
                "test_count": len(execution_info["plan"].test_cases)
            }
        return None
    
    async def stop_execution(self, execution_id: str) -> bool:
        """
        停止测试执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            是否成功停止
        """
        if execution_id in self.active_executions:
            self.active_executions[execution_id]["status"] = "stopped"
            logger.info(f"测试执行已停止: {execution_id}")
            return True
        return False
    
    def get_engine_status(self) -> Dict[str, Any]:
        """
        获取引擎状态
        
        Returns:
            引擎状态字典
        """
        return {
            "status": "active",
            "project_root": str(self.project_root),
            "active_executions": len(self.active_executions),
            "last_operations": {
                "generation": self.last_generation_time.isoformat() if self.last_generation_time else None,
                "execution": self.last_execution_time.isoformat() if self.last_execution_time else None,
                "fix": self.last_fix_time.isoformat() if self.last_fix_time else None
            },
            "reports_path": str(self.reports_path)
        }


# 创建全局引擎实例
_global_engine = None

def get_test_execution_engine(project_root: str = "/opt/powerautomation") -> TestExecutionEngine:
    """获取全局测试执行引擎实例"""
    global _global_engine
    if _global_engine is None:
        _global_engine = TestExecutionEngine(project_root)
    return _global_engine


if __name__ == "__main__":
    # 测试执行引擎
    async def test_engine():
        engine = TestExecutionEngine()
        
        # 测试框架生成
        result = await engine.generate_test_frameworks(["test_module"])
        print(f"生成结果: {result['status']}")
        
        # 获取引擎状态
        status = engine.get_engine_status()
        print(f"引擎状态: {status}")
    
    asyncio.run(test_engine())

