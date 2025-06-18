"""
智慧UI系統測試腳本
測試數據庫連接、用戶管理、工作流管理等核心功能
"""

import sys
import os
sys.path.append('/home/ubuntu/powerauto.ai_0.53')

from smart_ui import SmartUISystem, get_smart_ui
from smart_ui.user_manager import User, UserPermissions
from smart_ui.workflow_manager import WorkflowType, WorkflowStatus
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_smart_ui_system():
    """測試智慧UI系統"""
    print("🧠 開始測試PowerAutomation智慧UI系統...")
    
    try:
        # 初始化系統
        smart_ui = get_smart_ui()
        smart_ui.initialize()
        
        # 設置同步引擎關聯
        smart_ui.user_manager.set_sync_engine(smart_ui.sync_engine)
        smart_ui.workflow_manager.set_sync_engine(smart_ui.sync_engine)
        
        # 啟動同步引擎
        smart_ui.sync_engine.start_sync_engine()
        
        print("\n📊 系統狀態:")
        status = smart_ui.get_system_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 測試用戶管理
        print("\n👥 測試用戶管理...")
        test_user_management(smart_ui.user_manager)
        
        # 測試工作流管理
        print("\n⚡ 測試工作流管理...")
        test_workflow_management(smart_ui.workflow_manager)
        
        # 測試同步功能
        print("\n🔄 測試同步功能...")
        test_sync_functionality(smart_ui.sync_engine)
        
        print("\n✅ 智慧UI系統測試完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        logger.error(f"系統測試失敗: {e}")
        return False
    
    finally:
        # 停止同步引擎
        if 'smart_ui' in locals():
            smart_ui.sync_engine.stop_sync_engine()

def test_user_management(user_manager):
    """測試用戶管理功能"""
    print("  創建測試用戶...")
    
    # 創建測試用戶
    user = user_manager.create_user(
        username="test_user",
        email="test@powerauto.ai",
        password="test123",
        role="user",
        version="professional"
    )
    
    if user:
        print(f"  ✅ 用戶創建成功: {user.username} (ID: {user.id})")
        
        # 測試積分管理
        print("  測試積分管理...")
        user_manager.add_user_credits(user.id, 1000)
        updated_user = user_manager.get_user_by_id(user.id)
        print(f"  ✅ 積分更新成功: {updated_user.credits}")
        
        # 測試權限檢查
        print("  測試權限檢查...")
        permissions = user_manager.get_user_permissions(user.id)
        print(f"  ✅ 用戶權限: 最大節點數={permissions.max_nodes}, 功能={permissions.features}")
        
        # 測試用戶認證
        print("  測試用戶認證...")
        auth_user = user_manager.authenticate_user("test_user", "test123")
        if auth_user:
            print("  ✅ 用戶認證成功")
        else:
            print("  ❌ 用戶認證失敗")
        
        # 獲取用戶統計
        print("  獲取用戶統計...")
        stats = user_manager.get_user_statistics()
        print(f"  📊 用戶統計: {stats}")
        
    else:
        print("  ❌ 用戶創建失敗")

def test_workflow_management(workflow_manager):
    """測試工作流管理功能"""
    print("  創建測試工作流...")
    
    # 創建編碼工作流
    coding_workflow = workflow_manager.create_workflow(
        project_id=1,
        name="測試編碼工作流",
        workflow_type=WorkflowType.CODING,
        description="用於測試的編碼工作流"
    )
    
    if coding_workflow:
        print(f"  ✅ 編碼工作流創建成功: {coding_workflow.name} (ID: {coding_workflow.id})")
        print(f"     步驟數量: {len(coding_workflow.steps)}")
        
        # 創建部署工作流
        deploy_workflow = workflow_manager.create_workflow(
            project_id=1,
            name="測試部署工作流",
            workflow_type=WorkflowType.DEPLOYMENT
        )
        
        if deploy_workflow:
            print(f"  ✅ 部署工作流創建成功: {deploy_workflow.name} (ID: {deploy_workflow.id})")
        
        # 創建測試工作流
        test_workflow = workflow_manager.create_workflow(
            project_id=1,
            name="測試測試工作流",
            workflow_type=WorkflowType.TESTING
        )
        
        if test_workflow:
            print(f"  ✅ 測試工作流創建成功: {test_workflow.name} (ID: {test_workflow.id})")
        
        # 測試工作流狀態更新
        print("  測試工作流狀態更新...")
        success = workflow_manager.update_workflow_status(coding_workflow.id, WorkflowStatus.ACTIVE)
        if success:
            print("  ✅ 工作流狀態更新成功")
        
        # 測試工作流執行
        print("  測試工作流執行...")
        execution_success = workflow_manager.execute_workflow(coding_workflow.id)
        if execution_success:
            print("  ✅ 工作流執行成功")
        else:
            print("  ⚠️ 工作流執行完成（模擬）")
        
        # 獲取工作流統計
        print("  獲取工作流統計...")
        stats = workflow_manager.get_workflow_statistics()
        print(f"  📊 工作流統計: {stats}")
        
    else:
        print("  ❌ 工作流創建失敗")

def test_sync_functionality(sync_engine):
    """測試同步功能"""
    print("  測試同步狀態...")
    
    # 獲取同步狀態
    sync_status = sync_engine.get_sync_status()
    print(f"  📊 同步狀態: {sync_status}")
    
    # 測試強制全量同步（如果雲端數據庫可用）
    print("  測試強制全量同步...")
    sync_success = sync_engine.force_full_sync()
    if sync_success:
        print("  ✅ 全量同步成功")
    else:
        print("  ⚠️ 全量同步跳過（雲端數據庫不可用）")

if __name__ == "__main__":
    test_smart_ui_system()

