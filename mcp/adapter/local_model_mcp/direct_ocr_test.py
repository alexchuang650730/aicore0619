#!/usr/bin/env python3
"""
直接OCR测试 - 绕过MCP复杂性，直接使用Tesseract测试
"""

import pytesseract
from PIL import Image
import json
import time
from pathlib import Path

def test_direct_ocr():
    """直接使用Tesseract进行OCR测试"""
    
    print("🚀 开始直接OCR测试")
    print("=" * 60)
    
    try:
        # 读取测试图像
        image_path = "/home/ubuntu/upload/張家銓_1.jpg"
        print(f"📸 读取测试图像: {image_path}")
        
        image = Image.open(image_path)
        print(f"✅ 图像读取成功，尺寸: {image.size}")
        
        # 使用不同的PSM模式测试
        psm_modes = [
            (6, "统一文本块"),
            (4, "单列文本"),
            (3, "完全自动页面分割"),
            (11, "稀疏文本"),
            (12, "稀疏文本OSD")
        ]
        
        results = {}
        
        for psm, description in psm_modes:
            print(f"\n🔍 测试PSM模式 {psm} ({description})...")
            start_time = time.time()
            
            try:
                text = pytesseract.image_to_string(
                    image,
                    lang='chi_tra+chi_sim+eng',
                    config=f'--psm {psm}'
                )
                
                processing_time = time.time() - start_time
                print(f"⏱️ 处理时间: {processing_time:.2f}秒")
                print(f"📝 识别文本长度: {len(text)} 字符")
                
                results[f"psm_{psm}"] = {
                    "description": description,
                    "processing_time": processing_time,
                    "text": text,
                    "text_length": len(text)
                }
                
                # 显示前200个字符
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"📄 文本预览: {preview}")
                
            except Exception as e:
                print(f"❌ PSM {psm} 测试失败: {e}")
                results[f"psm_{psm}"] = {
                    "description": description,
                    "error": str(e)
                }
        
        # 保存结果
        result_file = Path(__file__).parent / "direct_ocr_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 结果已保存到: {result_file}")
        
        # 分析最佳结果
        print("\n📊 结果分析:")
        print("-" * 40)
        
        best_result = None
        best_length = 0
        
        for mode, result in results.items():
            if "text" in result and result["text_length"] > best_length:
                best_length = result["text_length"]
                best_result = (mode, result)
        
        if best_result:
            mode, result = best_result
            print(f"🏆 最佳识别模式: {mode} ({result['description']})")
            print(f"📝 识别文本长度: {result['text_length']} 字符")
            print(f"⏱️ 处理时间: {result['processing_time']:.2f}秒")
        
        return results
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_direct_ocr()

