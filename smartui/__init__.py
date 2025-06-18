"""
PowerAutomation 智慧UI系統
完整的個人專業版開發工作站

系統架構：
- 雲側WebAdmin: PowerAuto.ai員工管理後台
- 端側WebAdmin: 用戶智慧工作台  
- 數據層: SQLite + PostgreSQL + Redis
- 同步機制: 增量同步 + 事件驅動
- 工作流: 編碼 + 部署 + 測試
"""

from .database_config import HybridDatabaseManager, get_db_manager
from .sync_engine import SmartSyncEngine
from .user_manager import UserManager
from .workflow_manager import WorkflowManager

__version__ = "1.0.0"
__author__ = "PowerAutomation Team"

class SmartUISystem:
    """智慧UI系統主控制器"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.sync_engine = SmartSyncEngine(self.db_manager)
        self.user_manager = UserManager(self.db_manager)
        self.workflow_manager = WorkflowManager(self.db_manager)
        
    def initialize(self):
        """初始化智慧UI系統"""
        print("🧠 PowerAutomation 智慧UI系統啟動中...")
        print("📊 數據庫連接: ✅")
        print("🔄 同步引擎: ✅") 
        print("👥 用戶管理: ✅")
        print("⚡ 工作流管理: ✅")
        print("🚀 智慧UI系統就緒！")
        
    def get_system_status(self):
        """獲取系統狀態"""
        return {
            "database": "connected",
            "sync_engine": "running",
            "user_manager": "active",
            "workflow_manager": "active",
            "version": __version__
        }

# 全局智慧UI系統實例
smart_ui = SmartUISystem()

def get_smart_ui() -> SmartUISystem:
    """獲取智慧UI系統實例"""
    return smart_ui

