#!/usr/bin/env python3
"""
Operations Workflow MCP - MCP Registry Manager
MCP注册管理器 - 负责管理和协调所有小型MCP适配器
"""

import os
import json
import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class MCPType(Enum):
    """MCP类型"""
    ADAPTER = "adapter"      # 小型MCP适配器
    WORKFLOW = "workflow"    # 大型MCP工作流

class MCPStatus(Enum):
    """MCP状态"""
    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"

@dataclass
class MCPRegistration:
    """MCP注册信息"""
    name: str
    type: MCPType
    path: str
    class_name: str
    status: MCPStatus
    capabilities: List[str]
    version: str = "1.0.0"
    description: str = ""
    dependencies: List[str] = None
    registered_at: str = None
    last_health_check: str = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.registered_at is None:
            self.registered_at = datetime.now().isoformat()

class MCPRegistryManager:
    """MCP注册管理器"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.registry: Dict[str, MCPRegistration] = {}
        self.active_instances: Dict[str, Any] = {}
        self.registry_file = self.repo_root / "mcp" / "workflow" / "operations_workflow_mcp" / "config" / "mcp_registry.json"
        
        # 确保配置目录存在
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有注册信息
        self._load_registry()
        
        logger.info("🗂️ MCP Registry Manager 初始化完成")
    
    def _load_registry(self):
        """加载注册表"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, reg_data in data.items():
                        self.registry[name] = MCPRegistration(
                            name=reg_data['name'],
                            type=MCPType(reg_data['type']),
                            path=reg_data['path'],
                            class_name=reg_data['class_name'],
                            status=MCPStatus(reg_data['status']),
                            capabilities=reg_data['capabilities'],
                            version=reg_data.get('version', '1.0.0'),
                            description=reg_data.get('description', ''),
                            dependencies=reg_data.get('dependencies', []),
                            registered_at=reg_data.get('registered_at'),
                            last_health_check=reg_data.get('last_health_check')
                        )
                logger.info(f"📋 加载了 {len(self.registry)} 个MCP注册信息")
            except Exception as e:
                logger.error(f"❌ 加载注册表失败: {e}")
                self.registry = {}
    
    def _save_registry(self):
        """保存注册表"""
        try:
            registry_data = {}
            for name, registration in self.registry.items():
                registry_data[name] = asdict(registration)
                # 转换Enum为字符串
                registry_data[name]['type'] = registration.type.value
                registry_data[name]['status'] = registration.status.value
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 保存了 {len(self.registry)} 个MCP注册信息")
        except Exception as e:
            logger.error(f"❌ 保存注册表失败: {e}")
    
    def auto_discover_mcps(self) -> Dict[str, Any]:
        """自动发现MCP"""
        discovered = {
            "adapters": [],
            "workflows": [],
            "total": 0
        }
        
        # 扫描adapter目录
        adapter_dir = self.repo_root / "mcp" / "adapter"
        if adapter_dir.exists():
            for mcp_dir in adapter_dir.iterdir():
                if mcp_dir.is_dir() and mcp_dir.name.endswith('_mcp'):
                    mcp_info = self._analyze_mcp_directory(mcp_dir, MCPType.ADAPTER)
                    if mcp_info:
                        discovered["adapters"].append(mcp_info)
        
        # 扫描workflow目录
        workflow_dir = self.repo_root / "mcp" / "workflow"
        if workflow_dir.exists():
            for mcp_dir in workflow_dir.iterdir():
                if mcp_dir.is_dir() and mcp_dir.name.endswith('_mcp'):
                    mcp_info = self._analyze_mcp_directory(mcp_dir, MCPType.WORKFLOW)
                    if mcp_info:
                        discovered["workflows"].append(mcp_info)
        
        discovered["total"] = len(discovered["adapters"]) + len(discovered["workflows"])
        
        logger.info(f"🔍 自动发现 {discovered['total']} 个MCP")
        return discovered
    
    def _analyze_mcp_directory(self, mcp_dir: Path, mcp_type: MCPType) -> Optional[Dict]:
        """分析MCP目录"""
        try:
            # 查找主要的Python文件
            main_file = None
            for py_file in mcp_dir.glob("*.py"):
                if py_file.name == f"{mcp_dir.name}.py":
                    main_file = py_file
                    break
            
            if not main_file:
                # 查找其他可能的主文件
                for py_file in mcp_dir.glob("*.py"):
                    if "mcp" in py_file.name.lower():
                        main_file = py_file
                        break
            
            if main_file:
                # 分析Python文件获取类信息
                class_info = self._analyze_python_file(main_file)
                
                return {
                    "name": mcp_dir.name,
                    "type": mcp_type,
                    "path": str(mcp_dir.relative_to(self.repo_root)),
                    "main_file": main_file.name,
                    "class_name": class_info.get("main_class"),
                    "capabilities": class_info.get("capabilities", []),
                    "description": class_info.get("description", "")
                }
        except Exception as e:
            logger.error(f"❌ 分析MCP目录 {mcp_dir} 失败: {e}")
        
        return None
    
    def _analyze_python_file(self, py_file: Path) -> Dict:
        """分析Python文件"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的类名提取
            import re
            class_matches = re.findall(r'class\s+(\w+MCP)\s*[:\(]', content)
            main_class = class_matches[0] if class_matches else None
            
            # 提取文档字符串作为描述
            doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            description = doc_match.group(1).strip() if doc_match else ""
            
            # 简单的能力提取（基于方法名）
            method_matches = re.findall(r'def\s+(\w+)', content)
            capabilities = [method for method in method_matches if not method.startswith('_')]
            
            return {
                "main_class": main_class,
                "description": description,
                "capabilities": capabilities[:10]  # 限制数量
            }
        except Exception as e:
            logger.error(f"❌ 分析Python文件 {py_file} 失败: {e}")
            return {}
    
    def register_mcp(self, name: str, mcp_type: MCPType, path: str, class_name: str, 
                     capabilities: List[str], description: str = "", 
                     dependencies: List[str] = None) -> bool:
        """注册MCP"""
        try:
            registration = MCPRegistration(
                name=name,
                type=mcp_type,
                path=path,
                class_name=class_name,
                status=MCPStatus.REGISTERED,
                capabilities=capabilities,
                description=description,
                dependencies=dependencies or []
            )
            
            self.registry[name] = registration
            self._save_registry()
            
            logger.info(f"✅ 成功注册MCP: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 注册MCP {name} 失败: {e}")
            return False
    
    def load_mcp(self, name: str) -> Optional[Any]:
        """加载MCP实例"""
        if name not in self.registry:
            logger.error(f"❌ MCP {name} 未注册")
            return None
        
        if name in self.active_instances:
            return self.active_instances[name]
        
        try:
            registration = self.registry[name]
            
            # 构建模块路径
            module_path = registration.path.replace('/', '.').replace('\\', '.')
            if module_path.startswith('.'):
                module_path = module_path[1:]
            
            # 动态导入模块
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                f"{name}_module",
                self.repo_root / registration.path / f"{name}.py"
            )
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 获取MCP类
                mcp_class = getattr(module, registration.class_name)
                
                # 创建实例
                instance = mcp_class()
                self.active_instances[name] = instance
                
                # 更新状态
                registration.status = MCPStatus.ACTIVE
                registration.last_health_check = datetime.now().isoformat()
                self._save_registry()
                
                logger.info(f"✅ 成功加载MCP: {name}")
                return instance
            
        except Exception as e:
            logger.error(f"❌ 加载MCP {name} 失败: {e}")
            if name in self.registry:
                self.registry[name].status = MCPStatus.ERROR
                self._save_registry()
        
        return None
    
    def call_mcp_method(self, mcp_name: str, method_name: str, *args, **kwargs) -> Any:
        """调用MCP方法"""
        instance = self.load_mcp(mcp_name)
        if not instance:
            return None
        
        try:
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                result = method(*args, **kwargs)
                logger.info(f"✅ 成功调用 {mcp_name}.{method_name}")
                return result
            else:
                logger.error(f"❌ MCP {mcp_name} 没有方法 {method_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 调用 {mcp_name}.{method_name} 失败: {e}")
            return None
    
    def get_registry_status(self) -> Dict[str, Any]:
        """获取注册表状态"""
        status = {
            "total_registered": len(self.registry),
            "active_instances": len(self.active_instances),
            "by_type": {"adapter": 0, "workflow": 0},
            "by_status": {"registered": 0, "active": 0, "inactive": 0, "error": 0},
            "mcps": []
        }
        
        for name, registration in self.registry.items():
            status["by_type"][registration.type.value] += 1
            status["by_status"][registration.status.value] += 1
            
            status["mcps"].append({
                "name": name,
                "type": registration.type.value,
                "status": registration.status.value,
                "capabilities": len(registration.capabilities),
                "has_instance": name in self.active_instances
            })
        
        return status
    
    def health_check_all(self) -> Dict[str, Any]:
        """对所有MCP进行健康检查"""
        results = {
            "total_checked": 0,
            "healthy": 0,
            "unhealthy": 0,
            "details": []
        }
        
        for name, registration in self.registry.items():
            try:
                instance = self.load_mcp(name)
                if instance and hasattr(instance, 'get_status'):
                    status = instance.get_status()
                    is_healthy = status.get('status') in ['ACTIVE', 'active', 'healthy']
                    
                    results["details"].append({
                        "name": name,
                        "healthy": is_healthy,
                        "status": status
                    })
                    
                    if is_healthy:
                        results["healthy"] += 1
                        registration.status = MCPStatus.ACTIVE
                    else:
                        results["unhealthy"] += 1
                        registration.status = MCPStatus.INACTIVE
                        
                    registration.last_health_check = datetime.now().isoformat()
                    
                else:
                    results["details"].append({
                        "name": name,
                        "healthy": False,
                        "status": "无法加载或缺少get_status方法"
                    })
                    results["unhealthy"] += 1
                    registration.status = MCPStatus.ERROR
                    
                results["total_checked"] += 1
                
            except Exception as e:
                results["details"].append({
                    "name": name,
                    "healthy": False,
                    "status": f"健康检查失败: {e}"
                })
                results["unhealthy"] += 1
                registration.status = MCPStatus.ERROR
        
        self._save_registry()
        return results

if __name__ == "__main__":
    # 测试MCP注册管理器
    manager = MCPRegistryManager()
    
    print("🔍 自动发现MCP...")
    discovered = manager.auto_discover_mcps()
    print(f"发现 {discovered['total']} 个MCP")
    
    print("\n📋 注册表状态...")
    status = manager.get_registry_status()
    print(f"已注册: {status['total_registered']} 个")
    print(f"活跃实例: {status['active_instances']} 个")
    
    print("\n🏥 健康检查...")
    health = manager.health_check_all()
    print(f"检查了 {health['total_checked']} 个MCP")
    print(f"健康: {health['healthy']} 个，不健康: {health['unhealthy']} 个")

