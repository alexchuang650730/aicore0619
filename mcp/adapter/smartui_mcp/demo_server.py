"""
SmartUI MCP 演示服务器

这个演示服务器展示了SmartUI MCP作为组件级adapter的完整功能，
包括智慧感知UI生成、用户行为分析、主题管理等核心能力。

基于三层架构：
- coding_plugin_orchestrator (产品级)
- workflow orchestrator (工作流级)  
- mcp/adapter组件 (组件级) ← SmartUI MCP演示

作者: Manus AI
版本: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main_server import SmartUIMCPServer
from src.mcp_communication.coordinator_integration import ComponentCapability, OrchestrationLevel


class SmartUIMCPDemoServer:
    """
    SmartUI MCP 演示服务器
    
    提供Web界面来演示SmartUI MCP的各种功能和能力
    """
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # SmartUI MCP服务器实例
        self.smartui_server: Optional[SmartUIMCPServer] = None
        
        # FastAPI应用
        self.app = FastAPI(
            title="SmartUI MCP Demo",
            description="智慧感知UI组件演示服务器",
            version="1.0.0"
        )
        
        # WebSocket连接管理
        self.websocket_connections: List[WebSocket] = []
        
        # 设置CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 设置路由
        self._setup_routes()
        
        self.logger.info("SmartUI MCP Demo Server initialized")
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_demo_page():
            """获取演示页面"""
            return self._generate_demo_html()
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            if self.smartui_server:
                health_status = await self.smartui_server.get_health_status()
                return health_status
            else:
                return {"status": "smartui_server_not_initialized"}
        
        @self.app.post("/api/ui/generate")
        async def generate_ui(request: Dict[str, Any]):
            """生成UI配置"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                # 通过协调器集成调用UI生成能力
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.UI_GENERATION
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error generating UI: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/analysis/user")
        async def analyze_user(request: Dict[str, Any]):
            """分析用户行为"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.USER_ANALYSIS
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error analyzing user: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/ui/theme")
        async def manage_theme(request: Dict[str, Any]):
            """管理主题"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.THEME_MANAGEMENT
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error managing theme: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/ui/layout/optimize")
        async def optimize_layout(request: Dict[str, Any]):
            """优化布局"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.LAYOUT_OPTIMIZATION
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error optimizing layout: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/component/render")
        async def render_component(request: Dict[str, Any]):
            """渲染组件"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.COMPONENT_RENDERING
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error rendering component: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/state/manage")
        async def manage_state(request: Dict[str, Any]):
            """管理状态"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.STATE_MANAGEMENT
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error managing state: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/accessibility/apply")
        async def apply_accessibility(request: Dict[str, Any]):
            """应用可访问性功能"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.ACCESSIBILITY_SUPPORT
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error applying accessibility: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/performance/optimize")
        async def optimize_performance(request: Dict[str, Any]):
            """优化性能"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    raise HTTPException(status_code=503, detail="SmartUI MCP not ready")
                
                result = await self.smartui_server.coordinator_integration.capability_handlers[
                    ComponentCapability.PERFORMANCE_OPTIMIZATION
                ](request)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error optimizing performance: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/capabilities")
        async def get_capabilities():
            """获取组件能力列表"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    return {"capabilities": []}
                
                capabilities = list(self.smartui_server.coordinator_integration.capability_handlers.keys())
                return {
                    "capabilities": [cap.value for cap in capabilities],
                    "total": len(capabilities),
                    "registration_info": self.smartui_server.coordinator_integration.get_registration_info()
                }
                
            except Exception as e:
                self.logger.error(f"Error getting capabilities: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/orchestrators")
        async def get_orchestrator_connections():
            """获取编排器连接状态"""
            try:
                if not self.smartui_server or not self.smartui_server.coordinator_integration:
                    return {"connections": {}}
                
                connections = self.smartui_server.coordinator_integration.get_orchestrator_connections()
                return {
                    "connections": {level.value: info for level, info in connections.items()},
                    "total": len(connections)
                }
                
            except Exception as e:
                self.logger.error(f"Error getting orchestrator connections: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket端点，用于实时通信"""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            
            try:
                while True:
                    # 接收客户端消息
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # 处理消息
                    response = await self._handle_websocket_message(message)
                    
                    # 发送响应
                    await websocket.send_text(json.dumps(response))
                    
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
                self.logger.info("WebSocket client disconnected")
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                if websocket in self.websocket_connections:
                    self.websocket_connections.remove(websocket)
    
    async def _handle_websocket_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """处理WebSocket消息"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "ui_interaction":
                # 处理UI交互事件
                if self.smartui_server and self.smartui_server.user_analyzer:
                    await self.smartui_server.user_analyzer.track_interaction(data)
                
                return {
                    "type": "interaction_tracked",
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            
            elif message_type == "request_ui_update":
                # 请求UI更新
                if self.smartui_server and self.smartui_server.coordinator_integration:
                    result = await self.smartui_server.coordinator_integration.capability_handlers[
                        ComponentCapability.UI_GENERATION
                    ](data)
                    
                    return {
                        "type": "ui_update",
                        "success": result.get("success", False),
                        "ui_config": result.get("ui_config"),
                        "timestamp": datetime.now().isoformat()
                    }
            
            elif message_type == "get_status":
                # 获取状态信息
                if self.smartui_server:
                    health_status = await self.smartui_server.get_health_status()
                    return {
                        "type": "status",
                        "data": health_status,
                        "timestamp": datetime.now().isoformat()
                    }
            
            else:
                return {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
            return {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_demo_html(self) -> str:
        """生成演示页面HTML"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartUI MCP 演示</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .demo-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .demo-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 48px rgba(0,0,0,0.15);
        }
        
        .demo-card h3 {
            color: #667eea;
            margin-bottom: 16px;
            font-size: 1.4rem;
        }
        
        .demo-card p {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .demo-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .demo-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
        }
        
        .demo-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-panel {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .status-panel h3 {
            color: #667eea;
            margin-bottom: 16px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-indicator.online {
            background: #4CAF50;
        }
        
        .status-indicator.offline {
            background: #f44336;
        }
        
        .result-area {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
            border-left: 4px solid #667eea;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .architecture-info {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 24px;
            color: white;
            margin-bottom: 20px;
        }
        
        .architecture-info h3 {
            margin-bottom: 16px;
            font-size: 1.3rem;
        }
        
        .architecture-levels {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
        }
        
        .level {
            background: rgba(255,255,255,0.2);
            padding: 12px 20px;
            border-radius: 8px;
            text-align: center;
            flex: 1;
            margin: 0 10px;
        }
        
        .level:first-child {
            margin-left: 0;
        }
        
        .level:last-child {
            margin-right: 0;
        }
        
        .arrow {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .architecture-levels {
                flex-direction: column;
            }
            
            .arrow {
                transform: rotate(90deg);
                margin: 10px 0;
            }
            
            .level {
                margin: 5px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 SmartUI MCP</h1>
            <p>智慧感知UI组件演示 - 组件级Adapter</p>
        </div>
        
        <div class="architecture-info">
            <h3>🏗️ 三层架构</h3>
            <div class="architecture-levels">
                <div class="level">
                    <strong>产品级</strong><br>
                    coding_plugin_orchestrator
                </div>
                <div class="arrow">→</div>
                <div class="level">
                    <strong>工作流级</strong><br>
                    workflow orchestrator
                </div>
                <div class="arrow">→</div>
                <div class="level" style="background: rgba(255,255,255,0.3);">
                    <strong>组件级</strong><br>
                    SmartUI MCP (当前)
                </div>
            </div>
        </div>
        
        <div class="status-panel">
            <h3>📊 系统状态</h3>
            <div id="status-content">
                <span class="status-indicator offline"></span>
                <span>正在连接...</span>
            </div>
        </div>
        
        <div class="demo-grid">
            <div class="demo-card">
                <h3>🎨 UI生成</h3>
                <p>智能生成UI配置，根据用户需求和上下文自动创建最适合的界面布局。</p>
                <button class="demo-button" onclick="testUIGeneration()">测试UI生成</button>
                <div id="ui-generation-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>👤 用户分析</h3>
                <p>分析用户行为模式，识别用户偏好和使用习惯，为智能适配提供数据支持。</p>
                <button class="demo-button" onclick="testUserAnalysis()">测试用户分析</button>
                <div id="user-analysis-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>🎭 主题管理</h3>
                <p>智能主题切换和自定义，支持亮色、暗色、高对比度等多种主题模式。</p>
                <button class="demo-button" onclick="testThemeManagement()">测试主题管理</button>
                <div id="theme-management-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>📐 布局优化</h3>
                <p>根据屏幕尺寸和设备类型自动优化布局，确保最佳的用户体验。</p>
                <button class="demo-button" onclick="testLayoutOptimization()">测试布局优化</button>
                <div id="layout-optimization-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>🧩 组件渲染</h3>
                <p>高性能组件渲染系统，支持动态组件加载和实时更新。</p>
                <button class="demo-button" onclick="testComponentRendering()">测试组件渲染</button>
                <div id="component-rendering-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>🔄 状态管理</h3>
                <p>智能状态管理，自动同步UI状态与后端数据，确保数据一致性。</p>
                <button class="demo-button" onclick="testStateManagement()">测试状态管理</button>
                <div id="state-management-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>♿ 可访问性</h3>
                <p>完整的无障碍功能支持，包括屏幕阅读器、键盘导航等。</p>
                <button class="demo-button" onclick="testAccessibility()">测试可访问性</button>
                <div id="accessibility-result" class="result-area" style="display: none;"></div>
            </div>
            
            <div class="demo-card">
                <h3>⚡ 性能优化</h3>
                <p>智能性能优化，包括懒加载、虚拟滚动、缓存策略等。</p>
                <button class="demo-button" onclick="testPerformanceOptimization()">测试性能优化</button>
                <div id="performance-optimization-result" class="result-area" style="display: none;"></div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        
        // 初始化WebSocket连接
        function initWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket连接已建立');
                updateStatus(true);
                loadSystemStatus();
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                console.log('收到WebSocket消息:', message);
            };
            
            ws.onclose = function() {
                console.log('WebSocket连接已关闭');
                updateStatus(false);
                // 尝试重连
                setTimeout(initWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket错误:', error);
                updateStatus(false);
            };
        }
        
        // 更新状态显示
        function updateStatus(isOnline) {
            const statusContent = document.getElementById('status-content');
            const indicator = statusContent.querySelector('.status-indicator');
            
            if (isOnline) {
                indicator.className = 'status-indicator online';
                statusContent.innerHTML = '<span class="status-indicator online"></span><span>系统在线 - SmartUI MCP 运行正常</span>';
            } else {
                indicator.className = 'status-indicator offline';
                statusContent.innerHTML = '<span class="status-indicator offline"></span><span>系统离线 - 正在尝试重连...</span>';
            }
        }
        
        // 加载系统状态
        async function loadSystemStatus() {
            try {
                const response = await fetch('/health');
                const status = await response.json();
                
                const statusContent = document.getElementById('status-content');
                statusContent.innerHTML = `
                    <span class="status-indicator online"></span>
                    <span>系统在线 - 服务器状态: ${status.server_status}</span>
                    <br><small>组件数量: ${Object.keys(status.components || {}).length}</small>
                `;
            } catch (error) {
                console.error('加载系统状态失败:', error);
            }
        }
        
        // API调用辅助函数
        async function callAPI(endpoint, data = {}) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                return await response.json();
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
        
        // 显示结果
        function showResult(elementId, result) {
            const resultElement = document.getElementById(elementId);
            resultElement.style.display = 'block';
            resultElement.textContent = JSON.stringify(result, null, 2);
        }
        
        // 测试UI生成
        async function testUIGeneration() {
            const result = await callAPI('/api/ui/generate', {
                layout_type: 'dashboard',
                theme: 'modern',
                components: ['header', 'sidebar', 'main_content'],
                user_preferences: {
                    color_scheme: 'blue',
                    density: 'comfortable'
                }
            });
            showResult('ui-generation-result', result);
        }
        
        // 测试用户分析
        async function testUserAnalysis() {
            const result = await callAPI('/api/analysis/user', {
                user_interactions: [
                    { type: 'click', element: 'button', timestamp: Date.now() },
                    { type: 'scroll', direction: 'down', timestamp: Date.now() - 1000 }
                ],
                session_duration: 300,
                device_info: {
                    type: 'desktop',
                    screen_size: '1920x1080'
                }
            });
            showResult('user-analysis-result', result);
        }
        
        // 测试主题管理
        async function testThemeManagement() {
            const result = await callAPI('/api/ui/theme', {
                theme_name: 'dark',
                custom_colors: {
                    primary: '#667eea',
                    secondary: '#764ba2'
                },
                accessibility_mode: false
            });
            showResult('theme-management-result', result);
        }
        
        // 测试布局优化
        async function testLayoutOptimization() {
            const result = await callAPI('/api/ui/layout/optimize', {
                current_layout: 'grid',
                screen_size: { width: 1920, height: 1080 },
                device_type: 'desktop',
                content_density: 'high'
            });
            showResult('layout-optimization-result', result);
        }
        
        // 测试组件渲染
        async function testComponentRendering() {
            const result = await callAPI('/api/component/render', {
                component_type: 'data_table',
                props: {
                    data: [
                        { id: 1, name: '示例1', status: 'active' },
                        { id: 2, name: '示例2', status: 'inactive' }
                    ],
                    columns: ['id', 'name', 'status']
                },
                render_options: {
                    virtual_scrolling: true,
                    lazy_loading: true
                }
            });
            showResult('component-rendering-result', result);
        }
        
        // 测试状态管理
        async function testStateManagement() {
            const result = await callAPI('/api/state/manage', {
                action: 'update',
                state_path: 'user.preferences',
                new_value: {
                    theme: 'dark',
                    language: 'zh-CN',
                    notifications: true
                },
                sync_to_backend: true
            });
            showResult('state-management-result', result);
        }
        
        // 测试可访问性
        async function testAccessibility() {
            const result = await callAPI('/api/accessibility/apply', {
                features: ['high_contrast', 'large_fonts', 'screen_reader'],
                user_needs: {
                    visual_impairment: false,
                    motor_impairment: false,
                    cognitive_impairment: false
                }
            });
            showResult('accessibility-result', result);
        }
        
        // 测试性能优化
        async function testPerformanceOptimization() {
            const result = await callAPI('/api/performance/optimize', {
                optimization_targets: ['load_time', 'memory_usage', 'render_performance'],
                current_metrics: {
                    load_time: 2.5,
                    memory_usage: 150,
                    fps: 45
                },
                optimization_level: 'aggressive'
            });
            showResult('performance-optimization-result', result);
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initWebSocket();
        });
    </script>
</body>
</html>
        """
    
    async def start_smartui_server(self):
        """启动SmartUI MCP服务器"""
        try:
            self.smartui_server = SmartUIMCPServer()
            
            # 在后台启动SmartUI服务器
            asyncio.create_task(self.smartui_server.start_server())
            
            # 等待一段时间让服务器初始化
            await asyncio.sleep(2)
            
            self.logger.info("SmartUI MCP Server started in background")
            
        except Exception as e:
            self.logger.error(f"Failed to start SmartUI MCP Server: {e}")
            raise
    
    async def start_demo_server(self):
        """启动演示服务器"""
        try:
            self.logger.info(f"Starting SmartUI MCP Demo Server on port {self.port}...")
            
            # 启动SmartUI服务器
            await self.start_smartui_server()
            
            # 启动演示服务器
            config = uvicorn.Config(
                app=self.app,
                host="0.0.0.0",
                port=self.port,
                log_level="info"
            )
            
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"Failed to start demo server: {e}")
            raise
    
    async def shutdown(self):
        """关闭服务器"""
        try:
            self.logger.info("Shutting down SmartUI MCP Demo Server...")
            
            # 关闭所有WebSocket连接
            for ws in self.websocket_connections:
                try:
                    await ws.close()
                except:
                    pass
            
            # 关闭SmartUI服务器
            if self.smartui_server:
                await self.smartui_server.shutdown()
            
            self.logger.info("Demo server shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


async def main():
    """主函数"""
    demo_server = None
    try:
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 创建演示服务器
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
        demo_server = SmartUIMCPDemoServer(port)
        
        # 启动服务器
        await demo_server.start_demo_server()
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"Demo server error: {e}")
        sys.exit(1)
    finally:
        if demo_server:
            await demo_server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

