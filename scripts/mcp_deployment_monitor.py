#!/usr/bin/env python3
"""
MCP部署监控服务
让用户能在后台实时看到KiloCode MCP的部署进展
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# 部署状态存储
deployment_status = {
    "current_step": 1,
    "total_steps": 4,
    "steps": [
        {
            "id": 1,
            "name": "创建部署监控",
            "status": "in_progress",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "details": "设置部署状态监控接口",
            "logs": ["启动部署监控服务"]
        },
        {
            "id": 2,
            "name": "部署KiloCode MCP",
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "details": "将KiloCode MCP部署到生产环境",
            "logs": []
        },
        {
            "id": 3,
            "name": "SmartUI集成",
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "details": "与SmartUI管理界面集成",
            "logs": []
        },
        {
            "id": 4,
            "name": "工作流注册",
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "details": "注册到工作流系统",
            "logs": []
        }
    ],
    "overall_status": "deploying",
    "start_time": datetime.now().isoformat(),
    "end_time": None
}

def update_step_status(step_id, status, log_message=None):
    """更新步骤状态"""
    for step in deployment_status["steps"]:
        if step["id"] == step_id:
            step["status"] = status
            if status == "in_progress" and not step["start_time"]:
                step["start_time"] = datetime.now().isoformat()
            elif status in ["completed", "failed"]:
                step["end_time"] = datetime.now().isoformat()
            
            if log_message:
                step["logs"].append(f"{datetime.now().strftime('%H:%M:%S')} - {log_message}")
            break
    
    # 更新当前步骤
    if status == "completed":
        deployment_status["current_step"] = min(step_id + 1, deployment_status["total_steps"])
    
    # 更新整体状态
    completed_steps = sum(1 for step in deployment_status["steps"] if step["status"] == "completed")
    if completed_steps == deployment_status["total_steps"]:
        deployment_status["overall_status"] = "completed"
        deployment_status["end_time"] = datetime.now().isoformat()

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>KiloCode MCP 部署监控</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .status-overview { display: flex; justify-content: space-between; margin-bottom: 30px; }
        .status-card { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; flex: 1; margin: 0 10px; }
        .step { border: 1px solid #ddd; margin-bottom: 15px; border-radius: 6px; overflow: hidden; }
        .step-header { padding: 15px; background: #f8f9fa; display: flex; justify-content: space-between; align-items: center; }
        .step-content { padding: 15px; display: none; }
        .step.active .step-content { display: block; }
        .status-badge { padding: 4px 12px; border-radius: 20px; color: white; font-size: 12px; }
        .status-pending { background: #6c757d; }
        .status-in_progress { background: #007bff; }
        .status-completed { background: #28a745; }
        .status-failed { background: #dc3545; }
        .logs { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; }
        .progress-bar { width: 100%; height: 20px; background: #e9ecef; border-radius: 10px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; background: #007bff; transition: width 0.3s ease; }
        .refresh-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .refresh-btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 KiloCode MCP 部署监控</h1>
            <p>实时监控MCP部署进展</p>
            <button class="refresh-btn" onclick="refreshStatus()">刷新状态</button>
        </div>
        
        <div class="status-overview">
            <div class="status-card">
                <h3>整体状态</h3>
                <span id="overall-status" class="status-badge">加载中...</span>
            </div>
            <div class="status-card">
                <h3>当前步骤</h3>
                <span id="current-step">-/-</span>
            </div>
            <div class="status-card">
                <h3>开始时间</h3>
                <span id="start-time">-</span>
            </div>
            <div class="status-card">
                <h3>预计完成</h3>
                <span id="estimated-time">计算中...</span>
            </div>
        </div>
        
        <div class="progress-bar">
            <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
        </div>
        
        <div id="steps-container">
            <!-- 步骤将通过JavaScript动态加载 -->
        </div>
    </div>

    <script>
        function refreshStatus() {
            fetch('/api/deployment-status')
                .then(response => response.json())
                .then(data => updateUI(data))
                .catch(error => console.error('Error:', error));
        }
        
        function updateUI(status) {
            // 更新概览信息
            document.getElementById('overall-status').textContent = status.overall_status;
            document.getElementById('overall-status').className = 'status-badge status-' + status.overall_status;
            document.getElementById('current-step').textContent = status.current_step + '/' + status.total_steps;
            document.getElementById('start-time').textContent = new Date(status.start_time).toLocaleTimeString();
            
            // 更新进度条
            const progress = (status.current_step - 1) / status.total_steps * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
            
            // 更新步骤
            const container = document.getElementById('steps-container');
            container.innerHTML = '';
            
            status.steps.forEach(step => {
                const stepDiv = document.createElement('div');
                stepDiv.className = 'step' + (step.status === 'in_progress' ? ' active' : '');
                
                stepDiv.innerHTML = `
                    <div class="step-header" onclick="toggleStep(${step.id})">
                        <div>
                            <strong>步骤 ${step.id}: ${step.name}</strong>
                            <div style="font-size: 12px; color: #666;">${step.details}</div>
                        </div>
                        <span class="status-badge status-${step.status}">${getStatusText(step.status)}</span>
                    </div>
                    <div class="step-content">
                        <div class="logs">
                            ${step.logs.map(log => '<div>' + log + '</div>').join('')}
                        </div>
                    </div>
                `;
                
                container.appendChild(stepDiv);
            });
        }
        
        function getStatusText(status) {
            const statusMap = {
                'pending': '等待中',
                'in_progress': '进行中',
                'completed': '已完成',
                'failed': '失败'
            };
            return statusMap[status] || status;
        }
        
        function toggleStep(stepId) {
            const step = document.querySelector('.step:nth-child(' + stepId + ')');
            step.classList.toggle('active');
        }
        
        // 自动刷新
        setInterval(refreshStatus, 3000);
        
        // 初始加载
        refreshStatus();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """部署监控仪表板"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/deployment-status')
def get_deployment_status():
    """获取部署状态API"""
    return jsonify(deployment_status)

@app.route('/api/update-step', methods=['POST'])
def update_step():
    """更新步骤状态API"""
    data = request.get_json()
    step_id = data.get('step_id')
    status = data.get('status')
    log_message = data.get('log_message')
    
    update_step_status(step_id, status, log_message)
    return jsonify({"success": True})

@app.route('/api/add-log', methods=['POST'])
def add_log():
    """添加日志API"""
    data = request.get_json()
    step_id = data.get('step_id')
    log_message = data.get('log_message')
    
    for step in deployment_status["steps"]:
        if step["id"] == step_id:
            step["logs"].append(f"{datetime.now().strftime('%H:%M:%S')} - {log_message}")
            break
    
    return jsonify({"success": True})

if __name__ == "__main__":
    # 完成第一步
    update_step_status(1, "completed", "部署监控服务已启动")
    
    print("🚀 MCP部署监控服务启动")
    print("📍 监控地址: http://98.81.255.168:9000")
    print("📊 您可以在浏览器中实时查看部署进展")
    
    app.run(host='0.0.0.0', port=9000, debug=False)

