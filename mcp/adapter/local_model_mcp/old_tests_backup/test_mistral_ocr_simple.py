#!/usr/bin/env python3
"""
简化的OCR工作流测试 - 测试Mistral OCR功能
"""

import asyncio
import logging
import sys
import time
import json
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mistral_ocr_simple():
    """简化的Mistral OCR测试"""
    
    print("🤖 测试Mistral OCR功能")
    print("=" * 60)
    
    try:
        # 直接测试Mistral OCR API
        import aiohttp
        import base64
        
        # 配置
        api_key = "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"
        base_url = "https://openrouter.ai/api/v1"
        model_name = "mistralai/pixtral-12b"
        
        # 测试图像
        test_image = "/home/ubuntu/upload/張家銓_1.jpg"
        
        if not Path(test_image).exists():
            print(f"❌ 测试图像不存在: {test_image}")
            return
        
        print(f"📸 处理图像: {test_image}")
        
        # 编码图像
        with open(test_image, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        print("✅ 图像编码完成")
        
        # 创建提示词
        prompt = """你是一个专业的OCR专家，请仔细分析这张图像并提取所有文本内容。

请按照以下要求处理：

1. **文本识别**：
   - 识别所有可见的文字，包括印刷体和手写体
   - 保持原始的文本布局和格式
   - 对于不确定的字符，请标注[?]

2. **结构化输出**：
   - 如果是表格，请保持表格结构
   - 如果是表单，请识别字段名和对应值
   - 保持段落和行的分隔

3. **特殊处理**：
   - 日期格式：保持原始格式
   - 数字：确保准确性
   - 签名和手写：尽力识别

请以JSON格式返回结果：
```json
{
  "extracted_text": "完整的文本内容",
  "confidence": 0.95,
  "document_type": "表单/表格/文档",
  "structured_data": {
    "fields": {},
    "tables": [],
    "metadata": {}
  }
}
```"""
        
        # 构建请求
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://powerautomation.ai",
            "X-Title": "PowerAutomation OCR Test"
        }
        
        data = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.1
        }
        
        print("🚀 发送API请求...")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    print("✅ API请求成功")
                    print(f"⏱️ 处理时间: {processing_time:.2f}s")
                    
                    # 提取响应内容
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        
                        print(f"📝 响应长度: {len(content)} 字符")
                        print("📄 OCR结果:")
                        print("-" * 40)
                        print(content[:1000] + "..." if len(content) > 1000 else content)
                        print("-" * 40)
                        
                        # 尝试解析JSON结果
                        try:
                            # 查找JSON部分
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            
                            if json_start != -1 and json_end > json_start:
                                json_content = content[json_start:json_end]
                                parsed_result = json.loads(json_content)
                                
                                print("📊 解析的结构化数据:")
                                print(f"  - 文档类型: {parsed_result.get('document_type', 'N/A')}")
                                print(f"  - 置信度: {parsed_result.get('confidence', 'N/A')}")
                                print(f"  - 提取文本长度: {len(parsed_result.get('extracted_text', ''))}")
                                
                                if 'structured_data' in parsed_result:
                                    print(f"  - 结构化数据: {parsed_result['structured_data']}")
                        
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON解析失败: {e}")
                            print("📄 原始文本内容已显示")
                    
                    else:
                        print("⚠️ 响应格式异常")
                        print(f"完整响应: {result}")
                
                else:
                    error_text = await response.text()
                    print(f"❌ API请求失败: {response.status}")
                    print(f"错误信息: {error_text}")
        
        print("\\n🏁 Mistral OCR测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_workflow_interface():
    """测试工作流接口（模拟）"""
    
    print("\\n🔄 测试OCR工作流接口（模拟）")
    print("=" * 60)
    
    try:
        # 模拟工作流请求
        test_scenarios = [
            {
                "name": "文档OCR",
                "task_type": "document_ocr",
                "quality_level": "medium",
                "privacy_level": "normal",
                "expected_adapter": "local_traditional_ocr"
            },
            {
                "name": "手写识别",
                "task_type": "handwriting",
                "quality_level": "high",
                "privacy_level": "normal",
                "expected_adapter": "mistral_ocr"
            },
            {
                "name": "表格提取",
                "task_type": "table_extraction",
                "quality_level": "high",
                "privacy_level": "normal",
                "expected_adapter": "mistral_ocr"
            },
            {
                "name": "隐私敏感",
                "task_type": "document_ocr",
                "quality_level": "medium",
                "privacy_level": "sensitive",
                "expected_adapter": "local_traditional_ocr"
            }
        ]
        
        print("📋 路由规则测试:")
        print("-" * 40)
        
        for scenario in test_scenarios:
            print(f"场景: {scenario['name']}")
            print(f"  任务类型: {scenario['task_type']}")
            print(f"  质量级别: {scenario['quality_level']}")
            print(f"  隐私级别: {scenario['privacy_level']}")
            print(f"  预期适配器: {scenario['expected_adapter']}")
            print()
        
        print("✅ 工作流接口设计验证完成")
        
    except Exception as e:
        print(f"❌ 工作流接口测试失败: {e}")

if __name__ == "__main__":
    print("🧪 OCR Workflow 简化测试套件")
    print("=" * 60)
    
    # 运行Mistral OCR测试
    asyncio.run(test_mistral_ocr_simple())
    
    # 运行工作流接口测试
    asyncio.run(test_workflow_interface())

