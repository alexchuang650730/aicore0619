#!/usr/bin/env python3
"""
完整的OCR工作流测试 - 使用保险表单图像测试Mistral OCR
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

async def test_mistral_ocr_with_insurance_form():
    """使用保险表单测试Mistral OCR的完整功能"""
    
    print("🏥 保险表单OCR测试 - Mistral Pixtral 12B")
    print("=" * 80)
    
    try:
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
        
        print(f"📸 处理保险表单: {test_image}")
        
        # 编码图像
        with open(test_image, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        print("✅ 图像编码完成")
        
        # 专门针对保险表单的提示词
        prompt = """你是一个专业的保险表单OCR专家，请仔细分析这张保险表单并提取所有信息。

这是一张台湾人寿保险表单，请按照以下要求处理：

1. **表单基本信息**：
   - 表单类型和名称
   - 列印者编号和时间
   - 条码信息

2. **被保险人信息**：
   - 姓名
   - 性别
   - 出生日期
   - 身份证号
   - 地址
   - 电话

3. **保险信息**：
   - 保险名称
   - 保险金额
   - 保险期间
   - 缴费方式

4. **表格数据**：
   - 识别所有表格内容
   - 保持表格结构
   - 提取手写和印刷文字

5. **特殊标记**：
   - 复选框状态
   - 手写签名
   - 日期填写

请以详细的JSON格式返回结果：
```json
{
  "document_type": "保险表单",
  "form_info": {
    "form_name": "",
    "print_number": "",
    "print_time": "",
    "barcode": ""
  },
  "insured_person": {
    "name": "",
    "gender": "",
    "birth_date": "",
    "id_number": "",
    "address": "",
    "phone": ""
  },
  "insurance_details": {
    "insurance_name": "",
    "insurance_amount": "",
    "insurance_period": "",
    "payment_method": ""
  },
  "extracted_text": "完整的文本内容",
  "confidence": 0.95,
  "tables": [],
  "handwritten_content": [],
  "checkboxes": [],
  "signatures": []
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
            "X-Title": "PowerAutomation Insurance OCR"
        }
        
        data = {
            "model": model_name,
            "messages": messages,
            "max_tokens": 6000,  # 增加token限制以获取更完整的结果
            "temperature": 0.1
        }
        
        print("🚀 发送保险表单OCR请求...")
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=180)  # 增加超时时间
            ) as response:
                
                processing_time = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    print("✅ 保险表单OCR处理成功")
                    print(f"⏱️ 处理时间: {processing_time:.2f}s")
                    
                    # 提取响应内容
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        
                        print(f"📝 响应长度: {len(content)} 字符")
                        
                        # 保存完整结果到文件
                        output_file = "/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/insurance_ocr_result.txt"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(f"保险表单OCR结果\\n")
                            f.write(f"处理时间: {processing_time:.2f}s\\n")
                            f.write(f"模型: {model_name}\\n")
                            f.write("=" * 80 + "\\n")
                            f.write(content)
                        
                        print(f"📄 完整结果已保存到: {output_file}")
                        
                        # 显示结果预览
                        print("\\n📋 OCR结果预览:")
                        print("-" * 60)
                        
                        # 尝试解析JSON结果
                        try:
                            # 查找JSON部分
                            json_start = content.find('{')
                            json_end = content.rfind('}') + 1
                            
                            if json_start != -1 and json_end > json_start:
                                json_content = content[json_start:json_end]
                                parsed_result = json.loads(json_content)
                                
                                print("📊 解析的保险表单信息:")
                                print(f"  📋 文档类型: {parsed_result.get('document_type', 'N/A')}")
                                
                                # 表单信息
                                form_info = parsed_result.get('form_info', {})
                                if form_info:
                                    print("  📝 表单信息:")
                                    for key, value in form_info.items():
                                        if value:
                                            print(f"    - {key}: {value}")
                                
                                # 被保险人信息
                                insured = parsed_result.get('insured_person', {})
                                if insured:
                                    print("  👤 被保险人信息:")
                                    for key, value in insured.items():
                                        if value:
                                            print(f"    - {key}: {value}")
                                
                                # 保险详情
                                insurance = parsed_result.get('insurance_details', {})
                                if insurance:
                                    print("  🏥 保险详情:")
                                    for key, value in insurance.items():
                                        if value:
                                            print(f"    - {key}: {value}")
                                
                                # 其他信息
                                confidence = parsed_result.get('confidence', 'N/A')
                                print(f"  🎯 置信度: {confidence}")
                                
                                extracted_text = parsed_result.get('extracted_text', '')
                                if extracted_text:
                                    print(f"  📝 提取文本长度: {len(extracted_text)} 字符")
                                    
                                    # 显示文本预览
                                    preview = extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text
                                    print(f"  📄 文本预览: {preview}")
                                
                                # 保存结构化数据
                                json_output_file = "/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/insurance_ocr_structured.json"
                                with open(json_output_file, 'w', encoding='utf-8') as f:
                                    json.dump(parsed_result, f, ensure_ascii=False, indent=2)
                                
                                print(f"  💾 结构化数据已保存到: {json_output_file}")
                        
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON解析失败: {e}")
                            print("📄 显示原始文本内容:")
                            preview = content[:500] + "..." if len(content) > 500 else content
                            print(preview)
                    
                    else:
                        print("⚠️ 响应格式异常")
                        print(f"完整响应: {result}")
                
                else:
                    error_text = await response.text()
                    print(f"❌ API请求失败: {response.status}")
                    print(f"错误信息: {error_text}")
        
        print("\\n🏁 保险表单OCR测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def test_workflow_routing():
    """测试OCR工作流路由逻辑"""
    
    print("\\n🔄 OCR工作流路由测试")
    print("=" * 80)
    
    # 模拟路由规则
    routing_rules = {
        "task_type": {
            "document_ocr": "local_traditional_ocr",
            "handwriting": "mistral_ocr",
            "table_extraction": "mistral_ocr", 
            "form_processing": "mistral_ocr"
        },
        "quality_level": {
            "high": "mistral_ocr",
            "medium": "local_traditional_ocr",
            "fast": "local_traditional_ocr"
        },
        "privacy_level": {
            "sensitive": "local_traditional_ocr",
            "normal": "mistral_ocr",
            "public": "mistral_ocr"
        }
    }
    
    def select_adapter(task_type, quality_level, privacy_level):
        """模拟适配器选择逻辑"""
        selected_adapter = "local_traditional_ocr"  # 默认
        
        # 任务类型路由
        task_adapter = routing_rules["task_type"].get(task_type)
        if task_adapter:
            selected_adapter = task_adapter
        
        # 质量级别路由
        if quality_level == "high":
            selected_adapter = "mistral_ocr"
        
        # 隐私级别路由
        if privacy_level == "sensitive":
            selected_adapter = "local_traditional_ocr"
        
        return selected_adapter
    
    # 测试场景
    test_scenarios = [
        ("保险表单处理", "form_processing", "high", "normal"),
        ("手写识别", "handwriting", "high", "normal"),
        ("隐私文档", "document_ocr", "medium", "sensitive"),
        ("快速OCR", "document_ocr", "fast", "public"),
        ("表格提取", "table_extraction", "high", "normal")
    ]
    
    print("📋 路由决策测试结果:")
    print("-" * 60)
    print(f"{'场景':<15} {'任务类型':<15} {'质量':<8} {'隐私':<10} {'选择的适配器':<20}")
    print("-" * 60)
    
    for name, task_type, quality, privacy in test_scenarios:
        adapter = select_adapter(task_type, quality, privacy)
        print(f"{name:<15} {task_type:<15} {quality:<8} {privacy:<10} {adapter:<20}")
    
    print("\\n✅ 路由逻辑验证完成")

if __name__ == "__main__":
    print("🧪 完整OCR工作流测试套件")
    print("=" * 80)
    
    # 运行保险表单OCR测试
    asyncio.run(test_mistral_ocr_with_insurance_form())
    
    # 运行路由测试
    asyncio.run(test_workflow_routing())

