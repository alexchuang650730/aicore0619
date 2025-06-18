"""
统一的本地模型MCP适配器
支持Qwen 8B和Mistral 12B多模型配置，集成OCR功能
添加OCR工作流接口支持
"""

import os
import sys
import json
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import toml

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .models.model_manager import ModelManager
from .ocr.ocr_engine import OCREngine
from .utils.device_utils import DeviceUtils
from .utils.memory_utils import MemoryUtils
from .ocr_workflow_interface import OCRWorkflowInterface, OCRWorkflowRequest, OCRWorkflowResult

logger = logging.getLogger(__name__)

class LocalModelMCP:
    """统一的本地模型MCP适配器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化Local Model MCP
        
        Args:
            config_path: 配置文件路径，默认使用当前目录的config.toml
        """
        self.config_path = config_path or Path(__file__).parent / "config.toml"
        self.config = self._load_config()
        
        # 初始化组件
        self.model_manager = ModelManager(self.config)
        self.ocr_engine = OCREngine(self.config) if self.config.get("ocr", {}).get("enabled", False) else None
        self.device_utils = DeviceUtils()
        self.memory_utils = MemoryUtils()
        
        # 初始化Mistral OCR引擎（如果配置了）
        self.mistral_ocr_engine = None
        if self.config.get("mistral_ocr", {}).get("enabled", False):
            api_key = self.config.get("mistral_ocr", {}).get("api_key")
            if api_key:
                from .mistral_ocr_engine import MistralOCREngine
                self.mistral_ocr_engine = MistralOCREngine(api_key)
                logger.info("Mistral OCR引擎配置完成")
            else:
                logger.warning("Mistral OCR已启用但未配置API密钥")
        
        # 状态管理
        self.initialized = False
        self.current_model = None
        self.start_time = time.time()
        
        # 性能统计
        self.stats = {
            "requests_processed": 0,
            "total_tokens_generated": 0,
            "average_response_time": 0,
            "model_switches": 0,
            "ocr_requests": 0,
            "workflow_requests": 0
        }
        
        # 初始化OCR工作流接口
        self.ocr_workflow = None  # 延迟初始化
        
        logger.info(f"LocalModelMCP初始化完成 - 版本: {self.config['mcp_info']['version']}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            
            logger.info(f"配置文件加载成功: {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"配置文件加载失败: {e}")
            # 返回默认配置
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "mcp_info": {
                "name": "local_model_mcp",
                "version": "1.0.0",
                "type": "local_model_provider"
            },
            "models": {
                "default_model": "qwen",
                "auto_switch": True,
                "qwen": {
                    "enabled": True,
                    "model_name": "qwen2.5:8b",
                    "provider": "ollama",
                    "base_url": "http://localhost:11434"
                },
                "mistral": {
                    "enabled": True,
                    "model_name": "mistralai/Mistral-Nemo-Instruct-2407",
                    "provider": "transformers"
                }
            },
            "ocr": {
                "enabled": False
            },
            "mistral_ocr": {
                "enabled": False,
                "api_key": "",
                "model_name": "mistralai/pixtral-12b"
            },
            "performance": {
                "max_concurrent_requests": 3,
                "memory_limit_gb": 8
            }
        }
    
    async def initialize(self) -> bool:
        """
        初始化所有组件
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("开始初始化LocalModelMCP...")
            
            # 1. 检测设备环境
            device_info = await self.device_utils.detect_device()
            logger.info(f"设备信息: {device_info}")
            
            # 2. 检查内存状况
            memory_info = await self.memory_utils.get_memory_info()
            logger.info(f"内存信息: {memory_info}")
            
            # 3. 初始化模型管理器
            if not await self.model_manager.initialize():
                logger.error("模型管理器初始化失败")
                return False
            
            # 4. 初始化OCR引擎（如果启用）
            if self.ocr_engine:
                if not await self.ocr_engine.initialize():
                    logger.warning("OCR引擎初始化失败，OCR功能将不可用")
                    self.ocr_engine = None
            
            # 5. 加载默认模型
            default_model = self.config["models"]["default_model"]
            if not await self.model_manager.load_model(default_model):
                logger.warning(f"默认模型 {default_model} 加载失败")
            else:
                self.current_model = default_model
                logger.info(f"默认模型 {default_model} 加载成功")
            
            # 5. 初始化OCR工作流接口
            self.ocr_workflow = OCRWorkflowInterface(self)
            logger.info("OCR工作流接口初始化完成")
            
            self.initialized = True
            logger.info("LocalModelMCP初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"LocalModelMCP初始化失败: {e}")
            return False
    
    async def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表
            model: 指定模型名称，None则使用当前模型
            **kwargs: 其他参数
            
        Returns:
            Dict: 响应结果
        """
        start_time = time.time()
        
        try:
            if not self.initialized:
                await self.initialize()
            
            # 选择模型
            target_model = model or self.current_model or self.config["models"]["default_model"]
            
            # 自动切换模型（如果需要）
            if target_model != self.current_model:
                if not await self._switch_model(target_model):
                    return {
                        "success": False,
                        "error": f"模型切换失败: {target_model}",
                        "model": self.current_model
                    }
            
            # 调用模型生成
            result = await self.model_manager.chat_completion(messages, target_model, **kwargs)
            
            # 更新统计
            self._update_stats(start_time, result)
            
            return {
                "success": True,
                "model": target_model,
                "response": result,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"聊天完成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.current_model,
                "processing_time": time.time() - start_time
            }
    
    async def text_generation(self, prompt: str, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        文本生成接口
        
        Args:
            prompt: 输入提示
            model: 指定模型名称
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果
        """
        start_time = time.time()
        
        try:
            if not self.initialized:
                await self.initialize()
            
            # 选择模型
            target_model = model or self.current_model or self.config["models"]["default_model"]
            
            # 自动切换模型（如果需要）
            if target_model != self.current_model:
                if not await self._switch_model(target_model):
                    return {
                        "success": False,
                        "error": f"模型切换失败: {target_model}",
                        "model": self.current_model
                    }
            
            # 调用模型生成
            result = await self.model_manager.text_generation(prompt, target_model, **kwargs)
            
            # 更新统计
            self._update_stats(start_time, result)
            
            return {
                "success": True,
                "model": target_model,
                "response": result,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": self.current_model,
                "processing_time": time.time() - start_time
            }
    
    async def ocr_processing(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        OCR处理接口
        
        Args:
            image_data: 图像数据
            **kwargs: 其他参数
            
        Returns:
            Dict: OCR结果
        """
        start_time = time.time()
        
        try:
            if not self.ocr_engine:
                return {
                    "success": False,
                    "error": "OCR功能未启用",
                    "processing_time": time.time() - start_time
                }
            
            # 调用OCR引擎
            result = await self.ocr_engine.extract_text(image_data, **kwargs)
            
            # 更新统计
            self.stats["ocr_requests"] += 1
            
            return {
                "success": True,
                "result": result,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"OCR处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _switch_model(self, model_name: str) -> bool:
        """
        切换模型
        
        Args:
            model_name: 目标模型名称
            
        Returns:
            bool: 切换是否成功
        """
        try:
            if not await self.model_manager.load_model(model_name):
                return False
            
            # 卸载当前模型（如果配置了自动卸载）
            if (self.current_model and 
                self.current_model != model_name and 
                self.config.get("performance", {}).get("auto_unload_inactive", False)):
                await self.model_manager.unload_model(self.current_model)
            
            self.current_model = model_name
            self.stats["model_switches"] += 1
            
            logger.info(f"模型切换成功: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"模型切换失败: {e}")
            return False
    
    def _update_stats(self, start_time: float, result: Dict[str, Any]):
        """更新性能统计"""
        processing_time = time.time() - start_time
        
        self.stats["requests_processed"] += 1
        
        # 更新平均响应时间
        current_avg = self.stats["average_response_time"]
        request_count = self.stats["requests_processed"]
        self.stats["average_response_time"] = (current_avg * (request_count - 1) + processing_time) / request_count
        
        # 更新token统计（如果有）
        if isinstance(result, dict) and "tokens" in result:
            self.stats["total_tokens_generated"] += result.get("tokens", 0)
    
    async def process_ocr_workflow(self, request: Union[Dict[str, Any], OCRWorkflowRequest]) -> OCRWorkflowResult:
        """
        处理OCR工作流请求 - 新的workflow兼容接口
        
        Args:
            request: OCR工作流请求
            
        Returns:
            OCRWorkflowResult: 处理结果
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            if not self.ocr_workflow:
                return OCRWorkflowResult(
                    success=False,
                    text="",
                    confidence=0.0,
                    processing_time=0.0,
                    adapter_used="none",
                    quality_score=0.0,
                    error="OCR工作流接口未初始化"
                )
            
            # 更新统计
            self.stats["workflow_requests"] += 1
            
            # 调用OCR工作流接口
            result = await self.ocr_workflow.process_ocr_workflow(request)
            
            logger.info(f"OCR工作流处理完成: 成功={result.success}, 质量={result.quality_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"OCR工作流处理失败: {e}")
            return OCRWorkflowResult(
                success=False,
                text="",
                confidence=0.0,
                processing_time=0.0,
                adapter_used="none",
                quality_score=0.0,
                error=str(e)
            )
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取MCP状态
        
        Returns:
            Dict: 状态信息
        """
        try:
            model_status = await self.model_manager.get_model_status()
            memory_info = await self.memory_utils.get_memory_info()
            
            return {
                "mcp_info": self.config["mcp_info"],
                "initialized": self.initialized,
                "current_model": self.current_model,
                "uptime": time.time() - self.start_time,
                "models": model_status,
                "ocr_enabled": self.ocr_engine is not None,
                "memory": memory_info,
                "statistics": self.stats
            }
            
        except Exception as e:
            logger.error(f"获取状态失败: {e}")
            return {
                "error": str(e),
                "initialized": self.initialized
            }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        获取MCP能力信息
        
        Returns:
            Dict: 能力信息
        """
        return {
            "name": self.config["mcp_info"]["name"],
            "version": self.config["mcp_info"]["version"],
            "type": self.config["mcp_info"]["type"],
            "capabilities": self.config.get("capabilities", {}),
            "supported_models": list(self.config["models"].keys()),
            "features": {
                "text_generation": True,
                "chat_completion": True,
                "ocr_processing": self.ocr_engine is not None,
                "model_switching": True,
                "batch_processing": False  # 待实现
            }
        }
    
    async def shutdown(self):
        """关闭MCP"""
        try:
            logger.info("开始关闭LocalModelMCP...")
            
            # 卸载所有模型
            if self.model_manager:
                await self.model_manager.shutdown()
            
            # 关闭OCR引擎
            if self.ocr_engine:
                await self.ocr_engine.shutdown()
            
            self.initialized = False
            logger.info("LocalModelMCP关闭完成")
            
        except Exception as e:
            logger.error(f"关闭MCP失败: {e}")

# 用于命令行和测试的便捷函数
async def create_local_model_mcp(config_path: Optional[str] = None) -> LocalModelMCP:
    """
    创建并初始化LocalModelMCP实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        LocalModelMCP: 初始化后的实例
    """
    mcp = LocalModelMCP(config_path)
    await mcp.initialize()
    return mcp

if __name__ == "__main__":
    # 简单的测试运行
    async def main():
        mcp = await create_local_model_mcp()
        
        # 测试文本生成
        result = await mcp.text_generation("你好，请介绍一下你自己。")
        print(f"文本生成结果: {result}")
        
        # 获取状态
        status = await mcp.get_status()
        print(f"MCP状态: {status}")
        
        await mcp.shutdown()
    
    asyncio.run(main())

