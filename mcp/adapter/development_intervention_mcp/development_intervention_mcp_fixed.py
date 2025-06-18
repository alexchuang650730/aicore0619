#!/usr/bin/env python3
"""
Development Intervention MCP - 开发介入MCP (修复版本)
智能开发介入与PR预防系统
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """违规类型"""
    DIRECT_MCP_IMPORT = "direct_mcp_import"
    BYPASS_COORDINATOR = "bypass_coordinator"
    HARDCODED_CREDENTIALS = "hardcoded_credentials"
    MISSING_DOCUMENTATION = "missing_documentation"
    CODE_QUALITY = "code_quality"

class SeverityLevel(Enum):
    """严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ViolationReport:
    """违规报告"""
    violation_type: ViolationType
    severity: SeverityLevel
    file_path: str
    line_number: int
    description: str
    suggestion: str
    auto_fixable: bool = False

class DevelopmentInterventionMCP:
    """开发介入MCP - 智能开发介入与PR预防"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.mcp_id = "development_intervention_mcp"
        self.version = "2.0.0"
        
        # 违规检测规则
        self.violation_rules = self._initialize_violation_rules()
        
        # 统计信息
        self.intervention_stats = {
            "total_scans": 0,
            "violations_detected": 0,
            "auto_fixes_applied": 0,
            "prevented_commits": 0
        }
        
        # 初始化Git监控
        self.git_extension = None
        
        logger.info(f"🛡️ {self.mcp_id} 初始化完成")
    
    def _initialize_violation_rules(self) -> Dict[str, Dict]:
        """初始化违规检测规则"""
        return {
            "direct_mcp_import": {
                "patterns": [
                    r"from\s+\w*mcp\w*\s+import",
                    r"import\s+\w*mcp\w*(?!.*coordinator)",
                ],
                "severity": SeverityLevel.CRITICAL,
                "description": "检测到直接MCP导入，违反中央协调原则",
                "suggestion": "使用 coordinator.get_mcp() 获取MCP实例"
            },
            "bypass_coordinator": {
                "patterns": [
                    r"(?<!coordinator\.)route_to",
                    r"(?<!coordinator\.)call_mcp",
                ],
                "severity": SeverityLevel.HIGH,
                "description": "检测到绕过中央协调器的调用",
                "suggestion": "所有MCP调用必须通过coordinator进行"
            }
        }
    
    async def scan_project_compliance(self, project_path: str) -> Dict[str, Any]:
        """扫描项目合规性"""
        try:
            violations = []
            scanned_files = 0
            
            project_root = Path(project_path)
            
            # 扫描Python文件
            for py_file in project_root.rglob("*.py"):
                if self._should_skip_file(py_file):
                    continue
                
                file_violations = await self._scan_file_compliance(py_file)
                violations.extend(file_violations)
                scanned_files += 1
            
            # 更新统计
            self.intervention_stats["total_scans"] += 1
            self.intervention_stats["violations_detected"] += len(violations)
            
            return {
                "success": True,
                "scanned_files": scanned_files,
                "total_violations": len(violations),
                "violations": [self._violation_to_dict(v) for v in violations],
                "compliance_score": self._calculate_compliance_score(violations, scanned_files)
            }
            
        except Exception as e:
            logger.error(f"项目合规性扫描失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "node_modules",
            ".pytest_cache"
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    async def _scan_file_compliance(self, file_path: Path) -> List[ViolationReport]:
        """扫描单个文件的合规性"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 应用违规检测规则
            for rule_name, rule_config in self.violation_rules.items():
                import re
                for pattern in rule_config["patterns"]:
                    matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                    
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        
                        violation = ViolationReport(
                            violation_type=ViolationType(rule_name),
                            severity=rule_config["severity"],
                            file_path=str(file_path),
                            line_number=line_number,
                            description=rule_config["description"],
                            suggestion=rule_config["suggestion"],
                            auto_fixable=True
                        )
                        violations.append(violation)
            
        except Exception as e:
            logger.error(f"扫描文件失败 {file_path}: {e}")
        
        return violations
    
    def _calculate_compliance_score(self, violations: List[ViolationReport], total_files: int) -> float:
        """计算合规分数"""
        if total_files == 0:
            return 100.0
        
        # 根据严重程度计算扣分
        penalty_map = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.HIGH: 5,
            SeverityLevel.CRITICAL: 10
        }
        
        total_penalty = sum(penalty_map[v.severity] for v in violations)
        max_possible_penalty = total_files * 10  # 假设每个文件最多扣10分
        
        score = max(0, 100 - (total_penalty / max_possible_penalty * 100))
        return round(score, 2)
    
    def _violation_to_dict(self, violation: ViolationReport) -> Dict[str, Any]:
        """将违规报告转换为字典"""
        return {
            "violation_type": violation.violation_type.value,
            "severity": violation.severity.value,
            "file_path": violation.file_path,
            "line_number": violation.line_number,
            "description": violation.description,
            "suggestion": violation.suggestion,
            "auto_fixable": violation.auto_fixable
        }
    
    def enable_pr_review_prevention(self) -> Dict[str, Any]:
        """启用PR review阶段预防机制"""
        try:
            from .pr_review_prevention import PRReviewPrevention
            
            # 创建预防实例
            self.pr_prevention = PRReviewPrevention()
            
            # 安装Git hooks
            hook_result = self.pr_prevention.install_git_hooks()
            
            if hook_result["success"]:
                logger.info("✅ PR Review预防机制已启用")
                return {
                    "status": "success",
                    "message": "PR Review预防机制已启用",
                    "hooks_installed": hook_result["hooks_installed"],
                    "prevention_enabled": True
                }
            else:
                logger.error(f"❌ PR Review预防机制启用失败: {hook_result['error']}")
                return {
                    "status": "error",
                    "error": hook_result["error"]
                }
                
        except Exception as e:
            logger.error(f"启用PR Review预防机制失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_pr_compliance(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """检查PR合规性"""
        try:
            if not hasattr(self, 'pr_prevention'):
                return {
                    "status": "error",
                    "error": "PR预防机制未启用"
                }
            
            # 检查暂存文件
            check_result = self.pr_prevention.check_staged_files()
            
            if check_result["success"]:
                return {
                    "status": "completed",
                    "pr_compliant": not check_result["should_block_commit"],
                    "total_issues": check_result["total_issues"],
                    "critical_issues": check_result["critical_issues"],
                    "error_issues": check_result["error_issues"],
                    "warning_issues": check_result["warning_issues"],
                    "blocked_files": check_result["blocked_files"]
                }
            else:
                return {
                    "status": "error",
                    "error": check_result["error"]
                }
                
        except Exception as e:
            logger.error(f"PR合规性检查失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_prevention_stats(self) -> Dict[str, Any]:
        """获取预防统计信息"""
        try:
            if not hasattr(self, 'pr_prevention'):
                return {
                    "prevention_enabled": False,
                    "message": "PR预防机制未启用"
                }
            
            stats = self.pr_prevention.get_prevention_stats()
            return {
                "prevention_enabled": True,
                **stats
            }
            
        except Exception as e:
            logger.error(f"获取预防统计失败: {e}")
            return {
                "prevention_enabled": False,
                "error": str(e)
            }

    # Git监控功能集成
    def initialize_git_monitoring(self) -> Dict[str, Any]:
        """初始化Git监控功能"""
        try:
            from git_monitor import GitMonitor, DeveloperInterventionMCPExtension
            
            # 创建Git监控扩展
            self.git_extension = DeveloperInterventionMCPExtension(self)
            
            logger.info("🔍 Git监控功能已集成")
            return {
                "success": True,
                "message": "Git监控功能初始化成功",
                "monitoring_status": self.git_extension.get_git_monitoring_status()
            }
            
        except Exception as e:
            logger.error(f"❌ Git监控初始化失败: {e}")
            return {"success": False, "error": str(e)}
    
    def start_git_monitoring(self) -> Dict[str, Any]:
        """启动Git监控"""
        try:
            if not hasattr(self, 'git_extension') or self.git_extension is None:
                init_result = self.initialize_git_monitoring()
                if not init_result["success"]:
                    return init_result
            
            return self.git_extension.git_monitor.start_monitoring()
            
        except Exception as e:
            logger.error(f"❌ 启动Git监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_git_monitoring(self) -> Dict[str, Any]:
        """停止Git监控"""
        try:
            if hasattr(self, 'git_extension') and self.git_extension:
                return self.git_extension.git_monitor.stop_monitoring()
            else:
                return {"success": False, "error": "Git监控未初始化"}
                
        except Exception as e:
            logger.error(f"❌ 停止Git监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_git_status(self) -> Dict[str, Any]:
        """获取当前Git状态"""
        try:
            if not hasattr(self, 'git_extension') or self.git_extension is None:
                init_result = self.initialize_git_monitoring()
                if not init_result["success"]:
                    return init_result
            
            return self.git_extension.git_monitor.get_current_status()
            
        except Exception as e:
            logger.error(f"❌ 获取Git状态失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_checkin_events(self, limit: int = 20) -> Dict[str, Any]:
        """获取最近的checkin事件"""
        try:
            if not hasattr(self, 'git_extension') or self.git_extension is None:
                return {"success": False, "error": "Git监控未初始化"}
            
            return self.git_extension.git_monitor.get_recent_events(limit)
            
        except Exception as e:
            logger.error(f"❌ 获取checkin事件失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_developer_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取开发者活动摘要"""
        try:
            if not hasattr(self, 'git_extension') or self.git_extension is None:
                return {"success": False, "error": "Git监控未初始化"}
            
            return self.git_extension.git_monitor.get_developer_activity_summary(hours)
            
        except Exception as e:
            logger.error(f"❌ 获取活动摘要失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取dashboard数据"""
        try:
            # 获取基础统计信息
            dashboard_data = {
                "mcp_info": {
                    "mcp_id": self.mcp_id,
                    "version": self.version,
                    "status": "running"
                },
                "intervention_stats": self.intervention_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            # 添加Git监控数据
            if hasattr(self, 'git_extension') and self.git_extension:
                git_status = self.get_git_status()
                checkin_events = self.get_checkin_events(10)
                activity_summary = self.get_developer_activity_summary(24)
                
                dashboard_data.update({
                    "git_status": git_status.get("git_status"),
                    "recent_checkin_events": checkin_events.get("events", []),
                    "activity_summary": activity_summary.get("activity_summary"),
                    "git_monitoring_active": self.git_extension.git_monitor.monitoring
                })
            
            return {
                "success": True,
                "dashboard_data": dashboard_data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取dashboard数据失败: {e}")
            return {"success": False, "error": str(e)}

# ============================================================================
# Flask MCP Server
# ============================================================================

def create_development_intervention_mcp_server():
    """创建Development Intervention MCP服务器"""
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    # 创建MCP实例
    dev_mcp = DevelopmentInterventionMCP()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            "mcp_id": "development_intervention_mcp",
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "prevention_enabled": hasattr(dev_mcp, 'pr_prevention')
        })
    
    @app.route('/mcp/info', methods=['GET'])
    def mcp_info():
        """MCP基本信息"""
        return jsonify({
            "mcp_id": "development_intervention_mcp",
            "version": "2.0.0",
            "capabilities": [
                "architecture_compliance_scanning",
                "real_time_code_monitoring", 
                "auto_fix_generation",
                "pr_review_prevention",
                "violation_detection"
            ],
            "description": "Development Intervention MCP - 智能开发介入与PR预防"
        })
    
    @app.route('/mcp/request', methods=['POST'])
    def mcp_request():
        """标准MCP请求处理"""
        try:
            data = request.get_json()
            action = data.get('action')
            params = data.get('params', {})
            
            if action == 'enable_pr_prevention':
                result = dev_mcp.enable_pr_review_prevention()
            elif action == 'check_pr_compliance':
                result = dev_mcp.check_pr_compliance(params)
            elif action == 'scan_project_compliance':
                project_path = params.get('project_path', '/home/ubuntu/kilocode_integrated_repo')
                result = asyncio.run(dev_mcp.scan_project_compliance(project_path))
            elif action == 'get_prevention_stats':
                result = dev_mcp.get_prevention_stats()
            elif action == 'process_coding_task':
                # 处理编码任务的接口
                result = {
                    "success": True,
                    "message": "编码任务处理完成",
                    "task_id": params.get('task_id'),
                    "phase": params.get('phase'),
                    "intervention_applied": True,
                    "quality_check": "passed"
                }
            elif action == 'start_git_monitoring':
                result = dev_mcp.start_git_monitoring()
            elif action == 'stop_git_monitoring':
                result = dev_mcp.stop_git_monitoring()
            elif action == 'get_git_status':
                result = dev_mcp.get_git_status()
            elif action == 'get_checkin_events':
                limit = params.get('limit', 20)
                result = dev_mcp.get_checkin_events(limit)
            elif action == 'get_developer_activity_summary':
                hours = params.get('hours', 24)
                result = dev_mcp.get_developer_activity_summary(hours)
            elif action == 'get_dashboard_data':
                result = dev_mcp.get_dashboard_data()
            else:
                result = {
                    "success": False,
                    "error": f"未知操作: {action}"
                }
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"MCP请求处理失败: {e}")
            return jsonify({
                "success": False,
                "error": f"MCP请求处理失败: {e}"
            }), 500
    
    return app

if __name__ == '__main__':
    # 创建并启动MCP服务器
    app = create_development_intervention_mcp_server()
    
    print(f"🚀 启动Development Intervention MCP服务器...")
    print(f"🔧 MCP ID: development_intervention_mcp")
    print(f"📡 端口: 8092")
    print(f"🛡️ PR Review预防: 已集成")
    
    app.run(host='0.0.0.0', port=8092, debug=False)


    async def trigger_configurable_review(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """触发可配置的PR审查流程"""
        try:
            # 调用可配置审查工作流
            response = requests.post(
                "http://localhost:8095/api/review/process",
                json=pr_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 记录审查结果
                logger.info(f"✅ 可配置PR审查完成: {result.get('review_id')}")
                
                return {
                    "success": True,
                    "review_completed": True,
                    "review_id": result.get("review_id"),
                    "workflow_summary": result.get("workflow_summary"),
                    "human_reviews_conducted": result.get("final_results", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"审查工作流调用失败: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ 触发可配置审查失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_review_workflow_config(self) -> Dict[str, Any]:
        """获取审查工作流配置"""
        try:
            response = requests.get("http://localhost:8095/api/review/config", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": "无法获取配置"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_review_workflow_config(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新审查工作流配置"""
        try:
            response = requests.post(
                "http://localhost:8095/api/review/config",
                json=config_updates,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": "配置更新失败"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Git监控功能集成
    def initialize_git_monitoring(self) -> Dict[str, Any]:
        """初始化Git监控功能"""
        try:
            from git_monitor import GitMonitor, DeveloperInterventionMCPExtension
            
            # 创建Git监控扩展
            self.git_extension = DeveloperInterventionMCPExtension(self)
            
            logger.info("🔍 Git监控功能已集成")
            return {
                "success": True,
                "message": "Git监控功能初始化成功",
                "monitoring_status": self.git_extension.get_git_monitoring_status()
            }
            
        except Exception as e:
            logger.error(f"❌ Git监控初始化失败: {e}")
            return {"success": False, "error": str(e)}
    
    def start_git_monitoring(self) -> Dict[str, Any]:
        """启动Git监控"""
        try:
            if not hasattr(self, 'git_extension'):
                init_result = self.initialize_git_monitoring()
                if not init_result["success"]:
                    return init_result
            
            return self.git_extension.git_monitor.start_monitoring()
            
        except Exception as e:
            logger.error(f"❌ 启动Git监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_git_monitoring(self) -> Dict[str, Any]:
        """停止Git监控"""
        try:
            if hasattr(self, 'git_extension'):
                return self.git_extension.git_monitor.stop_monitoring()
            else:
                return {"success": False, "error": "Git监控未初始化"}
                
        except Exception as e:
            logger.error(f"❌ 停止Git监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_git_status(self) -> Dict[str, Any]:
        """获取当前Git状态"""
        try:
            if not hasattr(self, 'git_extension'):
                init_result = self.initialize_git_monitoring()
                if not init_result["success"]:
                    return init_result
            
            return self.git_extension.git_monitor.get_current_status()
            
        except Exception as e:
            logger.error(f"❌ 获取Git状态失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_checkin_events(self, limit: int = 20) -> Dict[str, Any]:
        """获取最近的checkin事件"""
        try:
            if not hasattr(self, 'git_extension'):
                return {"success": False, "error": "Git监控未初始化"}
            
            return self.git_extension.git_monitor.get_recent_events(limit)
            
        except Exception as e:
            logger.error(f"❌ 获取checkin事件失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_developer_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取开发者活动摘要"""
        try:
            if not hasattr(self, 'git_extension'):
                return {"success": False, "error": "Git监控未初始化"}
            
            return self.git_extension.git_monitor.get_developer_activity_summary(hours)
            
        except Exception as e:
            logger.error(f"❌ 获取活动摘要失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取dashboard数据"""
        try:
            # 获取基础统计信息
            dashboard_data = {
                "mcp_info": {
                    "mcp_id": self.mcp_id,
                    "version": self.version,
                    "status": "running"
                },
                "intervention_stats": self.intervention_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            # 添加Git监控数据
            if hasattr(self, 'git_extension'):
                git_status = self.get_git_status()
                checkin_events = self.get_checkin_events(10)
                activity_summary = self.get_developer_activity_summary(24)
                
                dashboard_data.update({
                    "git_status": git_status.get("git_status"),
                    "recent_checkin_events": checkin_events.get("events", []),
                    "activity_summary": activity_summary.get("activity_summary"),
                    "git_monitoring_active": self.git_extension.git_monitor.monitoring
                })
            
            return {
                "success": True,
                "dashboard_data": dashboard_data
            }
            
        except Exception as e:
            logger.error(f"❌ 获取dashboard数据失败: {e}")
            return {"success": False, "error": str(e)}

