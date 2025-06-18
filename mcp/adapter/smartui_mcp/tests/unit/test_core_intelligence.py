"""
SmartUI MCP - 核心智能组件单元测试

测试用户分析器、决策引擎、状态管理器等核心智能组件。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any

from src.core_intelligence import (
    UserAnalyzer, DecisionEngine, ApiStateManager,
    UIGenerator, MCPIntegration
)
from src.common import EventBus, EventBusEventType


class TestUserAnalyzer:
    """用户分析器测试类"""
    
    @pytest.fixture
    def user_analyzer(self):
        """创建用户分析器实例"""
        config = Mock()
        config.behavior_cache_ttl = 3600
        config.session_timeout = 1800
        config.max_behavior_history = 1000
        return UserAnalyzer(config)
    
    @pytest.mark.asyncio
    async def test_record_interaction(self, user_analyzer):
        """测试记录用户交互"""
        await user_analyzer.start()
        
        interaction = {
            'user_id': 'test_user',
            'type': 'click',
            'target': 'button',
            'timestamp': datetime.now().isoformat(),
            'context': {'page': 'home'}
        }
        
        await user_analyzer.record_interaction(interaction)
        
        # 验证交互被记录
        user_profile = await user_analyzer.get_user_profile('test_user')
        assert user_profile is not None
        assert user_profile['user_id'] == 'test_user'
        assert len(user_profile['behavior_history']) > 0
        
        await user_analyzer.stop()
    
    @pytest.mark.asyncio
    async def test_behavior_pattern_analysis(self, user_analyzer):
        """测试行为模式分析"""
        await user_analyzer.start()
        
        user_id = 'test_user'
        
        # 模拟多次交互
        interactions = [
            {'user_id': user_id, 'type': 'click', 'target': 'menu'},
            {'user_id': user_id, 'type': 'scroll', 'target': 'page'},
            {'user_id': user_id, 'type': 'click', 'target': 'button'},
            {'user_id': user_id, 'type': 'input', 'target': 'search_box'},
        ]
        
        for interaction in interactions:
            interaction['timestamp'] = datetime.now().isoformat()
            await user_analyzer.record_interaction(interaction)
        
        # 分析行为模式
        patterns = await user_analyzer.analyze_behavior_patterns(user_id)
        
        assert patterns is not None
        assert 'interaction_frequency' in patterns
        assert 'preferred_actions' in patterns
        assert 'session_duration' in patterns
        
        await user_analyzer.stop()
    
    @pytest.mark.asyncio
    async def test_intent_detection(self, user_analyzer):
        """测试意图检测"""
        await user_analyzer.start()
        
        # 模拟搜索意图的交互序列
        search_interactions = [
            {'type': 'click', 'target': 'search_icon'},
            {'type': 'input', 'target': 'search_box', 'value': 'python tutorial'},
            {'type': 'click', 'target': 'search_button'}
        ]
        
        intent = await user_analyzer.detect_intent(search_interactions)
        
        assert intent is not None
        assert intent['type'] == 'search'
        assert intent['confidence'] > 0.5
        
        await user_analyzer.stop()
    
    @pytest.mark.asyncio
    async def test_preference_learning(self, user_analyzer):
        """测试偏好学习"""
        await user_analyzer.start()
        
        user_id = 'test_user'
        
        # 模拟用户偏好暗色主题
        theme_interactions = [
            {'user_id': user_id, 'type': 'theme_change', 'value': 'dark'},
            {'user_id': user_id, 'type': 'theme_change', 'value': 'dark'},
            {'user_id': user_id, 'type': 'theme_change', 'value': 'dark'},
        ]
        
        for interaction in theme_interactions:
            interaction['timestamp'] = datetime.now().isoformat()
            await user_analyzer.record_interaction(interaction)
        
        # 学习偏好
        preferences = await user_analyzer.learn_preferences(user_id)
        
        assert preferences is not None
        assert 'theme' in preferences
        assert preferences['theme'] == 'dark'
        
        await user_analyzer.stop()


class TestDecisionEngine:
    """决策引擎测试类"""
    
    @pytest.fixture
    def decision_engine(self):
        """创建决策引擎实例"""
        config = Mock()
        config.default_strategy = 'hybrid'
        config.confidence_threshold = 0.7
        config.max_decision_time = 5.0
        return DecisionEngine(config)
    
    @pytest.mark.asyncio
    async def test_make_decision(self, decision_engine):
        """测试决策制定"""
        await decision_engine.start()
        
        context = {
            'user_id': 'test_user',
            'current_theme': 'light',
            'user_preferences': {'theme': 'dark'},
            'device_type': 'desktop'
        }
        
        decision = await decision_engine.make_decision('theme_adaptation', context)
        
        assert decision is not None
        assert decision['type'] == 'theme_adaptation'
        assert decision['action'] is not None
        assert 'confidence' in decision
        assert decision['confidence'] >= 0.0
        
        await decision_engine.stop()
    
    @pytest.mark.asyncio
    async def test_rule_based_strategy(self, decision_engine):
        """测试基于规则的决策策略"""
        await decision_engine.start()
        
        # 添加规则
        rule = {
            'condition': 'user_preferences.theme == "dark"',
            'action': {'type': 'change_theme', 'value': 'dark'},
            'priority': 1
        }
        
        await decision_engine.add_rule('theme_adaptation', rule)
        
        context = {
            'user_preferences': {'theme': 'dark'}
        }
        
        decision = await decision_engine._apply_rule_strategy('theme_adaptation', context)
        
        assert decision is not None
        assert decision['action']['type'] == 'change_theme'
        assert decision['action']['value'] == 'dark'
        
        await decision_engine.stop()
    
    @pytest.mark.asyncio
    async def test_decision_execution(self, decision_engine):
        """测试决策执行"""
        await decision_engine.start()
        
        decision = {
            'type': 'ui_update',
            'action': {
                'type': 'update_component',
                'component_id': 'header',
                'properties': {'theme': 'dark'}
            },
            'confidence': 0.9
        }
        
        # 模拟执行器
        executor_called = False
        
        async def mock_executor(action):
            nonlocal executor_called
            executor_called = True
            return {'success': True}
        
        decision_engine.register_executor('update_component', mock_executor)
        
        result = await decision_engine.execute_decision(decision)
        
        assert result['success'] is True
        assert executor_called
        
        await decision_engine.stop()


class TestApiStateManager:
    """API状态管理器测试类"""
    
    @pytest.fixture
    def state_manager(self):
        """创建状态管理器实例"""
        config = Mock()
        return ApiStateManager(config)
    
    @pytest.mark.asyncio
    async def test_state_operations(self, state_manager):
        """测试状态操作"""
        await state_manager.start()
        
        # 设置状态
        await state_manager.set_state('user.profile.name', 'John Doe')
        await state_manager.set_state('user.profile.age', 30)
        await state_manager.set_state('app.theme', 'dark')
        
        # 获取状态
        name = await state_manager.get_state('user.profile.name')
        age = await state_manager.get_state('user.profile.age')
        theme = await state_manager.get_state('app.theme')
        
        assert name == 'John Doe'
        assert age == 30
        assert theme == 'dark'
        
        # 获取嵌套状态
        profile = await state_manager.get_state('user.profile')
        assert profile['name'] == 'John Doe'
        assert profile['age'] == 30
        
        await state_manager.stop()
    
    @pytest.mark.asyncio
    async def test_state_binding(self, state_manager):
        """测试状态绑定"""
        await state_manager.start()
        
        # 设置双向绑定
        await state_manager.bind_states('user.theme', 'app.current_theme', bidirectional=True)
        
        # 更新源状态
        await state_manager.set_state('user.theme', 'dark')
        
        # 验证目标状态也被更新
        current_theme = await state_manager.get_state('app.current_theme')
        assert current_theme == 'dark'
        
        # 反向更新
        await state_manager.set_state('app.current_theme', 'light')
        
        # 验证源状态也被更新
        user_theme = await state_manager.get_state('user.theme')
        assert user_theme == 'light'
        
        await state_manager.stop()
    
    @pytest.mark.asyncio
    async def test_computed_state(self, state_manager):
        """测试计算状态"""
        await state_manager.start()
        
        # 设置基础状态
        await state_manager.set_state('user.first_name', 'John')
        await state_manager.set_state('user.last_name', 'Doe')
        
        # 定义计算状态
        def compute_full_name(state_manager):
            first = state_manager.get_state_sync('user.first_name')
            last = state_manager.get_state_sync('user.last_name')
            return f"{first} {last}" if first and last else None
        
        await state_manager.add_computed_state(
            'user.full_name',
            compute_full_name,
            dependencies=['user.first_name', 'user.last_name']
        )
        
        # 获取计算状态
        full_name = await state_manager.get_state('user.full_name')
        assert full_name == 'John Doe'
        
        # 更新依赖状态
        await state_manager.set_state('user.first_name', 'Jane')
        
        # 验证计算状态自动更新
        updated_full_name = await state_manager.get_state('user.full_name')
        assert updated_full_name == 'Jane Doe'
        
        await state_manager.stop()
    
    @pytest.mark.asyncio
    async def test_state_persistence(self, state_manager):
        """测试状态持久化"""
        await state_manager.start()
        
        # 设置需要持久化的状态
        await state_manager.set_state('user.settings.theme', 'dark', persist=True)
        await state_manager.set_state('user.settings.language', 'en', persist=True)
        
        # 保存状态
        await state_manager.save_persistent_state()
        
        # 清除内存状态
        await state_manager.clear_state('user.settings')
        
        # 验证状态被清除
        theme = await state_manager.get_state('user.settings.theme')
        assert theme is None
        
        # 加载持久化状态
        await state_manager.load_persistent_state()
        
        # 验证状态被恢复
        restored_theme = await state_manager.get_state('user.settings.theme')
        restored_language = await state_manager.get_state('user.settings.language')
        
        assert restored_theme == 'dark'
        assert restored_language == 'en'
        
        await state_manager.stop()


class TestUIGenerator:
    """UI生成器测试类"""
    
    @pytest.fixture
    def ui_generator(self):
        """创建UI生成器实例"""
        config = Mock()
        config.template_cache_size = 100
        config.component_cache_ttl = 1800
        config.max_generation_time = 10.0
        return UIGenerator(config)
    
    @pytest.mark.asyncio
    async def test_generate_ui(self, ui_generator):
        """测试UI生成"""
        await ui_generator.start()
        
        request = {
            'type': 'dashboard',
            'user_preferences': {
                'theme': 'dark',
                'layout': 'grid'
            },
            'data': {
                'widgets': ['chart', 'table', 'summary']
            }
        }
        
        ui_config = await ui_generator.generate_ui(request)
        
        assert ui_config is not None
        assert 'components' in ui_config
        assert 'layout' in ui_config
        assert 'theme' in ui_config
        assert ui_config['theme'] == 'dark'
        
        await ui_generator.stop()
    
    @pytest.mark.asyncio
    async def test_template_based_generation(self, ui_generator):
        """测试基于模板的生成"""
        await ui_generator.start()
        
        # 注册模板
        template = {
            'name': 'simple_form',
            'components': [
                {'type': 'input', 'id': 'name', 'label': 'Name'},
                {'type': 'input', 'id': 'email', 'label': 'Email'},
                {'type': 'button', 'id': 'submit', 'text': 'Submit'}
            ]
        }
        
        await ui_generator.register_template('simple_form', template)
        
        # 使用模板生成UI
        request = {
            'template': 'simple_form',
            'data': {
                'title': 'User Registration'
            }
        }
        
        ui_config = await ui_generator.generate_ui(request)
        
        assert ui_config is not None
        assert len(ui_config['components']) == 3
        assert ui_config['components'][0]['type'] == 'input'
        assert ui_config['components'][2]['type'] == 'button'
        
        await ui_generator.stop()


class TestMCPIntegration:
    """MCP集成组件测试类"""
    
    @pytest.fixture
    def mcp_integration(self):
        """创建MCP集成组件实例"""
        config = Mock()
        config.endpoint = 'http://localhost:8080'
        config.service_id = 'smartui_mcp'
        return MCPIntegration(config)
    
    @pytest.mark.asyncio
    async def test_service_registration(self, mcp_integration):
        """测试服务注册"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'success': True})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await mcp_integration.start()
            
            # 验证注册请求被调用
            mock_post.assert_called()
            
            await mcp_integration.stop()
    
    @pytest.mark.asyncio
    async def test_service_call(self, mcp_integration):
        """测试服务调用"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'success': True,
                'result': {'data': 'test_result'}
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            await mcp_integration.start()
            
            result = await mcp_integration.call_service(
                'test_service',
                'test_method',
                {'param1': 'value1'}
            )
            
            assert result['success'] is True
            assert result['result']['data'] == 'test_result'
            
            await mcp_integration.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

