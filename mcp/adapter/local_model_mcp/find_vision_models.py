#!/usr/bin/env python3
"""
查找支持视觉的模型
"""

import json

def find_vision_models():
    """查找支持视觉的模型"""
    
    with open("models_list.json", "r") as f:
        models_data = json.load(f)
    
    models = models_data.get("data", [])
    
    print(f"📊 总模型数量: {len(models)}")
    
    # 查找Mistral模型
    mistral_models = [m for m in models if "mistral" in m.get("id", "").lower()]
    print(f"\n🔍 Mistral模型数量: {len(mistral_models)}")
    
    for model in mistral_models:
        print(f"- {model.get('id', 'N/A')}: {model.get('name', 'N/A')}")
    
    # 查找支持视觉的模型（通过关键词）
    vision_keywords = ["vision", "visual", "image", "multimodal", "gpt-4", "claude", "gemini"]
    
    vision_models = []
    for model in models:
        model_id = model.get("id", "").lower()
        model_name = model.get("name", "").lower()
        
        if any(keyword in model_id or keyword in model_name for keyword in vision_keywords):
            vision_models.append(model)
    
    print(f"\n👁️ 可能支持视觉的模型数量: {len(vision_models)}")
    
    # 显示前20个视觉模型
    for i, model in enumerate(vision_models[:20]):
        print(f"{i+1:2d}. {model.get('id', 'N/A')}")
        print(f"    名称: {model.get('name', 'N/A')}")
        if 'pricing' in model:
            prompt_price = model['pricing'].get('prompt', 'N/A')
            completion_price = model['pricing'].get('completion', 'N/A')
            print(f"    价格: ${prompt_price}/1M tokens (输入), ${completion_price}/1M tokens (输出)")
        print()
    
    # 查找特定的OCR友好模型
    ocr_friendly = []
    ocr_keywords = ["gpt-4", "claude", "gemini", "vision"]
    
    for model in models:
        model_id = model.get("id", "").lower()
        if any(keyword in model_id for keyword in ocr_keywords):
            ocr_friendly.append(model)
    
    print(f"\n📄 OCR友好模型推荐:")
    for model in ocr_friendly[:10]:
        print(f"- {model.get('id', 'N/A')}")
        print(f"  名称: {model.get('name', 'N/A')}")
        if 'pricing' in model:
            prompt_price = model['pricing'].get('prompt', 'N/A')
            print(f"  价格: ${prompt_price}/1M tokens")
        print()

if __name__ == "__main__":
    find_vision_models()

