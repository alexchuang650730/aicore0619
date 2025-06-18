#!/usr/bin/env python3
"""
SmartUI Enhanced 集成测试
测试完整的工作流程和MCP集成
"""

import unittest
import requests
import time
import json
import subprocess
import signal
import os
import sys

class TestSmartUIIntegration(unittest.TestCase):
    """SmartUI Enhanced 集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """启动测试服务"""
        print("启动SmartUI Enhanced服务...")
        
        # 启动主服务器
        cls.server_process = subprocess.Popen([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), '../../main_server.py')
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        time.sleep(3)
        
        # 验证服务是否启动成功
        try:
            response = requests.get('http://localhost:5002/health', timeout=5)
            if response.status_code != 200:
                raise Exception("服务启动失败")
        except Exception as e:
            cls.tearDownClass()
            raise Exception(f"无法连接到SmartUI Enhanced服务: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """停止测试服务"""
        if hasattr(cls, 'server_process'):
            cls.server_process.terminate()
            cls.server_process.wait()
    
    def test_health_check(self):
        """测试健康检查"""
        response = requests.get('http://localhost:5002/health')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'SmartUI Enhanced')
        self.assertIn('components', data)
    
    def test_capabilities_endpoint(self):
        """测试能力查询端点"""
        response = requests.get('http://localhost:5002/api/capabilities')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('capabilities', data)
        self.assertIn('ui_generation', data['capabilities'])
        self.assertIn('user_analysis', data['capabilities'])
    
    def test_mcp_request_handling(self):
        """测试MCP请求处理"""
        request_data = {
            "action": "modify_ui",
            "params": {
                "request_id": "integration_test_001",
                "source_mcp": "test_mcp",
                "modification_request": {
                    "ui_requirements": {
                        "layout_changes": {
                            "primary_layout": "grid"
                        },
                        "component_updates": [
                            {
                                "component_id": "test_button",
                                "component_type": "button",
                                "props": {
                                    "text": "Test Button"
                                }
                            }
                        ],
                        "theme_adjustments": {
                            "color_scheme": "light"
                        }
                    }
                }
            }
        }
        
        response = requests.post(
            'http://localhost:5002/mcp/request',
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('modification_result', data)
        self.assertTrue(data['modification_result']['ui_generated'])
    
    def test_ui_generation_endpoint(self):
        """测试UI生成端点"""
        request_data = {
            "request_id": "ui_gen_test_001",
            "modification_request": {
                "ui_requirements": {
                    "layout_changes": {
                        "primary_layout": "coding_workspace"
                    },
                    "component_updates": [
                        {
                            "component_id": "code_editor",
                            "component_type": "code_editor",
                            "props": {
                                "language": "python",
                                "theme": "dark"
                            }
                        }
                    ]
                }
            }
        }
        
        response = requests.post(
            'http://localhost:5002/api/ui/generate',
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('modification_result', data)
    
    def test_complex_workflow_scenario(self):
        """测试复杂工作流场景"""
        # 场景1: 代码生成工作流
        coding_request = {
            "action": "modify_ui",
            "params": {
                "request_id": "workflow_coding_001",
                "modification_request": {
                    "modification_type": "dynamic_update",
                    "trigger_context": {
                        "workflow_stage": "code_generation",
                        "user_action": "start_coding_session",
                        "environment": {
                            "task_type": "web_development",
                            "framework": "react"
                        }
                    },
                    "ui_requirements": {
                        "layout_changes": {
                            "primary_layout": "coding_workspace"
                        },
                        "component_updates": [
                            {
                                "component_id": "code_editor",
                                "component_type": "code_editor",
                                "props": {
                                    "language": "javascript",
                                    "theme": "vs-dark"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        response = requests.post(
            'http://localhost:5002/mcp/request',
            json=coding_request,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['modification_result']['layout_applied'], 'coding_workspace')
        
        # 场景2: 切换到测试工作流
        testing_request = {
            "action": "modify_ui",
            "params": {
                "request_id": "workflow_testing_001",
                "modification_request": {
                    "modification_type": "workflow_transition",
                    "trigger_context": {
                        "workflow_stage": "testing",
                        "previous_stage": "code_generation"
                    },
                    "ui_requirements": {
                        "layout_changes": {
                            "primary_layout": "testing_workspace"
                        },
                        "component_updates": [
                            {
                                "component_id": "test_runner",
                                "component_type": "test_runner",
                                "props": {
                                    "framework": "jest"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        response = requests.post(
            'http://localhost:5002/mcp/request',
            json=testing_request,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['modification_result']['layout_applied'], 'testing_workspace')
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的请求
        invalid_request = {
            "action": "invalid_action",
            "params": {}
        }
        
        response = requests.post(
            'http://localhost:5002/mcp/request',
            json=invalid_request,
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertEqual(data['success'], False)
        self.assertIn('error', data)
    
    def test_performance_metrics(self):
        """测试性能指标"""
        start_time = time.time()
        
        request_data = {
            "action": "modify_ui",
            "params": {
                "request_id": "performance_test_001",
                "modification_request": {
                    "ui_requirements": {
                        "component_updates": [
                            {
                                "component_id": f"component_{i}",
                                "component_type": "button",
                                "props": {"text": f"Button {i}"}
                            } for i in range(10)  # 生成10个组件
                        ]
                    }
                }
            }
        }
        
        response = requests.post(
            'http://localhost:5002/mcp/request',
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0)  # 响应时间应小于2秒
        
        data = response.json()
        self.assertIn('performance_metrics', data['modification_result'])

if __name__ == '__main__':
    # 运行集成测试
    unittest.main(verbosity=2)

