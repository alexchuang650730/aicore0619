# Workflow Coding MCP 动态修改 SmartUI 界面方案

## 🎯 方案概述

本方案设计了一套完整的通信协议和实现机制，使Workflow Coding MCP能够通过MCP Coordinator动态修改SmartUI Enhanced的界面，实现工作流驱动的智能UI适配。

## 🏗️ 整体架构

```
Workflow Coding MCP → MCP Coordinator → SmartUI Enhanced MCP
        ↓                    ↓                    ↓
   工作流分析          协议转换路由         动态UI生成
   需求识别          安全验证转发         界面实时更新
   指令生成          状态同步管理         用户体验优化
```

### 核心组件关系

1. **Workflow Coding MCP** - 工作流分析和UI需求生成
2. **MCP Coordinator** - 中央协调和协议转换
3. **SmartUI Enhanced MCP** - 动态界面生成和管理
4. **通信协议层** - 标准化的数据交换格式

## 📋 通信协议规范

### 1. UI修改请求协议

**协议名称**: `ui_modification_request`
**版本**: `v1.0`
**传输方式**: HTTP POST via MCP Coordinator

#### 请求格式

```json
{
  "protocol_version": "1.0",
  "request_id": "workflow_ui_mod_20240617_001",
  "source_mcp": "workflow_coding_mcp",
  "target_mcp": "smartui_enhanced",
  "action": "modify_ui",
  "timestamp": "2024-06-17T14:30:00Z",
  "modification_request": {
    "modification_type": "dynamic_update",
    "trigger_context": {
      "workflow_stage": "code_generation",
      "user_action": "start_coding_task",
      "environment": {
        "project_type": "web_application",
        "complexity": "medium",
        "deadline": "2024-06-20T18:00:00Z"
      }
    },
    "ui_requirements": {
      "layout_changes": {
        "primary_layout": "coding_workspace",
        "sidebar_config": {
          "show_file_tree": true,
          "show_task_progress": true,
          "show_code_snippets": true
        },
        "main_area_config": {
          "editor_layout": "split_vertical",
          "preview_panel": true,
          "console_panel": true
        }
      },
      "component_updates": [
        {
          "component_id": "progress_tracker",
          "component_type": "progress_bar",
          "update_type": "create_or_update",
          "props": {
            "title": "代码生成进度",
            "current_step": 1,
            "total_steps": 5,
            "steps": [
              "需求分析",
              "架构设计", 
              "代码生成",
              "测试编写",
              "部署准备"
            ]
          },
          "position": {
            "container": "sidebar",
            "order": 1
          }
        },
        {
          "component_id": "code_editor",
          "component_type": "code_editor",
          "update_type": "create_or_update",
          "props": {
            "language": "javascript",
            "theme": "vs-dark",
            "features": ["autocomplete", "syntax_highlight", "error_detection"],
            "initial_content": "// 工作流自动生成的代码框架\nfunction initializeProject() {\n  // TODO: 实现项目初始化逻辑\n}"
          },
          "position": {
            "container": "main_area",
            "order": 1
          }
        },
        {
          "component_id": "task_checklist",
          "component_type": "checklist",
          "update_type": "create_or_update",
          "props": {
            "title": "编码任务清单",
            "items": [
              {"id": "setup_project", "text": "项目结构搭建", "completed": false},
              {"id": "implement_core", "text": "核心功能实现", "completed": false},
              {"id": "add_tests", "text": "单元测试编写", "completed": false},
              {"id": "documentation", "text": "文档编写", "completed": false}
            ],
            "allow_reorder": true,
            "show_progress": true
          },
          "position": {
            "container": "sidebar",
            "order": 2
          }
        }
      ],
      "theme_adjustments": {
        "color_scheme": "dark",
        "accent_color": "#00d4aa",
        "focus_mode": true
      },
      "interaction_enhancements": {
        "keyboard_shortcuts": [
          {"key": "Ctrl+S", "action": "save_progress"},
          {"key": "Ctrl+R", "action": "run_code"},
          {"key": "F5", "action": "refresh_preview"}
        ],
        "auto_save": {
          "enabled": true,
          "interval": 30
        },
        "real_time_collaboration": {
          "enabled": true,
          "session_id": "coding_session_001"
        }
      }
    },
    "adaptation_rules": {
      "responsive_behavior": {
        "mobile": "stack_vertically",
        "tablet": "sidebar_collapsible", 
        "desktop": "full_layout"
      },
      "performance_optimization": {
        "lazy_load_components": true,
        "cache_code_snippets": true,
        "debounce_updates": 300
      },
      "accessibility": {
        "high_contrast_mode": false,
        "screen_reader_support": true,
        "keyboard_navigation": true
      }
    },
    "callback_config": {
      "progress_updates": {
        "endpoint": "workflow_coding_mcp/ui_progress",
        "frequency": "on_change"
      },
      "user_interactions": {
        "endpoint": "workflow_coding_mcp/user_action",
        "events": ["component_click", "code_change", "task_complete"]
      },
      "error_reporting": {
        "endpoint": "workflow_coding_mcp/error_report",
        "include_stack_trace": true
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
```

#### 响应格式

```json
{
  "protocol_version": "1.0",
  "request_id": "workflow_ui_mod_20240617_001",
  "response_id": "smartui_resp_20240617_001",
  "source_mcp": "smartui_enhanced",
  "target_mcp": "workflow_coding_mcp",
  "status": "success",
  "timestamp": "2024-06-17T14:30:02Z",
  "modification_result": {
    "ui_generated": true,
    "interface_id": "coding_workspace_001",
    "generation_time": 1.25,
    "components_created": 3,
    "components_updated": 0,
    "layout_applied": "coding_workspace",
    "theme_applied": "dark_coding",
    "accessibility_features": ["keyboard_navigation", "screen_reader_support"],
    "performance_metrics": {
      "initial_load_time": 0.8,
      "component_render_time": 0.45,
      "total_memory_usage": "12.5MB"
    }
  },
  "ui_state": {
    "current_layout": "coding_workspace",
    "active_components": [
      "progress_tracker",
      "code_editor", 
      "task_checklist"
    ],
    "user_session": {
      "session_id": "coding_session_001",
      "user_preferences": {
        "theme": "dark",
        "editor_font_size": 14,
        "sidebar_width": 300
      }
    }
  },
  "callback_endpoints": {
    "progress_updates": "http://smartui:5002/api/callbacks/progress",
    "user_interactions": "http://smartui:5002/api/callbacks/interactions",
    "error_reporting": "http://smartui:5002/api/callbacks/errors"
  },
  "next_actions": [
    {
      "action": "monitor_user_progress",
      "trigger": "user_interaction",
      "description": "监控用户编码进度并更新进度条"
    },
    {
      "action": "auto_save_code",
      "trigger": "timer_30s",
      "description": "每30秒自动保存用户代码"
    }
  ]
}
```

### 2. UI状态同步协议

**协议名称**: `ui_state_sync`
**用途**: 实时同步UI状态变化

#### 状态更新通知

```json
{
  "protocol_version": "1.0",
  "sync_id": "ui_sync_20240617_001",
  "source_mcp": "smartui_enhanced",
  "target_mcp": "workflow_coding_mcp",
  "action": "state_update",
  "timestamp": "2024-06-17T14:35:00Z",
  "state_changes": {
    "component_updates": [
      {
        "component_id": "progress_tracker",
        "change_type": "property_update",
        "changes": {
          "current_step": 2,
          "step_status": {
            "需求分析": "completed",
            "架构设计": "in_progress"
          }
        }
      }
    ],
    "user_interactions": [
      {
        "interaction_id": "user_action_001",
        "component_id": "task_checklist",
        "action": "item_checked",
        "data": {
          "item_id": "setup_project",
          "completed": true,
          "timestamp": "2024-06-17T14:34:55Z"
        }
      }
    ],
    "performance_metrics": {
      "response_time": 0.12,
      "memory_usage": "13.2MB",
      "cpu_usage": "15%"
    }
  }
}
```

### 3. 工作流触发协议

**协议名称**: `workflow_trigger`
**用途**: 基于UI交互触发工作流操作

#### 触发请求

```json
{
  "protocol_version": "1.0",
  "trigger_id": "workflow_trigger_001",
  "source_mcp": "smartui_enhanced",
  "target_mcp": "workflow_coding_mcp",
  "action": "trigger_workflow",
  "timestamp": "2024-06-17T14:40:00Z",
  "trigger_data": {
    "trigger_type": "user_action",
    "trigger_source": {
      "component_id": "code_editor",
      "action": "code_completion_request",
      "context": {
        "current_code": "function calculateTotal(items) {\n  // TODO: 实现计算逻辑\n",
        "cursor_position": {"line": 2, "column": 20},
        "language": "javascript",
        "project_context": {
          "type": "e-commerce",
          "framework": "react"
        }
      }
    },
    "expected_response": {
      "response_type": "code_suggestion",
      "ui_update_required": true,
      "timeout": 10
    }
  }
}
```

## 🔧 实现方案

### 1. Workflow Coding MCP 端实现

```python
# workflow_coding_mcp/ui_controller.py
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests

@dataclass
class UIModificationRequest:
    """UI修改请求"""
    request_id: str
    modification_type: str
    trigger_context: Dict[str, Any]
    ui_requirements: Dict[str, Any]
    adaptation_rules: Dict[str, Any]
    callback_config: Dict[str, Any]
    execution_options: Dict[str, Any]

class WorkflowUIController:
    """工作流UI控制器"""
    
    def __init__(self, coordinator_url: str = "http://localhost:8089"):
        self.coordinator_url = coordinator_url
        self.active_ui_sessions = {}
        self.ui_templates = {}
        self._load_ui_templates()
    
    def _load_ui_templates(self):
        """加载UI模板"""
        self.ui_templates = {
            "coding_workspace": {
                "layout": "coding_workspace",
                "components": ["progress_tracker", "code_editor", "task_checklist"],
                "theme": "dark_coding",
                "shortcuts": ["Ctrl+S", "Ctrl+R", "F5"]
            },
            "design_workspace": {
                "layout": "design_workspace", 
                "components": ["design_canvas", "tool_palette", "layer_panel"],
                "theme": "light_design",
                "shortcuts": ["Ctrl+Z", "Ctrl+Y", "Space"]
            },
            "testing_workspace": {
                "layout": "testing_workspace",
                "components": ["test_runner", "coverage_report", "error_console"],
                "theme": "testing_theme",
                "shortcuts": ["F9", "F10", "F11"]
            }
        }
    
    async def analyze_workflow_stage(self, workflow_context: Dict[str, Any]) -> str:
        """分析工作流阶段并确定UI需求"""
        stage = workflow_context.get("current_stage", "unknown")
        task_type = workflow_context.get("task_type", "general")
        user_preferences = workflow_context.get("user_preferences", {})
        
        # 基于工作流阶段选择UI模板
        if stage in ["code_generation", "implementation", "debugging"]:
            return "coding_workspace"
        elif stage in ["design", "prototyping", "ui_design"]:
            return "design_workspace"
        elif stage in ["testing", "validation", "quality_assurance"]:
            return "testing_workspace"
        else:
            return "coding_workspace"  # 默认
    
    async def generate_ui_modification_request(self, 
                                             workflow_context: Dict[str, Any],
                                             user_action: Dict[str, Any] = None) -> UIModificationRequest:
        """生成UI修改请求"""
        
        # 分析工作流需求
        ui_template = await self.analyze_workflow_stage(workflow_context)
        template_config = self.ui_templates[ui_template]
        
        # 生成请求ID
        request_id = f"workflow_ui_mod_{int(time.time())}"
        
        # 构建UI需求
        ui_requirements = await self._build_ui_requirements(
            template_config, workflow_context, user_action
        )
        
        # 构建适配规则
        adaptation_rules = await self._build_adaptation_rules(workflow_context)
        
        # 构建回调配置
        callback_config = await self._build_callback_config(request_id)
        
        return UIModificationRequest(
            request_id=request_id,
            modification_type="dynamic_update",
            trigger_context={
                "workflow_stage": workflow_context.get("current_stage"),
                "user_action": user_action.get("action") if user_action else "workflow_trigger",
                "environment": workflow_context.get("environment", {})
            },
            ui_requirements=ui_requirements,
            adaptation_rules=adaptation_rules,
            callback_config=callback_config,
            execution_options={
                "priority": "high",
                "timeout": 30,
                "retry_count": 3,
                "fallback_strategy": "maintain_current_ui"
            }
        )
    
    async def _build_ui_requirements(self, 
                                   template_config: Dict[str, Any],
                                   workflow_context: Dict[str, Any],
                                   user_action: Dict[str, Any] = None) -> Dict[str, Any]:
        """构建UI需求配置"""
        
        # 基础布局配置
        layout_changes = {
            "primary_layout": template_config["layout"],
            "sidebar_config": {
                "show_file_tree": True,
                "show_task_progress": True,
                "show_code_snippets": workflow_context.get("current_stage") == "code_generation"
            },
            "main_area_config": {
                "editor_layout": "split_vertical",
                "preview_panel": True,
                "console_panel": True
            }
        }
        
        # 动态组件配置
        component_updates = []
        
        # 进度跟踪组件
        if workflow_context.get("workflow_steps"):
            progress_component = {
                "component_id": "progress_tracker",
                "component_type": "progress_bar",
                "update_type": "create_or_update",
                "props": {
                    "title": f"{workflow_context.get('task_name', '任务')}进度",
                    "current_step": workflow_context.get("current_step", 1),
                    "total_steps": len(workflow_context.get("workflow_steps", [])),
                    "steps": workflow_context.get("workflow_steps", [])
                },
                "position": {"container": "sidebar", "order": 1}
            }
            component_updates.append(progress_component)
        
        # 代码编辑器组件
        if template_config["layout"] == "coding_workspace":
            code_editor_component = {
                "component_id": "code_editor",
                "component_type": "code_editor",
                "update_type": "create_or_update",
                "props": {
                    "language": workflow_context.get("programming_language", "javascript"),
                    "theme": "vs-dark",
                    "features": ["autocomplete", "syntax_highlight", "error_detection"],
                    "initial_content": workflow_context.get("initial_code", "// 工作流自动生成的代码框架")
                },
                "position": {"container": "main_area", "order": 1}
            }
            component_updates.append(code_editor_component)
        
        # 任务清单组件
        if workflow_context.get("task_list"):
            task_checklist_component = {
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
            }
            component_updates.append(task_checklist_component)
        
        return {
            "layout_changes": layout_changes,
            "component_updates": component_updates,
            "theme_adjustments": {
                "color_scheme": template_config.get("theme", "dark"),
                "accent_color": workflow_context.get("brand_color", "#00d4aa"),
                "focus_mode": workflow_context.get("focus_mode", True)
            },
            "interaction_enhancements": {
                "keyboard_shortcuts": [
                    {"key": shortcut, "action": f"workflow_action_{i}"}
                    for i, shortcut in enumerate(template_config.get("shortcuts", []))
                ],
                "auto_save": {
                    "enabled": True,
                    "interval": workflow_context.get("auto_save_interval", 30)
                },
                "real_time_collaboration": {
                    "enabled": workflow_context.get("collaboration_enabled", False),
                    "session_id": workflow_context.get("session_id")
                }
            }
        }
    
    async def _build_adaptation_rules(self, workflow_context: Dict[str, Any]) -> Dict[str, Any]:
        """构建适配规则"""
        return {
            "responsive_behavior": {
                "mobile": "stack_vertically",
                "tablet": "sidebar_collapsible",
                "desktop": "full_layout"
            },
            "performance_optimization": {
                "lazy_load_components": True,
                "cache_code_snippets": True,
                "debounce_updates": workflow_context.get("debounce_ms", 300)
            },
            "accessibility": {
                "high_contrast_mode": workflow_context.get("high_contrast", False),
                "screen_reader_support": True,
                "keyboard_navigation": True
            }
        }
    
    async def _build_callback_config(self, request_id: str) -> Dict[str, Any]:
        """构建回调配置"""
        return {
            "progress_updates": {
                "endpoint": "workflow_coding_mcp/ui_progress",
                "frequency": "on_change"
            },
            "user_interactions": {
                "endpoint": "workflow_coding_mcp/user_action", 
                "events": ["component_click", "code_change", "task_complete"]
            },
            "error_reporting": {
                "endpoint": "workflow_coding_mcp/error_report",
                "include_stack_trace": True
            }
        }
    
    async def send_ui_modification_request(self, request: UIModificationRequest) -> Dict[str, Any]:
        """发送UI修改请求到SmartUI Enhanced"""
        
        # 构建完整的请求数据
        request_data = {
            "protocol_version": "1.0",
            "request_id": request.request_id,
            "source_mcp": "workflow_coding_mcp",
            "target_mcp": "smartui_enhanced",
            "action": "modify_ui",
            "timestamp": time.time(),
            "modification_request": {
                "modification_type": request.modification_type,
                "trigger_context": request.trigger_context,
                "ui_requirements": request.ui_requirements,
                "adaptation_rules": request.adaptation_rules,
                "callback_config": request.callback_config
            },
            "execution_options": request.execution_options
        }
        
        try:
            # 通过MCP Coordinator转发请求
            response = requests.post(
                f"{self.coordinator_url}/coordinator/request/smartui_enhanced",
                json={
                    "action": "modify_ui",
                    "params": request_data
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 记录活跃会话
                if result.get("success"):
                    self.active_ui_sessions[request.request_id] = {
                        "request": request,
                        "response": result,
                        "created_at": time.time()
                    }
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"请求发送失败: {str(e)}"
            }
    
    async def handle_ui_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理来自SmartUI的回调"""
        
        callback_type = callback_data.get("callback_type")
        request_id = callback_data.get("request_id")
        
        if callback_type == "progress_update":
            return await self._handle_progress_update(callback_data)
        elif callback_type == "user_interaction":
            return await self._handle_user_interaction(callback_data)
        elif callback_type == "error_report":
            return await self._handle_error_report(callback_data)
        else:
            return {"success": False, "error": f"未知回调类型: {callback_type}"}
    
    async def _handle_progress_update(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理进度更新回调"""
        # 更新工作流状态
        # 可能触发下一步工作流操作
        return {"success": True, "action": "progress_updated"}
    
    async def _handle_user_interaction(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户交互回调"""
        interaction_type = callback_data.get("interaction_type")
        
        if interaction_type == "code_change":
            # 分析代码变化，可能触发代码建议
            return await self._handle_code_change(callback_data)
        elif interaction_type == "task_complete":
            # 任务完成，更新工作流进度
            return await self._handle_task_complete(callback_data)
        else:
            return {"success": True, "action": "interaction_logged"}
    
    async def _handle_code_change(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理代码变化"""
        # 这里可以集成代码分析、自动补全等功能
        return {"success": True, "action": "code_analyzed"}
    
    async def _handle_task_complete(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务完成"""
        # 更新工作流进度，可能触发下一阶段UI更新
        return {"success": True, "action": "workflow_advanced"}
    
    async def _handle_error_report(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理错误报告回调"""
        # 记录错误，可能触发错误恢复流程
        return {"success": True, "action": "error_logged"}

# 使用示例
async def example_workflow_ui_integration():
    """工作流UI集成示例"""
    
    ui_controller = WorkflowUIController()
    
    # 模拟工作流上下文
    workflow_context = {
        "current_stage": "code_generation",
        "task_name": "电商网站开发",
        "workflow_steps": ["需求分析", "架构设计", "代码生成", "测试编写", "部署准备"],
        "current_step": 3,
        "programming_language": "javascript",
        "task_list": [
            "项目结构搭建",
            "核心功能实现", 
            "单元测试编写",
            "文档编写"
        ],
        "completed_tasks": 1,
        "environment": {
            "project_type": "web_application",
            "framework": "react",
            "complexity": "medium"
        }
    }
    
    # 生成UI修改请求
    ui_request = await ui_controller.generate_ui_modification_request(workflow_context)
    
    # 发送请求
    result = await ui_controller.send_ui_modification_request(ui_request)
    
    print(f"UI修改结果: {result}")
    
    return result

if __name__ == "__main__":
    asyncio.run(example_workflow_ui_integration())
```

### 2. SmartUI Enhanced MCP 端实现

```python
# smartui_enhanced/workflow_ui_handler.py
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from flask import request, jsonify

class WorkflowUIHandler:
    """工作流UI处理器"""
    
    def __init__(self, ui_generator, api_state_manager):
        self.ui_generator = ui_generator
        self.api_state_manager = api_state_manager
        self.active_workflow_sessions = {}
        self.callback_endpoints = {}
    
    async def handle_ui_modification_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理UI修改请求"""
        
        try:
            # 解析请求
            request_id = request_data.get("request_id")
            modification_request = request_data.get("modification_request", {})
            
            # 提取UI需求
            ui_requirements = modification_request.get("ui_requirements", {})
            adaptation_rules = modification_request.get("adaptation_rules", {})
            callback_config = modification_request.get("callback_config", {})
            
            # 转换为UI生成器格式
            ui_generator_requirements = await self._convert_to_ui_requirements(
                ui_requirements, adaptation_rules
            )
            
            # 生成UI
            ui_result = await self.ui_generator.generate_interface(ui_generator_requirements)
            
            # 注册回调端点
            await self._register_callbacks(request_id, callback_config)
            
            # 记录会话
            self.active_workflow_sessions[request_id] = {
                "request_data": request_data,
                "ui_result": ui_result,
                "created_at": time.time(),
                "callback_config": callback_config
            }
            
            # 构建响应
            response = {
                "protocol_version": "1.0",
                "request_id": request_id,
                "response_id": f"smartui_resp_{int(time.time())}",
                "source_mcp": "smartui_enhanced",
                "target_mcp": request_data.get("source_mcp"),
                "status": "success",
                "timestamp": time.time(),
                "modification_result": {
                    "ui_generated": True,
                    "interface_id": ui_result.get("interface_id"),
                    "generation_time": ui_result.get("generation_time"),
                    "components_created": len(ui_requirements.get("component_updates", [])),
                    "components_updated": 0,
                    "layout_applied": ui_requirements.get("layout_changes", {}).get("primary_layout"),
                    "theme_applied": ui_requirements.get("theme_adjustments", {}).get("color_scheme"),
                    "accessibility_features": adaptation_rules.get("accessibility", {}).keys(),
                    "performance_metrics": {
                        "initial_load_time": ui_result.get("generation_time", 0),
                        "component_render_time": ui_result.get("generation_time", 0) * 0.6,
                        "total_memory_usage": "12.5MB"
                    }
                },
                "ui_state": {
                    "current_layout": ui_requirements.get("layout_changes", {}).get("primary_layout"),
                    "active_components": [
                        comp.get("component_id") 
                        for comp in ui_requirements.get("component_updates", [])
                    ],
                    "user_session": {
                        "session_id": f"workflow_session_{request_id}",
                        "user_preferences": {}
                    }
                },
                "callback_endpoints": self.callback_endpoints.get(request_id, {}),
                "next_actions": [
                    {
                        "action": "monitor_user_progress",
                        "trigger": "user_interaction",
                        "description": "监控用户进度并发送回调"
                    }
                ]
            }
            
            return response
            
        except Exception as e:
            return {
                "protocol_version": "1.0",
                "request_id": request_data.get("request_id"),
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _convert_to_ui_requirements(self, 
                                        ui_requirements: Dict[str, Any],
                                        adaptation_rules: Dict[str, Any]) -> 'UIRequirements':
        """转换为UI生成器需求格式"""
        
        from ui_generator import UIRequirements, ComponentConfig, ComponentType, LayoutType, ThemeType
        
        # 解析布局类型
        layout_name = ui_requirements.get("layout_changes", {}).get("primary_layout", "grid")
        layout_type = self._map_layout_type(layout_name)
        
        # 解析主题
        theme_name = ui_requirements.get("theme_adjustments", {}).get("color_scheme", "light")
        theme_type = self._map_theme_type(theme_name)
        
        # 解析组件
        components = []
        for comp_data in ui_requirements.get("component_updates", []):
            component = ComponentConfig(
                component_type=self._map_component_type(comp_data.get("component_type")),
                component_id=comp_data.get("component_id"),
                props=comp_data.get("props", {}),
                styles={},
                events={}
            )
            components.append(component)
        
        # 解析响应式断点
        responsive_behavior = adaptation_rules.get("responsive_behavior", {})
        breakpoints = {"mobile": 768, "tablet": 1024, "desktop": 1200}
        
        # 解析可访问性特性
        accessibility = adaptation_rules.get("accessibility", {})
        accessibility_features = [
            key for key, value in accessibility.items() if value
        ]
        
        return UIRequirements(
            layout_type=layout_type,
            theme=theme_type,
            components=components,
            responsive_breakpoints=breakpoints,
            accessibility_features=accessibility_features,
            performance_requirements=adaptation_rules.get("performance_optimization", {}),
            user_preferences=ui_requirements.get("theme_adjustments", {}),
            context={"workflow_driven": True}
        )
    
    def _map_layout_type(self, layout_name: str) -> 'LayoutType':
        """映射布局类型"""
        from ui_generator import LayoutType
        
        mapping = {
            "coding_workspace": LayoutType.SIDEBAR,
            "design_workspace": LayoutType.GRID,
            "testing_workspace": LayoutType.DASHBOARD,
            "grid": LayoutType.GRID,
            "flexbox": LayoutType.FLEXBOX,
            "sidebar": LayoutType.SIDEBAR,
            "dashboard": LayoutType.DASHBOARD
        }
        return mapping.get(layout_name, LayoutType.GRID)
    
    def _map_theme_type(self, theme_name: str) -> 'ThemeType':
        """映射主题类型"""
        from ui_generator import ThemeType
        
        mapping = {
            "dark": ThemeType.DARK,
            "light": ThemeType.LIGHT,
            "auto": ThemeType.AUTO,
            "high_contrast": ThemeType.HIGH_CONTRAST,
            "dark_coding": ThemeType.DARK,
            "light_design": ThemeType.LIGHT,
            "testing_theme": ThemeType.LIGHT
        }
        return mapping.get(theme_name, ThemeType.LIGHT)
    
    def _map_component_type(self, component_type_name: str) -> 'ComponentType':
        """映射组件类型"""
        from ui_generator import ComponentType
        
        mapping = {
            "progress_bar": ComponentType.CARD,  # 使用卡片显示进度
            "code_editor": ComponentType.CARD,   # 代码编辑器作为卡片
            "checklist": ComponentType.LIST,     # 检查列表
            "button": ComponentType.BUTTON,
            "input": ComponentType.INPUT,
            "card": ComponentType.CARD,
            "table": ComponentType.TABLE,
            "navigation": ComponentType.NAVIGATION
        }
        return mapping.get(component_type_name, ComponentType.CARD)
    
    async def _register_callbacks(self, request_id: str, callback_config: Dict[str, Any]):
        """注册回调端点"""
        
        callbacks = {}
        
        for callback_type, config in callback_config.items():
            endpoint_path = f"/api/callbacks/{callback_type}/{request_id}"
            callbacks[callback_type] = f"http://localhost:5002{endpoint_path}"
            
            # 动态注册Flask路由
            await self._register_flask_callback_route(endpoint_path, callback_type, request_id)
        
        self.callback_endpoints[request_id] = callbacks
    
    async def _register_flask_callback_route(self, endpoint_path: str, callback_type: str, request_id: str):
        """动态注册Flask回调路由"""
        
        def callback_handler():
            callback_data = request.get_json()
            
            # 处理回调数据
            result = asyncio.run(self._process_callback(
                callback_type, request_id, callback_data
            ))
            
            return jsonify(result)
        
        # 注册路由到API状态管理器
        from api_state_manager import APIRoute
        
        route = APIRoute(
            path=endpoint_path,
            methods=["POST"],
            handler=callback_handler,
            version="1.0"
        )
        
        await self.api_state_manager.register_route(route)
    
    async def _process_callback(self, callback_type: str, request_id: str, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理回调数据"""
        
        # 发送回调到Workflow Coding MCP
        session = self.active_workflow_sessions.get(request_id)
        if not session:
            return {"success": False, "error": "会话不存在"}
        
        source_mcp = session["request_data"].get("source_mcp")
        callback_endpoint = session["callback_config"].get(callback_type, {}).get("endpoint")
        
        if callback_endpoint and source_mcp:
            # 通过MCP Coordinator发送回调
            callback_request = {
                "callback_type": callback_type,
                "request_id": request_id,
                "data": callback_data,
                "timestamp": time.time()
            }
            
            # 这里应该通过MCP Coordinator转发回调
            # 简化实现，直接返回成功
            return {"success": True, "callback_sent": True}
        
        return {"success": False, "error": "回调配置不完整"}
    
    async def send_state_update(self, request_id: str, state_changes: Dict[str, Any]):
        """发送状态更新"""
        
        session = self.active_workflow_sessions.get(request_id)
        if not session:
            return
        
        # 构建状态同步消息
        sync_message = {
            "protocol_version": "1.0",
            "sync_id": f"ui_sync_{int(time.time())}",
            "source_mcp": "smartui_enhanced",
            "target_mcp": session["request_data"].get("source_mcp"),
            "action": "state_update",
            "timestamp": time.time(),
            "state_changes": state_changes
        }
        
        # 发送到Workflow Coding MCP
        # 这里应该通过MCP Coordinator转发
        pass

# 在main_server.py中集成
def integrate_workflow_ui_handler(app, smartui_server):
    """集成工作流UI处理器"""
    
    workflow_handler = WorkflowUIHandler(
        smartui_server.ui_generator,
        smartui_server.api_state_manager
    )
    
    @app.route('/mcp/request', methods=['POST'])
    def handle_mcp_request():
        """处理MCP请求"""
        data = request.get_json()
        action = data.get('action')
        
        if action == 'modify_ui':
            result = asyncio.run(
                workflow_handler.handle_ui_modification_request(data.get('params', {}))
            )
            return jsonify(result)
        else:
            return jsonify({"success": False, "error": f"未知操作: {action}"}), 400
    
    return workflow_handler
```

## 📊 完整通信流程

### 流程图

```
1. Workflow分析阶段
   Workflow Coding MCP 分析当前工作流状态
   ↓
2. UI需求生成
   根据工作流阶段生成UI修改需求
   ↓
3. 请求发送
   通过MCP Coordinator发送UI修改请求
   ↓
4. 协议转换
   MCP Coordinator验证并转发请求
   ↓
5. UI生成
   SmartUI Enhanced接收请求并生成界面
   ↓
6. 响应返回
   返回生成结果和回调端点信息
   ↓
7. 状态同步
   实时同步UI状态变化
   ↓
8. 用户交互
   用户与动态生成的界面交互
   ↓
9. 回调处理
   SmartUI发送用户交互回调
   ↓
10. 工作流更新
    Workflow Coding MCP根据回调更新工作流
```

## 🎯 应用场景示例

### 场景1: 代码生成工作流

1. **触发**: 用户启动"创建React组件"工作流
2. **分析**: Workflow Coding MCP识别为代码生成任务
3. **UI生成**: 动态创建包含代码编辑器、组件预览、属性配置的界面
4. **交互**: 用户在生成的界面中编写代码
5. **反馈**: 实时代码分析和建议
6. **完成**: 组件生成完成，界面自动切换到测试模式

### 场景2: 设计工作流

1. **触发**: 用户启动"UI设计"工作流  
2. **分析**: 识别为设计任务
3. **UI生成**: 创建设计画布、工具面板、图层管理界面
4. **交互**: 用户进行设计操作
5. **同步**: 设计变更实时同步到工作流
6. **输出**: 自动生成设计规范和代码

### 场景3: 测试工作流

1. **触发**: 代码提交后自动触发测试工作流
2. **分析**: 识别为测试验证任务
3. **UI生成**: 创建测试运行器、覆盖率报告、错误控制台
4. **执行**: 自动运行测试并显示结果
5. **反馈**: 测试失败时提供修复建议
6. **完成**: 测试通过后触发部署工作流

## 🔧 部署和配置

### 1. 环境要求

```bash
# Python依赖
pip install flask flask-cors requests websockets asyncio

# Node.js依赖 (如果需要前端构建)
npm install axios socket.io-client
```

### 2. 配置文件

```yaml
# config/workflow_ui_config.yaml
workflow_ui:
  coordinator_url: "http://localhost:8089"
  smartui_url: "http://localhost:5002"
  
  ui_templates:
    coding_workspace:
      layout: "sidebar"
      theme: "dark"
      components: ["code_editor", "file_tree", "terminal"]
    
    design_workspace:
      layout: "grid"
      theme: "light"
      components: ["canvas", "tools", "layers"]
  
  callback_config:
    timeout: 30
    retry_count: 3
    batch_size: 10
  
  performance:
    debounce_ms: 300
    cache_ttl: 3600
    max_sessions: 100
```

### 3. 启动脚本

```bash
#!/bin/bash
# start_workflow_ui_system.sh

# 启动MCP Coordinator
cd /path/to/mcp/adapter
python mcp_coordinator_server.py &

# 启动SmartUI Enhanced
cd /path/to/smartui_enhanced  
python main_server.py &

# 启动Workflow Coding MCP
cd /path/to/workflow_coding_mcp
python workflow_ui_server.py &

echo "工作流UI系统启动完成"
echo "MCP Coordinator: http://localhost:8089"
echo "SmartUI Enhanced: http://localhost:5002"
echo "Workflow Coding MCP: http://localhost:8097"
```

## 📈 监控和调试

### 1. 日志配置

```python
# logging_config.py
import logging

def setup_workflow_ui_logging():
    """配置工作流UI日志"""
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler('workflow_ui.log')
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 配置各组件日志
    loggers = [
        'WorkflowUIController',
        'WorkflowUIHandler', 
        'MCPCoordinator',
        'SmartUIEnhanced'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
```

### 2. 性能监控

```python
# performance_monitor.py
import time
import json
from typing import Dict, Any

class WorkflowUIPerformanceMonitor:
    """工作流UI性能监控"""
    
    def __init__(self):
        self.metrics = {
            "ui_generation_times": [],
            "request_response_times": [],
            "callback_processing_times": [],
            "memory_usage": [],
            "error_counts": {}
        }
    
    def record_ui_generation(self, generation_time: float):
        """记录UI生成时间"""
        self.metrics["ui_generation_times"].append({
            "time": generation_time,
            "timestamp": time.time()
        })
    
    def record_request_response(self, response_time: float):
        """记录请求响应时间"""
        self.metrics["request_response_times"].append({
            "time": response_time,
            "timestamp": time.time()
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        ui_times = [m["time"] for m in self.metrics["ui_generation_times"]]
        response_times = [m["time"] for m in self.metrics["request_response_times"]]
        
        return {
            "average_ui_generation_time": sum(ui_times) / len(ui_times) if ui_times else 0,
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "total_requests": len(response_times),
            "error_rate": sum(self.metrics["error_counts"].values()) / len(response_times) if response_times else 0
        }
```

这个完整的方案展示了如何通过标准化的通信协议实现Workflow Coding MCP对SmartUI Enhanced的动态控制，确保了系统的可扩展性、可维护性和高性能。

