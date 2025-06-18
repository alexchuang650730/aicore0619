#!/usr/bin/env python3
"""
Operations Workflow MCP - Main Service
Operations Workflow MCP 主服务 - 统一的运行入口
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

# 添加项目根目录到Python路径
repo_root = Path("/home/ubuntu/kilocode_integrated_repo")
sys.path.insert(0, str(repo_root))

from mcp.workflow.operations_workflow_mcp.src.mcp_registry_manager import MCPRegistryManager
from mcp.workflow.operations_workflow_mcp.src.smart_intervention_coordinator import SmartInterventionCoordinator
from mcp.workflow.operations_workflow_mcp.src.directory_structure_manager import DirectoryStructureManager
from mcp.workflow.operations_workflow_mcp.src.file_placement_manager import FilePlacementManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OperationsWorkflowMCPService:
    """Operations Workflow MCP 主服务"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.running = False
        self.services = {}
        
        # 初始化各个组件
        self.registry_manager = MCPRegistryManager(repo_root)
        self.intervention_coordinator = SmartInterventionCoordinator(repo_root)
        self.directory_manager = DirectoryStructureManager(repo_root)
        self.file_placement_manager = FilePlacementManager(repo_root)
        
        # 服务状态
        self.start_time = None
        self.status = "STOPPED"
        
        logger.info("🚀 Operations Workflow MCP Service 初始化完成")
    
    async def start_service(self):
        """启动服务"""
        try:
            self.status = "STARTING"
            self.start_time = datetime.now()
            
            logger.info("🔄 启动 Operations Workflow MCP Service...")
            
            # 1. 自动发现和注册MCP
            logger.info("📋 自动发现和注册MCP...")
            await self._auto_register_mcps()
            
            # 2. 启动智能介入协调器
            logger.info("🎯 启动智能介入协调器...")
            await self._start_intervention_coordinator()
            
            # 3. 启动目录结构监控
            logger.info("🗂️ 启动目录结构监控...")
            await self._start_directory_monitoring()
            
            # 4. 启动文件放置监控
            logger.info("📁 启动文件放置监控...")
            await self._start_file_placement_monitoring()
            
            self.running = True
            self.status = "RUNNING"
            
            logger.info("✅ Operations Workflow MCP Service 启动成功")
            
            # 启动主循环
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"❌ 服务启动失败: {e}")
            self.status = "ERROR"
            raise
    
    async def _auto_register_mcps(self):
        """自动发现和注册MCP"""
        try:
            # 自动发现MCP
            discovered = self.registry_manager.auto_discover_mcps()
            logger.info(f"发现 {discovered['total']} 个MCP")
            
            # 注册所有发现的MCP
            for adapter in discovered['adapters']:
                if adapter['name'] not in [mcp['name'] for mcp in self.registry_manager.get_registry_status()['mcps']]:
                    success = self.registry_manager.register_mcp(
                        name=adapter['name'],
                        mcp_type=self.registry_manager.MCPType.ADAPTER,
                        path=adapter['path'],
                        class_name=adapter['class_name'] or f"{adapter['name'].replace('_', '').title()}",
                        capabilities=adapter['capabilities'],
                        description=adapter['description'] or f"{adapter['name']} 适配器"
                    )
                    if success:
                        logger.info(f"✅ 注册MCP: {adapter['name']}")
            
            # 健康检查
            health = self.registry_manager.health_check_all()
            logger.info(f"健康检查: {health['healthy']}/{health['total_checked']} 健康")
            
        except Exception as e:
            logger.error(f"❌ MCP注册失败: {e}")
    
    async def _start_intervention_coordinator(self):
        """启动智能介入协调器"""
        try:
            # 创建后台任务处理介入队列
            self.services['intervention_task'] = asyncio.create_task(
                self._intervention_loop()
            )
            logger.info("✅ 智能介入协调器启动成功")
        except Exception as e:
            logger.error(f"❌ 智能介入协调器启动失败: {e}")
    
    async def _intervention_loop(self):
        """介入处理循环"""
        while self.running:
            try:
                # 处理介入队列
                await self.intervention_coordinator.process_intervention_queue()
                
                # 等待一段时间再次检查
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ 介入处理循环错误: {e}")
                await asyncio.sleep(10)
    
    async def _start_directory_monitoring(self):
        """启动目录结构监控"""
        try:
            # 创建后台任务监控目录结构
            self.services['directory_task'] = asyncio.create_task(
                self._directory_monitoring_loop()
            )
            logger.info("✅ 目录结构监控启动成功")
        except Exception as e:
            logger.error(f"❌ 目录结构监控启动失败: {e}")
    
    async def _directory_monitoring_loop(self):
        """目录结构监控循环"""
        while self.running:
            try:
                # 检查目录结构合规性
                violations = self.directory_manager.check_directory_compliance()
                
                if violations:
                    logger.warning(f"发现 {len(violations)} 个目录结构违规")
                    
                    # 创建介入请求
                    for violation in violations:
                        self.intervention_coordinator.request_intervention(
                            self.intervention_coordinator.InterventionType.DIRECTORY_STRUCTURE,
                            self.intervention_coordinator.InterventionPriority.MEDIUM,
                            f"目录结构违规: {violation}",
                            "operations_workflow_mcp",
                            {"violation": violation}
                        )
                
                # 每30分钟检查一次
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"❌ 目录结构监控错误: {e}")
                await asyncio.sleep(300)
    
    async def _start_file_placement_monitoring(self):
        """启动文件放置监控"""
        try:
            # 创建后台任务监控文件上传
            self.services['file_placement_task'] = asyncio.create_task(
                self._file_placement_loop()
            )
            logger.info("✅ 文件放置监控启动成功")
        except Exception as e:
            logger.error(f"❌ 文件放置监控启动失败: {e}")
    
    async def _file_placement_loop(self):
        """文件放置监控循环"""
        while self.running:
            try:
                # 检查上传目录是否有新文件
                upload_dir = self.repo_root / "upload"
                if upload_dir.exists():
                    # 分析上传文件
                    analysis = self.file_placement_manager.analyze_upload_files()
                    
                    if analysis['placement_plan']:
                        logger.info(f"发现 {len(analysis['placement_plan'])} 个文件需要放置")
                        
                        # 执行文件放置
                        results = self.file_placement_manager.execute_placement_plan(
                            analysis['placement_plan']
                        )
                        
                        if results['successful'] > 0:
                            logger.info(f"成功放置 {results['successful']} 个文件")
                            
                            # 清理上传目录
                            self.file_placement_manager.cleanup_upload_directory()
                
                # 每5分钟检查一次
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"❌ 文件放置监控错误: {e}")
                await asyncio.sleep(60)
    
    async def _main_loop(self):
        """主循环"""
        logger.info("🔄 进入主循环...")
        
        try:
            while self.running:
                # 定期报告状态
                await self._report_status()
                
                # 等待10分钟
                await asyncio.sleep(600)
                
        except asyncio.CancelledError:
            logger.info("📴 主循环被取消")
        except Exception as e:
            logger.error(f"❌ 主循环错误: {e}")
    
    async def _report_status(self):
        """报告服务状态"""
        try:
            status = self.get_service_status()
            
            logger.info(f"📊 服务状态报告:")
            logger.info(f"  - 运行时间: {status['uptime']}")
            logger.info(f"  - 注册MCP: {status['registry']['total_registered']}")
            logger.info(f"  - 活跃实例: {status['registry']['active_instances']}")
            logger.info(f"  - 介入队列: {status['intervention']['queue_size']}")
            logger.info(f"  - 已完成介入: {status['intervention']['completed_interventions']}")
            
        except Exception as e:
            logger.error(f"❌ 状态报告错误: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            "status": self.status,
            "uptime": f"{uptime:.0f}秒",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "running_services": len(self.services),
            "registry": self.registry_manager.get_registry_status(),
            "intervention": self.intervention_coordinator.get_coordinator_status()
        }
    
    async def stop_service(self):
        """停止服务"""
        logger.info("🛑 停止 Operations Workflow MCP Service...")
        
        self.running = False
        self.status = "STOPPING"
        
        # 取消所有后台任务
        for service_name, task in self.services.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"📴 {service_name} 已停止")
        
        self.status = "STOPPED"
        logger.info("✅ Operations Workflow MCP Service 已停止")
    
    def handle_signal(self, signum, frame):
        """处理信号"""
        logger.info(f"📡 收到信号 {signum}")
        asyncio.create_task(self.stop_service())

async def main():
    """主函数"""
    service = OperationsWorkflowMCPService()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, service.handle_signal)
    signal.signal(signal.SIGTERM, service.handle_signal)
    
    try:
        await service.start_service()
    except KeyboardInterrupt:
        logger.info("📴 收到键盘中断")
    except Exception as e:
        logger.error(f"❌ 服务运行错误: {e}")
    finally:
        await service.stop_service()

if __name__ == "__main__":
    print("🚀 启动 Operations Workflow MCP Service")
    print("=" * 60)
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n📴 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

