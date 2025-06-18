# PowerAutomation 智慧UI系統

## 🧠 系統概述

PowerAutomation智慧UI系統是一個完整的個人專業版開發工作站，整合了編碼、部署、測試三大工作流，提供智能化的用戶界面和強大的後端支持。

## ✨ 核心特色

### 🎯 **三大工作流整合**
- **編碼工作流**: AI輔助代碼生成、智能審查、自動重構
- **部署工作流**: CI/CD自動化、多環境部署、回滾機制
- **測試工作流**: 單元測試、集成測試、性能測試、安全測試

### 🏗️ **混合架構設計**
- **本地SQLite**: 用戶配置、項目數據、實時緩存
- **雲端PostgreSQL**: 數據持久化、團隊協作、備份
- **Redis緩存**: 查詢緩存、會話存儲、消息隊列

### 🔄 **智能同步機制**
- **增量同步**: 只同步變更數據，提高效率
- **事件驅動**: 實時響應數據變化
- **衝突解決**: 智能合併策略，避免數據衝突

### 🎨 **現代化UI設計**
- **白底藍色**: 統一的設計語言
- **響應式布局**: 完美支持桌面和移動端
- **流暢動畫**: 現代化的交互體驗

## 📁 項目結構

```
smart_ui/
├── __init__.py                 # 智慧UI系統主控制器
├── database_config.py          # 混合數據庫配置
├── sync_engine.py             # 基礎同步引擎
├── advanced_sync_engine.py    # 高級同步引擎
├── user_manager.py            # 用戶管理器
├── workflow_manager.py        # 工作流管理器
├── api_server.py              # Flask API服務器
├── test_smart_ui.py           # 系統測試腳本
└── frontend/
    └── client_webadmin.html   # 端側WebAdmin界面
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip3 install psycopg2-binary redis async_timeout flask flask-cors
```

### 2. 啟動系統

```bash
cd /home/ubuntu/powerauto.ai_0.53
python3 smart_ui/api_server.py
```

### 3. 訪問界面

打開瀏覽器訪問: `http://localhost:5000`

## 🔧 系統配置

### 數據庫配置

```python
from smart_ui.database_config import DatabaseConfig

config = DatabaseConfig(
    # SQLite本地數據庫
    sqlite_path="powerautomation.db",
    
    # PostgreSQL雲端數據庫
    postgres_host="localhost",
    postgres_port=5432,
    postgres_db="powerautomation",
    postgres_user="postgres",
    postgres_password="password",
    
    # Redis緩存
    redis_host="localhost",
    redis_port=6379,
    redis_db=0
)
```

### 同步配置

```python
from smart_ui.advanced_sync_engine import SyncConfig, SyncStrategy

sync_config = SyncConfig(
    strategy=SyncStrategy.REAL_TIME,
    batch_size=50,
    sync_interval=10,
    max_retries=3
)
```

## 📊 API接口

### 系統狀態
- `GET /api/status` - 獲取系統狀態
- `GET /api/dashboard` - 獲取儀表板數據

### 工作流管理
- `GET /api/workflows` - 獲取工作流列表
- `POST /api/workflows` - 創建新工作流
- `POST /api/workflows/{id}/execute` - 執行工作流

### 用戶管理
- `GET /api/users` - 獲取用戶列表
- `POST /api/users` - 創建新用戶
- `PUT /api/users/{id}/credits` - 更新用戶積分

### 同步管理
- `GET /api/sync/status` - 獲取同步狀態
- `POST /api/sync/force` - 強制全量同步

## 🧪 系統測試

運行完整的系統測試:

```bash
python3 smart_ui/test_smart_ui.py
```

測試包括:
- 數據庫連接測試
- 用戶管理功能測試
- 工作流管理功能測試
- 同步引擎功能測試

## 🎯 功能特色

### 智能用戶管理
- **版本權限控制**: 免費版、專業版、企業版
- **積分系統**: 靈活的積分管理和消費
- **權限映射**: 根據版本自動分配功能權限

### 工作流引擎
- **可視化編輯**: 拖拽式工作流設計
- **模板系統**: 預定義的工作流模板
- **智能執行**: 依賴關係和錯誤處理

### 數據同步
- **實時同步**: 數據變更即時同步
- **批量處理**: 高效的批量同步機制
- **衝突解決**: 多種衝突解決策略

## 🔐 安全特性

- **密碼哈希**: SHA-256密碼加密
- **會話管理**: 安全的用戶會話
- **權限控制**: 細粒度的功能權限
- **數據驗證**: 完整的輸入驗證

## 📈 性能優化

- **連接池**: 數據庫連接池管理
- **緩存策略**: Redis緩存加速
- **異步處理**: 非阻塞的同步操作
- **批量操作**: 減少數據庫訪問次數

## 🌟 未來規劃

### Phase 4: 雲側WebAdmin管理後台
- PowerAuto.ai員工管理界面
- 用戶積分和權限管理
- 系統監控和統計

### Phase 5: 高級功能
- AI驅動的個性化界面
- 智能學習助手
- 跨平台協作增強

### Phase 6: 企業級擴展
- 多租戶支持
- 企業級安全
- 高可用部署

## 🤝 貢獻指南

1. Fork 項目
2. 創建功能分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request

## 📄 許可證

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情

## 📞 聯繫我們

- 項目主頁: https://powerauto.ai
- 問題反饋: https://github.com/alexchuang650730/powerauto.ai_0.53/issues
- 郵箱: support@powerauto.ai

---

**PowerAutomation 智慧UI系統 - 讓開發更智能，讓工作更高效！** 🚀

