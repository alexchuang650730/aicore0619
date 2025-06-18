"""
模型管理器 - 统一管理多个本地模型
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from .qwen_model import QwenModel
from .mistral_model import MistralModel

logger = logging.getLogger(__name__)

class ModelManager:
    """模型管理器 - 统一管理多个本地模型"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化模型管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.models = {}
        self.active_models = set()
        self.model_configs = config.get("models", {})
        
        # 性能配置
        self.max_concurrent = config.get("performance", {}).get("max_concurrent_requests", 3)
        self.memory_limit = config.get("performance", {}).get("memory_limit_gb", 8)
        self.auto_unload = config.get("performance", {}).get("auto_unload_inactive", True)
        
        logger.info("模型管理器初始化完成")
    
    async def initialize(self) -> bool:
        """
        初始化模型管理器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("开始初始化模型管理器...")
            
            # 初始化支持的模型类
            self._register_model_classes()
            
            # 预检查模型配置
            await self._validate_model_configs()
            
            logger.info("模型管理器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"模型管理器初始化失败: {e}")
            return False
    
    def _register_model_classes(self):
        """注册模型类"""
        self.model_classes = {
            "qwen": QwenModel,
            "mistral": MistralModel
        }
        logger.info(f"已注册模型类: {list(self.model_classes.keys())}")
    
    async def _validate_model_configs(self):
        """验证模型配置"""
        for model_name, model_config in self.model_configs.items():
            if model_name in ["default_model", "auto_switch", "selection_strategy"]:
                continue
                
            if not model_config.get("enabled", False):
                logger.info(f"模型 {model_name} 已禁用")
                continue
            
            if model_name not in self.model_classes:
                logger.warning(f"不支持的模型类型: {model_name}")
                continue
            
            logger.info(f"模型配置验证通过: {model_name}")
    
    async def load_model(self, model_name: str) -> bool:
        """
        加载指定模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 检查模型是否已加载
            if model_name in self.active_models:
                logger.info(f"模型 {model_name} 已经加载")
                return True
            
            # 检查模型配置
            if model_name not in self.model_configs:
                logger.error(f"模型配置不存在: {model_name}")
                return False
            
            model_config = self.model_configs[model_name]
            if not model_config.get("enabled", False):
                logger.error(f"模型 {model_name} 已禁用")
                return False
            
            # 检查模型类是否支持
            if model_name not in self.model_classes:
                logger.error(f"不支持的模型类型: {model_name}")
                return False
            
            logger.info(f"开始加载模型: {model_name}")
            
            # 创建模型实例
            model_class = self.model_classes[model_name]
            model_instance = model_class(model_config)
            
            # 初始化模型
            if not await model_instance.initialize():
                logger.error(f"模型 {model_name} 初始化失败")
                return False
            
            # 保存模型实例
            self.models[model_name] = model_instance
            self.active_models.add(model_name)
            
            logger.info(f"模型 {model_name} 加载成功")
            return True
            
        except Exception as e:
            logger.error(f"加载模型 {model_name} 失败: {e}")
            return False
    
    async def unload_model(self, model_name: str) -> bool:
        """
        卸载指定模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 卸载是否成功
        """
        try:
            if model_name not in self.active_models:
                logger.info(f"模型 {model_name} 未加载")
                return True
            
            logger.info(f"开始卸载模型: {model_name}")
            
            # 获取模型实例
            model_instance = self.models.get(model_name)
            if model_instance:
                # 调用模型的清理方法
                if hasattr(model_instance, 'shutdown'):
                    await model_instance.shutdown()
            
            # 从管理器中移除
            self.models.pop(model_name, None)
            self.active_models.discard(model_name)
            
            logger.info(f"模型 {model_name} 卸载成功")
            return True
            
        except Exception as e:
            logger.error(f"卸载模型 {model_name} 失败: {e}")
            return False
    
    async def get_model_status(self) -> Dict[str, Any]:
        """
        获取所有模型状态
        
        Returns:
            Dict: 模型状态信息
        """
        try:
            status = {
                "active_models": list(self.active_models),
                "total_models": len(self.model_configs) - 3,  # 排除配置项
                "model_details": {}
            }
            
            for model_name in self.active_models:
                model_instance = self.models.get(model_name)
                if model_instance and hasattr(model_instance, 'get_status'):
                    status["model_details"][model_name] = await model_instance.get_status()
                else:
                    status["model_details"][model_name] = {"status": "loaded"}
            
            return status
            
        except Exception as e:
            logger.error(f"获取模型状态失败: {e}")
            return {"error": str(e)}
    
    async def auto_select_model(self, task_type: str) -> str:
        """
        根据任务类型自动选择模型
        
        Args:
            task_type: 任务类型
            
        Returns:
            str: 推荐的模型名称
        """
        try:
            # 获取任务类型到模型的映射
            task_model_mapping = {
                "conversation": "qwen",
                "general_text": "qwen", 
                "code_generation": "qwen",
                "document_analysis": "mistral",
                "complex_reasoning": "mistral",
                "ocr_processing": "mistral"
            }
            
            recommended_model = task_model_mapping.get(task_type, self.model_configs.get("default_model", "qwen"))
            
            # 检查推荐模型是否可用
            if recommended_model in self.model_configs and self.model_configs[recommended_model].get("enabled", False):
                return recommended_model
            
            # 如果推荐模型不可用，返回默认模型
            default_model = self.model_configs.get("default_model", "qwen")
            if default_model in self.model_configs and self.model_configs[default_model].get("enabled", False):
                return default_model
            
            # 如果默认模型也不可用，返回第一个可用模型
            for model_name, model_config in self.model_configs.items():
                if model_name not in ["default_model", "auto_switch", "selection_strategy"] and model_config.get("enabled", False):
                    return model_name
            
            logger.warning("没有可用的模型")
            return "qwen"  # 最后的备选
            
        except Exception as e:
            logger.error(f"自动选择模型失败: {e}")
            return self.model_configs.get("default_model", "qwen")
    
    async def chat_completion(self, messages: List[Dict[str, str]], model_name: str, **kwargs) -> Dict[str, Any]:
        """
        聊天完成
        
        Args:
            messages: 消息列表
            model_name: 模型名称
            **kwargs: 其他参数
            
        Returns:
            Dict: 响应结果
        """
        try:
            # 确保模型已加载
            if model_name not in self.active_models:
                if not await self.load_model(model_name):
                    raise Exception(f"模型 {model_name} 加载失败")
            
            # 获取模型实例
            model_instance = self.models[model_name]
            
            # 调用模型的聊天完成方法
            if hasattr(model_instance, 'chat_completion'):
                return await model_instance.chat_completion(messages, **kwargs)
            else:
                # 如果模型不支持聊天完成，转换为文本生成
                prompt = self._messages_to_prompt(messages)
                return await model_instance.generate(prompt, **kwargs)
            
        except Exception as e:
            logger.error(f"聊天完成失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def text_generation(self, prompt: str, model_name: str, **kwargs) -> Dict[str, Any]:
        """
        文本生成
        
        Args:
            prompt: 输入提示
            model_name: 模型名称
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果
        """
        try:
            # 确保模型已加载
            if model_name not in self.active_models:
                if not await self.load_model(model_name):
                    raise Exception(f"模型 {model_name} 加载失败")
            
            # 获取模型实例
            model_instance = self.models[model_name]
            
            # 调用模型的生成方法
            return await model_instance.generate(prompt, **kwargs)
            
        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """将消息列表转换为提示文本"""
        prompt_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n".join(prompt_parts) + "\nAssistant:"
    
    async def shutdown(self):
        """关闭模型管理器"""
        try:
            logger.info("开始关闭模型管理器...")
            
            # 卸载所有活跃模型
            for model_name in list(self.active_models):
                await self.unload_model(model_name)
            
            self.models.clear()
            self.active_models.clear()
            
            logger.info("模型管理器关闭完成")
            
        except Exception as e:
            logger.error(f"关闭模型管理器失败: {e}")

