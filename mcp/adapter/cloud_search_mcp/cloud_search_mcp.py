#!/usr/bin/env python3
"""
Cloud Search MCP - 统一的云端视觉搜索MCP

基于PowerAutomation架构，参考Gemini MCP和Claude MCP实现，
提供统一的云端视觉模型接口，支持多模型配置化选择。

作者: PowerAutomation团队
版本: 1.0.0
日期: 2025-06-15
"""

import os
import sys
import json
import asyncio
import logging
import time
import base64
import hashlib
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import toml

# 添加项目路径
sys.path.append('/home/ubuntu/projects/communitypowerautomation')

# 导入基础MCP
try:
    from mcptool.adapters.base_mcp import BaseMCP
except ImportError:
    class BaseMCP:
        def __init__(self, name: str = "BaseMCP"):
            self.name = name
            self.logger = logging.getLogger(f"MCP.{name}")
        
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            raise NotImplementedError("子类必须实现此方法")

# 导入标准化日志系统
try:
    from standardized_logging_system import log_info, log_error, log_warning, LogCategory, performance_monitor
except ImportError:
    def log_info(category, message, data=None): pass
    def log_error(category, message, data=None): pass
    def log_warning(category, message, data=None): pass
    def performance_monitor(name):
        def decorator(func): return func
        return decorator
    class LogCategory:
        SYSTEM = "system"
        MCP = "mcp"

logger = logging.getLogger("cloud_search_mcp")

class CloudModel(Enum):
    """支持的云端模型"""
    GEMINI_FLASH = "google/gemini-2.5-flash-preview"
    GEMINI_PRO = "google/gemini-2.5-pro-preview"
    CLAUDE_SONNET = "anthropic/claude-3.7-sonnet"
    CLAUDE_OPUS = "anthropic/claude-opus-4"
    PIXTRAL_12B = "mistralai/pixtral-12b"
    PIXTRAL_LARGE = "mistralai/pixtral-large-2411"

class TaskType(Enum):
    """OCR任务类型"""
    DOCUMENT_OCR = "document_ocr"
    HANDWRITING_OCR = "handwriting_ocr"
    TABLE_EXTRACTION = "table_extraction"
    FORM_PROCESSING = "form_processing"
    MULTILINGUAL_OCR = "multilingual_ocr"
    STRUCTURED_DATA = "structured_data"

@dataclass
class ModelConfig:
    """模型配置"""
    model_id: str
    api_key: str
    base_url: str
    max_tokens: int
    temperature: float
    timeout: int
    cost_per_1k_tokens: float
    quality_score: float
    speed_score: float
    enabled: bool = True

@dataclass
class OCRRequest:
    """OCR请求"""
    image_data: bytes
    task_type: TaskType
    language: str = "auto"
    output_format: str = "markdown"
    quality_level: str = "high"
    metadata: Dict[str, Any] = None

@dataclass
class OCRResponse:
    """OCR响应"""
    success: bool
    content: str
    confidence: float
    model_used: str
    processing_time: float
    cost: float
    metadata: Dict[str, Any] = None
    error: str = None

class ModelSelector:
    """智能模型选择器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_capabilities = self._build_capabilities_matrix()
    
    def _build_capabilities_matrix(self) -> Dict[CloudModel, Dict[str, float]]:
        """构建模型能力矩阵"""
        capabilities = {}
        
        for model in CloudModel:
            model_key = model.value.replace("/", "_").replace("-", "_").replace(".", "_")
            model_config = self.config.get("models", {}).get(model_key, {})
            
            if model_config.get("enabled", False):
                capabilities[model] = {
                    "speed": model_config.get("speed_score", 0.5),
                    "cost": 1.0 - model_config.get("cost_per_1k_tokens", 0.001) * 1000,  # 成本越低分数越高
                    "quality": model_config.get("quality_score", 0.5),
                    "multilingual": self._get_multilingual_score(model),
                    "handwriting": self._get_handwriting_score(model),
                    "tables": self._get_table_score(model)
                }
        
        return capabilities
    
    def _get_multilingual_score(self, model: CloudModel) -> float:
        """获取多语言支持分数"""
        scores = {
            CloudModel.GEMINI_FLASH: 0.90,
            CloudModel.GEMINI_PRO: 0.95,
            CloudModel.CLAUDE_SONNET: 0.95,
            CloudModel.CLAUDE_OPUS: 0.98,
            CloudModel.PIXTRAL_12B: 0.85,
            CloudModel.PIXTRAL_LARGE: 0.90
        }
        return scores.get(model, 0.5)
    
    def _get_handwriting_score(self, model: CloudModel) -> float:
        """获取手写识别分数"""
        scores = {
            CloudModel.GEMINI_FLASH: 0.80,
            CloudModel.GEMINI_PRO: 0.85,
            CloudModel.CLAUDE_SONNET: 0.90,
            CloudModel.CLAUDE_OPUS: 0.95,
            CloudModel.PIXTRAL_12B: 0.85,
            CloudModel.PIXTRAL_LARGE: 0.88
        }
        return scores.get(model, 0.5)
    
    def _get_table_score(self, model: CloudModel) -> float:
        """获取表格处理分数"""
        scores = {
            CloudModel.GEMINI_FLASH: 0.85,
            CloudModel.GEMINI_PRO: 0.90,
            CloudModel.CLAUDE_SONNET: 0.92,
            CloudModel.CLAUDE_OPUS: 0.95,
            CloudModel.PIXTRAL_12B: 0.88,
            CloudModel.PIXTRAL_LARGE: 0.90
        }
        return scores.get(model, 0.5)
    
    def select_optimal_model(self, 
                           task_type: TaskType, 
                           priority: str = "balanced") -> Optional[CloudModel]:
        """
        选择最优模型
        
        Args:
            task_type: 任务类型
            priority: 优先级 ("speed", "cost", "quality", "balanced")
        
        Returns:
            最优的云端模型
        """
        
        # 基于任务类型的权重
        task_weights = {
            TaskType.DOCUMENT_OCR: {"quality": 0.4, "speed": 0.3, "cost": 0.3},
            TaskType.HANDWRITING_OCR: {"quality": 0.6, "handwriting": 0.3, "cost": 0.1},
            TaskType.TABLE_EXTRACTION: {"quality": 0.4, "tables": 0.4, "speed": 0.2},
            TaskType.FORM_PROCESSING: {"quality": 0.4, "speed": 0.4, "cost": 0.2},
            TaskType.MULTILINGUAL_OCR: {"quality": 0.4, "multilingual": 0.4, "cost": 0.2},
            TaskType.STRUCTURED_DATA: {"quality": 0.5, "tables": 0.3, "speed": 0.2}
        }
        
        # 基于优先级的权重调整
        priority_adjustments = {
            "speed": {"speed": 1.5, "quality": 0.8, "cost": 0.8},
            "cost": {"cost": 1.5, "quality": 0.8, "speed": 0.8},
            "quality": {"quality": 1.5, "speed": 0.8, "cost": 0.8},
            "balanced": {"speed": 1.0, "quality": 1.0, "cost": 1.0}
        }
        
        weights = task_weights.get(task_type, task_weights[TaskType.DOCUMENT_OCR])
        adjustments = priority_adjustments.get(priority, priority_adjustments["balanced"])
        
        # 计算每个模型的综合得分
        best_model = None
        best_score = 0
        
        for model, capabilities in self.model_capabilities.items():
            score = 0
            for factor, weight in weights.items():
                adjusted_weight = weight * adjustments.get(factor, 1.0)
                score += capabilities.get(factor, 0.5) * adjusted_weight
            
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model

class CloudModelClient:
    """云端模型客户端"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def process_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """处理图像OCR请求"""
        
        # 编码图像
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://powerautomation.ai",
            "X-Title": "PowerAutomation Cloud Search MCP"
        }
        
        request_data = {
            "model": self.config.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # 估算成本
                    input_tokens = len(prompt) // 4  # 粗略估算
                    output_tokens = len(content) // 4
                    cost = (input_tokens + output_tokens) / 1000 * self.config.cost_per_1k_tokens
                    
                    return {
                        "success": True,
                        "content": content,
                        "processing_time": processing_time,
                        "cost": cost,
                        "model": self.config.model_id
                    }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"API错误 {response.status}: {error_text}",
                        "processing_time": processing_time,
                        "cost": 0.0,
                        "model": self.config.model_id
                    }
                    
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "success": False,
                "error": f"请求异常: {str(e)}",
                "processing_time": processing_time,
                "cost": 0.0,
                "model": self.config.model_id
            }

class CloudSearchMCP(BaseMCP):
    """
    云端搜索MCP主类
    
    提供统一的云端视觉模型接口，支持多模型配置化选择，
    实现智能路由和OCR任务处理。
    """
    
    def __init__(self, config_path: str = None):
        """初始化Cloud Search MCP"""
        super().__init__("CloudSearchMCP")
        
        # 加载配置
        if config_path is None:
            config_path = Path(__file__).parent / "config.toml"
        
        self.config = self._load_config(config_path)
        self.model_selector = ModelSelector(self.config)
        self.model_configs = self._load_model_configs()
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "model_usage": {},
            "average_processing_time": 0.0
        }
        
        # MCP操作映射
        self.operations = {
            "process_ocr": self.process_ocr_request,
            "get_capabilities": self.get_capabilities,
            "get_supported_models": self.get_supported_models,
            "get_statistics": self.get_statistics,
            "health_check": self.health_check
        }
        
        log_info(LogCategory.MCP, "Cloud Search MCP初始化完成", {
            "config_path": str(config_path),
            "enabled_models": list(self.model_configs.keys()),
            "operations": list(self.operations.keys())
        })
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            
            # 处理环境变量
            self._resolve_env_variables(config)
            
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()
    
    def _resolve_env_variables(self, config: Dict[str, Any]):
        """解析环境变量"""
        def resolve_value(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.environ.get(env_var, "")
            elif isinstance(value, dict):
                for k, v in value.items():
                    value[k] = resolve_value(v)
            return value
        
        for key, value in config.items():
            config[key] = resolve_value(value)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "cloud_search_mcp": {
                "name": "CloudSearchMCP",
                "version": "1.0.0",
                "default_model": "gemini_flash",
                "priority": "balanced"
            },
            "models": {},
            "ocr_settings": {
                "default_language": "auto",
                "output_format": "markdown",
                "quality_level": "high"
            },
            "routing": {
                "enable_smart_routing": True,
                "quality_threshold": 0.8,
                "max_retries": 3,
                "fallback_enabled": True
            }
        }
    
    def _load_model_configs(self) -> Dict[str, ModelConfig]:
        """加载模型配置"""
        model_configs = {}
        models_config = self.config.get("models", {})
        
        for model_key, model_data in models_config.items():
            if model_data.get("enabled", False) and model_data.get("api_key"):
                try:
                    config = ModelConfig(
                        model_id=model_data["model_id"],
                        api_key=model_data["api_key"],
                        base_url=model_data["base_url"],
                        max_tokens=model_data["max_tokens"],
                        temperature=model_data["temperature"],
                        timeout=model_data["timeout"],
                        cost_per_1k_tokens=model_data["cost_per_1k_tokens"],
                        quality_score=model_data["quality_score"],
                        speed_score=model_data["speed_score"],
                        enabled=True
                    )
                    model_configs[model_key] = config
                except KeyError as e:
                    logger.warning(f"模型配置不完整 {model_key}: 缺少 {e}")
        
        return model_configs
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP标准处理接口"""
        try:
            operation = input_data.get("operation", "process_ocr")
            params = input_data.get("params", {})
            
            if operation not in self.operations:
                return {
                    "status": "error",
                    "message": f"不支持的操作: {operation}",
                    "available_operations": list(self.operations.keys())
                }
            
            # 执行对应操作
            if asyncio.iscoroutinefunction(self.operations[operation]):
                # 异步操作
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.operations[operation](**params))
            else:
                # 同步操作
                result = self.operations[operation](**params)
            
            log_info(LogCategory.MCP, f"Cloud Search MCP操作完成: {operation}", {
                "operation": operation,
                "status": result.get("status", "unknown")
            })
            
            return result
            
        except Exception as e:
            log_error(LogCategory.MCP, "Cloud Search MCP处理失败", {
                "operation": input_data.get("operation"),
                "error": str(e)
            })
            return {
                "status": "error",
                "message": f"处理失败: {str(e)}"
            }
    
    @performance_monitor("process_ocr_request")
    async def process_ocr_request(self, **kwargs) -> Dict[str, Any]:
        """处理OCR请求"""
        try:
            # 从kwargs构建请求
            image_data = kwargs.get("image_data")
            task_type_str = kwargs.get("task_type", "document_ocr")
            language = kwargs.get("language", "auto")
            output_format = kwargs.get("output_format", "markdown")
            
            if not image_data:
                return {
                    "status": "error",
                    "message": "缺少图像数据"
                }
            
            # 如果image_data是base64字符串，解码为bytes
            if isinstance(image_data, str):
                try:
                    image_data = base64.b64decode(image_data)
                except Exception as e:
                    return {
                        "status": "error",
                        "message": f"图像数据解码失败: {e}"
                    }
            
            # 构建请求对象
            try:
                task_type = TaskType(task_type_str)
            except ValueError:
                task_type = TaskType.DOCUMENT_OCR
            
            request = OCRRequest(
                image_data=image_data,
                task_type=task_type,
                language=language,
                output_format=output_format
            )
            
            # 更新统计
            self.stats["total_requests"] += 1
            
            # 选择最优模型
            priority = self.config.get("cloud_search_mcp", {}).get("priority", "balanced")
            optimal_model = self.model_selector.select_optimal_model(task_type, priority)
            
            if not optimal_model:
                self.stats["failed_requests"] += 1
                return {
                    "status": "error",
                    "message": "没有可用的模型"
                }
            
            # 执行OCR处理
            response = await self._execute_ocr(optimal_model, request)
            
            # 验证结果质量
            quality_threshold = self.config.get("routing", {}).get("quality_threshold", 0.8)
            if (response.success and 
                response.confidence < quality_threshold and 
                self.config.get("routing", {}).get("fallback_enabled", True)):
                
                # 尝试备用模型
                fallback_response = await self._try_fallback_models(request, optimal_model)
                if fallback_response.success and fallback_response.confidence > response.confidence:
                    response = fallback_response
            
            # 更新统计
            if response.success:
                self.stats["successful_requests"] += 1
                self.stats["total_cost"] += response.cost
                
                model_name = response.model_used
                if model_name not in self.stats["model_usage"]:
                    self.stats["model_usage"][model_name] = 0
                self.stats["model_usage"][model_name] += 1
                
                # 更新平均处理时间
                total_time = (self.stats["average_processing_time"] * 
                             (self.stats["successful_requests"] - 1) + 
                             response.processing_time)
                self.stats["average_processing_time"] = total_time / self.stats["successful_requests"]
            else:
                self.stats["failed_requests"] += 1
            
            return {
                "status": "success" if response.success else "error",
                "result": asdict(response)
            }
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            log_error(LogCategory.MCP, "OCR请求处理失败", {"error": str(e)})
            return {
                "status": "error",
                "message": f"OCR处理失败: {str(e)}"
            }
    
    async def _execute_ocr(self, model: CloudModel, request: OCRRequest) -> OCRResponse:
        """执行OCR处理"""
        
        # 构建提示词
        prompt = self._build_ocr_prompt(request)
        
        # 获取模型配置
        model_key = model.value.replace("/", "_").replace("-", "_").replace(".", "_")
        model_config = self.model_configs.get(model_key)
        
        if not model_config:
            return OCRResponse(
                success=False,
                content="",
                confidence=0.0,
                model_used=model.value,
                processing_time=0.0,
                cost=0.0,
                error="模型配置不存在"
            )
        
        # 执行API调用
        async with CloudModelClient(model_config) as client:
            result = await client.process_image(request.image_data, prompt)
        
        if result["success"]:
            # 计算置信度（简单实现）
            confidence = self._calculate_confidence(result["content"], request.task_type)
            
            return OCRResponse(
                success=True,
                content=result["content"],
                confidence=confidence,
                model_used=result["model"],
                processing_time=result["processing_time"],
                cost=result["cost"],
                metadata={"prompt": prompt}
            )
        else:
            return OCRResponse(
                success=False,
                content="",
                confidence=0.0,
                model_used=result["model"],
                processing_time=result["processing_time"],
                cost=result["cost"],
                error=result["error"]
            )
    
    def _build_ocr_prompt(self, request: OCRRequest) -> str:
        """构建OCR提示词"""
        
        base_prompt = f"""请仔细分析这张图像，并完成以下OCR任务：

任务类型: {request.task_type.value}
语言: {request.language}
输出格式: {request.output_format}
质量要求: {request.quality_level}

请按照以下要求处理：
"""
        
        task_specific_prompts = {
            TaskType.DOCUMENT_OCR: """
1. 识别所有可见的文字内容
2. 保持原有的格式和布局
3. 用markdown格式输出
4. 标注不确定的文字内容
""",
            TaskType.HANDWRITING_OCR: """
1. 仔细识别手写文字内容
2. 对于模糊或不确定的字符，用[?]标注
3. 保持原有的行间距和段落结构
4. 用markdown格式输出
""",
            TaskType.TABLE_EXTRACTION: """
1. 识别并提取表格结构
2. 用markdown表格格式输出
3. 保持表格的行列对应关系
4. 对于合并单元格，用适当的方式表示
""",
            TaskType.FORM_PROCESSING: """
1. 识别表单的字段和对应的值
2. 用结构化的格式输出（如JSON或markdown）
3. 标注字段名称和填写内容
4. 保持表单的逻辑结构
""",
            TaskType.MULTILINGUAL_OCR: """
1. 识别图像中的所有语言文字
2. 标注每种语言的内容
3. 保持原有的布局和格式
4. 用markdown格式输出，并标注语言类型
""",
            TaskType.STRUCTURED_DATA: """
1. 提取图像中的结构化信息
2. 识别数据的层次关系
3. 用JSON或markdown格式输出
4. 保持数据的完整性和准确性
"""
        }
        
        specific_prompt = task_specific_prompts.get(request.task_type, task_specific_prompts[TaskType.DOCUMENT_OCR])
        
        return base_prompt + specific_prompt + "\n请开始处理："
    
    def _calculate_confidence(self, content: str, task_type: TaskType) -> float:
        """计算置信度（简单实现）"""
        
        # 基础置信度
        base_confidence = 0.8
        
        # 基于内容长度调整
        if len(content) < 10:
            base_confidence -= 0.3
        elif len(content) > 100:
            base_confidence += 0.1
        
        # 基于任务类型调整
        task_adjustments = {
            TaskType.DOCUMENT_OCR: 0.0,
            TaskType.HANDWRITING_OCR: -0.1,
            TaskType.TABLE_EXTRACTION: -0.05,
            TaskType.FORM_PROCESSING: -0.05,
            TaskType.MULTILINGUAL_OCR: -0.1,
            TaskType.STRUCTURED_DATA: -0.05
        }
        
        adjustment = task_adjustments.get(task_type, 0.0)
        confidence = max(0.0, min(1.0, base_confidence + adjustment))
        
        return confidence
    
    async def _try_fallback_models(self, request: OCRRequest, failed_model: CloudModel) -> OCRResponse:
        """尝试备用模型"""
        
        fallback_models = self.config.get("cloud_search_mcp", {}).get("fallback_models", [])
        
        for model_key in fallback_models:
            # 跳过已失败的模型
            if model_key == failed_model.value.replace("/", "_").replace("-", "_").replace(".", "_"):
                continue
            
            # 查找对应的CloudModel
            fallback_model = None
            for model in CloudModel:
                if model.value.replace("/", "_").replace("-", "_").replace(".", "_") == model_key:
                    fallback_model = model
                    break
            
            if fallback_model and model_key in self.model_configs:
                try:
                    response = await self._execute_ocr(fallback_model, request)
                    if response.success:
                        return response
                except Exception as e:
                    logger.warning(f"备用模型 {model_key} 处理失败: {e}")
                    continue
        
        # 所有备用模型都失败
        return OCRResponse(
            success=False,
            content="",
            confidence=0.0,
            model_used="fallback_failed",
            processing_time=0.0,
            cost=0.0,
            error="所有备用模型都失败"
        )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取MCP能力列表"""
        return {
            "status": "success",
            "capabilities": [
                "document_ocr",
                "handwriting_recognition",
                "table_extraction", 
                "form_processing",
                "multilingual_ocr",
                "structured_data_extraction"
            ],
            "supported_formats": self.config.get("ocr_settings", {}).get("supported_formats", []),
            "supported_languages": ["auto", "zh-CN", "en", "ja", "ko", "fr", "de", "es", "ru"]
        }
    
    def get_supported_models(self) -> Dict[str, Any]:
        """获取支持的模型列表"""
        models = []
        for model_key, config in self.model_configs.items():
            models.append({
                "key": model_key,
                "model_id": config.model_id,
                "enabled": config.enabled,
                "quality_score": config.quality_score,
                "speed_score": config.speed_score,
                "cost_per_1k_tokens": config.cost_per_1k_tokens
            })
        
        return {
            "status": "success",
            "models": models
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "status": "success",
            "statistics": self.stats.copy()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        enabled_models = len([c for c in self.model_configs.values() if c.enabled])
        
        return {
            "status": "success",
            "health": {
                "service": "healthy",
                "enabled_models": enabled_models,
                "total_requests": self.stats["total_requests"],
                "success_rate": (self.stats["successful_requests"] / max(1, self.stats["total_requests"])) * 100,
                "average_cost": self.stats["total_cost"] / max(1, self.stats["successful_requests"]),
                "average_processing_time": self.stats["average_processing_time"]
            }
        }

# ============================================================================
# CLI接口
# ============================================================================

def main():
    """CLI主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud Search MCP - 云端视觉搜索MCP")
    parser.add_argument("--config", default="config.toml", help="配置文件路径")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--image", help="测试图像路径")
    parser.add_argument("--task-type", default="document_ocr", help="任务类型")
    
    args = parser.parse_args()
    
    if args.test:
        # 运行测试
        asyncio.run(run_test(args.config, args.image, args.task_type))
    else:
        # 启动MCP服务
        print("Cloud Search MCP 服务启动中...")
        mcp = CloudSearchMCP(args.config)
        print(f"服务已启动，支持的模型: {list(mcp.model_configs.keys())}")

async def run_test(config_path: str, image_path: str, task_type: str):
    """运行测试"""
    if not image_path:
        print("请提供测试图像路径: --image <path>")
        return
    
    try:
        # 读取图像
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # 初始化MCP
        mcp = CloudSearchMCP(config_path)
        
        # 处理请求
        result = await mcp.process_ocr_request(
            image_data=image_data,
            task_type=task_type,
            language="auto",
            output_format="markdown"
        )
        
        print("=" * 60)
        print("Cloud Search MCP 测试结果")
        print("=" * 60)
        print(f"状态: {result['status']}")
        
        if result["status"] == "success":
            response = result["result"]
            print(f"模型: {response['model_used']}")
            print(f"置信度: {response['confidence']:.2f}")
            print(f"处理时间: {response['processing_time']:.2f}s")
            print(f"成本: ${response['cost']:.6f}")
            print("\nOCR结果:")
            print("-" * 40)
            print(response['content'])
        else:
            print(f"错误: {result['message']}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    main()

