"""
图像预处理优化器 - 针对保险表单的专用预处理算法
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Tuple, List, Optional
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class PreprocessConfig:
    """预处理配置"""
    # 图像尺寸优化
    max_width: int = 2000
    max_height: int = 2800
    min_width: int = 800
    min_height: int = 1000
    
    # 图像质量
    dpi: int = 300
    quality: int = 95
    
    # 预处理参数
    contrast_factor: float = 1.2
    brightness_factor: float = 1.1
    sharpness_factor: float = 1.3
    
    # 噪声去除
    denoise_strength: int = 3
    morphology_kernel_size: int = 2
    
    # 表格检测
    table_line_thickness: int = 2
    min_line_length: int = 50
    
    # 手写区域检测
    handwriting_threshold: float = 0.3
    text_region_padding: int = 5

class ImagePreprocessor:
    """图像预处理器"""
    
    def __init__(self, config: PreprocessConfig = None):
        self.config = config or PreprocessConfig()
        
    def optimize_for_ocr(self, image_path: str, output_path: str = None) -> str:
        """
        为OCR优化图像
        
        Args:
            image_path: 输入图像路径
            output_path: 输出图像路径，None则自动生成
            
        Returns:
            str: 优化后的图像路径
        """
        logger.info(f"🔧 开始图像预处理: {image_path}")
        
        # 生成输出路径
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = f"{base_name}_optimized.jpg"
        
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        original_shape = image.shape
        logger.info(f"📐 原始图像尺寸: {original_shape[1]}x{original_shape[0]}")
        
        # 预处理流水线
        processed_image = self._preprocessing_pipeline(image)
        
        # 保存优化后的图像
        cv2.imwrite(output_path, processed_image, [
            cv2.IMWRITE_JPEG_QUALITY, self.config.quality
        ])
        
        final_shape = processed_image.shape
        logger.info(f"✅ 预处理完成: {final_shape[1]}x{final_shape[0]} -> {output_path}")
        
        return output_path
    
    def _preprocessing_pipeline(self, image: np.ndarray) -> np.ndarray:
        """预处理流水线"""
        
        # 1. 尺寸优化 - 减少内存占用
        image = self._resize_image(image)
        
        # 2. 颜色空间转换
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 3. 噪声去除
        denoised = self._remove_noise(gray)
        
        # 4. 对比度和亮度增强
        enhanced = self._enhance_contrast_brightness(denoised)
        
        # 5. 锐化处理
        sharpened = self._sharpen_image(enhanced)
        
        # 6. 表格线条增强
        table_enhanced = self._enhance_table_lines(sharpened)
        
        # 7. 手写区域优化
        final_image = self._optimize_handwriting_regions(table_enhanced)
        
        return final_image
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """智能调整图像尺寸"""
        height, width = image.shape[:2]
        
        # 计算缩放比例
        scale_w = self.config.max_width / width
        scale_h = self.config.max_height / height
        scale = min(scale_w, scale_h, 1.0)  # 不放大图像
        
        # 确保最小尺寸
        if width * scale < self.config.min_width:
            scale = self.config.min_width / width
        if height * scale < self.config.min_height:
            scale = self.config.min_height / height
        
        if scale != 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # 使用高质量插值
            image = cv2.resize(
                image, 
                (new_width, new_height), 
                interpolation=cv2.INTER_CUBIC
            )
            logger.info(f"📏 图像缩放: {width}x{height} -> {new_width}x{new_height} (比例: {scale:.2f})")
        
        return image
    
    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """去除噪声"""
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # 非局部均值去噪
        denoised = cv2.fastNlMeansDenoising(
            blurred, 
            None, 
            self.config.denoise_strength, 
            7, 
            21
        )
        
        # 形态学操作去除小噪点
        kernel = np.ones((self.config.morphology_kernel_size, self.config.morphology_kernel_size), np.uint8)
        cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _enhance_contrast_brightness(self, image: np.ndarray) -> np.ndarray:
        """增强对比度和亮度"""
        # 直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        equalized = clahe.apply(image)
        
        # 对比度和亮度调整
        enhanced = cv2.convertScaleAbs(
            equalized,
            alpha=self.config.contrast_factor,
            beta=int(255 * (self.config.brightness_factor - 1))
        )
        
        return enhanced
    
    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """锐化图像"""
        # 拉普拉斯锐化核
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        
        sharpened = cv2.filter2D(image, -1, kernel)
        
        # 混合原图和锐化图
        alpha = self.config.sharpness_factor
        result = cv2.addWeighted(image, 1-alpha, sharpened, alpha, 0)
        
        return result
    
    def _enhance_table_lines(self, image: np.ndarray) -> np.ndarray:
        """增强表格线条"""
        # 检测水平线
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
        
        # 检测垂直线
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
        
        # 合并线条
        table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0)
        
        # 增强线条
        enhanced_lines = cv2.dilate(table_mask, np.ones((2, 2), np.uint8), iterations=1)
        
        # 将增强的线条添加回原图
        result = cv2.addWeighted(image, 0.8, enhanced_lines, 0.2, 0)
        
        return result
    
    def _optimize_handwriting_regions(self, image: np.ndarray) -> np.ndarray:
        """优化手写区域"""
        # 检测文本区域
        text_regions = self._detect_text_regions(image)
        
        # 对每个文本区域进行优化
        result = image.copy()
        
        for region in text_regions:
            x, y, w, h = region
            
            # 提取区域
            roi = image[y:y+h, x:x+w]
            
            # 手写优化处理
            optimized_roi = self._optimize_handwriting_roi(roi)
            
            # 放回原图
            result[y:y+h, x:x+w] = optimized_roi
        
        return result
    
    def _detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """检测文本区域"""
        # 使用MSER检测文本区域
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(image)
        
        # 转换为边界框
        bboxes = []
        for region in regions:
            x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
            
            # 过滤太小的区域
            if w > 20 and h > 10:
                # 添加padding
                padding = self.config.text_region_padding
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(image.shape[1] - x, w + 2 * padding)
                h = min(image.shape[0] - y, h + 2 * padding)
                
                bboxes.append((x, y, w, h))
        
        return bboxes
    
    def _optimize_handwriting_roi(self, roi: np.ndarray) -> np.ndarray:
        """优化手写区域"""
        # 二值化
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作连接断开的笔画
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 去除小噪点
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        cleaned = cv2.morphologyEx(connected, cv2.MORPH_OPEN, kernel)
        
        return cleaned
    
    def create_multiple_versions(self, image_path: str) -> List[str]:
        """
        创建多个预处理版本用于不同OCR引擎
        
        Returns:
            List[str]: 不同预处理版本的文件路径
        """
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        versions = []
        
        # 版本1: 标准预处理
        standard_config = PreprocessConfig()
        standard_processor = ImagePreprocessor(standard_config)
        standard_path = f"{base_name}_standard.jpg"
        standard_processor.optimize_for_ocr(image_path, standard_path)
        versions.append(standard_path)
        
        # 版本2: 高对比度版本（适合Tesseract）
        high_contrast_config = PreprocessConfig(
            contrast_factor=1.5,
            brightness_factor=1.0,
            sharpness_factor=1.5
        )
        high_contrast_processor = ImagePreprocessor(high_contrast_config)
        high_contrast_path = f"{base_name}_high_contrast.jpg"
        high_contrast_processor.optimize_for_ocr(image_path, high_contrast_path)
        versions.append(high_contrast_path)
        
        # 版本3: 平滑版本（适合EasyOCR）
        smooth_config = PreprocessConfig(
            contrast_factor=1.1,
            brightness_factor=1.2,
            sharpness_factor=1.0,
            denoise_strength=5
        )
        smooth_processor = ImagePreprocessor(smooth_config)
        smooth_path = f"{base_name}_smooth.jpg"
        smooth_processor.optimize_for_ocr(image_path, smooth_path)
        versions.append(smooth_path)
        
        logger.info(f"✅ 创建了 {len(versions)} 个预处理版本")
        return versions

# 测试函数
def test_preprocessing():
    """测试预处理功能"""
    print("🧪 测试图像预处理器")
    print("=" * 50)
    
    # 测试图像路径
    test_image = "/home/ubuntu/upload/張家銓_1.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图像不存在: {test_image}")
        return
    
    # 创建预处理器
    preprocessor = ImagePreprocessor()
    
    try:
        # 单版本优化
        print("📸 单版本预处理测试...")
        optimized_path = preprocessor.optimize_for_ocr(test_image)
        print(f"✅ 优化完成: {optimized_path}")
        
        # 多版本优化
        print("\n📸 多版本预处理测试...")
        versions = preprocessor.create_multiple_versions(test_image)
        print(f"✅ 创建版本: {versions}")
        
        # 显示文件大小对比
        original_size = os.path.getsize(test_image) / 1024 / 1024
        print(f"\n📊 文件大小对比:")
        print(f"原始图像: {original_size:.2f} MB")
        
        for version in versions:
            if os.path.exists(version):
                size = os.path.getsize(version) / 1024 / 1024
                reduction = (1 - size / original_size) * 100
                print(f"{version}: {size:.2f} MB (减少 {reduction:.1f}%)")
        
    except Exception as e:
        print(f"❌ 预处理测试失败: {e}")

if __name__ == "__main__":
    test_preprocessing()

