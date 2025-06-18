#!/usr/bin/env python3
"""
六大工作流中kilocode兜底机制的测试用例设计
"""

import json
from typing import Dict, Any, List

class KiloCodeWorkflowTestCases:
    """六大工作流中kilocode兜底的测试用例"""
    
    def __init__(self):
        self.test_cases = {
            "requirements_analysis": {
                "workflow_name": "需求分析工作流",
                "primary_mcp": "requirements_analysis_mcp",
                "fallback_scenarios": [
                    {
                        "case_id": "REQ_001",
                        "case_name": "PPT生成兜底",
                        "description": "需求分析MCP找不到PPT生成工具时，kilocode兜底生成PPT代码",
                        "input": {
                            "type": "ppt_generation",
                            "content": "生成华为2024年终端年终PPT",
                            "session_id": "req_ppt_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "PPT生成代码或HTML展示"
                    },
                    {
                        "case_id": "REQ_002", 
                        "case_name": "需求文档生成兜底",
                        "description": "需求分析MCP找不到文档工具时，kilocode兜底生成文档代码",
                        "input": {
                            "type": "document_generation",
                            "content": "生成产品需求文档PRD",
                            "session_id": "req_doc_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "文档生成代码或Markdown"
                    }
                ]
            },
            
            "architecture_design": {
                "workflow_name": "架构设计工作流",
                "primary_mcp": "architecture_design_mcp",
                "fallback_scenarios": [
                    {
                        "case_id": "ARCH_001",
                        "case_name": "架构图生成兜底",
                        "description": "架构设计MCP找不到绘图工具时，kilocode兜底生成图表代码",
                        "input": {
                            "type": "architecture_diagram",
                            "content": "设计微服务架构图",
                            "session_id": "arch_diagram_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "架构图生成代码(Mermaid/PlantUML)"
                    },
                    {
                        "case_id": "ARCH_002",
                        "case_name": "设计模式代码兜底",
                        "description": "架构设计MCP找不到模式工具时，kilocode兜底生成设计模式代码",
                        "input": {
                            "type": "design_pattern",
                            "content": "实现工厂模式",
                            "session_id": "arch_pattern_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "设计模式实现代码"
                    }
                ]
            },
            
            "coding_implementation": {
                "workflow_name": "编码实现工作流",
                "primary_mcp": "kilocode_mcp",
                "fallback_scenarios": [
                    {
                        "case_id": "CODE_001",
                        "case_name": "直接代码生成",
                        "description": "编码工作流直接使用kilocode_mcp生成代码",
                        "input": {
                            "type": "code_generation",
                            "content": "生成Python Flask API",
                            "session_id": "code_direct_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "Flask API代码"
                    },
                    {
                        "case_id": "CODE_002",
                        "case_name": "代码优化兜底",
                        "description": "编码工作流找不到优化工具时，kilocode兜底优化代码",
                        "input": {
                            "type": "code_optimization",
                            "content": "优化Python性能代码",
                            "session_id": "code_optimize_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "optimize_code",
                        "expected_output": "优化后的代码"
                    }
                ]
            },
            
            "testing_verification": {
                "workflow_name": "测试验证工作流",
                "primary_mcp": "test_verification_mcp",
                "fallback_scenarios": [
                    {
                        "case_id": "TEST_001",
                        "case_name": "测试脚本生成兜底",
                        "description": "测试验证MCP找不到测试工具时，kilocode兜底生成测试脚本",
                        "input": {
                            "type": "test_script_generation",
                            "content": "生成API自动化测试脚本",
                            "session_id": "test_script_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "自动化测试脚本"
                    },
                    {
                        "case_id": "TEST_002",
                        "case_name": "测试数据生成兜底",
                        "description": "测试验证MCP找不到数据工具时，kilocode兜底生成测试数据",
                        "input": {
                            "type": "test_data_generation",
                            "content": "生成用户测试数据",
                            "session_id": "test_data_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "测试数据生成代码"
                    }
                ]
            },
            
            "deployment_release": {
                "workflow_name": "部署发布工作流",
                "primary_mcp": "deployment_release_mcp",
                "fallback_scenarios": [
                    {
                        "case_id": "DEPLOY_001",
                        "case_name": "部署脚本生成兜底",
                        "description": "部署发布MCP找不到部署工具时，kilocode兜底生成部署脚本",
                        "input": {
                            "type": "deployment_script",
                            "content": "生成Docker部署脚本",
                            "session_id": "deploy_script_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "Docker部署脚本"
                    },
                    {
                        "case_id": "DEPLOY_002",
                        "case_name": "CI/CD配置兜底",
                        "description": "部署发布MCP找不到CI/CD工具时，kilocode兜底生成配置",
                        "input": {
                            "type": "cicd_configuration",
                            "content": "生成GitHub Actions配置",
                            "session_id": "cicd_config_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "CI/CD配置文件"
                    }
                ]
            },
            
            "monitoring_operations": {
                "workflow_name": "监控运维工作流",
                "primary_mcp": "monitoring_ops_mcp",
                "fallback_scenarios": [
                    {
                        "case_id": "MONITOR_001",
                        "case_name": "监控脚本生成兜底",
                        "description": "监控运维MCP找不到监控工具时，kilocode兜底生成监控脚本",
                        "input": {
                            "type": "monitoring_script",
                            "content": "生成系统性能监控脚本",
                            "session_id": "monitor_script_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "性能监控脚本"
                    },
                    {
                        "case_id": "MONITOR_002",
                        "case_name": "告警配置兜底",
                        "description": "监控运维MCP找不到告警工具时，kilocode兜底生成告警配置",
                        "input": {
                            "type": "alert_configuration",
                            "content": "生成Prometheus告警规则",
                            "session_id": "alert_config_test"
                        },
                        "expected_fallback": "kilocode_mcp",
                        "expected_action": "generate_code",
                        "expected_output": "告警规则配置"
                    }
                ]
            }
        }
    
    def get_all_test_cases(self) -> List[Dict[str, Any]]:
        """获取所有测试用例的扁平列表"""
        all_cases = []
        for workflow, workflow_data in self.test_cases.items():
            for scenario in workflow_data["fallback_scenarios"]:
                test_case = {
                    "workflow": workflow,
                    "workflow_name": workflow_data["workflow_name"],
                    "primary_mcp": workflow_data["primary_mcp"],
                    **scenario
                }
                all_cases.append(test_case)
        return all_cases
    
    def get_test_cases_by_workflow(self, workflow: str) -> List[Dict[str, Any]]:
        """获取特定工作流的测试用例"""
        if workflow in self.test_cases:
            return self.test_cases[workflow]["fallback_scenarios"]
        return []
    
    def print_test_cases_summary(self):
        """打印测试用例摘要"""
        print("🎯 六大工作流kilocode兜底测试用例")
        print("=" * 60)
        
        total_cases = 0
        for workflow, workflow_data in self.test_cases.items():
            print(f"\n📋 {workflow_data['workflow_name']} ({workflow})")
            print(f"   主要MCP: {workflow_data['primary_mcp']}")
            print(f"   兜底场景: {len(workflow_data['fallback_scenarios'])}个")
            
            for i, scenario in enumerate(workflow_data['fallback_scenarios'], 1):
                print(f"   {i}. {scenario['case_id']}: {scenario['case_name']}")
                print(f"      描述: {scenario['description']}")
                print(f"      期望兜底: {scenario['expected_fallback']}")
                print(f"      期望输出: {scenario['expected_output']}")
                total_cases += 1
        
        print(f"\n📊 总计: {total_cases}个测试用例")
        return total_cases

if __name__ == "__main__":
    test_cases = KiloCodeWorkflowTestCases()
    total = test_cases.print_test_cases_summary()
    
    # 保存测试用例到文件
    all_cases = test_cases.get_all_test_cases()
    with open("/home/ubuntu/kilocode_workflow_test_cases.json", "w", encoding="utf-8") as f:
        json.dump(all_cases, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试用例已保存到: /home/ubuntu/kilocode_workflow_test_cases.json")

