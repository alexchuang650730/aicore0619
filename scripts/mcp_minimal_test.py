#!/usr/bin/env python3
"""
PowerAutomation MCP最小测试集
专门用于测试和修复十个MCP组件
"""

import json
import subprocess
import sys
from typing import Dict, Any

class MCPMinimalTester:
    """MCP组件最小测试器"""
    
    def __init__(self):
        self.mcp_components = [
            "gemini_mcp",
            "claude_mcp", 
            "super_memory_mcp",
            "rl_srt_mcp",
            "search_mcp",
            "kilocode_mcp",
            "playwright_mcp",
            "test_case_generator_mcp",
            "video_analysis_mcp",
            "mcp_coordinator"
        ]
        
    def test_kilocode_routing(self) -> Dict[str, Any]:
        """测试kilocode_mcp路由问题"""
        print("🔍 测试kilocode_mcp路由...")
        
        test_cases = [
            {
                "name": "PPT生成任务",
                "data": {
                    "type": "ppt_generation",
                    "content": "生成华为2024年终端年终PPT",
                    "session_id": "ppt_test"
                },
                "expected_tool": "kilocode_mcp"
            },
            {
                "name": "代码生成任务", 
                "data": {
                    "type": "code_generation",
                    "content": "生成Python代码",
                    "session_id": "code_test"
                },
                "expected_tool": "kilocode_mcp"
            }
        ]
        
        results = []
        for test_case in test_cases:
            result = self._run_mcp_test(test_case)
            results.append(result)
            
        return {
            "test_name": "kilocode_routing",
            "results": results,
            "summary": self._analyze_routing_results(results)
        }
    
    def _run_mcp_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个MCP测试"""
        try:
            # 构建命令
            cmd = [
                "ssh", "-i", "/home/ubuntu/upload/alexchuang.pem",
                "ec2-user@98.81.255.168",
                f"cd /opt/powerautomation/mcp/mcp_coordinator && python3 mcp_coordinator.py process_input --data '{json.dumps(test_case['data'])}'"
            ]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 解析输出中的JSON
                output_lines = result.stdout.strip().split('\n')
                json_line = None
                for line in reversed(output_lines):
                    if line.startswith('{') and line.endswith('}'):
                        json_line = line
                        break
                
                if json_line:
                    response = json.loads(json_line)
                    selected_tool = response.get("tool_selection_result", {}).get("tool_id", "unknown")
                    
                    return {
                        "test_case": test_case["name"],
                        "status": "success",
                        "selected_tool": selected_tool,
                        "expected_tool": test_case["expected_tool"],
                        "routing_correct": selected_tool == test_case["expected_tool"],
                        "response": response
                    }
                else:
                    return {
                        "test_case": test_case["name"],
                        "status": "error",
                        "message": "无法解析JSON响应",
                        "output": result.stdout
                    }
            else:
                return {
                    "test_case": test_case["name"],
                    "status": "error", 
                    "message": f"命令执行失败: {result.stderr}",
                    "returncode": result.returncode
                }
                
        except Exception as e:
            return {
                "test_case": test_case["name"],
                "status": "error",
                "message": f"测试执行异常: {str(e)}"
            }
    
    def _analyze_routing_results(self, results: list) -> Dict[str, Any]:
        """分析路由测试结果"""
        total_tests = len(results)
        successful_tests = len([r for r in results if r.get("status") == "success"])
        correct_routing = len([r for r in results if r.get("routing_correct") == True])
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "correct_routing": correct_routing,
            "routing_accuracy": correct_routing / total_tests if total_tests > 0 else 0,
            "issues_found": [
                r for r in results 
                if r.get("status") == "success" and not r.get("routing_correct")
            ]
        }
    
    def run_minimal_test_suite(self):
        """运行最小测试套件"""
        print("🚀 PowerAutomation MCP最小测试集")
        print("=" * 50)
        
        # 测试kilocode路由
        routing_test = self.test_kilocode_routing()
        
        print("\n📊 测试结果:")
        print(f"总测试数: {routing_test['summary']['total_tests']}")
        print(f"成功测试: {routing_test['summary']['successful_tests']}")
        print(f"路由正确: {routing_test['summary']['correct_routing']}")
        print(f"路由准确率: {routing_test['summary']['routing_accuracy']:.1%}")
        
        if routing_test['summary']['issues_found']:
            print("\n❌ 发现的路由问题:")
            for issue in routing_test['summary']['issues_found']:
                print(f"  - {issue['test_case']}: 期望{issue['expected_tool']}, 实际{issue['selected_tool']}")
        
        return routing_test

if __name__ == "__main__":
    tester = MCPMinimalTester()
    results = tester.run_minimal_test_suite()
    
    # 保存结果
    with open("/home/ubuntu/mcp_minimal_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: /home/ubuntu/mcp_minimal_test_results.json")

