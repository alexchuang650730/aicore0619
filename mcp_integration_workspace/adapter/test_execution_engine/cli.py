#!/usr/bin/env python3
"""
Test Management MCP 命令行接口
PowerAutomation测试框架管理器的CLI工具

支持测试框架生成、执行、修复和状态查询等功能。
遵循PowerAutomation MCP CLI规范。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-17
"""

import asyncio
import argparse
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.adapter.test_manage_mcp import TestManageMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestManageMCPCLI:
    """Test Management MCP 命令行接口"""
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        """
        初始化CLI
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = project_root
        self.test_manager = None
    
    async def init_manager(self):
        """初始化测试管理器"""
        if not self.test_manager:
            self.test_manager = TestManageMCP(self.project_root)
    
    async def generate_frameworks(self, args) -> int:
        """生成测试框架命令"""
        await self.init_manager()
        
        print("🚀 开始生成测试框架...")
        result = await self.test_manager.generate_test_frameworks()
        
        if result["status"] == "success":
            print("✅ 测试框架生成成功!")
            print(f"📊 生成统计: {result['results']['total_modules']} 个模块")
            print(f"📄 报告路径: {result['report_path']}")
            return 0
        else:
            print(f"❌ 测试框架生成失败: {result['error']}")
            return 1
    
    async def execute_tests(self, args) -> int:
        """执行测试命令"""
        await self.init_manager()
        
        print(f"🧪 开始执行测试 (并行: {not args.sequential}, 工作线程: {args.workers})...")
        result = await self.test_manager.execute_all_tests(
            parallel=not args.sequential,
            max_workers=args.workers
        )
        
        if result["status"] == "success":
            if result["all_tests_passed"]:
                print("✅ 所有测试通过!")
            else:
                print("⚠️ 部分测试失败，请查看详细报告")
            print(f"📄 报告路径: {result['report_path']}")
            return 0 if result["all_tests_passed"] else 1
        else:
            print(f"❌ 测试执行失败: {result['error']}")
            return 1
    
    async def fix_frameworks(self, args) -> int:
        """修复测试框架命令"""
        await self.init_manager()
        
        print("🔧 开始修复测试框架...")
        result = await self.test_manager.fix_test_frameworks()
        
        if result["status"] == "success":
            print("✅ 测试框架修复成功!")
            print(f"📊 修复统计: {result['results']['fixed_files']} 个文件")
            print(f"📄 报告路径: {result['report_path']}")
            return 0
        else:
            print(f"❌ 测试框架修复失败: {result['error']}")
            return 1
    
    async def show_status(self, args) -> int:
        """显示测试状态命令"""
        await self.init_manager()
        
        print("📊 获取测试状态...")
        result = await self.test_manager.get_test_status()
        
        if result["status"] == "success":
            overview = result["overview"]
            last_ops = result["last_operations"]
            
            print("\\n" + "="*60)
            print("📋 PowerAutomation 测试状态概览")
            print("="*60)
            print(f"📦 总模块数: {overview['total_modules']}")
            print(f"🧪 总测试数: {overview['total_tests']}")
            print(f"   - 单元测试: {overview['unit_tests']}")
            print(f"   - 集成测试: {overview['integration_tests']}")
            print(f"📁 模块分布:")
            print(f"   - 适配器模块: {overview['adapter_modules']}")
            print(f"   - 工作流模块: {overview['workflow_modules']}")
            
            print("\\n⏰ 最近操作:")
            print(f"   - 框架生成: {last_ops['generation'] or '未执行'}")
            print(f"   - 测试执行: {last_ops['execution'] or '未执行'}")
            print(f"   - 框架修复: {last_ops['fix'] or '未执行'}")
            
            if args.verbose:
                print("\\n📄 最新报告:")
                for report_type, report_info in result["latest_reports"].items():
                    if report_info:
                        print(f"   - {report_type}: {report_info['file']} ({report_info['time']})")
                    else:
                        print(f"   - {report_type}: 无")
            
            return 0
        else:
            print(f"❌ 获取测试状态失败: {result['error']}")
            return 1
    
    async def run_full_cycle(self, args) -> int:
        """运行完整测试周期命令"""
        await self.init_manager()
        
        print("🔄 开始运行完整测试周期...")
        result = await self.test_manager.run_full_test_cycle(
            fix_first=not args.no_fix,
            parallel=not args.sequential,
            max_workers=args.workers
        )
        
        print("\\n" + "="*80)
        print("🎉 完整测试周期执行完成")
        print("="*80)
        print(f"总体状态: {result['overall_status']}")
        print(f"执行步骤: {result['summary']['successful_steps']}/{result['summary']['total_steps']} 成功")
        print(f"总耗时: {result.get('cycle_duration', 0):.2f}秒")
        
        if 'cycle_report_path' in result:
            print(f"详细报告: {result['cycle_report_path']}")
        
        # 显示各步骤结果
        if args.verbose:
            print("\\n📋 步骤详情:")
            for step in result["steps"]:
                step_name = step["step"]
                step_result = step["result"]
                status_icon = "✅" if step_result["status"] == "success" else "❌"
                print(f"   {status_icon} {step_name}: {step_result['status']}")
        
        return 0 if result['overall_status'] == 'success' else 1
    
    async def list_reports(self, args) -> int:
        """列出测试报告命令"""
        await self.init_manager()
        
        reports_path = Path(self.test_manager.reports_path)
        
        print(f"📄 测试报告列表 ({reports_path}):")
        print("-" * 60)
        
        # 按类型分组显示报告
        report_types = ["generation", "execution", "fix", "full_cycle"]
        
        for report_type in report_types:
            print(f"\\n📋 {report_type.title()} 报告:")
            report_files = list(reports_path.glob(f"{report_type}_report_*.json"))
            
            if report_files:
                # 按时间排序
                report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                for i, report_file in enumerate(report_files[:args.limit]):
                    mtime = report_file.stat().st_mtime
                    time_str = Path(report_file).stem.split('_')[-2:]
                    time_display = f"{time_str[0]}_{time_str[1]}" if len(time_str) >= 2 else "unknown"
                    size = report_file.stat().st_size
                    
                    print(f"   {i+1}. {report_file.name} ({size} bytes, {time_display})")
                    
                    if args.verbose and i < 3:  # 只显示前3个的详细信息
                        try:
                            with open(report_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if 'status' in data:
                                    print(f"      状态: {data['status']}")
                                if 'summary' in data:
                                    print(f"      摘要: {data['summary']}")
                        except Exception as e:
                            print(f"      (无法读取详情: {e})")
            else:
                print("   (无报告)")
        
        return 0

def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Test Management MCP - PowerAutomation测试框架管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s generate                    # 生成测试框架
  %(prog)s execute --workers 4        # 执行测试(4个并发)
  %(prog)s fix                         # 修复测试框架
  %(prog)s status --verbose           # 显示详细状态
  %(prog)s cycle --no-fix             # 运行完整周期(跳过修复)
  %(prog)s reports --limit 10         # 列出最近10个报告
        """
    )
    
    parser.add_argument(
        '--project-root',
        default='/opt/powerautomation',
        help='项目根目录 (默认: /opt/powerautomation)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # generate 命令
    generate_parser = subparsers.add_parser('generate', help='生成测试框架')
    
    # execute 命令
    execute_parser = subparsers.add_parser('execute', help='执行测试')
    execute_parser.add_argument(
        '--sequential',
        action='store_true',
        help='顺序执行测试(默认并行)'
    )
    execute_parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='并行执行的最大工作线程数 (默认: 4)'
    )
    
    # fix 命令
    fix_parser = subparsers.add_parser('fix', help='修复测试框架')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='显示测试状态')
    
    # cycle 命令
    cycle_parser = subparsers.add_parser('cycle', help='运行完整测试周期')
    cycle_parser.add_argument(
        '--no-fix',
        action='store_true',
        help='跳过修复步骤'
    )
    cycle_parser.add_argument(
        '--sequential',
        action='store_true',
        help='顺序执行测试(默认并行)'
    )
    cycle_parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='并行执行的最大工作线程数 (默认: 4)'
    )
    
    # reports 命令
    reports_parser = subparsers.add_parser('reports', help='列出测试报告')
    reports_parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='显示报告数量限制 (默认: 5)'
    )
    
    return parser

async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    cli = TestManageMCPCLI(args.project_root)
    
    try:
        # 根据命令执行相应操作
        if args.command == 'generate':
            return await cli.generate_frameworks(args)
        elif args.command == 'execute':
            return await cli.execute_tests(args)
        elif args.command == 'fix':
            return await cli.fix_frameworks(args)
        elif args.command == 'status':
            return await cli.show_status(args)
        elif args.command == 'cycle':
            return await cli.run_full_cycle(args)
        elif args.command == 'reports':
            return await cli.list_reports(args)
        else:
            print(f"未知命令: {args.command}")
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\\n⚠️ 操作被用户中断")
        return 130
    except Exception as e:
        logger.error(f"执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

