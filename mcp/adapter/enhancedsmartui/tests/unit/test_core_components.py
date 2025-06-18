#!/usr/bin/env python3
"""
SmartUI Enhanced 单元测试
测试核心组件的功能
"""

import unittest
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from core.api_state_manager import APIStateManager, APIRoute
from engines.user_analyzer import UserAnalyzer
from engines.decision_engine import DecisionEngine
from engines.ui_generator import UIGenerator

class TestAPIStateManager(unittest.TestCase):
    """测试API状态管理器"""
    
    def setUp(self):
        self.manager = APIStateManager()
    
    def test_route_registration(self):
        """测试路由注册"""
        route = APIRoute(
            path="/test",
            method="GET",
            handler=lambda: "test"
        )
        
        result = self.manager.register_route(route)
        self.assertTrue(result)
        self.assertIn("/test", self.manager.routes)
    
    def test_state_transition(self):
        """测试状态转换"""
        initial_state = self.manager.get_current_state()
        self.assertEqual(initial_state, "idle")
        
        self.manager.transition_to("processing")
        current_state = self.manager.get_current_state()
        self.assertEqual(current_state, "processing")

class TestUserAnalyzer(unittest.TestCase):
    """测试用户分析引擎"""
    
    def setUp(self):
        self.analyzer = UserAnalyzer()
    
    def test_user_input_analysis(self):
        """测试用户输入分析"""
        user_input = {
            "action": "start_coding",
            "context": {"language": "python"},
            "timestamp": 1750183800
        }
        
        result = self.analyzer.analyze_user_input(user_input)
        
        self.assertIsInstance(result, dict)
        self.assertIn("user_intent", result)
        self.assertIn("confidence", result)
    
    def test_behavior_pattern_detection(self):
        """测试行为模式检测"""
        interactions = [
            {"action": "click", "target": "button", "timestamp": 1750183800},
            {"action": "type", "target": "input", "timestamp": 1750183801},
            {"action": "click", "target": "submit", "timestamp": 1750183802}
        ]
        
        patterns = self.analyzer.detect_behavior_patterns(interactions)
        
        self.assertIsInstance(patterns, list)
        self.assertTrue(len(patterns) > 0)

class TestDecisionEngine(unittest.TestCase):
    """测试决策引擎"""
    
    def setUp(self):
        self.engine = DecisionEngine()
    
    def test_ui_decision_making(self):
        """测试UI决策制定"""
        context = {
            "user_analysis": {
                "user_intent": "code_editing",
                "experience_level": "intermediate"
            },
            "environment": {
                "device_type": "desktop",
                "screen_size": "large"
            },
            "workflow_context": {
                "stage": "development",
                "task_type": "web_development"
            }
        }
        
        decision = self.engine.make_ui_decision(context)
        
        self.assertIsInstance(decision, dict)
        self.assertIn("layout", decision)
        self.assertIn("components", decision)
        self.assertIn("theme", decision)
    
    def test_rule_evaluation(self):
        """测试规则评估"""
        rules = [
            {
                "condition": "user_intent == 'code_editing'",
                "action": "use_coding_layout",
                "priority": 1
            }
        ]
        
        context = {"user_intent": "code_editing"}
        
        result = self.engine.evaluate_rules(rules, context)
        self.assertTrue(result)

class TestUIGenerator(unittest.TestCase):
    """测试UI生成引擎"""
    
    def setUp(self):
        self.generator = UIGenerator()
    
    def test_component_generation(self):
        """测试组件生成"""
        component_spec = {
            "type": "button",
            "variant": "primary",
            "props": {
                "text": "Click Me",
                "onclick": "handleClick()"
            }
        }
        
        html = self.generator.generate_component(component_spec)
        
        self.assertIsInstance(html, str)
        self.assertIn("button", html)
        self.assertIn("Click Me", html)
    
    def test_layout_generation(self):
        """测试布局生成"""
        layout_spec = {
            "type": "grid",
            "columns": 2,
            "components": [
                {"type": "button", "props": {"text": "Button 1"}},
                {"type": "button", "props": {"text": "Button 2"}}
            ]
        }
        
        html = self.generator.generate_layout(layout_spec)
        
        self.assertIsInstance(html, str)
        self.assertIn("grid", html)
        self.assertIn("Button 1", html)
        self.assertIn("Button 2", html)
    
    def test_theme_application(self):
        """测试主题应用"""
        theme_spec = {
            "name": "dark",
            "colors": {
                "primary": "#ffffff",
                "background": "#000000"
            }
        }
        
        css = self.generator.apply_theme(theme_spec)
        
        self.assertIsInstance(css, str)
        self.assertIn("--primary-color: #ffffff", css)
        self.assertIn("--background-color: #000000", css)

if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestAPIStateManager))
    test_suite.addTest(unittest.makeSuite(TestUserAnalyzer))
    test_suite.addTest(unittest.makeSuite(TestDecisionEngine))
    test_suite.addTest(unittest.makeSuite(TestUIGenerator))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果
    if result.wasSuccessful():
        print("\n✅ 所有测试通过!")
    else:
        print(f"\n❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        
        for failure in result.failures:
            print(f"失败: {failure[0]}")
            print(f"详情: {failure[1]}")
        
        for error in result.errors:
            print(f"错误: {error[0]}")
            print(f"详情: {error[1]}")

