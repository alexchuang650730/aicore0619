#!/usr/bin/env python3
"""
目录结构检查子MCP
负责项目目录结构的合规性检查和自动修复
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

class DirectoryStructureMcp:
    """目录结构检查子MCP"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = "DirectoryStructureMCP"
        self.is_running = False
        
        # 标准目录结构
        self.standard_structure = {
            "mcp/adapters/": "MCP适配器目录",
            "workflow/": "工作流目录", 
            "docs/mcphowto/": "MCP开发指南",
            "docs/workflowhowto/": "工作流指南",
            "src/": "源代码目录",
            "tests/": "测试目录",
            "config/": "配置目录",
            "scripts/": "脚本目录",
            "logs/": "日志目录"
        }
        
        logger.info(f"📁 {self.name} 初始化完成")
    
    async def start(self):
        """启动目录结构检查"""
        self.is_running = True
        logger.info(f"🚀 {self.name} 启动")
    
    async def stop(self):
        """停止目录结构检查"""
        self.is_running = False
        logger.info(f"🛑 {self.name} 停止")
    
    async def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """执行目录结构操作"""
        if operation == "check_structure":
            return await self.check_directory_structure(kwargs.get("path", "."))
        elif operation == "fix_structure":
            return await self.fix_directory_structure(kwargs.get("path", "."))
        elif operation == "validate_mcp_structure":
            return await self.validate_mcp_structure(kwargs.get("mcp_path"))
        else:
            raise ValueError(f"未知操作: {operation}")
    
    async def check_directory_structure(self, path: str) -> Dict[str, Any]:
        """检查目录结构"""
        issues = []
        missing_dirs = []
        
        # 检查标准目录是否存在
        for dir_path, description in self.standard_structure.items():
            full_path = os.path.join(path, dir_path)
            if not os.path.exists(full_path):
                missing_dirs.append({
                    "path": dir_path,
                    "description": description,
                    "severity": "medium"
                })
        
        # 检查MCP目录结构
        mcp_adapters_path = os.path.join(path, "mcp/adapters")
        if os.path.exists(mcp_adapters_path):
            mcp_issues = await self._check_mcp_adapters(mcp_adapters_path)
            issues.extend(mcp_issues)
        
        return {
            "total_issues": len(issues) + len(missing_dirs),
            "missing_directories": missing_dirs,
            "structure_issues": issues,
            "check_time": datetime.now().isoformat()
        }
    
    async def _check_mcp_adapters(self, adapters_path: str) -> List[Dict]:
        """检查MCP适配器目录结构"""
        issues = []
        
        for item in os.listdir(adapters_path):
            item_path = os.path.join(adapters_path, item)
            if os.path.isdir(item_path):
                # 检查每个MCP是否有必需文件
                required_files = ["__init__.py", "README.md"]
                for req_file in required_files:
                    file_path = os.path.join(item_path, req_file)
                    if not os.path.exists(file_path):
                        issues.append({
                            "type": "missing_file",
                            "mcp": item,
                            "missing_file": req_file,
                            "severity": "low"
                        })
        
        return issues
    
    async def fix_directory_structure(self, path: str) -> Dict[str, Any]:
        """修复目录结构"""
        fixes_applied = []
        
        # 创建缺失的标准目录
        for dir_path, description in self.standard_structure.items():
            full_path = os.path.join(path, dir_path)
            if not os.path.exists(full_path):
                try:
                    os.makedirs(full_path, exist_ok=True)
                    
                    # 创建README文件
                    readme_path = os.path.join(full_path, "README.md")
                    if not os.path.exists(readme_path):
                        with open(readme_path, 'w', encoding='utf-8') as f:
                            f.write(f"# {description}\n\n此目录用于{description}。\n")
                    
                    fixes_applied.append({
                        "type": "create_directory",
                        "path": dir_path,
                        "description": description
                    })
                    
                except Exception as e:
                    logger.error(f"创建目录失败 {dir_path}: {e}")
        
        return {
            "fixes_applied": len(fixes_applied),
            "details": fixes_applied,
            "fix_time": datetime.now().isoformat()
        }
    
    async def validate_mcp_structure(self, mcp_path: str) -> Dict[str, Any]:
        """验证单个MCP的目录结构"""
        if not os.path.exists(mcp_path):
            return {"valid": False, "error": "MCP路径不存在"}
        
        required_files = ["__init__.py", "README.md"]
        missing_files = []
        
        for req_file in required_files:
            file_path = os.path.join(mcp_path, req_file)
            if not os.path.exists(file_path):
                missing_files.append(req_file)
        
        return {
            "valid": len(missing_files) == 0,
            "missing_files": missing_files,
            "mcp_path": mcp_path
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "status": "running" if self.is_running else "stopped",
            "name": self.name,
            "standard_dirs_count": len(self.standard_structure)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "last_check": datetime.now().isoformat()
        }

