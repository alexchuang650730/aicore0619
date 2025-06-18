#!/usr/bin/env python3
"""
测试完善后的Local Model MCP - OCR Workflow功能
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent.parent.parent))

# 修复导入问题
try:
    from local_model_mcp import LocalModelMCP
    from ocr_workflow_interface import OCRWorkflowRequest
except ImportError:
    # 如果相对导入失败，尝试直接导入
    import importlib.util
    
    # 导入local_model_mcp
    spec = importlib.util.spec_from_file_location("local_model_mcp", current_dir / "local_model_mcp.py")
    local_model_mcp_module = importlib.util.module_from_spec(spec)
    sys.modules["local_model_mcp"] = local_model_mcp_module
    spec.loader.exec_module(local_model_mcp_module)
    LocalModelMCP = local_model_mcp_module.LocalModelMCP
    
    # 导入ocr_workflow_interface
    spec = importlib.util.spec_from_file_location("ocr_workflow_interface", current_dir / "ocr_workflow_interface.py")
    ocr_workflow_module = importlib.util.module_from_spec(spec)
    sys.modules["ocr_workflow_interface"] = ocr_workflow_module
    spec.loader.exec_module(ocr_workflow_module)
    OCRWorkflowRequest = ocr_workflow_module.OCRWorkflowRequest

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ocr_workflow():
    """测试OCR工作流功能"""
    
    print("🚀 开始测试Local Model MCP的OCR Workflow功能")
    print("=" * 80)
    
    try:
        # 1. 初始化Local Model MCP
        print("📦 初始化Local Model MCP...")
        mcp = LocalModelMCP()
        
        if not await mcp.initialize():
            print("❌ Local Model MCP初始化失败")
            return
        
        print("✅ Local Model MCP初始化成功")
        
        # 2. 检查状态
        status = await mcp.get_status()
        print(f"📊 MCP状态: {status['status']}")
        print(f"🔧 支持的功能: {status['capabilities']}")
        
        # 3. 测试图像路径
        test_image = "/home/ubuntu/upload/張家銓_1.jpg"
        
        if not Path(test_image).exists():
            print(f"❌ 测试图像不存在: {test_image}")
            return
        
        print(f"📸 使用测试图像: {test_image}")
        
        # 4. 测试不同的OCR工作流场景
        test_scenarios = [
            {
                "name": "文档OCR (传统OCR)",
                "request": OCRWorkflowRequest(
                    image_path=test_image,
                    task_type="document_ocr",
                    quality_level="medium",
                    privacy_level="normal",
                    language="auto",
                    output_format="structured_json"
                )
            },
            {
                "name": "手写识别 (Mistral OCR)",
                "request": OCRWorkflowRequest(
                    image_path=test_image,
                    task_type="handwriting",
                    quality_level="high",
                    privacy_level="normal",
                    language="zh+en",
                    output_format="structured_json"
                )
            },
            {
                "name": "表格提取 (Mistral OCR)",
                "request": OCRWorkflowRequest(
                    image_path=test_image,
                    task_type="table_extraction",
                    quality_level="high",
                    privacy_level="normal",
                    language="auto",
                    output_format="structured_json"
                )
            },
            {
                "name": "表单处理 (Mistral OCR)",
                "request": OCRWorkflowRequest(
                    image_path=test_image,
                    task_type="form_processing",
                    quality_level="high",
                    privacy_level="normal",
                    language="auto",
                    output_format="markdown"
                )
            },
            {
                "name": "隐私敏感文档 (本地处理)",
                "request": OCRWorkflowRequest(
                    image_path=test_image,
                    task_type="document_ocr",
                    quality_level="medium",
                    privacy_level="sensitive",
                    language="auto",
                    output_format="text"
                )
            }
        ]
        
        # 5. 执行测试场景
        results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🧪 测试场景 {i}: {scenario['name']}")
            print("-" * 60)
            
            start_time = time.time()
            
            try:
                # 执行OCR工作流
                result = await mcp.process_ocr_workflow(scenario['request'])
                
                processing_time = time.time() - start_time
                
                # 显示结果
                print(f"✅ 处理成功: {result.success}")
                print(f"⏱️ 处理时间: {result.processing_time:.2f}s")
                print(f"🎯 使用适配器: {result.adapter_used}")
                print(f"📊 质量分数: {result.quality_score:.2f}")
                print(f"🔍 置信度: {result.confidence:.2f}")
                print(f"📝 文本长度: {len(result.text)} 字符")
                
                if result.text:
                    preview = result.text[:200] + "..." if len(result.text) > 200 else result.text
                    print(f"📄 文本预览: {preview}")
                
                if result.error:
                    print(f"⚠️ 错误信息: {result.error}")
                
                # 保存结果
                results.append({
                    "scenario": scenario['name'],
                    "success": result.success,
                    "processing_time": result.processing_time,
                    "adapter_used": result.adapter_used,
                    "quality_score": result.quality_score,
                    "confidence": result.confidence,
                    "text_length": len(result.text),
                    "error": result.error
                })
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                results.append({
                    "scenario": scenario['name'],
                    "success": False,
                    "error": str(e)
                })
        
        # 6. 生成测试报告
        print("\\n" + "=" * 80)
        print("📊 测试结果汇总")
        print("=" * 80)
        
        successful_tests = sum(1 for r in results if r.get('success', False))
        total_tests = len(results)
        
        print(f"✅ 成功测试: {successful_tests}/{total_tests}")
        print(f"📈 成功率: {successful_tests/total_tests*100:.1f}%")
        
        print("\\n📋 详细结果:")
        print("-" * 80)
        print(f"{'场景':<25} {'成功':<8} {'时间':<10} {'适配器':<20} {'质量':<8}")
        print("-" * 80)
        
        for result in results:
            success_icon = "✅" if result.get('success', False) else "❌"
            processing_time = f"{result.get('processing_time', 0):.2f}s" if result.get('processing_time') else "N/A"
            adapter = result.get('adapter_used', 'N/A')[:18]
            quality = f"{result.get('quality_score', 0):.2f}" if result.get('quality_score') else "N/A"
            
            print(f"{result['scenario']:<25} {success_icon:<8} {processing_time:<10} {adapter:<20} {quality:<8}")
        
        # 7. 检查最终状态
        print("\\n📊 最终MCP状态:")
        final_status = await mcp.get_status()
        print(f"📈 处理的请求数: {final_status['stats']['requests_processed']}")
        print(f"🔄 工作流请求数: {final_status['stats']['workflow_requests']}")
        print(f"⏱️ 平均响应时间: {final_status['stats']['average_response_time']:.2f}s")
        
        # 8. 关闭MCP
        await mcp.shutdown()
        print("\\n🏁 测试完成，MCP已关闭")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        print(f"❌ 测试失败: {e}")

async def test_mistral_ocr_direct():
    """直接测试Mistral OCR引擎"""
    
    print("\\n🤖 直接测试Mistral OCR引擎")
    print("=" * 80)
    
    try:
        from mistral_ocr_engine import MistralOCREngine
        
        # 使用配置的API密钥
        api_key = "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"
        
        async with MistralOCREngine(api_key) as engine:
            test_image = "/home/ubuntu/upload/張家銓_1.jpg"
            
            if not Path(test_image).exists():
                print(f"❌ 测试图像不存在: {test_image}")
                return
            
            print(f"📸 处理图像: {test_image}")
            
            # 测试不同任务类型
            task_types = ["comprehensive", "table_focus", "handwriting_focus", "form_focus"]
            
            for task_type in task_types:
                print(f"\\n🔍 测试任务类型: {task_type}")
                
                try:
                    result = await engine.process_image(test_image, task_type=task_type)
                    
                    print(f"✅ 处理成功")
                    print(f"⏱️ 处理时间: {result.processing_time:.2f}s")
                    print(f"🔍 置信度: {result.confidence:.2f}")
                    print(f"📝 文本长度: {len(result.text)} 字符")
                    
                    if result.text:
                        preview = result.text[:150] + "..." if len(result.text) > 150 else result.text
                        print(f"📄 文本预览: {preview}")
                    
                    if result.structured_data:
                        print(f"📊 结构化数据: {result.structured_data}")
                    
                except Exception as e:
                    print(f"❌ 任务类型 {task_type} 失败: {e}")
        
        print("\\n🏁 Mistral OCR直接测试完成")
        
    except Exception as e:
        print(f"❌ Mistral OCR测试失败: {e}")

if __name__ == "__main__":
    print("🧪 Local Model MCP OCR Workflow 测试套件")
    print("=" * 80)
    
    # 运行测试
    asyncio.run(test_ocr_workflow())
    
    # 运行Mistral OCR直接测试
    asyncio.run(test_mistral_ocr_direct())

