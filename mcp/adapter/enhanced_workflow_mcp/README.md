#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型工作流引擎使用文档
Enhanced Workflow Engine Documentation

详细的使用指南和API文档
"""

# 增强型工作流引擎使用文档

## 概述

增强型工作流引擎是PowerAutomation的核心组件，提供了强大的工作流编排、执行和优化功能。

## 核心组件

### 1. EnhancedWorkflowEngine (增强型工作流引擎)

主控制器，负责工作流的整体管理和协调。

```python
from enhanced_workflow_engine import EnhancedWorkflowEngine

# 初始化引擎
engine = EnhancedWorkflowEngine()

# 创建工作流
workflow = engine.create_workflow(
    name="示例工作流",
    description="这是一个示例工作流"
)
```

### 2. DynamicWorkflowGenerator (动态工作流生成器)

根据需求自动生成优化的工作流结构。

```python
from dynamic_workflow_generator import DynamicWorkflowGenerator, WorkflowRequirement, WorkflowTemplate

# 初始化生成器
generator = DynamicWorkflowGenerator()

# 定义需求
requirement = WorkflowRequirement(
    name="数据处理工作流",
    description="处理用户数据的工作流",
    template=WorkflowTemplate.DATA_PROCESSING,
    required_capabilities=["data_validation", "data_transformation"]
)

# 生成工作流
workflow = await generator.generate_workflow(requirement)
```

### 3. ParallelExecutionScheduler (并行执行调度器)

高效的并行任务调度和执行。

```python
from parallel_execution_scheduler import ParallelExecutionScheduler, ExecutionStrategy

# 初始化调度器
scheduler = ParallelExecutionScheduler()

# 配置执行策略
strategy = ExecutionStrategy.PARALLEL

# 执行任务
result = await scheduler.execute_tasks(tasks, strategy)
```

### 4. IntelligentDependencyManager (智能依赖管理器)

复杂依赖关系的智能分析和管理。

```python
from intelligent_dependency_manager import IntelligentDependencyManager, DependencyType

# 初始化依赖管理器
dep_manager = IntelligentDependencyManager()

# 添加依赖关系
await dep_manager.add_dependency(
    source_node="task1",
    target_node="task2", 
    dependency_type=DependencyType.DATA
)

# 检测冲突
conflicts = await dep_manager._detect_conflicts()
```

### 5. WorkflowStateManager (工作流状态管理器)

完整的工作流状态持久化和管理。

```python
from workflow_state_manager import WorkflowStateManager

# 初始化状态管理器
state_manager = WorkflowStateManager()

# 创建工作流状态
state_manager.create_workflow_state(workflow_id, initial_state)

# 更新状态
state_manager.update_workflow_state(workflow_id, new_state)

# 查询状态
current_state = state_manager.get_workflow_state(workflow_id)
```

## 快速开始

### 基本工作流创建

```python
import asyncio
from enhanced_workflow_engine import EnhancedWorkflowEngine, WorkflowNode, WorkflowEdge

async def create_basic_workflow():
    # 初始化引擎
    engine = EnhancedWorkflowEngine()
    
    # 创建节点
    node1 = WorkflowNode(
        id="start",
        name="开始节点",
        type="start",
        description="工作流开始"
    )
    
    node2 = WorkflowNode(
        id="process",
        name="处理节点", 
        type="action",
        description="数据处理",
        config={"action": "process_data"}
    )
    
    node3 = WorkflowNode(
        id="end",
        name="结束节点",
        type="end", 
        description="工作流结束"
    )
    
    # 创建边
    edge1 = WorkflowEdge(source="start", target="process")
    edge2 = WorkflowEdge(source="process", target="end")
    
    # 创建工作流
    workflow = engine.create_workflow(
        name="基本工作流",
        description="一个基本的工作流示例",
        nodes=[node1, node2, node3],
        edges=[edge1, edge2]
    )
    
    return workflow

# 运行示例
workflow = asyncio.run(create_basic_workflow())
```

### 动态工作流生成

```python
import asyncio
from dynamic_workflow_generator import DynamicWorkflowGenerator, WorkflowRequirement

async def generate_dynamic_workflow():
    generator = DynamicWorkflowGenerator()
    
    # 定义需求
    requirement = WorkflowRequirement(
        name="自动化测试工作流",
        description="自动化测试流程",
        required_capabilities=["code_analysis", "test_execution", "report_generation"],
        max_parallel_tasks=3
    )
    
    # 生成工作流
    workflow = await generator.generate_workflow(requirement)
    
    print(f"生成的工作流: {workflow.name}")
    print(f"节点数量: {len(workflow.nodes)}")
    print(f"边数量: {len(workflow.edges)}")
    
    return workflow

# 运行示例
workflow = asyncio.run(generate_dynamic_workflow())
```

### 并行执行示例

```python
import asyncio
from parallel_execution_scheduler import ParallelExecutionScheduler

async def parallel_execution_example():
    scheduler = ParallelExecutionScheduler()
    
    # 定义任务
    tasks = [
        {"id": "task1", "type": "data_fetch", "config": {"source": "db1"}},
        {"id": "task2", "type": "data_fetch", "config": {"source": "db2"}},
        {"id": "task3", "type": "data_process", "config": {"algorithm": "ml_model"}},
    ]
    
    # 并行执行
    results = await scheduler.execute_parallel(tasks)
    
    for task_id, result in results.items():
        print(f"任务 {task_id}: {result['status']}")
    
    return results

# 运行示例
results = asyncio.run(parallel_execution_example())
```

## 高级功能

### 依赖关系管理

```python
import asyncio
from intelligent_dependency_manager import IntelligentDependencyManager, DependencyType

async def dependency_management_example():
    dep_manager = IntelligentDependencyManager()
    
    # 添加复杂依赖关系
    await dep_manager.add_dependency("data_fetch", "data_validate", DependencyType.DATA)
    await dep_manager.add_dependency("data_validate", "data_transform", DependencyType.DATA)
    await dep_manager.add_dependency("data_transform", "data_store", DependencyType.DATA)
    
    # 添加控制依赖
    await dep_manager.add_dependency("config_load", "data_fetch", DependencyType.CONTROL)
    
    # 计算拓扑排序
    execution_order = dep_manager._calculate_topological_order()
    print(f"执行顺序: {execution_order}")
    
    # 检测冲突
    conflicts = await dep_manager._detect_conflicts()
    if conflicts:
        print(f"发现 {len(conflicts)} 个冲突")
    else:
        print("没有发现冲突")

# 运行示例
asyncio.run(dependency_management_example())
```

### 状态管理

```python
from workflow_state_manager import WorkflowStateManager

def state_management_example():
    state_manager = WorkflowStateManager()
    
    workflow_id = "workflow_123"
    
    # 创建初始状态
    initial_state = {
        "status": "created",
        "progress": 0,
        "current_step": "initialization",
        "metadata": {"created_by": "user123"}
    }
    
    state_manager.create_workflow_state(workflow_id, initial_state)
    
    # 更新状态
    state_manager.update_workflow_state(workflow_id, {
        "status": "running",
        "progress": 25,
        "current_step": "data_processing"
    })
    
    # 查询状态
    current_state = state_manager.get_workflow_state(workflow_id)
    print(f"当前状态: {current_state}")
    
    # 获取历史记录
    history = state_manager.get_workflow_history(workflow_id)
    print(f"历史记录数量: {len(history)}")

# 运行示例
state_management_example()
```

## CLI 使用

增强型工作流引擎提供了完整的命令行接口：

```bash
# 创建工作流
python cli.py create --name "测试工作流" --template basic

# 执行工作流
python cli.py execute --workflow-id workflow_123

# 查看状态
python cli.py status --workflow-id workflow_123

# 列出所有工作流
python cli.py list

# 分析工作流
python cli.py analyze --workflow-id workflow_123

# 优化工作流
python cli.py optimize --workflow-id workflow_123
```

## 性能优化

### 工作流生成优化

- 使用缓存机制减少重复计算
- 模板预编译提升生成速度
- 智能模板选择算法

### 并行执行优化

- 动态负载均衡
- 资源池管理
- 智能任务调度

### 依赖管理优化

- 图算法优化
- 增量更新机制
- 冲突预测和预防

### 状态管理优化

- 数据库连接池
- 批量操作优化
- 自动检查点机制

## 最佳实践

### 1. 工作流设计

- 保持节点职责单一
- 合理设计依赖关系
- 避免过深的嵌套结构
- 使用有意义的节点命名

### 2. 性能优化

- 合理设置并行度
- 使用资源约束避免过载
- 定期清理历史数据
- 监控系统性能指标

### 3. 错误处理

- 设置合理的超时时间
- 实现重试机制
- 记录详细的错误日志
- 提供回滚机制

### 4. 监控和调试

- 使用性能指标监控
- 启用详细日志记录
- 定期进行性能测试
- 建立告警机制

## 故障排除

### 常见问题

1. **导入错误**
   - 检查Python路径配置
   - 确认所有依赖已安装
   - 验证模块文件完整性

2. **性能问题**
   - 检查并行度设置
   - 监控资源使用情况
   - 优化依赖关系图

3. **状态不一致**
   - 检查数据库连接
   - 验证事务完整性
   - 重建状态索引

### 调试技巧

- 启用详细日志记录
- 使用性能分析工具
- 分步骤验证功能
- 查看系统资源使用

## 扩展开发

### 自定义节点类型

```python
from enhanced_workflow_engine import WorkflowNode

class CustomNode(WorkflowNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "custom"
    
    async def execute(self, context):
        # 自定义执行逻辑
        pass
```

### 自定义执行器

```python
from parallel_execution_scheduler import BaseExecutor

class CustomExecutor(BaseExecutor):
    async def execute_task(self, task, context):
        # 自定义任务执行逻辑
        pass
```

### 自定义依赖类型

```python
from intelligent_dependency_manager import DependencyType

# 扩展依赖类型
class CustomDependencyType(DependencyType):
    CUSTOM_TYPE = "custom_type"
```

## 版本信息

- **当前版本**: 1.0.0
- **Python要求**: 3.8+
- **主要依赖**: asyncio, sqlite3, logging

## 支持和反馈

如有问题或建议，请联系开发团队或提交Issue。

---

*本文档持续更新中，最新版本请查看项目仓库。*

