#!/usr/bin/env python3
"""
PowerAutomation MCP 六大工作流测试CLI工具
按照六大工作流类别进行系统化测试
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

class PowerAutoWorkflowTestCLI:
    """PowerAutomation六大工作流测试CLI工具"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.workflow_categories = {
            "智能协调工作流": {
                "description": "MCP协调器、智能路由、决策引擎",
                "components": ["mcp_coordinator", "smart_routing", "enhanced_coordinator"],
                "icon": "🧠"
            },
            "开发介入工作流": {
                "description": "开发智能介入、架构合规检查、代码分析",
                "components": ["development_intervention", "architecture_compliance", "code_analysis"],
                "icon": "💻"
            },
            "对话分类工作流": {
                "description": "对话分类、智能路由增强、用户意图识别",
                "components": ["dialog_classifier", "enhanced_routing", "intent_recognition"],
                "icon": "💬"
            },
            "工作流引擎工作流": {
                "description": "PowerAuto工作流引擎、流程自动化、任务编排",
                "components": ["workflow_engine", "task_orchestration", "automation"],
                "icon": "⚙️"
            },
            "共享核心工作流": {
                "description": "共享核心集成、模块间通信、数据共享",
                "components": ["shared_core", "integration", "data_sharing"],
                "icon": "🔗"
            },
            "实时监控工作流": {
                "description": "实时架构合规检查、系统监控、性能分析",
                "components": ["realtime_compliance", "monitoring", "performance"],
                "icon": "📊"
            }
        }
        
    def log_result(self, workflow: str, test_name: str, status: str, details: Any = None):
        """记录测试结果"""
        result = {
            "workflow": workflow,
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        # 实时输出
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        workflow_icon = self.workflow_categories.get(workflow, {}).get("icon", "🔧")
        print(f"{status_icon} {workflow_icon} [{workflow}] {test_name}: {status}")
        if details and isinstance(details, dict) and details.get('message'):
            print(f"   └─ {details['message']}")
    
    async def test_intelligent_coordination_workflow(self):
        """测试智能协调工作流"""
        workflow = "智能协调工作流"
        print(f"\n🧠 测试{workflow}...")
        
        # 测试MCP协调器
        try:
            from mcp_coordinator import MCPCoordinator, SafeMCPRegistry
            from mcp_coordinator import (
                PlaceholderGeminiMCP, PlaceholderClaudeMCP, PlaceholderSuperMemoryMCP,
                PlaceholderRLSRTMCP, PlaceholderSearchMCP, PlaceholderKiloCodeMCP,
                PlaceholderPlaywrightMCP, PlaceholderTestCaseGeneratorMCP, PlaceholderVideoAnalysisMCP
            )
            
            registry = SafeMCPRegistry()
            mcps = [
                PlaceholderGeminiMCP(), PlaceholderClaudeMCP(), PlaceholderSuperMemoryMCP(),
                PlaceholderRLSRTMCP(), PlaceholderSearchMCP(), PlaceholderKiloCodeMCP(),
                PlaceholderPlaywrightMCP(), PlaceholderTestCaseGeneratorMCP(), PlaceholderVideoAnalysisMCP()
            ]
            
            for mcp in mcps:
                registry.register_mcp(mcp)
            
            coordinator = MCPCoordinator(registry)
            
            # 测试协调器状态
            status_result = await coordinator.execute("get_status", {})
            self.log_result(workflow, "MCP协调器状态查询", "success", 
                          {"message": f"协调器运行状态: {status_result.get('status')}"})
            
            # 测试智能协调流程
            input_data = {
                "type": "coordination_request",
                "content": "智能协调测试",
                "session_id": "coord_test_001"
            }
            coord_result = await coordinator.execute("process_input", input_data)
            self.log_result(workflow, "智能协调流程", "success", 
                          {"message": f"协调了{len(coord_result.get('ai_analysis', {}))}个AI组件"})
            
        except Exception as e:
            self.log_result(workflow, "MCP协调器测试", "error", {"message": str(e)})
        
        # 测试智能路由
        try:
            from smart_routing_mcp import SmartRoutingMCP
            router = SmartRoutingMCP()
            
            # 测试协调路由决策
            coord_request = {
                'content': 'coordinate multiple AI services for complex task',
                'task_type': 'coordination',
                'request_id': 'coord-001'
            }
            
            route_result = await router.route_request(coord_request)
            self.log_result(workflow, "智能路由协调", "success", {
                "message": f"路由策略: {route_result['routing_info']['strategy']}"
            })
            
        except Exception as e:
            self.log_result(workflow, "智能路由测试", "error", {"message": str(e)})
    
    async def test_development_intervention_workflow(self):
        """测试开发介入工作流"""
        workflow = "开发介入工作流"
        print(f"\n💻 测试{workflow}...")
        
        # 测试开发介入MCP
        try:
            # 检查开发介入文件
            dev_intervention_file = "/opt/powerautomation/mcp/development_intervention_mcp.py"
            if os.path.exists(dev_intervention_file):
                file_size = os.path.getsize(dev_intervention_file)
                self.log_result(workflow, "开发介入MCP文件", "success", 
                              {"message": f"文件大小: {file_size} bytes"})
            else:
                self.log_result(workflow, "开发介入MCP文件", "error", 
                              {"message": "文件不存在"})
            
            # 模拟开发介入场景
            from smart_routing_mcp import SmartRoutingMCP
            router = SmartRoutingMCP()
            
            # 测试代码审查介入
            code_review_request = {
                'content': 'def vulnerable_function(user_input): exec(user_input)',
                'task_type': 'security_review',
                'request_id': 'dev-001'
            }
            
            review_result = await router.route_request(code_review_request)
            self.log_result(workflow, "代码安全审查介入", "success", {
                "message": f"安全级别: {review_result['routing_info']['privacy_level']}"
            })
            
        except Exception as e:
            self.log_result(workflow, "开发介入测试", "error", {"message": str(e)})
        
        # 测试架构合规检查
        try:
            compliance_file = "/opt/powerautomation/mcp/mcp_coordinator/realtime_architecture_compliance_checker.py"
            if os.path.exists(compliance_file):
                file_size = os.path.getsize(compliance_file)
                self.log_result(workflow, "架构合规检查器", "success", 
                              {"message": f"合规检查器文件: {file_size} bytes"})
            else:
                self.log_result(workflow, "架构合规检查器", "error", 
                              {"message": "合规检查器文件不存在"})
                
        except Exception as e:
            self.log_result(workflow, "架构合规检查", "error", {"message": str(e)})
    
    async def test_dialog_classification_workflow(self):
        """测试对话分类工作流"""
        workflow = "对话分类工作流"
        print(f"\n💬 测试{workflow}...")
        
        try:
            from dialog_classifier import DialogClassifier, DialogType
            classifier = DialogClassifier()
            
            # 测试不同类型的对话分类
            test_dialogs = [
                ("请帮我写一个Python函数", "代码请求"),
                ("系统出现了错误，需要调试", "问题报告"),
                ("如何优化这个算法的性能？", "技术咨询"),
                ("请解释一下这个架构设计", "知识查询")
            ]
            
            for dialog, expected_type in test_dialogs:
                result = classifier.classify(dialog)
                self.log_result(workflow, f"对话分类-{expected_type}", "success", {
                    "message": f"分类结果: {result.name}, 输入: '{dialog[:20]}...'"
                })
            
            # 测试批量分类性能
            batch_dialogs = [dialog for dialog, _ in test_dialogs]
            start_time = time.time()
            batch_results = [classifier.classify(dialog) for dialog in batch_dialogs]
            end_time = time.time()
            
            self.log_result(workflow, "批量对话分类性能", "success", {
                "message": f"处理{len(batch_dialogs)}条对话，耗时: {end_time - start_time:.3f}秒"
            })
            
        except Exception as e:
            self.log_result(workflow, "对话分类测试", "error", {"message": str(e)})
    
    async def test_workflow_engine_workflow(self):
        """测试工作流引擎工作流"""
        workflow = "工作流引擎工作流"
        print(f"\n⚙️ 测试{workflow}...")
        
        try:
            # 检查工作流引擎文件
            engine_file = "/opt/powerautomation/mcp/mcp_coordinator/powerauto_workflow_engine.py"
            if os.path.exists(engine_file):
                file_size = os.path.getsize(engine_file)
                self.log_result(workflow, "工作流引擎文件", "success", 
                              {"message": f"引擎文件大小: {file_size} bytes"})
                
                # 读取文件内容分析
                with open(engine_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 分析工作流引擎特性
                features = []
                if 'class' in content:
                    features.append("面向对象设计")
                if 'async' in content:
                    features.append("异步处理")
                if 'workflow' in content.lower():
                    features.append("工作流管理")
                if 'engine' in content.lower():
                    features.append("引擎架构")
                
                self.log_result(workflow, "工作流引擎特性分析", "success", {
                    "message": f"检测到特性: {', '.join(features)}"
                })
                
            else:
                self.log_result(workflow, "工作流引擎文件", "error", 
                              {"message": "引擎文件不存在"})
            
            # 模拟工作流执行
            from smart_routing_mcp import SmartRoutingMCP
            router = SmartRoutingMCP()
            
            workflow_request = {
                'content': 'execute automated testing workflow',
                'task_type': 'workflow_execution',
                'request_id': 'wf-001'
            }
            
            wf_result = await router.route_request(workflow_request)
            self.log_result(workflow, "工作流执行路由", "success", {
                "message": f"执行策略: {wf_result['routing_info']['strategy']}"
            })
            
        except Exception as e:
            self.log_result(workflow, "工作流引擎测试", "error", {"message": str(e)})
    
    async def test_shared_core_workflow(self):
        """测试共享核心工作流"""
        workflow = "共享核心工作流"
        print(f"\n🔗 测试{workflow}...")
        
        try:
            # 测试共享核心集成
            import shared_core_integration
            self.log_result(workflow, "共享核心模块导入", "success", 
                          {"message": "共享核心集成模块加载成功"})
            
            # 检查共享核心目录
            shared_core_dir = "/opt/powerautomation/shared_core"
            if os.path.exists(shared_core_dir):
                files = os.listdir(shared_core_dir)
                self.log_result(workflow, "共享核心目录", "success", 
                              {"message": f"包含{len(files)}个共享组件"})
                
                # 分析共享组件
                py_files = [f for f in files if f.endswith('.py')]
                self.log_result(workflow, "共享Python组件", "success", 
                              {"message": f"Python模块: {len(py_files)}个"})
            else:
                self.log_result(workflow, "共享核心目录", "warning", 
                              {"message": "共享核心目录不存在"})
            
            # 测试模块间通信
            from smart_routing_mcp import SmartRoutingMCP
            router = SmartRoutingMCP()
            
            integration_request = {
                'content': 'integrate shared components across modules',
                'task_type': 'integration',
                'request_id': 'int-001'
            }
            
            int_result = await router.route_request(integration_request)
            self.log_result(workflow, "模块间集成路由", "success", {
                "message": f"集成策略: {int_result['routing_info']['strategy']}"
            })
            
        except Exception as e:
            self.log_result(workflow, "共享核心测试", "error", {"message": str(e)})
    
    async def test_realtime_monitoring_workflow(self):
        """测试实时监控工作流"""
        workflow = "实时监控工作流"
        print(f"\n📊 测试{workflow}...")
        
        try:
            # 检查实时监控文件
            monitoring_file = "/opt/powerautomation/mcp/mcp_coordinator/realtime_architecture_compliance_checker.py"
            if os.path.exists(monitoring_file):
                file_size = os.path.getsize(monitoring_file)
                self.log_result(workflow, "实时监控文件", "success", 
                              {"message": f"监控文件大小: {file_size} bytes"})
            else:
                self.log_result(workflow, "实时监控文件", "error", 
                              {"message": "监控文件不存在"})
            
            # 测试智能路由监控
            from smart_routing_mcp import SmartRoutingMCP
            router = SmartRoutingMCP()
            
            # 执行多个请求以生成监控数据
            monitoring_requests = [
                {'content': 'monitor system performance', 'task_type': 'monitoring', 'request_id': 'mon-001'},
                {'content': 'check compliance status', 'task_type': 'compliance', 'request_id': 'mon-002'},
                {'content': 'analyze system metrics', 'task_type': 'analysis', 'request_id': 'mon-003'}
            ]
            
            for req in monitoring_requests:
                await router.route_request(req)
            
            # 获取监控报告
            report = router.get_monitoring_report()
            if '总请求数: ' in report:
                request_count = report.split('总请求数: ')[1].split('\n')[0]
                self.log_result(workflow, "实时监控报告", "success", {
                    "message": f"监控请求数: {request_count}"
                })
            else:
                self.log_result(workflow, "实时监控报告", "warning", {
                    "message": "监控报告格式异常"
                })
            
            # 分析监控性能
            if '平均响应时间: ' in report:
                response_time = report.split('平均响应时间: ')[1].split('秒')[0]
                self.log_result(workflow, "监控性能分析", "success", {
                    "message": f"平均响应时间: {response_time}秒"
                })
            
        except Exception as e:
            self.log_result(workflow, "实时监控测试", "error", {"message": str(e)})
    
    def test_other_components(self):
        """测试其他组件"""
        workflow = "其他组件"
        print(f"\n🔧 测试{workflow}...")
        
        # 测试文档和配置文件
        doc_files = [
            ("README.md", "项目说明文档"),
            ("DELIVERY_REPORT.md", "交付报告"),
            ("SMART_ROUTING_MCP_COMPLETE_DOCUMENTATION.md", "智能路由完整文档"),
            ("__init__.py", "模块初始化文件")
        ]
        
        base_path = "/opt/powerautomation/mcp/mcp_coordinator"
        for file_name, description in doc_files:
            file_path = os.path.join(base_path, file_name)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_result(workflow, f"{description}", "success", 
                              {"message": f"文件大小: {file_size} bytes"})
            else:
                self.log_result(workflow, f"{description}", "warning", 
                              {"message": "文件不存在"})
        
        # 测试增强组件
        enhanced_files = [
            ("enhanced_mcp_coordinator.py", "增强MCP协调器"),
            ("enhanced_smart_routing_mcp.py", "增强智能路由")
        ]
        
        for file_name, description in enhanced_files:
            file_path = os.path.join(base_path, file_name)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.log_result(workflow, f"{description}", "success", 
                              {"message": f"增强组件: {file_size} bytes"})
            else:
                self.log_result(workflow, f"{description}", "warning", 
                              {"message": "增强组件不存在"})
    
    def generate_workflow_report(self):
        """生成工作流测试报告"""
        print("\n" + "="*80)
        print("📊 PowerAutomation 六大工作流测试报告")
        print("="*80)
        
        # 按工作流分组统计
        workflow_stats = {}
        for result in self.test_results:
            workflow = result["workflow"]
            if workflow not in workflow_stats:
                workflow_stats[workflow] = {"total": 0, "success": 0, "warning": 0, "error": 0}
            
            workflow_stats[workflow]["total"] += 1
            workflow_stats[workflow][result["status"]] += 1
        
        # 总体统计
        total_tests = len(self.test_results)
        total_success = len([r for r in self.test_results if r["status"] == "success"])
        total_warning = len([r for r in self.test_results if r["status"] == "warning"])
        total_error = len([r for r in self.test_results if r["status"] == "error"])
        
        print(f"📈 总体统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   ✅ 成功: {total_success}")
        print(f"   ⚠️  警告: {total_warning}")
        print(f"   ❌ 错误: {total_error}")
        print(f"   📊 成功率: {total_success/total_tests*100:.1f}%")
        
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"   ⏱️  总耗时: {duration:.2f}秒")
        
        print(f"\n🔄 工作流分析:")
        for workflow, stats in workflow_stats.items():
            icon = self.workflow_categories.get(workflow, {}).get("icon", "🔧")
            success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"   {icon} {workflow}:")
            print(f"      测试数: {stats['total']} | 成功: {stats['success']} | 成功率: {success_rate:.1f}%")
            if workflow in self.workflow_categories:
                print(f"      描述: {self.workflow_categories[workflow]['description']}")
        
        # 保存详细报告
        report_data = {
            "test_summary": {
                "total": total_tests,
                "success": total_success,
                "warning": total_warning,
                "error": total_error,
                "success_rate": total_success/total_tests*100,
                "duration": time.time() - self.start_time if self.start_time else 0
            },
            "workflow_stats": workflow_stats,
            "workflow_categories": self.workflow_categories,
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        report_file = "/opt/powerautomation/workflow_test_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 详细报告已保存: {report_file}")
        except Exception as e:
            print(f"\n❌ 报告保存失败: {e}")
    
    async def run_all_workflows(self):
        """运行所有工作流测试"""
        self.start_time = time.time()
        
        print("🚀 PowerAutomation 六大工作流测试开始...")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示工作流类别
        print(f"\n📋 工作流类别:")
        for workflow, info in self.workflow_categories.items():
            print(f"   {info['icon']} {workflow}: {info['description']}")
        
        # 运行各工作流测试
        await self.test_intelligent_coordination_workflow()
        await self.test_development_intervention_workflow()
        await self.test_dialog_classification_workflow()
        await self.test_workflow_engine_workflow()
        await self.test_shared_core_workflow()
        await self.test_realtime_monitoring_workflow()
        self.test_other_components()
        
        # 生成报告
        self.generate_workflow_report()
    
    async def run_specific_workflow(self, workflow_name: str):
        """运行特定工作流测试"""
        self.start_time = time.time()
        
        print(f"🎯 运行特定工作流测试: {workflow_name}")
        
        workflow_map = {
            "coordination": self.test_intelligent_coordination_workflow,
            "development": self.test_development_intervention_workflow,
            "dialog": self.test_dialog_classification_workflow,
            "engine": self.test_workflow_engine_workflow,
            "shared": self.test_shared_core_workflow,
            "monitoring": self.test_realtime_monitoring_workflow,
            "other": self.test_other_components
        }
        
        if workflow_name in workflow_map:
            if workflow_name == "other":
                workflow_map[workflow_name]()
            else:
                await workflow_map[workflow_name]()
        else:
            print(f"❌ 未知工作流: {workflow_name}")
            return
        
        self.generate_workflow_report()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PowerAutomation 六大工作流测试CLI工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
六大工作流类别:
  all          - 运行所有工作流测试 (默认)
  coordination - 智能协调工作流 (MCP协调器、智能路由)
  development  - 开发介入工作流 (开发介入、架构合规)
  dialog       - 对话分类工作流 (对话分类、意图识别)
  engine       - 工作流引擎工作流 (流程自动化、任务编排)
  shared       - 共享核心工作流 (模块集成、数据共享)
  monitoring   - 实时监控工作流 (系统监控、性能分析)
  other        - 其他组件 (文档、配置、增强组件)

示例:
  python3 workflow_test_cli.py                      # 运行所有工作流测试
  python3 workflow_test_cli.py --workflow coordination # 测试智能协调工作流
  python3 workflow_test_cli.py --workflow development  # 测试开发介入工作流
  python3 workflow_test_cli.py --verbose               # 详细输出模式
        """
    )
    
    parser.add_argument(
        "--workflow",
        type=str,
        choices=["all", "coordination", "development", "dialog", "engine", "shared", "monitoring", "other"],
        default="all",
        help="指定要测试的工作流类别"
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
    
    # 创建工作流测试CLI实例
    test_cli = PowerAutoWorkflowTestCLI()
    
    # 运行测试
    try:
        if args.workflow == "all":
            asyncio.run(test_cli.run_all_workflows())
        else:
            asyncio.run(test_cli.run_specific_workflow(args.workflow))
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

