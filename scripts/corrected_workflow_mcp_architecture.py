#!/usr/bin/env python3
"""
修正后的六大工作流MCP架构
PPT生成属于需求分析工作流
"""

import json
from typing import Dict, Any, List

class CorrectedWorkflowMCPArchitecture:
    """修正后的六大工作流MCP架构"""
    
    def __init__(self):
        self.workflow_mcps = {
            "requirements_analysis": {
                "mcp_name": "requirements_analysis_mcp",
                "description": "AI理解业务需求，生成技术方案",
                "tasks": ["业务需求分析", "PPT内容规划", "方案生成", "需求文档"],
                "tools": ["business_analyzer", "requirement_parser", "solution_generator", "ppt_planner"],
                "fallback_tools": ["ai_requirement_tool", "smart_analysis_tool"]
            },
            "architecture_design": {
                "mcp_name": "architecture_design_mcp", 
                "description": "智能架构建议，最佳实践推荐",
                "tasks": ["系统架构设计", "技术选型", "设计模式", "最佳实践"],
                "tools": ["architecture_advisor", "pattern_recommender", "best_practice_engine"],
                "fallback_tools": ["smart_architect_tool", "design_pattern_tool"]
            },
            "coding_implementation": {
                "mcp_name": "kilocode_mcp",
                "description": "智能介入(Kilo Code引擎)，AI编程助手",
                "tasks": ["代码生成", "代码优化", "模板生成", "编程实现"],
                "tools": ["code_generator", "smart_completion", "template_engine"],
                "fallback_tools": ["ai_coder_tool", "code_assistant_tool"]
            },
            "testing_verification": {
                "mcp_name": "test_verification_mcp",
                "description": "自动化分布式测试，质量保障",
                "tasks": ["测试用例生成", "自动化测试", "质量检查", "测试报告"],
                "tools": ["test_generator", "quality_checker", "automation_engine"],
                "fallback_tools": ["smart_test_tool", "qa_assistant_tool"]
            },
            "deployment_release": {
                "mcp_name": "deployment_release_mcp",
                "description": "Release Manager + 插件系统",
                "tasks": ["部署管理", "版本发布", "环境配置", "插件管理"],
                "tools": ["release_manager", "deployment_engine", "plugin_system"],
                "fallback_tools": ["deploy_assistant_tool", "release_tool"]
            },
            "monitoring_operations": {
                "mcp_name": "monitoring_ops_mcp",
                "description": "性能监控，问题预警(AdminBoard)",
                "tasks": ["性能监控", "问题预警", "运维管理", "系统分析"],
                "tools": ["performance_monitor", "alert_system", "admin_board"],
                "fallback_tools": ["monitoring_tool", "ops_assistant_tool"]
            }
        }
    
    def get_workflow_for_task(self, task_type: str, content: str) -> str:
        """根据任务类型和内容确定工作流"""
        full_text = f"{task_type} {content}".lower()
        
        # 1. 需求分析工作流 (包括PPT生成)
        requirements_keywords = [
            "需求", "requirement", "分析", "analysis", "业务", "business",
            "ppt", "presentation", "报告", "report", "总结", "summary",
            "年终", "年报", "汇报", "展示", "方案", "规划"
        ]
        if any(keyword in full_text for keyword in requirements_keywords):
            return "requirements_analysis"
        
        # 2. 架构设计工作流
        architecture_keywords = [
            "架构", "architecture", "设计", "design", "模式", "pattern",
            "技术选型", "框架", "framework", "结构", "structure"
        ]
        if any(keyword in full_text for keyword in architecture_keywords):
            return "architecture_design"
        
        # 3. 编码实现工作流 (纯代码相关)
        coding_keywords = [
            "代码", "code", "编程", "programming", "开发", "development",
            "函数", "function", "类", "class", "算法", "algorithm",
            "python", "javascript", "java", "html", "css"
        ]
        if any(keyword in full_text for keyword in coding_keywords):
            return "coding_implementation"
        
        # 4. 测试验证工作流
        testing_keywords = [
            "测试", "test", "验证", "verification", "质量", "quality",
            "检查", "check", "验收", "acceptance"
        ]
        if any(keyword in full_text for keyword in testing_keywords):
            return "testing_verification"
        
        # 5. 部署发布工作流
        deployment_keywords = [
            "部署", "deploy", "发布", "release", "上线", "launch",
            "环境", "environment", "配置", "config"
        ]
        if any(keyword in full_text for keyword in deployment_keywords):
            return "deployment_release"
        
        # 6. 监控运维工作流
        monitoring_keywords = [
            "监控", "monitor", "运维", "ops", "性能", "performance",
            "告警", "alert", "日志", "log", "分析", "analytics"
        ]
        if any(keyword in full_text for keyword in monitoring_keywords):
            return "monitoring_operations"
        
        # 默认选择需求分析工作流 (更合理的默认选择)
        return "requirements_analysis"
    
    def get_mcp_for_workflow(self, workflow: str) -> Dict[str, Any]:
        """获取工作流对应的MCP信息"""
        return self.workflow_mcps.get(workflow, self.workflow_mcps["requirements_analysis"])

if __name__ == "__main__":
    arch = CorrectedWorkflowMCPArchitecture()
    
    # 测试任务路由
    test_cases = [
        ("ppt_generation", "生成华为2024年终端年终PPT"),
        ("business_analysis", "分析华为终端业务需求"),
        ("code_generation", "生成Python代码"),
        ("requirement_analysis", "分析用户需求"),
        ("architecture_design", "设计系统架构"),
        ("testing", "执行自动化测试"),
        ("deployment", "部署到生产环境"),
        ("monitoring", "监控系统性能")
    ]
    
    print("🎯 修正后的六大工作流MCP路由测试")
    print("=" * 60)
    
    for task_type, content in test_cases:
        workflow = arch.get_workflow_for_task(task_type, content)
        mcp_info = arch.get_mcp_for_workflow(workflow)
        print(f"📋 任务: {content}")
        print(f"   → 工作流: {workflow}")
        print(f"   → MCP: {mcp_info['mcp_name']}")
        print(f"   → 描述: {mcp_info['description']}")
        print(f"   → 任务类型: {', '.join(mcp_info['tasks'])}")
        print()

