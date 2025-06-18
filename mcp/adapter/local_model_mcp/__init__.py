"""
Local Model MCP 模块初始化
统一的本地模型MCP适配器，支持Qwen 8B和Mistral 12B，集成OCR功能
"""

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"
__description__ = "统一的本地模型MCP适配器"

from .local_model_mcp import LocalModelMCP
from .models.model_manager import ModelManager
from .models.qwen_model import QwenModel
from .models.mistral_model import MistralModel
from .ocr.ocr_engine import OCREngine

__all__ = [
    "LocalModelMCP",
    "ModelManager", 
    "QwenModel",
    "MistralModel",
    "OCREngine"
]

