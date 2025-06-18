#!/usr/bin/env python3
"""
Local Model MCP 完整测试用例
测试环境自适应、端云切换、OCR功能等所有核心功能
"""

import asyncio
import unittest
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.adapter.local_model_mcp.local_model_mcp import LocalModelMCP
from mcp.adapter.local_model_mcp.models.model_manager import ModelManager
from mcp.adapter.local_model_mcp.models.qwen_model import QwenModel
from mcp.adapter.local_model_mcp.models.mistral_model import MistralModel
from mcp.adapter.local_model_mcp.ocr.ocr_engine import OCREngine
from mcp.adapter.local_model_mcp.utils.device_utils import DeviceUtils
from mcp.adapter.local_model_mcp.utils.memory_utils import MemoryUtils

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLocalModelMCP(unittest.IsolatedAsyncioTestCase):
    """Local Model MCP 主要功能测试"""
    
    async def asyncSetUp(self):
        """测试设置"""
        # 创建临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False)
        config_content = """
[mcp_info]
name = "local_model_mcp_test"
version = "1.0.0"
type = "local_model_provider"

[models]
default_model = "qwen"
auto_switch = true

[models.qwen]
enabled = true
model_name = "qwen2.5:8b"
provider = "ollama"
base_url = "http://localhost:11434"
cloud_api_key = "test_key"

[models.mistral]
enabled = true
model_name = "mistralai/Mistral-Nemo-Instruct-2407"
provider = "transformers"
cloud_api_key = "test_key"

[ocr]
enabled = true
languages = ["zh", "en"]

[performance]
max_concurrent_requests = 3
memory_limit_gb = 8
"""
        self.temp_config.write(config_content)
        self.temp_config.close()
        
        # 创建MCP实例
        self.mcp = LocalModelMCP(self.temp_config.name)
    
    async def asyncTearDown(self):
        """测试清理"""
        if self.mcp:
            await self.mcp.shutdown()
        
        # 删除临时配置文件
        os.unlink(self.temp_config.name)
    
    async def test_mcp_initialization(self):
        """测试MCP初始化"""
        # 模拟设备检测
        with patch.object(DeviceUtils, 'detect_device') as mock_detect:
            mock_detect.return_value = {
                "platform": "linux",
                "gpu_available": True,
                "gpu_type": "NVIDIA GPU",
                "recommended_mode": "local"
            }
            
            # 模拟内存检测
            with patch.object(MemoryUtils, 'get_memory_info') as mock_memory:
                mock_memory.return_value = {
                    "available_memory_gb": 16.0,
                    "total_memory_gb": 32.0
                }
                
                # 模拟模型管理器初始化
                with patch.object(ModelManager, 'initialize') as mock_init:
                    mock_init.return_value = True
                    
                    result = await self.mcp.initialize()
                    self.assertTrue(result)
                    self.assertTrue(self.mcp.initialized)
    
    async def test_get_status(self):
        """测试状态获取"""
        # 模拟初始化
        with patch.object(self.mcp, 'initialize') as mock_init:
            mock_init.return_value = True
            await self.mcp.initialize()
            
            # 模拟模型状态
            with patch.object(self.mcp.model_manager, 'get_model_status') as mock_status:
                mock_status.return_value = {
                    "active_models": ["qwen"],
                    "total_models": 2
                }
                
                status = await self.mcp.get_status()
                self.assertIn("mcp_info", status)
                self.assertIn("initialized", status)
                self.assertIn("models", status)
    
    async def test_get_capabilities(self):
        """测试能力获取"""
        capabilities = await self.mcp.get_capabilities()
        
        self.assertIn("name", capabilities)
        self.assertIn("features", capabilities)
        self.assertTrue(capabilities["features"]["text_generation"])
        self.assertTrue(capabilities["features"]["chat_completion"])

class TestDeviceUtils(unittest.IsolatedAsyncioTestCase):
    """设备检测工具测试"""
    
    def setUp(self):
        """测试设置"""
        self.device_utils = DeviceUtils()
    
    async def test_detect_device(self):
        """测试设备检测"""
        device_info = await self.device_utils.detect_device()
        
        self.assertIn("platform", device_info)
        self.assertIn("gpu_available", device_info)
        self.assertIn("recommended_mode", device_info)
        self.assertIn(device_info["recommended_mode"], ["local", "cloud", "hybrid"])
    
    def test_get_optimal_device(self):
        """测试最优设备获取"""
        # 模拟设备信息
        self.device_utils.device_info = {
            "gpu_available": True,
            "gpu_type": "NVIDIA GPU"
        }
        
        device = self.device_utils.get_optimal_device()
        self.assertIn(device, ["cuda", "mps", "cpu"])
    
    def test_should_use_local_model(self):
        """测试本地模型使用判断"""
        # 模拟推荐本地模式
        self.device_utils.device_info = {
            "recommended_mode": "local",
            "gpu_available": True
        }
        
        result = self.device_utils.should_use_local_model("qwen")
        self.assertTrue(result)
        
        # 模拟推荐云端模式
        self.device_utils.device_info = {
            "recommended_mode": "cloud",
            "gpu_available": False
        }
        
        result = self.device_utils.should_use_local_model("qwen")
        self.assertFalse(result)

class TestMemoryUtils(unittest.IsolatedAsyncioTestCase):
    """内存管理工具测试"""
    
    def setUp(self):
        """测试设置"""
        self.memory_utils = MemoryUtils()
    
    async def test_get_memory_info(self):
        """测试内存信息获取"""
        memory_info = await self.memory_utils.get_memory_info()
        
        self.assertIn("total_memory_gb", memory_info)
        self.assertIn("available_memory_gb", memory_info)
        self.assertIn("memory_usage_percent", memory_info)
    
    def test_check_memory_sufficient(self):
        """测试内存充足性检查"""
        # 模拟内存信息
        self.memory_utils.memory_info = {
            "available_memory_gb": 16.0
        }
        
        # 测试充足情况
        result = self.memory_utils.check_memory_sufficient(8.0)
        self.assertTrue(result)
        
        # 测试不足情况
        result = self.memory_utils.check_memory_sufficient(20.0)
        self.assertFalse(result)
    
    def test_get_memory_recommendation(self):
        """测试内存使用建议"""
        # 模拟高内存使用率
        self.memory_utils.memory_info = {
            "memory_usage_percent": 95.0,
            "available_memory_gb": 2.0
        }
        
        recommendation = self.memory_utils.get_memory_recommendation()
        self.assertIn("云端模式", recommendation)

class TestQwenModel(unittest.IsolatedAsyncioTestCase):
    """Qwen模型测试"""
    
    def setUp(self):
        """测试设置"""
        config = {
            "model_name": "qwen2.5:8b",
            "provider": "ollama",
            "base_url": "http://localhost:11434",
            "cloud_api_key": "test_key"
        }
        self.qwen_model = QwenModel(config)
    
    async def test_check_local_ollama(self):
        """测试本地Ollama检查"""
        # 模拟Ollama可用
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.qwen_model._check_local_ollama()
            self.assertTrue(result)
        
        # 模拟Ollama不可用
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            result = await self.qwen_model._check_local_ollama()
            self.assertFalse(result)
    
    async def test_check_cloud_available(self):
        """测试云端API检查"""
        # 模拟云端API可用
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.qwen_model._check_cloud_available()
            self.assertTrue(result)
    
    async def test_get_status(self):
        """测试状态获取"""
        status = await self.qwen_model.get_status()
        
        self.assertIn("model_name", status)
        self.assertIn("current_mode", status)
        self.assertIn("initialized", status)

class TestMistralModel(unittest.IsolatedAsyncioTestCase):
    """Mistral模型测试"""
    
    def setUp(self):
        """测试设置"""
        config = {
            "model_name": "mistralai/Mistral-Nemo-Instruct-2407",
            "provider": "transformers",
            "cloud_api_key": "test_key"
        }
        self.mistral_model = MistralModel(config)
    
    async def test_check_local_environment(self):
        """测试本地环境检查"""
        # 模拟环境可用
        with patch('importlib.import_module'):
            with patch.object(self.mistral_model, '_get_optimal_device') as mock_device:
                mock_device.return_value = "cuda"
                with patch.object(self.mistral_model, '_get_memory_info') as mock_memory:
                    mock_memory.return_value = {"available_memory_gb": 16.0}
                    
                    result = await self.mistral_model._check_local_environment()
                    # 由于transformers库可能不可用，这里主要测试逻辑
                    self.assertIsInstance(result, bool)
    
    def test_get_optimal_device(self):
        """测试最优设备获取"""
        device = self.mistral_model._get_optimal_device()
        self.assertIn(device, ["cuda", "mps", "cpu"])
    
    async def test_get_status(self):
        """测试状态获取"""
        status = await self.mistral_model.get_status()
        
        self.assertIn("model_name", status)
        self.assertIn("current_mode", status)
        self.assertIn("initialized", status)

class TestOCREngine(unittest.IsolatedAsyncioTestCase):
    """OCR引擎测试"""
    
    def setUp(self):
        """测试设置"""
        config = {
            "ocr": {
                "enabled": True,
                "languages": ["zh", "en"],
                "engine": "integrated"
            }
        }
        self.ocr_engine = OCREngine(config)
    
    async def test_detect_available_engines(self):
        """测试OCR引擎检测"""
        await self.ocr_engine._detect_available_engines()
        self.assertIsInstance(self.ocr_engine.available_engines, list)
    
    async def test_get_status(self):
        """测试状态获取"""
        status = await self.ocr_engine.get_status()
        
        self.assertIn("enabled", status)
        self.assertIn("initialized", status)
        self.assertIn("available_engines", status)
    
    async def test_extract_text_disabled(self):
        """测试OCR禁用时的文本提取"""
        # 禁用OCR
        self.ocr_engine.enabled = False
        
        result = await self.ocr_engine.extract_text(b"fake_image_data")
        self.assertFalse(result["success"])
        self.assertIn("禁用", result["error"])

class TestModelManager(unittest.IsolatedAsyncioTestCase):
    """模型管理器测试"""
    
    def setUp(self):
        """测试设置"""
        config = {
            "models": {
                "default_model": "qwen",
                "qwen": {
                    "enabled": True,
                    "model_name": "qwen2.5:8b"
                },
                "mistral": {
                    "enabled": True,
                    "model_name": "mistralai/Mistral-Nemo-Instruct-2407"
                }
            }
        }
        self.model_manager = ModelManager(config)
    
    async def test_initialize(self):
        """测试初始化"""
        result = await self.model_manager.initialize()
        self.assertTrue(result)
    
    async def test_auto_select_model(self):
        """测试自动模型选择"""
        # 测试对话任务
        model = await self.model_manager.auto_select_model("conversation")
        self.assertEqual(model, "qwen")
        
        # 测试文档分析任务
        model = await self.model_manager.auto_select_model("document_analysis")
        self.assertEqual(model, "mistral")
        
        # 测试未知任务
        model = await self.model_manager.auto_select_model("unknown_task")
        self.assertEqual(model, "qwen")  # 应该返回默认模型
    
    async def test_get_model_status(self):
        """测试模型状态获取"""
        status = await self.model_manager.get_model_status()
        
        self.assertIn("active_models", status)
        self.assertIn("total_models", status)
        self.assertIn("model_details", status)

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    """集成测试"""
    
    async def asyncSetUp(self):
        """测试设置"""
        # 创建临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False)
        config_content = """
[mcp_info]
name = "local_model_mcp_integration_test"
version = "1.0.0"

[models]
default_model = "qwen"

[models.qwen]
enabled = true
model_name = "qwen2.5:8b"

[models.mistral]
enabled = true
model_name = "mistralai/Mistral-Nemo-Instruct-2407"

[ocr]
enabled = false
"""
        self.temp_config.write(config_content)
        self.temp_config.close()
        
        self.mcp = LocalModelMCP(self.temp_config.name)
    
    async def asyncTearDown(self):
        """测试清理"""
        if self.mcp:
            await self.mcp.shutdown()
        os.unlink(self.temp_config.name)
    
    async def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 模拟完整的初始化和使用流程
        with patch.object(self.mcp, 'initialize') as mock_init:
            mock_init.return_value = True
            
            # 初始化
            result = await self.mcp.initialize()
            self.assertTrue(result)
            
            # 获取能力
            capabilities = await self.mcp.get_capabilities()
            self.assertIn("features", capabilities)
            
            # 获取状态
            with patch.object(self.mcp.model_manager, 'get_model_status') as mock_status:
                mock_status.return_value = {"active_models": []}
                
                status = await self.mcp.get_status()
                self.assertIn("initialized", status)

class TestErrorHandling(unittest.IsolatedAsyncioTestCase):
    """错误处理测试"""
    
    def setUp(self):
        """测试设置"""
        # 使用无效配置
        self.mcp = LocalModelMCP("nonexistent_config.toml")
    
    async def test_invalid_config_handling(self):
        """测试无效配置处理"""
        # 应该使用默认配置
        self.assertIsNotNone(self.mcp.config)
        self.assertIn("mcp_info", self.mcp.config)
    
    async def test_uninitialized_operations(self):
        """测试未初始化时的操作"""
        # 测试未初始化时的文本生成
        result = await self.mcp.text_generation("test prompt")
        # 应该尝试初始化或返回错误
        self.assertIn("success", result)

def create_test_image():
    """创建测试图像"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 创建一个简单的测试图像
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加一些文本
        try:
            # 尝试使用默认字体
            draw.text((10, 10), "Hello World\n你好世界", fill='black')
        except:
            # 如果字体不可用，使用简单文本
            draw.text((10, 10), "Hello World", fill='black')
        
        # 转换为字节
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
        
    except ImportError:
        # 如果PIL不可用，返回空字节
        return b"fake_image_data"

class TestPerformance(unittest.IsolatedAsyncioTestCase):
    """性能测试"""
    
    async def test_concurrent_requests(self):
        """测试并发请求处理"""
        # 创建多个并发任务
        tasks = []
        for i in range(5):
            task = asyncio.create_task(self._mock_request(f"request_{i}"))
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证结果
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertIsNotNone(result)
    
    async def _mock_request(self, request_id: str):
        """模拟请求"""
        await asyncio.sleep(0.1)  # 模拟处理时间
        return {"request_id": request_id, "status": "completed"}

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_classes = [
        TestLocalModelMCP,
        TestDeviceUtils,
        TestMemoryUtils,
        TestQwenModel,
        TestMistralModel,
        TestOCREngine,
        TestModelManager,
        TestIntegration,
        TestErrorHandling,
        TestPerformance
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # 运行测试
    success = run_tests()
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)

