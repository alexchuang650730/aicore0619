#!/usr/bin/env python3
"""
测试真正的Mistral视觉模型 - Pixtral 12B
"""

import asyncio
import aiohttp
import json
import base64
import time
from pathlib import Path

async def test_pixtral_ocr():
    """测试Mistral Pixtral 12B的OCR能力"""
    
    api_key = "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"
    base_url = "https://openrouter.ai/api/v1"
    
    # 查找保险表单图像
    image_path = Path("/home/ubuntu/upload/張家銓_1.jpg")
    
    if not image_path.exists():
        print("❌ 找不到保险表单图像文件")
        return
    
    print(f"📄 使用图像: {image_path}")
    
    # 读取并编码图像
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_b64 = base64.b64encode(image_data).decode('utf-8')
    
    print(f"📊 图像大小: {len(image_data)} bytes")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://powerautomation.ai",
        "X-Title": "PowerAutomation Pixtral OCR Test"
    }
    
    # 测试Pixtral 12B
    models_to_test = [
        {
            "name": "Mistral Pixtral 12B",
            "model_id": "mistralai/pixtral-12b",
            "description": "Mistral的多模态视觉模型"
        },
        {
            "name": "Google Gemini 2.5 Flash",
            "model_id": "google/gemini-2.5-flash-preview",
            "description": "Google的高性价比视觉模型"
        },
        {
            "name": "OpenAI GPT-4.1 Mini",
            "model_id": "openai/gpt-4.1-mini",
            "description": "OpenAI的轻量级视觉模型"
        }
    ]
    
    # OCR测试任务
    ocr_prompt = """请仔细分析这张台湾银行人寿保险要保书图像，并完成以下任务：

1. **文字识别**: 识别所有可见的文字内容，包括印刷体和手写文字
2. **表格还原**: 识别并还原表格结构，用markdown格式输出
3. **关键信息提取**: 提取重要信息如：
   - 文档类型和标题
   - 保险公司名称
   - 投保人信息（如有手写内容）
   - 重要的条款和说明

请用中文回复，保持原有的格式和布局。"""
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for model_info in models_to_test:
            print(f"\n🧪 测试模型: {model_info['name']}")
            print(f"📝 模型ID: {model_info['model_id']}")
            print(f"📋 描述: {model_info['description']}")
            
            start_time = time.time()
            
            request_data = {
                "model": model_info['model_id'],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": ocr_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 3000,
                "temperature": 0.1
            }
            
            try:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=request_data
                ) as response:
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        print(f"✅ 成功 (耗时: {processing_time:.2f}秒)")
                        print(f"📄 结果长度: {len(content)} 字符")
                        print(f"📝 内容预览: {content[:300]}...")
                        
                        results[model_info['name']] = {
                            "model_id": model_info['model_id'],
                            "success": True,
                            "content": content,
                            "processing_time": processing_time,
                            "content_length": len(content)
                        }
                        
                    else:
                        error_text = await response.text()
                        print(f"❌ 失败: {response.status}")
                        print(f"📝 错误: {error_text}")
                        
                        results[model_info['name']] = {
                            "model_id": model_info['model_id'],
                            "success": False,
                            "error": error_text,
                            "processing_time": processing_time
                        }
                        
            except Exception as e:
                print(f"❌ 异常: {e}")
                results[model_info['name']] = {
                    "model_id": model_info['model_id'],
                    "success": False,
                    "error": str(e),
                    "processing_time": 0
                }
            
            # 避免API限制
            await asyncio.sleep(3)
    
    # 保存结果
    output_file = "pixtral_ocr_comparison_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 测试完成！详细结果已保存到: {output_file}")
    
    # 生成对比报告
    await generate_comparison_report(results)

async def generate_comparison_report(results):
    """生成模型对比报告"""
    
    report = []
    report.append("# 多模态OCR模型对比测试报告")
    report.append(f"\n**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**测试图像**: 台湾银行人寿保险要保书")
    report.append(f"**测试任务**: 文字识别、表格还原、关键信息提取")
    
    report.append("\n## 测试结果概览")
    
    successful_models = [name for name, result in results.items() if result.get('success', False)]
    
    report.append(f"- **测试模型数**: {len(results)}")
    report.append(f"- **成功模型数**: {len(successful_models)}")
    report.append(f"- **成功率**: {len(successful_models)/len(results)*100:.1f}%")
    
    if successful_models:
        # 性能对比
        report.append("\n## 性能对比")
        report.append("| 模型 | 处理时间 | 内容长度 | 状态 |")
        report.append("|------|---------|---------|------|")
        
        for name, result in results.items():
            if result.get('success', False):
                time_str = f"{result.get('processing_time', 0):.2f}s"
                length_str = f"{result.get('content_length', 0)}字符"
                status = "✅ 成功"
            else:
                time_str = f"{result.get('processing_time', 0):.2f}s"
                length_str = "N/A"
                status = "❌ 失败"
            
            report.append(f"| {name} | {time_str} | {length_str} | {status} |")
    
    report.append("\n## 详细测试结果")
    
    for name, result in results.items():
        report.append(f"\n### {name}")
        report.append(f"- **模型ID**: {result.get('model_id', 'N/A')}")
        
        if result.get('success', False):
            report.append(f"- **状态**: ✅ 成功")
            report.append(f"- **处理时间**: {result.get('processing_time', 0):.2f}秒")
            report.append(f"- **内容长度**: {result.get('content_length', 0)}字符")
            
            content = result.get('content', '')
            if len(content) > 1000:
                preview = content[:1000] + "..."
            else:
                preview = content
                
            report.append(f"- **OCR结果**:")
            report.append(f"```")
            report.append(preview)
            report.append(f"```")
            
        else:
            report.append(f"- **状态**: ❌ 失败")
            report.append(f"- **错误**: {result.get('error', 'Unknown error')}")
    
    # 保存报告
    report_content = "\n".join(report)
    with open("pixtral_ocr_comparison_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("📋 对比报告已生成: pixtral_ocr_comparison_report.md")

if __name__ == "__main__":
    asyncio.run(test_pixtral_ocr())

