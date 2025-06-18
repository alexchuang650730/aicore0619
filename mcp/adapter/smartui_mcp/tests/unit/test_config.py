"""
SmartUI MCP - 配置管理器单元测试

测试配置管理系统的各项功能，包括配置加载、验证、合并等。
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import yaml

from src.config import (
    ConfigManager, SmartUIConfig, ServerConfig, 
    ConfigValidator, ConfigFormat, ConfigSource
)


class TestConfigManager:
    """配置管理器测试类"""
    
    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件"""
        config_data = {
            'environment': 'test',
            'debug': True,
            'server': {
                'host': '127.0.0.1',
                'port': 8080,
                'debug': True
            },
            'logging': {
                'level': 'DEBUG',
                'file_path': 'test.log'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # 清理
        os.unlink(temp_file)
    
    @pytest.fixture
    def config_manager(self, temp_config_file):
        """创建配置管理器实例"""
        return ConfigManager(temp_config_file)
    
    @pytest.mark.asyncio
    async def test_load_config_from_file(self, config_manager):
        """测试从文件加载配置"""
        config = await config_manager.load_config()
        
        assert isinstance(config, SmartUIConfig)
        assert config.environment == 'test'
        assert config.debug is True
        assert config.server.host == '127.0.0.1'
        assert config.server.port == 8080
    
    @pytest.mark.asyncio
    async def test_load_config_with_env_override(self, config_manager):
        """测试环境变量覆盖配置"""
        with patch.dict(os.environ, {
            'SMARTUI_SERVER_HOST': '0.0.0.0',
            'SMARTUI_SERVER_PORT': '9000',
            'SMARTUI_DEBUG': 'false'
        }):
            config = await config_manager.load_config()
            
            assert config.server.host == '0.0.0.0'
            assert config.server.port == 9000
            assert config.debug is False
    
    @pytest.mark.asyncio
    async def test_config_validation(self, config_manager):
        """测试配置验证"""
        # 测试有效配置
        config = await config_manager.load_config()
        is_valid, errors = await config_manager.validate_config(config)
        assert is_valid
        assert len(errors) == 0
        
        # 测试无效配置
        config.server.port = -1  # 无效端口
        is_valid, errors = await config_manager.validate_config(config)
        assert not is_valid
        assert len(errors) > 0
    
    @pytest.mark.asyncio
    async def test_config_merge(self, config_manager):
        """测试配置合并"""
        base_config = {
            'server': {'host': '127.0.0.1', 'port': 8000},
            'logging': {'level': 'INFO'}
        }
        
        override_config = {
            'server': {'port': 9000},
            'debug': True
        }
        
        merged = config_manager._merge_configs(base_config, override_config)
        
        assert merged['server']['host'] == '127.0.0.1'  # 保持原值
        assert merged['server']['port'] == 9000  # 被覆盖
        assert merged['logging']['level'] == 'INFO'  # 保持原值
        assert merged['debug'] is True  # 新增值
    
    @pytest.mark.asyncio
    async def test_file_watching(self, config_manager, temp_config_file):
        """测试文件监控"""
        callback_called = False
        
        def callback():
            nonlocal callback_called
            callback_called = True
        
        # 启动文件监控
        config_manager.start_file_watching(callback)
        
        # 等待监控启动
        await asyncio.sleep(0.1)
        
        # 修改配置文件
        with open(temp_config_file, 'a') as f:
            f.write('\n# test comment\n')
        
        # 等待文件变化检测
        await asyncio.sleep(0.5)
        
        # 停止监控
        config_manager.stop_file_watching()
        
        assert callback_called
    
    def test_config_format_detection(self, config_manager):
        """测试配置格式检测"""
        assert config_manager._detect_format('config.yaml') == ConfigFormat.YAML
        assert config_manager._detect_format('config.yml') == ConfigFormat.YAML
        assert config_manager._detect_format('config.json') == ConfigFormat.JSON
        assert config_manager._detect_format('config.toml') == ConfigFormat.TOML
        assert config_manager._detect_format('config.txt') == ConfigFormat.YAML  # 默认
    
    @pytest.mark.asyncio
    async def test_runtime_config_update(self, config_manager):
        """测试运行时配置更新"""
        # 加载初始配置
        config = await config_manager.load_config()
        initial_port = config.server.port
        
        # 更新运行时配置
        await config_manager.update_runtime_config('server.port', 9999)
        
        # 重新加载配置
        updated_config = await config_manager.load_config()
        
        assert updated_config.server.port == 9999
        assert updated_config.server.port != initial_port


class TestConfigValidator:
    """配置验证器测试类"""
    
    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        return ConfigValidator()
    
    @pytest.mark.asyncio
    async def test_server_config_validation(self, validator):
        """测试服务器配置验证"""
        # 有效配置
        valid_config = ServerConfig(
            host='127.0.0.1',
            port=8000,
            debug=False
        )
        
        is_valid, errors = await validator.validate_server_config(valid_config)
        assert is_valid
        assert len(errors) == 0
        
        # 无效端口
        invalid_config = ServerConfig(
            host='127.0.0.1',
            port=-1,
            debug=False
        )
        
        is_valid, errors = await validator.validate_server_config(invalid_config)
        assert not is_valid
        assert any('port' in error.lower() for error in errors)
    
    @pytest.mark.asyncio
    async def test_security_validation(self, validator):
        """测试安全配置验证"""
        # 测试弱密钥
        weak_key = "123456"
        is_valid, errors = await validator.validate_security_key(weak_key)
        assert not is_valid
        assert len(errors) > 0
        
        # 测试强密钥
        strong_key = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
        is_valid, errors = await validator.validate_security_key(strong_key)
        assert is_valid
        assert len(errors) == 0
    
    @pytest.mark.asyncio
    async def test_path_validation(self, validator):
        """测试路径验证"""
        # 测试有效路径
        valid_path = "/tmp/test.log"
        is_valid, errors = await validator.validate_file_path(valid_path)
        assert is_valid
        
        # 测试无效路径
        invalid_path = "/invalid/path/that/does/not/exist/test.log"
        is_valid, errors = await validator.validate_file_path(invalid_path)
        assert not is_valid
    
    @pytest.mark.asyncio
    async def test_url_validation(self, validator):
        """测试URL验证"""
        # 有效URL
        valid_urls = [
            "http://localhost:8080",
            "https://api.example.com",
            "http://127.0.0.1:3000/api"
        ]
        
        for url in valid_urls:
            is_valid, errors = await validator.validate_url(url)
            assert is_valid, f"URL {url} should be valid"
        
        # 无效URL
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol.com",
            "http://",
            ""
        ]
        
        for url in invalid_urls:
            is_valid, errors = await validator.validate_url(url)
            assert not is_valid, f"URL {url} should be invalid"


class TestSmartUIConfig:
    """SmartUI配置测试类"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = SmartUIConfig()
        
        # 检查默认值
        assert config.environment == 'development'
        assert config.debug is False
        assert isinstance(config.server, ServerConfig)
        assert config.server.host == '0.0.0.0'
        assert config.server.port == 8000
    
    def test_config_serialization(self):
        """测试配置序列化"""
        config = SmartUIConfig()
        
        # 转换为字典
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        assert 'server' in config_dict
        assert 'logging' in config_dict
        
        # 从字典创建
        new_config = SmartUIConfig.model_validate(config_dict)
        assert new_config.environment == config.environment
        assert new_config.server.port == config.server.port
    
    def test_config_update(self):
        """测试配置更新"""
        config = SmartUIConfig()
        original_port = config.server.port
        
        # 更新配置
        update_data = {'server': {'port': 9000}}
        updated_config = config.model_copy(update=update_data)
        
        assert updated_config.server.port == 9000
        assert updated_config.server.port != original_port
        assert updated_config.server.host == config.server.host  # 其他值保持不变


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

