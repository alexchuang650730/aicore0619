#!/usr/bin/env python3
"""
Operations Workflow MCP - File Placement Manager
文件放置管理器 - 根据目录结构标准自动放置上传文件
"""

import os
import shutil
import tarfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FilePlacementManager:
    """文件放置管理器"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.upload_dir = self.repo_root / "upload"
        
        # 定义文件类型和目标位置的映射
        self.placement_rules = {
            # 测试相关文件
            "test_case_generator.py": {
                "target": "scripts/test_case_generator.py",
                "type": "script",
                "description": "PowerAutomation测试用例生成器"
            },
            "simplified_test_cases_template.md": {
                "target": "workflow_howto/test_case_template.md",
                "type": "documentation",
                "description": "简化测试用例模板"
            },
            "powerautomation_test_framework.tar.gz": {
                "target": "test/powerautomation_test_framework/",
                "type": "test_framework",
                "description": "PowerAutomation测试框架",
                "extract": True
            },
            "generated_tests/": {
                "target": "test/generated_tests/",
                "type": "test_cases",
                "description": "生成的测试用例"
            },
            # 配置文件
            "*.pem": {
                "target": "upload/.recovery/",
                "type": "security",
                "description": "安全密钥文件，保持在upload目录"
            },
            ".recovery/": {
                "target": "upload/.recovery/",
                "type": "recovery",
                "description": "恢复文件，保持在upload目录"
            }
        }
        
        logger.info("📁 File Placement Manager 初始化完成")
    
    def analyze_upload_files(self) -> Dict[str, Any]:
        """分析上传文件"""
        analysis = {
            "total_files": 0,
            "total_directories": 0,
            "files_by_type": {},
            "placement_plan": [],
            "files": []
        }
        
        if not self.upload_dir.exists():
            logger.warning("⚠️ 上传目录不存在")
            return analysis
        
        # 扫描上传目录
        for item in self.upload_dir.rglob("*"):
            if item.is_file():
                analysis["total_files"] += 1
                relative_path = item.relative_to(self.upload_dir)
                
                file_info = {
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "type": self._determine_file_type(item),
                    "placement_rule": self._find_placement_rule(str(relative_path))
                }
                
                analysis["files"].append(file_info)
                
                # 按类型分组
                file_type = file_info["type"]
                if file_type not in analysis["files_by_type"]:
                    analysis["files_by_type"][file_type] = 0
                analysis["files_by_type"][file_type] += 1
                
                # 生成放置计划
                if file_info["placement_rule"]:
                    analysis["placement_plan"].append({
                        "source": str(relative_path),
                        "target": file_info["placement_rule"]["target"],
                        "type": file_info["placement_rule"]["type"],
                        "description": file_info["placement_rule"]["description"],
                        "extract": file_info["placement_rule"].get("extract", False)
                    })
            
            elif item.is_dir() and item != self.upload_dir:
                analysis["total_directories"] += 1
        
        logger.info(f"📊 分析完成: {analysis['total_files']} 个文件, {analysis['total_directories']} 个目录")
        return analysis
    
    def _determine_file_type(self, file_path: Path) -> str:
        """确定文件类型"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        
        if suffix == ".py":
            return "python_script"
        elif suffix == ".md":
            return "documentation"
        elif suffix in [".tar.gz", ".zip", ".tar"]:
            return "archive"
        elif suffix == ".yaml" or suffix == ".yml":
            return "configuration"
        elif suffix == ".json":
            return "data"
        elif suffix == ".pem":
            return "security"
        elif "test" in name:
            return "test"
        else:
            return "unknown"
    
    def _find_placement_rule(self, file_path: str) -> Optional[Dict[str, Any]]:
        """查找文件放置规则"""
        file_name = Path(file_path).name
        
        # 精确匹配
        if file_name in self.placement_rules:
            return self.placement_rules[file_name]
        
        # 目录匹配
        for rule_pattern, rule_config in self.placement_rules.items():
            if rule_pattern.endswith("/") and file_path.startswith(rule_pattern):
                return rule_config
        
        # 通配符匹配
        for rule_pattern, rule_config in self.placement_rules.items():
            if "*" in rule_pattern:
                import fnmatch
                if fnmatch.fnmatch(file_name, rule_pattern):
                    return rule_config
        
        return None
    
    def execute_placement_plan(self, placement_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """执行文件放置计划"""
        results = {
            "total_planned": len(placement_plan),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for plan_item in placement_plan:
            try:
                source_path = self.upload_dir / plan_item["source"]
                target_path = self.repo_root / plan_item["target"]
                
                # 确保目标目录存在
                if plan_item.get("extract", False):
                    # 解压文件
                    target_path.mkdir(parents=True, exist_ok=True)
                    self._extract_archive(source_path, target_path)
                    action = "extracted"
                else:
                    # 复制文件
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_path.is_dir():
                        if target_path.exists():
                            shutil.rmtree(target_path)
                        shutil.copytree(source_path, target_path)
                        action = "copied_directory"
                    else:
                        shutil.copy2(source_path, target_path)
                        action = "copied_file"
                
                results["successful"] += 1
                results["details"].append({
                    "source": plan_item["source"],
                    "target": plan_item["target"],
                    "action": action,
                    "status": "success",
                    "description": plan_item["description"]
                })
                
                logger.info(f"✅ {action}: {plan_item['source']} → {plan_item['target']}")
                
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "source": plan_item["source"],
                    "target": plan_item["target"],
                    "action": "failed",
                    "status": "error",
                    "error": str(e),
                    "description": plan_item["description"]
                })
                
                logger.error(f"❌ 放置失败: {plan_item['source']} → {plan_item['target']}: {e}")
        
        return results
    
    def _extract_archive(self, archive_path: Path, target_dir: Path):
        """解压归档文件"""
        if archive_path.suffix == ".gz" and archive_path.stem.endswith(".tar"):
            # tar.gz 文件
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(target_dir)
        elif archive_path.suffix == ".tar":
            # tar 文件
            with tarfile.open(archive_path, 'r') as tar:
                tar.extractall(target_dir)
        elif archive_path.suffix == ".zip":
            # zip 文件
            import zipfile
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                zip_file.extractall(target_dir)
        else:
            raise ValueError(f"不支持的归档格式: {archive_path.suffix}")
    
    def generate_placement_report(self, analysis: Dict[str, Any], results: Dict[str, Any]) -> str:
        """生成文件放置报告"""
        report = f"""# 文件放置报告

## 📊 分析结果
- **总文件数**: {analysis['total_files']}
- **总目录数**: {analysis['total_directories']}
- **计划放置**: {len(analysis['placement_plan'])} 个项目

### 文件类型分布
"""
        
        for file_type, count in analysis['files_by_type'].items():
            report += f"- **{file_type}**: {count} 个\n"
        
        report += f"""
## 🎯 执行结果
- **计划总数**: {results['total_planned']}
- **成功**: {results['successful']}
- **失败**: {results['failed']}
- **成功率**: {(results['successful'] / results['total_planned'] * 100) if results['total_planned'] > 0 else 0:.1f}%

### 详细结果
"""
        
        for detail in results['details']:
            status_icon = "✅" if detail['status'] == 'success' else "❌"
            report += f"{status_icon} **{detail['action']}**: `{detail['source']}` → `{detail['target']}`\n"
            report += f"   - {detail['description']}\n"
            if detail['status'] == 'error':
                report += f"   - 错误: {detail.get('error', 'Unknown error')}\n"
            report += "\n"
        
        report += f"""
## 📋 目录结构更新

根据PowerAutomation目录结构标准，文件已放置到以下位置：

### 脚本文件 (`/scripts/`)
- 测试用例生成器和其他工具脚本

### 测试文件 (`/test/`)
- PowerAutomation测试框架
- 生成的测试用例

### 文档文件 (`/workflow_howto/`)
- 测试用例模板和开发指南

### 安全文件 (`/upload/`)
- 密钥文件和恢复数据保持在原位置

---
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**操作者**: Operations Workflow MCP
"""
        
        return report
    
    def cleanup_upload_directory(self, keep_security_files: bool = True):
        """清理上传目录"""
        if not self.upload_dir.exists():
            return
        
        for item in self.upload_dir.iterdir():
            if keep_security_files and (item.name.endswith('.pem') or item.name == '.recovery'):
                continue
            
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                logger.info(f"🗑️ 清理: {item.name}")
            except Exception as e:
                logger.error(f"❌ 清理失败: {item.name}: {e}")

if __name__ == "__main__":
    # 测试文件放置管理器
    from datetime import datetime
    
    manager = FilePlacementManager()
    
    print("📁 PowerAutomation 文件放置管理器")
    print("=" * 50)
    
    # 分析上传文件
    print("🔍 分析上传文件...")
    analysis = manager.analyze_upload_files()
    
    print(f"发现 {analysis['total_files']} 个文件")
    print(f"计划放置 {len(analysis['placement_plan'])} 个项目")
    
    if analysis['placement_plan']:
        print("\n📋 放置计划:")
        for plan in analysis['placement_plan']:
            print(f"  {plan['source']} → {plan['target']}")
        
        # 执行放置计划
        print("\n🚀 执行文件放置...")
        results = manager.execute_placement_plan(analysis['placement_plan'])
        
        print(f"成功: {results['successful']}, 失败: {results['failed']}")
        
        # 生成报告
        print("\n📄 生成放置报告...")
        report = manager.generate_placement_report(analysis, results)
        
        # 保存报告
        report_path = manager.repo_root / "FILE_PLACEMENT_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"报告已保存到: {report_path}")
        
        # 清理上传目录（保留安全文件）
        print("\n🗑️ 清理上传目录...")
        manager.cleanup_upload_directory(keep_security_files=True)
        
        print("\n✅ 文件放置完成！")
    else:
        print("⚠️ 没有找到需要放置的文件")

