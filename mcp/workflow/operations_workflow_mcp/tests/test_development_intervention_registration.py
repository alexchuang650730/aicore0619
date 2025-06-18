#!/usr/bin/env python3
"""
Development Intervention MCP Registration Script
Development Intervention MCP注册脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
repo_root = Path("/home/ubuntu/kilocode_integrated_repo")
sys.path.insert(0, str(repo_root))

from mcp.workflow.operations_workflow_mcp.src.mcp_registry_manager import MCPRegistryManager, MCPType

def register_development_intervention_mcp():
    """注册Development Intervention MCP"""
    
    print("🔧 开始注册Development Intervention MCP...")
    
    # 创建注册管理器
    manager = MCPRegistryManager()
    
    # 自动发现所有MCP
    print("\n🔍 自动发现MCP...")
    discovered = manager.auto_discover_mcps()
    
    print(f"发现的适配器MCP: {len(discovered['adapters'])}")
    for adapter in discovered['adapters']:
        print(f"  - {adapter['name']}: {adapter.get('description', 'No description')}")
    
    print(f"发现的工作流MCP: {len(discovered['workflows'])}")
    for workflow in discovered['workflows']:
        print(f"  - {workflow['name']}: {workflow.get('description', 'No description')}")
    
    # 注册Development Intervention MCP
    dev_intervention_found = False
    for adapter in discovered['adapters']:
        if adapter['name'] == 'development_intervention_mcp':
            dev_intervention_found = True
            
            print(f"\n📝 注册 {adapter['name']}...")
            success = manager.register_mcp(
                name=adapter['name'],
                mcp_type=MCPType.ADAPTER,
                path=adapter['path'],
                class_name=adapter['class_name'] or 'DevelopmentInterventionMCP',
                capabilities=adapter['capabilities'],
                description=adapter['description'] or "智能开发介入MCP，提供代码分析和自动修复功能",
                dependencies=[]
            )
            
            if success:
                print(f"✅ 成功注册 {adapter['name']}")
            else:
                print(f"❌ 注册 {adapter['name']} 失败")
            break
    
    if not dev_intervention_found:
        print("❌ 未找到Development Intervention MCP")
        return False
    
    # 注册其他发现的适配器MCP
    print("\n📝 注册其他适配器MCP...")
    for adapter in discovered['adapters']:
        if adapter['name'] != 'development_intervention_mcp':
            print(f"注册 {adapter['name']}...")
            manager.register_mcp(
                name=adapter['name'],
                mcp_type=MCPType.ADAPTER,
                path=adapter['path'],
                class_name=adapter['class_name'] or f"{adapter['name'].replace('_', '').title()}",
                capabilities=adapter['capabilities'],
                description=adapter['description'] or f"{adapter['name']} 适配器",
                dependencies=[]
            )
    
    # 显示注册状态
    print("\n📊 注册状态...")
    status = manager.get_registry_status()
    print(f"总注册数: {status['total_registered']}")
    print(f"适配器: {status['by_type']['adapter']}")
    print(f"工作流: {status['by_type']['workflow']}")
    
    # 进行健康检查
    print("\n🏥 健康检查...")
    health = manager.health_check_all()
    print(f"检查了 {health['total_checked']} 个MCP")
    print(f"健康: {health['healthy']} 个")
    print(f"不健康: {health['unhealthy']} 个")
    
    if health['unhealthy'] > 0:
        print("\n❌ 不健康的MCP详情:")
        for detail in health['details']:
            if not detail['healthy']:
                print(f"  - {detail['name']}: {detail['status']}")
    
    return True

def test_development_intervention_integration():
    """测试Development Intervention MCP集成"""
    
    print("\n🧪 测试Development Intervention MCP集成...")
    
    manager = MCPRegistryManager()
    
    # 测试加载Development Intervention MCP
    print("📥 加载Development Intervention MCP...")
    dev_mcp = manager.load_mcp('development_intervention_mcp')
    
    if dev_mcp:
        print("✅ 成功加载Development Intervention MCP")
        
        # 测试获取状态
        if hasattr(dev_mcp, 'get_status'):
            status = dev_mcp.get_status()
            print(f"📊 MCP状态: {status}")
        
        # 测试分析介入需求
        if hasattr(dev_mcp, 'analyze_intervention_need'):
            test_scenario = {
                "type": "code_quality_issue",
                "description": "发现代码质量问题",
                "severity": "medium"
            }
            
            result = dev_mcp.analyze_intervention_need(test_scenario)
            print(f"🧠 介入分析结果: {result}")
        
        return True
    else:
        print("❌ 加载Development Intervention MCP失败")
        return False

if __name__ == "__main__":
    print("🚀 Development Intervention MCP 注册和集成测试")
    print("=" * 60)
    
    # 注册MCP
    registration_success = register_development_intervention_mcp()
    
    if registration_success:
        # 测试集成
        integration_success = test_development_intervention_integration()
        
        if integration_success:
            print("\n🎉 Development Intervention MCP 注册和集成测试成功！")
        else:
            print("\n❌ Development Intervention MCP 集成测试失败")
    else:
        print("\n❌ Development Intervention MCP 注册失败")

