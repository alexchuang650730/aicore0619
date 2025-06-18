#!/usr/bin/env python3
"""
轻量级多引擎OCR测试
"""

import asyncio
import logging
import time
from multi_engine_ocr import MultiEngineOCRManager, OCREngine

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def lightweight_test():
    """轻量级测试"""
    print("🚀 开始轻量级多引擎OCR测试")
    print("=" * 60)
    
    # 初始化管理器
    manager = MultiEngineOCRManager()
    
    # 显示引擎状态
    status = manager.get_engine_status()
    print(f"📊 可用引擎数量: {status['total_engines']}")
    print(f"🔧 引擎列表: {status['available_engines']}")
    
    # 测试图像路径
    test_image = "/home/ubuntu/upload/張家銓_1.jpg"
    
    # 分别测试每个引擎（避免并行处理导致内存问题）
    for engine_name in status['available_engines']:
        print(f"\n🔍 测试引擎: {engine_name}")
        print("-" * 40)
        
        try:
            engine_enum = OCREngine(engine_name)
            start_time = time.time()
            
            # 单独测试每个引擎
            result = await manager._process_with_engine(test_image, engine_enum)
            
            processing_time = time.time() - start_time
            
            print(f"✅ 处理完成")
            print(f"⏱️ 处理时间: {processing_time:.2f}秒")
            print(f"📊 置信度: {result.confidence:.2f}")
            print(f"📝 文本长度: {len(result.text)} 字符")
            print(f"📄 文本预览: {result.text[:100]}...")
            
        except Exception as e:
            print(f"❌ 引擎 {engine_name} 测试失败: {e}")
    
    print(f"\n🎉 轻量级测试完成")

if __name__ == "__main__":
    asyncio.run(lightweight_test())

