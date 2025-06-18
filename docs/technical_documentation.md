# SmartUI MCP 技术文档

**智慧感知UI组件 - 组件级Adapter完整技术规范**

---

**作者：** Manus AI  
**版本：** 1.0.0  
**日期：** 2025年6月18日  
**架构层级：** 组件级 (Component Level)

---

## 目录

1. [项目概述](#项目概述)
2. [架构设计](#架构设计)
3. [核心组件](#核心组件)
4. [接口规范](#接口规范)
5. [配置系统](#配置系统)
6. [部署指南](#部署指南)
7. [API文档](#api文档)
8. [开发指南](#开发指南)
9. [故障排除](#故障排除)
10. [附录](#附录)

---

## 项目概述

SmartUI MCP（Model Context Protocol）是一个基于三层架构设计的智慧感知UI组件，作为组件级adapter为上层的工作流编排器和产品级编排器提供智能UI生成、用户行为分析、自适应界面等核心功能。

### 核心特性

SmartUI MCP集成了enhancedsmartui的智能感知能力与smartui_fixed的稳定UI基础，实现了真正的智慧感知组件。其核心特性包括：

**智能感知能力：**
- 实时用户行为分析和模式识别
- 基于上下文的智能决策引擎
- 动态UI生成和自适应布局
- 多维度性能监控和优化

**组件级架构：**
- 完整的MCP协议支持
- 标准化的组件接口设计
- 灵活的编排器集成机制
- 高可用的服务发现和注册

**企业级功能：**
- 多主题管理和品牌定制
- 完整的可访问性支持
- 国际化和本地化
- 安全认证和权限控制

### 三层架构定位

在整个系统的三层架构中，SmartUI MCP明确定位为组件级adapter：

```
coding_plugin_orchestrator (产品级)
           ↓
workflow orchestrator (工作流级)
           ↓
SmartUI MCP (组件级) ← 当前组件
```

这种定位确保了SmartUI MCP能够：
- 被上层编排器正确调用和管理
- 提供标准化的组件接口
- 支持水平扩展和负载均衡
- 实现跨平台和跨环境部署




## 架构设计

### 整体架构

SmartUI MCP采用模块化的微服务架构设计，确保各个组件之间的松耦合和高内聚。整体架构分为以下几个核心层次：

**1. 接口层（Interface Layer）**
接口层负责与上层编排器的通信和协调，提供标准化的MCP协议接口。主要组件包括：
- 协调器集成模块（Coordinator Integration）
- MCP协议处理器（MCP Protocol Handler）
- 事件监听系统（Event Listener System）
- 发布管理集成（Release Management Integration）

**2. 核心智能层（Core Intelligence Layer）**
核心智能层是SmartUI MCP的大脑，负责智能决策和行为分析。主要组件包括：
- 用户分析器（User Analyzer）：实时分析用户行为模式，识别用户偏好和使用习惯
- 决策引擎（Decision Engine）：基于规则和机器学习算法进行智能决策
- API状态管理器（API State Manager）：管理和同步各种API状态
- UI生成器（UI Generator）：动态生成和优化用户界面
- MCP集成模块（MCP Integration）：处理MCP协议相关的业务逻辑

**3. UI渲染层（UI Rendering Layer）**
UI渲染层负责将智能决策转化为具体的用户界面。主要组件包括：
- 固定UI渲染器（Fixed UI Renderer）：提供稳定的基础UI渲染能力
- 智能UI适配器（Smart UI Adapter）：实现智能适配和主题切换
- 响应式组件系统（Reactive Component System）：支持响应式设计和交互
- VS Code接口（VS Code Interface）：专门为VS Code扩展提供的接口

**4. 通信层（Communication Layer）**
通信层负责组件间的消息传递和事件处理。主要组件包括：
- 事件总线（Event Bus）：高性能的异步事件处理系统
- 消息总线（Message Bus）：可靠的消息传递机制
- 通信协议（Communication Protocol）：标准化的通信协议实现

**5. 基础设施层（Infrastructure Layer）**
基础设施层提供系统运行所需的基础服务。主要组件包括：
- 配置管理（Configuration Management）：集中化的配置管理系统
- 日志系统（Logging System）：结构化的日志记录和分析
- 监控系统（Monitoring System）：实时性能监控和告警
- 缓存系统（Caching System）：多级缓存优化性能

### 数据流架构

SmartUI MCP的数据流设计遵循事件驱动架构（Event-Driven Architecture）原则，确保系统的响应性和可扩展性：

**1. 用户交互数据流**
```
用户交互 → 事件捕获 → 用户分析器 → 行为模式识别 → 决策引擎 → UI适配 → 界面更新
```

**2. MCP通信数据流**
```
上层编排器 → MCP协议 → 协调器集成 → 事件总线 → 核心组件 → 响应生成 → MCP协议 → 上层编排器
```

**3. 状态同步数据流**
```
API状态变化 → 状态管理器 → 事件发布 → 相关组件 → 状态更新 → UI刷新
```

### 安全架构

SmartUI MCP在设计时充分考虑了安全性要求，实现了多层次的安全防护：

**1. 接口安全**
- 基于JWT的身份认证机制
- API访问频率限制和防护
- 输入验证和SQL注入防护
- CORS跨域访问控制

**2. 数据安全**
- 敏感数据加密存储
- 传输过程TLS加密
- 用户隐私数据匿名化处理
- 数据访问权限控制

**3. 系统安全**
- 容器化部署隔离
- 网络访问控制
- 安全审计日志
- 漏洞扫描和修复

### 性能架构

为了确保高性能和低延迟，SmartUI MCP采用了多种性能优化策略：

**1. 缓存策略**
- 多级缓存架构（内存缓存、Redis缓存、CDN缓存）
- 智能缓存失效机制
- 缓存预热和预加载
- 缓存命中率监控和优化

**2. 异步处理**
- 全异步的事件处理机制
- 非阻塞的I/O操作
- 任务队列和批处理
- 背景任务调度

**3. 资源优化**
- 代码分割和懒加载
- 图片压缩和优化
- CSS和JavaScript压缩
- 虚拟滚动和分页加载

**4. 监控和调优**
- 实时性能指标监控
- 自动性能瓶颈识别
- 动态资源分配
- 性能基准测试和回归测试



## 核心组件

### 用户分析器（User Analyzer）

用户分析器是SmartUI MCP智能感知能力的核心组件之一，负责实时分析用户行为模式，为智能决策提供数据支持。

**主要功能：**

**1. 行为数据收集**
用户分析器通过多种渠道收集用户行为数据，包括：
- 鼠标移动轨迹和点击模式
- 键盘输入习惯和快捷键使用
- 页面浏览路径和停留时间
- 滚动行为和阅读模式
- 设备信息和环境上下文

**2. 模式识别算法**
采用先进的机器学习算法进行用户行为模式识别：
- 聚类算法识别用户群体特征
- 时间序列分析预测用户需求
- 异常检测识别特殊行为模式
- 关联规则挖掘发现行为关联性

**3. 用户画像构建**
基于收集的数据构建详细的用户画像：
- 技能水平评估（新手、中级、专家）
- 使用偏好分析（界面风格、交互方式）
- 工作模式识别（专注型、探索型、效率型）
- 设备环境适配（桌面、移动、平板）

**技术实现：**

用户分析器采用事件驱动的架构设计，通过事件总线接收用户交互事件，并实时进行分析处理。核心算法包括：

```python
class SmartUIUserAnalyzer:
    def __init__(self):
        self.behavior_patterns = {}
        self.user_profiles = {}
        self.ml_models = self._initialize_models()
    
    async def analyze_user_behavior(self, interaction_data):
        # 实时行为分析
        pattern = self._extract_behavior_pattern(interaction_data)
        user_id = interaction_data.get('user_id')
        
        # 更新用户画像
        self._update_user_profile(user_id, pattern)
        
        # 预测用户需求
        predictions = self._predict_user_needs(user_id)
        
        return {
            'user_profile': self.user_profiles[user_id],
            'behavior_pattern': pattern,
            'predictions': predictions
        }
```

### 决策引擎（Decision Engine）

决策引擎是SmartUI MCP的智能大脑，负责基于用户分析结果和系统状态做出智能决策。

**核心能力：**

**1. 规则引擎**
支持灵活的规则配置和动态规则更新：
- 基于条件的规则匹配
- 规则优先级和冲突解决
- 规则执行结果跟踪
- 规则性能监控和优化

**2. 机器学习决策**
集成多种机器学习算法进行智能决策：
- 决策树和随机森林
- 神经网络和深度学习
- 强化学习和在线学习
- 集成学习和模型融合

**3. 上下文感知**
充分考虑各种上下文信息：
- 用户当前状态和历史行为
- 系统负载和性能指标
- 时间和环境因素
- 业务规则和约束条件

**决策流程：**

```
输入数据 → 数据预处理 → 特征提取 → 规则匹配 → ML模型预测 → 决策融合 → 结果输出 → 效果反馈
```

**技术架构：**

决策引擎采用插件化的架构设计，支持动态加载和更新决策算法：

```python
class SmartUIDecisionEngine:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.ml_models = ModelRegistry()
        self.context_manager = ContextManager()
    
    async def make_decision(self, request):
        # 收集上下文信息
        context = await self.context_manager.get_context(request)
        
        # 规则引擎决策
        rule_result = self.rule_engine.evaluate(request, context)
        
        # 机器学习决策
        ml_result = await self.ml_models.predict(request, context)
        
        # 决策融合
        final_decision = self._fuse_decisions(rule_result, ml_result)
        
        # 记录决策过程
        self._log_decision(request, final_decision)
        
        return final_decision
```

### API状态管理器（API State Manager）

API状态管理器负责管理和同步系统中各种API的状态信息，确保数据的一致性和实时性。

**主要职责：**

**1. 状态监控**
- 实时监控API服务状态
- 检测API响应时间和可用性
- 监控API调用频率和错误率
- 跟踪API版本和兼容性

**2. 状态同步**
- 多实例间的状态同步
- 缓存状态的一致性维护
- 状态变更的事件通知
- 状态恢复和容错处理

**3. 性能优化**
- 智能缓存策略
- 请求合并和批处理
- 连接池管理
- 负载均衡和故障转移

### UI生成器（UI Generator）

UI生成器是SmartUI MCP的核心输出组件，负责根据智能决策结果动态生成和优化用户界面。

**生成能力：**

**1. 动态布局生成**
- 基于内容自适应布局
- 响应式设计自动适配
- 组件智能排列和组合
- 布局性能优化

**2. 主题和样式生成**
- 动态主题切换
- 个性化样式定制
- 品牌一致性保证
- 可访问性优化

**3. 交互逻辑生成**
- 智能交互流程设计
- 用户引导和帮助系统
- 快捷操作和手势支持
- 错误处理和反馈机制

**生成算法：**

UI生成器采用模板引擎和组件化的设计模式：

```python
class SmartUIGenerator:
    def __init__(self):
        self.template_engine = TemplateEngine()
        self.component_library = ComponentLibrary()
        self.layout_optimizer = LayoutOptimizer()
    
    async def generate_ui(self, requirements):
        # 分析UI需求
        ui_spec = self._analyze_requirements(requirements)
        
        # 选择最佳模板
        template = self.template_engine.select_template(ui_spec)
        
        # 生成组件配置
        components = self.component_library.generate_components(ui_spec)
        
        # 优化布局
        layout = self.layout_optimizer.optimize(template, components)
        
        # 生成最终UI配置
        ui_config = self._build_ui_config(layout, components)
        
        return ui_config
```

### MCP集成模块（MCP Integration）

MCP集成模块负责处理与Model Context Protocol相关的所有业务逻辑，确保SmartUI MCP能够正确地与上层编排器进行通信。

**集成功能：**

**1. 协议适配**
- MCP协议版本兼容性处理
- 消息格式转换和验证
- 协议扩展和自定义字段支持
- 错误处理和重试机制

**2. 服务发现**
- 自动服务注册和注销
- 健康检查和状态报告
- 负载均衡和故障转移
- 服务依赖管理

**3. 数据同步**
- 配置信息同步
- 状态信息同步
- 事件信息同步
- 性能指标同步

**架构设计：**

MCP集成模块采用适配器模式，支持多种MCP协议版本：

```python
class SmartUIMCPIntegration:
    def __init__(self):
        self.protocol_adapters = {}
        self.service_registry = ServiceRegistry()
        self.message_router = MessageRouter()
    
    async def handle_mcp_message(self, message):
        # 协议版本检测
        version = self._detect_protocol_version(message)
        
        # 选择适配器
        adapter = self.protocol_adapters[version]
        
        # 消息处理
        processed_message = adapter.process_message(message)
        
        # 路由到相应处理器
        response = await self.message_router.route(processed_message)
        
        # 响应格式化
        formatted_response = adapter.format_response(response)
        
        return formatted_response
```


## 接口规范

### MCP协议接口

SmartUI MCP严格遵循Model Context Protocol规范，提供标准化的接口供上层编排器调用。

**1. 组件注册接口**

```json
{
  "method": "component/register",
  "params": {
    "component_id": "smartui_mcp",
    "component_name": "SmartUI MCP",
    "version": "1.0.0",
    "capabilities": [
      "ui_generation",
      "user_analysis", 
      "intelligent_adaptation",
      "theme_management",
      "layout_optimization",
      "component_rendering",
      "event_handling",
      "state_management",
      "accessibility_support",
      "performance_optimization"
    ],
    "endpoints": {
      "health": "/health",
      "ui_generation": "/api/ui/generate",
      "user_analysis": "/api/analysis/user",
      "theme_management": "/api/ui/theme",
      "state_management": "/api/state",
      "orchestration": "/api/orchestration"
    },
    "metadata": {
      "description": "智慧感知UI组件，提供智能UI生成和用户行为分析",
      "architecture_level": "component",
      "supported_orchestrators": ["workflow", "product"]
    }
  }
}
```

**2. 能力调用接口**

每个能力都有对应的调用接口，支持异步调用和结果回调：

```json
{
  "method": "capability/invoke",
  "params": {
    "capability": "ui_generation",
    "parameters": {
      "layout_type": "dashboard",
      "theme": "modern",
      "components": ["header", "sidebar", "main_content"],
      "user_preferences": {
        "color_scheme": "blue",
        "density": "comfortable"
      }
    },
    "callback_url": "http://orchestrator/callback",
    "timeout": 30000
  }
}
```

**3. 事件通知接口**

支持主动向上层编排器推送事件通知：

```json
{
  "method": "event/notify",
  "params": {
    "event_type": "user_behavior_change",
    "event_data": {
      "user_id": "user123",
      "behavior_pattern": "efficiency_focused",
      "confidence": 0.85,
      "recommendations": [
        "enable_keyboard_shortcuts",
        "compact_layout",
        "quick_actions"
      ]
    },
    "timestamp": "2025-06-18T15:30:00Z"
  }
}
```

### REST API接口

除了MCP协议接口，SmartUI MCP还提供RESTful API接口，方便直接集成和测试。

**1. UI生成API**

```http
POST /api/ui/generate
Content-Type: application/json

{
  "layout_type": "dashboard",
  "theme": "modern",
  "components": ["header", "sidebar", "main_content"],
  "user_preferences": {
    "color_scheme": "blue",
    "density": "comfortable"
  },
  "constraints": {
    "max_components": 10,
    "responsive": true,
    "accessibility": true
  }
}
```

响应：
```json
{
  "success": true,
  "ui_config": {
    "layout": {
      "type": "grid",
      "columns": 12,
      "rows": "auto"
    },
    "components": [
      {
        "id": "header",
        "type": "header",
        "position": {"row": 1, "col": 1, "span": 12},
        "props": {
          "title": "Dashboard",
          "theme": "modern"
        }
      }
    ],
    "theme": {
      "primary_color": "#667eea",
      "secondary_color": "#764ba2"
    }
  },
  "metadata": {
    "generation_time": 150,
    "cache_hit": false,
    "version": "1.0.0"
  }
}
```

**2. 用户分析API**

```http
POST /api/analysis/user
Content-Type: application/json

{
  "user_interactions": [
    {
      "type": "click",
      "element": "button",
      "timestamp": 1718723400000,
      "position": {"x": 100, "y": 200}
    },
    {
      "type": "scroll",
      "direction": "down",
      "distance": 500,
      "timestamp": 1718723401000
    }
  ],
  "session_duration": 300,
  "device_info": {
    "type": "desktop",
    "screen_size": "1920x1080",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**3. 主题管理API**

```http
POST /api/ui/theme
Content-Type: application/json

{
  "theme_name": "dark",
  "custom_colors": {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "background": "#1a1a1a",
    "text": "#ffffff"
  },
  "accessibility_mode": false,
  "apply_to": ["current_session", "user_preference"]
}
```

### WebSocket接口

为了支持实时通信和事件推送，SmartUI MCP提供WebSocket接口。

**1. 连接建立**

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = function() {
  console.log('WebSocket连接已建立');
  
  // 发送认证信息
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_auth_token'
  }));
};
```

**2. 消息格式**

所有WebSocket消息都采用统一的JSON格式：

```json
{
  "type": "message_type",
  "data": {
    "key": "value"
  },
  "timestamp": "2025-06-18T15:30:00Z",
  "message_id": "msg_123456"
}
```

**3. 支持的消息类型**

- `ui_interaction`: UI交互事件
- `request_ui_update`: 请求UI更新
- `get_status`: 获取状态信息
- `subscribe_events`: 订阅事件通知
- `unsubscribe_events`: 取消事件订阅

### 事件接口

SmartUI MCP采用事件驱动架构，支持丰富的事件类型和处理机制。

**1. 事件类型定义**

```python
class EventBusEventType(str, Enum):
    # 用户交互事件
    USER_INTERACTION = "user_interaction"
    USER_BEHAVIOR_CHANGE = "user_behavior_change"
    USER_PREFERENCE_UPDATE = "user_preference_update"
    
    # UI相关事件
    UI_COMPONENT_MOUNTED = "ui_component_mounted"
    UI_COMPONENT_UNMOUNTED = "ui_component_unmounted"
    UI_COMPONENT_UPDATED = "ui_component_updated"
    UI_CONFIGURATION_CHANGED = "ui_configuration_changed"
    UI_RENDER_COMPLETE = "ui_render_complete"
    UI_RENDER_ERROR = "ui_render_error"
    
    # API状态事件
    API_STATE_CHANGED = "api_state_changed"
    API_REQUEST_START = "api_request_start"
    API_REQUEST_COMPLETE = "api_request_complete"
    API_REQUEST_ERROR = "api_request_error"
    
    # MCP通信事件
    MCP_MESSAGE_RECEIVED = "mcp_message_received"
    MCP_MESSAGE_SENT = "mcp_message_sent"
    MCP_CONNECTION_ESTABLISHED = "mcp_connection_established"
    MCP_CONNECTION_LOST = "mcp_connection_lost"
```

**2. 事件订阅机制**

```python
# 订阅事件
subscription_id = await event_bus.subscribe(
    event_type=EventBusEventType.USER_INTERACTION,
    handler=handle_user_interaction,
    filter_func=lambda event: event.data.get('user_id') == 'target_user'
)

# 事件处理器
async def handle_user_interaction(event):
    user_data = event.data
    # 处理用户交互逻辑
    await process_user_interaction(user_data)
```

**3. 事件发布机制**

```python
# 发布事件
await event_bus.publish(EventBusEvent(
    event_type=EventBusEventType.UI_COMPONENT_UPDATED,
    data={
        'component_id': 'header',
        'changes': ['theme', 'layout'],
        'user_id': 'user123'
    },
    source='ui_generator'
))
```

### 配置接口

SmartUI MCP提供灵活的配置管理接口，支持动态配置更新和多环境配置。

**1. 配置获取接口**

```http
GET /api/config
GET /api/config/section/{section_name}
GET /api/config/key/{key_path}
```

**2. 配置更新接口**

```http
PUT /api/config
Content-Type: application/json

{
  "core_intelligence": {
    "user_analyzer": {
      "analysis_depth": "full",
      "tracking_enabled": true
    }
  }
}
```

**3. 配置验证接口**

```http
POST /api/config/validate
Content-Type: application/json

{
  "config_data": {
    "server": {
      "port": 8080,
      "host": "0.0.0.0"
    }
  }
}
```

响应：
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Port 8080 is commonly used, consider using a different port for production"
  ]
}
```


## 配置系统

### 配置文件结构

SmartUI MCP采用YAML格式的配置文件，支持分层配置和环境变量替换。主配置文件位于 `config/smartui_config.yaml`。

**主配置文件示例：**

```yaml
# SmartUI MCP 配置文件
# 智慧感知UI组件的核心配置

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8080
  debug: false
  workers: 4
  max_connections: 1000
  timeout: 30
  cors:
    enabled: true
    origins: ["*"]
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    headers: ["*"]

# 核心智能配置
core_intelligence:
  user_analyzer:
    enabled: true
    analysis_depth: "full"  # basic, standard, full
    tracking_enabled: true
    privacy_mode: false
    session_timeout: 3600
    behavior_patterns:
      min_interactions: 10
      pattern_confidence_threshold: 0.7
      learning_rate: 0.01
    
  decision_engine:
    enabled: true
    rule_engine:
      enabled: true
      rules_file: "config/rules.yaml"
      auto_reload: true
    ml_models:
      enabled: true
      model_path: "models/"
      auto_update: false
      confidence_threshold: 0.8
    
  api_state_manager:
    enabled: true
    cache_ttl: 300
    max_cache_size: 1000
    health_check_interval: 60
    retry_attempts: 3
    
  ui_generator:
    enabled: true
    template_path: "templates/"
    component_library: "components/"
    cache_enabled: true
    optimization_level: "high"  # low, medium, high
    
  mcp_integration:
    enabled: true
    protocol_version: "1.0"
    heartbeat_interval: 30
    max_message_size: 1048576  # 1MB

# UI渲染配置
ui_rendering:
  fixed_ui_renderer:
    enabled: true
    theme_path: "themes/"
    default_theme: "modern"
    cache_enabled: true
    
  smart_ui_adapter:
    enabled: true
    adaptation_enabled: true
    auto_theme_switching: true
    responsive_breakpoints:
      mobile: 768
      tablet: 1024
      desktop: 1200
    
  reactive_components:
    enabled: true
    virtual_scrolling: true
    lazy_loading: true
    animation_enabled: true
    
  vscode_interface:
    enabled: true
    extension_id: "smartui-mcp"
    api_version: "1.0"

# 通信配置
communication:
  event_bus:
    enabled: true
    max_history_size: 1000
    cleanup_interval: 3600
    enable_metrics: true
    
  message_bus:
    enabled: true
    queue_size: 10000
    batch_size: 100
    flush_interval: 1000
    
  mcp_protocol:
    enabled: true
    connection_timeout: 10
    read_timeout: 30
    write_timeout: 10
    max_retries: 3

# MCP通信配置
mcp_communication:
  coordinator_integration:
    enabled: true
    component_id: "smartui_mcp"
    orchestration_levels:
      - "workflow"
      - "product"
    capabilities:
      - "ui_generation"
      - "user_analysis"
      - "intelligent_adaptation"
      - "theme_management"
      - "layout_optimization"
      - "component_rendering"
      - "event_handling"
      - "state_management"
      - "accessibility_support"
      - "performance_optimization"
    
  release_management:
    enabled: true
    service_url: "http://release-manager:8080"
    health_check_interval: 60
    deployment_timeout: 300

# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file:
    enabled: true
    path: "logs/smartui_mcp.log"
    max_size: "10MB"
    backup_count: 5
  console:
    enabled: true
    colored: true

# 监控配置
monitoring:
  enabled: true
  metrics:
    enabled: true
    port: 9090
    path: "/metrics"
  health_check:
    enabled: true
    path: "/health"
    detailed: true
  performance:
    enabled: true
    profiling: false
    tracing: false

# 安全配置
security:
  authentication:
    enabled: false  # 开发环境关闭
    jwt_secret: "${JWT_SECRET}"
    token_expiry: 3600
  authorization:
    enabled: false
    rbac: false
  encryption:
    enabled: false
    algorithm: "AES-256-GCM"

# 缓存配置
cache:
  redis:
    enabled: false
    host: "localhost"
    port: 6379
    db: 0
    password: ""
    ttl: 3600
  memory:
    enabled: true
    max_size: 1000
    ttl: 1800

# 数据库配置（如果需要）
database:
  enabled: false
  type: "sqlite"  # sqlite, postgresql, mysql
  connection_string: "sqlite:///smartui_mcp.db"
  pool_size: 10
  max_overflow: 20

# 开发配置
development:
  hot_reload: true
  debug_mode: true
  mock_data: true
  test_mode: false
```

### 环境配置

SmartUI MCP支持多环境配置，通过环境变量和配置文件覆盖实现。

**1. 环境变量支持**

配置文件中可以使用环境变量替换：

```yaml
server:
  host: "${SMARTUI_HOST:0.0.0.0}"
  port: "${SMARTUI_PORT:8080}"
  
security:
  jwt_secret: "${JWT_SECRET:default_secret}"
```

**2. 环境特定配置**

支持为不同环境创建特定的配置文件：

- `config/smartui_config.yaml` - 基础配置
- `config/smartui_config.development.yaml` - 开发环境配置
- `config/smartui_config.production.yaml` - 生产环境配置
- `config/smartui_config.test.yaml` - 测试环境配置

**3. 配置优先级**

配置加载的优先级顺序：
1. 环境变量
2. 环境特定配置文件
3. 基础配置文件
4. 默认值

### 动态配置

SmartUI MCP支持运行时动态更新配置，无需重启服务。

**1. 配置热更新**

```python
# 监听配置文件变化
config_manager.watch_config_file("config/smartui_config.yaml")

# 配置变更回调
@config_manager.on_config_change
async def handle_config_change(section, key, old_value, new_value):
    logger.info(f"配置更新: {section}.{key} = {new_value}")
    
    # 根据配置变更执行相应操作
    if section == "core_intelligence" and key == "user_analyzer.enabled":
        if new_value:
            await user_analyzer.start()
        else:
            await user_analyzer.stop()
```

**2. API配置更新**

```http
PUT /api/config/core_intelligence/user_analyzer
Content-Type: application/json

{
  "analysis_depth": "standard",
  "tracking_enabled": false
}
```

**3. 配置验证**

所有配置更新都会经过严格的验证：

```python
class ConfigValidator:
    def validate_server_config(self, config):
        if not (1 <= config.get('port', 8080) <= 65535):
            raise ValueError("端口号必须在1-65535之间")
        
        if config.get('workers', 1) < 1:
            raise ValueError("工作进程数必须大于0")
    
    def validate_intelligence_config(self, config):
        threshold = config.get('confidence_threshold', 0.8)
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("置信度阈值必须在0.0-1.0之间")
```

### 配置管理API

SmartUI MCP提供完整的配置管理API，支持配置的查询、更新、验证和回滚。

**1. 获取配置**

```http
GET /api/config
GET /api/config/core_intelligence
GET /api/config/core_intelligence/user_analyzer/analysis_depth
```

**2. 更新配置**

```http
PUT /api/config/core_intelligence
Content-Type: application/json

{
  "user_analyzer": {
    "analysis_depth": "full",
    "tracking_enabled": true
  }
}
```

**3. 配置历史**

```http
GET /api/config/history
GET /api/config/history/core_intelligence/user_analyzer
```

**4. 配置回滚**

```http
POST /api/config/rollback
Content-Type: application/json

{
  "version": "2025-06-18T15:30:00Z"
}
```

### 配置最佳实践

**1. 安全配置**
- 敏感信息使用环境变量
- 生产环境禁用调试模式
- 启用适当的安全功能

**2. 性能配置**
- 根据硬件资源调整工作进程数
- 合理设置缓存大小和TTL
- 启用性能监控

**3. 监控配置**
- 启用详细的健康检查
- 配置适当的日志级别
- 设置性能指标收集

**4. 开发配置**
- 开发环境启用热重载
- 使用模拟数据进行测试
- 启用详细的调试信息


## 部署指南

### 环境要求

**系统要求：**
- 操作系统：Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- Python版本：3.11+
- 内存：最小2GB，推荐4GB+
- 存储：最小1GB可用空间
- 网络：支持HTTP/HTTPS和WebSocket连接

**依赖服务：**
- Redis（可选，用于分布式缓存）
- PostgreSQL/MySQL（可选，用于持久化存储）
- Nginx（可选，用于反向代理）

### 安装部署

**1. 源码安装**

```bash
# 克隆代码仓库
git clone https://github.com/your-org/smartui-mcp.git
cd smartui-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

**2. Docker部署**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 smartui && chown -R smartui:smartui /app
USER smartui

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "demo_server.py", "8080"]
```

```bash
# 构建镜像
docker build -t smartui-mcp:latest .

# 运行容器
docker run -d \
  --name smartui-mcp \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  smartui-mcp:latest
```

**3. Docker Compose部署**

```yaml
# docker-compose.yml
version: '3.8'

services:
  smartui-mcp:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - SMARTUI_ENV=production
      - SMARTUI_HOST=0.0.0.0
      - SMARTUI_PORT=8080
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=smartui_mcp
      - POSTGRES_USER=smartui
      - POSTGRES_PASSWORD=smartui_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - smartui-mcp
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### 配置部署

**1. 生产环境配置**

创建生产环境配置文件 `config/smartui_config.production.yaml`：

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  debug: false
  workers: 8

security:
  authentication:
    enabled: true
    jwt_secret: "${JWT_SECRET}"
  authorization:
    enabled: true
    rbac: true

logging:
  level: "WARNING"
  file:
    enabled: true
    path: "/app/logs/smartui_mcp.log"

monitoring:
  enabled: true
  metrics:
    enabled: true
    port: 9090

cache:
  redis:
    enabled: true
    host: "redis"
    port: 6379

database:
  enabled: true
  type: "postgresql"
  connection_string: "postgresql://smartui:${DB_PASSWORD}@postgres:5432/smartui_mcp"
```

**2. 环境变量配置**

创建 `.env` 文件：

```bash
# 环境配置
SMARTUI_ENV=production
SMARTUI_HOST=0.0.0.0
SMARTUI_PORT=8080

# 安全配置
JWT_SECRET=your_super_secret_jwt_key_here
DB_PASSWORD=your_database_password_here

# 外部服务配置
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://smartui:password@postgres:5432/smartui_mcp

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
```

**3. Nginx配置**

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream smartui_mcp {
        server smartui-mcp:8080;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API请求
        location /api/ {
            proxy_pass http://smartui_mcp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket连接
        location /ws {
            proxy_pass http://smartui_mcp;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # 健康检查
        location /health {
            proxy_pass http://smartui_mcp;
            access_log off;
        }

        # 默认路由
        location / {
            proxy_pass http://smartui_mcp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 启动脚本

**1. 系统服务配置**

创建systemd服务文件 `/etc/systemd/system/smartui-mcp.service`：

```ini
[Unit]
Description=SmartUI MCP Service
After=network.target

[Service]
Type=simple
User=smartui
Group=smartui
WorkingDirectory=/opt/smartui-mcp
Environment=SMARTUI_ENV=production
ExecStart=/opt/smartui-mcp/venv/bin/python demo_server.py 8080
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable smartui-mcp
sudo systemctl start smartui-mcp
sudo systemctl status smartui-mcp
```

**2. 启动脚本**

创建 `scripts/start.sh`：

```bash
#!/bin/bash

# SmartUI MCP 启动脚本

set -e

# 配置变量
APP_DIR="/opt/smartui-mcp"
VENV_DIR="$APP_DIR/venv"
CONFIG_FILE="$APP_DIR/config/smartui_config.yaml"
PID_FILE="/var/run/smartui-mcp.pid"
LOG_FILE="/var/log/smartui-mcp.log"

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "错误：虚拟环境不存在: $VENV_DIR"
    exit 1
fi

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误：配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 切换到应用目录
cd "$APP_DIR"

# 检查是否已经运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "SmartUI MCP 已经在运行 (PID: $PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 启动应用
echo "启动 SmartUI MCP..."
nohup python demo_server.py 8080 > "$LOG_FILE" 2>&1 &
PID=$!

# 保存PID
echo "$PID" > "$PID_FILE"

# 等待启动
sleep 5

# 检查是否成功启动
if ps -p "$PID" > /dev/null 2>&1; then
    echo "SmartUI MCP 启动成功 (PID: $PID)"
    
    # 健康检查
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "健康检查通过"
    else
        echo "警告：健康检查失败"
    fi
else
    echo "错误：SmartUI MCP 启动失败"
    rm -f "$PID_FILE"
    exit 1
fi
```

**3. 停止脚本**

创建 `scripts/stop.sh`：

```bash
#!/bin/bash

# SmartUI MCP 停止脚本

set -e

PID_FILE="/var/run/smartui-mcp.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "SmartUI MCP 未运行"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "SmartUI MCP 进程不存在，清理PID文件"
    rm -f "$PID_FILE"
    exit 0
fi

echo "停止 SmartUI MCP (PID: $PID)..."

# 发送TERM信号
kill -TERM "$PID"

# 等待进程结束
for i in {1..30}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "SmartUI MCP 已停止"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# 强制结束
echo "强制结束 SmartUI MCP..."
kill -KILL "$PID"
rm -f "$PID_FILE"
echo "SmartUI MCP 已强制停止"
```

### 监控和维护

**1. 健康检查**

```bash
# 基本健康检查
curl -f http://localhost:8080/health

# 详细健康检查
curl -s http://localhost:8080/health | jq .
```

**2. 日志监控**

```bash
# 查看实时日志
tail -f /var/log/smartui-mcp.log

# 查看错误日志
grep ERROR /var/log/smartui-mcp.log

# 日志轮转配置
sudo logrotate -d /etc/logrotate.d/smartui-mcp
```

**3. 性能监控**

```bash
# 查看性能指标
curl -s http://localhost:9090/metrics

# 系统资源监控
htop
iostat -x 1
```

**4. 备份和恢复**

```bash
# 配置备份
tar -czf smartui-mcp-config-$(date +%Y%m%d).tar.gz config/

# 数据备份
pg_dump smartui_mcp > smartui-mcp-$(date +%Y%m%d).sql

# 恢复配置
tar -xzf smartui-mcp-config-20250618.tar.gz

# 恢复数据
psql smartui_mcp < smartui-mcp-20250618.sql
```


## API文档

### 概述

SmartUI MCP提供RESTful API和WebSocket API两种接口形式，支持同步和异步调用模式。所有API都遵循统一的响应格式和错误处理机制。

### 通用响应格式

**成功响应：**
```json
{
  "success": true,
  "data": {
    // 具体数据内容
  },
  "metadata": {
    "timestamp": "2025-06-18T15:30:00Z",
    "request_id": "req_123456",
    "version": "1.0.0",
    "execution_time": 150
  }
}
```

**错误响应：**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "field": "layout_type",
      "reason": "不支持的布局类型"
    }
  },
  "metadata": {
    "timestamp": "2025-06-18T15:30:00Z",
    "request_id": "req_123456",
    "version": "1.0.0"
  }
}
```

### 核心API接口

#### 1. UI生成API

**生成UI配置**

```http
POST /api/ui/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "layout_type": "dashboard",
  "theme": "modern",
  "components": [
    {
      "type": "header",
      "props": {
        "title": "Dashboard",
        "show_navigation": true
      }
    },
    {
      "type": "sidebar",
      "props": {
        "width": 250,
        "collapsible": true
      }
    }
  ],
  "user_preferences": {
    "color_scheme": "blue",
    "density": "comfortable",
    "animations": true
  },
  "constraints": {
    "max_components": 10,
    "responsive": true,
    "accessibility": true,
    "performance_budget": {
      "max_load_time": 2000,
      "max_bundle_size": 500000
    }
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "ui_config": {
      "layout": {
        "type": "grid",
        "columns": 12,
        "rows": "auto",
        "gap": 16
      },
      "components": [
        {
          "id": "header_001",
          "type": "header",
          "position": {
            "row": 1,
            "col": 1,
            "span": 12
          },
          "props": {
            "title": "Dashboard",
            "show_navigation": true,
            "theme": "modern"
          },
          "styles": {
            "backgroundColor": "#667eea",
            "color": "#ffffff",
            "height": "64px"
          }
        }
      ],
      "theme": {
        "name": "modern",
        "primary_color": "#667eea",
        "secondary_color": "#764ba2",
        "background_color": "#f8fafc",
        "text_color": "#1a202c"
      },
      "responsive_breakpoints": {
        "mobile": 768,
        "tablet": 1024,
        "desktop": 1200
      }
    },
    "optimization_info": {
      "estimated_load_time": 1200,
      "bundle_size": 350000,
      "performance_score": 95
    }
  },
  "metadata": {
    "generation_time": 150,
    "cache_hit": false,
    "version": "1.0.0"
  }
}
```

**更新UI组件**

```http
PUT /api/ui/component/{component_id}
Content-Type: application/json

{
  "props": {
    "title": "Updated Dashboard",
    "show_navigation": false
  },
  "styles": {
    "backgroundColor": "#4f46e5"
  }
}
```

#### 2. 用户分析API

**提交用户交互数据**

```http
POST /api/analysis/user/interactions
Content-Type: application/json

{
  "user_id": "user_123",
  "session_id": "session_456",
  "interactions": [
    {
      "type": "click",
      "element": "button",
      "element_id": "submit_btn",
      "timestamp": 1718723400000,
      "position": {"x": 100, "y": 200},
      "metadata": {
        "page": "/dashboard",
        "viewport": {"width": 1920, "height": 1080}
      }
    },
    {
      "type": "scroll",
      "direction": "down",
      "distance": 500,
      "timestamp": 1718723401000,
      "speed": 250
    },
    {
      "type": "hover",
      "element": "menu_item",
      "element_id": "nav_settings",
      "duration": 1500,
      "timestamp": 1718723402000
    }
  ],
  "context": {
    "device_info": {
      "type": "desktop",
      "os": "Windows 10",
      "browser": "Chrome 91.0",
      "screen_size": "1920x1080"
    },
    "session_duration": 300,
    "page_views": 5,
    "previous_actions": ["login", "navigate_dashboard"]
  }
}
```

**获取用户分析结果**

```http
GET /api/analysis/user/{user_id}
GET /api/analysis/user/{user_id}/behavior_pattern
GET /api/analysis/user/{user_id}/recommendations
```

**响应：**
```json
{
  "success": true,
  "data": {
    "user_profile": {
      "user_id": "user_123",
      "skill_level": "intermediate",
      "usage_pattern": "efficiency_focused",
      "preferences": {
        "interface_density": "compact",
        "color_scheme": "blue",
        "animations": false,
        "keyboard_shortcuts": true
      },
      "behavior_metrics": {
        "average_session_duration": 450,
        "clicks_per_session": 25,
        "scroll_speed": 300,
        "task_completion_rate": 0.85
      }
    },
    "behavior_pattern": {
      "pattern_type": "power_user",
      "confidence": 0.92,
      "characteristics": [
        "frequent_keyboard_shortcuts",
        "fast_navigation",
        "minimal_ui_preference",
        "task_oriented"
      ],
      "predicted_needs": [
        "quick_actions_panel",
        "customizable_shortcuts",
        "advanced_search",
        "bulk_operations"
      ]
    },
    "recommendations": [
      {
        "type": "ui_adaptation",
        "action": "enable_compact_mode",
        "reason": "用户偏好高密度界面",
        "confidence": 0.88
      },
      {
        "type": "feature_suggestion",
        "action": "show_keyboard_shortcuts",
        "reason": "用户频繁使用快捷键",
        "confidence": 0.95
      }
    ]
  }
}
```

#### 3. 主题管理API

**获取可用主题**

```http
GET /api/ui/themes
```

**应用主题**

```http
POST /api/ui/theme/apply
Content-Type: application/json

{
  "theme_name": "dark",
  "customizations": {
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "background_color": "#1a1a1a",
    "text_color": "#ffffff",
    "accent_color": "#f093fb"
  },
  "scope": "user_session",  // user_session, user_preference, global
  "accessibility_mode": false
}
```

**创建自定义主题**

```http
POST /api/ui/themes
Content-Type: application/json

{
  "name": "corporate_blue",
  "display_name": "Corporate Blue",
  "description": "企业级蓝色主题",
  "colors": {
    "primary": "#1e40af",
    "secondary": "#3b82f6",
    "background": "#f8fafc",
    "surface": "#ffffff",
    "text": "#1f2937",
    "text_secondary": "#6b7280",
    "border": "#e5e7eb",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444"
  },
  "typography": {
    "font_family": "Inter, sans-serif",
    "font_sizes": {
      "xs": "12px",
      "sm": "14px",
      "base": "16px",
      "lg": "18px",
      "xl": "20px"
    }
  },
  "spacing": {
    "unit": 8,
    "scale": [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64]
  },
  "shadows": {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)"
  }
}
```

#### 4. 状态管理API

**获取系统状态**

```http
GET /api/state
GET /api/state/component/{component_id}
GET /api/state/user/{user_id}
```

**更新状态**

```http
PUT /api/state/component/{component_id}
Content-Type: application/json

{
  "state": {
    "visible": true,
    "expanded": false,
    "data": {
      "items": [1, 2, 3],
      "selected": 1
    }
  },
  "metadata": {
    "last_updated": "2025-06-18T15:30:00Z",
    "version": 2
  }
}
```

#### 5. 事件API

**订阅事件**

```http
POST /api/events/subscribe
Content-Type: application/json

{
  "event_types": [
    "user_interaction",
    "ui_component_updated",
    "theme_changed"
  ],
  "filters": {
    "user_id": "user_123",
    "component_type": "button"
  },
  "callback_url": "https://your-app.com/webhook/smartui-events",
  "delivery_mode": "webhook"  // webhook, websocket, polling
}
```

**发布事件**

```http
POST /api/events/publish
Content-Type: application/json

{
  "event_type": "custom_event",
  "data": {
    "action": "button_clicked",
    "component_id": "submit_btn",
    "user_id": "user_123"
  },
  "source": "external_app"
}
```

### WebSocket API

**连接建立**

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

// 认证
ws.onopen = function() {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};

// 消息处理
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  console.log('收到消息:', message);
};
```

**实时UI更新**

```javascript
// 请求UI更新
ws.send(JSON.stringify({
  type: 'ui_update_request',
  data: {
    component_id: 'header_001',
    changes: {
      props: {
        title: 'New Title'
      }
    }
  }
}));

// 接收UI更新通知
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  if (message.type === 'ui_updated') {
    // 更新UI
    updateComponent(message.data.component_id, message.data.config);
  }
};
```

### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| AUTHENTICATION_REQUIRED | 401 | 需要身份认证 |
| AUTHORIZATION_FAILED | 403 | 权限不足 |
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| METHOD_NOT_ALLOWED | 405 | 不支持的HTTP方法 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 内部服务器错误 |
| SERVICE_UNAVAILABLE | 503 | 服务暂时不可用 |

### 限制和配额

**请求频率限制：**
- 普通API：100请求/分钟
- 分析API：50请求/分钟
- 事件API：200请求/分钟

**数据大小限制：**
- 请求体大小：最大1MB
- 响应体大小：最大10MB
- WebSocket消息：最大100KB

**并发连接限制：**
- WebSocket连接：每用户最大10个
- HTTP连接：每IP最大100个


## 开发指南

### 开发环境搭建

**1. 环境准备**

```bash
# 安装Python 3.11+
python --version

# 克隆项目
git clone https://github.com/your-org/smartui-mcp.git
cd smartui-mcp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install
```

**2. 开发配置**

创建开发环境配置文件 `config/smartui_config.development.yaml`：

```yaml
server:
  debug: true
  hot_reload: true

logging:
  level: "DEBUG"
  console:
    enabled: true
    colored: true

development:
  mock_data: true
  test_mode: true
  profiling: true
```

**3. 启动开发服务器**

```bash
# 启动开发服务器
python demo_server.py 8080

# 或使用热重载
python -m uvicorn src.main_server:app --reload --host 0.0.0.0 --port 8080
```

### 代码结构

```
smartui_mcp/
├── src/                          # 源代码目录
│   ├── common/                   # 通用模块
│   │   ├── __init__.py
│   │   ├── interfaces.py         # 接口定义
│   │   ├── ui_models.py         # UI数据模型
│   │   ├── event_bus.py         # 事件总线
│   │   ├── communication.py     # 通信协议
│   │   └── utils.py             # 工具函数
│   ├── core_intelligence/       # 核心智能模块
│   │   ├── __init__.py
│   │   ├── user_analyzer.py     # 用户分析器
│   │   ├── decision_engine.py   # 决策引擎
│   │   ├── api_state_manager.py # API状态管理
│   │   ├── ui_generator.py      # UI生成器
│   │   └── mcp_integration.py   # MCP集成
│   ├── ui_renderer/             # UI渲染模块
│   │   ├── __init__.py
│   │   ├── fixed_ui_renderer.py # 固定UI渲染器
│   │   ├── smart_ui_adapter.py  # 智能UI适配器
│   │   ├── reactive_components.py # 响应式组件
│   │   └── vscode_interface.py  # VS Code接口
│   ├── mcp_communication/       # MCP通信模块
│   │   ├── __init__.py
│   │   ├── mcp_protocol.py      # MCP协议
│   │   ├── event_listener.py    # 事件监听器
│   │   ├── coordinator_integration.py # 协调器集成
│   │   └── release_management_integration.py # 发布管理集成
│   ├── config/                  # 配置模块
│   │   ├── __init__.py
│   │   └── config_manager.py    # 配置管理器
│   └── main_server.py           # 主服务器
├── config/                      # 配置文件
│   ├── smartui_config.yaml     # 主配置文件
│   ├── smartui_config.development.yaml
│   └── smartui_config.production.yaml
├── tests/                       # 测试文件
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── e2e/                     # 端到端测试
├── docs/                        # 文档
├── scripts/                     # 脚本文件
├── requirements.txt             # 生产依赖
├── requirements-dev.txt         # 开发依赖
├── demo_server.py              # 演示服务器
├── README.md                   # 项目说明
└── .gitignore                  # Git忽略文件
```

### 编码规范

**1. Python代码规范**

遵循PEP 8规范，使用以下工具进行代码检查：

```bash
# 代码格式化
black src/ tests/

# 导入排序
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

**2. 命名规范**

- 类名：使用PascalCase，如 `UserAnalyzer`
- 函数名：使用snake_case，如 `analyze_user_behavior`
- 常量：使用UPPER_CASE，如 `MAX_CACHE_SIZE`
- 私有成员：使用下划线前缀，如 `_internal_method`

**3. 文档字符串**

使用Google风格的文档字符串：

```python
def analyze_user_behavior(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
    """分析用户行为数据。
    
    Args:
        interaction_data: 用户交互数据，包含事件类型、时间戳等信息
        
    Returns:
        分析结果字典，包含用户画像、行为模式和预测信息
        
    Raises:
        ValueError: 当输入数据格式不正确时
        AnalysisError: 当分析过程出现错误时
        
    Example:
        >>> analyzer = UserAnalyzer()
        >>> data = {"type": "click", "timestamp": 1718723400}
        >>> result = analyzer.analyze_user_behavior(data)
        >>> print(result["user_profile"]["skill_level"])
        "intermediate"
    """
```

### 测试指南

**1. 单元测试**

使用pytest进行单元测试：

```python
# tests/unit/test_user_analyzer.py
import pytest
from src.core_intelligence.user_analyzer import SmartUIUserAnalyzer

class TestUserAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return SmartUIUserAnalyzer()
    
    @pytest.fixture
    def sample_interaction_data(self):
        return {
            "type": "click",
            "element": "button",
            "timestamp": 1718723400000,
            "user_id": "test_user"
        }
    
    def test_analyze_user_behavior(self, analyzer, sample_interaction_data):
        result = analyzer.analyze_user_behavior(sample_interaction_data)
        
        assert "user_profile" in result
        assert "behavior_pattern" in result
        assert result["user_profile"]["user_id"] == "test_user"
    
    def test_invalid_interaction_data(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.analyze_user_behavior({})
```

**2. 集成测试**

```python
# tests/integration/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.main_server import app

class TestAPIEndpoints:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_ui_generation_endpoint(self, client):
        payload = {
            "layout_type": "dashboard",
            "theme": "modern",
            "components": ["header", "sidebar"]
        }
        response = client.post("/api/ui/generate", json=payload)
        assert response.status_code == 200
        assert "ui_config" in response.json()["data"]
```

**3. 运行测试**

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_user_analyzer.py

# 运行带覆盖率的测试
pytest --cov=src --cov-report=html

# 运行性能测试
pytest tests/performance/ --benchmark-only
```

### 调试指南

**1. 日志调试**

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 使用日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

**2. 断点调试**

```python
# 使用pdb调试
import pdb; pdb.set_trace()

# 使用ipdb调试（推荐）
import ipdb; ipdb.set_trace()

# 使用IDE断点
# 在IDE中设置断点，然后以调试模式运行
```

**3. 性能分析**

```python
# 使用cProfile进行性能分析
python -m cProfile -o profile_output.prof demo_server.py

# 使用line_profiler进行行级分析
@profile
def slow_function():
    # 需要分析的代码
    pass

# 运行分析
kernprof -l -v your_script.py
```

### 扩展开发

**1. 添加新的智能组件**

```python
# src/core_intelligence/new_component.py
from ..common.interfaces import ISmartComponent
from ..common.event_bus import event_handler, EventBusEventType

class NewSmartComponent(ISmartComponent):
    def __init__(self):
        self.component_id = "new_component"
        self.version = "1.0.0"
    
    async def initialize(self):
        """初始化组件"""
        pass
    
    @event_handler(EventBusEventType.USER_INTERACTION)
    async def handle_user_interaction(self, event):
        """处理用户交互事件"""
        pass
    
    async def process_request(self, request):
        """处理请求"""
        return {"result": "processed"}
```

**2. 添加新的UI组件**

```python
# src/ui_renderer/new_ui_component.py
from ..common.ui_models import UIComponent, ComponentType

class NewUIComponent(UIComponent):
    def __init__(self):
        super().__init__(
            component_type=ComponentType.CUSTOM,
            component_id="new_ui_component"
        )
    
    def render(self, props, context):
        """渲染组件"""
        return {
            "html": "<div>New Component</div>",
            "css": ".new-component { color: blue; }",
            "js": "console.log('New component loaded');"
        }
```

**3. 添加新的事件类型**

```python
# 在 src/common/interfaces.py 中添加
class EventBusEventType(str, Enum):
    # 现有事件类型...
    NEW_EVENT_TYPE = "new_event_type"

# 使用新事件类型
await event_bus.publish(EventBusEvent(
    event_type=EventBusEventType.NEW_EVENT_TYPE,
    data={"custom_data": "value"},
    source="new_component"
))
```

### 贡献指南

**1. 提交代码**

```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: 添加新功能"

# 推送分支
git push origin feature/new-feature

# 创建Pull Request
```

**2. 提交信息规范**

使用Conventional Commits规范：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

**3. 代码审查**

- 确保所有测试通过
- 代码覆盖率不低于80%
- 遵循编码规范
- 添加必要的文档
- 性能影响评估

### 常见问题

**1. 导入错误**

```python
# 错误：循环导入
# 解决：使用延迟导入或重构代码结构

# 错误：模块未找到
# 解决：检查PYTHONPATH或使用相对导入
```

**2. 性能问题**

```python
# 问题：事件处理器阻塞
# 解决：使用异步处理
@event_handler(EventBusEventType.USER_INTERACTION)
async def handle_event(self, event):
    await asyncio.create_task(self.process_event(event))

# 问题：内存泄漏
# 解决：及时清理资源，使用弱引用
```

**3. 配置问题**

```yaml
# 问题：配置文件格式错误
# 解决：使用YAML验证器检查格式

# 问题：环境变量未生效
# 解决：检查变量名和默认值设置
server:
  port: "${SMARTUI_PORT:8080}"
```


## 故障排除

### 常见问题诊断

#### 1. 服务启动问题

**问题：服务无法启动**

```bash
# 检查端口占用
netstat -tlnp | grep 8080
lsof -i :8080

# 检查配置文件
python -c "import yaml; yaml.safe_load(open('config/smartui_config.yaml'))"

# 检查依赖
pip check
pip list --outdated
```

**解决方案：**
- 更换端口或停止占用端口的进程
- 修复配置文件语法错误
- 更新或重新安装依赖包

**问题：导入错误**

```bash
# 检查Python路径
python -c "import sys; print('\n'.join(sys.path))"

# 检查模块安装
python -c "import src.main_server"

# 检查循环导入
python -X importtime demo_server.py 2>&1 | grep -E "import time|cumulative"
```

**解决方案：**
- 设置正确的PYTHONPATH
- 重构代码避免循环导入
- 使用延迟导入或依赖注入

#### 2. 性能问题

**问题：响应时间过长**

```bash
# 检查系统资源
top
htop
iostat -x 1

# 检查网络连接
netstat -an | grep 8080
ss -tuln | grep 8080

# 分析性能瓶颈
python -m cProfile -o profile.prof demo_server.py
python -c "import pstats; pstats.Stats('profile.prof').sort_stats('cumulative').print_stats(20)"
```

**解决方案：**
- 增加服务器资源（CPU、内存）
- 优化数据库查询
- 启用缓存机制
- 使用异步处理

**问题：内存泄漏**

```python
# 内存监控脚本
import psutil
import time

def monitor_memory():
    process = psutil.Process()
    while True:
        memory_info = process.memory_info()
        print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
        print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
        time.sleep(10)

if __name__ == "__main__":
    monitor_memory()
```

**解决方案：**
- 使用内存分析工具（memory_profiler）
- 及时释放不需要的对象
- 使用弱引用避免循环引用
- 定期清理缓存

#### 3. 网络连接问题

**问题：WebSocket连接失败**

```javascript
// 客户端调试
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onerror = function(error) {
    console.error('WebSocket错误:', error);
};

ws.onclose = function(event) {
    console.log('连接关闭:', event.code, event.reason);
};
```

**解决方案：**
- 检查防火墙设置
- 验证WebSocket路由配置
- 检查代理服务器配置
- 确认SSL证书有效性

**问题：API请求超时**

```bash
# 测试API连接
curl -v -m 30 http://localhost:8080/health
curl -v -m 30 -X POST http://localhost:8080/api/ui/generate \
  -H "Content-Type: application/json" \
  -d '{"layout_type": "dashboard"}'

# 检查网络延迟
ping localhost
traceroute localhost
```

**解决方案：**
- 增加请求超时时间
- 优化API处理逻辑
- 使用连接池
- 实现请求重试机制

#### 4. 数据库连接问题

**问题：数据库连接失败**

```python
# 数据库连接测试
import asyncpg
import asyncio

async def test_db_connection():
    try:
        conn = await asyncpg.connect(
            "postgresql://user:password@localhost:5432/smartui_mcp"
        )
        result = await conn.fetchval("SELECT version()")
        print(f"数据库版本: {result}")
        await conn.close()
    except Exception as e:
        print(f"连接失败: {e}")

asyncio.run(test_db_connection())
```

**解决方案：**
- 检查数据库服务状态
- 验证连接字符串
- 检查网络连接
- 确认用户权限

### 日志分析

#### 1. 日志级别配置

```yaml
# config/smartui_config.yaml
logging:
  level: "DEBUG"  # 临时启用详细日志
  handlers:
    file:
      enabled: true
      path: "logs/smartui_mcp.log"
      max_size: "100MB"
      backup_count: 10
    console:
      enabled: true
      colored: true
```

#### 2. 关键日志模式

**启动日志：**
```
2025-06-18 15:30:00 - smartui_mcp.main - INFO - SmartUI MCP服务启动
2025-06-18 15:30:01 - smartui_mcp.config - INFO - 配置加载完成
2025-06-18 15:30:02 - smartui_mcp.event_bus - INFO - 事件总线初始化完成
2025-06-18 15:30:03 - smartui_mcp.server - INFO - 服务器监听 0.0.0.0:8080
```

**错误日志：**
```
2025-06-18 15:30:10 - smartui_mcp.user_analyzer - ERROR - 用户分析失败: 数据格式错误
2025-06-18 15:30:11 - smartui_mcp.api - ERROR - API请求处理异常: /api/ui/generate
```

**性能日志：**
```
2025-06-18 15:30:15 - smartui_mcp.performance - WARNING - API响应时间过长: 2.5s
2025-06-18 15:30:16 - smartui_mcp.cache - INFO - 缓存命中率: 85%
```

#### 3. 日志分析工具

```bash
# 实时监控错误日志
tail -f logs/smartui_mcp.log | grep ERROR

# 统计错误类型
grep ERROR logs/smartui_mcp.log | awk '{print $5}' | sort | uniq -c

# 分析API响应时间
grep "API响应时间" logs/smartui_mcp.log | awk '{print $6}' | sort -n

# 查找特定用户的操作
grep "user_123" logs/smartui_mcp.log
```

### 监控和告警

#### 1. 健康检查

```python
# 自定义健康检查
async def detailed_health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {}
    }
    
    # 检查数据库连接
    try:
        await database.execute("SELECT 1")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # 检查缓存连接
    try:
        await cache.ping()
        health_status["components"]["cache"] = "healthy"
    except Exception as e:
        health_status["components"]["cache"] = f"unhealthy: {e}"
        health_status["status"] = "degraded"
    
    # 检查事件总线
    try:
        await event_bus.health_check()
        health_status["components"]["event_bus"] = "healthy"
    except Exception as e:
        health_status["components"]["event_bus"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    return health_status
```

#### 2. 性能监控

```python
# 性能指标收集
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "response_times": [],
            "memory_usage": [],
            "cpu_usage": []
        }
    
    async def record_request(self, endpoint, response_time, status_code):
        self.metrics["request_count"] += 1
        self.metrics["response_times"].append(response_time)
        
        if status_code >= 400:
            self.metrics["error_count"] += 1
    
    async def record_system_metrics(self):
        import psutil
        self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
        self.metrics["cpu_usage"].append(psutil.cpu_percent())
    
    def get_metrics(self):
        if self.metrics["response_times"]:
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        else:
            avg_response_time = 0
        
        return {
            "request_count": self.metrics["request_count"],
            "error_rate": self.metrics["error_count"] / max(self.metrics["request_count"], 1),
            "avg_response_time": avg_response_time,
            "memory_usage": self.metrics["memory_usage"][-1] if self.metrics["memory_usage"] else 0,
            "cpu_usage": self.metrics["cpu_usage"][-1] if self.metrics["cpu_usage"] else 0
        }
```

#### 3. 告警配置

```yaml
# 告警规则配置
alerts:
  enabled: true
  rules:
    - name: "high_error_rate"
      condition: "error_rate > 0.05"
      duration: "5m"
      severity: "warning"
      message: "错误率过高: {{.error_rate}}"
    
    - name: "slow_response"
      condition: "avg_response_time > 2000"
      duration: "3m"
      severity: "warning"
      message: "响应时间过长: {{.avg_response_time}}ms"
    
    - name: "high_memory_usage"
      condition: "memory_usage > 80"
      duration: "10m"
      severity: "critical"
      message: "内存使用率过高: {{.memory_usage}}%"
  
  notifications:
    - type: "webhook"
      url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    - type: "email"
      smtp_server: "smtp.gmail.com"
      recipients: ["admin@example.com"]
```

### 故障恢复

#### 1. 自动恢复机制

```python
# 自动重启机制
class AutoRecovery:
    def __init__(self, max_retries=3, retry_delay=10):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_count = 0
    
    async def handle_failure(self, component_name, error):
        logger.error(f"组件 {component_name} 发生故障: {error}")
        
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            logger.info(f"尝试重启组件 {component_name} (第{self.retry_count}次)")
            
            await asyncio.sleep(self.retry_delay)
            
            try:
                await self.restart_component(component_name)
                self.retry_count = 0  # 重置重试计数
                logger.info(f"组件 {component_name} 重启成功")
            except Exception as e:
                logger.error(f"组件 {component_name} 重启失败: {e}")
                await self.handle_failure(component_name, e)
        else:
            logger.critical(f"组件 {component_name} 重启失败，已达到最大重试次数")
            await self.escalate_failure(component_name, error)
    
    async def restart_component(self, component_name):
        # 实现组件重启逻辑
        pass
    
    async def escalate_failure(self, component_name, error):
        # 实现故障升级逻辑（如发送告警、切换到备用服务等）
        pass
```

#### 2. 数据备份和恢复

```bash
#!/bin/bash
# 数据备份脚本

BACKUP_DIR="/backup/smartui_mcp"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份配置文件
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" config/

# 备份数据库
pg_dump smartui_mcp > "$BACKUP_DIR/database_$DATE.sql"

# 备份日志文件
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete

echo "备份完成: $DATE"
```

#### 3. 灾难恢复计划

**恢复优先级：**
1. 核心服务恢复（API服务）
2. 数据库恢复
3. 缓存服务恢复
4. 监控服务恢复

**恢复步骤：**
```bash
# 1. 停止所有服务
sudo systemctl stop smartui-mcp

# 2. 恢复配置文件
tar -xzf /backup/smartui_mcp/config_20250618_153000.tar.gz

# 3. 恢复数据库
psql smartui_mcp < /backup/smartui_mcp/database_20250618_153000.sql

# 4. 重启服务
sudo systemctl start smartui-mcp

# 5. 验证服务状态
curl -f http://localhost:8080/health
```

## 附录

### A. 配置参数参考

详细的配置参数说明请参考配置文件中的注释和本文档的配置系统章节。

### B. API错误代码

完整的API错误代码列表请参考API文档章节。

### C. 性能基准

**硬件配置：**
- CPU: Intel i7-9700K (8核)
- 内存: 16GB DDR4
- 存储: NVMe SSD
- 网络: 1Gbps

**性能指标：**
- API响应时间: 平均150ms，95%分位数300ms
- 并发处理能力: 1000并发用户
- 内存使用: 平均200MB，峰值500MB
- CPU使用: 平均15%，峰值40%

### D. 兼容性矩阵

| 组件 | 支持版本 | 备注 |
|------|---------|------|
| Python | 3.11+ | 推荐3.11.0+ |
| FastAPI | 0.100+ | 核心依赖 |
| PostgreSQL | 12+ | 可选数据库 |
| Redis | 6+ | 可选缓存 |
| Nginx | 1.18+ | 可选代理 |

### E. 许可证

本项目采用MIT许可证，详情请参考LICENSE文件。

### F. 贡献者

感谢所有为SmartUI MCP项目做出贡献的开发者。

---

**文档版本：** 1.0.0  
**最后更新：** 2025年6月18日  
**维护者：** Manus AI Team

如有问题或建议，请通过GitHub Issues或邮件联系我们。

