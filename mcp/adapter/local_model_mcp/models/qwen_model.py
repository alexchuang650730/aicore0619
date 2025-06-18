"""
Qwen模型封装 - 支持本地Ollama和OpenRouter云端API的环境自适应
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
import aiohttp
import requests

logger = logging.getLogger(__name__)

class QwenModel:
    """Qwen 8B模型封装 - 环境自适应端云支持"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Qwen模型
        
        Args:
            config: 模型配置
        """
        self.config = config
        self.model_name = config.get("model_name", "qwen2.5:8b")
        self.provider = config.get("provider", "ollama")
        
        # 本地配置
        self.local_base_url = config.get("base_url", "http://localhost:11434")
        self.local_api_endpoint = config.get("api_endpoint", "/api/generate")
        self.local_chat_endpoint = config.get("chat_endpoint", "/api/chat")
        
        # 云端配置 (OpenRouter)
        self.cloud_base_url = config.get("cloud_base_url", "https://openrouter.ai/api/v1")
        self.cloud_api_key = config.get("cloud_api_key", "")
        self.cloud_model_name = config.get("cloud_model_name", "qwen/qwen-2.5-72b-instruct")
        
        # 运行时状态
        self.is_local_available = False
        self.current_mode = "local"  # "local" 或 "cloud"
        self.initialized = False
        
        # 性能配置
        self.max_tokens = config.get("max_tokens", 2048)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9)
        
        logger.info(f"QwenModel初始化 - 模型: {self.model_name}")
    
    async def initialize(self) -> bool:
        """
        初始化Qwen模型
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            logger.info("开始初始化Qwen模型...")
            
            # 1. 检查本地Ollama是否可用
            self.is_local_available = await self._check_local_ollama()
            
            if self.is_local_available:
                # 2. 确保模型已下载
                if await self._ensure_model_downloaded():
                    self.current_mode = "local"
                    logger.info("Qwen模型初始化成功 - 本地模式")
                else:
                    # 本地模型下载失败，切换到云端
                    if await self._check_cloud_available():
                        self.current_mode = "cloud"
                        logger.info("本地模型不可用，切换到云端模式")
                    else:
                        logger.error("本地和云端模式都不可用")
                        return False
            else:
                # 3. 检查云端API是否可用
                if await self._check_cloud_available():
                    self.current_mode = "cloud"
                    logger.info("Qwen模型初始化成功 - 云端模式")
                else:
                    logger.error("本地Ollama和云端API都不可用")
                    return False
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Qwen模型初始化失败: {e}")
            return False
    
    async def _check_local_ollama(self) -> bool:
        """检查本地Ollama是否可用"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.local_base_url}/api/tags", timeout=5) as response:
                    if response.status == 200:
                        logger.info("本地Ollama服务可用")
                        return True
        except Exception as e:
            logger.warning(f"本地Ollama不可用: {e}")
        
        return False
    
    async def _ensure_model_downloaded(self) -> bool:
        """确保模型已下载"""
        try:
            # 检查模型是否存在
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.local_base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        
                        if self.model_name in models:
                            logger.info(f"模型 {self.model_name} 已存在")
                            return True
                        else:
                            logger.info(f"模型 {self.model_name} 不存在，开始下载...")
                            return await self._download_model()
            
        except Exception as e:
            logger.error(f"检查模型失败: {e}")
            return False
    
    async def _download_model(self) -> bool:
        """下载模型"""
        try:
            logger.info(f"开始下载模型: {self.model_name}")
            
            async with aiohttp.ClientSession() as session:
                pull_data = {"name": self.model_name}
                async with session.post(
                    f"{self.local_base_url}/api/pull",
                    json=pull_data,
                    timeout=300  # 5分钟超时
                ) as response:
                    if response.status == 200:
                        # 读取流式响应
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode())
                                    if data.get("status") == "success":
                                        logger.info(f"模型 {self.model_name} 下载完成")
                                        return True
                                except json.JSONDecodeError:
                                    continue
            
            logger.error(f"模型 {self.model_name} 下载失败")
            return False
            
        except Exception as e:
            logger.error(f"下载模型失败: {e}")
            return False
    
    async def _check_cloud_available(self) -> bool:
        """检查云端API是否可用"""
        try:
            if not self.cloud_api_key:
                logger.warning("未配置OpenRouter API密钥")
                return False
            
            headers = {
                "Authorization": f"Bearer {self.cloud_api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.cloud_base_url}/models",
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        logger.info("OpenRouter云端API可用")
                        return True
                    else:
                        logger.warning(f"OpenRouter API响应错误: {response.status}")
                        return False
            
        except Exception as e:
            logger.warning(f"云端API检查失败: {e}")
            return False
    
    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 其他参数
            
        Returns:
            Dict: 生成结果
        """
        if not self.initialized:
            return {"success": False, "error": "模型未初始化"}
        
        if self.current_mode == "local":
            return await self._generate_local(prompt, **kwargs)
        else:
            return await self._generate_cloud(prompt, **kwargs)
    
    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        聊天完成
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            Dict: 响应结果
        """
        if not self.initialized:
            return {"success": False, "error": "模型未初始化"}
        
        if self.current_mode == "local":
            return await self._chat_completion_local(messages, **kwargs)
        else:
            return await self._chat_completion_cloud(messages, **kwargs)
    
    async def _generate_local(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """本地生成"""
        try:
            generate_data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.local_base_url}{self.local_api_endpoint}",
                    json=generate_data,
                    timeout=120
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "text": data.get("response", ""),
                            "mode": "local",
                            "model": self.model_name,
                            "tokens": len(data.get("response", "").split())
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"本地生成失败: {response.status} - {error_text}",
                            "mode": "local"
                        }
            
        except Exception as e:
            logger.error(f"本地生成失败: {e}")
            # 尝试切换到云端
            if await self._check_cloud_available():
                logger.info("本地生成失败，切换到云端模式")
                self.current_mode = "cloud"
                return await self._generate_cloud(prompt, **kwargs)
            else:
                return {"success": False, "error": str(e), "mode": "local"}
    
    async def _generate_cloud(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """云端生成"""
        try:
            headers = {
                "Authorization": f"Bearer {self.cloud_api_key}",
                "Content-Type": "application/json"
            }
            
            completion_data = {
                "model": self.cloud_model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cloud_base_url}/chat/completions",
                    headers=headers,
                    json=completion_data,
                    timeout=120
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        choice = data["choices"][0]
                        return {
                            "success": True,
                            "text": choice["message"]["content"],
                            "mode": "cloud",
                            "model": self.cloud_model_name,
                            "tokens": data.get("usage", {}).get("completion_tokens", 0)
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"云端生成失败: {response.status} - {error_text}",
                            "mode": "cloud"
                        }
            
        except Exception as e:
            logger.error(f"云端生成失败: {e}")
            return {"success": False, "error": str(e), "mode": "cloud"}
    
    async def _chat_completion_local(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """本地聊天完成"""
        try:
            chat_data = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.local_base_url}{self.local_chat_endpoint}",
                    json=chat_data,
                    timeout=120
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "message": data.get("message", {}),
                            "mode": "local",
                            "model": self.model_name
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"本地聊天失败: {response.status} - {error_text}",
                            "mode": "local"
                        }
            
        except Exception as e:
            logger.error(f"本地聊天失败: {e}")
            # 尝试切换到云端
            if await self._check_cloud_available():
                logger.info("本地聊天失败，切换到云端模式")
                self.current_mode = "cloud"
                return await self._chat_completion_cloud(messages, **kwargs)
            else:
                return {"success": False, "error": str(e), "mode": "local"}
    
    async def _chat_completion_cloud(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """云端聊天完成"""
        try:
            headers = {
                "Authorization": f"Bearer {self.cloud_api_key}",
                "Content-Type": "application/json"
            }
            
            completion_data = {
                "model": self.cloud_model_name,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", self.top_p)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cloud_base_url}/chat/completions",
                    headers=headers,
                    json=completion_data,
                    timeout=120
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        choice = data["choices"][0]
                        return {
                            "success": True,
                            "message": {
                                "role": "assistant",
                                "content": choice["message"]["content"]
                            },
                            "mode": "cloud",
                            "model": self.cloud_model_name,
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"云端聊天失败: {response.status} - {error_text}",
                            "mode": "cloud"
                        }
            
        except Exception as e:
            logger.error(f"云端聊天失败: {e}")
            return {"success": False, "error": str(e), "mode": "cloud"}
    
    async def get_status(self) -> Dict[str, Any]:
        """获取模型状态"""
        return {
            "model_name": self.model_name,
            "current_mode": self.current_mode,
            "local_available": self.is_local_available,
            "cloud_available": bool(self.cloud_api_key),
            "initialized": self.initialized,
            "provider": self.provider
        }
    
    async def switch_mode(self, mode: str) -> bool:
        """
        切换运行模式
        
        Args:
            mode: "local" 或 "cloud"
            
        Returns:
            bool: 切换是否成功
        """
        try:
            if mode == "local" and self.is_local_available:
                self.current_mode = "local"
                logger.info("切换到本地模式")
                return True
            elif mode == "cloud" and await self._check_cloud_available():
                self.current_mode = "cloud"
                logger.info("切换到云端模式")
                return True
            else:
                logger.warning(f"无法切换到 {mode} 模式")
                return False
                
        except Exception as e:
            logger.error(f"模式切换失败: {e}")
            return False
    
    async def shutdown(self):
        """关闭模型"""
        try:
            logger.info("关闭Qwen模型")
            self.initialized = False
            
        except Exception as e:
            logger.error(f"关闭Qwen模型失败: {e}")

