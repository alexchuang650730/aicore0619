"""
OCR引擎 - 整合OCR Mistral功能到统一MCP中
基于现有OCR Mistral项目的实现
"""

import asyncio
import logging
import json
import time
import base64
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import io

logger = logging.getLogger(__name__)

class OCREngine:
    """OCR引擎 - 整合现有OCR Mistral功能"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化OCR引擎
        
        Args:
            config: OCR配置
        """
        self.config = config.get("ocr", {})
        self.enabled = self.config.get("enabled", False)
        
        # OCR配置
        self.languages = self.config.get("languages", ["zh", "en", "auto"])
        self.output_format = self.config.get("output_format", "text")
        self.preserve_layout = self.config.get("preserve_layout", True)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.8)
        self.preprocessing = self.config.get("preprocessing", True)
        
        # OCR引擎选择
        self.engine = self.config.get("engine", "integrated")
        
        # 运行时状态
        self.ocr_model = None
        self.initialized = False
        self.available_engines = []
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "average_processing_time": 0
        }
        
        logger.info(f"OCREngine初始化 - 启用: {self.enabled}")
    
    async def initialize(self) -> bool:
        """
        初始化OCR引擎
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            if not self.enabled:
                logger.info("OCR功能已禁用")
                return True
            
            logger.info("开始初始化OCR引擎...")
            
            # 检测可用的OCR引擎
            await self._detect_available_engines()
            
            if not self.available_engines:
                logger.warning("没有可用的OCR引擎")
                return False
            
            # 初始化首选引擎
            if await self._initialize_engine():
                self.initialized = True
                logger.info(f"OCR引擎初始化成功 - 引擎: {self.engine}")
                return True
            else:
                logger.error("OCR引擎初始化失败")
                return False
            
        except Exception as e:
            logger.error(f"OCR引擎初始化失败: {e}")
            return False
    
    async def _detect_available_engines(self):
        """检测可用的OCR引擎"""
        self.available_engines = []
        
        # 检测EasyOCR
        try:
            import easyocr
            self.available_engines.append("easyocr")
            logger.info("检测到EasyOCR")
        except ImportError:
            pass
        
        # 检测PaddleOCR
        try:
            import paddleocr
            self.available_engines.append("paddleocr")
            logger.info("检测到PaddleOCR")
        except ImportError:
            pass
        
        # 检测Tesseract
        try:
            import pytesseract
            self.available_engines.append("tesseract")
            logger.info("检测到Tesseract")
        except ImportError:
            pass
        
        # 检测云端OCR API
        if self.config.get("cloud_ocr_api_key"):
            self.available_engines.append("cloud_api")
            logger.info("检测到云端OCR API")
        
        logger.info(f"可用OCR引擎: {self.available_engines}")
    
    async def _initialize_engine(self) -> bool:
        """初始化OCR引擎"""
        try:
            # 根据配置和可用性选择引擎
            if self.engine == "integrated":
                # 自动选择最佳引擎
                if "easyocr" in self.available_engines:
                    return await self._initialize_easyocr()
                elif "paddleocr" in self.available_engines:
                    return await self._initialize_paddleocr()
                elif "tesseract" in self.available_engines:
                    return await self._initialize_tesseract()
                elif "cloud_api" in self.available_engines:
                    return await self._initialize_cloud_api()
            else:
                # 使用指定引擎
                if self.engine == "easyocr" and "easyocr" in self.available_engines:
                    return await self._initialize_easyocr()
                elif self.engine == "paddleocr" and "paddleocr" in self.available_engines:
                    return await self._initialize_paddleocr()
                elif self.engine == "tesseract" and "tesseract" in self.available_engines:
                    return await self._initialize_tesseract()
                elif self.engine == "cloud_api" and "cloud_api" in self.available_engines:
                    return await self._initialize_cloud_api()
            
            return False
            
        except Exception as e:
            logger.error(f"引擎初始化失败: {e}")
            return False
    
    async def _initialize_easyocr(self) -> bool:
        """初始化EasyOCR"""
        try:
            import easyocr
            
            # 设置语言
            languages = []
            for lang in self.languages:
                if lang == "zh":
                    languages.append("ch_sim")
                elif lang == "en":
                    languages.append("en")
                elif lang != "auto":
                    languages.append(lang)
            
            if not languages:
                languages = ["ch_sim", "en"]
            
            self.ocr_model = easyocr.Reader(languages, gpu=True)
            self.engine = "easyocr"
            logger.info("EasyOCR初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"EasyOCR初始化失败: {e}")
            return False
    
    async def _initialize_paddleocr(self) -> bool:
        """初始化PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            # 设置语言
            lang = "ch" if "zh" in self.languages else "en"
            
            self.ocr_model = PaddleOCR(
                use_angle_cls=True,
                lang=lang,
                use_gpu=True,
                show_log=False
            )
            self.engine = "paddleocr"
            logger.info("PaddleOCR初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {e}")
            return False
    
    async def _initialize_tesseract(self) -> bool:
        """初始化Tesseract"""
        try:
            import pytesseract
            
            # 检查Tesseract是否安装
            try:
                pytesseract.get_tesseract_version()
                self.ocr_model = pytesseract
                self.engine = "tesseract"
                logger.info("Tesseract初始化成功")
                return True
            except Exception:
                logger.error("Tesseract未正确安装")
                return False
            
        except Exception as e:
            logger.error(f"Tesseract初始化失败: {e}")
            return False
    
    async def _initialize_cloud_api(self) -> bool:
        """初始化云端OCR API"""
        try:
            # 这里可以集成各种云端OCR服务
            # 如百度OCR、腾讯OCR、阿里云OCR等
            self.engine = "cloud_api"
            logger.info("云端OCR API初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"云端OCR API初始化失败: {e}")
            return False
    
    async def extract_text(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """
        从图像提取文本
        
        Args:
            image_data: 图像数据
            **kwargs: 其他参数
            
        Returns:
            Dict: OCR结果
        """
        start_time = time.time()
        
        try:
            if not self.initialized or not self.enabled:
                return {
                    "success": False,
                    "error": "OCR引擎未初始化或已禁用",
                    "processing_time": time.time() - start_time
                }
            
            # 更新统计
            self.stats["total_requests"] += 1
            
            # 预处理图像
            if self.preprocessing:
                image_data = await self._preprocess_image(image_data)
            
            # 根据引擎类型进行OCR
            if self.engine == "easyocr":
                result = await self._extract_with_easyocr(image_data, **kwargs)
            elif self.engine == "paddleocr":
                result = await self._extract_with_paddleocr(image_data, **kwargs)
            elif self.engine == "tesseract":
                result = await self._extract_with_tesseract(image_data, **kwargs)
            elif self.engine == "cloud_api":
                result = await self._extract_with_cloud_api(image_data, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"不支持的OCR引擎: {self.engine}",
                    "processing_time": time.time() - start_time
                }
            
            # 后处理结果
            if result["success"]:
                result = await self._postprocess_result(result, **kwargs)
                self.stats["successful_extractions"] += 1
            else:
                self.stats["failed_extractions"] += 1
            
            # 更新平均处理时间
            processing_time = time.time() - start_time
            result["processing_time"] = processing_time
            self._update_average_time(processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"OCR文本提取失败: {e}")
            self.stats["failed_extractions"] += 1
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _preprocess_image(self, image_data: bytes) -> bytes:
        """预处理图像"""
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            import io
            
            # 打开图像
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # 锐化
            image = image.filter(ImageFilter.SHARPEN)
            
            # 保存处理后的图像
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"图像预处理失败: {e}")
            return image_data  # 返回原始图像
    
    async def _extract_with_easyocr(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """使用EasyOCR提取文本"""
        try:
            import numpy as np
            from PIL import Image
            import io
            
            # 转换图像格式
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # 执行OCR
            results = self.ocr_model.readtext(image_array)
            
            # 处理结果
            extracted_text = []
            confidence_scores = []
            
            for (bbox, text, confidence) in results:
                if confidence >= self.confidence_threshold:
                    extracted_text.append(text)
                    confidence_scores.append(confidence)
            
            return {
                "success": True,
                "text": "\n".join(extracted_text) if self.preserve_layout else " ".join(extracted_text),
                "confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                "engine": "easyocr",
                "details": {
                    "total_detections": len(results),
                    "valid_detections": len(extracted_text),
                    "confidence_scores": confidence_scores
                }
            }
            
        except Exception as e:
            logger.error(f"EasyOCR提取失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_with_paddleocr(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """使用PaddleOCR提取文本"""
        try:
            import numpy as np
            from PIL import Image
            import io
            
            # 转换图像格式
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # 执行OCR
            results = self.ocr_model.ocr(image_array, cls=True)
            
            # 处理结果
            extracted_text = []
            confidence_scores = []
            
            for line in results[0] if results[0] else []:
                text = line[1][0]
                confidence = line[1][1]
                
                if confidence >= self.confidence_threshold:
                    extracted_text.append(text)
                    confidence_scores.append(confidence)
            
            return {
                "success": True,
                "text": "\n".join(extracted_text) if self.preserve_layout else " ".join(extracted_text),
                "confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
                "engine": "paddleocr",
                "details": {
                    "total_detections": len(results[0]) if results[0] else 0,
                    "valid_detections": len(extracted_text),
                    "confidence_scores": confidence_scores
                }
            }
            
        except Exception as e:
            logger.error(f"PaddleOCR提取失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_with_tesseract(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """使用Tesseract提取文本"""
        try:
            from PIL import Image
            import io
            
            # 转换图像格式
            image = Image.open(io.BytesIO(image_data))
            
            # 设置语言
            lang = "chi_sim+eng" if "zh" in self.languages else "eng"
            
            # 执行OCR
            text = self.ocr_model.image_to_string(image, lang=lang)
            
            return {
                "success": True,
                "text": text.strip(),
                "confidence": 0.8,  # Tesseract不提供置信度，使用默认值
                "engine": "tesseract",
                "details": {
                    "language": lang
                }
            }
            
        except Exception as e:
            logger.error(f"Tesseract提取失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_with_cloud_api(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """使用云端API提取文本"""
        try:
            # 这里可以集成各种云端OCR服务
            # 示例：百度OCR API
            
            # 将图像转换为base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 调用云端API（这里需要根据具体的API实现）
            # result = await self._call_cloud_ocr_api(image_base64)
            
            # 临时返回示例结果
            return {
                "success": True,
                "text": "云端OCR功能待实现",
                "confidence": 0.9,
                "engine": "cloud_api",
                "details": {
                    "api_provider": "example"
                }
            }
            
        except Exception as e:
            logger.error(f"云端OCR提取失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _postprocess_result(self, result: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """后处理OCR结果"""
        try:
            if not result["success"]:
                return result
            
            text = result["text"]
            
            # 清理文本
            if kwargs.get("clean_text", True):
                # 移除多余的空白字符
                text = " ".join(text.split())
                
                # 移除特殊字符（可选）
                if kwargs.get("remove_special_chars", False):
                    import re
                    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
            
            # 格式化输出
            if self.output_format == "json":
                result["formatted_output"] = {
                    "text": text,
                    "metadata": result.get("details", {})
                }
            elif self.output_format == "markdown":
                result["formatted_output"] = f"```\n{text}\n```"
            
            result["text"] = text
            return result
            
        except Exception as e:
            logger.warning(f"结果后处理失败: {e}")
            return result
    
    def _update_average_time(self, processing_time: float):
        """更新平均处理时间"""
        current_avg = self.stats["average_processing_time"]
        total_requests = self.stats["total_requests"]
        
        self.stats["average_processing_time"] = (
            (current_avg * (total_requests - 1) + processing_time) / total_requests
        )
    
    async def process_document(self, image_list: List[bytes], **kwargs) -> Dict[str, Any]:
        """
        处理多页文档
        
        Args:
            image_list: 图像数据列表
            **kwargs: 其他参数
            
        Returns:
            Dict: 处理结果
        """
        try:
            results = []
            total_text = []
            
            for i, image_data in enumerate(image_list):
                logger.info(f"处理第 {i+1}/{len(image_list)} 页")
                
                result = await self.extract_text(image_data, **kwargs)
                results.append(result)
                
                if result["success"]:
                    total_text.append(result["text"])
            
            # 合并所有文本
            combined_text = "\n\n".join(total_text) if self.preserve_layout else " ".join(total_text)
            
            # 计算总体统计
            successful_pages = sum(1 for r in results if r["success"])
            total_confidence = sum(r.get("confidence", 0) for r in results if r["success"])
            average_confidence = total_confidence / successful_pages if successful_pages > 0 else 0
            
            return {
                "success": successful_pages > 0,
                "text": combined_text,
                "confidence": average_confidence,
                "total_pages": len(image_list),
                "successful_pages": successful_pages,
                "failed_pages": len(image_list) - successful_pages,
                "page_results": results
            }
            
        except Exception as e:
            logger.error(f"文档处理失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_pages": len(image_list)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取OCR引擎状态"""
        return {
            "enabled": self.enabled,
            "initialized": self.initialized,
            "engine": self.engine,
            "available_engines": self.available_engines,
            "languages": self.languages,
            "statistics": self.stats
        }
    
    async def shutdown(self):
        """关闭OCR引擎"""
        try:
            logger.info("关闭OCR引擎")
            
            # 清理模型
            if self.ocr_model:
                del self.ocr_model
                self.ocr_model = None
            
            self.initialized = False
            
        except Exception as e:
            logger.error(f"关闭OCR引擎失败: {e}")

