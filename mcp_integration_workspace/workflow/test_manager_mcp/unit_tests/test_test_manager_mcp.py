#!/usr/bin/env python3
"""
Test Manager MCP 单元测试
测试test_manager_mcp的核心功能
"""

import unittest
import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp.workflow.test_manager_mcp.test_manager_mcp import TestManagerMCP

class TestTestManagerMCP(unittest.TestCase):
    """Test Manager MCP 测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_manager_mcp = TestManagerMCP()
        self.sample_project_info = {
            "name": "贪吃蛇游戏",
            "type": "game",
            "complexity": "simple",
            "description": "一个简单的贪吃蛇游戏"
        }
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.test_manager_mcp.service_id, "test_manager_mcp")
        self.assertEqual(self.test_manager_mcp.version, "1.0.0")
        self.assertEqual(self.test_manager_mcp.status, "running")
        self.assertIsNotNone(self.test_manager_mcp.test_manager)
    
    def test_determine_test_strategy(self):
        """测试测试策略确定"""
        # 测试游戏项目策略
        strategy = self.test_manager_mcp._determine_test_strategy("game", "simple")
        self.assertEqual(strategy["test_type"], "simple")
        self.assertIn("游戏逻辑", strategy["focus_areas"])
        
        # 测试Web应用策略
        strategy = self.test_manager_mcp._determine_test_strategy("web_app", "complex")
        self.assertEqual(strategy["test_type"], "comprehensive")
        self.assertIn("API测试", strategy["focus_areas"])
    
    def test_generate_test_plan(self):
        """测试测试计划生成"""
        # 模拟发现的测试
        mock_tests = [
            {"test_name": "test_game_logic", "test_type": "unit"},
            {"test_name": "test_ui_interaction", "test_type": "integration"},
            {"test_name": "test_performance", "test_type": "performance"}
        ]
        
        test_plan = self.test_manager_mcp._generate_test_plan(self.sample_project_info, mock_tests)
        
        self.assertEqual(test_plan["project_name"], "贪吃蛇游戏")
        self.assertEqual(test_plan["total_tests"], 3)
        self.assertIn("execution_phases", test_plan)
        self.assertGreater(len(test_plan["execution_phases"]), 0)
    
    def test_create_fallback_test_plan(self):
        """测试备用测试计划创建"""
        fallback_plan = self.test_manager_mcp._create_fallback_test_plan(self.sample_project_info)
        
        self.assertEqual(fallback_plan["project_name"], "贪吃蛇游戏")
        self.assertIn("test_template", fallback_plan)
        self.assertGreater(fallback_plan["total_template_tests"], 0)
    
    @patch('mcp.workflow.test_manager_mcp.test_manager_mcp.get_test_manager')
    def test_discover_tests_by_project(self, mock_get_test_manager):
        """测试项目测试发现"""
        # 模拟测试管理器
        mock_manager = Mock()
        mock_manager.discover_tests = AsyncMock(return_value=[
            {"test_name": "test_snake_movement", "test_type": "unit"},
            {"test_name": "test_food_collision", "test_type": "unit"}
        ])
        mock_get_test_manager.return_value = mock_manager
        
        # 创建新的实例以使用模拟的管理器
        test_mcp = TestManagerMCP()
        test_mcp.test_manager = mock_manager
        
        # 运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            test_mcp.discover_tests_by_project(self.sample_project_info)
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["project_name"], "贪吃蛇游戏")
        self.assertEqual(result["discovered_tests"], 2)
        self.assertIn("test_plan", result)
    
    def test_execute_template_tests(self):
        """测试模板测试执行"""
        test_template = [
            {"name": "游戏逻辑测试", "type": "unit", "description": "测试游戏核心逻辑"},
            {"name": "UI交互测试", "type": "integration", "description": "测试用户界面交互"}
        ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(
            self.test_manager_mcp._execute_template_tests(test_template)
        )
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("name", result)
            self.assertIn("status", result)
            self.assertIn("duration", result)
    
    def test_generate_test_report(self):
        """测试测试报告生成"""
        # 模拟测试结果
        mock_results = [
            {"name": "测试1", "status": "passed", "duration": 0.1},
            {"name": "测试2", "status": "failed", "duration": 0.2},
            {"name": "测试3", "status": "passed", "duration": 0.15}
        ]
        
        mock_test_plan = {
            "project_name": "贪吃蛇游戏",
            "total_tests": 3
        }
        
        report = self.test_manager_mcp._generate_test_report(
            self.sample_project_info, mock_test_plan, mock_results
        )
        
        self.assertEqual(report["project_name"], "贪吃蛇游戏")
        self.assertEqual(report["test_execution_summary"]["total_tests"], 3)
        self.assertEqual(report["test_execution_summary"]["passed"], 2)
        self.assertEqual(report["test_execution_summary"]["failed"], 1)
        self.assertAlmostEqual(report["test_execution_summary"]["success_rate"], 66.67, places=1)
    
    def test_generate_recommendations(self):
        """测试建议生成"""
        # 测试高成功率
        recommendations = self.test_manager_mcp._generate_recommendations(95.0, [])
        self.assertIn("测试成功率良好", recommendations[0])
        
        # 测试低成功率
        recommendations = self.test_manager_mcp._generate_recommendations(60.0, [])
        self.assertIn("测试成功率较低", recommendations[0])
        
        # 测试有失败测试的情况
        failed_results = [
            {"status": "failed"},
            {"status": "passed"},
            {"status": "failed"}
        ]
        recommendations = self.test_manager_mcp._generate_recommendations(50.0, failed_results)
        self.assertTrue(any("失败测试" in rec for rec in recommendations))
    
    def test_generate_next_steps(self):
        """测试下一步建议生成"""
        # 测试高成功率
        next_steps = self.test_manager_mcp._generate_next_steps(self.sample_project_info, 95.0)
        self.assertTrue(any("可以进行部署" in step for step in next_steps))
        
        # 测试中等成功率
        next_steps = self.test_manager_mcp._generate_next_steps(self.sample_project_info, 75.0)
        self.assertTrue(any("修复后重新测试" in step for step in next_steps))
        
        # 测试低成功率
        next_steps = self.test_manager_mcp._generate_next_steps(self.sample_project_info, 50.0)
        self.assertTrue(any("不建议部署" in step for step in next_steps))

class TestTestManagerMCPIntegration(unittest.TestCase):
    """Test Manager MCP 集成测试"""
    
    def setUp(self):
        """设置集成测试环境"""
        self.test_manager_mcp = TestManagerMCP()
        self.complex_project_info = {
            "name": "电商平台",
            "type": "ecommerce",
            "complexity": "complex",
            "description": "一个完整的电商平台系统"
        }
    
    def test_full_test_cycle_integration(self):
        """测试完整测试周期集成"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 1. 发现测试
        discovery_result = loop.run_until_complete(
            self.test_manager_mcp.discover_tests_by_project(self.complex_project_info)
        )
        
        # 验证发现结果
        self.assertTrue(discovery_result["success"] or "fallback_plan" in discovery_result)
        
        # 2. 执行测试
        test_plan = discovery_result.get("test_plan", discovery_result.get("fallback_plan", {}))
        execution_result = loop.run_until_complete(
            self.test_manager_mcp.execute_test_plan(test_plan, self.complex_project_info)
        )
        
        # 验证执行结果
        self.assertTrue(execution_result["success"])
        self.assertEqual(execution_result["project_name"], "电商平台")
        self.assertIn("test_report", execution_result)
    
    def test_different_project_types(self):
        """测试不同项目类型的处理"""
        project_types = [
            {"name": "API服务", "type": "api", "complexity": "medium"},
            {"name": "移动应用", "type": "mobile", "complexity": "complex"},
            {"name": "数据分析", "type": "data", "complexity": "simple"}
        ]
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for project_info in project_types:
            with self.subTest(project_type=project_info["type"]):
                result = loop.run_until_complete(
                    self.test_manager_mcp.discover_tests_by_project(project_info)
                )
                
                # 每种项目类型都应该能够处理
                self.assertTrue(result["success"] or "fallback_plan" in result)

def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加单元测试
    test_suite.addTest(unittest.makeSuite(TestTestManagerMCP))
    
    # 添加集成测试
    test_suite.addTest(unittest.makeSuite(TestTestManagerMCPIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success": result.wasSuccessful(),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0
    }

if __name__ == '__main__':
    print("🧪 Test Manager MCP 单元测试")
    print("=" * 50)
    
    test_results = run_all_tests()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"   总测试数: {test_results['tests_run']}")
    print(f"   失败数: {test_results['failures']}")
    print(f"   错误数: {test_results['errors']}")
    print(f"   成功率: {test_results['success_rate']:.1f}%")
    print(f"   整体状态: {'✅ 通过' if test_results['success'] else '❌ 失败'}")

