#!/usr/bin/env python3
"""
PowerAutomation MCP测试框架修复器

修复生成的测试代码中的常见问题，确保所有测试能够正常运行。

作者: Manus AI
版本: 1.0.0
日期: 2025-06-17
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

class MCPTestFrameworkFixer:
    """MCP测试框架修复器"""
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        self.project_root = Path(project_root)
        self.mcp_adapter_path = self.project_root / "mcp" / "adapter"
        self.mcp_workflow_path = self.project_root / "mcp" / "workflow"
        self.fixed_files = []
        
    def fix_all_test_files(self) -> Dict[str, Any]:
        """修复所有测试文件"""
        print("🔧 开始修复PowerAutomation MCP测试文件")
        print("=" * 60)
        
        results = {
            'total_files': 0,
            'fixed_files': 0,
            'error_files': []
        }
        
        # 修复适配器测试
        if self.mcp_adapter_path.exists():
            for module_dir in self.mcp_adapter_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    self._fix_module_tests(module_dir, results)
        
        # 修复工作流测试
        if self.mcp_workflow_path.exists():
            for module_dir in self.mcp_workflow_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    self._fix_module_tests(module_dir, results)
        
        print(f"\\n🎉 修复完成! 总计: {results['total_files']}, 修复: {results['fixed_files']}, 错误: {len(results['error_files'])}")
        return results
    
    def _fix_module_tests(self, module_dir: Path, results: Dict[str, Any]):
        """修复单个模块的测试"""
        module_name = module_dir.name
        print(f"🔧 修复模块: {module_name}")
        
        # 修复单元测试
        unit_tests_dir = module_dir / 'unit_tests'
        if unit_tests_dir.exists():
            for test_file in unit_tests_dir.glob('test_*.py'):
                self._fix_test_file(test_file, module_name, results)
        
        # 修复集成测试
        integration_tests_dir = module_dir / 'integration_tests'
        if integration_tests_dir.exists():
            for test_file in integration_tests_dir.glob('test_*.py'):
                self._fix_test_file(test_file, module_name, results)
    
    def _fix_test_file(self, test_file: Path, module_name: str, results: Dict[str, Any]):
        """修复单个测试文件"""
        results['total_files'] += 1
        
        try:
            # 读取文件内容
            content = test_file.read_text(encoding='utf-8')
            original_content = content
            
            # 应用修复
            content = self._fix_class_name_variable(content, module_name)
            content = self._fix_report_path(content, module_name)
            content = self._fix_imports(content)
            content = self._fix_string_formatting(content)
            
            # 如果有修改，保存文件
            if content != original_content:
                test_file.write_text(content, encoding='utf-8')
                results['fixed_files'] += 1
                self.fixed_files.append(str(test_file))
                print(f"  ✅ 修复: {test_file.name}")
            else:
                print(f"  ℹ️  无需修复: {test_file.name}")
                
        except Exception as e:
            results['error_files'].append({
                'file': str(test_file),
                'error': str(e)
            })
            print(f"  ❌ 修复失败: {test_file.name} - {e}")
    
    def _fix_class_name_variable(self, content: str, module_name: str) -> str:
        """修复class_name变量问题"""
        # 生成正确的类名
        class_name = ''.join(word.capitalize() for word in module_name.split('_'))
        
        # 替换所有{class_name}引用
        content = content.replace('{class_name}', class_name)
        content = content.replace('f\'MCP_Test{class_name}_', f'f\'MCP_Test{class_name}_')
        content = content.replace('f\'Test{class_name}', f'f\'Test{class_name}')
        content = content.replace('f\'MCP_Integration{class_name}_', f'f\'MCP_Integration{class_name}_')
        
        # 修复具体的变量引用
        content = re.sub(
            r'f\'MCP_Test\{class_name\}_\{datetime\.now\(\)\.strftime\("%Y%m%d_%H%M%S"\)\}\'',
            f'f\'MCP_Test{class_name}_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}\'',
            content
        )
        
        content = re.sub(
            r'f\'Test\{class_name\}\'',
            f'f\'Test{class_name}\'',
            content
        )
        
        content = re.sub(
            r'f\'test_report_\{class_name\.lower\(\)\}_',
            f'f\'test_report_{module_name}_',
            content
        )
        
        content = re.sub(
            r'f\'integration_test_report_\{class_name\.lower\(\)\}_',
            f'f\'integration_test_report_{module_name}_',
            content
        )
        
        return content
    
    def _fix_report_path(self, content: str, module_name: str) -> str:
        """修复报告路径问题"""
        # 修复单元测试报告路径
        content = re.sub(
            r'report_path = Path\(__file__\)\.parent\.parent / f\'test_report_\{class_name\.lower\(\)\}_\{datetime\.now\(\)\.strftime\("%Y%m%d_%H%M%S"\)\}\.json\'',
            f'report_path = Path(__file__).parent.parent / f\'test_report_{module_name}_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}.json\'',
            content
        )
        
        # 修复集成测试报告路径
        content = re.sub(
            r'report_path = Path\(__file__\)\.parent\.parent / f\'integration_test_report_\{class_name\.lower\(\)\}_\{datetime\.now\(\)\.strftime\("%Y%m%d_%H%M%S"\)\}\.json\'',
            f'report_path = Path(__file__).parent.parent / f\'integration_test_report_{module_name}_{{datetime.now().strftime("%Y%m%d_%H%M%S")}}.json\'',
            content
        )
        
        return content
    
    def _fix_imports(self, content: str) -> str:
        """修复导入问题"""
        # 确保所有必要的导入都存在
        required_imports = [
            'import unittest',
            'from unittest.mock import Mock, patch, AsyncMock, MagicMock',
            'import asyncio',
            'import json',
            'import yaml',
            'from datetime import datetime',
            'from pathlib import Path',
            'import sys',
            'import os'
        ]
        
        # 检查并添加缺失的导入
        for import_line in required_imports:
            if import_line not in content:
                # 在第一个import之后添加
                import_pattern = r'(#!/usr/bin/env python3\\n"""[^"]*"""\\n\\n)'
                if re.search(import_pattern, content):
                    content = re.sub(
                        import_pattern,
                        f'\\1{import_line}\\n',
                        content
                    )
        
        return content
    
    def _fix_string_formatting(self, content: str) -> str:
        """修复字符串格式化问题"""
        # 修复双重花括号问题
        content = re.sub(r'\\{\\{([^}]+)\\}\\}', r'{\\1}', content)
        
        # 修复转义字符问题
        content = content.replace('\\\\n', '\\n')
        content = content.replace('\\\\"', '\\"')
        
        return content

def main():
    """主函数"""
    fixer = MCPTestFrameworkFixer()
    results = fixer.fix_all_test_files()
    
    if results['error_files']:
        print(f"\\n⚠️  有 {len(results['error_files'])} 个文件修复失败:")
        for error in results['error_files']:
            print(f"  - {error['file']}: {error['error']}")
        return False
    
    print("\\n🎉 所有测试文件修复成功!")
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        exit(1)

