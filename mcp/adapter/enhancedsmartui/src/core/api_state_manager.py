#!/usr/bin/env python3
"""
SmartUI Enhanced - 动态API状态管理器
实现动态修改API端点、管理API版本和实时性能监控
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from functools import wraps
import threading
import weakref

logger = logging.getLogger(__name__)

@dataclass
class APIRoute:
    """API路由定义"""
    path: str
    methods: List[str]
    handler: Callable
    middleware: List[Callable] = None
    rate_limit: Optional[int] = None
    cache_ttl: Optional[int] = None
    auth_required: bool = False
    version: str = "1.0"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.middleware is None:
            self.middleware = []

@dataclass
class APIMetrics:
    """API性能指标"""
    endpoint: str
    request_count: int = 0
    total_response_time: float = 0.0
    error_count: int = 0
    last_request_time: Optional[datetime] = None
    avg_response_time: float = 0.0
    success_rate: float = 100.0
    
    def update_metrics(self, response_time: float, is_error: bool = False):
        """更新指标"""
        self.request_count += 1
        self.total_response_time += response_time
        self.avg_response_time = self.total_response_time / self.request_count
        self.last_request_time = datetime.now()
        
        if is_error:
            self.error_count += 1
        
        self.success_rate = ((self.request_count - self.error_count) / self.request_count) * 100

class DynamicRouteRegistry:
    """动态路由注册表"""
    
    def __init__(self):
        self.routes: Dict[str, APIRoute] = {}
        self.route_groups: Dict[str, List[str]] = {}
        self.middleware_stack: List[Callable] = []
        self._lock = threading.RLock()
    
    def register_route(self, route: APIRoute) -> bool:
        """注册动态路由"""
        with self._lock:
            route_key = f"{route.path}:{':'.join(route.methods)}"
            
            if route_key in self.routes:
                logger.warning(f"路由已存在，将被覆盖: {route_key}")
            
            self.routes[route_key] = route
            logger.info(f"注册动态路由: {route_key}")
            return True
    
    def unregister_route(self, path: str, methods: List[str] = None) -> bool:
        """注销动态路由"""
        with self._lock:
            if methods is None:
                # 删除所有方法的路由
                keys_to_remove = [key for key in self.routes.keys() if key.startswith(f"{path}:")]
            else:
                route_key = f"{path}:{':'.join(methods)}"
                keys_to_remove = [route_key] if route_key in self.routes else []
            
            for key in keys_to_remove:
                del self.routes[key]
                logger.info(f"注销动态路由: {key}")
            
            return len(keys_to_remove) > 0
    
    def get_route(self, path: str, method: str) -> Optional[APIRoute]:
        """获取路由"""
        with self._lock:
            # 精确匹配
            for route_key, route in self.routes.items():
                if route.path == path and method in route.methods:
                    return route
            
            # 模式匹配 (简单的通配符支持)
            for route_key, route in self.routes.items():
                if self._path_matches(path, route.path) and method in route.methods:
                    return route
            
            return None
    
    def _path_matches(self, request_path: str, route_path: str) -> bool:
        """路径匹配检查"""
        # 简单的通配符匹配
        if '*' in route_path:
            route_parts = route_path.split('/')
            request_parts = request_path.split('/')
            
            if len(route_parts) != len(request_parts):
                return False
            
            for route_part, request_part in zip(route_parts, request_parts):
                if route_part != '*' and route_part != request_part:
                    return False
            
            return True
        
        return request_path == route_path
    
    def list_routes(self) -> List[Dict[str, Any]]:
        """列出所有路由"""
        with self._lock:
            return [
                {
                    "path": route.path,
                    "methods": route.methods,
                    "version": route.version,
                    "created_at": route.created_at.isoformat(),
                    "auth_required": route.auth_required,
                    "rate_limit": route.rate_limit,
                    "cache_ttl": route.cache_ttl
                }
                for route in self.routes.values()
            ]

class APIPerformanceMonitor:
    """API性能监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, APIMetrics] = {}
        self.monitoring_enabled = True
        self._lock = threading.RLock()
        self.alert_thresholds = {
            "avg_response_time": 1000,  # ms
            "error_rate": 5,  # %
            "request_rate": 100  # requests/minute
        }
    
    def record_request(self, endpoint: str, response_time: float, is_error: bool = False):
        """记录请求指标"""
        if not self.monitoring_enabled:
            return
        
        with self._lock:
            if endpoint not in self.metrics:
                self.metrics[endpoint] = APIMetrics(endpoint=endpoint)
            
            self.metrics[endpoint].update_metrics(response_time, is_error)
            
            # 检查告警阈值
            self._check_alerts(endpoint)
    
    def _check_alerts(self, endpoint: str):
        """检查告警阈值"""
        metrics = self.metrics[endpoint]
        
        # 响应时间告警
        if metrics.avg_response_time > self.alert_thresholds["avg_response_time"]:
            logger.warning(f"API响应时间过高: {endpoint} - {metrics.avg_response_time:.2f}ms")
        
        # 错误率告警
        if metrics.success_rate < (100 - self.alert_thresholds["error_rate"]):
            logger.warning(f"API错误率过高: {endpoint} - {100 - metrics.success_rate:.2f}%")
    
    def get_metrics(self, endpoint: str = None) -> Dict[str, Any]:
        """获取性能指标"""
        with self._lock:
            if endpoint:
                return asdict(self.metrics.get(endpoint, APIMetrics(endpoint=endpoint)))
            else:
                return {
                    endpoint: asdict(metrics)
                    for endpoint, metrics in self.metrics.items()
                }
    
    def reset_metrics(self, endpoint: str = None):
        """重置指标"""
        with self._lock:
            if endpoint:
                if endpoint in self.metrics:
                    self.metrics[endpoint] = APIMetrics(endpoint=endpoint)
            else:
                self.metrics.clear()

class APIVersionManager:
    """API版本管理器"""
    
    def __init__(self):
        self.versions: Dict[str, Dict[str, Any]] = {}
        self.default_version = "1.0"
        self.deprecated_versions: List[str] = []
    
    def register_version(self, version: str, config: Dict[str, Any]):
        """注册API版本"""
        self.versions[version] = {
            "config": config,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        logger.info(f"注册API版本: {version}")
    
    def deprecate_version(self, version: str, sunset_date: datetime = None):
        """废弃API版本"""
        if version in self.versions:
            self.versions[version]["active"] = False
            self.versions[version]["deprecated_at"] = datetime.now().isoformat()
            
            if sunset_date:
                self.versions[version]["sunset_date"] = sunset_date.isoformat()
            
            if version not in self.deprecated_versions:
                self.deprecated_versions.append(version)
            
            logger.info(f"废弃API版本: {version}")
    
    def get_version_info(self, version: str = None) -> Dict[str, Any]:
        """获取版本信息"""
        if version:
            return self.versions.get(version, {})
        else:
            return {
                "versions": self.versions,
                "default_version": self.default_version,
                "deprecated_versions": self.deprecated_versions
            }

class APIStateManager:
    """API状态管理器 - 核心类"""
    
    def __init__(self, flask_app: Flask):
        self.app = flask_app
        self.route_registry = DynamicRouteRegistry()
        self.performance_monitor = APIPerformanceMonitor()
        self.version_manager = APIVersionManager()
        self.cache = {}
        self.rate_limiters = {}
        self._setup_middleware()
        
        # 启动后台监控任务
        self._start_background_tasks()
    
    def _setup_middleware(self):
        """设置中间件"""
        
        @self.app.before_request
        def before_request():
            """请求前处理"""
            g.start_time = time.time()
            g.request_id = f"{int(time.time() * 1000)}-{id(request)}"
            
            # 检查动态路由
            dynamic_route = self.route_registry.get_route(request.path, request.method)
            if dynamic_route:
                g.dynamic_route = dynamic_route
                
                # 应用中间件
                for middleware in dynamic_route.middleware:
                    result = middleware(request)
                    if result:  # 中间件返回响应，直接返回
                        return result
        
        @self.app.after_request
        def after_request(response):
            """请求后处理"""
            if hasattr(g, 'start_time'):
                response_time = (time.time() - g.start_time) * 1000  # ms
                
                # 记录性能指标
                is_error = response.status_code >= 400
                self.performance_monitor.record_request(
                    request.path, response_time, is_error
                )
                
                # 添加性能头
                response.headers['X-Response-Time'] = f"{response_time:.2f}ms"
                response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            
            return response
    
    def _start_background_tasks(self):
        """启动后台任务"""
        def background_monitor():
            while True:
                try:
                    # 清理过期缓存
                    self._cleanup_cache()
                    
                    # 生成性能报告
                    self._generate_performance_report()
                    
                    time.sleep(60)  # 每分钟执行一次
                except Exception as e:
                    logger.error(f"后台监控任务错误: {e}")
        
        monitor_thread = threading.Thread(target=background_monitor, daemon=True)
        monitor_thread.start()
    
    def add_dynamic_route(self, path: str, methods: List[str], handler: Callable, **kwargs) -> bool:
        """添加动态路由"""
        try:
            # 创建路由对象
            route = APIRoute(
                path=path,
                methods=methods,
                handler=handler,
                **kwargs
            )
            
            # 注册到路由表
            success = self.route_registry.register_route(route)
            
            if success:
                # 动态添加到Flask应用
                self._add_flask_route(route)
                logger.info(f"成功添加动态路由: {path} {methods}")
            
            return success
            
        except Exception as e:
            logger.error(f"添加动态路由失败: {e}")
            return False
    
    def _add_flask_route(self, route: APIRoute):
        """将动态路由添加到Flask应用"""
        def dynamic_handler(*args, **kwargs):
            """动态路由处理器"""
            try:
                # 应用速率限制
                if route.rate_limit:
                    if not self._check_rate_limit(route.path, route.rate_limit):
                        return jsonify({"error": "Rate limit exceeded"}), 429
                
                # 检查缓存
                if route.cache_ttl and request.method == 'GET':
                    cache_key = f"{route.path}:{request.query_string.decode()}"
                    cached_response = self._get_cache(cache_key)
                    if cached_response:
                        return cached_response
                
                # 调用实际处理器
                result = route.handler(*args, **kwargs)
                
                # 缓存响应
                if route.cache_ttl and request.method == 'GET' and isinstance(result, tuple):
                    response, status_code = result
                    if status_code == 200:
                        self._set_cache(cache_key, result, route.cache_ttl)
                
                return result
                
            except Exception as e:
                logger.error(f"动态路由处理错误: {e}")
                return jsonify({"error": "Internal server error"}), 500
        
        # 设置端点名称
        endpoint_name = f"dynamic_{route.path.replace('/', '_').replace('<', '').replace('>', '')}"
        
        # 添加路由到Flask
        self.app.add_url_rule(
            route.path,
            endpoint=endpoint_name,
            view_func=dynamic_handler,
            methods=route.methods
        )
    
    def remove_dynamic_route(self, path: str, methods: List[str] = None) -> bool:
        """移除动态路由"""
        try:
            success = self.route_registry.unregister_route(path, methods)
            
            if success:
                # 注意：Flask不支持动态移除路由，需要重启应用
                logger.warning(f"路由已从注册表移除，但Flask路由仍然存在: {path}")
            
            return success
            
        except Exception as e:
            logger.error(f"移除动态路由失败: {e}")
            return False
    
    def modify_route_behavior(self, path: str, modifications: Dict[str, Any]) -> bool:
        """修改路由行为"""
        try:
            # 查找现有路由
            existing_route = None
            for route in self.route_registry.routes.values():
                if route.path == path:
                    existing_route = route
                    break
            
            if not existing_route:
                logger.error(f"路由不存在: {path}")
                return False
            
            # 应用修改
            for key, value in modifications.items():
                if hasattr(existing_route, key):
                    setattr(existing_route, key, value)
                    logger.info(f"修改路由属性: {path}.{key} = {value}")
            
            return True
            
        except Exception as e:
            logger.error(f"修改路由行为失败: {e}")
            return False
    
    def _check_rate_limit(self, path: str, limit: int) -> bool:
        """检查速率限制"""
        current_time = time.time()
        window_start = current_time - 60  # 1分钟窗口
        
        if path not in self.rate_limiters:
            self.rate_limiters[path] = []
        
        # 清理过期记录
        self.rate_limiters[path] = [
            timestamp for timestamp in self.rate_limiters[path]
            if timestamp > window_start
        ]
        
        # 检查是否超过限制
        if len(self.rate_limiters[path]) >= limit:
            return False
        
        # 记录当前请求
        self.rate_limiters[path].append(current_time)
        return True
    
    def _get_cache(self, key: str) -> Any:
        """获取缓存"""
        if key in self.cache:
            cached_item = self.cache[key]
            if cached_item["expires_at"] > time.time():
                return cached_item["data"]
            else:
                del self.cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any, ttl: int):
        """设置缓存"""
        self.cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl
        }
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if item["expires_at"] <= current_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"清理过期缓存: {len(expired_keys)} 项")
    
    def _generate_performance_report(self):
        """生成性能报告"""
        metrics = self.performance_monitor.get_metrics()
        
        if metrics:
            total_requests = sum(m["request_count"] for m in metrics.values())
            avg_response_time = sum(
                m["avg_response_time"] * m["request_count"] for m in metrics.values()
            ) / total_requests if total_requests > 0 else 0
            
            logger.info(f"性能报告 - 总请求: {total_requests}, 平均响应时间: {avg_response_time:.2f}ms")
    
    def get_api_state(self) -> Dict[str, Any]:
        """获取API状态"""
        return {
            "routes": self.route_registry.list_routes(),
            "performance": self.performance_monitor.get_metrics(),
            "versions": self.version_manager.get_version_info(),
            "cache_stats": {
                "total_items": len(self.cache),
                "memory_usage": sum(len(str(item)) for item in self.cache.values())
            },
            "rate_limiters": {
                path: len(timestamps)
                for path, timestamps in self.rate_limiters.items()
            }
        }
    
    def apply_state_changes(self, changes: Dict[str, Any]) -> Dict[str, bool]:
        """应用状态变更"""
        results = {}
        
        # 处理路由变更
        if "routes" in changes:
            for route_change in changes["routes"]:
                action = route_change.get("action")
                
                if action == "add":
                    results[f"add_route_{route_change['path']}"] = self.add_dynamic_route(
                        route_change["path"],
                        route_change["methods"],
                        route_change["handler"],
                        **route_change.get("config", {})
                    )
                elif action == "remove":
                    results[f"remove_route_{route_change['path']}"] = self.remove_dynamic_route(
                        route_change["path"],
                        route_change.get("methods")
                    )
                elif action == "modify":
                    results[f"modify_route_{route_change['path']}"] = self.modify_route_behavior(
                        route_change["path"],
                        route_change["modifications"]
                    )
        
        # 处理性能配置变更
        if "performance" in changes:
            perf_changes = changes["performance"]
            if "monitoring_enabled" in perf_changes:
                self.performance_monitor.monitoring_enabled = perf_changes["monitoring_enabled"]
                results["performance_monitoring"] = True
            
            if "alert_thresholds" in perf_changes:
                self.performance_monitor.alert_thresholds.update(perf_changes["alert_thresholds"])
                results["alert_thresholds"] = True
        
        # 处理版本变更
        if "versions" in changes:
            for version_change in changes["versions"]:
                action = version_change.get("action")
                
                if action == "register":
                    self.version_manager.register_version(
                        version_change["version"],
                        version_change["config"]
                    )
                    results[f"register_version_{version_change['version']}"] = True
                elif action == "deprecate":
                    self.version_manager.deprecate_version(
                        version_change["version"],
                        version_change.get("sunset_date")
                    )
                    results[f"deprecate_version_{version_change['version']}"] = True
        
        return results

# 示例动态路由处理器
def create_dynamic_handler(response_data: Dict[str, Any]):
    """创建动态路由处理器"""
    def handler():
        return jsonify(response_data)
    return handler

def create_proxy_handler(target_url: str):
    """创建代理路由处理器"""
    import requests
    
    def handler():
        try:
            # 转发请求到目标URL
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                data=request.get_data(),
                params=request.args,
                timeout=30
            )
            
            return response.content, response.status_code, dict(response.headers)
        except Exception as e:
            return jsonify({"error": f"Proxy error: {str(e)}"}), 502
    
    return handler

if __name__ == "__main__":
    # 测试代码
    from flask import Flask
    
    app = Flask(__name__)
    api_manager = APIStateManager(app)
    
    # 添加一些测试路由
    api_manager.add_dynamic_route(
        "/api/test",
        ["GET"],
        create_dynamic_handler({"message": "Hello from dynamic route!"}),
        rate_limit=10,
        cache_ttl=60
    )
    
    @app.route("/api/state")
    def get_state():
        return jsonify(api_manager.get_api_state())
    
    print("API状态管理器测试服务器启动...")
    app.run(host="0.0.0.0", port=5002, debug=True)

