#!/usr/bin/env python3
"""
MCP服务注册器
用于将新的MCP服务注册到PowerAutomation系统中
"""

import json
import requests
import time
from datetime import datetime

class MCPServiceRegistrar:
    def __init__(self):
        self.services = [
            {
                "name": "REQUIREMENTS ANALYSIS_MCP",
                "description": "需求分析智能引擎",
                "port": 8094,
                "endpoint": "http://98.81.255.168:8094",
                "health_check": "/health",
                "capabilities": ["需求分析", "技术方案生成", "业务理解"],
                "status": "active",
                "version": "1.0.0"
            },
            {
                "name": "ARCHITECTURE DESIGN_MCP",
                "description": "架构设计智能引擎", 
                "port": 8095,
                "endpoint": "http://98.81.255.168:8095",
                "health_check": "/health",
                "capabilities": ["架构设计", "最佳实践推荐", "技术选型"],
                "status": "active",
                "version": "1.0.0"
            }
        ]
    
    def register_services(self):
        """注册所有MCP服务"""
        print("🚀 开始注册MCP服务...")
        
        for service in self.services:
            try:
                # 检查服务健康状态
                health_url = f"http://localhost:{service['port']}{service['health_check']}"
                response = requests.get(health_url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {service['name']} 健康检查通过")
                    
                    # 尝试注册到各种可能的注册端点
                    self._try_register_to_endpoints(service)
                else:
                    print(f"❌ {service['name']} 健康检查失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {service['name']} 注册失败: {e}")
    
    def _try_register_to_endpoints(self, service):
        """尝试向多个可能的注册端点注册服务"""
        registration_endpoints = [
            "http://localhost:8000/api/mcp/register",
            "http://localhost:5001/api/mcp/register", 
            "http://localhost:8080/api/mcp/register",
            "http://localhost:9000/api/mcp/register"
        ]
        
        for endpoint in registration_endpoints:
            try:
                response = requests.post(
                    endpoint,
                    json=service,
                    timeout=5,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ {service['name']} 成功注册到 {endpoint}")
                    return True
                else:
                    print(f"⚠️ {service['name']} 注册到 {endpoint} 失败: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️ 无法连接到注册端点 {endpoint}: {e}")
        
        return False
    
    def create_service_discovery_file(self):
        """创建服务发现文件"""
        discovery_data = {
            "timestamp": datetime.now().isoformat(),
            "services": self.services,
            "total_count": len(self.services)
        }
        
        # 保存到多个可能的位置
        discovery_paths = [
            "/opt/powerautomation/shared_core/mcptool/config/mcp_services.json",
            "/home/ubuntu/mcp_services_registry.json",
            "/tmp/mcp_services_discovery.json"
        ]
        
        for path in discovery_paths:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(discovery_data, f, indent=2, ensure_ascii=False)
                print(f"✅ 服务发现文件已保存到: {path}")
            except Exception as e:
                print(f"⚠️ 无法保存到 {path}: {e}")
    
    def update_smartui_config(self):
        """更新SmartUI配置"""
        try:
            # 尝试通过API更新SmartUI配置
            smartui_endpoints = [
                "http://localhost:5001/api/services/register",
                "http://localhost:5001/api/mcp/update"
            ]
            
            for endpoint in smartui_endpoints:
                try:
                    response = requests.post(
                        endpoint,
                        json={"services": self.services},
                        timeout=5
                    )
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ SmartUI配置已更新: {endpoint}")
                        return True
                        
                except Exception as e:
                    print(f"⚠️ 无法更新SmartUI配置 {endpoint}: {e}")
                    
        except Exception as e:
            print(f"❌ SmartUI配置更新失败: {e}")
        
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 MCP服务注册器启动")
    print("📋 目标: 注册需求分析和架构设计MCP服务")
    print("=" * 60)
    
    registrar = MCPServiceRegistrar()
    
    # 1. 注册服务到各种端点
    registrar.register_services()
    
    # 2. 创建服务发现文件
    registrar.create_service_discovery_file()
    
    # 3. 更新SmartUI配置
    registrar.update_smartui_config()
    
    print("=" * 60)
    print("🎉 MCP服务注册完成!")
    print("📊 如果MCP协调器仍未显示新服务，可能需要:")
    print("   1. 重启MCP协调器服务")
    print("   2. 清除浏览器缓存")
    print("   3. 检查服务发现机制配置")
    print("=" * 60)

if __name__ == "__main__":
    main()

