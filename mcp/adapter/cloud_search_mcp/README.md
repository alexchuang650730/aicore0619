# Cloud Search MCP

统一的云端视觉搜索MCP，支持多模型配置化选择，实现智能路由和OCR任务处理。

## 功能特性

### 🤖 多模型支持
- **Google Gemini 2.5 Flash/Pro** - 高性价比，快速处理
- **Anthropic Claude 3.7 Sonnet/Opus** - 高质量文档理解
- **Mistral Pixtral 12B/Large** - 专业OCR能力

### 🎯 OCR任务类型
- **文档OCR** - 通用文档文字识别
- **手写识别** - 手写文字识别和转换
- **表格提取** - 表格结构识别和数据提取
- **表单处理** - 表单字段识别和数据提取
- **多语言OCR** - 多语言混合文档处理
- **结构化数据** - 复杂文档结构分析

### 🧠 智能路由
- **任务类型适配** - 根据任务类型选择最优模型
- **成本优化** - 平衡质量和成本的智能选择
- **降级机制** - 主模型失败时自动切换备用模型
- **性能监控** - 实时监控模型性能和成本

## 安装和配置

### 1. 安装依赖
```bash
pip install aiohttp toml
```

### 2. 配置API密钥
编辑 `config.toml` 文件，设置相应的API密钥：

```toml
[models.gemini_flash]
enabled = true
api_key = "your_gemini_api_key"

[models.claude_sonnet]
enabled = true
api_key = "your_claude_api_key"

[models.pixtral_12b]
enabled = true
api_key = "your_openrouter_api_key"
```

或者设置环境变量：
```bash
export GEMINI_API_KEY="your_gemini_api_key"
export CLAUDE_API_KEY="your_claude_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"
```

## 使用方法

### 命令行接口

#### 1. 测试OCR功能
```bash
# 基本文档OCR
python cli.py --test --image document.jpg

# 手写识别
python cli.py --test --image handwriting.jpg --task-type handwriting_ocr

# 表格提取
python cli.py --test --image table.png --task-type table_extraction

# 指定语言
python cli.py --test --image chinese_doc.jpg --language zh-CN
```

#### 2. 健康检查
```bash
python cli.py --health-check
```

#### 3. 查看支持的模型
```bash
python cli.py --list-models
```

#### 4. 查看MCP能力
```bash
python cli.py --list-capabilities
```

#### 5. 交互模式
```bash
python cli.py --interactive
```

### Python API

```python
import asyncio
from cloud_search_mcp import CloudSearchMCP, TaskType

async def main():
    # 初始化MCP
    mcp = CloudSearchMCP("config.toml")
    
    # 读取图像
    with open("document.jpg", "rb") as f:
        image_data = f.read()
    
    # 处理OCR请求
    result = await mcp.process_ocr_request(
        image_data=image_data,
        task_type="document_ocr",
        language="auto",
        output_format="markdown"
    )
    
    if result["status"] == "success":
        response = result["result"]
        print(f"模型: {response['model_used']}")
        print(f"置信度: {response['confidence']:.2%}")
        print(f"内容: {response['content']}")
    else:
        print(f"错误: {result['message']}")

asyncio.run(main())
```

### MCP标准接口

```python
# 通过MCP标准接口调用
input_data = {
    "operation": "process_ocr",
    "params": {
        "image_data": image_bytes,
        "task_type": "document_ocr",
        "language": "auto"
    }
}

result = mcp.process(input_data)
```

## 配置说明

### 模型配置
每个模型都可以独立配置：

```toml
[models.gemini_flash]
enabled = true                              # 是否启用
model_id = "google/gemini-2.5-flash-preview"  # 模型ID
api_key = "${GEMINI_API_KEY}"               # API密钥
base_url = "https://openrouter.ai/api/v1"   # API基础URL
max_tokens = 4000                           # 最大token数
temperature = 0.1                           # 温度参数
timeout = 30                                # 超时时间(秒)
cost_per_1k_tokens = 0.00000015            # 每1K token成本
quality_score = 0.85                        # 质量评分
speed_score = 0.95                          # 速度评分
```

### 路由配置
```toml
[routing]
enable_smart_routing = true      # 启用智能路由
cost_optimization = true         # 成本优化
quality_threshold = 0.8          # 质量阈值
max_retries = 3                  # 最大重试次数
fallback_enabled = true          # 启用降级机制
```

### OCR设置
```toml
[ocr_settings]
default_language = "auto"        # 默认语言
output_format = "markdown"       # 输出格式
quality_level = "high"           # 质量级别
max_image_size = 10485760        # 最大图像大小(10MB)
```

## 性能优化

### 1. 模型选择策略
- **速度优先**: 选择Gemini Flash
- **成本优先**: 选择Gemini Flash
- **质量优先**: 选择Claude Sonnet
- **平衡模式**: 根据任务类型智能选择

### 2. 任务类型优化
- **文档OCR**: 平衡质量和速度
- **手写识别**: 优先选择高质量模型
- **表格提取**: 优先选择表格处理能力强的模型
- **多语言**: 优先选择多语言支持好的模型

### 3. 成本控制
- 实时监控API调用成本
- 根据预算自动选择合适的模型
- 支持成本上限设置

## 监控和统计

### 实时统计
- 总请求数和成功率
- 各模型使用情况
- 平均处理时间
- 总成本和平均成本

### 健康检查
- 服务状态监控
- 模型可用性检查
- 性能指标统计

## 错误处理

### 自动重试
- API调用失败自动重试
- 支持指数退避策略
- 最大重试次数限制

### 降级机制
- 主模型失败时自动切换备用模型
- 质量不达标时尝试更高质量模型
- 所有模型失败时返回详细错误信息

## 安全和隐私

### API密钥管理
- 支持环境变量配置
- 配置文件中的密钥加密存储
- 运行时内存中的密钥保护

### 数据保护
- 图像数据不会持久化存储
- API调用使用HTTPS加密
- 支持数据保留期限设置

## 扩展和集成

### 与PowerAutomation集成
- 遵循MCP标准接口
- 支持智慧路由系统调用
- 集成标准化日志系统

### 自定义扩展
- 支持新模型的快速集成
- 可扩展的任务类型定义
- 灵活的配置管理系统

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: API错误 401: Unauthorized
   解决: 检查API密钥是否正确设置
   ```

2. **模型不可用**
   ```
   错误: 没有可用的模型
   解决: 检查config.toml中是否有启用的模型
   ```

3. **图像格式不支持**
   ```
   错误: 图像数据解码失败
   解决: 确保图像格式为支持的格式(jpg, png等)
   ```

### 调试模式
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python cli.py --test --image test.jpg
```

## 版本历史

### v1.0.0 (2025-06-15)
- 初始版本发布
- 支持Gemini、Claude、Pixtral模型
- 实现智能路由和降级机制
- 提供完整的CLI接口
- 集成PowerAutomation MCP标准

## 许可证

本项目遵循PowerAutomation项目的许可证条款。

## 贡献

欢迎提交Issue和Pull Request来改进Cloud Search MCP。

## 联系方式

如有问题或建议，请联系PowerAutomation团队。

