# Local Model MCP Adapter

## 📁 目录结构

```
mcp/adapter/local_model_mcp/
├── __init__.py                    # 模块初始化
├── local_model_mcp.py            # 主MCP适配器
├── config.toml                   # 配置文件
├── cli.py                        # 命令行接口
├── run.py                        # 启动脚本
├── test_local_model_mcp.py       # 测试用例
├── README.md                     # 项目文档
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

## 🚀 使用方法

### 直接运行
```bash
cd mcp/adapter/local_model_mcp/
python run.py status
python run.py generate "你好"
python run.py interactive
```

### 作为模块导入
```python
from mcp.adapter.local_model_mcp import LocalModelMCP

mcp = LocalModelMCP()
await mcp.initialize()
```

## 🧪 测试

```bash
cd mcp/adapter/local_model_mcp/
python test_local_model_mcp.py
```

## 📋 待添加测试用例

等待用户提供具体的测试用例配置...

