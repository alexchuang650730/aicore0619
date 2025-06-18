# AICore0615 项目目录结构标准

## 📋 目录结构规范

### 🎯 设计原则
- **功能分离**: 不同功能的代码放在不同目录
- **类型分类**: 按照MCP类型(adapter/workflow)分类
- **标准命名**: 统一的命名规范和目录结构
- **文档同步**: 每个目录都有对应的文档说明

### 📁 标准目录结构

```
aicore0615/
├── README.md                    # 项目主说明文档
├── todo.md                      # 任务清单
├── mcp/                         # MCP组件目录
│   ├── MCP_DIRECTORY_STRUCTURE.md  # MCP目录结构说明
│   ├── adapter/                 # 小型MCP适配器
│   │   ├── local_model_mcp/     # 本地模型适配器
│   │   ├── cloud_search_mcp/    # 云端搜索适配器
│   │   ├── kilocode_mcp/        # KiloCode适配器
│   │   └── development_intervention_mcp/  # 开发介入适配器
│   └── workflow/                # 大型MCP工作流
│       ├── ocr_workflow_mcp/    # OCR工作流MCP
│       └── operations_workflow_mcp/  # 运营工作流MCP
├── workflow_howto/              # 工作流开发指南
│   ├── DIRECTORY_STRUCTURE_STANDARD.md  # 目录结构标准
│   └── *.md                     # 各种工作流开发指南
├── mcphowto/                    # MCP开发指南
│   ├── DIRECTORY_STRUCTURE_STANDARD.md  # 目录结构标准
│   └── *.md                     # 各种MCP开发指南
├── scripts/                     # 脚本文件
│   └── *.py, *.sh              # 各种脚本
├── test/                        # 测试文件
│   └── test_*.py, *_test.py    # 测试文件
├── smartui/                     # SmartUI相关
│   └── *.py, *.html, *.css, *.js  # UI文件
└── upload/                      # 上传文件临时目录
    └── *                        # 临时文件
```

### 🏷️ MCP分类标准

#### **小型MCP (Adapter类型)**
- **位置**: `/mcp/adapter/xxx_mcp/`
- **特点**: 单一功能，轻量级，专注特定任务
- **命名**: `*_mcp/` 格式
- **示例**: `local_model_mcp`, `cloud_search_mcp`

#### **大型MCP (Workflow类型)**
- **位置**: `/mcp/workflow/xxx_workflow_mcp/`
- **特点**: 复杂工作流，多步骤处理，智能路由
- **命名**: `*_workflow_mcp/` 格式
- **示例**: `ocr_workflow_mcp`, `operations_workflow_mcp`

### ❌ 禁止的目录结构

以下目录结构不符合规范，需要修复：

- `/adapters/` → 应该移动到 `/mcp/adapter/`
- `/howto/` → 应该移动到 `/workflow_howto/` 或 `/mcphowto/`
- `/mcp/*.py` → MCP实现文件应该在对应的子目录中

### 🔧 自动修复

Operations Workflow MCP会自动检测和修复不符合规范的目录结构：

1. **检测违规**: 扫描不符合规范的目录和文件
2. **智能分类**: 根据文件内容和功能自动分类
3. **安全迁移**: 保留备份，安全移动文件
4. **更新引用**: 自动更新文件间的引用关系
5. **验证完整**: 确保迁移后功能正常

### 📊 合规检查

定期运行合规检查确保目录结构符合标准：

```bash
# 检查目录结构合规性
python3 mcp/workflow/operations_workflow_mcp/cli.py check-structure

# 自动修复目录结构
python3 mcp/workflow/operations_workflow_mcp/cli.py fix-structure

# 生成目录结构报告
python3 mcp/workflow/operations_workflow_mcp/cli.py structure-report
```

---

**版本**: 1.0.0  
**维护**: Operations Workflow MCP  
**更新**: 自动同步到所有相关目录
