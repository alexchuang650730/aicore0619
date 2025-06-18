# Cloud Search MCP 项目结构

```
cloud_search_mcp/
├── cloud_search_mcp.py          # 核心MCP实现
├── cli.py                       # 命令行接口
├── config.toml                  # 配置文件
├── test_cloud_search_mcp.py     # 测试套件
├── README.md                    # 项目文档
└── __init__.py                  # Python包初始化
```

## 核心文件说明

### cloud_search_mcp.py
- **CloudSearchMCP**: 主MCP类，实现统一的云端视觉搜索接口
- **ModelSelector**: 智能模型选择器，根据任务类型和优先级选择最优模型
- **CloudModelClient**: 云端模型客户端，处理API调用
- **TaskType**: 支持的OCR任务类型枚举
- **CloudModel**: 支持的云端模型枚举

### cli.py
- 命令行接口，支持测试、健康检查、模型列表等功能
- 交互模式，方便调试和测试
- 完整的参数解析和错误处理

### config.toml
- 完整的配置文件模板
- 支持多模型配置
- 路由、监控、安全等设置

### test_cloud_search_mcp.py
- 全面的测试套件
- 包括功能测试、性能测试、错误处理测试
- 自动生成测试报告

## 使用流程

1. **配置API密钥**: 编辑config.toml或设置环境变量
2. **测试连接**: `python cli.py --health-check`
3. **运行OCR**: `python cli.py --test --image test.jpg`
4. **查看统计**: `python cli.py --interactive` -> `stats`

## 集成方式

### 作为Python模块
```python
from cloud_search_mcp import CloudSearchMCP
mcp = CloudSearchMCP("config.toml")
result = await mcp.process_ocr_request(...)
```

### 作为MCP服务
```python
input_data = {"operation": "process_ocr", "params": {...}}
result = mcp.process(input_data)
```

### 与PowerAutomation集成
- 遵循MCP标准接口
- 支持智慧路由系统调用
- 集成标准化日志系统

