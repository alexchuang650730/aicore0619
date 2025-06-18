"""
智慧UI數據同步引擎
實現本地SQLite與雲端PostgreSQL的智能同步
支持增量同步、事件驅動和衝突解決
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import threading

logger = logging.getLogger(__name__)

@dataclass
class SyncRecord:
    """同步記錄"""
    table_name: str
    record_id: int
    action: str  # 'insert', 'update', 'delete'
    data: Dict[str, Any]
    timestamp: datetime
    sync_status: str = 'pending'  # 'pending', 'synced', 'failed'

class SmartSyncEngine:
    """智慧同步引擎"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.sync_queue = []
        self.sync_lock = threading.Lock()
        self.is_running = False
        self.sync_thread = None
        
    def start_sync_engine(self):
        """啟動同步引擎"""
        if not self.is_running:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
            self.sync_thread.start()
            logger.info("智慧同步引擎已啟動")
    
    def stop_sync_engine(self):
        """停止同步引擎"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join()
        logger.info("智慧同步引擎已停止")
    
    def add_sync_record(self, table_name: str, record_id: int, action: str, data: Dict[str, Any]):
        """添加同步記錄"""
        sync_record = SyncRecord(
            table_name=table_name,
            record_id=record_id,
            action=action,
            data=data,
            timestamp=datetime.now()
        )
        
        with self.sync_lock:
            self.sync_queue.append(sync_record)
            
        # 記錄到本地同步日誌
        self._log_sync_record(sync_record)
        logger.info(f"添加同步記錄: {table_name}.{record_id} ({action})")
    
    def _log_sync_record(self, record: SyncRecord):
        """記錄同步日誌到本地數據庫"""
        conn = self.db_manager.get_local_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sync_log (table_name, record_id, action, data, sync_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            record.table_name,
            record.record_id,
            record.action,
            json.dumps(record.data),
            record.sync_status,
            record.timestamp
        ))
        conn.commit()
    
    def _sync_worker(self):
        """同步工作線程"""
        while self.is_running:
            try:
                if self.sync_queue:
                    with self.sync_lock:
                        records_to_sync = self.sync_queue.copy()
                        self.sync_queue.clear()
                    
                    self._process_sync_batch(records_to_sync)
                
                time.sleep(5)  # 每5秒檢查一次
                
            except Exception as e:
                logger.error(f"同步工作線程錯誤: {e}")
                time.sleep(10)  # 錯誤時等待更長時間
    
    def _process_sync_batch(self, records: List[SyncRecord]):
        """處理同步批次"""
        if not self.db_manager.get_cloud_connection():
            logger.warning("雲端數據庫不可用，跳過同步")
            return
        
        cloud_conn = self.db_manager.get_cloud_connection()
        local_conn = self.db_manager.get_local_connection()
        
        for record in records:
            try:
                success = self._sync_single_record(record, cloud_conn, local_conn)
                
                # 更新同步狀態
                status = 'synced' if success else 'failed'
                self._update_sync_status(record, status, local_conn)
                
            except Exception as e:
                logger.error(f"同步記錄失敗 {record.table_name}.{record.record_id}: {e}")
                self._update_sync_status(record, 'failed', local_conn)
    
    def _sync_single_record(self, record: SyncRecord, cloud_conn, local_conn) -> bool:
        """同步單個記錄"""
        try:
            cursor = cloud_conn.cursor()
            
            if record.action == 'insert':
                # 插入新記錄
                columns = ', '.join(record.data.keys())
                placeholders = ', '.join(['%s'] * len(record.data))
                sql = f"INSERT INTO {record.table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(record.data.values()))
                
            elif record.action == 'update':
                # 更新記錄
                set_clause = ', '.join([f"{k} = %s" for k in record.data.keys()])
                sql = f"UPDATE {record.table_name} SET {set_clause} WHERE id = %s"
                cursor.execute(sql, list(record.data.values()) + [record.record_id])
                
            elif record.action == 'delete':
                # 刪除記錄
                sql = f"DELETE FROM {record.table_name} WHERE id = %s"
                cursor.execute(sql, [record.record_id])
            
            cloud_conn.commit()
            logger.info(f"同步成功: {record.table_name}.{record.record_id}")
            return True
            
        except Exception as e:
            cloud_conn.rollback()
            logger.error(f"同步失敗: {e}")
            return False
    
    def _update_sync_status(self, record: SyncRecord, status: str, local_conn):
        """更新同步狀態"""
        cursor = local_conn.cursor()
        cursor.execute("""
            UPDATE sync_log 
            SET sync_status = ?, synced_at = ?
            WHERE table_name = ? AND record_id = ? AND action = ? AND created_at = ?
        """, (
            status,
            datetime.now(),
            record.table_name,
            record.record_id,
            record.action,
            record.timestamp
        ))
        local_conn.commit()
    
    def force_full_sync(self):
        """強制全量同步"""
        logger.info("開始強制全量同步...")
        
        if not self.db_manager.get_cloud_connection():
            logger.error("雲端數據庫不可用，無法執行全量同步")
            return False
        
        try:
            # 同步用戶表
            self._sync_table_full('users')
            # 同步項目表
            self._sync_table_full('projects')
            # 同步工作流表
            self._sync_table_full('workflows')
            
            logger.info("全量同步完成")
            return True
            
        except Exception as e:
            logger.error(f"全量同步失敗: {e}")
            return False
    
    def _sync_table_full(self, table_name: str):
        """全量同步單個表"""
        local_conn = self.db_manager.get_local_connection()
        cloud_conn = self.db_manager.get_cloud_connection()
        
        # 獲取本地數據
        local_cursor = local_conn.cursor()
        local_cursor.execute(f"SELECT * FROM {table_name}")
        local_records = local_cursor.fetchall()
        
        # 同步到雲端
        for record in local_records:
            record_dict = dict(record)
            record_id = record_dict.pop('id')
            
            # 檢查雲端是否存在
            cloud_cursor = cloud_conn.cursor()
            cloud_cursor.execute(f"SELECT id FROM {table_name} WHERE id = %s", [record_id])
            exists = cloud_cursor.fetchone()
            
            if exists:
                # 更新
                set_clause = ', '.join([f"{k} = %s" for k in record_dict.keys()])
                sql = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
                cloud_cursor.execute(sql, list(record_dict.values()) + [record_id])
            else:
                # 插入
                record_dict['id'] = record_id
                columns = ', '.join(record_dict.keys())
                placeholders = ', '.join(['%s'] * len(record_dict))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cloud_cursor.execute(sql, list(record_dict.values()))
        
        cloud_conn.commit()
        logger.info(f"表 {table_name} 全量同步完成")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """獲取同步狀態"""
        local_conn = self.db_manager.get_local_connection()
        cursor = local_conn.cursor()
        
        # 統計同步記錄
        cursor.execute("""
            SELECT sync_status, COUNT(*) as count
            FROM sync_log
            GROUP BY sync_status
        """)
        status_counts = dict(cursor.fetchall())
        
        # 獲取最近的同步記錄
        cursor.execute("""
            SELECT * FROM sync_log
            ORDER BY created_at DESC
            LIMIT 10
        """)
        recent_syncs = [dict(row) for row in cursor.fetchall()]
        
        return {
            "engine_running": self.is_running,
            "queue_size": len(self.sync_queue),
            "status_counts": status_counts,
            "recent_syncs": recent_syncs
        }

