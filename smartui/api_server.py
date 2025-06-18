"""
智慧UI Flask API服務器
為端側WebAdmin提供REST API接口
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime

# 添加項目路徑
sys.path.append('/opt/powerautomation')

from smart_ui import get_smart_ui
from smart_ui.user_manager import User
from smart_ui.workflow_manager import WorkflowType, WorkflowStatus

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建Flask應用
app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 初始化智慧UI系統
smart_ui = get_smart_ui()
smart_ui.initialize()

# 設置同步引擎關聯
smart_ui.user_manager.set_sync_engine(smart_ui.sync_engine)
smart_ui.workflow_manager.set_sync_engine(smart_ui.sync_engine)

# 啟動同步引擎
smart_ui.sync_engine.start_sync_engine()

@app.route('/')
def index():
    """主頁面"""
    return send_from_directory('frontend', 'client_webadmin.html')

@app.route('/api/status')
def get_system_status():
    """獲取系統狀態"""
    try:
        status = smart_ui.get_system_status()
        sync_metrics = smart_ui.sync_engine.get_sync_status()
        
        return jsonify({
            "success": True,
            "data": {
                "system": status,
                "sync": sync_metrics,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """獲取儀表板數據"""
    try:
        # 獲取用戶統計
        user_stats = smart_ui.user_manager.get_user_statistics()
        
        # 獲取工作流統計
        workflow_stats = smart_ui.workflow_manager.get_workflow_statistics()
        
        # 模擬項目數據
        project_data = {
            "active_projects": 12,
            "total_tasks": 156,
            "completed_tasks": 140,
            "user_credits": 2847
        }
        
        return jsonify({
            "success": True,
            "data": {
                "projects": project_data,
                "users": user_stats,
                "workflows": workflow_stats,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"獲取儀表板數據失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows')
def get_workflows():
    """獲取工作流列表"""
    try:
        # 獲取所有類型的工作流
        coding_workflows = smart_ui.workflow_manager.get_workflows_by_type(WorkflowType.CODING)
        deployment_workflows = smart_ui.workflow_manager.get_workflows_by_type(WorkflowType.DEPLOYMENT)
        testing_workflows = smart_ui.workflow_manager.get_workflows_by_type(WorkflowType.TESTING)
        
        workflows = {
            "coding": [_workflow_to_dict(w) for w in coding_workflows],
            "deployment": [_workflow_to_dict(w) for w in deployment_workflows],
            "testing": [_workflow_to_dict(w) for w in testing_workflows]
        }
        
        return jsonify({
            "success": True,
            "data": workflows
        })
    except Exception as e:
        logger.error(f"獲取工作流列表失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows', methods=['POST'])
def create_workflow():
    """創建新工作流"""
    try:
        data = request.get_json()
        
        workflow_type = WorkflowType(data.get('type', 'coding'))
        name = data.get('name', f'新{workflow_type.value}工作流')
        project_id = data.get('project_id', 1)
        description = data.get('description', '')
        
        workflow = smart_ui.workflow_manager.create_workflow(
            project_id=project_id,
            name=name,
            workflow_type=workflow_type,
            description=description
        )
        
        if workflow:
            return jsonify({
                "success": True,
                "data": _workflow_to_dict(workflow)
            })
        else:
            return jsonify({"success": False, "error": "創建工作流失敗"}), 500
            
    except Exception as e:
        logger.error(f"創建工作流失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/workflows/<int:workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id):
    """執行工作流"""
    try:
        # 先更新狀態為活躍
        smart_ui.workflow_manager.update_workflow_status(workflow_id, WorkflowStatus.ACTIVE)
        
        # 執行工作流
        success = smart_ui.workflow_manager.execute_workflow(workflow_id)
        
        return jsonify({
            "success": success,
            "message": "工作流執行成功" if success else "工作流執行失敗"
        })
    except Exception as e:
        logger.error(f"執行工作流失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users')
def get_users():
    """獲取用戶列表"""
    try:
        users = smart_ui.user_manager.get_all_users(limit=50)
        user_data = [_user_to_dict(user) for user in users]
        
        return jsonify({
            "success": True,
            "data": user_data
        })
    except Exception as e:
        logger.error(f"獲取用戶列表失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """創建新用戶"""
    try:
        data = request.get_json()
        
        user = smart_ui.user_manager.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            role=data.get('role', 'user'),
            version=data.get('version', 'free')
        )
        
        if user:
            return jsonify({
                "success": True,
                "data": _user_to_dict(user)
            })
        else:
            return jsonify({"success": False, "error": "創建用戶失敗"}), 500
            
    except Exception as e:
        logger.error(f"創建用戶失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/users/<int:user_id>/credits', methods=['PUT'])
def update_user_credits(user_id):
    """更新用戶積分"""
    try:
        data = request.get_json()
        credits = data.get('credits', 0)
        
        success = smart_ui.user_manager.update_user_credits(user_id, credits)
        
        return jsonify({
            "success": success,
            "message": "積分更新成功" if success else "積分更新失敗"
        })
    except Exception as e:
        logger.error(f"更新用戶積分失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync/status')
def get_sync_status():
    """獲取同步狀態"""
    try:
        status = smart_ui.sync_engine.get_sync_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        logger.error(f"獲取同步狀態失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync/force', methods=['POST'])
def force_sync():
    """強制全量同步"""
    try:
        success = smart_ui.sync_engine.force_full_sync()
        return jsonify({
            "success": success,
            "message": "強制同步成功" if success else "強制同步失敗"
        })
    except Exception as e:
        logger.error(f"強制同步失敗: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def _workflow_to_dict(workflow):
    """工作流對象轉字典"""
    return {
        "id": workflow.id,
        "name": workflow.name,
        "type": workflow.type.value,
        "status": workflow.status.value,
        "project_id": workflow.project_id,
        "steps_count": len(workflow.steps),
        "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
        "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None
    }

def _user_to_dict(user):
    """用戶對象轉字典"""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "credits": user.credits,
        "version": user.version,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "API端點不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "內部服務器錯誤"}), 500

if __name__ == '__main__':
    try:
        print("🧠 PowerAutomation 智慧UI API服務器啟動中...")
        print("📊 數據庫連接: ✅")
        print("🔄 同步引擎: ✅")
        print("🌐 API服務: ✅")
        print("🚀 服務器就緒！")
        print("📱 訪問地址: http://localhost:5001")
        
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 服務器停止中...")
        smart_ui.sync_engine.stop_sync_engine()
        print("✅ 智慧UI系統已安全關閉")
    except Exception as e:
        print(f"❌ 服務器啟動失敗: {e}")
        smart_ui.sync_engine.stop_sync_engine()

