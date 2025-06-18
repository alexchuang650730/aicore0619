"""
SmartUI MCP - 集成测试

测试整个系统的集成功能，包括组件间协作、API接口、WebSocket通信等。
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import httpx

from src.main_server import SmartUIMCPServer, create_server
from src.config import ConfigManager


class TestServerIntegration:
    """服务器集成测试类"""
    
    @pytest.fixture
    async def test_server(self):
        """创建测试服务器实例"""
        # 创建测试配置
        test_config = {
            'environment': 'test',
            'debug': True,
            'server': {
                'host': '127.0.0.1',
                'port': 8001,
                'cors_enabled': True
            },
            'database': {
                'type': 'sqlite',
                'database': ':memory:'
            },
            'logging': {
                'level': 'DEBUG',
                'console_output': False
            },
            'intelligence': {
                'user_analyzer_enabled': True,
                'decision_engine_enabled': True,
                'ui_generator_enabled': True,
                'mcp_integration_enabled': False  # 禁用外部依赖
            }
        }
        
        # 创建临时配置文件
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_file = f.name
        
        # 创建服务器
        server = SmartUIMCPServer(config_file)
        await server.initialize()
        
        yield server
        
        # 清理
        await server.stop()
        import os
        os.unlink(config_file)
    
    @pytest.mark.asyncio
    async def test_server_startup_shutdown(self, test_server):
        """测试服务器启动和关闭"""
        # 启动服务器
        success = await test_server.start()
        assert success
        assert test_server.running
        assert test_server.startup_time is not None
        
        # 检查组件状态
        assert test_server.user_analyzer is not None
        assert test_server.decision_engine is not None
        assert test_server.api_state_manager is not None
        
        # 关闭服务器
        success = await test_server.stop()
        assert success
        assert not test_server.running
    
    @pytest.mark.asyncio
    async def test_api_endpoints(self, test_server):
        """测试API端点"""
        await test_server.start()
        
        # 使用TestClient测试API
        with TestClient(test_server.app) as client:
            # 测试健康检查
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            
            # 测试状态接口
            response = client.get("/api/status")
            assert response.status_code == 200
            data = response.json()
            assert "running" in data
            assert "components" in data
            
            # 测试配置接口
            response = client.get("/api/config")
            assert response.status_code == 200
            data = response.json()
            assert "environment" in data
            assert "features" in data
        
        await test_server.stop()
    
    @pytest.mark.asyncio
    async def test_user_interaction_flow(self, test_server):
        """测试用户交互流程"""
        await test_server.start()
        
        with TestClient(test_server.app) as client:
            # 记录用户交互
            interaction_data = {
                "user_id": "test_user",
                "type": "click",
                "target": "button",
                "timestamp": "2024-01-01T12:00:00Z",
                "context": {"page": "home"}
            }
            
            response = client.post("/api/user/interaction", json=interaction_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # 获取用户画像
            response = client.get("/api/user/profile?user_id=test_user")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
        
        await test_server.stop()
    
    @pytest.mark.asyncio
    async def test_state_management_flow(self, test_server):
        """测试状态管理流程"""
        await test_server.start()
        
        with TestClient(test_server.app) as client:
            # 设置状态
            state_data = {"value": "dark"}
            response = client.post("/api/state/user.theme", json=state_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # 获取状态
            response = client.get("/api/state/user.theme")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"] == "dark"
        
        await test_server.stop()
    
    @pytest.mark.asyncio
    async def test_ui_generation_flow(self, test_server):
        """测试UI生成流程"""
        await test_server.start()
        
        with TestClient(test_server.app) as client:
            # 生成UI
            ui_request = {
                "type": "dashboard",
                "user_preferences": {
                    "theme": "dark",
                    "layout": "grid"
                },
                "data": {
                    "widgets": ["chart", "table"]
                }
            }
            
            response = client.post("/api/ui/generate", json=ui_request)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
        
        await test_server.stop()


class TestWebSocketIntegration:
    """WebSocket集成测试类"""
    
    @pytest.fixture
    async def test_server_with_websocket(self):
        """创建支持WebSocket的测试服务器"""
        # 使用与上面相同的设置
        test_config = {
            'environment': 'test',
            'debug': True,
            'server': {
                'host': '127.0.0.1',
                'port': 8002
            },
            'intelligence': {
                'user_analyzer_enabled': True,
                'decision_engine_enabled': True,
                'ui_generator_enabled': True,
                'mcp_integration_enabled': False
            }
        }
        
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_file = f.name
        
        server = SmartUIMCPServer(config_file)
        await server.initialize()
        await server.start()
        
        yield server
        
        await server.stop()
        import os
        os.unlink(config_file)
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, test_server_with_websocket):
        """测试WebSocket连接"""
        with TestClient(test_server_with_websocket.app) as client:
            with client.websocket_connect("/ws") as websocket:
                # 发送测试消息
                test_message = {
                    "type": "user_interaction",
                    "data": {
                        "user_id": "test_user",
                        "type": "click",
                        "target": "button"
                    }
                }
                
                websocket.send_json(test_message)
                
                # 等待响应（如果有的话）
                # 注意：实际的WebSocket处理可能是异步的
                
                # 验证连接仍然活跃
                assert len(test_server_with_websocket.websocket_connections) > 0
    
    @pytest.mark.asyncio
    async def test_websocket_ui_request(self, test_server_with_websocket):
        """测试通过WebSocket的UI请求"""
        with TestClient(test_server_with_websocket.app) as client:
            with client.websocket_connect("/ws") as websocket:
                # 发送UI生成请求
                ui_request = {
                    "type": "ui_request",
                    "data": {
                        "type": "form",
                        "fields": ["name", "email"]
                    }
                }
                
                websocket.send_json(ui_request)
                
                # 接收响应
                response = websocket.receive_json()
                
                assert response["type"] == "ui_response"
                assert "data" in response


class TestComponentIntegration:
    """组件集成测试类"""
    
    @pytest.fixture
    async def integrated_components(self):
        """创建集成的组件系统"""
        # 创建模拟配置
        config = Mock()
        config.behavior_cache_ttl = 3600
        config.session_timeout = 1800
        config.max_behavior_history = 1000
        config.default_strategy = 'hybrid'
        config.confidence_threshold = 0.7
        config.max_decision_time = 5.0
        config.template_cache_size = 100
        config.component_cache_ttl = 1800
        config.max_generation_time = 10.0
        
        # 导入组件
        from src.core_intelligence import UserAnalyzer, DecisionEngine, UIGenerator, ApiStateManager
        
        # 创建组件实例
        user_analyzer = UserAnalyzer(config)
        decision_engine = DecisionEngine(config)
        ui_generator = UIGenerator(config)
        state_manager = ApiStateManager(config)
        
        # 启动组件
        await user_analyzer.start()
        await decision_engine.start()
        await ui_generator.start()
        await state_manager.start()
        
        components = {
            'user_analyzer': user_analyzer,
            'decision_engine': decision_engine,
            'ui_generator': ui_generator,
            'state_manager': state_manager
        }
        
        yield components
        
        # 清理
        for component in components.values():
            await component.stop()
    
    @pytest.mark.asyncio
    async def test_user_behavior_to_ui_adaptation(self, integrated_components):
        """测试从用户行为到UI适配的完整流程"""
        user_analyzer = integrated_components['user_analyzer']
        decision_engine = integrated_components['decision_engine']
        ui_generator = integrated_components['ui_generator']
        state_manager = integrated_components['state_manager']
        
        user_id = 'test_user'
        
        # 1. 记录用户行为（偏好暗色主题）
        theme_interactions = [
            {'user_id': user_id, 'type': 'theme_change', 'value': 'dark'},
            {'user_id': user_id, 'type': 'theme_change', 'value': 'dark'},
            {'user_id': user_id, 'type': 'theme_change', 'value': 'dark'},
        ]
        
        for interaction in theme_interactions:
            interaction['timestamp'] = '2024-01-01T12:00:00Z'
            await user_analyzer.record_interaction(interaction)
        
        # 2. 分析用户偏好
        preferences = await user_analyzer.learn_preferences(user_id)
        assert preferences['theme'] == 'dark'
        
        # 3. 基于偏好做决策
        context = {
            'user_id': user_id,
            'user_preferences': preferences,
            'current_theme': 'light'
        }
        
        decision = await decision_engine.make_decision('theme_adaptation', context)
        assert decision is not None
        
        # 4. 更新状态
        await state_manager.set_state(f'users.{user_id}.theme', 'dark')
        
        # 5. 生成适配的UI
        ui_request = {
            'type': 'dashboard',
            'user_preferences': preferences,
            'user_id': user_id
        }
        
        ui_config = await ui_generator.generate_ui(ui_request)
        assert ui_config is not None
        assert ui_config.get('theme') == 'dark'
    
    @pytest.mark.asyncio
    async def test_state_change_propagation(self, integrated_components):
        """测试状态变化传播"""
        state_manager = integrated_components['state_manager']
        
        # 设置状态绑定
        await state_manager.bind_states(
            'user.theme',
            'app.current_theme',
            bidirectional=True
        )
        
        # 更新用户主题
        await state_manager.set_state('user.theme', 'dark')
        
        # 验证应用主题也被更新
        app_theme = await state_manager.get_state('app.current_theme')
        assert app_theme == 'dark'
        
        # 反向更新
        await state_manager.set_state('app.current_theme', 'light')
        
        # 验证用户主题也被更新
        user_theme = await state_manager.get_state('user.theme')
        assert user_theme == 'light'


class TestPerformanceIntegration:
    """性能集成测试类"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求处理"""
        # 创建轻量级测试服务器
        test_config = {
            'environment': 'test',
            'server': {'host': '127.0.0.1', 'port': 8003},
            'intelligence': {
                'user_analyzer_enabled': True,
                'decision_engine_enabled': False,
                'ui_generator_enabled': False,
                'mcp_integration_enabled': False
            }
        }
        
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            config_file = f.name
        
        server = SmartUIMCPServer(config_file)
        await server.initialize()
        await server.start()
        
        try:
            # 并发发送多个请求
            async def send_request(client, i):
                interaction_data = {
                    "user_id": f"user_{i}",
                    "type": "click",
                    "target": "button",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
                response = await client.post("/api/user/interaction", json=interaction_data)
                return response.status_code
            
            async with httpx.AsyncClient(base_url="http://127.0.0.1:8003") as client:
                # 发送100个并发请求
                tasks = [send_request(client, i) for i in range(100)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 验证大部分请求成功
                success_count = sum(1 for result in results if result == 200)
                assert success_count >= 90  # 至少90%成功率
        
        finally:
            await server.stop()
            import os
            os.unlink(config_file)
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """测试内存使用情况"""
        import psutil
        import os
        
        # 获取初始内存使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 创建和销毁多个服务器实例
        for i in range(10):
            test_config = {
                'environment': 'test',
                'server': {'host': '127.0.0.1', 'port': 8004 + i},
                'intelligence': {
                    'user_analyzer_enabled': True,
                    'decision_engine_enabled': True,
                    'ui_generator_enabled': True,
                    'mcp_integration_enabled': False
                }
            }
            
            import tempfile
            import yaml
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(test_config, f)
                config_file = f.name
            
            server = SmartUIMCPServer(config_file)
            await server.initialize()
            await server.start()
            await server.stop()
            
            import os
            os.unlink(config_file)
        
        # 获取最终内存使用
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 验证内存增长在合理范围内（小于100MB）
        assert memory_increase < 100 * 1024 * 1024


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

