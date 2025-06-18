# Test Management MCP

PowerAutomation测试框架管理器，提供统一的测试生成、执行和管理功能。

## 📋 功能特性

### 🏗️ 测试框架生成
- 自动发现所有MCP模块
- 生成标准化测试结构
- 支持单元测试和集成测试
- 创建测试模板和配置文件

### 🧪 测试执行
- 并行测试执行
- 详细测试报告
- 错误诊断和分析
- 超时控制

### 🔧 测试修复
- 自动修复测试代码问题
- 更新导入路径
- 修复语法错误
- 标准化测试结构

### 📊 测试管理
- 测试状态监控
- 报告生成和存储
- 完整测试周期管理
- CLI工具支持

## 🚀 快速开始

### 安装和初始化

```bash
# 进入项目目录
cd /opt/powerautomation

# 使用CLI工具
python mcp/adapter/test_manage_mcp/cli.py --help
```

### 基本用法

```bash
# 生成测试框架
python mcp/adapter/test_manage_mcp/cli.py generate

# 执行所有测试
python mcp/adapter/test_manage_mcp/cli.py execute

# 修复测试框架
python mcp/adapter/test_manage_mcp/cli.py fix

# 查看测试状态
python mcp/adapter/test_manage_mcp/cli.py status --verbose

# 运行完整测试周期
python mcp/adapter/test_manage_mcp/cli.py cycle
```

### 高级用法

```bash
# 并行执行测试(8个工作线程)
python mcp/adapter/test_manage_mcp/cli.py execute --workers 8

# 顺序执行测试
python mcp/adapter/test_manage_mcp/cli.py execute --sequential

# 运行完整周期(跳过修复)
python mcp/adapter/test_manage_mcp/cli.py cycle --no-fix

# 列出测试报告
python mcp/adapter/test_manage_mcp/cli.py reports --limit 10 --verbose
```

## 📁 目录结构

```
test_manage_mcp/
├── __init__.py                    # 模块初始化
├── test_manage_mcp.py            # 主模块
├── cli.py                        # 命令行接口
├── framework/                    # 测试框架组件
│   ├── __init__.py
│   ├── test_framework_generator.py  # 测试框架生成器
│   ├── test_executor.py            # 测试执行器
│   └── test_framework_fixer.py     # 测试框架修复器
├── reports/                      # 测试报告
│   ├── generation_report_*.json
│   ├── execution_report_*.json
│   ├── fix_report_*.json
│   └── full_cycle_report_*.json
└── README.md                     # 本文档
```

## 🔧 API 参考

### TestManageMCP 类

主要的测试管理类，提供以下方法：

#### `generate_test_frameworks()`
生成所有MCP模块的测试框架

**返回值:**
```python
{
    "status": "success|error",
    "results": {...},
    "report_path": "path/to/report.json",
    "generation_time": "2025-06-17T05:45:00"
}
```

#### `execute_all_tests(parallel=True, max_workers=4)`
执行所有测试

**参数:**
- `parallel`: 是否并行执行
- `max_workers`: 最大并发数

**返回值:**
```python
{
    "status": "success|partial_failure|error",
    "all_tests_passed": true|false,
    "report_path": "path/to/report.json",
    "execution_time": "2025-06-17T05:45:00"
}
```

#### `fix_test_frameworks()`
修复测试框架中的问题

**返回值:**
```python
{
    "status": "success|error",
    "results": {...},
    "report_path": "path/to/report.json",
    "fix_time": "2025-06-17T05:45:00"
}
```

#### `get_test_status()`
获取测试状态概览

**返回值:**
```python
{
    "status": "success|error",
    "overview": {
        "total_modules": 15,
        "total_tests": 30,
        "unit_tests": 15,
        "integration_tests": 15,
        "adapter_modules": 8,
        "workflow_modules": 7
    },
    "last_operations": {...},
    "latest_reports": {...}
}
```

#### `run_full_test_cycle(fix_first=True, parallel=True, max_workers=4)`
运行完整的测试周期

**参数:**
- `fix_first`: 是否先修复现有问题
- `parallel`: 是否并行执行测试
- `max_workers`: 最大并发数

**返回值:**
```python
{
    "cycle_start_time": "2025-06-17T05:45:00",
    "cycle_end_time": "2025-06-17T05:46:00",
    "cycle_duration": 60.0,
    "overall_status": "success|partial_failure|error",
    "steps": [...],
    "summary": {...}
}
```

## 📊 测试报告

### 报告类型

1. **生成报告** (`generation_report_*.json`)
   - 测试框架生成统计
   - 发现的模块列表
   - 生成的文件清单

2. **执行报告** (`execution_report_*.json`)
   - 测试执行结果
   - 通过/失败统计
   - 错误详情

3. **修复报告** (`fix_report_*.json`)
   - 修复的文件列表
   - 修复的问题类型
   - 修复前后对比

4. **完整周期报告** (`full_cycle_report_*.json`)
   - 完整测试周期的详细记录
   - 各步骤执行时间
   - 总体统计信息

### 报告格式

所有报告都采用JSON格式，包含以下通用字段：

```json
{
    "status": "success|partial_failure|error",
    "timestamp": "2025-06-17T05:45:00",
    "duration": 60.0,
    "summary": {...},
    "details": {...}
}
```

## 🔍 故障排除

### 常见问题

1. **模块导入失败**
   - 检查Python路径设置
   - 确认模块文件存在
   - 运行修复命令

2. **测试执行超时**
   - 增加超时时间
   - 减少并发数
   - 检查系统资源

3. **权限问题**
   - 确认文件写入权限
   - 检查目录访问权限

### 调试模式

```bash
# 启用详细日志
python mcp/adapter/test_manage_mcp/cli.py status --verbose

# 查看错误详情
python mcp/adapter/test_manage_mcp/cli.py reports --verbose
```

## 📈 性能优化

### 并行执行优化

- 根据CPU核心数调整 `--workers` 参数
- 对于IO密集型测试，可以增加并发数
- 对于CPU密集型测试，建议使用CPU核心数

### 内存优化

- 大型项目建议分批执行测试
- 定期清理旧的测试报告
- 监控内存使用情况

## 🤝 贡献指南

### 开发环境设置

1. 克隆项目
2. 安装依赖
3. 运行测试

### 代码规范

- 遵循PEP 8代码风格
- 添加类型注解
- 编写单元测试
- 更新文档

## 📄 许可证

PowerAutomation Team © 2025

---

**版本**: 1.0.0  
**维护**: PowerAutomation Team  
**更新**: 2025-06-17

