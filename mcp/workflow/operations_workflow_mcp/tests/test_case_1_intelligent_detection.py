#!/usr/bin/env python3
"""
Operations Workflow MCP - 测试用例1: 智能检测模块
测试目录结构合规检查、文件完整性检测、依赖关系验证、配置文件校验
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class IntelligentDetectionTestCase:
    """智能检测模块测试用例"""
    
    def __init__(self, base_path: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.base_path = Path(base_path)
        self.mcp_path = self.base_path / "mcp"
        self.test_results = []
        
    def test_directory_structure_compliance(self) -> Dict:
        """测试用例1.1: 目录结构合规检查"""
        print("🔍 执行测试用例1.1: 目录结构合规检查")
        
        # 定义标准目录结构
        expected_structure = {
            "mcp/adapter": ["local_model_mcp", "cloud_search_mcp", "kilocode_mcp"],
            "mcp/workflow": ["ocr_mcp", "operations_workflow_mcp"],
            "workflow_howto": [],
            "mcp/howto": []
        }
        
        results = {
            "test_name": "目录结构合规检查",
            "status": "PASS",
            "issues": [],
            "details": {}
        }
        
        # 检查每个预期目录
        for dir_path, expected_subdirs in expected_structure.items():
            full_path = self.base_path / dir_path
            
            if not full_path.exists():
                results["issues"].append(f"缺失目录: {dir_path}")
                results["status"] = "FAIL"
                continue
                
            # 检查子目录
            actual_subdirs = [d.name for d in full_path.iterdir() if d.is_dir()]
            missing_subdirs = set(expected_subdirs) - set(actual_subdirs)
            
            if missing_subdirs:
                results["issues"].append(f"目录 {dir_path} 缺失子目录: {missing_subdirs}")
                results["status"] = "FAIL"
                
            results["details"][dir_path] = {
                "expected": expected_subdirs,
                "actual": actual_subdirs,
                "missing": list(missing_subdirs)
            }
        
        self.test_results.append(results)
        return results
    
    def test_file_integrity_detection(self) -> Dict:
        """测试用例1.2: 文件完整性检测"""
        print("🔍 执行测试用例1.2: 文件完整性检测")
        
        results = {
            "test_name": "文件完整性检测",
            "status": "PASS",
            "issues": [],
            "details": {}
        }
        
        # 检查关键文件是否存在
        critical_files = [
            "mcp/adapter/local_model_mcp/local_model_mcp.py",
            "mcp/adapter/cloud_search_mcp/cloud_search_mcp.py",
            "mcp/workflow/ocr_mcp/src/ocr_workflow_mcp.py",
            "mcp/workflow/operations_workflow_mcp/src/operations_workflow_mcp.py"
        ]
        
        for file_path in critical_files:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                results["issues"].append(f"缺失关键文件: {file_path}")
                results["status"] = "FAIL"
            else:
                # 检查文件是否为空
                if full_path.stat().st_size == 0:
                    results["issues"].append(f"文件为空: {file_path}")
                    results["status"] = "FAIL"
                    
            results["details"][file_path] = {
                "exists": full_path.exists(),
                "size": full_path.stat().st_size if full_path.exists() else 0
            }
        
        self.test_results.append(results)
        return results
    
    def test_dependency_verification(self) -> Dict:
        """测试用例1.3: 依赖关系验证"""
        print("🔍 执行测试用例1.3: 依赖关系验证")
        
        results = {
            "test_name": "依赖关系验证",
            "status": "PASS",
            "issues": [],
            "details": {}
        }
        
        # 检查Python文件的import依赖
        python_files = list(self.mcp_path.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 简单检查import语句
                import_lines = [line.strip() for line in content.split('\n') 
                              if line.strip().startswith(('import ', 'from '))]
                
                results["details"][str(py_file.relative_to(self.base_path))] = {
                    "imports": import_lines,
                    "import_count": len(import_lines)
                }
                
            except Exception as e:
                results["issues"].append(f"无法读取文件 {py_file}: {str(e)}")
                results["status"] = "FAIL"
        
        self.test_results.append(results)
        return results
    
    def test_config_file_validation(self) -> Dict:
        """测试用例1.4: 配置文件校验"""
        print("🔍 执行测试用例1.4: 配置文件校验")
        
        results = {
            "test_name": "配置文件校验",
            "status": "PASS",
            "issues": [],
            "details": {}
        }
        
        # 查找配置文件
        config_files = {
            "toml": list(self.mcp_path.rglob("*.toml")),
            "yaml": list(self.mcp_path.rglob("*.yaml")) + list(self.mcp_path.rglob("*.yml")),
            "json": list(self.mcp_path.rglob("*.json"))
        }
        
        for file_type, files in config_files.items():
            for config_file in files:
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # 尝试解析配置文件
                    if file_type == "json":
                        json.loads(content)
                    elif file_type == "yaml":
                        yaml.safe_load(content)
                    elif file_type == "toml":
                        # 简单检查TOML格式
                        if not content.strip():
                            results["issues"].append(f"TOML文件为空: {config_file}")
                            results["status"] = "FAIL"
                    
                    results["details"][str(config_file.relative_to(self.base_path))] = {
                        "type": file_type,
                        "valid": True,
                        "size": len(content)
                    }
                    
                except Exception as e:
                    results["issues"].append(f"配置文件格式错误 {config_file}: {str(e)}")
                    results["status"] = "FAIL"
                    results["details"][str(config_file.relative_to(self.base_path))] = {
                        "type": file_type,
                        "valid": False,
                        "error": str(e)
                    }
        
        self.test_results.append(results)
        return results
    
    def run_all_tests(self) -> Dict:
        """运行所有智能检测测试用例"""
        print("🚀 开始执行智能检测模块测试用例")
        print("=" * 60)
        
        # 执行所有测试
        test1 = self.test_directory_structure_compliance()
        test2 = self.test_file_integrity_detection()
        test3 = self.test_dependency_verification()
        test4 = self.test_config_file_validation()
        
        # 汇总结果
        summary = {
            "module": "智能检测模块",
            "total_tests": 4,
            "passed": sum(1 for result in self.test_results if result["status"] == "PASS"),
            "failed": sum(1 for result in self.test_results if result["status"] == "FAIL"),
            "test_results": self.test_results
        }
        
        print("\n" + "=" * 60)
        print(f"📊 智能检测模块测试结果汇总:")
        print(f"   总测试数: {summary['total_tests']}")
        print(f"   通过: {summary['passed']}")
        print(f"   失败: {summary['failed']}")
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"   {status_icon} {result['test_name']}: {result['status']}")
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"      - {issue}")
        
        return summary

def main():
    """主函数"""
    print("🔍 Operations Workflow MCP - 智能检测模块测试用例")
    print("=" * 60)
    
    # 创建测试实例
    detector = IntelligentDetectionTestCase()
    
    # 运行所有测试
    summary = detector.run_all_tests()
    
    # 保存测试结果
    results_file = Path(__file__).parent / "test_results_detection.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 测试结果已保存到: {results_file}")
    
    return summary["failed"] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

