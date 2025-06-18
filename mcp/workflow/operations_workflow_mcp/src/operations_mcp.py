#!/usr/bin/env python3
"""
PowerAutomation Operations MCP - 大MCP主协调器
统一管理所有运维相关的子MCP
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import importlib
import os
import sys

# 添加子MCP路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'sub_mcps'))

logger = logging.getLogger(__name__)

class OperationsMCP:
    """
    Operations MCP - 大MCP主协调器
    
    管理的子MCP:
    1. continuous_refactoring_mcp - 持续重构
    2. directory_structure_mcp - 目录结构检查
    3. performance_monitoring_mcp - 性能监控
    4. health_check_mcp - 健康检查
    5. log_analysis_mcp - 日志分析
    6. resource_management_mcp - 资源管理
    7. alert_management_mcp - 告警管理
    8. documentation_management_mcp - 文档管理
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化Operations MCP大协调器"""
        self.config = config or {}
        self.name = "OperationsMCP"
        self.version = "2.0.0"
        
        # 子MCP注册表
        self.sub_mcps = {}
        
        # 运行状态
        self.is_running = False
        self.start_time = None
        
        # 性能指标
        self.metrics = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "sub_mcp_count": 0,
            "uptime": 0
        }
        
        logger.info(f"🏗️ {self.name} v{self.version} 初始化完成 - 大MCP协调器已就位")
    
    async def initialize_sub_mcps(self):
        """初始化所有子MCP"""
        sub_mcp_modules = [
            "continuous_refactoring_mcp",
            "directory_structure_mcp", 
            "performance_monitoring_mcp",
            "health_check_mcp",
            "log_analysis_mcp",
            "resource_management_mcp",
            "alert_management_mcp",
            "documentation_management_mcp"
        ]
        
        for module_name in sub_mcp_modules:
            try:
                # 动态导入子MCP
                module = importlib.import_module(f"{module_name}.{module_name}")
                mcp_class = getattr(module, f"{module_name.title().replace('_', '')}MCP")
                
                # 实例化子MCP
                sub_mcp = mcp_class(config=self.config.get(module_name, {}))
                self.sub_mcps[module_name] = sub_mcp
                
                logger.info(f"✅ 子MCP {module_name} 初始化成功")
                
            except Exception as e:
                logger.warning(f"⚠️ 子MCP {module_name} 初始化失败: {e}")
        
        self.metrics["sub_mcp_count"] = len(self.sub_mcps)
        logger.info(f"🎯 Operations MCP 已加载 {self.metrics['sub_mcp_count']} 个子MCP")
    
    async def start(self):
        """启动Operations MCP"""
        if self.is_running:
            logger.warning("Operations MCP 已在运行中")
            return
        
        logger.info("🚀 启动 Operations MCP 大协调器...")
        
        # 初始化子MCP
        await self.initialize_sub_mcps()
        
        # 启动所有子MCP
        for name, sub_mcp in self.sub_mcps.items():
            try:
                if hasattr(sub_mcp, 'start'):
                    await sub_mcp.start()
                logger.info(f"✅ 子MCP {name} 启动成功")
            except Exception as e:
                logger.error(f"❌ 子MCP {name} 启动失败: {e}")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("🎉 Operations MCP 大协调器启动完成！")
    
    async def stop(self):
        """停止Operations MCP"""
        if not self.is_running:
            logger.warning("Operations MCP 未在运行")
            return
        
        logger.info("🛑 停止 Operations MCP 大协调器...")
        
        # 停止所有子MCP
        for name, sub_mcp in self.sub_mcps.items():
            try:
                if hasattr(sub_mcp, 'stop'):
                    await sub_mcp.stop()
                logger.info(f"✅ 子MCP {name} 停止成功")
            except Exception as e:
                logger.error(f"❌ 子MCP {name} 停止失败: {e}")
        
        self.is_running = False
        logger.info("🎉 Operations MCP 大协调器停止完成！")
    
    async def execute_operation(self, operation_type: str, target_mcp: str, **kwargs) -> Dict[str, Any]:
        """执行运维操作"""
        if not self.is_running:
            raise RuntimeError("Operations MCP 未启动")
        
        if target_mcp not in self.sub_mcps:
            raise ValueError(f"未找到子MCP: {target_mcp}")
        
        try:
            self.metrics["total_operations"] += 1
            
            # 调用子MCP执行操作
            sub_mcp = self.sub_mcps[target_mcp]
            result = await sub_mcp.execute(operation_type, **kwargs)
            
            self.metrics["successful_operations"] += 1
            
            logger.info(f"✅ 运维操作成功: {target_mcp}.{operation_type}")
            return {
                "status": "success",
                "target_mcp": target_mcp,
                "operation": operation_type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.metrics["failed_operations"] += 1
            logger.error(f"❌ 运维操作失败: {target_mcp}.{operation_type} - {e}")
            
            return {
                "status": "error",
                "target_mcp": target_mcp,
                "operation": operation_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.metrics["uptime"] = uptime
        
        sub_mcp_status = {}
        for name, sub_mcp in self.sub_mcps.items():
            try:
                if hasattr(sub_mcp, 'get_status'):
                    status = await sub_mcp.get_status()
                else:
                    status = {"status": "unknown"}
                sub_mcp_status[name] = status
            except Exception as e:
                sub_mcp_status[name] = {"status": "error", "error": str(e)}
        
        return {
            "operations_mcp": {
                "name": self.name,
                "version": self.version,
                "status": "running" if self.is_running else "stopped",
                "uptime": self.metrics["uptime"],
                "metrics": self.metrics
            },
            "sub_mcps": sub_mcp_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health_status = {
            "overall_health": "healthy",
            "issues": [],
            "sub_mcp_health": {}
        }
        
        # 检查每个子MCP的健康状态
        for name, sub_mcp in self.sub_mcps.items():
            try:
                if hasattr(sub_mcp, 'health_check'):
                    health = await sub_mcp.health_check()
                else:
                    health = {"status": "unknown"}
                
                health_status["sub_mcp_health"][name] = health
                
                if health.get("status") != "healthy":
                    health_status["issues"].append(f"子MCP {name} 健康状态异常")
                    
            except Exception as e:
                health_status["sub_mcp_health"][name] = {"status": "error", "error": str(e)}
                health_status["issues"].append(f"子MCP {name} 健康检查失败: {e}")
        
        # 判断整体健康状态
        if health_status["issues"]:
            health_status["overall_health"] = "degraded" if len(health_status["issues"]) < len(self.sub_mcps) / 2 else "unhealthy"
        
        return health_status

# 主入口
async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 创建Operations MCP实例
    ops_mcp = OperationsMCP()
    
    try:
        # 启动
        await ops_mcp.start()
        
        # 获取状态
        status = await ops_mcp.get_system_status()
        print(f"系统状态: {status}")
        
        # 健康检查
        health = await ops_mcp.health_check()
        print(f"健康状态: {health}")
        
        # 保持运行
        print("Operations MCP 正在运行... (按 Ctrl+C 停止)")
        while True:
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n收到停止信号...")
    finally:
        await ops_mcp.stop()

if __name__ == "__main__":
    asyncio.run(main())

