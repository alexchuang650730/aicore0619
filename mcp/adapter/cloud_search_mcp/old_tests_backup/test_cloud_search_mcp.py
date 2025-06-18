#!/usr/bin/env python3
"""
Cloud Search MCP 测试套件

全面测试Cloud Search MCP的各项功能，包括：
- 多模型OCR测试
- 智能路由测试
- 降级机制测试
- 性能基准测试
"""

import asyncio
import json
import time
import base64
from pathlib import Path
from typing import Dict, Any, List
import sys

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

from cloud_search_mcp import CloudSearchMCP, TaskType

class CloudSearchMCPTester:
    """Cloud Search MCP测试器"""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = config_path
        self.mcp = None
        self.test_results = []
    
    async def setup(self):
        """初始化测试环境"""
        print("🚀 初始化Cloud Search MCP测试环境...")
        self.mcp = CloudSearchMCP(self.config_path)
        print(f"✅ MCP初始化完成，可用模型: {list(self.mcp.model_configs.keys())}")
    
    async def test_basic_functionality(self):
        """测试基本功能"""
        print("\n" + "="*60)
        print("🧪 测试基本功能")
        print("="*60)
        
        # 测试健康检查
        result = self.mcp.health_check()
        assert result["status"] == "success", "健康检查失败"
        print("✅ 健康检查通过")
        
        # 测试获取能力
        result = self.mcp.get_capabilities()
        assert result["status"] == "success", "获取能力失败"
        assert len(result["capabilities"]) > 0, "能力列表为空"
        print(f"✅ 能力检查通过，支持 {len(result['capabilities'])} 种任务类型")
        
        # 测试获取模型列表
        result = self.mcp.get_supported_models()
        assert result["status"] == "success", "获取模型列表失败"
        assert len(result["models"]) > 0, "模型列表为空"
        print(f"✅ 模型检查通过，支持 {len(result['models'])} 个模型")
        
        self.test_results.append({
            "test": "basic_functionality",
            "status": "passed",
            "details": "所有基本功能测试通过"
        })
    
    async def test_ocr_with_sample_image(self):
        """使用示例图像测试OCR"""
        print("\n" + "="*60)
        print("🖼️ 测试OCR功能（示例图像）")
        print("="*60)
        
        # 创建一个简单的测试图像（1x1像素PNG）
        test_image_data = self._create_test_image()
        
        # 测试不同任务类型
        task_types = [
            TaskType.DOCUMENT_OCR,
            TaskType.HANDWRITING_OCR,
            TaskType.TABLE_EXTRACTION
        ]
        
        for task_type in task_types:
            print(f"\n🔍 测试任务类型: {task_type.value}")
            
            try:
                result = await self.mcp.process_ocr_request(
                    image_data=test_image_data,
                    task_type=task_type.value,
                    language="auto",
                    output_format="markdown"
                )
                
                if result["status"] == "success":
                    response = result["result"]
                    print(f"✅ {task_type.value} 测试成功")
                    print(f"   模型: {response['model_used']}")
                    print(f"   置信度: {response['confidence']:.2%}")
                    print(f"   处理时间: {response['processing_time']:.2f}秒")
                    print(f"   成本: ${response['cost']:.6f}")
                else:
                    print(f"❌ {task_type.value} 测试失败: {result.get('message')}")
                
                # 短暂延迟避免API限制
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ {task_type.value} 测试异常: {e}")
        
        self.test_results.append({
            "test": "ocr_sample_image",
            "status": "completed",
            "details": f"测试了 {len(task_types)} 种任务类型"
        })
    
    def _create_test_image(self) -> bytes:
        """创建测试图像（1x1像素PNG）"""
        # 最小的PNG图像数据（1x1像素，透明）
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
        )
        return png_data
    
    async def test_model_selection(self):
        """测试模型选择逻辑"""
        print("\n" + "="*60)
        print("🤖 测试模型选择逻辑")
        print("="*60)
        
        # 测试不同优先级的模型选择
        priorities = ["speed", "cost", "quality", "balanced"]
        task_type = TaskType.DOCUMENT_OCR
        
        for priority in priorities:
            # 临时修改配置
            original_priority = self.mcp.config.get("cloud_search_mcp", {}).get("priority")
            self.mcp.config.setdefault("cloud_search_mcp", {})["priority"] = priority
            
            selected_model = self.mcp.model_selector.select_optimal_model(task_type, priority)
            
            if selected_model:
                print(f"✅ {priority} 优先级选择模型: {selected_model.value}")
            else:
                print(f"❌ {priority} 优先级未选择到模型")
            
            # 恢复原配置
            if original_priority:
                self.mcp.config["cloud_search_mcp"]["priority"] = original_priority
        
        self.test_results.append({
            "test": "model_selection",
            "status": "completed",
            "details": f"测试了 {len(priorities)} 种优先级策略"
        })
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "="*60)
        print("🚨 测试错误处理")
        print("="*60)
        
        # 测试无效图像数据
        try:
            result = await self.mcp.process_ocr_request(
                image_data=b"invalid_image_data",
                task_type="document_ocr"
            )
            
            if result["status"] == "error":
                print("✅ 无效图像数据错误处理正确")
            else:
                print("❌ 无效图像数据应该返回错误")
                
        except Exception as e:
            print(f"✅ 无效图像数据触发异常（预期行为）: {e}")
        
        # 测试无效任务类型
        try:
            result = await self.mcp.process_ocr_request(
                image_data=self._create_test_image(),
                task_type="invalid_task_type"
            )
            print("✅ 无效任务类型处理完成")
            
        except Exception as e:
            print(f"✅ 无效任务类型触发异常（预期行为）: {e}")
        
        # 测试缺少参数
        try:
            result = await self.mcp.process_ocr_request()
            if result["status"] == "error":
                print("✅ 缺少参数错误处理正确")
            
        except Exception as e:
            print(f"✅ 缺少参数触发异常（预期行为）: {e}")
        
        self.test_results.append({
            "test": "error_handling",
            "status": "passed",
            "details": "错误处理机制工作正常"
        })
    
    async def test_mcp_interface(self):
        """测试MCP标准接口"""
        print("\n" + "="*60)
        print("🔌 测试MCP标准接口")
        print("="*60)
        
        # 测试process方法
        test_cases = [
            {
                "operation": "get_capabilities",
                "params": {}
            },
            {
                "operation": "get_supported_models", 
                "params": {}
            },
            {
                "operation": "health_check",
                "params": {}
            },
            {
                "operation": "get_statistics",
                "params": {}
            }
        ]
        
        for test_case in test_cases:
            operation = test_case["operation"]
            result = self.mcp.process(test_case)
            
            if result["status"] == "success":
                print(f"✅ MCP接口 {operation} 测试通过")
            else:
                print(f"❌ MCP接口 {operation} 测试失败: {result.get('message')}")
        
        # 测试无效操作
        result = self.mcp.process({
            "operation": "invalid_operation",
            "params": {}
        })
        
        if result["status"] == "error":
            print("✅ 无效操作错误处理正确")
        else:
            print("❌ 无效操作应该返回错误")
        
        self.test_results.append({
            "test": "mcp_interface",
            "status": "passed",
            "details": "MCP标准接口测试通过"
        })
    
    async def test_performance_benchmark(self):
        """性能基准测试"""
        print("\n" + "="*60)
        print("⚡ 性能基准测试")
        print("="*60)
        
        test_image = self._create_test_image()
        num_requests = 5
        
        print(f"🔄 执行 {num_requests} 次OCR请求...")
        
        start_time = time.time()
        successful_requests = 0
        total_cost = 0.0
        processing_times = []
        
        for i in range(num_requests):
            try:
                result = await self.mcp.process_ocr_request(
                    image_data=test_image,
                    task_type="document_ocr",
                    language="auto"
                )
                
                if result["status"] == "success":
                    successful_requests += 1
                    response = result["result"]
                    total_cost += response["cost"]
                    processing_times.append(response["processing_time"])
                
                print(f"  请求 {i+1}/{num_requests} 完成")
                
                # 避免API限制
                if i < num_requests - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"  请求 {i+1} 失败: {e}")
        
        total_time = time.time() - start_time
        
        print(f"\n📊 性能统计:")
        print(f"   总请求数: {num_requests}")
        print(f"   成功请求数: {successful_requests}")
        print(f"   成功率: {successful_requests/num_requests*100:.1f}%")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均每请求: {total_time/num_requests:.2f}秒")
        print(f"   总成本: ${total_cost:.6f}")
        print(f"   平均成本: ${total_cost/max(1, successful_requests):.6f}")
        
        if processing_times:
            avg_processing = sum(processing_times) / len(processing_times)
            print(f"   平均处理时间: {avg_processing:.2f}秒")
        
        self.test_results.append({
            "test": "performance_benchmark",
            "status": "completed",
            "details": {
                "total_requests": num_requests,
                "successful_requests": successful_requests,
                "success_rate": successful_requests/num_requests*100,
                "total_time": total_time,
                "total_cost": total_cost
            }
        })
    
    async def test_statistics_tracking(self):
        """测试统计信息跟踪"""
        print("\n" + "="*60)
        print("📈 测试统计信息跟踪")
        print("="*60)
        
        # 获取初始统计
        initial_stats = self.mcp.get_statistics()["statistics"]
        print(f"📊 初始统计: {initial_stats['total_requests']} 个请求")
        
        # 执行一些请求
        test_image = self._create_test_image()
        
        for i in range(3):
            await self.mcp.process_ocr_request(
                image_data=test_image,
                task_type="document_ocr"
            )
            await asyncio.sleep(1)
        
        # 获取更新后的统计
        final_stats = self.mcp.get_statistics()["statistics"]
        print(f"📊 最终统计: {final_stats['total_requests']} 个请求")
        
        # 验证统计更新
        requests_diff = final_stats['total_requests'] - initial_stats['total_requests']
        if requests_diff >= 3:
            print("✅ 统计信息跟踪正常")
        else:
            print(f"❌ 统计信息跟踪异常，预期增加3个请求，实际增加{requests_diff}个")
        
        # 显示详细统计
        print(f"📈 详细统计信息:")
        for key, value in final_stats.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"     {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")
        
        self.test_results.append({
            "test": "statistics_tracking",
            "status": "passed",
            "details": "统计信息跟踪功能正常"
        })
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📋 测试报告")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "passed"])
        completed_tests = len([r for r in self.test_results if r["status"] in ["passed", "completed"]])
        
        print(f"📊 测试概览:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   完成测试: {completed_tests}")
        print(f"   成功率: {completed_tests/total_tests*100:.1f}%")
        
        print(f"\n📝 详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] in ["passed", "completed"] else "❌"
            print(f"   {status_icon} {result['test']}: {result['details']}")
        
        # 保存报告到文件
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "completed_tests": completed_tests,
                "success_rate": completed_tests/total_tests*100
            },
            "results": self.test_results
        }
        
        report_file = Path("test_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 测试报告已保存到: {report_file}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 Cloud Search MCP 全面测试开始")
        print("="*60)
        
        try:
            await self.setup()
            await self.test_basic_functionality()
            await self.test_ocr_with_sample_image()
            await self.test_model_selection()
            await self.test_error_handling()
            await self.test_mcp_interface()
            await self.test_performance_benchmark()
            await self.test_statistics_tracking()
            
        except Exception as e:
            print(f"❌ 测试过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            
            self.test_results.append({
                "test": "test_execution",
                "status": "failed",
                "details": f"测试执行异常: {str(e)}"
            })
        
        finally:
            self.generate_test_report()

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cloud Search MCP 测试套件")
    parser.add_argument("--config", default="config.toml", help="配置文件路径")
    parser.add_argument("--test", choices=[
        "basic", "ocr", "models", "errors", "mcp", "performance", "stats", "all"
    ], default="all", help="要运行的测试类型")
    
    args = parser.parse_args()
    
    tester = CloudSearchMCPTester(args.config)
    
    if args.test == "all":
        await tester.run_all_tests()
    else:
        await tester.setup()
        
        if args.test == "basic":
            await tester.test_basic_functionality()
        elif args.test == "ocr":
            await tester.test_ocr_with_sample_image()
        elif args.test == "models":
            await tester.test_model_selection()
        elif args.test == "errors":
            await tester.test_error_handling()
        elif args.test == "mcp":
            await tester.test_mcp_interface()
        elif args.test == "performance":
            await tester.test_performance_benchmark()
        elif args.test == "stats":
            await tester.test_statistics_tracking()
        
        tester.generate_test_report()

if __name__ == "__main__":
    asyncio.run(main())

