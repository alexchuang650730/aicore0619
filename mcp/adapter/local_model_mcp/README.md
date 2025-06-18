# Local Model MCP - 环境自适应的本地模型MCP适配器

## 🎯 项目概述

Local Model MCP是一个环境自适应的本地模型MCP适配器，支持Qwen 8B和Mistral 12B多模型配置，集成OCR功能。系统能够根据本地GPU、操作系统等条件智能选择本地模型或云端API，实现真正的端云结合。

## ✨ 核心特性

### 🔄 环境自适应端云架构
- **智能环境检测** - 自动检测GPU类型、内存大小、操作系统
- **动态模式切换** - 根据硬件条件智能选择本地/云端模式
- **实时故障转移** - 本地模型失败时自动切换云端API
- **性能优化** - 根据设备能力自动调整模型参数

### 🤖 多模型支持
- **Qwen 8B模型** - 本地Ollama + OpenRouter云端API
- **Mistral 12B模型** - 本地Transformers + OpenRouter云端API
- **任务智能路由** - 根据任务类型自动选择最适合的模型
- **并发处理** - 支持多请求并发处理

### 📸 OCR功能集成
- **多引擎支持** - EasyOCR、PaddleOCR、Tesseract、云端API
- **自动引擎选择** - 根据可用性自动选择最佳OCR引擎
- **图像预处理** - 自动增强、对比度调整、锐化
- **多页文档** - 支持批量处理多页文档

### 🛠️ 完整工具链
- **命令行接口** - 完整的CLI工具，支持所有功能
- **交互模式** - 实时对话和命令执行
- **状态监控** - 实时查看模型和系统状态
- **配置管理** - 灵活的TOML配置系统

## 📁 项目结构

```
mcp/local_model_mcp/
├── __init__.py                    # 模块初始化
├── local_model_mcp.py            # 主MCP适配器
├── config.toml                   # 配置文件
├── cli.py                        # 命令行接口
├── test_local_model_mcp.py       # 完整测试用例
├── models/                       # 模型管理模块
│   ├── __init__.py
│   ├── model_manager.py          # 模型管理器
│   ├── qwen_model.py            # Qwen模型封装
│   └── mistral_model.py         # Mistral模型封装
├── ocr/                         # OCR功能模块
│   ├── __init__.py
│   └── ocr_engine.py           # OCR引擎
└── utils/                       # 工具模块
    ├── __init__.py
    ├── device_utils.py         # 设备检测工具
    └── memory_utils.py         # 内存管理工具
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install aiohttp requests torch transformers

# OCR依赖（可选）
pip install easyocr paddleocr pytesseract pillow

# 本地模型依赖（可选）
# Ollama: https://ollama.ai/
# CUDA/MPS支持根据系统自动检测
```

### 2. 配置设置

编辑 `config.toml` 文件：

```toml
[models.qwen]
enabled = true
cloud_api_key = "your_openrouter_api_key"

[models.mistral]
enabled = true
cloud_api_key = "your_openrouter_api_key"

[ocr]
enabled = true
languages = ["zh", "en"]
```

### 3. 使用CLI

```bash
# 查看状态
python cli.py status

# 文本生成
python cli.py generate "你好，请介绍一下你自己"

# 聊天对话
python cli.py chat "什么是人工智能？"

# OCR识别
python cli.py ocr image.png

# 交互模式
python cli.py interactive
```

### 4. Python API使用

```python
import asyncio
from local_model_mcp import LocalModelMCP

async def main():
    # 创建MCP实例
    mcp = LocalModelMCP("config.toml")
    await mcp.initialize()
    
    # 文本生成
    result = await mcp.text_generation("你好，请介绍一下你自己")
    print(result["response"]["text"])
    
    # 聊天对话
    messages = [{"role": "user", "content": "什么是人工智能？"}]
    result = await mcp.chat_completion(messages)
    print(result["response"]["message"]["content"])
    
    # OCR处理
    with open("image.png", "rb") as f:
        image_data = f.read()
    result = await mcp.ocr_processing(image_data)
    print(result["result"]["text"])
    
    await mcp.shutdown()

asyncio.run(main())
```

## 🔧 环境自适应逻辑

### 设备检测
```
GPU检测 → 
├─ NVIDIA GPU + 8GB+ 内存 → 本地模式优先
├─ Apple Silicon + 12GB+ 内存 → 本地模式优先
├─ CPU + 16GB+ 内存 → 混合模式
└─ 资源不足 → 云端模式
```

### 模型选择
```
任务类型 → 
├─ 对话、代码生成 → Qwen模型
├─ 文档分析、复杂推理 → Mistral模型
└─ OCR处理 → Mistral模型 + OCR引擎
```

### 故障转移
```
本地模型调用 → 
├─ 成功 → 返回结果
├─ 失败 → 自动切换云端API
└─ 云端失败 → 返回错误信息
```

## 🧪 测试

运行完整测试用例：

```bash
python test_local_model_mcp.py
```

测试覆盖：
- ✅ MCP初始化和配置
- ✅ 环境检测和设备识别
- ✅ 模型加载和切换
- ✅ 文本生成和聊天功能
- ✅ OCR引擎和文本识别
- ✅ 错误处理和故障转移
- ✅ 并发处理和性能测试

## 📊 性能特性

### 内存管理
- **智能内存检测** - 自动检测可用内存
- **模型量化** - 4bit/8bit量化减少内存使用
- **自动卸载** - 不活跃模型自动卸载
- **内存清理** - GPU内存自动清理

### 并发处理
- **异步架构** - 全异步处理提高性能
- **并发限制** - 可配置的并发请求数量
- **请求队列** - 智能请求队列管理
- **超时控制** - 可配置的请求超时时间

### 缓存优化
- **模型缓存** - 已加载模型保持在内存中
- **结果缓存** - 可选的结果缓存机制
- **配置缓存** - 配置文件缓存避免重复读取

## 🔒 安全特性

### 输入验证
- **长度限制** - 输入文本长度限制
- **关键词过滤** - 危险关键词过滤
- **格式验证** - 输入格式验证

### API安全
- **密钥管理** - 安全的API密钥管理
- **速率限制** - 可配置的API调用速率限制
- **错误隐藏** - 敏感错误信息隐藏

## 🌐 云端集成

### OpenRouter支持
- **统一API** - 通过OpenRouter访问多种模型
- **自动认证** - API密钥自动管理
- **错误处理** - 完善的云端API错误处理
- **成本控制** - 可配置的使用限制

### 模型映射
```
本地模型 → 云端模型
├─ qwen2.5:8b → qwen/qwen-2.5-72b-instruct
└─ mistralai/Mistral-Nemo-Instruct-2407 → mistralai/mistral-nemo
```

## 📈 监控和日志

### 性能监控
- **响应时间** - 请求响应时间统计
- **成功率** - 请求成功率监控
- **资源使用** - CPU、内存、GPU使用监控
- **模型切换** - 模型切换次数统计

### 日志系统
- **分级日志** - INFO、WARNING、ERROR级别
- **文件日志** - 可配置的日志文件输出
- **性能日志** - 详细的性能分析日志
- **错误追踪** - 完整的错误堆栈追踪

## 🔄 扩展性

### 新模型集成
1. 继承基础模型类
2. 实现初始化和生成方法
3. 添加到模型管理器
4. 更新配置文件

### 新OCR引擎
1. 实现OCR引擎接口
2. 添加到引擎检测逻辑
3. 更新配置选项

### 新功能模块
1. 创建功能模块目录
2. 实现模块接口
3. 集成到主MCP适配器
4. 添加CLI命令支持

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 运行测试
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 🆘 支持

如有问题或建议，请：
1. 查看文档和FAQ
2. 运行测试用例诊断问题
3. 提交Issue描述问题
4. 联系开发团队

---

**Local Model MCP** - 让AI模型使用更智能、更灵活、更可靠！

