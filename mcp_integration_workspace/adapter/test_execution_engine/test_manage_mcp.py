#!/usr/bin/env python3
"""
Test Management MCP 主模块
PowerAutomation测试框架管理器，提供统一的测试生成、执行和管理功能

基于PowerAutomation MCP标准，集成测试框架生成、执行、修复和报告功能。
支持自动发现MCP模块、生成标准化测试、并行执行测试、生成详细报告。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-17
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from .framework.test_framework_generator import MCPTestFrameworkGenerator
from .framework.test_executor import MCPTestExecutor
from .framework.test_framework_fixer import MCPTestFrameworkFixer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestManageMCP:
    """
    Test Management MCP 主类
    提供PowerAutomation测试框架的统一管理接口
    """
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        """
        初始化Test Management MCP
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.module_path = Path(__file__).parent
        self.reports_path = self.module_path / "reports"
        
        # 确保报告目录存在
        self.reports_path.mkdir(exist_ok=True)
        
        # 初始化组件
        self.generator = MCPTestFrameworkGenerator(str(self.project_root))
        self.executor = MCPTestExecutor(str(self.project_root))
        self.fixer = MCPTestFrameworkFixer(str(self.project_root))
        
        # 状态信息
        self.last_generation_time = None
        self.last_execution_time = None
        self.last_fix_time = None
        
        logger.info(f"Test Management MCP initialized with project root: {self.project_root}")
    
    async def generate_test_frameworks(self) -> Dict[str, Any]:
        """
        生成所有MCP模块的测试框架
        
        Returns:
            生成结果字典
        """
        logger.info("开始生成测试框架...")
        
        try:
            results = self.generator.generate_all_test_frameworks()
            self.last_generation_time = datetime.now()
            
            # 保存生成报告
            report_path = self.reports_path / f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试框架生成完成，报告保存至: {report_path}")
            return {
                "status": "success",
                "results": results,
                "report_path": str(report_path),
                "generation_time": self.last_generation_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"测试框架生成失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "generation_time": datetime.now().isoformat()
            }
    
    async def execute_all_tests(self, parallel: bool = True, max_workers: int = 4) -> Dict[str, Any]:
        """
        执行所有测试
        
        Args:
            parallel: 是否并行执行
            max_workers: 最大并发数
            
        Returns:
            执行结果字典
        """
        logger.info(f"开始执行测试 (并行: {parallel}, 最大并发: {max_workers})...")
        
        try:
            success = self.executor.run_all_tests(parallel=parallel, max_workers=max_workers)
            self.last_execution_time = datetime.now()
            
            # 获取最新的测试报告
            report_files = list(self.project_root.glob("test/mcp_comprehensive_test_report_*.json"))
            if report_files:
                latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
                # 复制到我们的报告目录
                target_path = self.reports_path / f"execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                target_path.write_text(latest_report.read_text())
                
                logger.info(f"测试执行完成，报告保存至: {target_path}")
                return {
                    "status": "success" if success else "partial_failure",
                    "all_tests_passed": success,
                    "report_path": str(target_path),
                    "execution_time": self.last_execution_time.isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": "未找到测试报告",
                    "execution_time": self.last_execution_time.isoformat()
                }
                
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            }
    
    async def fix_test_frameworks(self) -> Dict[str, Any]:
        """
        修复测试框架中的问题
        
        Returns:
            修复结果字典
        """
        logger.info("开始修复测试框架...")
        
        try:
            results = self.fixer.fix_all_test_files()
            self.last_fix_time = datetime.now()
            
            # 保存修复报告
            report_path = self.reports_path / f"fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"测试框架修复完成，报告保存至: {report_path}")
            return {
                "status": "success",
                "results": results,
                "report_path": str(report_path),
                "fix_time": self.last_fix_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"测试框架修复失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fix_time": datetime.now().isoformat()
            }
    
    async def get_test_status(self) -> Dict[str, Any]:
        """
        获取测试状态概览
        
        Returns:
            测试状态字典
        """
        try:
            # 发现所有测试模块
            test_modules = self.executor.discover_all_tests()
            
            # 统计信息
            total_modules = len(set(module['module_name'] for module in test_modules))
            total_tests = len(test_modules)
            
            # 按类型统计
            unit_tests = len([m for m in test_modules if m['test_type'] == 'unit'])
            integration_tests = len([m for m in test_modules if m['test_type'] == 'integration'])
            
            # 按模块类型统计
            adapter_modules = len(set(m['module_name'] for m in test_modules if m['module_type'] == 'adapter'))
            workflow_modules = len(set(m['module_name'] for m in test_modules if m['module_type'] == 'workflow'))
            
            # 获取最新报告
            latest_reports = {
                "generation": None,
                "execution": None,
                "fix": None
            }
            
            for report_type in latest_reports.keys():
                report_files = list(self.reports_path.glob(f"{report_type}_report_*.json"))
                if report_files:
                    latest_file = max(report_files, key=lambda x: x.stat().st_mtime)
                    latest_reports[report_type] = {
                        "file": str(latest_file),
                        "time": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
                    }
            
            return {
                "status": "success",
                "overview": {
                    "total_modules": total_modules,
                    "total_tests": total_tests,
                    "unit_tests": unit_tests,
                    "integration_tests": integration_tests,
                    "adapter_modules": adapter_modules,
                    "workflow_modules": workflow_modules
                },
                "last_operations": {
                    "generation": self.last_generation_time.isoformat() if self.last_generation_time else None,
                    "execution": self.last_execution_time.isoformat() if self.last_execution_time else None,
                    "fix": self.last_fix_time.isoformat() if self.last_fix_time else None
                },
                "latest_reports": latest_reports,
                "query_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取测试状态失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "query_time": datetime.now().isoformat()
            }
    
    async def run_full_test_cycle(self, fix_first: bool = True, parallel: bool = True, max_workers: int = 4) -> Dict[str, Any]:
        """
        运行完整的测试周期：生成 -> 修复 -> 执行
        
        Args:
            fix_first: 是否先修复现有问题
            parallel: 是否并行执行测试
            max_workers: 最大并发数
            
        Returns:
            完整周期结果字典
        """
        logger.info("开始运行完整测试周期...")
        cycle_start_time = datetime.now()
        
        results = {
            "cycle_start_time": cycle_start_time.isoformat(),
            "steps": []
        }
        
        try:
            # 步骤1: 生成测试框架
            logger.info("步骤1: 生成测试框架")
            generation_result = await self.generate_test_frameworks()
            results["steps"].append({
                "step": "generation",
                "result": generation_result
            })
            
            if generation_result["status"] != "success":
                logger.error("测试框架生成失败，终止周期")
                return results
            
            # 步骤2: 修复测试框架（如果需要）
            if fix_first:
                logger.info("步骤2: 修复测试框架")
                fix_result = await self.fix_test_frameworks()
                results["steps"].append({
                    "step": "fix",
                    "result": fix_result
                })
                
                if fix_result["status"] != "success":
                    logger.warning("测试框架修复失败，但继续执行")
            
            # 步骤3: 执行测试
            logger.info("步骤3: 执行测试")
            execution_result = await self.execute_all_tests(parallel=parallel, max_workers=max_workers)
            results["steps"].append({
                "step": "execution",
                "result": execution_result
            })
            
            # 计算总体结果
            cycle_end_time = datetime.now()
            cycle_duration = (cycle_end_time - cycle_start_time).total_seconds()
            
            all_success = all(step["result"]["status"] == "success" for step in results["steps"])
            
            results.update({
                "cycle_end_time": cycle_end_time.isoformat(),
                "cycle_duration": cycle_duration,
                "overall_status": "success" if all_success else "partial_failure",
                "summary": {
                    "total_steps": len(results["steps"]),
                    "successful_steps": len([s for s in results["steps"] if s["result"]["status"] == "success"]),
                    "failed_steps": len([s for s in results["steps"] if s["result"]["status"] != "success"])
                }
            })
            
            # 保存周期报告
            cycle_report_path = self.reports_path / f"full_cycle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(cycle_report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            results["cycle_report_path"] = str(cycle_report_path)
            
            logger.info(f"完整测试周期完成，总耗时: {cycle_duration:.2f}秒")
            return results
            
        except Exception as e:
            logger.error(f"完整测试周期失败: {e}")
            results.update({
                "cycle_end_time": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            })
            return results

# 异步上下文管理器支持
class AsyncTestManageMCP(TestManageMCP):
    """异步版本的Test Management MCP"""
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("Test Management MCP session ended")

# 便捷函数
async def create_test_manager(project_root: str = "/opt/powerautomation") -> TestManageMCP:
    """
    创建Test Management MCP实例
    
    Args:
        project_root: 项目根目录
        
    Returns:
        TestManageMCP实例
    """
    return TestManageMCP(project_root)

# 主函数用于直接运行
async def main():
    """主函数，用于直接运行测试管理"""
    test_manager = await create_test_manager()
    
    # 运行完整测试周期
    results = await test_manager.run_full_test_cycle()
    
    print("\\n" + "="*80)
    print("🎉 Test Management MCP 执行完成")
    print("="*80)
    print(f"总体状态: {results['overall_status']}")
    print(f"执行步骤: {results['summary']['successful_steps']}/{results['summary']['total_steps']} 成功")
    print(f"总耗时: {results.get('cycle_duration', 0):.2f}秒")
    
    if 'cycle_report_path' in results:
        print(f"详细报告: {results['cycle_report_path']}")

if __name__ == "__main__":
    asyncio.run(main())

