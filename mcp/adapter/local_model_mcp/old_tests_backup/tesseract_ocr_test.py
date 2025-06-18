#!/usr/bin/env python3
"""
Tesseract OCR测试 - 测试手写识别和表格还原能力
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import json
import time
from pathlib import Path

def preprocess_image(image_path):
    """图像预处理以提高OCR效果"""
    
    # 使用PIL读取图像
    image = Image.open(image_path)
    
    # 转换为灰度
    if image.mode != 'L':
        image = image.convert('L')
    
    # 增强对比度
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # 锐化
    image = image.filter(ImageFilter.SHARPEN)
    
    # 转换为numpy数组用于OpenCV处理
    img_array = np.array(image)
    
    # 使用OpenCV进行进一步处理
    # 高斯模糊去噪
    img_array = cv2.GaussianBlur(img_array, (1, 1), 0)
    
    # 自适应阈值
    img_array = cv2.adaptiveThreshold(
        img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # 转换回PIL图像
    processed_image = Image.fromarray(img_array)
    
    return processed_image

def test_tesseract_ocr():
    """使用Tesseract进行OCR测试"""
    
    print("🚀 开始Tesseract OCR测试")
    print("=" * 60)
    
    try:
        # 检查Tesseract版本
        version = pytesseract.get_tesseract_version()
        print(f"📦 Tesseract版本: {version}")
        
        # 检查可用语言
        languages = pytesseract.get_languages()
        print(f"🌐 可用语言: {languages}")
        
        # 读取测试图像
        image_path = "/home/ubuntu/upload/張家銓_1.jpg"
        print(f"📸 读取测试图像: {image_path}")
        
        # 原始图像OCR
        print("\n🔍 原始图像OCR识别...")
        original_image = Image.open(image_path)
        start_time = time.time()
        
        # 使用中文+英文识别
        original_text = pytesseract.image_to_string(
            original_image, 
            lang='chi_tra+chi_sim+eng',
            config='--psm 6'
        )
        
        original_time = time.time() - start_time
        print(f"⏱️ 原始图像处理时间: {original_time:.2f}秒")
        
        # 预处理后的图像OCR
        print("\n🔧 预处理后图像OCR识别...")
        processed_image = preprocess_image(image_path)
        start_time = time.time()
        
        processed_text = pytesseract.image_to_string(
            processed_image,
            lang='chi_tra+chi_sim+eng', 
            config='--psm 6'
        )
        
        processed_time = time.time() - start_time
        print(f"⏱️ 预处理图像处理时间: {processed_time:.2f}秒")
        
        # 获取详细信息（包含置信度）
        print("\n📊 获取详细OCR信息...")
        start_time = time.time()
        
        detailed_data = pytesseract.image_to_data(
            processed_image,
            lang='chi_tra+chi_sim+eng',
            config='--psm 6',
            output_type=pytesseract.Output.DICT
        )
        
        detailed_time = time.time() - start_time
        print(f"⏱️ 详细信息处理时间: {detailed_time:.2f}秒")
        
        # 分析结果
        print("\n📄 OCR识别结果分析:")
        print("=" * 60)
        
        print("\n📝 原始图像识别文本:")
        print("-" * 40)
        print(original_text)
        
        print("\n🔧 预处理后识别文本:")
        print("-" * 40)
        print(processed_text)
        
        # 分析详细数据
        analyze_detailed_results(detailed_data)
        
        # 保存结果
        result_data = {
            "tesseract_version": str(version),
            "available_languages": languages,
            "processing_times": {
                "original_image": original_time,
                "processed_image": processed_time,
                "detailed_analysis": detailed_time
            },
            "original_text": original_text,
            "processed_text": processed_text,
            "detailed_data": detailed_data
        }
        
        result_file = Path(__file__).parent / "tesseract_ocr_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细结果已保存到: {result_file}")
        
        return result_data
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_detailed_results(data):
    """分析详细OCR结果"""
    
    print("\n📊 详细OCR分析:")
    print("-" * 40)
    
    # 统计信息
    total_words = len([text for text in data['text'] if text.strip()])
    high_confidence_words = len([conf for conf in data['conf'] if conf > 60])
    medium_confidence_words = len([conf for conf in data['conf'] if 30 <= conf <= 60])
    low_confidence_words = len([conf for conf in data['conf'] if 0 < conf < 30])
    
    print(f"📈 总识别词数: {total_words}")
    print(f"✅ 高置信度词数 (>60): {high_confidence_words}")
    print(f"⚠️ 中置信度词数 (30-60): {medium_confidence_words}")
    print(f"❌ 低置信度词数 (<30): {low_confidence_words}")
    
    # 可能的手写内容（低置信度）
    print("\n✍️ 可能的手写内容 (低置信度):")
    handwritten_candidates = []
    
    for i, (text, conf) in enumerate(zip(data['text'], data['conf'])):
        if text.strip() and conf < 50:  # 低置信度可能是手写
            handwritten_candidates.append({
                "text": text,
                "confidence": conf,
                "position": (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            })
    
    for item in handwritten_candidates[:10]:  # 显示前10个
        print(f"  - '{item['text']}' (置信度: {item['confidence']})")
    
    # 表格结构分析
    print("\n📊 表格结构分析:")
    analyze_table_structure_tesseract(data)

def analyze_table_structure_tesseract(data):
    """基于Tesseract数据分析表格结构"""
    
    # 按行分组
    rows = {}
    for i, (text, top, height) in enumerate(zip(data['text'], data['top'], data['height'])):
        if text.strip():
            row_center = top + height // 2
            
            # 找到最接近的行
            row_key = None
            min_distance = float('inf')
            
            for existing_row in rows.keys():
                distance = abs(row_center - existing_row)
                if distance < 20 and distance < min_distance:
                    min_distance = distance
                    row_key = existing_row
            
            if row_key is None:
                row_key = row_center
                rows[row_key] = []
            
            rows[row_key].append({
                "text": text,
                "confidence": data['conf'][i],
                "left": data['left'][i],
                "top": data['top'][i],
                "width": data['width'][i],
                "height": data['height'][i]
            })
    
    # 按行排序并显示
    sorted_rows = sorted(rows.items())
    print(f"检测到 {len(sorted_rows)} 行内容:")
    
    for i, (y_pos, row_items) in enumerate(sorted_rows[:10]):  # 显示前10行
        # 按X坐标排序
        sorted_items = sorted(row_items, key=lambda x: x["left"])
        row_text = " | ".join([item["text"] for item in sorted_items])
        print(f"  行 {i+1}: {row_text}")

if __name__ == "__main__":
    result = test_tesseract_ocr()

