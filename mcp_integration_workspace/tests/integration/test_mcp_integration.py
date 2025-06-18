"""
PowerAutomation 测试管理 - 整合测试套件

验证工作流层和适配器层的协作功能。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

import asyncio
import unittest
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# 添加路径以导入模块
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.interfaces import (
    TestStrategy, TestPlan, TestCase, TestType, ExecutionMode,
    get_message_bus, create_workflow_adapter, create_adapter_communication
)

from workflow.test_manager_mcp.test_manager_mcp import TestManagerMCP
from adapter.test_execution_engine.test_execution_engine import TestExecutionEngine


class TestIntegration(unittest.TestCase):
    """测试管理MCP组件整合测试"""
    
    def setUp(self):
        """测试设置"""
        self.test_root = "/tmp/powerautomation_test"
        Path(self.test_root).mkdir(exist_ok=True)
        
        # 创建组件实例
        self.manager = TestManagerMCP(self.test_root)
        self.engine = TestExecutionEngine(self.test_root)
        
        # 获取消息总线
        self.message_bus = get_message_bus()
    
    def tearDown(self):
        """测试清理"""
        # 清理测试数据
        import shutil
        if Path(self.test_root).exists():
            shutil.rmtree(self.test_root)
    
    async def test_strategy_creation(self):
        """测试策略创建功能"""
        # 创建测试策略
        requirements = {
            "name": "集成测试策略",
            "description": "用于集成测试的策略",
            "template": "unit_testing",
            "target_modules": ["module1", "module2"],
            "max_workers": 2
        }
        
        strategy = await self.manager.create_test_strategy(requirements)
        
        # 验证策略创建
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.name, "集成测试策略")
        self.assertEqual(len(strategy.target_modules), 2)
        self.assertEqual(strategy.max_workers, 2)
        self.assertIn(TestType.UNIT, strategy.test_types)
    
    async def test_framework_generation(self):
        """测试框架生成功能"""
        modules = ["test_module1", "test_module2"]
        
        result = await self.engine.generate_test_frameworks(modules)
        
        # 验证生成结果
        self.assertEqual(result["status"], "success")
        self.assertIn("results", result)
        self.assertIn("generation_time", result)
    
    async def test_workflow_execution(self):
        """测试完整工作流执行"""
        # 创建测试策略
        strategy = await self.manager.create_test_strategy({
            "name": "工作流测试策略",
            "template": "unit_testing",
            "target_modules": ["workflow_test_module"]
        })
        
        # 模拟适配器层响应
        with patch.object(self.manager.communication, 'request_framework_generation') as mock_framework:
            mock_framework.return_value = {"status": "success", "generated_files": 2}
            
            with patch.object(self.manager.communication, 'request_test_execution') as mock_execution:
                mock_execution.return_value = {
                    "status": "completed",
                    "passed_tests": 8,
                    "failed_tests": 1,
                    "skipped_tests": 0,
                    "error_tests": 1
                }
                
                # 执行工作流
                result = await self.manager.execute_test_workflow(strategy)
                
                # 验证执行结果
                self.assertIsNotNone(result)
                self.assertEqual(result.strategy_id, strategy.id)
                self.assertGreater(result.total_tests, 0)
    
    async def test_communication_protocol(self):
        """测试组件间通信协议"""
        # 创建通信适配器
        workflow_adapter = create_workflow_adapter()
        adapter_communication = create_adapter_communication()
        
        # 测试消息发送
        test_message = {
            "action": "test_communication",
            "data": {"test": "value"}
        }
        
        response = await workflow_adapter.send_request(
            target="test_execution_engine",
            payload=test_message
        )
        
        # 验证通信
        self.assertIsNotNone(response)
        self.assertEqual(response.type.value, "response")
    
    async def test_event_publishing(self):
        """测试事件发布和订阅"""
        from shared.interfaces import EventType
        
        # 设置事件监听器
        received_events = []
        
        async def event_handler(event):
            received_events.append(event)
        
        # 订阅事件
        self.manager.communication.subscribe_to_event(
            EventType.TEST_STARTED,
            event_handler
        )
        
        # 发布事件
        await self.manager.communication.publish_event(
            EventType.TEST_STARTED,
            {"test_id": "test_001", "module": "test_module"}
        )
        
        # 等待事件处理
        await asyncio.sleep(0.1)
        
        # 验证事件接收
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].type, EventType.TEST_STARTED)
    
    async def test_error_handling(self):
        """测试错误处理机制"""
        # 测试无效策略创建
        with self.assertRaises(Exception):
            await self.manager.create_test_strategy({
                "invalid_field": "invalid_value"
            })
        
        # 测试无效模块生成
        result = await self.engine.generate_test_frameworks([])
        self.assertEqual(result["status"], "success")  # 空模块列表应该成功处理
    
    async def test_performance_monitoring(self):
        """测试性能监控功能"""
        # 获取引擎状态
        engine_status = self.engine.get_engine_status()
        self.assertIn("status", engine_status)
        self.assertEqual(engine_status["status"], "active")
        
        # 获取管理器状态
        manager_status = self.manager.get_manager_status()
        self.assertIn("status", manager_status)
        self.assertEqual(manager_status["status"], "active")
    
    def test_data_model_serialization(self):
        """测试数据模型序列化"""
        from shared.interfaces import serialize_model, TestCase
        
        # 创建测试用例
        test_case = TestCase(
            id="test_001",
            name="序列化测试",
            description="测试数据模型序列化功能",
            test_type=TestType.UNIT,
            module_name="serialization_test",
            file_path="/test/serialization_test.py",
            function_name="test_serialization"
        )
        
        # 序列化
        serialized = serialize_model(test_case)
        self.assertIsInstance(serialized, str)
        self.assertIn("test_001", serialized)
        self.assertIn("序列化测试", serialized)


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def setUp(self):
        self.test_root = "/tmp/powerautomation_perf_test"
        Path(self.test_root).mkdir(exist_ok=True)
        self.manager = TestManagerMCP(self.test_root)
        self.engine = TestExecutionEngine(self.test_root)
    
    def tearDown(self):
        import shutil
        if Path(self.test_root).exists():
            shutil.rmtree(self.test_root)
    
    async def test_concurrent_strategy_creation(self):
        """测试并发策略创建性能"""
        start_time = datetime.now()
        
        # 并发创建多个策略
        tasks = []
        for i in range(5):
            task = self.manager.create_test_strategy({
                "name": f"并发测试策略_{i}",
                "template": "unit_testing",
                "target_modules": [f"module_{i}"]
            })
            tasks.append(task)
        
        strategies = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 验证性能
        self.assertEqual(len(strategies), 5)
        self.assertLess(duration, 5.0)  # 应该在5秒内完成
        
        # 验证策略唯一性
        strategy_ids = [s.id for s in strategies]
        self.assertEqual(len(set(strategy_ids)), 5)
    
    async def test_large_module_generation(self):
        """测试大量模块的框架生成性能"""
        # 生成大量模块
        modules = [f"large_module_{i}" for i in range(20)]
        
        start_time = datetime.now()
        result = await self.engine.generate_test_frameworks(modules)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        # 验证性能和结果
        self.assertEqual(result["status"], "success")
        self.assertLess(duration, 30.0)  # 应该在30秒内完成


async def run_integration_tests():
    """运行集成测试"""
    print("开始运行PowerAutomation测试管理MCP整合测试...")
    
    # 创建测试套件
    integration_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
    performance_suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformance)
    
    # 运行集成测试
    print("\n=== 运行集成测试 ===")
    integration_runner = unittest.TextTestRunner(verbosity=2)
    
    # 由于unittest不直接支持async，我们需要手动运行async测试
    test_instance = TestIntegration()
    test_instance.setUp()
    
    try:
        print("测试策略创建...")
        await test_instance.test_strategy_creation()
        print("✓ 策略创建测试通过")
        
        print("测试框架生成...")
        await test_instance.test_framework_generation()
        print("✓ 框架生成测试通过")
        
        print("测试工作流执行...")
        await test_instance.test_workflow_execution()
        print("✓ 工作流执行测试通过")
        
        print("测试通信协议...")
        await test_instance.test_communication_protocol()
        print("✓ 通信协议测试通过")
        
        print("测试事件发布...")
        await test_instance.test_event_publishing()
        print("✓ 事件发布测试通过")
        
        print("测试错误处理...")
        await test_instance.test_error_handling()
        print("✓ 错误处理测试通过")
        
        print("测试性能监控...")
        await test_instance.test_performance_monitoring()
        print("✓ 性能监控测试通过")
        
        print("测试数据模型序列化...")
        test_instance.test_data_model_serialization()
        print("✓ 数据模型序列化测试通过")
        
    finally:
        test_instance.tearDown()
    
    # 运行性能测试
    print("\n=== 运行性能测试 ===")
    perf_instance = TestPerformance()
    perf_instance.setUp()
    
    try:
        print("测试并发策略创建性能...")
        await perf_instance.test_concurrent_strategy_creation()
        print("✓ 并发策略创建性能测试通过")
        
        print("测试大量模块生成性能...")
        await perf_instance.test_large_module_generation()
        print("✓ 大量模块生成性能测试通过")
        
    finally:
        perf_instance.tearDown()
    
    print("\n=== 所有测试完成 ===")
    print("✓ 集成测试全部通过")
    print("✓ 性能测试全部通过")
    print("PowerAutomation测试管理MCP整合验证成功！")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_integration_tests())

