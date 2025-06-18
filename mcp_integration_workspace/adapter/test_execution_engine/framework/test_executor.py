#!/usr/bin/env python3
"""
PowerAutomation MCP统一测试执行器

基于PowerAutomation测试框架标准，自动发现并执行所有MCP模块的测试。
支持并行测试执行、综合报告生成和错误处理。

作者: Manus AI
版本: 1.0.0
日期: 2025-06-17
"""

import os
import sys
import json
import asyncio
import unittest
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util

class MCPTestExecutor:
    """MCP统一测试执行器"""
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        self.project_root = Path(project_root)
        self.mcp_adapter_path = self.project_root / "mcp" / "adapter"
        self.mcp_workflow_path = self.project_root / "mcp" / "workflow"
        self.test_results = []
        self.execution_start_time = datetime.now()
        
    def discover_all_tests(self) -> List[Dict[str, Any]]:
        """发现所有测试文件"""
        test_modules = []
        
        # 发现适配器测试
        if self.mcp_adapter_path.exists():
            for module_dir in self.mcp_adapter_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    test_modules.extend(self._discover_module_tests(module_dir, 'adapter'))
        
        # 发现工作流测试
        if self.mcp_workflow_path.exists():
            for module_dir in self.mcp_workflow_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    test_modules.extend(self._discover_module_tests(module_dir, 'workflow'))
        
        print(f"✅ 发现 {len(test_modules)} 个测试模块")
        return test_modules
    
    def _discover_module_tests(self, module_dir: Path, module_type: str) -> List[Dict[str, Any]]:
        """发现单个模块的测试"""
        tests = []
        
        # 查找单元测试
        unit_tests_dir = module_dir / 'unit_tests'
        if unit_tests_dir.exists():
            for test_file in unit_tests_dir.glob('test_*.py'):
                tests.append({
                    'module_name': module_dir.name,
                    'module_type': module_type,
                    'test_type': 'unit',
                    'test_file': test_file,
                    'test_path': str(test_file.relative_to(self.project_root))
                })
        
        # 查找集成测试
        integration_tests_dir = module_dir / 'integration_tests'
        if integration_tests_dir.exists():
            for test_file in integration_tests_dir.glob('test_*.py'):
                tests.append({
                    'module_name': module_dir.name,
                    'module_type': module_type,
                    'test_type': 'integration',
                    'test_file': test_file,
                    'test_path': str(test_file.relative_to(self.project_root))
                })
        
        return tests
    
    def execute_single_test(self, test_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个测试"""
        test_start_time = datetime.now()
        module_name = test_info['module_name']
        test_type = test_info['test_type']
        test_file = test_info['test_file']
        
        print(f"🧪 执行测试: {module_name} ({test_type})")
        
        try:
            # 构建测试命令
            cmd = [
                sys.executable, '-m', 'unittest', 
                f"{test_info['test_path'].replace('/', '.').replace('.py', '')}"
            ]
            
            # 执行测试
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            test_end_time = datetime.now()
            test_duration = (test_end_time - test_start_time).total_seconds()
            
            # 解析测试结果
            success = result.returncode == 0
            
            test_result = {
                'module_name': module_name,
                'test_type': test_type,
                'test_file': test_file.name,
                'test_path': test_info['test_path'],
                'status': 'PASS' if success else 'FAIL',
                'duration': test_duration,
                'start_time': test_start_time.isoformat(),
                'end_time': test_end_time.isoformat(),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            if success:
                print(f"✅ {module_name} ({test_type}) - 通过 ({test_duration:.2f}s)")
            else:
                print(f"❌ {module_name} ({test_type}) - 失败 ({test_duration:.2f}s)")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}...")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            test_result = {
                'module_name': module_name,
                'test_type': test_type,
                'test_file': test_file.name,
                'test_path': test_info['test_path'],
                'status': 'TIMEOUT',
                'duration': 300,
                'start_time': test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'stdout': '',
                'stderr': 'Test execution timeout (300s)',
                'return_code': -1
            }
            print(f"⏰ {module_name} ({test_type}) - 超时")
            return test_result
            
        except Exception as e:
            test_result = {
                'module_name': module_name,
                'test_type': test_type,
                'test_file': test_file.name,
                'test_path': test_info['test_path'],
                'status': 'ERROR',
                'duration': 0,
                'start_time': test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'stdout': '',
                'stderr': str(e),
                'return_code': -2
            }
            print(f"💥 {module_name} ({test_type}) - 错误: {e}")
            return test_result
    
    def execute_tests_parallel(self, test_modules: List[Dict[str, Any]], max_workers: int = 4) -> List[Dict[str, Any]]:
        """并行执行测试"""
        print(f"🚀 开始并行执行测试 (最大并发: {max_workers})")
        print("=" * 80)
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有测试任务
            future_to_test = {
                executor.submit(self.execute_single_test, test): test 
                for test in test_modules
            }
            
            # 收集结果
            for future in as_completed(future_to_test):
                test_info = future_to_test[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    error_result = {
                        'module_name': test_info['module_name'],
                        'test_type': test_info['test_type'],
                        'test_file': test_info['test_file'].name,
                        'test_path': test_info['test_path'],
                        'status': 'ERROR',
                        'duration': 0,
                        'start_time': datetime.now().isoformat(),
                        'end_time': datetime.now().isoformat(),
                        'stdout': '',
                        'stderr': f'Execution error: {str(e)}',
                        'return_code': -3
                    }
                    results.append(error_result)
                    print(f"💥 {test_info['module_name']} 执行异常: {e}")
        
        return results
    
    def execute_tests_sequential(self, test_modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """顺序执行测试"""
        print("🚀 开始顺序执行测试")
        print("=" * 80)
        
        results = []
        for test_info in test_modules:
            result = self.execute_single_test(test_info)
            results.append(result)
        
        return results
    
    def generate_comprehensive_report(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成综合测试报告"""
        execution_end_time = datetime.now()
        total_duration = (execution_end_time - self.execution_start_time).total_seconds()
        
        # 统计结果
        total_tests = len(test_results)
        passed_tests = len([r for r in test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in test_results if r['status'] == 'FAIL'])
        timeout_tests = len([r for r in test_results if r['status'] == 'TIMEOUT'])
        error_tests = len([r for r in test_results if r['status'] == 'ERROR'])
        
        # 按模块统计
        module_stats = {}
        for result in test_results:
            module_name = result['module_name']
            if module_name not in module_stats:
                module_stats[module_name] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'timeout': 0,
                    'error': 0
                }
            
            module_stats[module_name]['total'] += 1
            if result['status'] == 'PASS':
                module_stats[module_name]['passed'] += 1
            elif result['status'] == 'FAIL':
                module_stats[module_name]['failed'] += 1
            elif result['status'] == 'TIMEOUT':
                module_stats[module_name]['timeout'] += 1
            elif result['status'] == 'ERROR':
                module_stats[module_name]['error'] += 1
        
        # 按测试类型统计
        type_stats = {}
        for result in test_results:
            test_type = result['test_type']
            if test_type not in type_stats:
                type_stats[test_type] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'timeout': 0,
                    'error': 0
                }
            
            type_stats[test_type]['total'] += 1
            if result['status'] == 'PASS':
                type_stats[test_type]['passed'] += 1
            elif result['status'] == 'FAIL':
                type_stats[test_type]['failed'] += 1
            elif result['status'] == 'TIMEOUT':
                type_stats[test_type]['timeout'] += 1
            elif result['status'] == 'ERROR':
                type_stats[test_type]['error'] += 1
        
        # 生成报告
        comprehensive_report = {
            'test_execution_id': f'MCP_TestExecution_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'execution_summary': {
                'start_time': self.execution_start_time.isoformat(),
                'end_time': execution_end_time.isoformat(),
                'total_duration': total_duration,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'timeout_tests': timeout_tests,
                'error_tests': error_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'module_statistics': module_stats,
            'type_statistics': type_stats,
            'detailed_results': test_results,
            'failed_tests_summary': [
                {
                    'module': r['module_name'],
                    'test_type': r['test_type'],
                    'test_file': r['test_file'],
                    'status': r['status'],
                    'error': r['stderr'][:500] if r['stderr'] else 'No error message'
                }
                for r in test_results if r['status'] in ['FAIL', 'TIMEOUT', 'ERROR']
            ]
        }
        
        return comprehensive_report
    
    def save_report(self, report: Dict[str, Any]) -> Path:
        """保存测试报告"""
        report_filename = f"mcp_comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.project_root / "test" / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report_path
    
    def print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        summary = report['execution_summary']
        
        print("\\n" + "=" * 80)
        print("📊 PowerAutomation MCP测试执行摘要")
        print("=" * 80)
        print(f"⏱️  执行时间: {summary['total_duration']:.2f}秒")
        print(f"📝 总测试数: {summary['total_tests']}")
        print(f"✅ 通过测试: {summary['passed_tests']}")
        print(f"❌ 失败测试: {summary['failed_tests']}")
        print(f"⏰ 超时测试: {summary['timeout_tests']}")
        print(f"💥 错误测试: {summary['error_tests']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        
        # 按模块显示结果
        print("\\n📦 模块测试结果:")
        for module_name, stats in report['module_statistics'].items():
            status_icon = "✅" if stats['failed'] + stats['timeout'] + stats['error'] == 0 else "❌"
            print(f"  {status_icon} {module_name}: {stats['passed']}/{stats['total']} 通过")
        
        # 显示失败的测试
        if report['failed_tests_summary']:
            print("\\n❌ 失败的测试:")
            for failed_test in report['failed_tests_summary']:
                print(f"  - {failed_test['module']} ({failed_test['test_type']}): {failed_test['status']}")
                if failed_test['error']:
                    print(f"    错误: {failed_test['error'][:100]}...")
    
    def run_all_tests(self, parallel: bool = True, max_workers: int = 4) -> bool:
        """运行所有测试"""
        print("🚀 PowerAutomation MCP统一测试执行器")
        print("=" * 80)
        
        # 发现所有测试
        test_modules = self.discover_all_tests()
        
        if not test_modules:
            print("⚠️  没有发现任何测试文件")
            return False
        
        # 执行测试
        if parallel:
            test_results = self.execute_tests_parallel(test_modules, max_workers)
        else:
            test_results = self.execute_tests_sequential(test_modules)
        
        # 生成报告
        comprehensive_report = self.generate_comprehensive_report(test_results)
        
        # 保存报告
        report_path = self.save_report(comprehensive_report)
        
        # 打印摘要
        self.print_summary(comprehensive_report)
        
        print(f"\\n📄 详细报告已保存: {report_path}")
        
        # 返回是否所有测试都通过
        summary = comprehensive_report['execution_summary']
        all_passed = (summary['failed_tests'] + summary['timeout_tests'] + summary['error_tests']) == 0
        
        if all_passed:
            print("\\n🎉 所有测试都通过了!")
        else:
            print("\\n⚠️  有测试失败，请检查详细报告")
        
        return all_passed

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PowerAutomation MCP统一测试执行器')
    parser.add_argument('--sequential', action='store_true', help='顺序执行测试（默认并行）')
    parser.add_argument('--workers', type=int, default=4, help='并行执行的最大工作线程数')
    parser.add_argument('--project-root', default='/opt/powerautomation', help='项目根目录')
    
    args = parser.parse_args()
    
    executor = MCPTestExecutor(args.project_root)
    success = executor.run_all_tests(
        parallel=not args.sequential,
        max_workers=args.workers
    )
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()

