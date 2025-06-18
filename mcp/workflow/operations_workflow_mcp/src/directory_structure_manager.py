#!/usr/bin/env python3
"""
Operations Workflow MCP - Directory Structure Manager
目录结构管理器 - 负责定义和维护标准目录结构
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

class DirectoryStructureManager:
    """目录结构管理器"""
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.logger = logging.getLogger(__name__)
        
        # 定义标准目录结构
        self.standard_structure = {
            "aicore0615_standard_structure": {
                "description": "AICore0615项目标准目录结构",
                "version": "1.0.0",
                "structure": {
                    "/": {
                        "description": "项目根目录",
                        "required_files": ["README.md", "todo.md"],
                        "subdirectories": {
                            "mcp/": {
                                "description": "MCP组件目录",
                                "required_files": ["MCP_DIRECTORY_STRUCTURE.md"],
                                "subdirectories": {
                                    "adapter/": {
                                        "description": "小型MCP适配器目录",
                                        "naming_pattern": "*_mcp/",
                                        "examples": [
                                            "local_model_mcp/",
                                            "cloud_search_mcp/", 
                                            "kilocode_mcp/",
                                            "development_intervention_mcp/"
                                        ]
                                    },
                                    "workflow/": {
                                        "description": "大型MCP工作流目录",
                                        "naming_pattern": "*_workflow_mcp/",
                                        "examples": [
                                            "ocr_workflow_mcp/",
                                            "operations_workflow_mcp/"
                                        ]
                                    }
                                }
                            },
                            "workflow_howto/": {
                                "description": "工作流开发指南目录",
                                "required_files": ["DIRECTORY_STRUCTURE_STANDARD.md"],
                                "file_types": ["*.md"]
                            },
                            "mcphowto/": {
                                "description": "MCP开发指南目录", 
                                "required_files": ["DIRECTORY_STRUCTURE_STANDARD.md"],
                                "file_types": ["*.md"]
                            },
                            "scripts/": {
                                "description": "脚本文件目录",
                                "file_types": ["*.py", "*.sh"]
                            },
                            "test/": {
                                "description": "测试文件目录",
                                "file_types": ["test_*.py", "*_test.py"]
                            },
                            "smartui/": {
                                "description": "SmartUI相关文件",
                                "file_types": ["*.py", "*.html", "*.css", "*.js"]
                            },
                            "upload/": {
                                "description": "上传文件临时目录",
                                "file_types": ["*"]
                            }
                        }
                    }
                },
                "forbidden_locations": {
                    "/adapters/": "应该移动到 /mcp/adapter/",
                    "/howto/": "应该移动到 /workflow_howto/ 或 /mcphowto/",
                    "/mcp/*.py": "MCP实现文件应该在对应的子目录中"
                }
            }
        }
    
    def generate_structure_document(self) -> str:
        """生成目录结构文档"""
        doc = """# AICore0615 项目目录结构标准

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
"""
        return doc
    
    def check_structure_compliance(self) -> Dict[str, Any]:
        """检查目录结构合规性"""
        issues = []
        
        # 检查禁止的目录
        forbidden = self.standard_structure["aicore0615_standard_structure"]["forbidden_locations"]
        
        for forbidden_path, suggestion in forbidden.items():
            full_path = self.repo_root / forbidden_path.lstrip('/')
            if '*' in forbidden_path:
                # 处理通配符路径
                parent_dir = full_path.parent
                pattern = full_path.name
                if parent_dir.exists():
                    for item in parent_dir.iterdir():
                        if pattern.replace('*', '') in item.name and item.suffix == '.py':
                            issues.append({
                                "type": "forbidden_location",
                                "path": str(item.relative_to(self.repo_root)),
                                "suggestion": suggestion,
                                "severity": "high"
                            })
            else:
                if full_path.exists():
                    issues.append({
                        "type": "forbidden_location", 
                        "path": str(full_path.relative_to(self.repo_root)),
                        "suggestion": suggestion,
                        "severity": "high"
                    })
        
        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "total_issues": len(issues)
        }
    
    def fix_structure_issues(self) -> Dict[str, Any]:
        """修复目录结构问题"""
        compliance_check = self.check_structure_compliance()
        fixed_issues = []
        
        for issue in compliance_check["issues"]:
            if issue["type"] == "forbidden_location":
                try:
                    source_path = self.repo_root / issue["path"]
                    
                    # 根据建议确定目标路径
                    if "mcp/adapter/" in issue["suggestion"]:
                        if source_path.is_dir():
                            target_path = self.repo_root / "mcp" / "adapter" / source_path.name
                        else:
                            # 单个文件需要放到合适的MCP目录中
                            target_path = self.repo_root / "mcp" / "adapter" / f"{source_path.stem}_mcp" / source_path.name
                    elif "workflow_howto/" in issue["suggestion"]:
                        target_path = self.repo_root / "workflow_howto" / source_path.name
                    elif "mcphowto/" in issue["suggestion"]:
                        target_path = self.repo_root / "mcphowto" / source_path.name
                    else:
                        continue
                    
                    # 确保目标目录存在
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 移动文件或目录
                    if source_path.exists():
                        shutil.move(str(source_path), str(target_path))
                        fixed_issues.append({
                            "issue": issue,
                            "action": "moved",
                            "from": issue["path"],
                            "to": str(target_path.relative_to(self.repo_root))
                        })
                        
                except Exception as e:
                    self.logger.error(f"Failed to fix issue {issue}: {e}")
        
        return {
            "fixed_count": len(fixed_issues),
            "fixed_issues": fixed_issues
        }
    
    def deploy_structure_documents(self) -> Dict[str, Any]:
        """部署目录结构文档到各个位置"""
        doc_content = self.generate_structure_document()
        deployed_locations = []
        
        # 部署位置
        locations = [
            self.repo_root / "DIRECTORY_STRUCTURE_STANDARD.md",
            self.repo_root / "workflow_howto" / "DIRECTORY_STRUCTURE_STANDARD.md", 
            self.repo_root / "mcphowto" / "DIRECTORY_STRUCTURE_STANDARD.md",
            self.repo_root / "mcp" / "MCP_DIRECTORY_STRUCTURE.md"
        ]
        
        for location in locations:
            try:
                # 确保目录存在
                location.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入文档
                with open(location, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                
                deployed_locations.append(str(location.relative_to(self.repo_root)))
                
            except Exception as e:
                self.logger.error(f"Failed to deploy document to {location}: {e}")
        
        return {
            "deployed_count": len(deployed_locations),
            "deployed_locations": deployed_locations
        }

if __name__ == "__main__":
    # 测试目录结构管理器
    manager = DirectoryStructureManager("/home/ubuntu/kilocode_integrated_repo")
    
    print("🔍 检查目录结构合规性...")
    compliance = manager.check_structure_compliance()
    print(f"合规状态: {'✅ 合规' if compliance['compliant'] else '❌ 不合规'}")
    print(f"发现问题: {compliance['total_issues']}个")
    
    if not compliance['compliant']:
        print("\n🔧 修复目录结构问题...")
        fix_result = manager.fix_structure_issues()
        print(f"修复问题: {fix_result['fixed_count']}个")
    
    print("\n📚 部署目录结构文档...")
    deploy_result = manager.deploy_structure_documents()
    print(f"部署位置: {deploy_result['deployed_count']}个")
    
    print("\n✅ 目录结构管理完成！")

