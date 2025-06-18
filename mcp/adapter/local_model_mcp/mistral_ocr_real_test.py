#!/usr/bin/env python3
"""
Mistral OCR实际测试 - 使用保险表单图像测试OCR能力
"""

import asyncio
import aiohttp
import json
import base64
import time
from pathlib import Path

async def test_mistral_ocr_with_real_image():
    """使用实际保险表单测试Mistral OCR能力"""
    
    api_key = "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"
    base_url = "https://openrouter.ai/api/v1"
    
    # 查找保险表单图像
    image_path = Path("張家銓_1.jpg")
    if not image_path.exists():
        # 尝试在upload目录中查找
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
        "X-Title": "PowerAutomation OCR Test"
    }
    
    # 测试不同的OCR任务
    ocr_tests = [
        {
            "name": "基础OCR识别",
            "prompt": "请识别这张图像中的所有文字内容，包括印刷体和手写文字。请保持原有的格式和布局。"
        },
        {
            "name": "手写内容识别", 
            "prompt": "请专门识别这张图像中的手写内容，包括姓名、地址、签名等手写部分。"
        },
        {
            "name": "表格结构还原",
            "prompt": "请识别并还原这张图像中的表格结构，包括表头、行列关系和具体内容。请用markdown表格格式输出。"
        },
        {
            "name": "文档信息提取",
            "prompt": "请提取这份保险文档的关键信息，包括：文档类型、保险公司、投保人信息、保险产品名称等。"
        }
    ]
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for test in ocr_tests:
            print(f"\n🧪 测试: {test['name']}")
            print(f"📝 提示词: {test['prompt']}")
            
            start_time = time.time()
            
            request_data = {
                "model": "mistralai/mistral-nemo",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": test['prompt']
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
                "max_tokens": 2048,
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
                        print(f"📝 内容预览: {content[:200]}...")
                        
                        results[test['name']] = {
                            "success": True,
                            "content": content,
                            "processing_time": processing_time,
                            "content_length": len(content)
                        }
                        
                    else:
                        error_text = await response.text()
                        print(f"❌ 失败: {response.status}")
                        print(f"📝 错误: {error_text}")
                        
                        results[test['name']] = {
                            "success": False,
                            "error": error_text,
                            "processing_time": processing_time
                        }
                        
            except Exception as e:
                print(f"❌ 异常: {e}")
                results[test['name']] = {
                    "success": False,
                    "error": str(e),
                    "processing_time": 0
                }
            
            # 避免API限制，稍作延迟
            await asyncio.sleep(2)
    
    # 保存详细结果
    output_file = "mistral_ocr_real_test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 测试完成！详细结果已保存到: {output_file}")
    
    # 生成测试报告
    await generate_test_report(results)

async def generate_test_report(results):
    """生成测试报告"""
    
    report = []
    report.append("# Mistral OCR LLM 实际测试报告")
    report.append(f"\n**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**测试图像**: 台湾银行人寿保险要保书")
    report.append(f"**模型**: mistralai/mistral-nemo")
    
    report.append("\n## 测试结果概览")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r.get('success', False))
    
    report.append(f"- **总测试数**: {total_tests}")
    report.append(f"- **成功测试**: {successful_tests}")
    report.append(f"- **成功率**: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests > 0:
        avg_time = sum(r.get('processing_time', 0) for r in results.values() if r.get('success', False)) / successful_tests
        avg_length = sum(r.get('content_length', 0) for r in results.values() if r.get('success', False)) / successful_tests
        
        report.append(f"- **平均处理时间**: {avg_time:.2f}秒")
        report.append(f"- **平均内容长度**: {avg_length:.0f}字符")
    
    report.append("\n## 详细测试结果")
    
    for test_name, result in results.items():
        report.append(f"\n### {test_name}")
        
        if result.get('success', False):
            report.append(f"- **状态**: ✅ 成功")
            report.append(f"- **处理时间**: {result.get('processing_time', 0):.2f}秒")
            report.append(f"- **内容长度**: {result.get('content_length', 0)}字符")
            
            content = result.get('content', '')
            if len(content) > 500:
                preview = content[:500] + "..."
            else:
                preview = content
                
            report.append(f"- **内容预览**:")
            report.append(f"```")
            report.append(preview)
            report.append(f"```")
            
        else:
            report.append(f"- **状态**: ❌ 失败")
            report.append(f"- **错误**: {result.get('error', 'Unknown error')}")
    
    # 保存报告
    report_content = "\n".join(report)
    with open("mistral_ocr_test_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("📋 测试报告已生成: mistral_ocr_test_report.md")

if __name__ == "__main__":
    asyncio.run(test_mistral_ocr_with_real_image())

