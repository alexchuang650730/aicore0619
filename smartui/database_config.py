"""
PowerAutomation 混合架構數據庫配置
支持本地SQLite + 雲端PostgreSQL + Redis緩存的混合架構
"""

import os
import sqlite3
import psycopg2
import redis
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """數據庫配置類"""
    # SQLite本地數據庫配置
    sqlite_path: str = "powerautomation.db"
    
    # PostgreSQL雲端數據庫配置
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "powerautomation"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    
    # Redis緩存配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 同步配置
    sync_interval: int = 30  # 同步間隔（秒）
    batch_size: int = 100    # 批量同步大小
    max_retries: int = 3     # 最大重試次數

class HybridDatabaseManager:
    """混合數據庫管理器"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.sqlite_conn = None
        self.postgres_conn = None
        self.redis_conn = None
        self._initialize_connections()
        self._setup_tables()
    
    def _initialize_connections(self):
        """初始化數據庫連接"""
        try:
            # 初始化SQLite連接
            self.sqlite_conn = sqlite3.connect(
                self.config.sqlite_path,
                check_same_thread=False
            )
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info("SQLite連接初始化成功")
            
            # 初始化PostgreSQL連接（如果配置可用）
            try:
                self.postgres_conn = psycopg2.connect(
                    host=self.config.postgres_host,
                    port=self.config.postgres_port,
                    database=self.config.postgres_db,
                    user=self.config.postgres_user,
                    password=self.config.postgres_password
                )
                logger.info("PostgreSQL連接初始化成功")
            except Exception as e:
                logger.warning(f"PostgreSQL連接失敗，將使用本地模式: {e}")
            
            # 初始化Redis連接（如果配置可用）
            try:
                self.redis_conn = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    db=self.config.redis_db,
                    password=self.config.redis_password,
                    decode_responses=True
                )
                # 測試連接
                self.redis_conn.ping()
                logger.info("Redis連接初始化成功")
            except Exception as e:
                logger.warning(f"Redis連接失敗，將不使用緩存: {e}")
                self.redis_conn = None
                
        except Exception as e:
            logger.error(f"數據庫連接初始化失敗: {e}")
            raise
    
    def _setup_tables(self):
        """設置數據庫表結構"""
        # SQLite表結構
        sqlite_tables = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    credits INTEGER DEFAULT 0,
                    version VARCHAR(20) DEFAULT 'free',
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'projects': '''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    config JSON,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''',
            'workflows': '''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    config JSON,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            ''',
            'sync_log': '''
                CREATE TABLE IF NOT EXISTS sync_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name VARCHAR(50) NOT NULL,
                    record_id INTEGER NOT NULL,
                    action VARCHAR(20) NOT NULL,
                    data JSON,
                    sync_status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    synced_at TIMESTAMP
                )
            '''
        }
        
        # 創建SQLite表
        cursor = self.sqlite_conn.cursor()
        for table_name, sql in sqlite_tables.items():
            cursor.execute(sql)
            logger.info(f"SQLite表 {table_name} 創建成功")
        self.sqlite_conn.commit()
        
        # 如果PostgreSQL可用，創建相同的表結構
        if self.postgres_conn:
            postgres_tables = {
                'users': '''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) DEFAULT 'user',
                        credits INTEGER DEFAULT 0,
                        version VARCHAR(20) DEFAULT 'free',
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''',
                'projects': '''
                    CREATE TABLE IF NOT EXISTS projects (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        config JSONB,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''',
                'workflows': '''
                    CREATE TABLE IF NOT EXISTS workflows (
                        id SERIAL PRIMARY KEY,
                        project_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        config JSONB,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects (id)
                    )
                ''',
                'sync_log': '''
                    CREATE TABLE IF NOT EXISTS sync_log (
                        id SERIAL PRIMARY KEY,
                        table_name VARCHAR(50) NOT NULL,
                        record_id INTEGER NOT NULL,
                        action VARCHAR(20) NOT NULL,
                        data JSONB,
                        sync_status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        synced_at TIMESTAMP
                    )
                '''
            }
            
            cursor = self.postgres_conn.cursor()
            for table_name, sql in postgres_tables.items():
                cursor.execute(sql)
                logger.info(f"PostgreSQL表 {table_name} 創建成功")
            self.postgres_conn.commit()
    
    def get_local_connection(self):
        """獲取本地SQLite連接"""
        return self.sqlite_conn
    
    def get_cloud_connection(self):
        """獲取雲端PostgreSQL連接"""
        return self.postgres_conn
    
    def get_cache_connection(self):
        """獲取Redis緩存連接"""
        return self.redis_conn
    
    def close_connections(self):
        """關閉所有數據庫連接"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
            logger.info("SQLite連接已關閉")
        
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("PostgreSQL連接已關閉")
        
        if self.redis_conn:
            self.redis_conn.close()
            logger.info("Redis連接已關閉")

# 全局數據庫管理器實例
db_manager = HybridDatabaseManager()

def get_db_manager() -> HybridDatabaseManager:
    """獲取數據庫管理器實例"""
    return db_manager

