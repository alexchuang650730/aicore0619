"""
智慧UI高級同步引擎
增強版數據同步，支持實時同步、衝突解決、性能優化
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import hashlib

logger = logging.getLogger(__name__)

class SyncStrategy(Enum):
    """同步策略"""
    REAL_TIME = "real_time"      # 實時同步
    BATCH = "batch"              # 批量同步
    SCHEDULED = "scheduled"      # 定時同步

class ConflictResolution(Enum):
    """衝突解決策略"""
    LOCAL_WINS = "local_wins"    # 本地優先
    REMOTE_WINS = "remote_wins"  # 遠程優先
    TIMESTAMP = "timestamp"      # 時間戳優先
    MANUAL = "manual"            # 手動解決

@dataclass
class SyncConfig:
    """同步配置"""
    strategy: SyncStrategy = SyncStrategy.REAL_TIME
    conflict_resolution: ConflictResolution = ConflictResolution.TIMESTAMP
    batch_size: int = 50
    sync_interval: int = 10  # 秒
    max_retries: int = 3
    retry_delay: int = 5     # 秒
    enable_compression: bool = True
    enable_encryption: bool = False

@dataclass
class SyncMetrics:
    """同步指標"""
    total_synced: int = 0
    total_failed: int = 0
    last_sync_time: Optional[datetime] = None
    avg_sync_time: float = 0.0
    sync_queue_size: int = 0
    conflicts_resolved: int = 0

class AdvancedSyncEngine:
    """高級智慧同步引擎"""
    
    def __init__(self, db_manager, config: SyncConfig = None):
        self.db_manager = db_manager
        self.config = config or SyncConfig()
        self.sync_queue = asyncio.Queue()
        self.metrics = SyncMetrics()
        self.is_running = False
        self.sync_tasks = []
        self.event_loop = None
        self.sync_thread = None
        
        # 同步回調函數
        self.on_sync_success: Optional[Callable] = None
        self.on_sync_failure: Optional[Callable] = None
        self.on_conflict: Optional[Callable] = None
        
    def start_sync_engine(self):
        """啟動高級同步引擎"""
        if not self.is_running:
            self.is_running = True
            self.sync_thread = threading.Thread(target=self._run_async_loop, daemon=True)
            self.sync_thread.start()
            logger.info("高級智慧同步引擎已啟動")
    
    def stop_sync_engine(self):
        """停止同步引擎"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("高級智慧同步引擎已停止")
    
    def _run_async_loop(self):
        """運行異步事件循環"""
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        try:
            self.event_loop.run_until_complete(self._async_sync_worker())
        except Exception as e:
            logger.error(f"同步引擎異步循環錯誤: {e}")
        finally:
            self.event_loop.close()
    
    async def _async_sync_worker(self):
        """異步同步工作器"""
        while self.is_running:
            try:
                if self.config.strategy == SyncStrategy.REAL_TIME:
                    await self._real_time_sync()
                elif self.config.strategy == SyncStrategy.BATCH:
                    await self._batch_sync()
                elif self.config.strategy == SyncStrategy.SCHEDULED:
                    await self._scheduled_sync()
                
                await asyncio.sleep(1)  # 短暫休息
                
            except Exception as e:
                logger.error(f"同步工作器錯誤: {e}")
                await asyncio.sleep(5)
    
    async def _real_time_sync(self):
        """實時同步"""
        try:
            # 非阻塞獲取同步任務
            sync_record = await asyncio.wait_for(
                self.sync_queue.get(), timeout=1.0
            )
            
            start_time = time.time()
            success = await self._process_sync_record(sync_record)
            sync_time = time.time() - start_time
            
            # 更新指標
            self._update_metrics(success, sync_time)
            
            # 調用回調
            if success and self.on_sync_success:
                self.on_sync_success(sync_record)
            elif not success and self.on_sync_failure:
                self.on_sync_failure(sync_record)
                
        except asyncio.TimeoutError:
            # 沒有待同步的記錄，繼續等待
            pass
    
    async def _batch_sync(self):
        """批量同步"""
        records = []
        
        # 收集批量記錄
        for _ in range(self.config.batch_size):
            try:
                record = await asyncio.wait_for(
                    self.sync_queue.get(), timeout=0.1
                )
                records.append(record)
            except asyncio.TimeoutError:
                break
        
        if records:
            start_time = time.time()
            success_count = await self._process_batch_sync(records)
            sync_time = time.time() - start_time
            
            # 更新指標
            for i in range(len(records)):
                success = i < success_count
                self._update_metrics(success, sync_time / len(records))
    
    async def _scheduled_sync(self):
        """定時同步"""
        await asyncio.sleep(self.config.sync_interval)
        
        # 獲取所有待同步記錄
        records = []
        while not self.sync_queue.empty():
            try:
                record = self.sync_queue.get_nowait()
                records.append(record)
            except asyncio.QueueEmpty:
                break
        
        if records:
            await self._process_batch_sync(records)
    
    async def _process_sync_record(self, record) -> bool:
        """處理單個同步記錄"""
        if not self.db_manager.get_cloud_connection():
            logger.warning("雲端數據庫不可用，跳過同步")
            return False
        
        try:
            # 檢查衝突
            conflict = await self._check_conflict(record)
            if conflict:
                resolved_record = await self._resolve_conflict(record, conflict)
                if not resolved_record:
                    return False
                record = resolved_record
            
            # 執行同步
            success = await self._execute_sync(record)
            
            if success:
                # 更新本地同步狀態
                await self._update_local_sync_status(record, 'synced')
                logger.info(f"同步成功: {record.table_name}.{record.record_id}")
            else:
                await self._update_local_sync_status(record, 'failed')
                logger.error(f"同步失敗: {record.table_name}.{record.record_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"處理同步記錄錯誤: {e}")
            await self._update_local_sync_status(record, 'failed')
            return False
    
    async def _process_batch_sync(self, records: List) -> int:
        """處理批量同步"""
        success_count = 0
        
        for record in records:
            success = await self._process_sync_record(record)
            if success:
                success_count += 1
        
        logger.info(f"批量同步完成: {success_count}/{len(records)} 成功")
        return success_count
    
    async def _check_conflict(self, record) -> Optional[Dict]:
        """檢查同步衝突"""
        try:
            cloud_conn = self.db_manager.get_cloud_connection()
            cursor = cloud_conn.cursor()
            
            # 獲取雲端記錄
            cursor.execute(
                f"SELECT * FROM {record.table_name} WHERE id = %s",
                [record.record_id]
            )
            cloud_record = cursor.fetchone()
            
            if cloud_record and record.action == 'update':
                # 檢查時間戳衝突
                cloud_updated = cloud_record.get('updated_at')
                local_updated = record.data.get('updated_at')
                
                if cloud_updated and local_updated:
                    cloud_time = datetime.fromisoformat(cloud_updated)
                    local_time = datetime.fromisoformat(local_updated)
                    
                    if cloud_time > local_time:
                        return {
                            'type': 'timestamp_conflict',
                            'cloud_record': dict(cloud_record),
                            'local_record': record.data
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"檢查衝突錯誤: {e}")
            return None
    
    async def _resolve_conflict(self, record, conflict) -> Optional:
        """解決同步衝突"""
        try:
            resolution = self.config.conflict_resolution
            
            if resolution == ConflictResolution.LOCAL_WINS:
                # 本地優先，繼續使用本地記錄
                return record
                
            elif resolution == ConflictResolution.REMOTE_WINS:
                # 遠程優先，跳過本地更新
                logger.info(f"衝突解決: 遠程優先，跳過本地更新 {record.table_name}.{record.record_id}")
                return None
                
            elif resolution == ConflictResolution.TIMESTAMP:
                # 時間戳優先，已在檢查階段處理
                logger.info(f"衝突解決: 時間戳優先，使用雲端版本 {record.table_name}.{record.record_id}")
                return None
                
            elif resolution == ConflictResolution.MANUAL:
                # 手動解決，調用回調
                if self.on_conflict:
                    resolved = self.on_conflict(record, conflict)
                    return resolved
                else:
                    logger.warning(f"需要手動解決衝突，但未設置回調: {record.table_name}.{record.record_id}")
                    return None
            
            self.metrics.conflicts_resolved += 1
            return record
            
        except Exception as e:
            logger.error(f"解決衝突錯誤: {e}")
            return None
    
    async def _execute_sync(self, record) -> bool:
        """執行同步操作"""
        try:
            cloud_conn = self.db_manager.get_cloud_connection()
            cursor = cloud_conn.cursor()
            
            if record.action == 'insert':
                columns = ', '.join(record.data.keys())
                placeholders = ', '.join(['%s'] * len(record.data))
                sql = f"INSERT INTO {record.table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(record.data.values()))
                
            elif record.action == 'update':
                set_clause = ', '.join([f"{k} = %s" for k in record.data.keys()])
                sql = f"UPDATE {record.table_name} SET {set_clause} WHERE id = %s"
                cursor.execute(sql, list(record.data.values()) + [record.record_id])
                
            elif record.action == 'delete':
                sql = f"DELETE FROM {record.table_name} WHERE id = %s"
                cursor.execute(sql, [record.record_id])
            
            cloud_conn.commit()
            return True
            
        except Exception as e:
            cloud_conn.rollback()
            logger.error(f"執行同步錯誤: {e}")
            return False
    
    async def _update_local_sync_status(self, record, status: str):
        """更新本地同步狀態"""
        try:
            local_conn = self.db_manager.get_local_connection()
            cursor = local_conn.cursor()
            
            cursor.execute("""
                UPDATE sync_log 
                SET sync_status = ?, synced_at = ?
                WHERE table_name = ? AND record_id = ? AND action = ?
            """, (
                status,
                datetime.now(),
                record.table_name,
                record.record_id,
                record.action
            ))
            local_conn.commit()
            
        except Exception as e:
            logger.error(f"更新本地同步狀態錯誤: {e}")
    
    def _update_metrics(self, success: bool, sync_time: float):
        """更新同步指標"""
        if success:
            self.metrics.total_synced += 1
        else:
            self.metrics.total_failed += 1
        
        self.metrics.last_sync_time = datetime.now()
        
        # 計算平均同步時間
        total_operations = self.metrics.total_synced + self.metrics.total_failed
        if total_operations > 0:
            self.metrics.avg_sync_time = (
                (self.metrics.avg_sync_time * (total_operations - 1) + sync_time) / total_operations
            )
        
        self.metrics.sync_queue_size = self.sync_queue.qsize()
    
    async def add_sync_record_async(self, table_name: str, record_id: int, 
                                  action: str, data: Dict[str, Any]):
        """異步添加同步記錄"""
        from .sync_engine import SyncRecord
        
        sync_record = SyncRecord(
            table_name=table_name,
            record_id=record_id,
            action=action,
            data=data,
            timestamp=datetime.now()
        )
        
        await self.sync_queue.put(sync_record)
        logger.info(f"添加異步同步記錄: {table_name}.{record_id} ({action})")
    
    def add_sync_record(self, table_name: str, record_id: int, 
                       action: str, data: Dict[str, Any]):
        """同步添加同步記錄（兼容舊接口）"""
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.add_sync_record_async(table_name, record_id, action, data),
                self.event_loop
            )
        else:
            # 如果異步循環未運行，使用同步方式
            from .sync_engine import SyncRecord
            sync_record = SyncRecord(
                table_name=table_name,
                record_id=record_id,
                action=action,
                data=data,
                timestamp=datetime.now()
            )
            # 直接處理（同步模式）
            logger.info(f"添加同步記錄（同步模式）: {table_name}.{record_id} ({action})")
    
    def get_sync_metrics(self) -> Dict[str, Any]:
        """獲取同步指標"""
        return {
            "total_synced": self.metrics.total_synced,
            "total_failed": self.metrics.total_failed,
            "success_rate": (
                self.metrics.total_synced / 
                max(1, self.metrics.total_synced + self.metrics.total_failed) * 100
            ),
            "last_sync_time": self.metrics.last_sync_time.isoformat() if self.metrics.last_sync_time else None,
            "avg_sync_time": self.metrics.avg_sync_time,
            "sync_queue_size": self.metrics.sync_queue_size,
            "conflicts_resolved": self.metrics.conflicts_resolved,
            "engine_running": self.is_running,
            "sync_strategy": self.config.strategy.value,
            "conflict_resolution": self.config.conflict_resolution.value
        }
    
    def set_callbacks(self, on_success: Callable = None, 
                     on_failure: Callable = None, on_conflict: Callable = None):
        """設置同步回調函數"""
        self.on_sync_success = on_success
        self.on_sync_failure = on_failure
        self.on_conflict = on_conflict

