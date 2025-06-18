#!/usr/bin/env python3
"""
优化的Mistral OCR测试 - 精确识别单一表单
"""

import asyncio
import aiohttp
import json
import base64
import time

async def test_mistral_ocr_optimized():
    """优化的Mistral OCR测试"""
    
    # API配置
    api_key = "QvgE8rKZ23CTJ2RTHKtdQOmvFlcNObHV"
    base_url = "https://api.mistral.ai/v1"
    model_name = "pixtral-12b-2409"
    
    # 图像路径
    image_path = "/home/ubuntu/upload/張家銓_1.jpg"
    
    # 编码图像
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 优化的OCR提示词
    prompt = """请仔细分析这张台湾保险表单图像，这是一张单一的保险要保书。

请按以下格式提取信息：

**表单基本信息：**
- 列印者：
- 列印时间：
- 条码：

**被保险人信息：**
- 姓名：
- 性别：
- 出生日期：
- 保险年龄：
- 住址：

**保险详情：**
- 保险名称：
- 缴费年期：
- 保险金额：
- 保险费：

**附加契约：**
- 附加契约名称：
- 保险金额：
- 保险费：

请特别注意手写的数字和文字，确保准确识别。只识别这一张表单的内容，不要重复或创造额外信息。"""
    
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
                    "image_url": f"data:image/jpeg;base64,{image_base64}"
                }
            ]
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.0  # 更低的温度确保准确性
    }
    
    print("🎯 优化的Mistral OCR测试...")
    start_time = time.time()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                processing_time = time.time() - start_time
                response_text = await response.text()
                
                print(f"⏱️ 处理时间: {processing_time:.2f}秒")
                print(f"📊 状态码: {response.status}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    content = result['choices'][0]['message']['content']
                    
                    print("✅ Mistral OCR 优化结果!")
                    print("=" * 80)
                    print(content)
                    print("=" * 80)
                    
                    # 保存结果
                    with open("/home/ubuntu/kilocode_integrated_repo/mcp/adapter/local_model_mcp/mistral_ocr_optimized.txt", 'w', encoding='utf-8') as f:
                        f.write(f"Mistral OCR 优化结果 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"处理时间: {processing_time:.2f}秒\n")
                        f.write("=" * 80 + "\n")
                        f.write(content)
                    
                    print(f"\n📄 结果已保存到: mistral_ocr_optimized.txt")
                    
                else:
                    print(f"❌ API错误: {response.status}")
                    print(f"错误信息: {response_text}")
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mistral_ocr_optimized())

