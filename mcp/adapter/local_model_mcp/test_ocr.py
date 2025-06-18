#!/usr/bin/env python3
"""
OCR测试脚本 - 使用Local Model MCP进行OCR识别测试
"""

import asyncio
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.adapter.local_model_mcp.local_model_mcp import LocalModelMCP

async def test_ocr_with_local_model_mcp():
    """使用Local Model MCP进行OCR测试"""
    
    print("🚀 开始OCR测试 - 使用Local Model MCP")
    print("=" * 60)
    
    # 初始化MCP
    mcp = LocalModelMCP()
    
    try:
        # 初始化MCP
        print("📋 初始化Local Model MCP...")
        init_success = await mcp.initialize()
        
        if not init_success:
            print("❌ MCP初始化失败")
            return
        
        print("✅ MCP初始化成功")
        
        # 获取MCP状态
        print("\n📊 MCP状态:")
        status = await mcp.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # 读取测试图像
        image_path = "/home/ubuntu/upload/張家銓_1.jpg"
        print(f"\n📸 读取测试图像: {image_path}")
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        print(f"✅ 图像读取成功，大小: {len(image_data)} bytes")
        
        # 进行OCR识别
        print("\n🔍 开始OCR识别...")
        start_time = time.time()
        
        ocr_result = await mcp.ocr_processing(
            image_data,
            clean_text=True,
            preserve_layout=True
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ OCR处理时间: {processing_time:.2f}秒")
        
        # 输出OCR结果
        print("\n📄 OCR识别结果:")
        print("=" * 60)
        
        if ocr_result["success"]:
            result_data = ocr_result["result"]
            
            print(f"✅ OCR识别成功")
            print(f"🔧 使用引擎: {result_data.get('engine', 'unknown')}")
            print(f"📊 置信度: {result_data.get('confidence', 0):.2f}")
            print(f"⏱️ 处理时间: {result_data.get('processing_time', 0):.2f}秒")
            
            print("\n📝 识别文本:")
            print("-" * 40)
            print(result_data.get('text', ''))
            print("-" * 40)
            
            # 保存结果到文件
            result_file = Path(__file__).parent / "ocr_test_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(ocr_result, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 结果已保存到: {result_file}")
            
        else:
            print(f"❌ OCR识别失败: {ocr_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 关闭MCP
        print("\n🔄 关闭MCP...")
        await mcp.shutdown()
        print("✅ MCP已关闭")

async def test_multiple_ocr_engines():
    """测试多种OCR引擎"""
    
    print("\n🔧 测试多种OCR引擎")
    print("=" * 60)
    
    # 这里可以测试不同的OCR引擎配置
    engines_to_test = ["integrated", "easyocr", "paddleocr", "tesseract"]
    
    for engine in engines_to_test:
        print(f"\n🧪 测试引擎: {engine}")
        print("-" * 30)
        
        # 创建特定引擎的配置
        config_path = Path(__file__).parent / f"config_{engine}.toml"
        
        # 这里可以创建不同引擎的配置文件
        # 然后使用该配置初始化MCP进行测试
        
        print(f"⏭️ {engine} 引擎测试待实现")

if __name__ == "__main__":
    asyncio.run(test_ocr_with_local_model_mcp())
    asyncio.run(test_multiple_ocr_engines())

