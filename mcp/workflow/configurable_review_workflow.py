#!/usr/bin/env python3
"""
Automated PR Review Workflow with Configurable Human-in-the-Loop
可配置的自动化PR审查工作流
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

logger = logging.getLogger(__name__)

class ReviewSeverity(Enum):
    """审查严重程度"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ReviewType(Enum):
    """审查类型"""
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    CODE_STYLE = "code_style"
    FUNCTIONALITY = "functionality"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"

class HumanLoopDecision(Enum):
    """Human Loop决策"""
    REQUIRED = "required"           # 必须人工审查
    OPTIONAL = "optional"           # 可选人工审查
    AUTO_HANDLE = "auto_handle"     # 自动处理
    SKIP = "skip"                   # 跳过

@dataclass
class ReviewConfig:
    """审查配置"""
    review_type: ReviewType
    severity_threshold: ReviewSeverity
    human_loop_required: bool
    auto_fix_enabled: bool
    notification_enabled: bool
    timeout_minutes: int = 30

@dataclass
class ReviewResult:
    """审查结果"""
    review_id: str
    review_type: ReviewType
    severity: ReviewSeverity
    issues_found: List[Dict[str, Any]]
    auto_fixes_applied: List[Dict[str, Any]]
    human_loop_decision: HumanLoopDecision
    human_feedback: Optional[Dict[str, Any]] = None
    final_status: str = "pending"

class ConfigurableReviewWorkflow:
    """可配置的审查工作流"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "/home/ubuntu/kilocode_integrated_repo/config/review_workflow_config.json"
        self.review_configs = self._load_review_configs()
        self.human_loop_mcp_url = "http://localhost:8094"  # Human-in-the-Loop MCP
        self.dev_intervention_mcp_url = "http://localhost:8092"  # Development Intervention MCP
        
        # 审查统计
        self.review_stats = {
            "total_reviews": 0,
            "auto_handled": 0,
            "human_reviewed": 0,
            "auto_fixes_applied": 0,
            "critical_issues_found": 0
        }
        
        logger.info("🔧 可配置审查工作流初始化完成")
    
    def _load_review_configs(self) -> Dict[str, ReviewConfig]:
        """加载审查配置"""
        default_configs = {
            "architecture_review": ReviewConfig(
                review_type=ReviewType.ARCHITECTURE,
                severity_threshold=ReviewSeverity.HIGH,
                human_loop_required=True,
                auto_fix_enabled=True,
                notification_enabled=True,
                timeout_minutes=45
            ),
            "security_review": ReviewConfig(
                review_type=ReviewType.SECURITY,
                severity_threshold=ReviewSeverity.MEDIUM,
                human_loop_required=True,
                auto_fix_enabled=False,  # 安全问题不自动修复
                notification_enabled=True,
                timeout_minutes=60
            ),
            "code_style_review": ReviewConfig(
                review_type=ReviewType.CODE_STYLE,
                severity_threshold=ReviewSeverity.LOW,
                human_loop_required=False,
                auto_fix_enabled=True,
                notification_enabled=False,
                timeout_minutes=15
            ),
            "functionality_review": ReviewConfig(
                review_type=ReviewType.FUNCTIONALITY,
                severity_threshold=ReviewSeverity.MEDIUM,
                human_loop_required=True,
                auto_fix_enabled=False,
                notification_enabled=True,
                timeout_minutes=30
            ),
            "documentation_review": ReviewConfig(
                review_type=ReviewType.DOCUMENTATION,
                severity_threshold=ReviewSeverity.LOW,
                human_loop_required=False,
                auto_fix_enabled=True,
                notification_enabled=False,
                timeout_minutes=10
            )
        }
        
        # 尝试从文件加载配置
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # 这里可以添加配置解析逻辑
                    logger.info(f"✅ 从文件加载审查配置: {self.config_path}")
        except Exception as e:
            logger.warning(f"⚠️ 无法加载配置文件，使用默认配置: {e}")
        
        return default_configs
    
    async def process_pr_review(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理PR审查流程"""
        try:
            review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"🔍 开始PR审查流程: {review_id}")
            
            # 第一阶段：Development Intervention MCP自动检查
            auto_review_results = await self._run_automated_review(pr_data, review_id)
            
            # 第二阶段：根据配置决定是否需要Human-in-the-Loop
            human_loop_decisions = self._determine_human_loop_requirements(auto_review_results)
            
            # 第三阶段：执行Human-in-the-Loop（如果需要）
            final_results = await self._execute_human_loop_if_needed(
                auto_review_results, 
                human_loop_decisions, 
                review_id
            )
            
            # 更新统计
            self._update_review_stats(final_results)
            
            return {
                "success": True,
                "review_id": review_id,
                "auto_review_results": auto_review_results,
                "human_loop_decisions": human_loop_decisions,
                "final_results": final_results,
                "workflow_summary": self._generate_workflow_summary(final_results)
            }
            
        except Exception as e:
            logger.error(f"❌ PR审查流程失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_automated_review(self, pr_data: Dict[str, Any], review_id: str) -> List[ReviewResult]:
        """运行自动化审查"""
        results = []
        
        # 对每种审查类型运行检查
        for config_name, config in self.review_configs.items():
            try:
                # 调用Development Intervention MCP进行检查
                review_response = await self._call_dev_intervention_mcp(
                    "perform_review",
                    {
                        "review_id": review_id,
                        "review_type": config.review_type.value,
                        "pr_data": pr_data,
                        "config": {
                            "severity_threshold": config.severity_threshold.value,
                            "auto_fix_enabled": config.auto_fix_enabled
                        }
                    }
                )
                
                if review_response.get("success"):
                    result = ReviewResult(
                        review_id=f"{review_id}_{config.review_type.value}",
                        review_type=config.review_type,
                        severity=ReviewSeverity(review_response.get("max_severity", "low")),
                        issues_found=review_response.get("issues", []),
                        auto_fixes_applied=review_response.get("auto_fixes", []),
                        human_loop_decision=HumanLoopDecision.REQUIRED  # 待决定
                    )
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"❌ {config_name} 审查失败: {e}")
        
        return results
    
    def _determine_human_loop_requirements(self, review_results: List[ReviewResult]) -> Dict[str, HumanLoopDecision]:
        """根据配置确定Human-in-the-Loop需求"""
        decisions = {}
        
        for result in review_results:
            config = self.review_configs.get(f"{result.review_type.value}_review")
            if not config:
                continue
            
            decision = HumanLoopDecision.AUTO_HANDLE
            
            # 根据严重程度决定
            if result.severity == ReviewSeverity.CRITICAL:
                decision = HumanLoopDecision.REQUIRED
            elif result.severity == ReviewSeverity.HIGH:
                if config.human_loop_required:
                    decision = HumanLoopDecision.REQUIRED
                else:
                    decision = HumanLoopDecision.OPTIONAL
            elif result.severity in [ReviewSeverity.MEDIUM, ReviewSeverity.LOW]:
                if config.human_loop_required and len(result.issues_found) > 0:
                    decision = HumanLoopDecision.OPTIONAL
                else:
                    decision = HumanLoopDecision.AUTO_HANDLE
            
            # 特殊规则
            if result.review_type == ReviewType.SECURITY and len(result.issues_found) > 0:
                decision = HumanLoopDecision.REQUIRED  # 安全问题必须人工审查
            
            if result.review_type == ReviewType.CODE_STYLE and result.severity == ReviewSeverity.LOW:
                decision = HumanLoopDecision.AUTO_HANDLE  # 代码风格问题自动处理
            
            decisions[result.review_id] = decision
            result.human_loop_decision = decision
        
        return decisions
    
    async def _execute_human_loop_if_needed(
        self, 
        review_results: List[ReviewResult], 
        decisions: Dict[str, HumanLoopDecision],
        review_id: str
    ) -> List[ReviewResult]:
        """根据需要执行Human-in-the-Loop"""
        
        for result in review_results:
            decision = decisions.get(result.review_id, HumanLoopDecision.AUTO_HANDLE)
            
            if decision == HumanLoopDecision.REQUIRED:
                # 必须人工审查
                human_feedback = await self._request_human_review(result, required=True)
                result.human_feedback = human_feedback
                result.final_status = "human_reviewed"
                
            elif decision == HumanLoopDecision.OPTIONAL:
                # 可选人工审查 - 可以设置超时自动处理
                human_feedback = await self._request_human_review(result, required=False, timeout=300)
                if human_feedback:
                    result.human_feedback = human_feedback
                    result.final_status = "human_reviewed"
                else:
                    result.final_status = "auto_handled_timeout"
                    
            elif decision == HumanLoopDecision.AUTO_HANDLE:
                # 自动处理
                result.final_status = "auto_handled"
                
            else:  # SKIP
                result.final_status = "skipped"
        
        return review_results
    
    async def _request_human_review(
        self, 
        result: ReviewResult, 
        required: bool = True, 
        timeout: int = 1800
    ) -> Optional[Dict[str, Any]]:
        """请求人工审查"""
        try:
            # 准备人工审查的数据
            review_data = {
                "review_id": result.review_id,
                "review_type": result.review_type.value,
                "severity": result.severity.value,
                "issues_count": len(result.issues_found),
                "auto_fixes_count": len(result.auto_fixes_applied),
                "issues_summary": self._generate_issues_summary(result.issues_found),
                "required": required,
                "timeout_seconds": timeout
            }
            
            # 调用Human-in-the-Loop MCP
            response = await self._call_human_loop_mcp(
                "request_code_review",
                review_data
            )
            
            if response.get("success") and not response.get("cancelled"):
                return {
                    "reviewer": response.get("reviewer", "unknown"),
                    "decision": response.get("decision", "approved"),
                    "comments": response.get("comments", ""),
                    "additional_fixes": response.get("additional_fixes", []),
                    "timestamp": datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 人工审查请求失败: {e}")
            return None
    
    def _generate_issues_summary(self, issues: List[Dict[str, Any]]) -> str:
        """生成问题摘要"""
        if not issues:
            return "未发现问题"
        
        summary_parts = []
        issue_types = {}
        
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type not in issue_types:
                issue_types[issue_type] = 0
            issue_types[issue_type] += 1
        
        for issue_type, count in issue_types.items():
            summary_parts.append(f"{issue_type}: {count}个")
        
        return f"发现 {len(issues)} 个问题 - " + ", ".join(summary_parts)
    
    async def _call_dev_intervention_mcp(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用Development Intervention MCP"""
        try:
            response = requests.post(
                f"{self.dev_intervention_mcp_url}/mcp/request",
                json={"action": action, "params": params},
                timeout=30
            )
            return response.json() if response.status_code == 200 else {"success": False}
        except Exception as e:
            logger.error(f"调用Development Intervention MCP失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def _call_human_loop_mcp(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用Human-in-the-Loop MCP"""
        try:
            response = requests.post(
                f"{self.human_loop_mcp_url}/mcp/request",
                json={"action": action, "params": params},
                timeout=60
            )
            return response.json() if response.status_code == 200 else {"success": False}
        except Exception as e:
            logger.error(f"调用Human-in-the-Loop MCP失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _update_review_stats(self, results: List[ReviewResult]):
        """更新审查统计"""
        self.review_stats["total_reviews"] += len(results)
        
        for result in results:
            if result.final_status.startswith("auto_handled"):
                self.review_stats["auto_handled"] += 1
            elif result.final_status == "human_reviewed":
                self.review_stats["human_reviewed"] += 1
            
            self.review_stats["auto_fixes_applied"] += len(result.auto_fixes_applied)
            
            if result.severity == ReviewSeverity.CRITICAL:
                self.review_stats["critical_issues_found"] += len(result.issues_found)
    
    def _generate_workflow_summary(self, results: List[ReviewResult]) -> Dict[str, Any]:
        """生成工作流摘要"""
        total_issues = sum(len(r.issues_found) for r in results)
        total_fixes = sum(len(r.auto_fixes_applied) for r in results)
        human_reviews = sum(1 for r in results if r.final_status == "human_reviewed")
        
        return {
            "total_review_types": len(results),
            "total_issues_found": total_issues,
            "total_auto_fixes": total_fixes,
            "human_reviews_conducted": human_reviews,
            "automation_rate": round((len(results) - human_reviews) / len(results) * 100, 2) if results else 0,
            "overall_status": "completed",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_review_stats(self) -> Dict[str, Any]:
        """获取审查统计"""
        return {
            **self.review_stats,
            "automation_rate": round(
                self.review_stats["auto_handled"] / max(self.review_stats["total_reviews"], 1) * 100, 2
            ),
            "human_intervention_rate": round(
                self.review_stats["human_reviewed"] / max(self.review_stats["total_reviews"], 1) * 100, 2
            )
        }
    
    def update_config(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        try:
            for config_name, updates in config_updates.items():
                if config_name in self.review_configs:
                    config = self.review_configs[config_name]
                    
                    if "human_loop_required" in updates:
                        config.human_loop_required = updates["human_loop_required"]
                    if "auto_fix_enabled" in updates:
                        config.auto_fix_enabled = updates["auto_fix_enabled"]
                    if "severity_threshold" in updates:
                        config.severity_threshold = ReviewSeverity(updates["severity_threshold"])
            
            return {"success": True, "message": "配置更新成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# ============================================================================
# Flask MCP Server
# ============================================================================

def create_configurable_review_workflow_server():
    """创建可配置审查工作流服务器"""
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    # 创建工作流实例
    workflow = ConfigurableReviewWorkflow()
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            "service": "configurable_review_workflow",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })
    
    @app.route('/api/review/process', methods=['POST'])
    def process_review():
        """处理PR审查"""
        try:
            pr_data = request.get_json()
            result = asyncio.run(workflow.process_pr_review(pr_data))
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route('/api/review/stats', methods=['GET'])
    def get_stats():
        """获取审查统计"""
        return jsonify(workflow.get_review_stats())
    
    @app.route('/api/review/config', methods=['GET'])
    def get_config():
        """获取当前配置"""
        config_data = {}
        for name, config in workflow.review_configs.items():
            config_data[name] = {
                "review_type": config.review_type.value,
                "severity_threshold": config.severity_threshold.value,
                "human_loop_required": config.human_loop_required,
                "auto_fix_enabled": config.auto_fix_enabled,
                "notification_enabled": config.notification_enabled,
                "timeout_minutes": config.timeout_minutes
            }
        return jsonify({"success": True, "configs": config_data})
    
    @app.route('/api/review/config', methods=['POST'])
    def update_config():
        """更新配置"""
        try:
            config_updates = request.get_json()
            result = workflow.update_config(config_updates)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    return app

if __name__ == '__main__':
    # 创建并启动可配置审查工作流服务器
    app = create_configurable_review_workflow_server()
    
    print(f"🚀 启动可配置审查工作流服务器...")
    print(f"🔧 服务: Configurable Review Workflow")
    print(f"📡 端口: 8095")
    print(f"🎯 功能: 可配置的自动化PR审查 + Human-in-the-Loop")
    
    app.run(host='0.0.0.0', port=8095, debug=False)

