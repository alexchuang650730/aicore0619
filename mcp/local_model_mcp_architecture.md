## 统一Local Model MCP架构设计

### 🎯 设计目标

创建一个统一的本地模型MCP适配器，整合OCR Mistral功能，支持多模型配置（qwen 8b和mistral 12b），专注功能实现。

### 📋 核心功能需求

#### **1. 多模型支持**
- **Qwen 8B模型** - 通过Ollama运行
- **Mistral 12B模型** - 通过Transformers运行
- **动态模型切换** - 根据任务类型自动选择
- **模型状态管理** - 加载、卸载、健康检查

#### **2. OCR功能集成**
- **文本识别** - 图像到文本转换
- **多语言支持** - 中英文OCR识别
- **格式保持** - 保持原始文档格式
- **批量处理** - 支持多图像处理

#### **3. 统一API接口**
- **标准MCP协议** - 符合PowerAutomation规范
- **OpenAI兼容** - 支持标准chat completion
- **流式响应** - 支持实时文本生成
- **错误处理** - 完善的异常处理机制

### 🏗️ 架构设计

#### **目录结构**
```
mcp/local_model_mcp/
├── __init__.py                    # 模块初始化
├── local_model_mcp.py            # 主MCP适配器
├── config.toml                   # 配置文件
├── models/                       # 模型管理
│   ├── __init__.py
│   ├── qwen_model.py            # Qwen 8B模型封装
│   ├── mistral_model.py         # Mistral 12B模型封装
│   └── model_manager.py         # 模型管理器
├── ocr/                         # OCR功能模块
│   ├── __init__.py
│   ├── ocr_engine.py           # OCR引擎
│   └── text_processor.py       # 文本处理
├── utils/                       # 工具模块
│   ├── __init__.py
│   ├── device_utils.py         # 设备检测
│   └── memory_utils.py         # 内存管理
└── cli.py                      # 命令行接口
```

#### **核心组件设计**

##### **1. LocalModelMCP (主适配器)**
```python
class LocalModelMCP:
    """统一的本地模型MCP适配器"""
    
    def __init__(self, config_path: str = None):
        self.config = self.load_config(config_path)
        self.model_manager = ModelManager(self.config)
        self.ocr_engine = OCREngine(self.config)
        self.current_model = None
        
    async def initialize(self) -> bool:
        """初始化所有组件"""
        
    async def chat_completion(self, messages: List[Dict], model: str = None) -> Dict:
        """聊天完成接口"""
        
    async def text_generation(self, prompt: str, model: str = None) -> Dict:
        """文本生成接口"""
        
    async def ocr_processing(self, image_data: bytes) -> Dict:
        """OCR处理接口"""
        
    async def switch_model(self, model_name: str) -> bool:
        """切换模型"""
```

##### **2. ModelManager (模型管理器)**
```python
class ModelManager:
    """模型管理器 - 统一管理多个本地模型"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.models = {}
        self.active_model = None
        
    async def load_model(self, model_name: str) -> bool:
        """加载指定模型"""
        
    async def unload_model(self, model_name: str) -> bool:
        """卸载指定模型"""
        
    async def get_model_status(self) -> Dict:
        """获取所有模型状态"""
        
    async def auto_select_model(self, task_type: str) -> str:
        """根据任务类型自动选择模型"""
```

##### **3. QwenModel & MistralModel (模型封装)**
```python
class QwenModel:
    """Qwen 8B模型封装 - 基于Ollama"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_name = "qwen2.5:8b"
        self.base_url = "http://localhost:11434"
        
    async def initialize(self) -> bool:
        """初始化Qwen模型"""
        
    async def generate(self, prompt: str, **kwargs) -> Dict:
        """生成文本"""

class MistralModel:
    """Mistral 12B模型封装 - 基于Transformers"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_name = "mistralai/Mistral-Nemo-Instruct-2407"
        self.model = None
        self.tokenizer = None
        
    async def initialize(self) -> bool:
        """初始化Mistral模型"""
        
    async def generate(self, prompt: str, **kwargs) -> Dict:
        """生成文本"""
```

##### **4. OCREngine (OCR引擎)**
```python
class OCREngine:
    """OCR引擎 - 整合现有OCR Mistral功能"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.ocr_model = None
        
    async def initialize(self) -> bool:
        """初始化OCR引擎"""
        
    async def extract_text(self, image_data: bytes) -> Dict:
        """从图像提取文本"""
        
    async def process_document(self, image_list: List[bytes]) -> Dict:
        """处理多页文档"""
```

### 🔧 配置系统设计

#### **config.toml结构**
```toml
[mcp_info]
name = "local_model_mcp"
version = "1.0.0"
description = "统一的本地模型MCP适配器，支持Qwen 8B和Mistral 12B"
type = "local_model_provider"

[models]
default_model = "qwen"
auto_switch = true

[models.qwen]
enabled = true
model_name = "qwen2.5:8b"
base_url = "http://localhost:11434"
max_tokens = 2048
temperature = 0.7

[models.mistral]
enabled = true
model_name = "mistralai/Mistral-Nemo-Instruct-2407"
device = "auto"
load_in_4bit = true
max_tokens = 2048
temperature = 0.7

[ocr]
enabled = true
language = ["zh", "en"]
output_format = "text"
preserve_layout = true

[performance]
max_concurrent_requests = 3
memory_limit_gb = 8
auto_unload_inactive = true
```

### 🧪 测试策略

#### **测试用例设计**
1. **模型加载测试** - 验证Qwen和Mistral模型正确加载
2. **文本生成测试** - 测试两个模型的文本生成能力
3. **模型切换测试** - 验证动态模型切换功能
4. **OCR功能测试** - 测试图像文本识别
5. **并发处理测试** - 验证多请求并发处理
6. **错误处理测试** - 测试各种异常情况
7. **性能基准测试** - 对比两个模型的性能表现

### 📊 实现优先级

1. **Phase 1**: 创建基础MCP适配器框架
2. **Phase 2**: 集成Qwen 8B模型支持
3. **Phase 3**: 集成Mistral 12B模型支持
4. **Phase 4**: 添加OCR功能集成
5. **Phase 5**: 实现模型管理和切换
6. **Phase 6**: 建立完整测试用例

这个架构设计专注于功能实现，确保统一的本地模型管理和OCR功能整合。

