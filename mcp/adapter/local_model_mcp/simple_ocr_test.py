#!/usr/bin/env python3
"""
简化OCR测试 - 直接使用EasyOCR测试手写识别和表格还原
"""

import cv2
import numpy as np
from PIL import Image
import json
import time
from pathlib import Path

def test_simple_ocr():
    """简化的OCR测试"""
    
    print("🚀 开始简化OCR测试")
    print("=" * 60)
    
    try:
        # 尝试导入EasyOCR
        print("📦 导入EasyOCR...")
        import easyocr
        print("✅ EasyOCR导入成功")
        
        # 初始化EasyOCR
        print("🔧 初始化EasyOCR读取器...")
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        print("✅ EasyOCR读取器初始化成功")
        
        # 读取测试图像
        image_path = "/home/ubuntu/upload/張家銓_1.jpg"
        print(f"📸 读取测试图像: {image_path}")
        
        # 使用PIL读取图像
        image = Image.open(image_path)
        print(f"✅ 图像读取成功，尺寸: {image.size}")
        
        # 转换为numpy数组
        image_np = np.array(image)
        
        # 进行OCR识别
        print("\n🔍 开始OCR识别...")
        start_time = time.time()
        
        results = reader.readtext(image_np, detail=1)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ OCR处理时间: {processing_time:.2f}秒")
        print(f"📊 识别到 {len(results)} 个文本区域")
        
        # 分析识别结果
        print("\n📄 OCR识别结果:")
        print("=" * 60)
        
        all_text = []
        handwritten_text = []
        printed_text = []
        
        for i, (bbox, text, confidence) in enumerate(results):
            print(f"\n区域 {i+1}:")
            print(f"  文本: {text}")
            print(f"  置信度: {confidence:.3f}")
            print(f"  位置: {bbox}")
            
            all_text.append({
                "text": text,
                "confidence": confidence,
                "bbox": bbox,
                "area_id": i+1
            })
            
            # 简单分类：低置信度可能是手写，高置信度可能是印刷
            if confidence < 0.7:
                handwritten_text.append(text)
            else:
                printed_text.append(text)
        
        # 保存详细结果
        result_data = {
            "processing_time": processing_time,
            "total_regions": len(results),
            "all_text": all_text,
            "handwritten_candidates": handwritten_text,
            "printed_candidates": printed_text,
            "full_text": " ".join([item["text"] for item in all_text])
        }
        
        result_file = Path(__file__).parent / "simple_ocr_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 详细结果已保存到: {result_file}")
        
        # 分析手写识别效果
        print("\n✍️ 手写识别分析:")
        print("-" * 40)
        print("可能的手写内容:")
        for text in handwritten_text:
            print(f"  - {text}")
        
        # 分析表格结构
        print("\n📊 表格结构分析:")
        print("-" * 40)
        analyze_table_structure(results)
        
        return result_data
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_table_structure(ocr_results):
    """分析表格结构"""
    
    # 按Y坐标分组（行）
    rows = {}
    for bbox, text, confidence in ocr_results:
        # 计算中心Y坐标
        center_y = (bbox[0][1] + bbox[2][1]) / 2
        
        # 找到最接近的行
        row_key = None
        min_distance = float('inf')
        
        for existing_y in rows.keys():
            distance = abs(center_y - existing_y)
            if distance < 20 and distance < min_distance:  # 20像素容差
                min_distance = distance
                row_key = existing_y
        
        if row_key is None:
            row_key = center_y
            rows[row_key] = []
        
        rows[row_key].append({
            "text": text,
            "confidence": confidence,
            "bbox": bbox,
            "center_x": (bbox[0][0] + bbox[2][0]) / 2
        })
    
    # 按行排序
    sorted_rows = sorted(rows.items())
    
    print(f"检测到 {len(sorted_rows)} 行内容:")
    
    for i, (y_pos, row_items) in enumerate(sorted_rows):
        # 按X坐标排序（列）
        sorted_items = sorted(row_items, key=lambda x: x["center_x"])
        
        row_text = " | ".join([item["text"] for item in sorted_items])
        print(f"  行 {i+1}: {row_text}")
    
    return sorted_rows

if __name__ == "__main__":
    result = test_simple_ocr()

