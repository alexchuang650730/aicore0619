#!/usr/bin/env python3
"""
PR Review Prevention Module for Development Intervention MCP
PR审查阶段预防机制 - 在代码提交前进行预防性检查
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PreventionLevel(Enum):
    """预防级别"""
    INFO = "info"           # 信息提示
    WARNING = "warning"     # 警告
    ERROR = "error"         # 错误，阻止提交
    CRITICAL = "critical"   # 严重错误，强制阻止

@dataclass
class PreventionResult:
    """预防检查结果"""
    level: PreventionLevel
    rule_name: str
    file_path: str
    line_number: int
    message: str
    suggestion: str
    auto_fixable: bool = False
    blocked: bool = False

class PRReviewPrevention:
    """PR审查预防机制"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.prevention_rules = self._initialize_prevention_rules()
        self.git_hooks_installed = False
        
        # 预防统计
        self.prevention_stats = {
            "total_checks": 0,
            "blocked_commits": 0,
            "auto_fixes_applied": 0,
            "warnings_issued": 0
        }
        
        logger.info("🛡️ PR Review Prevention 初始化完成")
    
    def _initialize_prevention_rules(self) -> Dict[str, Dict]:
        """初始化预防规则"""
        return {
            # MCP通信违规预防
            "mcp_direct_import": {
                "patterns": [
                    r"from\s+\w*mcp\w*\s+import",
                    r"import\s+\w*mcp\w*(?!.*coordinator)",
                ],
                "level": PreventionLevel.ERROR,
                "message": "🚫 检测到直接MCP导入，违反中央协调原则",
                "suggestion": "使用 coordinator.get_mcp() 获取MCP实例",
                "auto_fix": True,
                "block_commit": True
            },
            
            "mcp_direct_call": {
                "patterns": [
                    r"\w*mcp\w*\.\w+\(",
                    r"\.process\(\s*(?!.*coordinator)"
                ],
                "level": PreventionLevel.CRITICAL,
                "message": "🚫 检测到直接MCP调用，必须通过中央协调器",
                "suggestion": "使用 coordinator.route_to_mcp() 进行调用",
                "auto_fix": True,
                "block_commit": True
            },
            
            # 代码质量预防
            "hardcoded_credentials": {
                "patterns": [
                    r"password\s*=\s*['\"][^'\"]+['\"]",
                    r"api_key\s*=\s*['\"][^'\"]+['\"]",
                    r"secret\s*=\s*['\"][^'\"]+['\"]"
                ],
                "level": PreventionLevel.CRITICAL,
                "message": "🔒 检测到硬编码凭据，存在安全风险",
                "suggestion": "使用环境变量或配置文件存储敏感信息",
                "auto_fix": False,
                "block_commit": True
            },
            
            "debug_code": {
                "patterns": [
                    r"print\s*\(",
                    r"console\.log\s*\(",
                    r"debugger;",
                    r"pdb\.set_trace\(\)"
                ],
                "level": PreventionLevel.WARNING,
                "message": "🐛 检测到调试代码，建议移除",
                "suggestion": "移除调试语句或使用日志记录",
                "auto_fix": True,
                "block_commit": False
            },
            
            # 架构合规预防
            "bypass_coordinator": {
                "patterns": [
                    r"(?<!coordinator\.)route_to",
                    r"(?<!coordinator\.)call_mcp",
                    r"direct_call\s*="
                ],
                "level": PreventionLevel.ERROR,
                "message": "🚫 检测到绕过中央协调器的调用",
                "suggestion": "所有MCP调用必须通过coordinator进行",
                "auto_fix": True,
                "block_commit": True
            },
            
            # 文档和注释预防
            "missing_docstring": {
                "patterns": [
                    r"def\s+\w+\([^)]*\):\s*\n\s*(?!\"\"\")",
                    r"class\s+\w+[^:]*:\s*\n\s*(?!\"\"\")"
                ],
                "level": PreventionLevel.WARNING,
                "message": "📝 缺少文档字符串",
                "suggestion": "为函数和类添加文档字符串",
                "auto_fix": False,
                "block_commit": False
            }
        }
    
    def install_git_hooks(self) -> Dict[str, Any]:
        """安装Git hooks进行预防性检查"""
        try:
            hooks_dir = self.repo_root / ".git" / "hooks"
            hooks_dir.mkdir(exist_ok=True)
            
            # 创建pre-commit hook
            pre_commit_hook = hooks_dir / "pre-commit"
            pre_commit_content = self._generate_pre_commit_hook()
            
            with open(pre_commit_hook, 'w') as f:
                f.write(pre_commit_content)
            
            # 设置执行权限
            os.chmod(pre_commit_hook, 0o755)
            
            # 创建pre-push hook
            pre_push_hook = hooks_dir / "pre-push"
            pre_push_content = self._generate_pre_push_hook()
            
            with open(pre_push_hook, 'w') as f:
                f.write(pre_push_content)
            
            os.chmod(pre_push_hook, 0o755)
            
            self.git_hooks_installed = True
            
            logger.info("✅ Git hooks 安装成功")
            return {
                "success": True,
                "message": "Git hooks 安装成功",
                "hooks_installed": ["pre-commit", "pre-push"]
            }
            
        except Exception as e:
            logger.error(f"❌ Git hooks 安装失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_pre_commit_hook(self) -> str:
        """生成pre-commit hook脚本"""
        return f'''#!/bin/bash
# Pre-commit hook for Development Intervention MCP
# 在提交前进行预防性检查

echo "🛡️ 运行Development Intervention MCP预防检查..."

# 调用Python预防检查脚本
python3 "{self.repo_root}/mcp/adapter/development_intervention_mcp/pr_review_prevention.py" --pre-commit

# 检查返回码
if [ $? -ne 0 ]; then
    echo "❌ 预防检查失败，提交被阻止"
    echo "请修复上述问题后重新提交"
    exit 1
fi

echo "✅ 预防检查通过"
exit 0
'''
    
    def _generate_pre_push_hook(self) -> str:
        """生成pre-push hook脚本"""
        return f'''#!/bin/bash
# Pre-push hook for Development Intervention MCP
# 在推送前进行最终检查

echo "🛡️ 运行Development Intervention MCP推送前检查..."

# 调用Python预防检查脚本
python3 "{self.repo_root}/mcp/adapter/development_intervention_mcp/pr_review_prevention.py" --pre-push

# 检查返回码
if [ $? -ne 0 ]; then
    echo "❌ 推送前检查失败，推送被阻止"
    echo "请修复上述问题后重新推送"
    exit 1
fi

echo "✅ 推送前检查通过"
exit 0
'''
    
    def check_staged_files(self) -> Dict[str, Any]:
        """检查暂存区文件"""
        try:
            # 获取暂存区文件
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "无法获取暂存区文件"
                }
            
            staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # 检查每个暂存文件
            all_results = []
            blocked_files = []
            
            for file_path in staged_files:
                if file_path.endswith('.py'):
                    file_results = self._check_file_prevention(self.repo_root / file_path)
                    all_results.extend(file_results)
                    
                    # 检查是否有阻止提交的问题
                    for result in file_results:
                        if result.blocked:
                            blocked_files.append(file_path)
            
            # 统计结果
            critical_count = len([r for r in all_results if r.level == PreventionLevel.CRITICAL])
            error_count = len([r for r in all_results if r.level == PreventionLevel.ERROR])
            warning_count = len([r for r in all_results if r.level == PreventionLevel.WARNING])
            
            # 更新统计
            self.prevention_stats["total_checks"] += 1
            if blocked_files:
                self.prevention_stats["blocked_commits"] += 1
            self.prevention_stats["warnings_issued"] += warning_count
            
            return {
                "success": True,
                "staged_files": staged_files,
                "total_issues": len(all_results),
                "critical_issues": critical_count,
                "error_issues": error_count,
                "warning_issues": warning_count,
                "blocked_files": list(set(blocked_files)),
                "should_block_commit": len(blocked_files) > 0,
                "results": [self._result_to_dict(r) for r in all_results]
            }
            
        except Exception as e:
            logger.error(f"检查暂存文件失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_file_prevention(self, file_path: Path) -> List[PreventionResult]:
        """检查单个文件的预防规则"""
        results = []
        
        try:
            if not file_path.exists():
                return results
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 应用所有预防规则
            for rule_name, rule_config in self.prevention_rules.items():
                for pattern in rule_config["patterns"]:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        
                        result = PreventionResult(
                            level=rule_config["level"],
                            rule_name=rule_name,
                            file_path=str(file_path),
                            line_number=line_number,
                            message=rule_config["message"],
                            suggestion=rule_config["suggestion"],
                            auto_fixable=rule_config.get("auto_fix", False),
                            blocked=rule_config.get("block_commit", False)
                        )
                        results.append(result)
            
        except Exception as e:
            logger.error(f"检查文件失败 {file_path}: {e}")
        
        return results
    
    def auto_fix_issues(self, results: List[PreventionResult]) -> Dict[str, Any]:
        """自动修复可修复的问题"""
        fixed_count = 0
        failed_fixes = []
        
        for result in results:
            if result.auto_fixable:
                try:
                    if self._apply_auto_fix(result):
                        fixed_count += 1
                        self.prevention_stats["auto_fixes_applied"] += 1
                    else:
                        failed_fixes.append(result.rule_name)
                except Exception as e:
                    logger.error(f"自动修复失败 {result.rule_name}: {e}")
                    failed_fixes.append(result.rule_name)
        
        return {
            "fixed_count": fixed_count,
            "failed_fixes": failed_fixes,
            "success": fixed_count > 0
        }
    
    def _apply_auto_fix(self, result: PreventionResult) -> bool:
        """应用自动修复"""
        try:
            with open(result.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 根据规则类型应用修复
            if result.rule_name == "mcp_direct_import":
                # 替换直接导入为协调器调用
                original_line = lines[result.line_number - 1]
                fixed_line = self._fix_mcp_import(original_line)
                lines[result.line_number - 1] = fixed_line
            
            elif result.rule_name == "debug_code":
                # 注释掉调试代码
                lines[result.line_number - 1] = "# " + lines[result.line_number - 1]
            
            # 写回文件
            with open(result.file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            logger.error(f"应用自动修复失败: {e}")
            return False
    
    def _fix_mcp_import(self, line: str) -> str:
        """修复MCP导入"""
        # 简化的修复逻辑
        if "import" in line:
            mcp_match = re.search(r'(\w*mcp\w*)', line, re.IGNORECASE)
            if mcp_match:
                mcp_name = mcp_match.group(1)
                return f"# 修复：通过中央协调器获取MCP\n# {line}# {mcp_name} = coordinator.get_mcp('{mcp_name.lower()}')\n"
        return line
    
    def _result_to_dict(self, result: PreventionResult) -> Dict:
        """将结果转换为字典"""
        return {
            "level": result.level.value,
            "rule_name": result.rule_name,
            "file_path": result.file_path,
            "line_number": result.line_number,
            "message": result.message,
            "suggestion": result.suggestion,
            "auto_fixable": result.auto_fixable,
            "blocked": result.blocked
        }
    
    def get_prevention_stats(self) -> Dict[str, Any]:
        """获取预防统计信息"""
        return {
            **self.prevention_stats,
            "git_hooks_installed": self.git_hooks_installed,
            "prevention_rules_count": len(self.prevention_rules),
            "last_check": datetime.now().isoformat()
        }

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Development Intervention MCP - PR Review Prevention")
    parser.add_argument("--pre-commit", action="store_true", help="运行pre-commit检查")
    parser.add_argument("--pre-push", action="store_true", help="运行pre-push检查")
    parser.add_argument("--install-hooks", action="store_true", help="安装Git hooks")
    parser.add_argument("--check-staged", action="store_true", help="检查暂存区文件")
    
    args = parser.parse_args()
    
    prevention = PRReviewPrevention()
    
    if args.install_hooks:
        result = prevention.install_git_hooks()
        print(json.dumps(result, indent=2))
        return 0 if result["success"] else 1
    
    if args.pre_commit or args.check_staged:
        result = prevention.check_staged_files()
        
        if result["success"]:
            print(f"🔍 检查了 {len(result['staged_files'])} 个文件")
            print(f"📊 发现 {result['total_issues']} 个问题:")
            print(f"  - 严重: {result['critical_issues']}")
            print(f"  - 错误: {result['error_issues']}")
            print(f"  - 警告: {result['warning_issues']}")
            
            if result["should_block_commit"]:
                print("❌ 发现阻止提交的问题，请修复后重新提交")
                for blocked_file in result["blocked_files"]:
                    print(f"  - {blocked_file}")
                return 1
            else:
                print("✅ 预防检查通过")
                return 0
        else:
            print(f"❌ 检查失败: {result['error']}")
            return 1
    
    if args.pre_push:
        # pre-push检查可以更严格
        result = prevention.check_staged_files()
        if result["success"] and result["total_issues"] > 0:
            print("⚠️ 发现代码质量问题，建议修复后推送")
            return 0  # 警告但不阻止推送
        return 0
    
    print("请指定操作参数")
    return 1

if __name__ == "__main__":
    sys.exit(main())

