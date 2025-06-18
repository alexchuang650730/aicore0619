#!/usr/bin/env python3
"""
简化的Mistral OCR测试 - 验证API连接和基本功能
"""

import asyncio
import aiohttp
import json
import base64

async def test_mistral_api():
    """简化的Mistral API测试"""
    
    api_key = "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"
    base_url = "https://openrouter.ai/api/v1"
    
    # 首先测试文本API
    print("🧪 测试Mistral文本API...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://powerautomation.ai",
        "X-Title": "PowerAutomation OCR Test"
    }
    
    # 简单的文本测试
    text_data = {
        "model": "mistralai/mistral-nemo",
        "messages": [
            {
                "role": "user", 
                "content": "请回复'Mistral API连接成功'"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=text_data
            ) as response:
                
                print(f"📊 响应状态: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"✅ 文本API成功: {content}")
                    
                    # 如果文本API成功，尝试图像API
                    print("\n🖼️ 测试图像API...")
                    await test_image_api(session, headers, base_url)
                    
                else:
                    error_text = await response.text()
                    print(f"❌ 文本API失败: {response.status} - {error_text}")
                    
    except Exception as e:
        print(f"❌ 连接失败: {e}")

async def test_image_api(session, headers, base_url):
    """测试图像API"""
    
    # 创建一个简单的测试图像（小的base64图像）
    # 这是一个1x1像素的透明PNG
    tiny_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    image_data = {
        "model": "mistralai/mistral-nemo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请描述这张图像"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{tiny_image_b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    try:
        async with session.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=image_data
        ) as response:
            
            print(f"📊 图像API响应状态: {response.status}")
            
            if response.status == 200:
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ 图像API成功: {content}")
                print("🎉 Mistral支持图像输入！")
                
            else:
                error_text = await response.text()
                print(f"❌ 图像API失败: {response.status}")
                print(f"📝 错误详情: {error_text}")
                
                # 检查是否是模型不支持图像的问题
                if "does not support" in error_text.lower() or "vision" in error_text.lower():
                    print("💡 提示: mistral-nemo可能不支持图像输入")
                    print("🔍 需要寻找支持视觉的Mistral模型")
                
    except Exception as e:
        print(f"❌ 图像API测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_mistral_api())

