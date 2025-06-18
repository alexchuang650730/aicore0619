#!/usr/bin/env python3
"""
简化版SmartUI Enhanced演示服务器
专门用于演示Workflow UI集成功能
"""

import os
import sys
import json
import time
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

class SimpleSmartUIServer:
    """简化版SmartUI服务器"""
    
    def __init__(self):
        self.active_sessions = {}
        self.ui_templates = {
            "coding_workspace": {
                "layout": "sidebar",
                "components": ["code_editor", "progress_tracker", "task_checklist"],
                "theme": "dark"
            },
            "design_workspace": {
                "layout": "grid", 
                "components": ["design_canvas", "tool_palette", "layer_panel"],
                "theme": "light"
            },
            "testing_workspace": {
                "layout": "dashboard",
                "components": ["test_runner", "coverage_report", "error_console"],
                "theme": "testing"
            }
        }
    
    def handle_ui_modification_request(self, request_data):
        """处理UI修改请求"""
        
        try:
            request_id = request_data.get("request_id", f"ui_req_{int(time.time())}")
            modification_request = request_data.get("modification_request", {})
            
            # 提取UI需求
            ui_requirements = modification_request.get("ui_requirements", {})
            layout_changes = ui_requirements.get("layout_changes", {})
            component_updates = ui_requirements.get("component_updates", [])
            theme_adjustments = ui_requirements.get("theme_adjustments", {})
            
            # 模拟UI生成
            layout_type = layout_changes.get("primary_layout", "grid")
            theme = theme_adjustments.get("color_scheme", "light")
            
            # 记录会话
            self.active_sessions[request_id] = {
                "request_data": request_data,
                "layout": layout_type,
                "theme": theme,
                "components": [comp.get("component_id") for comp in component_updates],
                "created_at": time.time()
            }
            
            # 构建响应
            response = {
                "protocol_version": "1.0",
                "request_id": request_id,
                "response_id": f"smartui_resp_{int(time.time())}",
                "source_mcp": "smartui_enhanced",
                "target_mcp": request_data.get("source_mcp", "workflow_coding_mcp"),
                "status": "success",
                "timestamp": time.time(),
                "modification_result": {
                    "ui_generated": True,
                    "interface_id": f"ui_{request_id}",
                    "generation_time": 0.85,
                    "components_created": len(component_updates),
                    "components_updated": 0,
                    "layout_applied": layout_type,
                    "theme_applied": theme,
                    "accessibility_features": ["keyboard_navigation", "screen_reader_support"],
                    "performance_metrics": {
                        "initial_load_time": 0.6,
                        "component_render_time": 0.25,
                        "total_memory_usage": "8.2MB"
                    }
                },
                "ui_state": {
                    "current_layout": layout_type,
                    "active_components": [comp.get("component_id") for comp in component_updates],
                    "user_session": {
                        "session_id": f"session_{request_id}",
                        "user_preferences": theme_adjustments
                    }
                },
                "callback_endpoints": {
                    "progress_updates": f"http://localhost:5002/api/callbacks/progress/{request_id}",
                    "user_interactions": f"http://localhost:5002/api/callbacks/interactions/{request_id}",
                    "error_reporting": f"http://localhost:5002/api/callbacks/errors/{request_id}"
                },
                "next_actions": [
                    {
                        "action": "monitor_user_progress",
                        "trigger": "user_interaction",
                        "description": "监控用户进度并发送回调"
                    },
                    {
                        "action": "auto_save_state",
                        "trigger": "timer_30s", 
                        "description": "每30秒自动保存界面状态"
                    }
                ]
            }
            
            return response
            
        except Exception as e:
            return {
                "protocol_version": "1.0",
                "request_id": request_data.get("request_id", "unknown"),
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }

# 全局服务器实例
smartui_server = SimpleSmartUIServer()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "SmartUI Enhanced Demo",
        "version": "1.0.0",
        "timestamp": time.time(),
        "active_sessions": len(smartui_server.active_sessions)
    })

@app.route('/mcp/request', methods=['POST'])
def handle_mcp_request():
    """处理MCP请求"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        if action == 'modify_ui':
            result = smartui_server.handle_ui_modification_request(data.get('params', {}))
            return jsonify(result)
        else:
            return jsonify({
                "success": False, 
                "error": f"未知操作: {action}"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"请求处理失败: {str(e)}"
        }), 500

@app.route('/api/ui/generate', methods=['POST'])
def generate_ui():
    """直接UI生成接口"""
    try:
        data = request.get_json()
        result = smartui_server.handle_ui_modification_request(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """获取活跃会话"""
    return jsonify({
        "active_sessions": len(smartui_server.active_sessions),
        "sessions": list(smartui_server.active_sessions.keys())
    })

@app.route('/api/callbacks/<callback_type>/<request_id>', methods=['POST'])
def handle_callback(callback_type, request_id):
    """处理回调"""
    callback_data = request.get_json()
    
    # 模拟回调处理
    return jsonify({
        "success": True,
        "callback_type": callback_type,
        "request_id": request_id,
        "processed_at": time.time()
    })

if __name__ == '__main__':
    print("🚀 启动SmartUI Enhanced演示服务器")
    print("=" * 50)
    print("服务地址: http://localhost:5002")
    print("健康检查: http://localhost:5002/health")
    print("MCP接口: http://localhost:5002/mcp/request")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5002, debug=False)

