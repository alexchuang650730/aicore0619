"""
智慧UI用戶管理器
管理用戶積分、權限、版本和基本信息
支持PowerAuto.ai員工對用戶的完整管理
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class User:
    """用戶數據模型"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    role: str = "user"  # 'user', 'admin', 'employee'
    credits: int = 0
    version: str = "free"  # 'free', 'professional', 'enterprise'
    status: str = "active"  # 'active', 'inactive', 'suspended'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None

@dataclass
class UserPermissions:
    """用戶權限模型"""
    max_nodes: int = 3
    max_projects: int = 5
    max_workflows: int = 10
    api_calls_per_day: int = 100
    storage_limit_mb: int = 100
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

class UserManager:
    """智慧UI用戶管理器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.sync_engine = None  # 將在初始化時設置
        
        # 版本權限配置
        self.version_permissions = {
            "free": UserPermissions(
                max_nodes=3,
                max_projects=3,
                max_workflows=5,
                api_calls_per_day=50,
                storage_limit_mb=50,
                features=["basic_coding", "basic_testing"]
            ),
            "professional": UserPermissions(
                max_nodes=6,
                max_projects=20,
                max_workflows=50,
                api_calls_per_day=1000,
                storage_limit_mb=1000,
                features=["advanced_coding", "deployment", "testing", "ai_assistant"]
            ),
            "enterprise": UserPermissions(
                max_nodes=-1,  # 無限制
                max_projects=-1,
                max_workflows=-1,
                api_calls_per_day=10000,
                storage_limit_mb=10000,
                features=["all_features", "team_collaboration", "custom_templates"]
            )
        }
    
    def set_sync_engine(self, sync_engine):
        """設置同步引擎"""
        self.sync_engine = sync_engine
    
    def create_user(self, username: str, email: str, password: str, 
                   role: str = "user", version: str = "free") -> Optional[User]:
        """創建新用戶"""
        try:
            # 檢查用戶名和郵箱是否已存在
            if self.get_user_by_username(username):
                logger.error(f"用戶名 {username} 已存在")
                return None
            
            if self.get_user_by_email(email):
                logger.error(f"郵箱 {email} 已存在")
                return None
            
            # 創建用戶
            password_hash = self._hash_password(password)
            now = datetime.now()
            
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, credits, version, status, created_at, updated_at, last_sync)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, role, 0, version, "active", now, now, now))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # 創建用戶對象
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                credits=0,
                version=version,
                status="active",
                created_at=now,
                updated_at=now,
                last_sync=now
            )
            
            # 添加到同步隊列
            if self.sync_engine:
                self.sync_engine.add_sync_record(
                    "users", user_id, "insert", self._user_to_dict(user)
                )
            
            logger.info(f"用戶創建成功: {username} ({email})")
            return user
            
        except Exception as e:
            logger.error(f"創建用戶失敗: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根據ID獲取用戶"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"獲取用戶失敗: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根據用戶名獲取用戶"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"獲取用戶失敗: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根據郵箱獲取用戶"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"獲取用戶失敗: {e}")
            return None
    
    def update_user_credits(self, user_id: int, credits: int) -> bool:
        """更新用戶積分"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                UPDATE users 
                SET credits = ?, updated_at = ?, last_sync = ?
                WHERE id = ?
            """, (credits, now, now, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                
                # 添加到同步隊列
                if self.sync_engine:
                    self.sync_engine.add_sync_record(
                        "users", user_id, "update", 
                        {"credits": credits, "updated_at": now, "last_sync": now}
                    )
                
                logger.info(f"用戶 {user_id} 積分更新為 {credits}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"更新用戶積分失敗: {e}")
            return False
    
    def add_user_credits(self, user_id: int, amount: int) -> bool:
        """增加用戶積分"""
        user = self.get_user_by_id(user_id)
        if user:
            new_credits = user.credits + amount
            return self.update_user_credits(user_id, new_credits)
        return False
    
    def deduct_user_credits(self, user_id: int, amount: int) -> bool:
        """扣除用戶積分"""
        user = self.get_user_by_id(user_id)
        if user and user.credits >= amount:
            new_credits = user.credits - amount
            return self.update_user_credits(user_id, new_credits)
        return False
    
    def update_user_version(self, user_id: int, version: str) -> bool:
        """更新用戶版本"""
        if version not in self.version_permissions:
            logger.error(f"無效的版本: {version}")
            return False
        
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                UPDATE users 
                SET version = ?, updated_at = ?, last_sync = ?
                WHERE id = ?
            """, (version, now, now, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                
                # 添加到同步隊列
                if self.sync_engine:
                    self.sync_engine.add_sync_record(
                        "users", user_id, "update",
                        {"version": version, "updated_at": now, "last_sync": now}
                    )
                
                logger.info(f"用戶 {user_id} 版本更新為 {version}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"更新用戶版本失敗: {e}")
            return False
    
    def update_user_status(self, user_id: int, status: str) -> bool:
        """更新用戶狀態"""
        valid_statuses = ["active", "inactive", "suspended"]
        if status not in valid_statuses:
            logger.error(f"無效的狀態: {status}")
            return False
        
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            cursor.execute("""
                UPDATE users 
                SET status = ?, updated_at = ?, last_sync = ?
                WHERE id = ?
            """, (status, now, now, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                
                # 添加到同步隊列
                if self.sync_engine:
                    self.sync_engine.add_sync_record(
                        "users", user_id, "update",
                        {"status": status, "updated_at": now, "last_sync": now}
                    )
                
                logger.info(f"用戶 {user_id} 狀態更新為 {status}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"更新用戶狀態失敗: {e}")
            return False
    
    def get_user_permissions(self, user_id: int) -> Optional[UserPermissions]:
        """獲取用戶權限"""
        user = self.get_user_by_id(user_id)
        if user:
            return self.version_permissions.get(user.version)
        return None
    
    def check_user_permission(self, user_id: int, feature: str) -> bool:
        """檢查用戶是否有特定功能權限"""
        permissions = self.get_user_permissions(user_id)
        if permissions:
            return feature in permissions.features or "all_features" in permissions.features
        return False
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """獲取所有用戶列表"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM users 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            return [self._row_to_user(row) for row in rows]
            
        except Exception as e:
            logger.error(f"獲取用戶列表失敗: {e}")
            return []
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """獲取用戶統計信息"""
        try:
            conn = self.db_manager.get_local_connection()
            cursor = conn.cursor()
            
            # 總用戶數
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            # 按版本統計
            cursor.execute("""
                SELECT version, COUNT(*) as count
                FROM users
                GROUP BY version
            """)
            version_stats = dict(cursor.fetchall())
            
            # 按狀態統計
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM users
                GROUP BY status
            """)
            status_stats = dict(cursor.fetchall())
            
            # 積分統計
            cursor.execute("""
                SELECT 
                    SUM(credits) as total_credits,
                    AVG(credits) as avg_credits,
                    MAX(credits) as max_credits
                FROM users
            """)
            credits_stats = cursor.fetchone()
            
            return {
                "total_users": total_users,
                "version_distribution": version_stats,
                "status_distribution": status_stats,
                "credits_statistics": {
                    "total": credits_stats[0] or 0,
                    "average": credits_stats[1] or 0,
                    "maximum": credits_stats[2] or 0
                }
            }
            
        except Exception as e:
            logger.error(f"獲取用戶統計失敗: {e}")
            return {}
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用戶認證"""
        user = self.get_user_by_username(username)
        if user and self._verify_password(password, user.password_hash):
            if user.status == "active":
                return user
            else:
                logger.warning(f"用戶 {username} 狀態為 {user.status}，無法登錄")
        return None
    
    def _hash_password(self, password: str) -> str:
        """密碼哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """驗證密碼"""
        return self._hash_password(password) == password_hash
    
    def _row_to_user(self, row) -> User:
        """數據庫行轉用戶對象"""
        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            role=row['role'],
            credits=row['credits'],
            version=row['version'],
            status=row['status'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
            last_sync=datetime.fromisoformat(row['last_sync']) if row['last_sync'] else None
        )
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """用戶對象轉字典"""
        return {
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "role": user.role,
            "credits": user.credits,
            "version": user.version,
            "status": user.status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_sync": user.last_sync.isoformat() if user.last_sync else None
        }

