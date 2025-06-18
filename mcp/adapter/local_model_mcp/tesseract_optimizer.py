"""
Tesseract参数调优器 - 针对不同内容类型的参数优化
"""

import pytesseract
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, replace
from enum import Enum
import re
import time
import os

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """内容类型枚举"""
    PRINTED_TEXT = "printed_text"      # 印刷体文字
    HANDWRITING = "handwriting"        # 手写文字
    NUMBERS = "numbers"                # 数字
    TABLE_CONTENT = "table_content"    # 表格内容
    MIXED_CONTENT = "mixed_content"    # 混合内容
    FORM_FIELDS = "form_fields"        # 表单字段

@dataclass
class TesseractConfig:
    """Tesseract配置"""
    psm: int = 6                      # Page Segmentation Mode
    oem: int = 1                      # OCR Engine Mode
    languages: str = "chi_sim+chi_tra+eng"
    whitelist: str = ""               # 字符白名单
    blacklist: str = ""               # 字符黑名单
    dpi: int = 300                    # DPI设置
    custom_config: str = ""           # 自定义配置

class TesseractOptimizer:
    """Tesseract参数优化器"""
    
    def __init__(self):
        self.content_configs = self._initialize_content_configs()
        self.performance_cache = {}
        
    def _initialize_content_configs(self) -> Dict[ContentType, TesseractConfig]:
        """初始化不同内容类型的配置"""
        configs = {
            # 印刷体文字配置
            ContentType.PRINTED_TEXT: TesseractConfig(
                psm=6,  # 统一文本块
                oem=1,  # LSTM引擎
                languages="chi_sim+chi_tra+eng",
                custom_config="-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億"
            ),
            
            # 手写文字配置
            ContentType.HANDWRITING: TesseractConfig(
                psm=8,  # 单词级别
                oem=1,  # LSTM引擎
                languages="chi_sim+chi_tra+eng",
                custom_config="-c tessedit_char_whitelist=0123456789一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            ),
            
            # 数字配置
            ContentType.NUMBERS: TesseractConfig(
                psm=8,  # 单词级别
                oem=1,  # LSTM引擎
                languages="eng",
                whitelist="0123456789.,+-/",
                custom_config="-c tessedit_char_whitelist=0123456789.,-+/"
            ),
            
            # 表格内容配置
            ContentType.TABLE_CONTENT: TesseractConfig(
                psm=6,  # 统一文本块
                oem=1,  # LSTM引擎
                languages="chi_sim+chi_tra+eng",
                custom_config="-c preserve_interword_spaces=1"
            ),
            
            # 混合内容配置
            ContentType.MIXED_CONTENT: TesseractConfig(
                psm=3,  # 完全自动页面分割
                oem=1,  # LSTM引擎
                languages="chi_sim+chi_tra+eng",
                custom_config=""
            ),
            
            # 表单字段配置
            ContentType.FORM_FIELDS: TesseractConfig(
                psm=7,  # 单行文本
                oem=1,  # LSTM引擎
                languages="chi_sim+chi_tra+eng",
                custom_config="-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz一二三四五六七八九十百千万亿零壹贰叁肆伍陆柒捌玖拾佰仟萬億"
            )
        }
        
        return configs
    
    def detect_content_type(self, image_path: str) -> ContentType:
        """
        检测图像的主要内容类型
        
        Args:
            image_path: 图像路径
            
        Returns:
            ContentType: 检测到的内容类型
        """
        logger.info(f"🔍 检测内容类型: {image_path}")
        
        # 读取图像
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # 基础OCR识别
        try:
            text = pytesseract.image_to_string(image, lang='chi_sim+chi_tra+eng')
            
            # 分析文本特征
            content_type = self._analyze_text_features(text, image)
            
            logger.info(f"📊 检测结果: {content_type.value}")
            return content_type
            
        except Exception as e:
            logger.warning(f"⚠️ 内容类型检测失败: {e}")
            return ContentType.MIXED_CONTENT
    
    def _analyze_text_features(self, text: str, image: np.ndarray) -> ContentType:
        """分析文本特征确定内容类型"""
        
        # 计算各种特征
        total_chars = len(text.strip())
        if total_chars == 0:
            return ContentType.MIXED_CONTENT
        
        # 数字比例
        digit_count = len(re.findall(r'\d', text))
        digit_ratio = digit_count / total_chars
        
        # 中文字符比例
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        chinese_ratio = chinese_count / total_chars
        
        # 英文字符比例
        english_count = len(re.findall(r'[a-zA-Z]', text))
        english_ratio = english_count / total_chars
        
        # 特殊字符比例（表格相关）
        special_count = len(re.findall(r'[|_\-=+]', text))
        special_ratio = special_count / total_chars
        
        # 检测表格结构
        has_table_structure = self._detect_table_structure(image)
        
        # 决策逻辑
        if digit_ratio > 0.7:
            return ContentType.NUMBERS
        elif has_table_structure and special_ratio > 0.1:
            return ContentType.TABLE_CONTENT
        elif chinese_ratio > 0.6:
            # 进一步判断是印刷体还是手写
            if self._is_handwriting(image):
                return ContentType.HANDWRITING
            else:
                return ContentType.PRINTED_TEXT
        elif english_ratio > 0.6:
            return ContentType.PRINTED_TEXT
        else:
            return ContentType.MIXED_CONTENT
    
    def _detect_table_structure(self, image: np.ndarray) -> bool:
        """检测是否有表格结构"""
        # 检测水平线
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
        
        # 检测垂直线
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
        
        # 计算线条密度
        h_line_pixels = np.sum(horizontal_lines > 0)
        v_line_pixels = np.sum(vertical_lines > 0)
        total_pixels = image.shape[0] * image.shape[1]
        
        line_density = (h_line_pixels + v_line_pixels) / total_pixels
        
        return line_density > 0.01  # 阈值可调
    
    def _is_handwriting(self, image: np.ndarray) -> bool:
        """简单判断是否为手写内容"""
        # 计算边缘密度和不规则性
        edges = cv2.Canny(image, 50, 150)
        edge_density = np.sum(edges > 0) / (image.shape[0] * image.shape[1])
        
        # 手写通常有更多不规则边缘
        return edge_density > 0.05
    
    def optimize_for_content(self, image_path: str, content_type: ContentType = None) -> TesseractConfig:
        """
        为特定内容类型优化Tesseract配置
        
        Args:
            image_path: 图像路径
            content_type: 内容类型，None则自动检测
            
        Returns:
            TesseractConfig: 优化后的配置
        """
        if content_type is None:
            content_type = self.detect_content_type(image_path)
        
        base_config = replace(self.content_configs[content_type])
        
        # 根据图像特征进一步调优
        optimized_config = self._fine_tune_config(image_path, base_config)
        
        logger.info(f"🔧 为 {content_type.value} 优化配置: PSM={optimized_config.psm}, OEM={optimized_config.oem}")
        
        return optimized_config
    
    def _fine_tune_config(self, image_path: str, config: TesseractConfig) -> TesseractConfig:
        """根据图像特征微调配置"""
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # 分析图像质量
        image_quality = self._analyze_image_quality(image)
        
        # 根据质量调整参数
        if image_quality['noise_level'] > 0.3:
            # 高噪声图像，使用更保守的设置
            config.custom_config += " -c tessedit_enable_doc_dict=0"
        
        if image_quality['contrast'] < 0.3:
            # 低对比度图像，启用更多预处理
            config.custom_config += " -c tessedit_enable_bigram_correction=1"
        
        if image_quality['resolution'] < 150:
            # 低分辨率图像，调整DPI
            config.dpi = 150
        
        return config
    
    def _analyze_image_quality(self, image: np.ndarray) -> Dict[str, float]:
        """分析图像质量指标"""
        # 噪声水平（基于拉普拉斯方差）
        laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
        noise_level = min(laplacian_var / 1000, 1.0)
        
        # 对比度（基于标准差）
        contrast = image.std() / 255.0
        
        # 分辨率估计（基于图像尺寸）
        resolution = min(image.shape) / 10  # 简化估计
        
        return {
            'noise_level': noise_level,
            'contrast': contrast,
            'resolution': resolution
        }
    
    def build_tesseract_command(self, config: TesseractConfig) -> str:
        """构建Tesseract命令字符串"""
        cmd_parts = []
        
        # PSM设置
        cmd_parts.append(f"--psm {config.psm}")
        
        # OEM设置
        cmd_parts.append(f"--oem {config.oem}")
        
        # DPI设置
        cmd_parts.append(f"--dpi {config.dpi}")
        
        # 语言设置
        cmd_parts.append(f"-l {config.languages}")
        
        # 字符白名单
        if config.whitelist:
            cmd_parts.append(f"-c tessedit_char_whitelist={config.whitelist}")
        
        # 字符黑名单
        if config.blacklist:
            cmd_parts.append(f"-c tessedit_char_blacklist={config.blacklist}")
        
        # 自定义配置
        if config.custom_config:
            cmd_parts.append(config.custom_config)
        
        return " ".join(cmd_parts)
    
    def test_multiple_configs(self, image_path: str) -> Dict[str, Dict]:
        """测试多种配置的效果"""
        logger.info(f"🧪 测试多种Tesseract配置: {image_path}")
        
        results = {}
        
        for content_type in ContentType:
            logger.info(f"📝 测试配置: {content_type.value}")
            
            try:
                # 获取配置
                config = self.content_configs[content_type]
                cmd = self.build_tesseract_command(config)
                
                # 执行OCR
                start_time = time.time()
                
                # 使用PIL读取图像
                image = Image.open(image_path)
                
                # 执行OCR
                text = pytesseract.image_to_string(image, config=cmd)
                
                processing_time = time.time() - start_time
                
                # 计算质量指标
                quality_score = self._calculate_quality_score(text)
                
                results[content_type.value] = {
                    'text': text,
                    'processing_time': processing_time,
                    'quality_score': quality_score,
                    'text_length': len(text.strip()),
                    'config': cmd
                }
                
                logger.info(f"✅ {content_type.value}: 质量={quality_score:.2f}, 时间={processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ {content_type.value} 测试失败: {e}")
                results[content_type.value] = {
                    'error': str(e),
                    'quality_score': 0.0
                }
        
        return results
    
    def _calculate_quality_score(self, text: str) -> float:
        """计算OCR质量分数"""
        if not text.strip():
            return 0.0
        
        score = 0.0
        
        # 文本长度分数（有内容得分）
        if len(text.strip()) > 10:
            score += 0.3
        
        # 中文字符识别分数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        if chinese_chars > 0:
            score += 0.3
        
        # 数字识别分数
        digits = len(re.findall(r'\d', text))
        if digits > 0:
            score += 0.2
        
        # 结构完整性分数（基于常见词汇）
        common_words = ['保险', '银行', '姓名', '地址', '电话', '金额', '日期']
        found_words = sum(1 for word in common_words if word in text)
        score += (found_words / len(common_words)) * 0.2
        
        return min(score, 1.0)
    
    def get_best_config(self, image_path: str) -> Tuple[TesseractConfig, str]:
        """获取最佳配置"""
        results = self.test_multiple_configs(image_path)
        
        # 找到质量分数最高的配置
        best_type = max(results.keys(), key=lambda k: results[k].get('quality_score', 0))
        best_result = results[best_type]
        
        logger.info(f"🏆 最佳配置: {best_type} (质量分数: {best_result['quality_score']:.2f})")
        
        return self.content_configs[ContentType(best_type)], best_result['text']

# 测试函数
def test_tesseract_optimization():
    """测试Tesseract优化功能"""
    print("🧪 测试Tesseract参数优化器")
    print("=" * 60)
    
    # 测试图像路径
    test_image = "/home/ubuntu/upload/張家銓_1.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        return
    
    # 创建优化器
    optimizer = TesseractOptimizer()
    
    try:
        # 内容类型检测
        print("🔍 检测内容类型...")
        content_type = optimizer.detect_content_type(test_image)
        print(f"📊 检测结果: {content_type.value}")
        
        # 配置优化
        print(f"\n🔧 为 {content_type.value} 优化配置...")
        optimized_config = optimizer.optimize_for_content(test_image, content_type)
        cmd = optimizer.build_tesseract_command(optimized_config)
        print(f"⚙️ 优化配置: {cmd}")
        
        # 多配置测试
        print(f"\n🧪 测试所有配置...")
        results = optimizer.test_multiple_configs(test_image)
        
        print(f"\n📊 测试结果汇总:")
        print("-" * 60)
        for config_name, result in results.items():
            if 'error' not in result:
                print(f"{config_name:15} | 质量: {result['quality_score']:.2f} | 时间: {result['processing_time']:.2f}s | 长度: {result['text_length']}")
            else:
                print(f"{config_name:15} | 错误: {result['error']}")
        
        # 获取最佳配置
        print(f"\n🏆 获取最佳配置...")
        best_config, best_text = optimizer.get_best_config(test_image)
        print(f"📝 最佳识别结果预览: {best_text[:100]}...")
        
    except Exception as e:
        print(f"❌ Tesseract优化测试失败: {e}")

if __name__ == "__main__":
    test_tesseract_optimization()

