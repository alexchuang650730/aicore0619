# PowerAutomation v0.57 雙倉庫架構設計

## 🏗️ 倉庫架構概覽

### **主源碼倉庫** 
**倉庫**: https://github.com/alexchuang650730/powerauto.ai_0.53
**職責**: 核心業務邏輯和後端服務

#### 包含組件
- ✅ **API Gateway**: 統一數據同步服務
- ✅ **雲側Admin**: 企業版和個人專業版管理界面
- ✅ **端側Admin**: VS Code插件
- ✅ **工作流引擎**: 六節點工作流系統
- ✅ **數據同步服務**: WebSocket實時通信
- ✅ **後端API**: 用戶認證、積分管理、權限控制
- ✅ **數據庫模型**: B端企業數據庫設計

### **C端用戶Web倉庫**
**倉庫**: https://github.com/alexchuang650730/powerauto.aiweb.git
**職責**: C端用戶入口和前端體驗
**域名**: powerauto.ai

#### 包含組件
- ✅ **用戶註冊登錄**: 身份認證界面
- ✅ **積分管理**: 用戶積分查看、購買
- ✅ **支付系統**: 訂閱升級、試用
- ✅ **版本選擇**: 個人專業版 vs 企業版
- ✅ **下載中心**: VS Code插件、CLI工具下載
- ✅ **用戶儀表板**: 個人使用統計
- ✅ **C端數據庫**: 個人用戶數據隔離

---

## 🔄 雙倉庫協調機制

### **API接口標準化**

#### **主倉庫提供的API服務**
```javascript
// 用戶認證API
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/profile

// 積分管理API
GET  /api/credits/balance
POST /api/credits/purchase
POST /api/credits/consume

// 數據同步API
WebSocket /ws/sync/credits
WebSocket /ws/sync/status
```

#### **C端Web調用的API**
```javascript
// C端Web前端調用主倉庫API
const API_BASE = 'https://api.powerauto.ai';

// 獲取用戶積分
const getCredits = async () => {
  const response = await fetch(`${API_BASE}/api/credits/balance`);
  return response.json();
};

// WebSocket實時同步
const ws = new WebSocket(`wss://api.powerauto.ai/ws/sync/credits`);
```

### **數據流架構**

```
C端用戶Web (powerauto.ai)
    ↕️ HTTPS API調用
API Gateway (主倉庫)
    ↕️ WebSocket實時同步
雲側Admin (主倉庫)
    ↕️ WebSocket長連接
端側Admin VS Code插件 (主倉庫)
```

### **部署策略**

#### **主倉庫部署**
- **API服務**: api.powerauto.ai
- **雲側Admin**: admin.powerauto.ai
- **WebSocket服務**: ws.powerauto.ai

#### **C端Web倉庫部署**
- **用戶入口**: powerauto.ai
- **Amazon服務器**: 獨立部署
- **DNS配置**: 指向Amazon服務器

---

## 🔒 數據庫隔離設計

### **C端數據庫** (C端Web倉庫管理)
```sql
-- 用戶基本信息
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP
);

-- 積分記錄
CREATE TABLE credits (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    amount INTEGER,
    transaction_type VARCHAR(50),
    created_at TIMESTAMP
);
```

### **B端數據庫** (主倉庫管理)
```sql
-- 企業用戶
CREATE TABLE enterprise_users (
    id UUID PRIMARY KEY,
    company_id UUID,
    role VARCHAR(50),
    permissions JSON,
    created_at TIMESTAMP
);

-- 企業配置
CREATE TABLE enterprise_configs (
    id UUID PRIMARY KEY,
    company_id UUID,
    ui_config JSON,
    workflow_config JSON,
    created_at TIMESTAMP
);
```

---

## 🚀 實施順序

### **Phase 1: 主倉庫API Gateway**
1. 實現統一API Gateway
2. 設計WebSocket實時同步
3. 建立數據同步服務

### **Phase 2: C端Web倉庫更新**
1. 更新C端用戶界面
2. 整合API調用
3. 實現實時積分同步

### **Phase 3: 雲側Admin增強**
1. 多版本用戶支持
2. 實時數據同步
3. 一鍵修改端側UI功能

### **Phase 4: 端側Admin完善**
1. VS Code插件更新
2. 實時積分顯示
3. 多版本UI適配

### **Phase 5: 測試與部署**
1. 雙倉庫協調測試
2. 數據同步測試
3. 端到端功能測試

---

**文檔版本**: v0.57  
**創建日期**: 2025-01-06  
**維護者**: PowerAutomation架構團隊

