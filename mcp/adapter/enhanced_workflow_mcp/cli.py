#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Workflow MCP CLI
增强型工作流MCP命令行接口

提供增强型工作流引擎的命令行操作接口
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from enhanced_workflow_engine import EnhancedWorkflowEngine
from dynamic_workflow_generator import DynamicWorkflowGenerator
from parallel_execution_scheduler import ParallelExecutionScheduler
from intelligent_dependency_manager import IntelligentDependencyManager
from workflow_state_manager import WorkflowStateManager

class EnhancedWorkflowCLI:
    """增强型工作流CLI"""
    
    def __init__(self):
        self.engine = EnhancedWorkflowEngine()
        self.generator = DynamicWorkflowGenerator()
        self.scheduler = ParallelExecutionScheduler()
        self.dependency_manager = IntelligentDependencyManager()
        self.state_manager = WorkflowStateManager()
    
    async def create_workflow(self, args):
        """创建工作流"""
        try:
            workflow_config = {
                "name": args.name,
                "description": args.description or f"工作流: {args.name}",
                "template_type": args.template or "basic",
                "requirements": args.requirements.split(",") if args.requirements else [],
                "parallel_enabled": args.parallel,
                "optimization_enabled": args.optimize
            }
            
            result = await self.generator.generate_workflow(workflow_config)
            
            if result["status"] == "success":
                print(f"✅ 工作流创建成功: {result['workflow_id']}")
                print(f"📋 节点数量: {result['nodes_count']}")
                print(f"🔗 边数量: {result['edges_count']}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"💾 工作流已保存到: {args.output}")
            else:
                print(f"❌ 工作流创建失败: {result['message']}")
                return 1
                
        except Exception as e:
            print(f"❌ 创建工作流时发生错误: {e}")
            return 1
        
        return 0
    
    async def execute_workflow(self, args):
        """执行工作流"""
        try:
            # 加载工作流
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                workflow_id = workflow_data.get("workflow_id")
            else:
                workflow_id = args.id
            
            if not workflow_id:
                print("❌ 请提供工作流ID或文件")
                return 1
            
            # 执行参数
            execution_config = {
                "workflow_id": workflow_id,
                "execution_mode": args.mode or "auto",
                "parallel_enabled": args.parallel,
                "max_workers": args.workers or 4,
                "timeout": args.timeout or 3600,
                "input_data": json.loads(args.input) if args.input else {}
            }
            
            print(f"🚀 开始执行工作流: {workflow_id}")
            print(f"⚙️ 执行模式: {execution_config['execution_mode']}")
            print(f"👥 最大工作线程: {execution_config['max_workers']}")
            
            result = await self.scheduler.execute_workflow(execution_config)
            
            if result["status"] == "success":
                print(f"✅ 工作流执行成功")
                print(f"⏱️ 执行时间: {result.get('execution_time', 'N/A')}秒")
                print(f"📊 成功节点: {result.get('successful_nodes', 0)}")
                print(f"❌ 失败节点: {result.get('failed_nodes', 0)}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"💾 执行结果已保存到: {args.output}")
            else:
                print(f"❌ 工作流执行失败: {result['message']}")
                return 1
                
        except Exception as e:
            print(f"❌ 执行工作流时发生错误: {e}")
            return 1
        
        return 0
    
    async def analyze_dependencies(self, args):
        """分析依赖关系"""
        try:
            # 加载工作流
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                workflow_id = workflow_data.get("workflow_id")
            else:
                workflow_id = args.id
            
            if not workflow_id:
                print("❌ 请提供工作流ID或文件")
                return 1
            
            # 获取工作流
            workflow = await self.state_manager.get_workflow(workflow_id)
            if not workflow:
                print(f"❌ 工作流不存在: {workflow_id}")
                return 1
            
            print(f"🔍 分析工作流依赖关系: {workflow_id}")
            
            result = await self.dependency_manager.analyze_dependencies(workflow)
            
            if result["status"] == "success":
                analysis = result["analysis"]
                print(f"✅ 依赖分析完成")
                print(f"📊 总节点数: {analysis['total_nodes']}")
                print(f"🔗 总依赖数: {analysis['total_dependencies']}")
                print(f"⚠️ 检测到冲突: {analysis['conflicts_detected']}")
                
                # 显示拓扑排序
                if analysis["topological_order"]:
                    print(f"\n📋 拓扑排序 (分层):")
                    for i, layer in enumerate(analysis["topological_order"]):
                        print(f"  层 {i+1}: {', '.join(layer)}")
                
                # 显示关键路径
                if analysis["critical_paths"]:
                    print(f"\n🎯 关键路径:")
                    for i, path in enumerate(analysis["critical_paths"][:3]):
                        print(f"  路径 {i+1}: {' -> '.join(path['path'])} (权重: {path['weight']})")
                
                # 显示并行机会
                if analysis["parallel_opportunities"]:
                    print(f"\n⚡ 并行执行机会:")
                    for opp in analysis["parallel_opportunities"]:
                        if opp.get("opportunity_type") == "topological_parallelism":
                            print(f"  层 {opp['layer']}: {opp['parallel_count']} 个节点可并行")
                
                # 显示冲突
                if result["conflicts"]:
                    print(f"\n⚠️ 检测到的冲突:")
                    for conflict in result["conflicts"]:
                        print(f"  - {conflict['conflict_type']}: {conflict['description']}")
                
                # 显示优化建议
                if analysis["optimization_suggestions"]:
                    print(f"\n💡 优化建议:")
                    for suggestion in analysis["optimization_suggestions"]:
                        print(f"  - {suggestion}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"\n💾 分析结果已保存到: {args.output}")
            else:
                print(f"❌ 依赖分析失败: {result['message']}")
                return 1
                
        except Exception as e:
            print(f"❌ 分析依赖关系时发生错误: {e}")
            return 1
        
        return 0
    
    async def list_workflows(self, args):
        """列出工作流"""
        try:
            result = await self.state_manager.list_workflows()
            
            if result["status"] == "success":
                workflows = result["workflows"]
                print(f"📋 共找到 {len(workflows)} 个工作流:")
                print()
                
                for workflow in workflows:
                    status_icon = "✅" if workflow["status"] == "completed" else "🔄" if workflow["status"] == "running" else "⏸️"
                    print(f"{status_icon} {workflow['id']}")
                    print(f"   名称: {workflow['name']}")
                    print(f"   状态: {workflow['status']}")
                    print(f"   创建时间: {workflow['created_at']}")
                    print(f"   节点数: {workflow.get('nodes_count', 'N/A')}")
                    print()
            else:
                print(f"❌ 获取工作流列表失败: {result['message']}")
                return 1
                
        except Exception as e:
            print(f"❌ 列出工作流时发生错误: {e}")
            return 1
        
        return 0
    
    async def status(self, args):
        """显示系统状态"""
        try:
            print("📊 增强型工作流引擎状态")
            print("=" * 50)
            
            # 工作流状态
            workflow_status = await self.state_manager.get_system_status()
            print(f"🔧 工作流管理:")
            print(f"   总工作流数: {workflow_status.get('total_workflows', 0)}")
            print(f"   运行中: {workflow_status.get('running_workflows', 0)}")
            print(f"   已完成: {workflow_status.get('completed_workflows', 0)}")
            print(f"   失败: {workflow_status.get('failed_workflows', 0)}")
            
            # 依赖管理状态
            dependency_status = self.dependency_manager.get_dependency_status()
            print(f"\n🔗 依赖管理:")
            print(f"   总节点数: {dependency_status['total_nodes']}")
            print(f"   总边数: {dependency_status['total_edges']}")
            print(f"   冲突数: {dependency_status['conflicts']['total']}")
            print(f"   资源冲突: {dependency_status['resources']['resource_conflicts']}")
            
            # 执行调度状态
            scheduler_status = await self.scheduler.get_scheduler_status()
            print(f"\n⚡ 执行调度:")
            print(f"   活跃执行器: {scheduler_status.get('active_executors', 0)}")
            print(f"   队列中任务: {scheduler_status.get('queued_tasks', 0)}")
            print(f"   总执行次数: {scheduler_status.get('total_executions', 0)}")
            print(f"   成功率: {scheduler_status.get('success_rate', 0):.1f}%")
            
            # 生成器状态
            generator_status = await self.generator.get_generator_status()
            print(f"\n🏗️ 工作流生成:")
            print(f"   可用模板: {generator_status.get('available_templates', 0)}")
            print(f"   生成次数: {generator_status.get('generation_count', 0)}")
            print(f"   缓存命中率: {generator_status.get('cache_hit_rate', 0):.1f}%")
            
        except Exception as e:
            print(f"❌ 获取系统状态时发生错误: {e}")
            return 1
        
        return 0
    
    async def optimize_workflow(self, args):
        """优化工作流"""
        try:
            # 加载工作流
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                workflow_id = workflow_data.get("workflow_id")
            else:
                workflow_id = args.id
            
            if not workflow_id:
                print("❌ 请提供工作流ID或文件")
                return 1
            
            print(f"🔧 优化工作流: {workflow_id}")
            
            optimization_config = {
                "workflow_id": workflow_id,
                "optimization_type": args.type or "auto",
                "enable_parallelization": args.parallel,
                "resolve_conflicts": args.resolve_conflicts,
                "optimize_resources": args.optimize_resources
            }
            
            result = await self.engine.optimize_workflow(optimization_config)
            
            if result["status"] == "success":
                print(f"✅ 工作流优化完成")
                print(f"📈 优化改进:")
                
                improvements = result.get("improvements", {})
                for metric, improvement in improvements.items():
                    print(f"   {metric}: {improvement}")
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f"💾 优化结果已保存到: {args.output}")
            else:
                print(f"❌ 工作流优化失败: {result['message']}")
                return 1
                
        except Exception as e:
            print(f"❌ 优化工作流时发生错误: {e}")
            return 1
        
        return 0

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Enhanced Workflow MCP CLI")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 创建工作流
    create_parser = subparsers.add_parser("create", help="创建工作流")
    create_parser.add_argument("name", help="工作流名称")
    create_parser.add_argument("--description", help="工作流描述")
    create_parser.add_argument("--template", help="模板类型 (basic/professional/composite)")
    create_parser.add_argument("--requirements", help="需求列表 (逗号分隔)")
    create_parser.add_argument("--parallel", action="store_true", help="启用并行执行")
    create_parser.add_argument("--optimize", action="store_true", help="启用自动优化")
    create_parser.add_argument("--output", help="输出文件路径")
    
    # 执行工作流
    execute_parser = subparsers.add_parser("execute", help="执行工作流")
    execute_parser.add_argument("--id", help="工作流ID")
    execute_parser.add_argument("--file", help="工作流文件路径")
    execute_parser.add_argument("--mode", help="执行模式 (auto/manual/debug)")
    execute_parser.add_argument("--parallel", action="store_true", help="启用并行执行")
    execute_parser.add_argument("--workers", type=int, help="最大工作线程数")
    execute_parser.add_argument("--timeout", type=int, help="超时时间(秒)")
    execute_parser.add_argument("--input", help="输入数据 (JSON格式)")
    execute_parser.add_argument("--output", help="输出文件路径")
    
    # 分析依赖
    analyze_parser = subparsers.add_parser("analyze", help="分析依赖关系")
    analyze_parser.add_argument("--id", help="工作流ID")
    analyze_parser.add_argument("--file", help="工作流文件路径")
    analyze_parser.add_argument("--output", help="输出文件路径")
    
    # 列出工作流
    list_parser = subparsers.add_parser("list", help="列出工作流")
    
    # 系统状态
    status_parser = subparsers.add_parser("status", help="显示系统状态")
    
    # 优化工作流
    optimize_parser = subparsers.add_parser("optimize", help="优化工作流")
    optimize_parser.add_argument("--id", help="工作流ID")
    optimize_parser.add_argument("--file", help="工作流文件路径")
    optimize_parser.add_argument("--type", help="优化类型 (auto/performance/resource)")
    optimize_parser.add_argument("--parallel", action="store_true", help="启用并行优化")
    optimize_parser.add_argument("--resolve-conflicts", action="store_true", help="解决冲突")
    optimize_parser.add_argument("--optimize-resources", action="store_true", help="优化资源使用")
    optimize_parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 创建CLI实例并执行命令
    cli = EnhancedWorkflowCLI()
    
    try:
        if args.command == "create":
            return asyncio.run(cli.create_workflow(args))
        elif args.command == "execute":
            return asyncio.run(cli.execute_workflow(args))
        elif args.command == "analyze":
            return asyncio.run(cli.analyze_dependencies(args))
        elif args.command == "list":
            return asyncio.run(cli.list_workflows(args))
        elif args.command == "status":
            return asyncio.run(cli.status(args))
        elif args.command == "optimize":
            return asyncio.run(cli.optimize_workflow(args))
        else:
            print(f"❌ 未知命令: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n⏹️ 操作已取消")
        return 1
    except Exception as e:
        print(f"❌ 执行命令时发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

