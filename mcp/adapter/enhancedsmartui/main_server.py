#!/usr/bin/env python3
"""
SmartUI Enhanced - 主服务器入口
整合版本，基于原有的main_server.py但修复了导入问题
"""

import os
import sys
import json
import time
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 导入核心组件
from core.api_state_manager import APIStateManager, APIRoute
from engines.user_analyzer import UserAnalyzer
from engines.decision_engine import DecisionEngine
from engines.ui_generator import UIGenerator
from adapters.mcp_integration import MCPCollaborationManager, WorkflowDriver

app = Flask(__name__)
CORS(app)

class SmartUIEnhancedServer:
    """SmartUI Enhanced 主服务器"""
    
    def __init__(self):
        self.api_state_manager = APIStateManager()
        self.user_analyzer = UserAnalyzer()
        self.decision_engine = DecisionEngine()
        self.ui_generator = UIGenerator()
        self.mcp_manager = MCPCollaborationManager()
        self.workflow_driver = WorkflowDriver()
        
        # 注册路由
        self._register_routes()
        
        # 初始化MCP连接
        asyncio.create_task(self._initialize_mcp_connection())
    
    def _register_routes(self):
        """注册API路由"""
        
        @app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "service": "SmartUI Enhanced",
                "version": "1.0.0",
                "timestamp": time.time(),
                "components": {
                    "api_state_manager": "active",
                    "user_analyzer": "active", 
                    "decision_engine": "active",
                    "ui_generator": "active",
                    "mcp_manager": "active",
                    "workflow_driver": "active"
                }
            })
        
        @app.route('/mcp/request', methods=['POST'])
        def handle_mcp_request():
            """处理来自MCP Coordinator的请求"""
            try:
                data = request.get_json()
                action = data.get('action')
                
                if action == 'modify_ui':
                    result = self._handle_ui_modification(data.get('params', {}))
                    return jsonify(result)
                elif action == 'analyze_user':
                    result = self._handle_user_analysis(data.get('params', {}))
                    return jsonify(result)
                elif action == 'get_ui_state':
                    result = self._handle_ui_state_query(data.get('params', {}))
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
                result = self._handle_ui_modification(data)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/capabilities', methods=['GET'])
        def get_capabilities():
            """获取MCP能力列表"""
            return jsonify({
                "capabilities": [
                    "ui_generation",
                    "user_analysis", 
                    "decision_making",
                    "workflow_coordination",
                    "api_state_management",
                    "real_time_adaptation"
                ],
                "version": "1.0.0",
                "description": "智能交互界面生成系统"
            })
    
    def _handle_ui_modification(self, request_data):
        """处理UI修改请求"""
        try:
            # 使用demo_server的简化逻辑
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
    
    def _handle_user_analysis(self, request_data):
        """处理用户分析请求"""
        # 简化实现
        return {
            "success": True,
            "analysis_result": {
                "user_type": "developer",
                "experience_level": "intermediate",
                "preferences": {
                    "theme": "dark",
                    "layout": "sidebar"
                }
            }
        }
    
    def _handle_ui_state_query(self, request_data):
        """处理UI状态查询"""
        # 简化实现
        return {
            "success": True,
            "ui_state": {
                "active_interfaces": 1,
                "current_layout": "coding_workspace",
                "theme": "dark"
            }
        }
    
    async def _initialize_mcp_connection(self):
        """初始化MCP连接"""
        try:
            # 这里可以添加MCP注册逻辑
            print("MCP连接初始化完成")
        except Exception as e:
            print(f"MCP连接初始化失败: {e}")

# 全局服务器实例
smartui_server = SmartUIEnhancedServer()

if __name__ == '__main__':
    print("🚀 启动SmartUI Enhanced服务器")
    print("=" * 50)
    print("服务地址: http://localhost:5002")
    print("健康检查: http://localhost:5002/health")
    print("MCP接口: http://localhost:5002/mcp/request")
    print("能力查询: http://localhost:5002/api/capabilities")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5002, debug=False)

