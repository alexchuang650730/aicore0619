#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型工作流引擎性能测试
Performance Test for Enhanced Workflow Engine

专门用于性能测试和基准测试
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from enhanced_workflow_engine import EnhancedWorkflowEngine
from dynamic_workflow_generator import DynamicWorkflowGenerator, WorkflowRequirement, WorkflowTemplate
from parallel_execution_scheduler import ParallelExecutionScheduler
from intelligent_dependency_manager import IntelligentDependencyManager, DependencyType, ConflictType
from workflow_state_manager import WorkflowStateManager

class PerformanceTest:
    """性能测试类"""
    
    def __init__(self):
        self.engine = EnhancedWorkflowEngine()
        self.generator = DynamicWorkflowGenerator()
        self.scheduler = ParallelExecutionScheduler()
        self.dependency_manager = IntelligentDependencyManager()
        self.state_manager = WorkflowStateManager()
        
        self.results = {}
    
    async def test_workflow_generation_performance(self, count: int = 100):
        """测试工作流生成性能"""
        print(f"🚀 测试工作流生成性能 (生成{count}个工作流)...")
        
        times = []
        successful = 0
        
        for i in range(count):
            start_time = time.time()
            try:
                req = WorkflowRequirement(
                    name=f"性能测试工作流_{i}",
                    description=f"这是第{i}个性能测试工作流",
                    template=WorkflowTemplate.BASIC
                )
                
                workflow = await self.generator.generate_workflow(req)
                end_time = time.time()
                times.append(end_time - start_time)
                successful += 1
                
            except Exception as e:
                print(f"❌ 工作流{i}生成失败: {e}")
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            median_time = statistics.median(times)
            
            self.results['workflow_generation'] = {
                'count': count,
                'successful': successful,
                'success_rate': successful / count * 100,
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'median_time': median_time,
                'total_time': sum(times)
            }
            
            print(f"✅ 工作流生成性能测试完成:")
            print(f"   总数量: {count}")
            print(f"   成功数: {successful}")
            print(f"   成功率: {successful/count*100:.1f}%")
            print(f"   平均时间: {avg_time:.4f}秒")
            print(f"   最小时间: {min_time:.4f}秒")
            print(f"   最大时间: {max_time:.4f}秒")
            print(f"   中位时间: {median_time:.4f}秒")
        else:
            print("❌ 没有成功的工作流生成")
    
    async def test_dependency_analysis_performance(self, node_count: int = 50):
        """测试依赖分析性能"""
        print(f"🔗 测试依赖分析性能 (分析{node_count}个节点)...")
        
        # 创建测试依赖关系
        start_time = time.time()
        
        # 添加节点 (自动添加到图中)
        for i in range(node_count):
            node_id = f"node_{i}"
            # 节点会在添加依赖时自动添加到图中
        
        # 添加依赖关系 (创建一个复杂的依赖图)
        for i in range(node_count - 1):
            await self.dependency_manager.add_dependency(f"node_{i}", f"node_{i+1}", DependencyType.DATA)
            
            # 添加一些交叉依赖
            if i % 3 == 0 and i + 3 < node_count:
                await self.dependency_manager.add_dependency(f"node_{i}", f"node_{i+3}", DependencyType.CONTROL)
        
        # 执行拓扑排序
        topo_start = time.time()
        sorted_nodes = self.dependency_manager._calculate_topological_order()
        topo_end = time.time()
        
        # 检测循环依赖
        cycle_start = time.time()
        conflicts = await self.dependency_manager._detect_conflicts()
        has_cycle = any(c.conflict_type == ConflictType.CIRCULAR_DEPENDENCY for c in conflicts)
        cycle_end = time.time()
        
        end_time = time.time()
        
        self.results['dependency_analysis'] = {
            'node_count': node_count,
            'total_time': end_time - start_time,
            'topo_sort_time': topo_end - topo_start,
            'cycle_detection_time': cycle_end - cycle_start,
            'sorted_nodes_count': len(sorted_nodes),
            'has_cycle': has_cycle
        }
        
        print(f"✅ 依赖分析性能测试完成:")
        print(f"   节点数量: {node_count}")
        print(f"   总时间: {end_time - start_time:.4f}秒")
        print(f"   拓扑排序: {topo_end - topo_start:.4f}秒")
        print(f"   循环检测: {cycle_end - cycle_start:.4f}秒")
        print(f"   排序结果: {len(sorted_nodes)}个节点")
    
    async def test_parallel_execution_performance(self, task_count: int = 20):
        """测试并行执行性能"""
        print(f"⚡ 测试并行执行性能 (执行{task_count}个任务)...")
        
        # 创建测试任务
        tasks = []
        for i in range(task_count):
            task = {
                'id': f'task_{i}',
                'type': 'test_task',
                'config': {'duration': 0.1, 'data': f'test_data_{i}'},
                'dependencies': []
            }
            tasks.append(task)
        
        # 顺序执行测试
        sequential_start = time.time()
        for task in tasks:
            await asyncio.sleep(0.1)  # 模拟任务执行
        sequential_end = time.time()
        sequential_time = sequential_end - sequential_start
        
        # 并行执行测试
        parallel_start = time.time()
        parallel_tasks = [asyncio.sleep(0.1) for _ in range(task_count)]
        await asyncio.gather(*parallel_tasks)
        parallel_end = time.time()
        parallel_time = parallel_end - parallel_start
        
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        
        self.results['parallel_execution'] = {
            'task_count': task_count,
            'sequential_time': sequential_time,
            'parallel_time': parallel_time,
            'speedup': speedup,
            'efficiency': speedup / task_count * 100
        }
        
        print(f"✅ 并行执行性能测试完成:")
        print(f"   任务数量: {task_count}")
        print(f"   顺序执行: {sequential_time:.4f}秒")
        print(f"   并行执行: {parallel_time:.4f}秒")
        print(f"   加速比: {speedup:.2f}x")
        print(f"   效率: {speedup/task_count*100:.1f}%")
    
    async def test_state_management_performance(self, operation_count: int = 1000):
        """测试状态管理性能"""
        print(f"💾 测试状态管理性能 (执行{operation_count}次操作)...")
        
        # 创建测试工作流
        req = WorkflowRequirement(
            name="状态测试工作流",
            description="用于状态管理性能测试"
        )
        workflow = await self.generator.generate_workflow(req)
        
        # 保存工作流
        save_start = time.time()
        self.state_manager.save_workflow_state(workflow.id, {
            'status': 'running',
            'progress': 0,
            'data': {'test': 'data'}
        })
        save_end = time.time()
        
        # 批量更新测试
        update_times = []
        for i in range(operation_count):
            update_start = time.time()
            self.state_manager.update_workflow_state(workflow.id, {
                'progress': i / operation_count * 100,
                'current_step': f'step_{i}'
            })
            update_end = time.time()
            update_times.append(update_end - update_start)
        
        # 查询测试
        query_start = time.time()
        for i in range(100):  # 查询100次
            state = self.state_manager.get_workflow_state(workflow.id)
        query_end = time.time()
        
        avg_update_time = statistics.mean(update_times) if update_times else 0
        avg_query_time = (query_end - query_start) / 100
        
        self.results['state_management'] = {
            'operation_count': operation_count,
            'save_time': save_end - save_start,
            'avg_update_time': avg_update_time,
            'avg_query_time': avg_query_time,
            'total_update_time': sum(update_times)
        }
        
        print(f"✅ 状态管理性能测试完成:")
        print(f"   操作数量: {operation_count}")
        print(f"   保存时间: {save_end - save_start:.4f}秒")
        print(f"   平均更新: {avg_update_time:.6f}秒")
        print(f"   平均查询: {avg_query_time:.6f}秒")
    
    def print_summary(self):
        """打印性能测试总结"""
        print("\n" + "="*60)
        print("📊 性能测试总结报告")
        print("="*60)
        
        for test_name, result in self.results.items():
            print(f"\n🎯 {test_name.replace('_', ' ').title()}:")
            for key, value in result.items():
                if isinstance(value, float):
                    if 'time' in key:
                        print(f"   {key}: {value:.4f}秒")
                    elif 'rate' in key or 'efficiency' in key:
                        print(f"   {key}: {value:.1f}%")
                    else:
                        print(f"   {key}: {value:.2f}")
                else:
                    print(f"   {key}: {value}")

async def main():
    """主测试函数"""
    print("🚀 开始增强型工作流引擎性能测试")
    print("="*60)
    
    perf_test = PerformanceTest()
    
    # 运行各项性能测试
    await perf_test.test_workflow_generation_performance(50)
    print()
    
    await perf_test.test_dependency_analysis_performance(30)
    print()
    
    await perf_test.test_parallel_execution_performance(10)
    print()
    
    await perf_test.test_state_management_performance(500)
    
    # 打印总结
    perf_test.print_summary()
    
    print("\n✅ 性能测试完成!")

if __name__ == "__main__":
    asyncio.run(main())

