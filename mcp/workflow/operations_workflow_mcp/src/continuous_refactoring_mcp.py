#!/usr/bin/env python3
"""
持续重构子MCP
负责代码质量监控和自动重构建议
"""

import os
import ast
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class ContinuousRefactoringMcp:
    """持续重构子MCP"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "ContinuousRefactoringMCP"
        self.is_running = False
        
        # 重构规则
        self.refactoring_rules = {
            "code_complexity": {"threshold": 10, "severity": "medium"},
            "function_length": {"threshold": 50, "severity": "low"},
            "duplicate_code": {"threshold": 5, "severity": "high"},
            "naming_convention": {"enabled": True, "severity": "low"}
        }
        
        logger.info(f"🔧 {self.name} 初始化完成")
    
    async def start(self):
        """启动持续重构监控"""
        self.is_running = True
        logger.info(f"🚀 {self.name} 启动")
    
    async def stop(self):
        """停止持续重构监控"""
        self.is_running = False
        logger.info(f"🛑 {self.name} 停止")
    
    async def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """执行重构操作"""
        if operation == "scan_code_quality":
            return await self.scan_code_quality(kwargs.get("path", "."))
        elif operation == "suggest_refactoring":
            return await self.suggest_refactoring(kwargs.get("file_path"))
        elif operation == "apply_auto_fixes":
            return await self.apply_auto_fixes(kwargs.get("fixes", []))
        else:
            raise ValueError(f"未知操作: {operation}")
    
    async def scan_code_quality(self, path: str) -> Dict[str, Any]:
        """扫描代码质量"""
        issues = []
        
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_issues = await self._analyze_file(file_path)
                    issues.extend(file_issues)
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "scan_time": datetime.now().isoformat()
        }
    
    async def _analyze_file(self, file_path: str) -> List[Dict]:
        """分析单个文件"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # 检查函数复杂度
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.refactoring_rules["code_complexity"]["threshold"]:
                        issues.append({
                            "type": "high_complexity",
                            "file": file_path,
                            "function": node.name,
                            "line": node.lineno,
                            "complexity": complexity,
                            "severity": self.refactoring_rules["code_complexity"]["severity"]
                        })
        
        except Exception as e:
            logger.warning(f"分析文件失败 {file_path}: {e}")
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    async def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "status": "running" if self.is_running else "stopped",
            "name": self.name,
            "rules_count": len(self.refactoring_rules)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "last_check": datetime.now().isoformat()
        }

