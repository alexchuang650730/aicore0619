#!/usr/bin/env python3
"""
Workflow UI Integration Demo
演示Workflow Coding MCP如何动态修改SmartUI界面
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

class WorkflowUIDemo:
    """工作流UI集成演示"""
    
    def __init__(self):
        self.coordinator_url = "http://localhost:8089"
        self.smartui_url = "http://localhost:5002"
        self.workflow_scenarios = self._load_scenarios()
    
    def _load_scenarios(self) -> Dict[str, Any]:
        """加载演示场景"""
        return {
            "coding_task": {
                "name": "代码生成任务",
                "workflow_context": {
                    "current_stage": "code_generation",
                    "task_name": "React组件开发",
                    "workflow_steps": ["需求分析", "组件设计", "代码实现", "单元测试", "集成测试"],
                    "current_step": 3,
                    "programming_language": "javascript",
                    "framework": "react",
                    "task_list": [
                        "创建组件结构",
                        "实现组件逻辑",
                        "添加样式",
                        "编写测试"
                    ],
                    "completed_tasks": 1
                },
                "expected_ui": {
                    "layout": "coding_workspace",
                    "components": ["code_editor", "progress_tracker", "task_checklist"],
                    "theme": "dark"
                }
            },
            "design_task": {
                "name": "UI设计任务", 
                "workflow_context": {
                    "current_stage": "ui_design",
                    "task_name": "移动端界面设计",
                    "workflow_steps": ["用户研究", "原型设计", "视觉设计", "交互设计", "设计验证"],
                    "current_step": 3,
                    "design_tool": "figma",
                    "target_platform": "mobile",
                    "task_list": [
                        "创建设计系统",
                        "设计主要页面",
                        "制作交互原型",
                        "用户测试"
                    ],
                    "completed_tasks": 2
                },
                "expected_ui": {
                    "layout": "design_workspace",
                    "components": ["design_canvas", "tool_palette", "layer_panel"],
                    "theme": "light"
                }
            },
            "testing_task": {
                "name": "测试验证任务",
                "workflow_context": {
                    "current_stage": "testing",
                    "task_name": "自动化测试执行",
                    "workflow_steps": ["测试计划", "用例编写", "自动化测试", "性能测试", "报告生成"],
                    "current_step": 3,
                    "test_framework": "jest",
                    "coverage_target": 90,
                    "task_list": [
                        "单元测试",
                        "集成测试",
                        "端到端测试",
                        "性能测试"
                    ],
                    "completed_tasks": 2
                },
                "expected_ui": {
                    "layout": "testing_workspace",
                    "components": ["test_runner", "coverage_report", "error_console"],
                    "theme": "testing"
                }
            }
        }
    
    async def run_demo(self, scenario_name: str = "coding_task"):
        """运行演示"""
        
        print(f"🚀 开始演示: {scenario_name}")
        print("=" * 60)
        
        scenario = self.workflow_scenarios.get(scenario_name)
        if not scenario:
            print(f"❌ 未找到场景: {scenario_name}")
            return
        
        # 1. 检查服务状态
        print("1️⃣ 检查服务状态...")
        await self._check_services()
        
        # 2. 生成UI修改请求
        print("2️⃣ 生成UI修改请求...")
        ui_request = await self._generate_ui_request(scenario)
        
        # 3. 发送请求到SmartUI
        print("3️⃣ 发送UI修改请求...")
        result = await self._send_ui_request(ui_request)
        
        # 4. 验证结果
        print("4️⃣ 验证UI生成结果...")
        await self._verify_result(result, scenario)
        
        # 5. 模拟用户交互
        print("5️⃣ 模拟用户交互...")
        await self._simulate_user_interactions(result)
        
        print("✅ 演示完成!")
        print("=" * 60)
    
    async def _check_services(self):
        """检查服务状态"""
        
        services = [
            ("MCP Coordinator", f"{self.coordinator_url}/health"),
            ("SmartUI Enhanced", f"{self.smartui_url}/health")
        ]
        
        for service_name, health_url in services:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {service_name}: 运行正常")
                else:
                    print(f"   ❌ {service_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {service_name}: 连接失败 - {e}")
    
    async def _generate_ui_request(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """生成UI修改请求"""
        
        workflow_context = scenario["workflow_context"]
        expected_ui = scenario["expected_ui"]
        
        request_id = f"demo_ui_mod_{int(time.time())}"
        
        # 构建组件配置
        component_updates = []
        
        # 进度跟踪组件
        if "progress_tracker" in expected_ui["components"]:
            component_updates.append({
                "component_id": "progress_tracker",
                "component_type": "progress_bar",
                "update_type": "create_or_update",
                "props": {
                    "title": f"{workflow_context['task_name']}进度",
                    "current_step": workflow_context["current_step"],
                    "total_steps": len(workflow_context["workflow_steps"]),
                    "steps": workflow_context["workflow_steps"]
                },
                "position": {"container": "sidebar", "order": 1}
            })
        
        # 代码编辑器组件
        if "code_editor" in expected_ui["components"]:
            component_updates.append({
                "component_id": "code_editor",
                "component_type": "code_editor",
                "update_type": "create_or_update",
                "props": {
                    "language": workflow_context.get("programming_language", "javascript"),
                    "theme": "vs-dark",
                    "features": ["autocomplete", "syntax_highlight", "error_detection"],
                    "initial_content": f"// {workflow_context['task_name']} - 自动生成的代码框架\n\n"
                },
                "position": {"container": "main_area", "order": 1}
            })
        
        # 任务清单组件
        if "task_checklist" in expected_ui["components"]:
            component_updates.append({
                "component_id": "task_checklist",
                "component_type": "checklist",
                "update_type": "create_or_update",
                "props": {
                    "title": "任务清单",
                    "items": [
                        {
                            "id": f"task_{i}",
                            "text": task,
                            "completed": i < workflow_context.get("completed_tasks", 0)
                        }
                        for i, task in enumerate(workflow_context["task_list"])
                    ],
                    "allow_reorder": True,
                    "show_progress": True
                },
                "position": {"container": "sidebar", "order": 2}
            })
        
        # 构建完整请求
        ui_request = {
            "protocol_version": "1.0",
            "request_id": request_id,
            "source_mcp": "workflow_coding_mcp_demo",
            "target_mcp": "smartui_enhanced",
            "action": "modify_ui",
            "timestamp": time.time(),
            "modification_request": {
                "modification_type": "dynamic_update",
                "trigger_context": {
                    "workflow_stage": workflow_context["current_stage"],
                    "user_action": "start_workflow",
                    "environment": {
                        "task_type": workflow_context["current_stage"],
                        "complexity": "medium"
                    }
                },
                "ui_requirements": {
                    "layout_changes": {
                        "primary_layout": expected_ui["layout"],
                        "sidebar_config": {
                            "show_file_tree": True,
                            "show_task_progress": True,
                            "show_code_snippets": "code_editor" in expected_ui["components"]
                        },
                        "main_area_config": {
                            "editor_layout": "split_vertical",
                            "preview_panel": True,
                            "console_panel": True
                        }
                    },
                    "component_updates": component_updates,
                    "theme_adjustments": {
                        "color_scheme": expected_ui["theme"],
                        "accent_color": "#00d4aa",
                        "focus_mode": True
                    },
                    "interaction_enhancements": {
                        "keyboard_shortcuts": [
                            {"key": "Ctrl+S", "action": "save_progress"},
                            {"key": "Ctrl+R", "action": "run_code"},
                            {"key": "F5", "action": "refresh_preview"}
                        ],
                        "auto_save": {"enabled": True, "interval": 30},
                        "real_time_collaboration": {"enabled": False}
                    }
                },
                "adaptation_rules": {
                    "responsive_behavior": {
                        "mobile": "stack_vertically",
                        "tablet": "sidebar_collapsible",
                        "desktop": "full_layout"
                    },
                    "performance_optimization": {
                        "lazy_load_components": True,
                        "cache_code_snippets": True,
                        "debounce_updates": 300
                    },
                    "accessibility": {
                        "high_contrast_mode": False,
                        "screen_reader_support": True,
                        "keyboard_navigation": True
                    }
                },
                "callback_config": {
                    "progress_updates": {
                        "endpoint": "workflow_coding_mcp_demo/ui_progress",
                        "frequency": "on_change"
                    },
                    "user_interactions": {
                        "endpoint": "workflow_coding_mcp_demo/user_action",
                        "events": ["component_click", "code_change", "task_complete"]
                    }
                }
            },
            "execution_options": {
                "priority": "high",
                "timeout": 30,
                "retry_count": 3,
                "fallback_strategy": "maintain_current_ui"
            }
        }
        
        print(f"   📝 生成请求ID: {request_id}")
        print(f"   🎨 目标布局: {expected_ui['layout']}")
        print(f"   🧩 组件数量: {len(component_updates)}")
        
        return ui_request
    
    async def _send_ui_request(self, ui_request: Dict[str, Any]) -> Dict[str, Any]:
        """发送UI请求"""
        
        try:
            # 通过MCP Coordinator转发请求
            response = requests.post(
                f"{self.coordinator_url}/coordinator/request/smartui_enhanced",
                json={
                    "action": "modify_ui",
                    "params": ui_request
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 请求发送成功")
                print(f"   ⏱️  响应时间: {response.elapsed.total_seconds():.2f}s")
                return result
            else:
                print(f"   ❌ 请求失败: HTTP {response.status_code}")
                print(f"   📄 响应内容: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def _verify_result(self, result: Dict[str, Any], scenario: Dict[str, Any]):
        """验证结果"""
        
        if result.get("success"):
            print(f"   ✅ UI生成成功")
            
            # 检查生成结果
            if "modification_result" in result:
                mod_result = result["modification_result"]
                print(f"   🎨 界面ID: {mod_result.get('interface_id', 'N/A')}")
                print(f"   ⏱️  生成时间: {mod_result.get('generation_time', 0):.2f}s")
                print(f"   🧩 创建组件: {mod_result.get('components_created', 0)}个")
                print(f"   🎭 应用主题: {mod_result.get('theme_applied', 'N/A')}")
            
            # 检查UI状态
            if "ui_state" in result:
                ui_state = result["ui_state"]
                print(f"   📐 当前布局: {ui_state.get('current_layout', 'N/A')}")
                print(f"   🔧 活跃组件: {', '.join(ui_state.get('active_components', []))}")
        else:
            print(f"   ❌ UI生成失败: {result.get('error', '未知错误')}")
    
    async def _simulate_user_interactions(self, result: Dict[str, Any]):
        """模拟用户交互"""
        
        if not result.get("success"):
            print("   ⏭️  跳过用户交互模拟（UI生成失败）")
            return
        
        print("   🖱️  模拟用户交互...")
        
        # 模拟进度更新
        await self._simulate_progress_update()
        
        # 模拟任务完成
        await self._simulate_task_completion()
        
        # 模拟代码编辑
        await self._simulate_code_editing()
    
    async def _simulate_progress_update(self):
        """模拟进度更新"""
        print("      📈 模拟进度更新...")
        await asyncio.sleep(1)
        print("      ✅ 进度从步骤3更新到步骤4")
    
    async def _simulate_task_completion(self):
        """模拟任务完成"""
        print("      ✅ 模拟任务完成...")
        await asyncio.sleep(1)
        print("      🎯 任务'实现组件逻辑'标记为完成")
    
    async def _simulate_code_editing(self):
        """模拟代码编辑"""
        print("      ⌨️  模拟代码编辑...")
        await asyncio.sleep(1)
        print("      💾 自动保存代码变更")
    
    async def run_all_scenarios(self):
        """运行所有演示场景"""
        
        print("🎬 开始运行所有演示场景")
        print("=" * 80)
        
        for scenario_name, scenario in self.workflow_scenarios.items():
            print(f"\n🎯 场景: {scenario['name']}")
            await self.run_demo(scenario_name)
            
            if scenario_name != list(self.workflow_scenarios.keys())[-1]:
                print("\n⏸️  等待3秒后继续下一个场景...")
                await asyncio.sleep(3)
        
        print("\n🎉 所有演示场景完成!")

async def main():
    """主函数"""
    
    demo = WorkflowUIDemo()
    
    print("🎭 Workflow UI Integration Demo")
    print("演示Workflow Coding MCP如何动态修改SmartUI界面")
    print("=" * 80)
    
    # 选择演示模式
    print("\n请选择演示模式:")
    print("1. 单个场景演示")
    print("2. 所有场景演示")
    
    try:
        choice = input("\n请输入选择 (1/2): ").strip()
        
        if choice == "1":
            print("\n可用场景:")
            for i, (key, scenario) in enumerate(demo.workflow_scenarios.items(), 1):
                print(f"{i}. {key} - {scenario['name']}")
            
            scenario_choice = input("\n请选择场景编号: ").strip()
            scenario_keys = list(demo.workflow_scenarios.keys())
            
            if scenario_choice.isdigit() and 1 <= int(scenario_choice) <= len(scenario_keys):
                scenario_name = scenario_keys[int(scenario_choice) - 1]
                await demo.run_demo(scenario_name)
            else:
                print("❌ 无效选择，使用默认场景")
                await demo.run_demo("coding_task")
        
        elif choice == "2":
            await demo.run_all_scenarios()
        
        else:
            print("❌ 无效选择，使用默认模式")
            await demo.run_demo("coding_task")
    
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())

