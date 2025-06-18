# MCP交互数据报告实现指南

## 🎯 概述

本文档说明如何在MCP中集成交互数据报告功能，向MCPCoordinator的InteractionLogManager发送处理数据。

## 🏗️ 架构概览

```
MCP业务逻辑 → MCPDataReporter → HTTP API → MCPCoordinator → InteractionLogManager
```

### **设计原则**
- ✅ **可选集成**: 现有MCP无需修改即可继续工作
- ✅ **异步处理**: 不阻塞MCP的核心业务逻辑
- ✅ **容错设计**: 网络故障时自动重试和本地缓存
- ✅ **向后兼容**: 支持渐进式迁移

## 🔧 实现步骤

### **步骤1: 添加MCPDataReporter依赖**

```python
# requirements.txt
aiohttp>=3.8.0
asyncio-throttle>=1.0.0
```

```python
# mcp_data_reporter.py
import asyncio
import json
import time
import logging
from typing import Dict, Optional, List
from aiohttp import ClientSession, ClientTimeout
from asyncio_throttle import Throttler
import sqlite3
from pathlib import Path

class MCPDataReporter:
    """MCP交互数据报告器"""
    
    def __init__(self, 
                 coordinator_url: str,
                 api_key: str,
                 mcp_id: str,
                 enable_reporting: bool = True,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 local_cache_path: str = "./interaction_cache.db"):
        
        self.coordinator_url = coordinator_url.rstrip('/')
        self.api_key = api_key
        self.mcp_id = mcp_id
        self.enable_reporting = enable_reporting
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.local_cache_path = local_cache_path
        
        # HTTP客户端配置
        self.timeout = ClientTimeout(total=5.0)
        self.session: Optional[ClientSession] = None
        
        # 限流器 (每秒最多10个请求)
        self.throttler = Throttler(rate_limit=10, period=1.0)
        
        # 本地缓存数据库
        self._init_local_cache()
        
        # 后台任务
        self._retry_task: Optional[asyncio.Task] = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"MCPDataReporter-{mcp_id}")
    
    def _init_local_cache(self):
        """初始化本地缓存数据库"""
        self.cache_db = sqlite3.connect(self.local_cache_path, check_same_thread=False)
        self.cache_db.execute("""
            CREATE TABLE IF NOT EXISTS failed_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_data TEXT NOT NULL,
                timestamp REAL NOT NULL,
                retry_count INTEGER DEFAULT 0
            )
        """)
        self.cache_db.commit()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = ClientSession(timeout=self.timeout)
        if self.enable_reporting:
            self._retry_task = asyncio.create_task(self._retry_failed_interactions())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._retry_task:
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
        
        self.cache_db.close()
    
    async def report_interaction_start(self, 
                                     interaction_id: str,
                                     request_data: Dict) -> bool:
        """报告交互开始"""
        if not self.enable_reporting:
            return True
            
        data = {
            "action": "interaction_start",
            "interaction_id": interaction_id,
            "mcp_id": self.mcp_id,
            "timestamp": time.time(),
            "request_data": request_data
        }
        
        return await self._send_data(data)
    
    async def report_interaction_progress(self,
                                        interaction_id: str,
                                        progress_data: Dict) -> bool:
        """报告交互进度"""
        if not self.enable_reporting:
            return True
            
        data = {
            "action": "interaction_progress",
            "interaction_id": interaction_id,
            "mcp_id": self.mcp_id,
            "timestamp": time.time(),
            "progress_data": progress_data
        }
        
        return await self._send_data(data)
    
    async def report_interaction_complete(self,
                                        interaction_id: str,
                                        result_data: Dict) -> bool:
        """报告交互完成"""
        if not self.enable_reporting:
            return True
            
        data = {
            "action": "interaction_complete",
            "interaction_id": interaction_id,
            "mcp_id": self.mcp_id,
            "timestamp": time.time(),
            "result_data": result_data
        }
        
        return await self._send_data(data)
    
    async def report_interaction_error(self,
                                     interaction_id: str,
                                     error_data: Dict) -> bool:
        """报告交互错误"""
        if not self.enable_reporting:
            return True
            
        data = {
            "action": "interaction_error",
            "interaction_id": interaction_id,
            "mcp_id": self.mcp_id,
            "timestamp": time.time(),
            "error_data": error_data
        }
        
        return await self._send_data(data)
    
    async def _send_data(self, data: Dict) -> bool:
        """发送数据到MCPCoordinator"""
        try:
            # 限流
            async with self.throttler:
                # 发送HTTP请求
                async with self.session.post(
                    f"{self.coordinator_url}/api/v2/interactions",
                    json=data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    
                    if response.status == 200:
                        self.logger.debug(f"Successfully sent interaction data: {data['interaction_id']}")
                        return True
                    else:
                        self.logger.warning(f"Failed to send data, status: {response.status}")
                        await self._cache_failed_interaction(data)
                        return False
                        
        except Exception as e:
            self.logger.error(f"Error sending interaction data: {e}")
            await self._cache_failed_interaction(data)
            return False
    
    async def _cache_failed_interaction(self, data: Dict):
        """缓存失败的交互数据"""
        try:
            self.cache_db.execute(
                "INSERT INTO failed_interactions (interaction_data, timestamp) VALUES (?, ?)",
                (json.dumps(data), time.time())
            )
            self.cache_db.commit()
            self.logger.info(f"Cached failed interaction: {data.get('interaction_id')}")
        except Exception as e:
            self.logger.error(f"Failed to cache interaction data: {e}")
    
    async def _retry_failed_interactions(self):
        """后台任务：重试失败的交互数据"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒重试一次
                
                cursor = self.cache_db.execute(
                    "SELECT id, interaction_data, retry_count FROM failed_interactions WHERE retry_count < ? ORDER BY timestamp LIMIT 10",
                    (self.max_retries,)
                )
                
                failed_interactions = cursor.fetchall()
                
                for row_id, interaction_data_str, retry_count in failed_interactions:
                    try:
                        interaction_data = json.loads(interaction_data_str)
                        
                        # 尝试重新发送
                        success = await self._send_data(interaction_data)
                        
                        if success:
                            # 成功则删除缓存
                            self.cache_db.execute("DELETE FROM failed_interactions WHERE id = ?", (row_id,))
                            self.cache_db.commit()
                            self.logger.info(f"Successfully retried interaction: {interaction_data.get('interaction_id')}")
                        else:
                            # 失败则增加重试次数
                            self.cache_db.execute(
                                "UPDATE failed_interactions SET retry_count = retry_count + 1 WHERE id = ?",
                                (row_id,)
                            )
                            self.cache_db.commit()
                            
                    except Exception as e:
                        self.logger.error(f"Error retrying interaction {row_id}: {e}")
                
                # 清理超过最大重试次数的记录
                self.cache_db.execute("DELETE FROM failed_interactions WHERE retry_count >= ?", (self.max_retries,))
                self.cache_db.commit()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in retry task: {e}")
```

### **步骤2: 在MCP中集成数据报告**

```python
# your_mcp.py
import asyncio
import uuid
from mcp_data_reporter import MCPDataReporter

class YourMCP:
    def __init__(self, config):
        self.config = config
        
        # 初始化数据报告器 (可选)
        self.data_reporter = None
        if config.get('enable_interaction_logging', False):
            self.data_reporter = MCPDataReporter(
                coordinator_url=config['coordinator_url'],
                api_key=config['coordinator_api_key'],
                mcp_id=config['mcp_id'],
                enable_reporting=True
            )
    
    async def process_request(self, user_request):
        """处理用户请求的主要方法"""
        
        # 生成唯一交互ID
        interaction_id = f"int_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # 可选：报告交互开始
        if self.data_reporter:
            await self.data_reporter.report_interaction_start(
                interaction_id=interaction_id,
                request_data={
                    "user_id": user_request.get('user_id'),
                    "request_type": user_request.get('type'),
                    "input_size": len(str(user_request)),
                    "parameters": user_request.get('parameters', {})
                }
            )
        
        try:
            # 执行核心业务逻辑
            result = await self._execute_business_logic(user_request)
            
            # 可选：报告交互完成
            if self.data_reporter:
                await self.data_reporter.report_interaction_complete(
                    interaction_id=interaction_id,
                    result_data={
                        "success": True,
                        "output_size": len(str(result)),
                        "processing_time": result.get('processing_time'),
                        "quality_score": result.get('quality_score'),
                        "adapter_used": result.get('adapter_used')
                    }
                )
            
            return result
            
        except Exception as e:
            # 可选：报告交互错误
            if self.data_reporter:
                await self.data_reporter.report_interaction_error(
                    interaction_id=interaction_id,
                    error_data={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "error_code": getattr(e, 'code', None)
                    }
                )
            
            raise
    
    async def _execute_business_logic(self, request):
        """执行核心业务逻辑"""
        # 这里是您的MCP核心逻辑
        # 不需要修改现有代码
        pass
    
    async def start(self):
        """启动MCP"""
        if self.data_reporter:
            await self.data_reporter.__aenter__()
    
    async def stop(self):
        """停止MCP"""
        if self.data_reporter:
            await self.data_reporter.__aexit__(None, None, None)
```

### **步骤3: 配置文件设置**

```toml
# mcp_config.toml
[mcp]
mcp_id = "your_mcp_001"
name = "Your MCP"
version = "1.0.0"

[interaction_logging]
# 可选启用交互日志功能
enable_interaction_logging = false  # 默认关闭
coordinator_url = "http://mcp-coordinator:8080"
coordinator_api_key = "your_api_key_here"

# 高级配置
max_retries = 3
retry_delay = 1.0
local_cache_path = "./data/interaction_cache.db"
```

## 🧪 测试和验证

### **单元测试示例**

```python
# test_mcp_data_reporter.py
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from mcp_data_reporter import MCPDataReporter

@pytest.mark.asyncio
async def test_data_reporter_success():
    """测试数据报告成功场景"""
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        # 模拟成功响应
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with MCPDataReporter(
            coordinator_url="http://test-coordinator:8080",
            api_key="test_key",
            mcp_id="test_mcp"
        ) as reporter:
            
            success = await reporter.report_interaction_start(
                interaction_id="test_123",
                request_data={"test": "data"}
            )
            
            assert success is True
            mock_post.assert_called_once()

@pytest.mark.asyncio
async def test_data_reporter_failure_and_cache():
    """测试数据报告失败和缓存场景"""
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        # 模拟失败响应
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with MCPDataReporter(
            coordinator_url="http://test-coordinator:8080",
            api_key="test_key",
            mcp_id="test_mcp",
            local_cache_path=":memory:"  # 使用内存数据库测试
        ) as reporter:
            
            success = await reporter.report_interaction_start(
                interaction_id="test_123",
                request_data={"test": "data"}
            )
            
            assert success is False
            
            # 验证数据被缓存
            cursor = reporter.cache_db.execute("SELECT COUNT(*) FROM failed_interactions")
            count = cursor.fetchone()[0]
            assert count == 1

@pytest.mark.asyncio
async def test_disabled_reporting():
    """测试禁用报告功能"""
    
    async with MCPDataReporter(
        coordinator_url="http://test-coordinator:8080",
        api_key="test_key",
        mcp_id="test_mcp",
        enable_reporting=False
    ) as reporter:
        
        success = await reporter.report_interaction_start(
            interaction_id="test_123",
            request_data={"test": "data"}
        )
        
        # 禁用时应该直接返回True
        assert success is True
```

### **集成测试**

```python
# test_mcp_integration.py
import pytest
import asyncio
from your_mcp import YourMCP

@pytest.mark.asyncio
async def test_mcp_with_reporting_enabled():
    """测试启用报告功能的MCP"""
    
    config = {
        'mcp_id': 'test_mcp',
        'enable_interaction_logging': True,
        'coordinator_url': 'http://test-coordinator:8080',
        'coordinator_api_key': 'test_key'
    }
    
    mcp = YourMCP(config)
    await mcp.start()
    
    try:
        # 测试请求处理
        result = await mcp.process_request({
            'user_id': 'test_user',
            'type': 'test_request',
            'data': 'test_data'
        })
        
        # 验证结果
        assert result is not None
        
    finally:
        await mcp.stop()

@pytest.mark.asyncio
async def test_mcp_with_reporting_disabled():
    """测试禁用报告功能的MCP"""
    
    config = {
        'mcp_id': 'test_mcp',
        'enable_interaction_logging': False
    }
    
    mcp = YourMCP(config)
    await mcp.start()
    
    try:
        # 测试请求处理 (应该正常工作)
        result = await mcp.process_request({
            'user_id': 'test_user',
            'type': 'test_request',
            'data': 'test_data'
        })
        
        # 验证结果
        assert result is not None
        
    finally:
        await mcp.stop()
```

## 📊 监控和调试

### **日志配置**

```python
# logging_config.py
import logging
import sys

def setup_logging(mcp_id: str, log_level: str = "INFO"):
    """设置日志配置"""
    
    # 创建logger
    logger = logging.getLogger(f"MCP-{mcp_id}")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 创建handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))
    
    # 创建formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # 添加handler到logger
    logger.addHandler(handler)
    
    return logger
```

### **性能监控**

```python
# performance_monitor.py
import time
import psutil
from typing import Dict

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.start_memory = psutil.virtual_memory().used
        self.start_cpu = psutil.cpu_percent()
    
    def get_metrics(self) -> Dict:
        """获取性能指标"""
        if self.start_time is None:
            return {}
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().used
        end_cpu = psutil.cpu_percent()
        
        return {
            "processing_time": end_time - self.start_time,
            "memory_usage_mb": (end_memory - self.start_memory) / 1024 / 1024,
            "cpu_usage_percent": end_cpu,
            "timestamp": end_time
        }

# 在MCP中使用
class YourMCPWithMonitoring(YourMCP):
    async def process_request(self, user_request):
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        try:
            result = await super().process_request(user_request)
            
            # 添加性能指标到结果
            result['performance_metrics'] = monitor.get_metrics()
            
            return result
        except Exception as e:
            # 即使出错也记录性能指标
            if self.data_reporter:
                await self.data_reporter.report_interaction_error(
                    interaction_id=interaction_id,
                    error_data={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "performance_metrics": monitor.get_metrics()
                    }
                )
            raise
```

## 🔧 故障排除

### **常见问题和解决方案**

#### **1. 网络连接问题**
```python
# 检查网络连接
async def check_coordinator_connection(coordinator_url: str, api_key: str) -> bool:
    try:
        async with ClientSession() as session:
            async with session.get(
                f"{coordinator_url}/api/v2/health",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=ClientTimeout(total=5.0)
            ) as response:
                return response.status == 200
    except Exception:
        return False
```

#### **2. API密钥验证问题**
```python
# 验证API密钥
async def validate_api_key(coordinator_url: str, api_key: str) -> bool:
    try:
        async with ClientSession() as session:
            async with session.post(
                f"{coordinator_url}/api/v2/validate",
                headers={"Authorization": f"Bearer {api_key}"}
            ) as response:
                return response.status == 200
    except Exception:
        return False
```

#### **3. 本地缓存问题**
```python
# 清理本地缓存
def cleanup_local_cache(cache_path: str, max_age_days: int = 7):
    import sqlite3
    import time
    
    conn = sqlite3.connect(cache_path)
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    
    conn.execute("DELETE FROM failed_interactions WHERE timestamp < ?", (cutoff_time,))
    conn.commit()
    conn.close()
```

## 📋 检查清单

### **集成前检查**
- [ ] 确认MCPCoordinator支持v2 API
- [ ] 获取有效的API密钥
- [ ] 配置网络访问权限
- [ ] 准备本地缓存存储路径

### **集成后验证**
- [ ] 测试数据报告功能正常工作
- [ ] 验证网络故障时的容错机制
- [ ] 检查本地缓存和重试机制
- [ ] 确认性能影响在可接受范围内

### **生产部署检查**
- [ ] 配置适当的日志级别
- [ ] 设置监控和告警
- [ ] 准备故障排除文档
- [ ] 建立数据备份策略

---

## 📞 支持和帮助

如果在集成过程中遇到问题，请参考：
- `workflow_howto/mcp_coordinator_interaction_management.md` - MCPCoordinator端架构
- `workflow_howto/MANDATORY_DEVELOPMENT_PRINCIPLES.md` - 开发原则
- 或联系系统架构师获取支持

