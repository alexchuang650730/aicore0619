"""
多引擎OCR管理器 - 统一管理多个OCR引擎
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import asyncio

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCREngine(Enum):
    """OCR引擎枚举"""
    TESSERACT = "tesseract"
    EASYOCR = "easyocr"
    PADDLEOCR = "paddleocr"
    CLOUD_API = "cloud_api"

@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    bbox: Optional[List[Tuple[int, int]]] = None
    engine: Optional[str] = None
    processing_time: Optional[float] = None

@dataclass
class EngineConfig:
    """引擎配置"""
    enabled: bool = True
    priority: int = 1
    languages: List[str] = None
    confidence_threshold: float = 0.6
    max_retry: int = 3
    timeout: int = 30

class MultiEngineOCRManager:
    """多引擎OCR管理器"""
    
    def __init__(self, config_path: str = None):
        self.engines = {}
        self.engine_configs = {}
        self.available_engines = []
        
        # 默认配置
        self.default_configs = {
            OCREngine.TESSERACT: EngineConfig(
                enabled=True,
                priority=3,
                languages=["chi_sim", "chi_tra", "eng"],
                confidence_threshold=0.6
            ),
            OCREngine.EASYOCR: EngineConfig(
                enabled=True,
                priority=1,
                languages=["ch_sim", "ch_tra", "en"],
                confidence_threshold=0.7
            ),
            OCREngine.PADDLEOCR: EngineConfig(
                enabled=True,
                priority=2,
                languages=["ch", "en"],
                confidence_threshold=0.8
            )
        }
        
        self._initialize_engines()
    
    def _initialize_engines(self):
        """初始化所有可用的OCR引擎"""
        logger.info("🚀 初始化多引擎OCR管理器...")
        
        # 初始化Tesseract
        self._init_tesseract()
        
        # 初始化EasyOCR
        self._init_easyocr()
        
        # 初始化PaddleOCR
        self._init_paddleocr()
        
        # 按优先级排序可用引擎
        self.available_engines.sort(key=lambda x: self.engine_configs[x].priority)
        
        logger.info(f"✅ 可用OCR引擎: {[engine.value for engine in self.available_engines]}")
    
    def _init_tesseract(self):
        """初始化Tesseract引擎"""
        try:
            import pytesseract
            
            # 检查Tesseract是否可用
            version = pytesseract.get_tesseract_version()
            logger.info(f"✅ Tesseract {version} 初始化成功")
            
            self.engines[OCREngine.TESSERACT] = pytesseract
            self.engine_configs[OCREngine.TESSERACT] = self.default_configs[OCREngine.TESSERACT]
            self.available_engines.append(OCREngine.TESSERACT)
            
        except Exception as e:
            logger.warning(f"❌ Tesseract初始化失败: {e}")
    
    def _init_easyocr(self):
        """初始化EasyOCR引擎"""
        try:
            import easyocr
            
            # 创建EasyOCR读取器 - 修复语言配置
            # 分别创建简体中文和繁体中文读取器
            try:
                reader_sim = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                logger.info("✅ EasyOCR (简体中文) 初始化成功")
                self.engines[OCREngine.EASYOCR] = reader_sim
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR简体中文初始化失败: {e}")
                # 尝试仅英文模式
                reader_en = easyocr.Reader(['en'], gpu=False)
                logger.info("✅ EasyOCR (英文) 初始化成功")
                self.engines[OCREngine.EASYOCR] = reader_en
            
            self.engine_configs[OCREngine.EASYOCR] = self.default_configs[OCREngine.EASYOCR]
            self.available_engines.append(OCREngine.EASYOCR)
            
        except Exception as e:
            logger.warning(f"❌ EasyOCR初始化失败: {e}")
    
    def _init_paddleocr(self):
        """初始化PaddleOCR引擎"""
        try:
            # 跳过PaddleOCR安装，因为依赖复杂
            logger.info("⏭️ 跳过PaddleOCR初始化 (依赖复杂，后续优化)")
            return
            
            # 以下代码保留用于后续优化
            import subprocess
            import sys
            
            try:
                import paddleocr
            except ImportError:
                logger.info("📦 安装PaddleOCR...")
                # 使用清华源安装
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
                    "paddlepaddle", "paddleocr"
                ])
                import paddleocr
            
            # 创建PaddleOCR实例
            ocr = paddleocr.PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                use_gpu=False,
                show_log=False
            )
            logger.info("✅ PaddleOCR 初始化成功")
            
            self.engines[OCREngine.PADDLEOCR] = ocr
            self.engine_configs[OCREngine.PADDLEOCR] = self.default_configs[OCREngine.PADDLEOCR]
            self.available_engines.append(OCREngine.PADDLEOCR)
            
        except Exception as e:
            logger.warning(f"❌ PaddleOCR初始化失败: {e}")
    
    async def process_image(
        self, 
        image_path: str, 
        engines: List[OCREngine] = None,
        fusion_strategy: str = "best_confidence"
    ) -> OCRResult:
        """
        使用多引擎处理图像
        
        Args:
            image_path: 图像路径
            engines: 指定使用的引擎列表，None表示使用所有可用引擎
            fusion_strategy: 融合策略 ("best_confidence", "majority_vote", "weighted_average")
        
        Returns:
            OCRResult: 融合后的识别结果
        """
        if engines is None:
            engines = self.available_engines
        
        # 并行处理多个引擎
        tasks = []
        for engine in engines:
            if engine in self.available_engines:
                task = self._process_with_engine(image_path, engine)
                tasks.append(task)
        
        if not tasks:
            raise ValueError("没有可用的OCR引擎")
        
        # 等待所有引擎完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤成功的结果
        valid_results = [
            result for result in results 
            if isinstance(result, OCRResult) and result.confidence > 0
        ]
        
        if not valid_results:
            return OCRResult(text="", confidence=0.0, engine="none")
        
        # 应用融合策略
        return self._apply_fusion_strategy(valid_results, fusion_strategy)
    
    async def _process_with_engine(self, image_path: str, engine: OCREngine) -> OCRResult:
        """使用指定引擎处理图像"""
        import time
        start_time = time.time()
        
        try:
            if engine == OCREngine.TESSERACT:
                result = await self._process_with_tesseract(image_path)
            elif engine == OCREngine.EASYOCR:
                result = await self._process_with_easyocr(image_path)
            elif engine == OCREngine.PADDLEOCR:
                result = await self._process_with_paddleocr(image_path)
            else:
                raise ValueError(f"不支持的引擎: {engine}")
            
            result.engine = engine.value
            result.processing_time = time.time() - start_time
            
            logger.info(f"✅ {engine.value} 处理完成: {result.confidence:.2f} 置信度, {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ {engine.value} 处理失败: {e}")
            return OCRResult(text="", confidence=0.0, engine=engine.value)
    
    async def _process_with_tesseract(self, image_path: str) -> OCRResult:
        """使用Tesseract处理图像"""
        import pytesseract
        from PIL import Image
        
        # 读取图像
        image = Image.open(image_path)
        
        # 配置Tesseract参数
        config = '--psm 6 --oem 1 -l chi_sim+chi_tra+eng'
        
        # 获取详细结果
        data = pytesseract.image_to_data(
            image, 
            config=config, 
            output_type=pytesseract.Output.DICT
        )
        
        # 提取文本和置信度
        text_parts = []
        confidences = []
        
        for i, conf in enumerate(data['conf']):
            if int(conf) > 0:
                text = data['text'][i].strip()
                if text:
                    text_parts.append(text)
                    confidences.append(int(conf))
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence / 100.0  # 转换为0-1范围
        )
    
    async def _process_with_easyocr(self, image_path: str) -> OCRResult:
        """使用EasyOCR处理图像"""
        reader = self.engines[OCREngine.EASYOCR]
        
        # 处理图像
        results = reader.readtext(image_path)
        
        # 合并结果
        text_parts = []
        confidences = []
        
        for (bbox, text, confidence) in results:
            if confidence > self.engine_configs[OCREngine.EASYOCR].confidence_threshold:
                text_parts.append(text)
                confidences.append(confidence)
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence
        )
    
    async def _process_with_paddleocr(self, image_path: str) -> OCRResult:
        """使用PaddleOCR处理图像"""
        ocr = self.engines[OCREngine.PADDLEOCR]
        
        # 处理图像
        results = ocr.ocr(image_path, cls=True)
        
        # 合并结果
        text_parts = []
        confidences = []
        
        if results and results[0]:
            for line in results[0]:
                if line:
                    text = line[1][0]
                    confidence = line[1][1]
                    
                    if confidence > self.engine_configs[OCREngine.PADDLEOCR].confidence_threshold:
                        text_parts.append(text)
                        confidences.append(confidence)
        
        full_text = ' '.join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence
        )
    
    def _apply_fusion_strategy(self, results: List[OCRResult], strategy: str) -> OCRResult:
        """应用融合策略"""
        if strategy == "best_confidence":
            # 选择置信度最高的结果
            best_result = max(results, key=lambda x: x.confidence)
            return best_result
        
        elif strategy == "majority_vote":
            # 多数投票（简化版本）
            text_votes = {}
            for result in results:
                text = result.text.strip()
                if text:
                    if text not in text_votes:
                        text_votes[text] = []
                    text_votes[text].append(result)
            
            if text_votes:
                # 选择得票最多的文本
                best_text = max(text_votes.keys(), key=lambda x: len(text_votes[x]))
                best_results = text_votes[best_text]
                avg_confidence = sum(r.confidence for r in best_results) / len(best_results)
                
                return OCRResult(
                    text=best_text,
                    confidence=avg_confidence,
                    engine="fusion_majority"
                )
        
        elif strategy == "weighted_average":
            # 加权平均（基于引擎优先级）
            total_weight = 0
            weighted_confidence = 0
            all_texts = []
            
            for result in results:
                engine_enum = OCREngine(result.engine)
                weight = 1.0 / self.engine_configs[engine_enum].priority
                
                weighted_confidence += result.confidence * weight
                total_weight += weight
                all_texts.append(result.text)
            
            # 简单合并文本（可以进一步优化）
            merged_text = max(all_texts, key=len) if all_texts else ""
            avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
            
            return OCRResult(
                text=merged_text,
                confidence=avg_confidence,
                engine="fusion_weighted"
            )
        
        # 默认返回第一个结果
        return results[0] if results else OCRResult(text="", confidence=0.0)
    
    def get_engine_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        status = {
            "available_engines": [engine.value for engine in self.available_engines],
            "total_engines": len(self.available_engines),
            "engine_details": {}
        }
        
        for engine in self.available_engines:
            config = self.engine_configs[engine]
            status["engine_details"][engine.value] = {
                "enabled": config.enabled,
                "priority": config.priority,
                "languages": config.languages,
                "confidence_threshold": config.confidence_threshold
            }
        
        return status
    
    def set_engine_config(self, engine: OCREngine, config: EngineConfig):
        """设置引擎配置"""
        if engine in self.available_engines:
            self.engine_configs[engine] = config
            logger.info(f"✅ 更新 {engine.value} 配置")
        else:
            logger.warning(f"❌ 引擎 {engine.value} 不可用")

# 使用示例
async def main():
    """测试多引擎OCR管理器"""
    manager = MultiEngineOCRManager()
    
    # 显示引擎状态
    status = manager.get_engine_status()
    print("🔍 引擎状态:", status)
    
    # 测试图像处理
    test_image = "/home/ubuntu/upload/張家銓_1.jpg"
    if os.path.exists(test_image):
        print(f"\n📸 测试图像: {test_image}")
        
        # 使用不同融合策略
        strategies = ["best_confidence", "majority_vote", "weighted_average"]
        
        for strategy in strategies:
            print(f"\n🔄 融合策略: {strategy}")
            result = await manager.process_image(test_image, fusion_strategy=strategy)
            print(f"📝 识别文本: {result.text[:100]}...")
            print(f"📊 置信度: {result.confidence:.2f}")
            print(f"🔧 引擎: {result.engine}")

if __name__ == "__main__":
    asyncio.run(main())

