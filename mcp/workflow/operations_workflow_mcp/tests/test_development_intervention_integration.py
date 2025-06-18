#!/usr/bin/env python3
"""
Operations Workflow MCP - Development Intervention Integration Test
Development Intervention MCP 整合功能测试
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
repo_root = Path("/home/ubuntu/kilocode_integrated_repo")
sys.path.insert(0, str(repo_root))

from mcp.workflow.operations_workflow_mcp.src.mcp_registry_manager import MCPRegistryManager, MCPType
from mcp.workflow.operations_workflow_mcp.src.smart_intervention_coordinator import (
    SmartInterventionCoordinator, InterventionType, InterventionPriority
)

class DevelopmentInterventionIntegrationTest:
    """Development Intervention MCP 整合测试"""
    
    def __init__(self):
        self.registry_manager = MCPRegistryManager()
        self.intervention_coordinator = SmartInterventionCoordinator()
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results["failed"] += 1
            status = "❌ FAIL"
        
        self.test_results["details"].append({
            "test": test_name,
            "status": status,
            "message": message
        })
        
        print(f"{status} {test_name}: {message}")
    
    def test_mcp_registry_discovery(self):
        """测试MCP注册表自动发现功能"""
        print("\n🔍 测试1: MCP注册表自动发现功能")
        
        try:
            discovered = self.registry_manager.auto_discover_mcps()
            
            # 检查是否发现了Development Intervention MCP
            dev_mcp_found = any(
                adapter['name'] == 'development_intervention_mcp' 
                for adapter in discovered['adapters']
            )
            
            if dev_mcp_found:
                self.log_test_result(
                    "MCP自动发现",
                    True,
                    f"成功发现 {discovered['total']} 个MCP，包括Development Intervention MCP"
                )
            else:
                self.log_test_result(
                    "MCP自动发现",
                    False,
                    "未发现Development Intervention MCP"
                )
                
        except Exception as e:
            self.log_test_result("MCP自动发现", False, f"异常: {e}")
    
    def test_development_intervention_registration(self):
        """测试Development Intervention MCP注册"""
        print("\n📝 测试2: Development Intervention MCP注册")
        
        try:
            # 注册Development Intervention MCP
            success = self.registry_manager.register_mcp(
                name="development_intervention_mcp",
                mcp_type=MCPType.ADAPTER,
                path="mcp/adapter/development_intervention_mcp",
                class_name="DevelopmentInterventionMCP",
                capabilities=["code_analysis", "intervention_decision", "auto_fix", "quality_check"],
                description="智能开发介入MCP，提供代码分析和自动修复功能"
            )
            
            if success:
                # 检查注册状态
                status = self.registry_manager.get_registry_status()
                registered = any(
                    mcp['name'] == 'development_intervention_mcp' 
                    for mcp in status['mcps']
                )
                
                if registered:
                    self.log_test_result(
                        "MCP注册",
                        True,
                        f"成功注册，总注册数: {status['total_registered']}"
                    )
                else:
                    self.log_test_result("MCP注册", False, "注册后未在注册表中找到")
            else:
                self.log_test_result("MCP注册", False, "注册失败")
                
        except Exception as e:
            self.log_test_result("MCP注册", False, f"异常: {e}")
    
    def test_development_intervention_loading(self):
        """测试Development Intervention MCP加载"""
        print("\n📥 测试3: Development Intervention MCP加载")
        
        try:
            # 加载Development Intervention MCP
            dev_mcp = self.registry_manager.load_mcp('development_intervention_mcp')
            
            if dev_mcp:
                # 测试获取状态
                if hasattr(dev_mcp, 'get_status'):
                    status = dev_mcp.get_status()
                    if status and status.get('status') == 'ACTIVE':
                        self.log_test_result(
                            "MCP加载",
                            True,
                            f"成功加载，状态: {status.get('status')}"
                        )
                    else:
                        self.log_test_result("MCP加载", False, f"状态异常: {status}")
                else:
                    self.log_test_result("MCP加载", False, "缺少get_status方法")
            else:
                self.log_test_result("MCP加载", False, "加载返回None")
                
        except Exception as e:
            self.log_test_result("MCP加载", False, f"异常: {e}")
    
    def test_intervention_analysis(self):
        """测试介入分析功能"""
        print("\n🧠 测试4: 介入分析功能")
        
        try:
            # 加载Development Intervention MCP
            dev_mcp = self.registry_manager.load_mcp('development_intervention_mcp')
            
            if dev_mcp and hasattr(dev_mcp, 'analyze_intervention_need'):
                # 测试介入分析
                test_scenario = {
                    "type": "code_quality_issue",
                    "description": "发现代码质量问题",
                    "severity": "high",
                    "files": ["test.py", "main.py"]
                }
                
                result = dev_mcp.analyze_intervention_need(test_scenario)
                
                if result and result.get('need_intervention'):
                    self.log_test_result(
                        "介入分析",
                        True,
                        f"分析成功，介入类型: {result.get('intervention_type')}"
                    )
                else:
                    self.log_test_result("介入分析", False, f"分析结果异常: {result}")
            else:
                self.log_test_result("介入分析", False, "MCP未加载或缺少分析方法")
                
        except Exception as e:
            self.log_test_result("介入分析", False, f"异常: {e}")
    
    async def test_intervention_coordination(self):
        """测试介入协调功能"""
        print("\n🎯 测试5: 介入协调功能")
        
        try:
            # 创建介入请求
            intervention_id = self.intervention_coordinator.request_intervention(
                InterventionType.CODE_QUALITY,
                InterventionPriority.HIGH,
                "测试代码质量介入",
                "operations_workflow_mcp",
                {"test_mode": True}
            )
            
            if intervention_id:
                # 检查介入状态
                status = self.intervention_coordinator.get_intervention_status(intervention_id)
                
                if status and status['status'] == 'pending':
                    # 处理介入队列
                    await self.intervention_coordinator.process_intervention_queue()
                    
                    # 等待处理完成
                    max_wait = 10  # 最多等待10秒
                    wait_count = 0
                    
                    while wait_count < max_wait:
                        if not self.intervention_coordinator.active_interventions:
                            break
                        await asyncio.sleep(0.5)
                        wait_count += 0.5
                    
                    # 检查最终状态
                    final_status = self.intervention_coordinator.get_intervention_status(intervention_id)
                    
                    if final_status and final_status['status'] == 'completed':
                        self.log_test_result(
                            "介入协调",
                            True,
                            f"介入成功完成，ID: {intervention_id}"
                        )
                    else:
                        self.log_test_result(
                            "介入协调",
                            False,
                            f"介入未完成，状态: {final_status.get('status') if final_status else 'None'}"
                        )
                else:
                    self.log_test_result("介入协调", False, f"介入状态异常: {status}")
            else:
                self.log_test_result("介入协调", False, "创建介入请求失败")
                
        except Exception as e:
            self.log_test_result("介入协调", False, f"异常: {e}")
    
    def test_mcp_method_calling(self):
        """测试MCP方法调用"""
        print("\n📞 测试6: MCP方法调用")
        
        try:
            # 通过注册管理器调用MCP方法
            result = self.registry_manager.call_mcp_method(
                'development_intervention_mcp',
                'get_status'
            )
            
            if result and isinstance(result, dict):
                if result.get('mcp_name') == 'Development Intervention MCP':
                    self.log_test_result(
                        "MCP方法调用",
                        True,
                        f"成功调用get_status，返回: {result.get('status')}"
                    )
                else:
                    self.log_test_result("MCP方法调用", False, f"返回结果异常: {result}")
            else:
                self.log_test_result("MCP方法调用", False, f"调用失败，返回: {result}")
                
        except Exception as e:
            self.log_test_result("MCP方法调用", False, f"异常: {e}")
    
    def test_health_check(self):
        """测试健康检查"""
        print("\n🏥 测试7: 健康检查")
        
        try:
            health_result = self.registry_manager.health_check_all()
            
            if health_result:
                total_checked = health_result.get('total_checked', 0)
                healthy = health_result.get('healthy', 0)
                
                # 检查Development Intervention MCP的健康状态
                dev_mcp_healthy = False
                for detail in health_result.get('details', []):
                    if detail.get('name') == 'development_intervention_mcp':
                        dev_mcp_healthy = detail.get('healthy', False)
                        break
                
                if dev_mcp_healthy:
                    self.log_test_result(
                        "健康检查",
                        True,
                        f"Development Intervention MCP健康，总检查: {total_checked}，健康: {healthy}"
                    )
                else:
                    self.log_test_result(
                        "健康检查",
                        False,
                        f"Development Intervention MCP不健康，总检查: {total_checked}，健康: {healthy}"
                    )
            else:
                self.log_test_result("健康检查", False, "健康检查返回空结果")
                
        except Exception as e:
            self.log_test_result("健康检查", False, f"异常: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 Development Intervention MCP 整合功能测试")
        print("=" * 70)
        
        # 运行同步测试
        self.test_mcp_registry_discovery()
        self.test_development_intervention_registration()
        self.test_development_intervention_loading()
        self.test_intervention_analysis()
        self.test_mcp_method_calling()
        self.test_health_check()
        
        # 运行异步测试
        await self.test_intervention_coordination()
        
        # 显示测试结果汇总
        self.print_test_summary()
    
    def print_test_summary(self):
        """打印测试结果汇总"""
        print("\n" + "=" * 70)
        print("📊 测试结果汇总")
        print("=" * 70)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {success_rate:.1f}%")
        
        print("\n📋 详细结果:")
        for detail in self.test_results["details"]:
            print(f"{detail['status']} {detail['test']}: {detail['message']}")
        
        if failed == 0:
            print("\n🎉 所有测试通过！Development Intervention MCP 整合成功！")
        else:
            print(f"\n⚠️ 有 {failed} 个测试失败，需要修复")

async def main():
    """主函数"""
    test_runner = DevelopmentInterventionIntegrationTest()
    await test_runner.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

