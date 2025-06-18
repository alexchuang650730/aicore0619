#!/usr/bin/env python3
"""
Release Manager MCP
发布管理器 - 负责统一部署管理、服务发现、部署验证和问题修复
运行在8096端口
"""

import asyncio
import json
import requests
import subprocess
import socket
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import os
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class ReleaseManager:
    """发布管理器"""
    
    def __init__(self):
        self.service_id = "release_manager_mcp"
        self.version = "1.0.0"
        self.status = "running"
        self.target_ip = "98.81.255.168"  # 统一部署目标IP
        self.coordinator_url = f"http://{self.target_ip}:8089"
        
        # 标准MCP端口分配
        self.standard_ports = {
            "mcp_coordinator": 8089,
            "operations_workflow_mcp": 8090,
            "github_mcp": 8091,
            "development_intervention_mcp": 8092,
            "coding_workflow_mcp": 8093,
            "requirements_analysis_mcp": 8094,
            "architecture_design_mcp": 8095,
            "release_manager_mcp": 8096
        }
        
        # 部署状态跟踪
        self.deployment_status = {}
        
        logger.info(f"✅ Release Manager MCP 初始化完成")
        logger.info(f"🎯 目标部署IP: {self.target_ip}")
    
    def get_current_ip(self):
        """获取当前服务器的实际IP地址"""
        try:
            # 尝试多种方法获取IP
            methods = [
                lambda: requests.get('http://ifconfig.me', timeout=5).text.strip(),
                lambda: requests.get('http://ipinfo.io/ip', timeout=5).text.strip(),
                lambda: socket.gethostbyname(socket.gethostname())
            ]
            
            for method in methods:
                try:
                    ip = method()
                    if ip and ip != '127.0.0.1':
                        return ip
                except:
                    continue
            
            return "unknown"
        except Exception as e:
            logger.error(f"获取IP地址失败: {e}")
            return "unknown"
    
    def check_service_health(self, service_name, port):
        """检查服务健康状态"""
        try:
            url = f"http://{self.target_ip}:{port}/health"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "response": response.json()}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
    
    def discover_services(self):
        """服务发现 - 扫描所有标准端口"""
        discovered = {}
        
        for service_name, port in self.standard_ports.items():
            logger.info(f"🔍 检查服务: {service_name} (端口 {port})")
            health = self.check_service_health(service_name, port)
            
            discovered[service_name] = {
                "port": port,
                "expected_url": f"http://{self.target_ip}:{port}",
                "health": health,
                "last_check": datetime.now().isoformat()
            }
        
        return discovered
    
    def register_service_to_coordinator(self, service_name, service_info):
        """将服务注册到MCP协调器"""
        try:
            register_url = f"{self.coordinator_url}/coordinator/register"
            
            registration_data = {
                "mcp_id": service_name,
                "url": service_info["expected_url"],
                "capabilities": self.get_service_capabilities(service_name),
                "description": f"{service_name} - 统一部署管理"
            }
            
            response = requests.post(register_url, json=registration_data, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ 服务 {service_name} 注册成功")
                return {"success": True, "response": response.json()}
            else:
                logger.error(f"❌ 服务 {service_name} 注册失败: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ 注册服务 {service_name} 时出错: {e}")
            return {"success": False, "error": str(e)}
    
    def get_service_capabilities(self, service_name):
        """获取服务能力列表"""
        capabilities_map = {
            "operations_workflow_mcp": ["file_placement", "mcp_registry_management", "smart_intervention"],
            "github_mcp": ["git_repo_info", "branch_management", "commit_history"],
            "development_intervention_mcp": ["architecture_compliance", "pr_review_prevention"],
            "coding_workflow_mcp": ["coding_process_management", "quality_control"],
            "requirements_analysis_mcp": ["requirement_collection", "analysis_generation"],
            "architecture_design_mcp": ["architecture_design", "intervention_mechanism"],
            "release_manager_mcp": ["deployment_management", "service_discovery", "deployment_verification"]
        }
        
        return capabilities_map.get(service_name, ["general_mcp_service"])
    
    def fix_ip_configuration(self):
        """修复IP地址配置问题"""
        current_ip = self.get_current_ip()
        
        fixes_applied = []
        
        # 检查当前IP是否为目标IP
        if current_ip != self.target_ip:
            logger.warning(f"⚠️ IP地址不匹配: 当前 {current_ip}, 目标 {self.target_ip}")
            fixes_applied.append(f"检测到IP不匹配: {current_ip} -> {self.target_ip}")
        
        # 检查服务绑定配置
        for service_name, port in self.standard_ports.items():
            try:
                # 检查端口是否监听在0.0.0.0
                result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
                if f"0.0.0.0:{port}" not in result.stdout:
                    fixes_applied.append(f"端口 {port} 未绑定到 0.0.0.0")
            except:
                pass
        
        return {
            "current_ip": current_ip,
            "target_ip": self.target_ip,
            "fixes_applied": fixes_applied,
            "timestamp": datetime.now().isoformat()
        }
    
    def perform_deployment_verification(self):
        """执行部署验证"""
        verification_results = {
            "ip_check": self.fix_ip_configuration(),
            "service_discovery": self.discover_services(),
            "coordinator_connectivity": None,
            "registration_status": {},
            "overall_status": "unknown"
        }
        
        # 检查协调器连接
        try:
            coord_response = requests.get(f"{self.coordinator_url}/coordinator/info", timeout=10)
            if coord_response.status_code == 200:
                verification_results["coordinator_connectivity"] = "healthy"
            else:
                verification_results["coordinator_connectivity"] = "unhealthy"
        except:
            verification_results["coordinator_connectivity"] = "unreachable"
        
        # 尝试注册健康的服务
        healthy_services = 0
        total_services = len(self.standard_ports)
        
        for service_name, service_info in verification_results["service_discovery"].items():
            if service_info["health"]["status"] == "healthy":
                reg_result = self.register_service_to_coordinator(service_name, service_info)
                verification_results["registration_status"][service_name] = reg_result
                if reg_result["success"]:
                    healthy_services += 1
        
        # 计算整体状态
        if healthy_services >= total_services * 0.8:  # 80%以上服务健康
            verification_results["overall_status"] = "healthy"
        elif healthy_services >= total_services * 0.5:  # 50%以上服务健康
            verification_results["overall_status"] = "degraded"
        else:
            verification_results["overall_status"] = "critical"
        
        return verification_results

# Flask API 端点
release_manager = ReleaseManager()

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        "service": release_manager.service_id,
        "status": "healthy",
        "version": release_manager.version,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/deployment/verify', methods=['POST'])
def verify_deployment():
    """执行部署验证"""
    try:
        results = release_manager.perform_deployment_verification()
        return jsonify({
            "success": True,
            "verification_results": results,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"部署验证失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/services/discover', methods=['GET'])
def discover_services():
    """服务发现"""
    try:
        services = release_manager.discover_services()
        return jsonify({
            "success": True,
            "discovered_services": services,
            "target_ip": release_manager.target_ip,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"服务发现失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/ip/fix', methods=['POST'])
def fix_ip_issues():
    """修复IP地址问题"""
    try:
        fix_results = release_manager.fix_ip_configuration()
        return jsonify({
            "success": True,
            "fix_results": fix_results,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"IP修复失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/mcp/request', methods=['POST'])
def handle_mcp_request():
    """处理MCP请求"""
    try:
        data = request.get_json()
        action = data.get('action')
        params = data.get('params', {})
        
        if action == "deployment_verification":
            results = release_manager.perform_deployment_verification()
            return jsonify({"success": True, "results": results})
        
        elif action == "service_discovery":
            services = release_manager.discover_services()
            return jsonify({"success": True, "services": services})
        
        elif action == "fix_ip_configuration":
            fix_results = release_manager.fix_ip_configuration()
            return jsonify({"success": True, "fix_results": fix_results})
        
        else:
            return jsonify({"success": False, "error": f"未知操作: {action}"}), 400
            
    except Exception as e:
        logger.error(f"处理MCP请求失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 启动 Release Manager MCP...")
    logger.info(f"📍 服务地址: http://0.0.0.0:8096")
    logger.info(f"🎯 目标部署IP: {release_manager.target_ip}")
    
    # 启动时执行一次部署验证
    try:
        logger.info("🔍 执行启动时部署验证...")
        verification_results = release_manager.perform_deployment_verification()
        logger.info(f"📊 验证结果: {verification_results['overall_status']}")
    except Exception as e:
        logger.error(f"启动验证失败: {e}")
    
    app.run(host='0.0.0.0', port=8096, debug=False)

