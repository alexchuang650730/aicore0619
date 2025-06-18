#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Workflow MCP 测试套件
Test Suite for Enhanced Workflow MCP

验证增强型工作流引擎的各项功能
"""

import asyncio
import json
import unittest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent))

# 导入测试模块
from enhanced_workflow_engine import (
    EnhancedWorkflowEngine, 
    EnhancedWorkflow, 
    WorkflowNode, 
    WorkflowEdge,
    WorkflowStatus,
    NodeStatus
)
from dynamic_workflow_generator import DynamicWorkflowGenerator
from parallel_execution_scheduler import ParallelExecutionScheduler
from intelligent_dependency_manager import IntelligentDependencyManager, DependencyType
from workflow_state_manager import WorkflowStateManager

class TestEnhancedWorkflowEngine(unittest.TestCase):
    """测试增强型工作流引擎"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = EnhancedWorkflowEngine()
        self.generator = DynamicWorkflowGenerator()
        self.scheduler = ParallelExecutionScheduler()
        self.dependency_manager = IntelligentDependencyManager()
        self.state_manager = WorkflowStateManager()
    
    def test_workflow_creation(self):
        """测试工作流创建"""
        # 创建测试节点
        node1 = WorkflowNode(
            id="node1",
            name="测试节点1",
            type="action",
            description="测试节点1的描述",
            config={"action": "test_action_1"}
        )
        
        node2 = WorkflowNode(
            id="node2",
            name="测试节点2", 
            type="action",
            description="测试节点2的描述",
            config={"action": "test_action_2"}
        )
        
        # 创建测试边
        edge1 = WorkflowEdge(
            source="node1",
            target="node2"
        )
        
        # 创建工作流
        workflow = EnhancedWorkflow(
            id="test_workflow",
            name="测试工作流",
            description="这是一个测试工作流",
            nodes=[node1, node2],
            edges=[edge1]
        )
        
        # 验证工作流创建
        self.assertEqual(workflow.id, "test_workflow")
        self.assertEqual(len(workflow.nodes), 2)
        self.assertEqual(len(workflow.edges), 1)
        self.assertEqual(workflow.status, WorkflowStatus.CREATED)
    
    async def test_dynamic_workflow_generation(self):
        """测试动态工作流生成"""
        config = {
            "name": "动态测试工作流",
            "description": "用于测试的动态生成工作流",
            "template_type": "basic",
            "requirements": ["数据处理", "结果输出"],
            "parallel_enabled": True
        }
        
        result = await self.generator.generate_workflow(config)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("workflow_id", result)
        self.assertGreater(result["nodes_count"], 0)
    
    async def test_dependency_management(self):
        """测试依赖管理"""
        # 添加依赖关系
        result = await self.dependency_manager.add_dependency(
            "node1", "node2", DependencyType.DATA,
            data_mapping={"output1": "input2"}
        )
        
        self.assertEqual(result["status"], "success")
        
        # 检测循环依赖
        result2 = await self.dependency_manager.add_dependency(
            "node2", "node1", DependencyType.CONTROL
        )
        
        self.assertEqual(result2["status"], "error")
        self.assertIn("循环依赖", result2["message"])
    
    async def test_parallel_execution(self):
        """测试并行执行"""
        # 创建测试工作流配置
        execution_config = {
            "workflow_id": "test_parallel_workflow",
            "execution_mode": "parallel",
            "max_workers": 2,
            "timeout": 60
        }
        
        # 模拟执行（实际测试中需要真实的工作流）
        # 这里只测试配置验证
        self.assertIsInstance(execution_config["max_workers"], int)
        self.assertGreater(execution_config["max_workers"], 0)
    
    async def test_workflow_state_management(self):
        """测试工作流状态管理"""
        # 创建测试工作流
        workflow = EnhancedWorkflow(
            id="state_test_workflow",
            name="状态测试工作流"
        )
        
        # 保存工作流
        result = await self.state_manager.save_workflow(workflow)
        self.assertEqual(result["status"], "success")
        
        # 获取工作流
        retrieved_workflow = await self.state_manager.get_workflow("state_test_workflow")
        self.assertIsNotNone(retrieved_workflow)
        self.assertEqual(retrieved_workflow.id, "state_test_workflow")
        
        # 更新状态
        result = await self.state_manager.update_workflow_status("state_test_workflow", "running")
        self.assertEqual(result["status"], "success")
        
        # 验证状态更新
        updated_workflow = await self.state_manager.get_workflow("state_test_workflow")
        self.assertEqual(updated_workflow.status, "running")

class TestWorkflowOptimization(unittest.TestCase):
    """测试工作流优化"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = EnhancedWorkflowEngine()
        self.dependency_manager = IntelligentDependencyManager()
    
    async def test_conflict_detection(self):
        """测试冲突检测"""
        # 创建有冲突的依赖关系
        await self.dependency_manager.add_dependency("A", "B", DependencyType.DATA)
        await self.dependency_manager.add_dependency("B", "C", DependencyType.DATA)
        await self.dependency_manager.add_dependency("C", "A", DependencyType.DATA)
        
        # 检测冲突
        conflicts = await self.dependency_manager._detect_conflicts()
        
        # 应该检测到循环依赖
        self.assertGreater(len(conflicts), 0)
        
        # 验证冲突类型
        circular_conflicts = [c for c in conflicts.values() if c.conflict_type.value == "circular_dependency"]
        self.assertGreater(len(circular_conflicts), 0)
    
    async def test_topological_sorting(self):
        """测试拓扑排序"""
        # 创建DAG
        await self.dependency_manager.add_dependency("A", "B", DependencyType.CONTROL)
        await self.dependency_manager.add_dependency("A", "C", DependencyType.CONTROL)
        await self.dependency_manager.add_dependency("B", "D", DependencyType.CONTROL)
        await self.dependency_manager.add_dependency("C", "D", DependencyType.CONTROL)
        
        # 计算拓扑排序
        topological_order = self.dependency_manager._calculate_topological_order()
        
        # 验证排序结果
        self.assertGreater(len(topological_order), 0)
        
        # A应该在第一层
        self.assertIn("A", topological_order[0])
        
        # D应该在最后一层
        last_layer = topological_order[-1]
        self.assertIn("D", last_layer)

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = EnhancedWorkflowEngine()
        self.generator = DynamicWorkflowGenerator()
        self.scheduler = ParallelExecutionScheduler()
        self.dependency_manager = IntelligentDependencyManager()
        self.state_manager = WorkflowStateManager()
    
    async def test_end_to_end_workflow(self):
        """端到端工作流测试"""
        # 1. 生成工作流
        config = {
            "name": "端到端测试工作流",
            "description": "完整的端到端测试",
            "template_type": "professional",
            "requirements": ["数据输入", "数据处理", "数据输出"],
            "parallel_enabled": True,
            "optimization_enabled": True
        }
        
        generation_result = await self.generator.generate_workflow(config)
        self.assertEqual(generation_result["status"], "success")
        
        workflow_id = generation_result["workflow_id"]
        
        # 2. 获取生成的工作流
        workflow = await self.state_manager.get_workflow(workflow_id)
        self.assertIsNotNone(workflow)
        
        # 3. 分析依赖关系
        analysis_result = await self.dependency_manager.analyze_dependencies(workflow)
        self.assertEqual(analysis_result["status"], "success")
        
        # 4. 优化工作流
        optimization_config = {
            "workflow_id": workflow_id,
            "optimization_type": "auto",
            "enable_parallelization": True,
            "resolve_conflicts": True
        }
        
        optimization_result = await self.engine.optimize_workflow(optimization_config)
        self.assertEqual(optimization_result["status"], "success")
        
        # 5. 验证优化结果
        optimized_workflow = await self.state_manager.get_workflow(workflow_id)
        self.assertIsNotNone(optimized_workflow)

def run_performance_test():
    """性能测试"""
    print("🚀 开始性能测试...")
    
    async def performance_test():
        generator = DynamicWorkflowGenerator()
        
        import time
        start_time = time.time()
        
        # 生成多个工作流
        tasks = []
        for i in range(10):
            config = {
                "name": f"性能测试工作流_{i}",
                "template_type": "basic",
                "requirements": ["测试需求"],
                "parallel_enabled": True
            }
            tasks.append(generator.generate_workflow(config))
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        successful_generations = len([r for r in results if r["status"] == "success"])
        
        print(f"✅ 性能测试完成:")
        print(f"   生成工作流数量: {len(tasks)}")
        print(f"   成功生成: {successful_generations}")
        print(f"   总耗时: {execution_time:.2f}秒")
        print(f"   平均耗时: {execution_time/len(tasks):.2f}秒/个")
        print(f"   成功率: {successful_generations/len(tasks)*100:.1f}%")
    
    asyncio.run(performance_test())

def run_stress_test():
    """压力测试"""
    print("💪 开始压力测试...")
    
    async def stress_test():
        dependency_manager = IntelligentDependencyManager()
        
        import time
        start_time = time.time()
        
        # 创建大量依赖关系
        tasks = []
        for i in range(100):
            for j in range(i+1, min(i+10, 100)):  # 每个节点最多连接10个其他节点
                tasks.append(dependency_manager.add_dependency(
                    f"node_{i}", f"node_{j}", DependencyType.DATA
                ))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        successful_additions = len([r for r in results if isinstance(r, dict) and r.get("status") == "success"])
        
        print(f"✅ 压力测试完成:")
        print(f"   尝试添加依赖: {len(tasks)}")
        print(f"   成功添加: {successful_additions}")
        print(f"   总耗时: {execution_time:.2f}秒")
        print(f"   平均耗时: {execution_time/len(tasks)*1000:.2f}毫秒/个")
        print(f"   成功率: {successful_additions/len(tasks)*100:.1f}%")
        
        # 检测冲突
        conflicts = await dependency_manager._detect_conflicts()
        print(f"   检测到冲突: {len(conflicts)}")
    
    asyncio.run(stress_test())

async def run_all_tests():
    """运行所有测试"""
    print("🧪 开始运行增强型工作流引擎测试套件")
    print("=" * 60)
    
    # 单元测试
    print("\n📋 运行单元测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestEnhancedWorkflowEngine))
    test_suite.addTest(unittest.makeSuite(TestWorkflowOptimization))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 显示测试结果
    print(f"\n📊 单元测试结果:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    print(f"   成功率: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun*100:.1f}%")
    
    # 性能测试
    print(f"\n⚡ 运行性能测试...")
    run_performance_test()
    
    # 压力测试
    print(f"\n💪 运行压力测试...")
    run_stress_test()
    
    print(f"\n✅ 所有测试完成!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "unit":
            # 只运行单元测试
            unittest.main(argv=[''], exit=False)
        elif test_type == "performance":
            run_performance_test()
        elif test_type == "stress":
            run_stress_test()
        else:
            print("❌ 未知测试类型。可用选项: unit, performance, stress")
            sys.exit(1)
    else:
        # 运行所有测试
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)

