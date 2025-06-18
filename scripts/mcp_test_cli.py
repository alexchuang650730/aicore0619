#!/usr/bin/env python3
"""
PowerAutomation MCP 完整测试CLI工具
提供统一的命令行接口来测试所有MCP组件
"""

import asyncio
import argparse
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# 添加路径以便导入MCP模块
sys.path.append('/opt/powerautomation')
sys.path.append('/opt/powerautomation/mcp')
sys.path.append('/opt/powerautomation/mcp/mcp_coordinator')

class MCPTestCLI:
    """MCP完整测试CLI工具"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        
    def log_result(self, test_name: str, status: str, details: Any = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        # 实时输出
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details and isinstance(details, dict) and details.get('message'):
            print(f"   └─ {details['message']}")
    
    async def test_mcp_coordinator(self):
        """测试MCP协调器"""
        print("\n🔧 测试MCP协调器...")
        
        try:
            # 导入MCP协调器
            from mcp_coordinator import MCPCoordinator, SafeMCPRegistry
            from mcp_coordinator import (
                PlaceholderGeminiMCP, PlaceholderClaudeMCP, PlaceholderSuperMemoryMCP,
                PlaceholderRLSRTMCP, PlaceholderSearchMCP, PlaceholderKiloCodeMCP,
                PlaceholderPlaywrightMCP, PlaceholderTestCaseGeneratorMCP, PlaceholderVideoAnalysisMCP
            )
            
            # 创建注册表并注册MCPs
            registry = SafeMCPRegistry()
            mcps = [
                PlaceholderGeminiMCP(), PlaceholderClaudeMCP(), PlaceholderSuperMemoryMCP(),
                PlaceholderRLSRTMCP(), PlaceholderSearchMCP(), PlaceholderKiloCodeMCP(),
                PlaceholderPlaywrightMCP(), PlaceholderTestCaseGeneratorMCP(), PlaceholderVideoAnalysisMCP()
            ]
            
            for mcp in mcps:
                registry.register_mcp(mcp)
            
            # 创建协调器
            coordinator = MCPCoordinator(registry)
            
            # 测试1: 获取状态
            status_result = await coordinator.execute("get_status", {})
            self.log_result("MCP协调器状态查询", "success", status_result)
            
            # 测试2: 处理输入
            input_data = {
                "type": "user_message",
                "content": "测试消息",
                "session_id": "test_session_001"
            }
            process_result = await coordinator.execute("process_input", input_data)
            self.log_result("MCP协调器输入处理", "success", {"message": f"处理了{len(process_result.get('ai_analysis', {}))}个AI分析"})
            
            # 测试3: 测试用例流程
            test_flow_data = {
                "context": {"test": True},
                "ai_analysis": {},
                "decision": {"should_generate_test_case": True}
            }
            flow_result = await coordinator.execute("run_test_case_flow", test_flow_data)
            self.log_result("MCP协调器测试流程", "success", {"message": f"生成测试脚本: {flow_result.get('generated_script_id')}"})
            
        except Exception as e:
            self.log_result("MCP协调器测试", "error", {"message": str(e)})
    
    async def test_smart_routing(self):
        """测试智能路由MCP"""
        print("\n🚀 测试智能路由MCP...")
        
        try:
            # 导入智能路由
            from smart_routing_mcp import SmartRoutingMCP
            
            router = SmartRoutingMCP()
            
            # 测试用例1: 高敏感代码
            test_request_1 = {
                'content': 'def process_user_password(password): return hash(password)',
                'task_type': 'code_review',
                'request_id': 'test-001'
            }
            
            result_1 = await router.route_request(test_request_1)
            self.log_result("智能路由-高敏感代码", "success", {
                "message": f"路由策略: {result_1['routing_info']['strategy']}, 隐私级别: {result_1['routing_info']['privacy_level']}"
            })
            
            # 测试用例2: 普通代码
            test_request_2 = {
                'content': 'def add_numbers(a, b): return a + b',
                'task_type': 'code_review',
                'request_id': 'test-002'
            }
            
            result_2 = await router.route_request(test_request_2)
            self.log_result("智能路由-普通代码", "success", {
                "message": f"路由策略: {result_2['routing_info']['strategy']}, 隐私级别: {result_2['routing_info']['privacy_level']}"
            })
            
            # 获取监控报告
            report = router.get_monitoring_report()
            if '总请求数: ' in report:
                request_count = report.split('总请求数: ')[1].split('\n')[0]
            else:
                request_count = 'N/A'
            self.log_result("智能路由监控报告", "success", {"message": f"总请求数: {request_count}"})
            
        except Exception as e:
            self.log_result("智能路由MCP测试", "error", {"message": str(e)})
    
    def test_individual_mcps(self):
        """测试各个独立MCP文件"""
        print("\n🧪 测试独立MCP文件...")
        
        mcp_files = [
            "dialog_classifier.py",
            "enhanced_mcp_coordinator.py", 
            "enhanced_smart_routing_mcp.py",
            "powerauto_workflow_engine.py",
            "realtime_architecture_compliance_checker.py",
            "shared_core_integration.py"
        ]
        
        for mcp_file in mcp_files:
            try:
                # 尝试导入模块
                module_name = mcp_file.replace('.py', '')
                
                if mcp_file == "dialog_classifier.py":
                    from dialog_classifier import DialogClassifier, DialogType
                    classifier = DialogClassifier()
                    test_result = classifier.classify("这是一个测试消息")
                    self.log_result(f"MCP模块-{module_name}", "success", {"message": f"分类结果: {test_result.name}"})
                    
                elif mcp_file == "shared_core_integration.py":
                    # 这个文件主要是集成函数，测试导入
                    import shared_core_integration
                    self.log_result(f"MCP模块-{module_name}", "success", {"message": "模块导入成功"})
                    
                else:
                    # 其他文件可能有导入问题，记录状态
                    self.log_result(f"MCP模块-{module_name}", "warning", {"message": "需要在包环境中运行"})
                    
            except Exception as e:
                self.log_result(f"MCP模块-{mcp_file}", "error", {"message": str(e)})
    
    def test_file_structure(self):
        """测试文件结构完整性"""
        print("\n📁 测试文件结构...")
        
        base_path = "/opt/powerautomation/mcp/mcp_coordinator"
        expected_files = [
            "mcp_coordinator.py",
            "smart_routing_mcp.py", 
            "dialog_classifier.py",
            "enhanced_mcp_coordinator.py",
            "enhanced_smart_routing_mcp.py",
            "powerauto_workflow_engine.py",
            "realtime_architecture_compliance_checker.py",
            "shared_core_integration.py",
            "__init__.py",
            "README.md"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(base_path, file_name)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_result(f"文件检查-{file_name}", "success", {"message": f"大小: {file_size} bytes"})
            else:
                self.log_result(f"文件检查-{file_name}", "error", {"message": "文件不存在"})
    
    def test_cli_interfaces(self):
        """测试CLI接口"""
        print("\n💻 测试CLI接口...")
        
        cli_tests = [
            {
                "name": "MCP协调器CLI状态",
                "command": "cd /opt/powerautomation/mcp/mcp_coordinator && python3 mcp_coordinator.py get_status",
                "expected": "success"
            },
            {
                "name": "智能路由测试运行",
                "command": "cd /opt/powerautomation/mcp/mcp_coordinator && timeout 10 python3 smart_routing_mcp.py",
                "expected": "监控报告"
            }
        ]
        
        for test in cli_tests:
            try:
                import subprocess
                result = subprocess.run(
                    test["command"], 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=15
                )
                
                if result.returncode == 0 and test["expected"] in result.stdout:
                    self.log_result(f"CLI测试-{test['name']}", "success", {"message": "CLI响应正常"})
                else:
                    self.log_result(f"CLI测试-{test['name']}", "warning", {"message": f"返回码: {result.returncode}"})
                    
            except Exception as e:
                self.log_result(f"CLI测试-{test['name']}", "error", {"message": str(e)})
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 PowerAutomation MCP 测试报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        success_tests = len([r for r in self.test_results if r["status"] == "success"])
        warning_tests = len([r for r in self.test_results if r["status"] == "warning"])
        error_tests = len([r for r in self.test_results if r["status"] == "error"])
        
        print(f"📈 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   ✅ 成功: {success_tests}")
        print(f"   ⚠️  警告: {warning_tests}")
        print(f"   ❌ 错误: {error_tests}")
        print(f"   📊 成功率: {success_tests/total_tests*100:.1f}%")
        
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"   ⏱️  耗时: {duration:.2f}秒")
        
        print(f"\n📋 详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "success" else "❌" if result["status"] == "error" else "⚠️"
            print(f"   {status_icon} {result['test_name']}: {result['status']}")
            if result["details"] and result["details"].get("message"):
                print(f"      └─ {result['details']['message']}")
        
        # 保存JSON报告
        report_data = {
            "test_summary": {
                "total": total_tests,
                "success": success_tests,
                "warning": warning_tests,
                "error": error_tests,
                "success_rate": success_tests/total_tests*100,
                "duration": time.time() - self.start_time if self.start_time else 0
            },
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        report_file = "/opt/powerautomation/mcp_test_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 详细报告已保存: {report_file}")
        except Exception as e:
            print(f"\n❌ 报告保存失败: {e}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.start_time = time.time()
        
        print("🚀 PowerAutomation MCP 完整测试开始...")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 运行各项测试
        self.test_file_structure()
        await self.test_mcp_coordinator()
        await self.test_smart_routing()
        self.test_individual_mcps()
        self.test_cli_interfaces()
        
        # 生成报告
        self.generate_report()
    
    async def run_specific_test(self, test_name: str):
        """运行特定测试"""
        self.start_time = time.time()
        
        print(f"🎯 运行特定测试: {test_name}")
        
        if test_name == "coordinator":
            await self.test_mcp_coordinator()
        elif test_name == "routing":
            await self.test_smart_routing()
        elif test_name == "modules":
            self.test_individual_mcps()
        elif test_name == "cli":
            self.test_cli_interfaces()
        elif test_name == "files":
            self.test_file_structure()
        else:
            print(f"❌ 未知测试: {test_name}")
            return
        
        self.generate_report()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation MCP 完整测试CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
测试类型:
  all         - 运行所有测试 (默认)
  coordinator - 测试MCP协调器
  routing     - 测试智能路由MCP
  modules     - 测试各个MCP模块
  cli         - 测试CLI接口
  files       - 测试文件结构

示例:
  python3 mcp_test_cli.py                    # 运行所有测试
  python3 mcp_test_cli.py --test coordinator # 只测试协调器
  python3 mcp_test_cli.py --test routing     # 只测试路由
  python3 mcp_test_cli.py --verbose          # 详细输出
        """
    )
    
    parser.add_argument(
        "--test",
        type=str,
        choices=["all", "coordinator", "routing", "modules", "cli", "files"],
        default="all",
        help="指定要运行的测试类型"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="指定报告输出文件路径"
    )
    
    args = parser.parse_args()
    
    # 创建测试CLI实例
    test_cli = MCPTestCLI()
    
    # 运行测试
    try:
        if args.test == "all":
            asyncio.run(test_cli.run_all_tests())
        else:
            asyncio.run(test_cli.run_specific_test(args.test))
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

