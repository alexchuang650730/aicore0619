#!/usr/bin/env python3
"""
PowerAutomation 企業級架構實現

提供完整的企業級雲服務架構，包括Web控制台、認證服務、計費系統等
"""

import os
import sys
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import jwt
import bcrypt
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加共享核心路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_core'))

from shared_core import get_shared_core, initialize_shared_core
from shared_core.config.unified_config import get_config_manager

logger = logging.getLogger(__name__)

@dataclass
class User:
    """用戶數據模型"""
    id: str
    email: str
    name: str
    role: str
    organization_id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True

@dataclass
class Organization:
    """組織數據模型"""
    id: str
    name: str
    plan: str  # basic, professional, enterprise
    max_users: int
    created_at: datetime
    is_active: bool = True

class AuthService:
    """企業級認證服務"""
    
    def __init__(self, jwt_secret: str, jwt_expiration_hours: int = 8):
        self.jwt_secret = jwt_secret
        self.jwt_expiration_hours = jwt_expiration_hours
        self.users: Dict[str, User] = {}
        self.organizations: Dict[str, Organization] = {}
        
        # 初始化示例數據
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """初始化示例數據"""
        # 創建示例組織
        org = Organization(
            id="org_001",
            name="示例企業",
            plan="enterprise",
            max_users=100,
            created_at=datetime.now()
        )
        self.organizations[org.id] = org
        
        # 創建示例用戶
        user = User(
            id="user_001",
            email="admin@example.com",
            name="管理員",
            role="admin",
            organization_id=org.id,
            created_at=datetime.now()
        )
        self.users[user.id] = user
    
    def hash_password(self, password: str) -> str:
        """密碼哈希"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """驗證密碼"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user_id: str) -> str:
        """創建訪問令牌"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[str]:
        """驗證令牌"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """用戶認證"""
        # 簡化實現：實際應該從數據庫查詢
        for user in self.users.values():
            if user.email == email and user.is_active:
                # 實際應該驗證密碼哈希
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根據ID獲取用戶"""
        return self.users.get(user_id)

class BillingService:
    """企業級計費服務"""
    
    def __init__(self):
        self.usage_records: Dict[str, List[Dict]] = {}
        self.billing_plans = {
            "basic": {"price_per_user": 10, "max_api_calls": 1000},
            "professional": {"price_per_user": 25, "max_api_calls": 5000},
            "enterprise": {"price_per_user": 50, "max_api_calls": -1}  # unlimited
        }
    
    def record_usage(self, organization_id: str, user_id: str, action: str, cost: float = 0.0):
        """記錄使用情況"""
        if organization_id not in self.usage_records:
            self.usage_records[organization_id] = []
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "cost": cost
        }
        self.usage_records[organization_id].append(record)
    
    def get_monthly_usage(self, organization_id: str, year: int, month: int) -> Dict[str, Any]:
        """獲取月度使用情況"""
        records = self.usage_records.get(organization_id, [])
        
        # 過濾當月記錄
        monthly_records = [
            record for record in records
            if datetime.fromisoformat(record["timestamp"]).year == year
            and datetime.fromisoformat(record["timestamp"]).month == month
        ]
        
        total_cost = sum(record["cost"] for record in monthly_records)
        total_actions = len(monthly_records)
        
        return {
            "organization_id": organization_id,
            "year": year,
            "month": month,
            "total_cost": total_cost,
            "total_actions": total_actions,
            "records": monthly_records
        }
    
    def calculate_monthly_bill(self, organization_id: str, year: int, month: int) -> Dict[str, Any]:
        """計算月度賬單"""
        # 簡化實現
        usage = self.get_monthly_usage(organization_id, year, month)
        
        # 假設基礎費用
        base_cost = 100.0
        usage_cost = usage["total_cost"]
        total_cost = base_cost + usage_cost
        
        return {
            "organization_id": organization_id,
            "billing_period": f"{year}-{month:02d}",
            "base_cost": base_cost,
            "usage_cost": usage_cost,
            "total_cost": total_cost,
            "due_date": datetime(year, month, 28).isoformat()
        }

class EnterpriseServer:
    """企業級服務器"""
    
    def __init__(self):
        self.app = FastAPI(
            title="PowerAutomation Enterprise API",
            description="企業級自動化平台API",
            version="0.5.3"
        )
        
        # 獲取企業級配置
        config_manager = get_config_manager()
        self.config = config_manager.get_all_config("enterprise")
        
        # 初始化服務
        self.auth_service = AuthService(
            jwt_secret=self.config["security"].jwt_secret_key or "enterprise_secret_key",
            jwt_expiration_hours=self.config["security"].jwt_expiration_hours
        )
        self.billing_service = BillingService()
        
        # 配置中間件
        self._setup_middleware()
        
        # 配置路由
        self._setup_routes()
        
        # 初始化共享核心
        self.shared_core = None
    
    def _setup_middleware(self):
        """設置中間件"""
        # CORS中間件
        if self.config["server"].cors_enabled:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config["server"].cors_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
    
    def _setup_routes(self):
        """設置路由"""
        security = HTTPBearer()
        
        @self.app.get("/")
        async def root():
            return {
                "message": "PowerAutomation Enterprise API",
                "version": "0.5.3",
                "architecture": "enterprise"
            }
        
        @self.app.post("/auth/login")
        async def login(credentials: Dict[str, str]):
            email = credentials.get("email")
            password = credentials.get("password")
            
            if not email or not password:
                raise HTTPException(status_code=400, detail="郵箱和密碼不能為空")
            
            user = self.auth_service.authenticate_user(email, password)
            if not user:
                raise HTTPException(status_code=401, detail="認證失敗")
            
            token = self.auth_service.create_access_token(user.id)
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }
            }
        
        @self.app.get("/auth/me")
        async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
            user_id = self.auth_service.verify_token(credentials.credentials)
            if not user_id:
                raise HTTPException(status_code=401, detail="無效的令牌")
            
            user = self.auth_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="用戶不存在")
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "organization_id": user.organization_id
            }
        
        @self.app.get("/billing/usage/{organization_id}")
        async def get_usage(
            organization_id: str,
            year: int,
            month: int,
            credentials: HTTPAuthorizationCredentials = Security(security)
        ):
            # 驗證用戶權限
            user_id = self.auth_service.verify_token(credentials.credentials)
            if not user_id:
                raise HTTPException(status_code=401, detail="無效的令牌")
            
            usage = self.billing_service.get_monthly_usage(organization_id, year, month)
            return usage
        
        @self.app.get("/billing/bill/{organization_id}")
        async def get_bill(
            organization_id: str,
            year: int,
            month: int,
            credentials: HTTPAuthorizationCredentials = Security(security)
        ):
            # 驗證用戶權限
            user_id = self.auth_service.verify_token(credentials.credentials)
            if not user_id:
                raise HTTPException(status_code=401, detail="無效的令牌")
            
            bill = self.billing_service.calculate_monthly_bill(organization_id, year, month)
            return bill
        
        @self.app.get("/health")
        async def health_check():
            health_status = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            
            if self.shared_core:
                core_health = await self.shared_core.health_check_all()
                health_status["shared_core"] = core_health
            
            return health_status
        
        @self.app.post("/automation/execute")
        async def execute_automation(
            request: Dict[str, Any],
            credentials: HTTPAuthorizationCredentials = Security(security)
        ):
            # 驗證用戶權限
            user_id = self.auth_service.verify_token(credentials.credentials)
            if not user_id:
                raise HTTPException(status_code=401, detail="無效的令牌")
            
            user = self.auth_service.get_user_by_id(user_id)
            
            # 記錄使用情況
            self.billing_service.record_usage(
                user.organization_id,
                user_id,
                "automation_execution",
                0.1  # 每次執行0.1美元
            )
            
            # 執行自動化任務（簡化實現）
            return {
                "task_id": f"task_{datetime.now().timestamp()}",
                "status": "submitted",
                "message": "自動化任務已提交執行"
            }
    
    async def start(self):
        """啟動企業級服務器"""
        try:
            # 初始化共享核心
            self.shared_core = initialize_shared_core("enterprise")
            await self.shared_core.start_all_components()
            
            logger.info("企業級服務器啟動成功")
            
            # 啟動FastAPI服務器
            config = uvicorn.Config(
                self.app,
                host=self.config["server"].host,
                port=self.config["server"].port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"企業級服務器啟動失敗: {e}")
            raise
    
    async def stop(self):
        """停止企業級服務器"""
        if self.shared_core:
            await self.shared_core.stop_all_components()
        logger.info("企業級服務器已停止")

async def main():
    """主函數"""
    print("🚀 PowerAutomation 企業級架構啟動")
    
    try:
        server = EnterpriseServer()
        await server.start()
    except KeyboardInterrupt:
        print("\n⏹️ 服務器停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())

