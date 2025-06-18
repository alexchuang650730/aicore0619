"""
SmartUI MCP 通用工具模块

提供SmartUI MCP系统中各组件共用的工具函数和辅助类。
"""

import asyncio
import logging
import json
import hashlib
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from pathlib import Path
import weakref
from functools import wraps, lru_cache
from contextlib import asynccontextmanager
import aiofiles
import yaml


T = TypeVar('T')


class SingletonMeta(type):
    """单例元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AsyncCache(Generic[T]):
    """异步缓存"""
    
    def __init__(self, max_size: int = 128, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {"args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if self.ttl is None:
            return False
        
        cache_time = self._cache[key].get("timestamp", 0)
        return time.time() - cache_time > self.ttl
    
    def _evict_lru(self) -> None:
        """淘汰最近最少使用的缓存项"""
        if len(self._cache) < self.max_size:
            return
        
        # 找到最少使用的键
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        del self._cache[lru_key]
        del self._access_times[lru_key]
    
    async def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        if key not in self._cache:
            return None
        
        if self._is_expired(key):
            del self._cache[key]
            del self._access_times[key]
            return None
        
        self._access_times[key] = time.time()
        return self._cache[key]["value"]
    
    async def set(self, key: str, value: T) -> None:
        """设置缓存值"""
        self._evict_lru()
        
        self._cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        self._access_times[key] = time.time()
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
            del self._access_times[key]
            return True
        return False
    
    async def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_times.clear()
    
    def cache_decorator(self, func: Callable) -> Callable:
        """缓存装饰器"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = self._generate_key(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = await self.get(key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数并缓存结果
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self.set(key, result)
            return result
        
        return wrapper


class Timer:
    """计时器"""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or str(uuid.uuid4())
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start(self) -> "Timer":
        """开始计时"""
        self.start_time = time.time()
        return self
    
    def stop(self) -> float:
        """停止计时并返回耗时"""
        if self.start_time is None:
            raise ValueError("Timer not started")
        
        self.end_time = time.time()
        return self.elapsed
    
    @property
    def elapsed(self) -> float:
        """获取耗时"""
        if self.start_time is None:
            return 0.0
        
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def __enter__(self) -> "Timer":
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self._calls: List[float] = []
    
    async def acquire(self) -> bool:
        """获取许可"""
        now = time.time()
        
        # 清理过期的调用记录
        self._calls = [call_time for call_time in self._calls if now - call_time < self.time_window]
        
        # 检查是否超过限制
        if len(self._calls) >= self.max_calls:
            return False
        
        # 记录本次调用
        self._calls.append(now)
        return True
    
    async def wait_for_permit(self) -> None:
        """等待获取许可"""
        while not await self.acquire():
            await asyncio.sleep(0.1)


class CircuitBreaker:
    """熔断器"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过熔断器调用函数"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """是否应该尝试重置"""
        if self.last_failure_time is None:
            return False
        
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self) -> None:
        """成功时的处理"""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self) -> None:
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class RetryPolicy:
    """重试策略"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行带重试的函数"""
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_attempts - 1:
                    delay = self.calculate_delay(attempt)
                    await asyncio.sleep(delay)
                else:
                    break
        
        raise last_exception


class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    async def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载YAML配置文件"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return yaml.safe_load(content)
    
    @staticmethod
    async def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
        """加载JSON配置文件"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    
    @staticmethod
    async def save_yaml(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
        """保存YAML配置文件"""
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            await f.write(content)
    
    @staticmethod
    async def save_json(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
        """保存JSON配置文件"""
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            content = json.dumps(data, indent=2, ensure_ascii=False)
            await f.write(content)


class WeakRefDict:
    """弱引用字典"""
    
    def __init__(self):
        self._data = weakref.WeakValueDictionary()
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def __delitem__(self, key: str) -> None:
        del self._data[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._data
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()
    
    def items(self):
        return self._data.items()


class EventEmitter:
    """事件发射器"""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, listener: Callable) -> None:
        """添加事件监听器"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)
    
    def off(self, event: str, listener: Callable) -> None:
        """移除事件监听器"""
        if event in self._listeners:
            try:
                self._listeners[event].remove(listener)
            except ValueError:
                pass
    
    def once(self, event: str, listener: Callable) -> None:
        """添加一次性事件监听器"""
        def wrapper(*args, **kwargs):
            self.off(event, wrapper)
            return listener(*args, **kwargs)
        
        self.on(event, wrapper)
    
    async def emit(self, event: str, *args, **kwargs) -> None:
        """发射事件"""
        listeners = self._listeners.get(event, [])
        
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(*args, **kwargs)
                else:
                    listener(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in event listener for {event}: {e}")


class AsyncLock:
    """异步锁管理器"""
    
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
    
    @asynccontextmanager
    async def acquire(self, key: str):
        """获取指定键的锁"""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        
        async with self._locks[key]:
            yield


class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """验证URL格式"""
        import re
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def validate_json(json_str: str) -> bool:
        """验证JSON格式"""
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def sanitize_html(html: str) -> str:
        """清理HTML内容"""
        import re
        # 移除脚本标签
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # 移除危险属性
        html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
        return html


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = {}
    
    @asynccontextmanager
    async def profile(self, name: str):
        """性能分析上下文管理器"""
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if name not in self.profiles:
                self.profiles[name] = []
            self.profiles[name].append(elapsed)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """获取性能统计"""
        if name not in self.profiles:
            return {}
        
        times = self.profiles[name]
        return {
            "count": len(times),
            "total": sum(times),
            "average": sum(times) / len(times),
            "min": min(times),
            "max": max(times)
        }
    
    def reset(self, name: Optional[str] = None) -> None:
        """重置性能数据"""
        if name:
            self.profiles.pop(name, None)
        else:
            self.profiles.clear()


# 装饰器

def async_timeout(timeout: float):
    """异步超时装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        return wrapper
    return decorator


def log_execution_time(logger: Optional[logging.Logger] = None):
    """记录执行时间装饰器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                log = logger or logging.getLogger(func.__module__)
                log.debug(f"{func.__name__} executed in {elapsed:.4f}s")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                log = logger or logging.getLogger(func.__module__)
                log.debug(f"{func.__name__} executed in {elapsed:.4f}s")
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def memoize(maxsize: int = 128, ttl: Optional[float] = None):
    """记忆化装饰器"""
    def decorator(func):
        cache = AsyncCache(max_size=maxsize, ttl=ttl)
        return cache.cache_decorator(func)
    return decorator


# 工具函数

def generate_id(prefix: str = "") -> str:
    """生成唯一ID"""
    return f"{prefix}{uuid.uuid4().hex}" if prefix else str(uuid.uuid4())


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并字典"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """反扁平化字典"""
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result


async def safe_execute(func: Callable, *args, default=None, **kwargs) -> Any:
    """安全执行函数"""
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error executing {func.__name__}: {e}")
        return default


def format_bytes(bytes_value: int) -> str:
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

