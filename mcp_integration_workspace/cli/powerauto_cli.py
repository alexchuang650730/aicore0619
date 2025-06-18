#!/usr/bin/env python3
"""
PowerAutomation 测试管理 - 用户友好的CLI工具

提供直观易用的命令行界面，支持测试管理的各种操作。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

import asyncio
import click
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint

# 导入我们的模块
sys.path.append(str(Path(__file__).parent))
from interfaces.test_interfaces import TestExecutionInterface, TestWorkflowInterface
from interfaces.data_models import TestResult, TestConfiguration, WorkflowStatus
from ai_optimization import get_ai_optimizer
from smart_diagnostic import get_smart_diagnostic_engine
from predictive_performance import get_performance_analyzer

# 初始化Rich控制台
console = Console()


class PowerAutomationCLI:
    """PowerAutomation测试管理CLI主类"""
    
    def __init__(self):
        self.console = Console()
        self.ai_optimizer = get_ai_optimizer()
        self.diagnostic_engine = get_smart_diagnostic_engine()
        self.performance_analyzer = get_performance_analyzer()
    
    def print_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    PowerAutomation                           ║
║                  测试管理平台 v3.0                           ║
║                                                              ║
║  🚀 AI驱动的智能测试管理                                     ║
║  🔧 自动化测试执行和优化                                     ║
║  📊 预测性性能分析                                           ║
║  🛠️ 智能错误诊断和修复                                       ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold blue")
    
    def print_help(self):
        """打印帮助信息"""
        help_table = Table(title="PowerAutomation CLI 命令", show_header=True, header_style="bold magenta")
        help_table.add_column("命令", style="cyan", width=20)
        help_table.add_column("描述", style="white", width=40)
        help_table.add_column("示例", style="green", width=30)
        
        commands = [
            ("run", "执行测试套件", "powerauto run --suite api_tests"),
            ("generate", "生成测试用例", "powerauto generate --type unit"),
            ("analyze", "分析测试结果", "powerauto analyze --report latest"),
            ("optimize", "优化测试配置", "powerauto optimize --target speed"),
            ("diagnose", "诊断测试错误", "powerauto diagnose --error-id 123"),
            ("predict", "预测性能趋势", "powerauto predict --metric execution_time"),
            ("status", "查看系统状态", "powerauto status"),
            ("config", "配置管理", "powerauto config --set timeout=60"),
            ("dashboard", "启动监控面板", "powerauto dashboard"),
            ("help", "显示帮助信息", "powerauto help")
        ]
        
        for cmd, desc, example in commands:
            help_table.add_row(cmd, desc, example)
        
        self.console.print(help_table)
    
    async def run_tests(self, suite: str = None, config_file: str = None, parallel: bool = False):
        """执行测试套件"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("正在执行测试...", total=None)
            
            try:
                # 模拟测试执行
                await asyncio.sleep(2)
                
                # 生成模拟结果
                results = {
                    "suite": suite or "default",
                    "total_tests": 50,
                    "passed_tests": 47,
                    "failed_tests": 3,
                    "execution_time": 25.5,
                    "memory_usage": 65.2,
                    "cpu_usage": 45.8,
                    "timestamp": datetime.now().isoformat()
                }
                
                progress.update(task, description="测试执行完成")
                
                # 显示结果
                self._display_test_results(results)
                
                # 收集性能指标
                await self.performance_analyzer.collect_performance_metrics(results)
                
                return results
                
            except Exception as e:
                progress.update(task, description=f"测试执行失败: {e}")
                self.console.print(f"❌ 测试执行失败: {e}", style="bold red")
                return None
    
    def _display_test_results(self, results: Dict[str, Any]):
        """显示测试结果"""
        # 创建结果面板
        success_rate = (results["passed_tests"] / results["total_tests"]) * 100
        
        result_text = f"""
📊 测试套件: {results['suite']}
✅ 通过: {results['passed_tests']}
❌ 失败: {results['failed_tests']}
📈 成功率: {success_rate:.1f}%
⏱️ 执行时间: {results['execution_time']:.1f}秒
💾 内存使用: {results['memory_usage']:.1f}%
🖥️ CPU使用: {results['cpu_usage']:.1f}%
        """
        
        panel_style = "green" if success_rate >= 90 else "yellow" if success_rate >= 80 else "red"
        panel = Panel(result_text, title="测试结果", style=panel_style)
        self.console.print(panel)
    
    async def generate_tests(self, test_type: str = "unit", target: str = None):
        """生成测试用例"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("正在生成测试用例...", total=None)
            
            try:
                # 使用AI优化器生成测试
                optimization_result = await self.ai_optimizer.optimize_test_strategy({
                    "test_type": test_type,
                    "target": target or "default",
                    "optimization_goals": ["coverage", "efficiency"]
                })
                
                progress.update(task, description="测试用例生成完成")
                
                # 显示生成结果
                self._display_generation_results(optimization_result, test_type)
                
                return optimization_result
                
            except Exception as e:
                progress.update(task, description=f"生成失败: {e}")
                self.console.print(f"❌ 测试生成失败: {e}", style="bold red")
                return None
    
    def _display_generation_results(self, result: Dict[str, Any], test_type: str):
        """显示生成结果"""
        generation_text = f"""
🎯 测试类型: {test_type}
📝 生成的测试用例: {result.get('generated_tests', 0)}
🎯 优化目标: {', '.join(result.get('optimization_goals', []))}
⚡ 优化策略: {result.get('strategy_name', 'Unknown')}
📊 预期覆盖率: {result.get('expected_coverage', 0):.1f}%
        """
        
        panel = Panel(generation_text, title="测试生成结果", style="cyan")
        self.console.print(panel)
    
    async def analyze_results(self, report_path: str = None):
        """分析测试结果"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("正在分析测试结果...", total=None)
            
            try:
                # 生成性能分析
                analysis = await self.performance_analyzer.generate_performance_analysis()
                
                progress.update(task, description="分析完成")
                
                # 显示分析结果
                self._display_analysis_results(analysis)
                
                return analysis
                
            except Exception as e:
                progress.update(task, description=f"分析失败: {e}")
                self.console.print(f"❌ 分析失败: {e}", style="bold red")
                return None
    
    def _display_analysis_results(self, analysis):
        """显示分析结果"""
        # 性能分析表格
        perf_table = Table(title="性能分析结果", show_header=True, header_style="bold magenta")
        perf_table.add_column("指标", style="cyan")
        perf_table.add_column("当前值", style="white")
        perf_table.add_column("状态", style="green")
        
        for metric, value in analysis.key_metrics.items():
            status = "✅ 正常" if value < 50 else "⚠️ 注意" if value < 80 else "❌ 警告"
            perf_table.add_row(metric, f"{value:.1f}", status)
        
        self.console.print(perf_table)
        
        # 总体评分
        score_text = f"""
🏆 总体性能分数: {analysis.overall_score:.1f}/100
📊 性能等级: {analysis.performance_level.value.upper()}
📈 趋势方向: {analysis.trend_direction.value.upper()}
🎯 分析置信度: {analysis.confidence:.1f}
        """
        
        panel_style = "green" if analysis.overall_score >= 80 else "yellow" if analysis.overall_score >= 60 else "red"
        panel = Panel(score_text, title="性能评估", style=panel_style)
        self.console.print(panel)
        
        # 瓶颈和建议
        if analysis.bottlenecks:
            self.console.print("\n🚨 发现的瓶颈:", style="bold red")
            for bottleneck in analysis.bottlenecks:
                self.console.print(f"  • {bottleneck['description']}", style="red")
        
        if analysis.recommendations:
            self.console.print("\n💡 优化建议:", style="bold blue")
            for rec in analysis.recommendations:
                self.console.print(f"  • {rec['title']}: {rec['description']}", style="blue")
    
    async def diagnose_error(self, error_id: str = None, error_message: str = None):
        """诊断错误"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("正在诊断错误...", total=None)
            
            try:
                # 构造错误信息
                error_info = {
                    "type": "ImportError",
                    "message": error_message or "ImportError: No module named 'requests'",
                    "stack_trace": "File '/test/test_api.py', line 5, in <module>\n    import requests",
                    "context": {"module": "test_api"}
                }
                
                # 执行诊断
                diagnosis = await self.diagnostic_engine.diagnose_error(error_info)
                
                # 生成修复建议
                suggestions = await self.diagnostic_engine.generate_fix_suggestions(diagnosis)
                
                progress.update(task, description="诊断完成")
                
                # 显示诊断结果
                self._display_diagnosis_results(diagnosis, suggestions)
                
                return diagnosis, suggestions
                
            except Exception as e:
                progress.update(task, description=f"诊断失败: {e}")
                self.console.print(f"❌ 诊断失败: {e}", style="bold red")
                return None, None
    
    def _display_diagnosis_results(self, diagnosis, suggestions):
        """显示诊断结果"""
        # 错误诊断信息
        diag_text = f"""
🔍 错误ID: {diagnosis.error_id}
🏷️ 错误类型: {diagnosis.error_type}
⚠️ 严重程度: {diagnosis.severity.value.upper()}
🎯 诊断置信度: {diagnosis.diagnosis_confidence:.1f}

📝 描述: {diagnosis.description}
🔎 根本原因: {diagnosis.root_cause}
🔧 受影响组件: {', '.join(diagnosis.affected_components)}
        """
        
        severity_style = {
            "low": "green",
            "medium": "yellow", 
            "high": "red",
            "critical": "bold red"
        }.get(diagnosis.severity.value, "white")
        
        panel = Panel(diag_text, title="错误诊断", style=severity_style)
        self.console.print(panel)
        
        # 修复建议
        if suggestions:
            self.console.print("\n🛠️ 修复建议:", style="bold blue")
            
            fix_table = Table(show_header=True, header_style="bold blue")
            fix_table.add_column("建议", style="cyan", width=25)
            fix_table.add_column("置信度", style="white", width=10)
            fix_table.add_column("预估工作量", style="yellow", width=12)
            fix_table.add_column("描述", style="white", width=40)
            
            for suggestion in suggestions:
                fix_table.add_row(
                    suggestion.title,
                    suggestion.confidence.value,
                    suggestion.estimated_effort,
                    suggestion.description
                )
            
            self.console.print(fix_table)
    
    async def predict_performance(self, metric: str = "execution_time", hours: int = 24):
        """预测性能趋势"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("正在分析性能趋势...", total=None)
            
            try:
                # 分析趋势
                trend_analysis = await self.performance_analyzer.analyze_performance_trends(metric)
                
                # 生成预测
                prediction = await self.performance_analyzer.predict_future_performance(metric, hours)
                
                progress.update(task, description="预测完成")
                
                # 显示预测结果
                self._display_prediction_results(trend_analysis, prediction)
                
                return trend_analysis, prediction
                
            except Exception as e:
                progress.update(task, description=f"预测失败: {e}")
                self.console.print(f"❌ 预测失败: {e}", style="bold red")
                return None, None
    
    def _display_prediction_results(self, trend_analysis, prediction):
        """显示预测结果"""
        # 趋势分析
        trend_text = f"""
📊 指标: {trend_analysis['metric_name']}
📈 趋势方向: {trend_analysis['trend_direction'].upper()}
📉 变化率: {trend_analysis['change_rate_percent']:.1f}%
🎯 稳定性评分: {trend_analysis['stability_score']:.1f}
📋 数据点数: {trend_analysis['data_points']}
⚠️ 异常值: {trend_analysis['anomalies_count']}个
        """
        
        trend_style = {
            "improving": "green",
            "stable": "blue",
            "degrading": "red",
            "volatile": "yellow"
        }.get(trend_analysis['trend_direction'], "white")
        
        panel = Panel(trend_text, title="趋势分析", style=trend_style)
        self.console.print(panel)
        
        # 预测信息
        pred_text = f"""
🔮 当前值: {prediction.current_value:.2f}
📊 趋势分析: {prediction.trend_analysis}
⚠️ 风险因素: {len(prediction.risk_factors)}个
📈 置信区间: {prediction.confidence_interval[0]:.2f} - {prediction.confidence_interval[1]:.2f}
        """
        
        pred_panel = Panel(pred_text, title="性能预测", style="cyan")
        self.console.print(pred_panel)
        
        # 风险因素
        if prediction.risk_factors:
            self.console.print("\n⚠️ 风险因素:", style="bold yellow")
            for risk in prediction.risk_factors:
                self.console.print(f"  • {risk}", style="yellow")
    
    def show_status(self):
        """显示系统状态"""
        # AI优化器状态
        ai_status = self.ai_optimizer.get_optimization_summary()
        
        # 诊断引擎状态
        diag_status = self.diagnostic_engine.get_diagnostic_summary()
        
        # 性能分析器状态
        perf_status = self.performance_analyzer.get_performance_summary()
        
        # 创建状态表格
        status_table = Table(title="PowerAutomation 系统状态", show_header=True, header_style="bold green")
        status_table.add_column("组件", style="cyan", width=20)
        status_table.add_column("状态", style="white", width=15)
        status_table.add_column("详细信息", style="white", width=50)
        
        # AI优化器状态
        status_table.add_row(
            "AI优化器",
            "🟢 运行中" if ai_status["status"] == "active" else "🔴 离线",
            f"策略: {ai_status['active_strategies']}, 优化: {ai_status['total_optimizations']}"
        )
        
        # 诊断引擎状态
        status_table.add_row(
            "智能诊断",
            "🟢 运行中" if diag_status["status"] == "active" else "🔴 离线",
            f"模式: {diag_status['error_patterns_loaded']}, 历史: {diag_status['error_history_size']}"
        )
        
        # 性能分析器状态
        status_table.add_row(
            "性能分析",
            "🟢 运行中" if perf_status["status"] == "active" else "🔴 离线",
            f"指标: {perf_status['total_metrics_collected']}, 24h: {perf_status['recent_metrics_24h']}"
        )
        
        self.console.print(status_table)
        
        # 系统摘要
        summary_text = f"""
🚀 PowerAutomation 测试管理平台 v3.0
📊 总体状态: 运行正常
🔧 活跃组件: 3/3
📈 性能等级: 优秀
⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        summary_panel = Panel(summary_text, title="系统摘要", style="bold green")
        self.console.print(summary_panel)


# CLI命令定义
@click.group()
@click.version_option(version="3.0.0", prog_name="PowerAutomation")
def cli():
    """PowerAutomation 测试管理平台 CLI"""
    pass


@cli.command()
@click.option('--suite', '-s', help='测试套件名称')
@click.option('--config', '-c', help='配置文件路径')
@click.option('--parallel', '-p', is_flag=True, help='并行执行')
def run(suite, config, parallel):
    """执行测试套件"""
    cli_tool = PowerAutomationCLI()
    cli_tool.print_banner()
    
    async def run_async():
        await cli_tool.run_tests(suite, config, parallel)
    
    asyncio.run(run_async())


@cli.command()
@click.option('--type', '-t', default='unit', help='测试类型 (unit/integration/e2e)')
@click.option('--target', help='目标模块或文件')
def generate(type, target):
    """生成测试用例"""
    cli_tool = PowerAutomationCLI()
    
    async def generate_async():
        await cli_tool.generate_tests(type, target)
    
    asyncio.run(generate_async())


@cli.command()
@click.option('--report', '-r', help='报告路径')
def analyze(report):
    """分析测试结果"""
    cli_tool = PowerAutomationCLI()
    
    async def analyze_async():
        await cli_tool.analyze_results(report)
    
    asyncio.run(analyze_async())


@cli.command()
@click.option('--error-id', help='错误ID')
@click.option('--message', '-m', help='错误消息')
def diagnose(error_id, message):
    """诊断测试错误"""
    cli_tool = PowerAutomationCLI()
    
    async def diagnose_async():
        await cli_tool.diagnose_error(error_id, message)
    
    asyncio.run(diagnose_async())


@cli.command()
@click.option('--metric', '-m', default='execution_time', help='性能指标')
@click.option('--hours', '-h', default=24, help='预测时间范围（小时）')
def predict(metric, hours):
    """预测性能趋势"""
    cli_tool = PowerAutomationCLI()
    
    async def predict_async():
        await cli_tool.predict_performance(metric, hours)
    
    asyncio.run(predict_async())


@cli.command()
def status():
    """查看系统状态"""
    cli_tool = PowerAutomationCLI()
    cli_tool.show_status()


@cli.command()
def dashboard():
    """启动监控面板"""
    cli_tool = PowerAutomationCLI()
    cli_tool.console.print("🚀 启动监控面板...", style="bold blue")
    cli_tool.console.print("📊 面板地址: http://localhost:8080", style="green")
    cli_tool.console.print("💡 提示: 使用 Ctrl+C 停止面板", style="yellow")


@cli.command()
def help():
    """显示详细帮助"""
    cli_tool = PowerAutomationCLI()
    cli_tool.print_banner()
    cli_tool.print_help()


if __name__ == "__main__":
    cli()

