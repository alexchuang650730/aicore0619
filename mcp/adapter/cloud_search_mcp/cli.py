#!/usr/bin/env python3
"""
Cloud Search MCP CLI

命令行接口，用于测试和管理Cloud Search MCP。

使用方法:
    python cli.py --test --image test.jpg --task-type document_ocr
    python cli.py --health-check
    python cli.py --list-models
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

from cloud_search_mcp import CloudSearchMCP, TaskType

async def test_ocr(config_path: str, image_path: str, task_type: str, language: str = "auto"):
    """测试OCR功能"""
    
    if not Path(image_path).exists():
        print(f"❌ 图像文件不存在: {image_path}")
        return
    
    try:
        # 读取图像
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        print(f"📄 读取图像: {image_path} ({len(image_data)} bytes)")
        
        # 初始化MCP
        mcp = CloudSearchMCP(config_path)
        print(f"🚀 Cloud Search MCP 已初始化")
        print(f"📊 可用模型: {list(mcp.model_configs.keys())}")
        
        # 处理请求
        print(f"\n🔍 开始OCR处理...")
        print(f"   任务类型: {task_type}")
        print(f"   语言: {language}")
        
        result = await mcp.process_ocr_request(
            image_data=image_data,
            task_type=task_type,
            language=language,
            output_format="markdown"
        )
        
        # 显示结果
        print("\n" + "=" * 60)
        print("🎯 OCR处理结果")
        print("=" * 60)
        
        if result["status"] == "success":
            response = result["result"]
            print(f"✅ 状态: 成功")
            print(f"🤖 使用模型: {response['model_used']}")
            print(f"📊 置信度: {response['confidence']:.2%}")
            print(f"⏱️  处理时间: {response['processing_time']:.2f}秒")
            print(f"💰 成本: ${response['cost']:.6f}")
            
            if response.get('error'):
                print(f"⚠️  警告: {response['error']}")
            
            print(f"\n📝 OCR内容:")
            print("-" * 40)
            print(response['content'])
            print("-" * 40)
            
        else:
            print(f"❌ 状态: 失败")
            print(f"💥 错误: {result.get('message', '未知错误')}")
        
        print("=" * 60)
        
        # 显示统计信息
        stats_result = mcp.get_statistics()
        if stats_result["status"] == "success":
            stats = stats_result["statistics"]
            print(f"\n📈 统计信息:")
            print(f"   总请求数: {stats['total_requests']}")
            print(f"   成功率: {stats['successful_requests']}/{stats['total_requests']}")
            print(f"   总成本: ${stats['total_cost']:.6f}")
            print(f"   平均处理时间: {stats['average_processing_time']:.2f}秒")
            
            if stats['model_usage']:
                print(f"   模型使用情况:")
                for model, count in stats['model_usage'].items():
                    print(f"     {model}: {count}次")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def health_check(config_path: str):
    """健康检查"""
    try:
        mcp = CloudSearchMCP(config_path)
        result = mcp.health_check()
        
        print("🏥 Cloud Search MCP 健康检查")
        print("=" * 40)
        
        if result["status"] == "success":
            health = result["health"]
            print(f"✅ 服务状态: {health['service']}")
            print(f"🤖 可用模型数: {health['enabled_models']}")
            print(f"📊 总请求数: {health['total_requests']}")
            print(f"📈 成功率: {health['success_rate']:.1f}%")
            print(f"💰 平均成本: ${health['average_cost']:.6f}")
            print(f"⏱️  平均处理时间: {health['average_processing_time']:.2f}秒")
        else:
            print(f"❌ 健康检查失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")

def list_models(config_path: str):
    """列出支持的模型"""
    try:
        mcp = CloudSearchMCP(config_path)
        result = mcp.get_supported_models()
        
        print("🤖 支持的模型列表")
        print("=" * 60)
        
        if result["status"] == "success":
            models = result["models"]
            
            if not models:
                print("❌ 没有配置可用的模型")
                return
            
            print(f"{'模型名称':<30} {'启用':<6} {'质量':<6} {'速度':<6} {'成本/1K':<10}")
            print("-" * 60)
            
            for model in models:
                enabled = "✅" if model['enabled'] else "❌"
                quality = f"{model['quality_score']:.2f}"
                speed = f"{model['speed_score']:.2f}"
                cost = f"${model['cost_per_1k_tokens']:.6f}"
                
                print(f"{model['model_id']:<30} {enabled:<6} {quality:<6} {speed:<6} {cost:<10}")
        else:
            print(f"❌ 获取模型列表失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 列出模型异常: {e}")

def list_capabilities(config_path: str):
    """列出MCP能力"""
    try:
        mcp = CloudSearchMCP(config_path)
        result = mcp.get_capabilities()
        
        print("🎯 Cloud Search MCP 能力")
        print("=" * 40)
        
        if result["status"] == "success":
            capabilities = result["capabilities"]
            formats = result["supported_formats"]
            languages = result["supported_languages"]
            
            print("📋 支持的任务类型:")
            for cap in capabilities:
                print(f"   • {cap}")
            
            print(f"\n📁 支持的图像格式:")
            for fmt in formats:
                print(f"   • {fmt}")
            
            print(f"\n🌐 支持的语言:")
            for lang in languages:
                print(f"   • {lang}")
        else:
            print(f"❌ 获取能力列表失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 列出能力异常: {e}")

def interactive_mode(config_path: str):
    """交互模式"""
    print("🎮 Cloud Search MCP 交互模式")
    print("=" * 40)
    print("可用命令:")
    print("  test <image_path> [task_type] [language] - 测试OCR")
    print("  health - 健康检查")
    print("  models - 列出模型")
    print("  capabilities - 列出能力")
    print("  stats - 显示统计")
    print("  quit - 退出")
    print("-" * 40)
    
    mcp = None
    
    while True:
        try:
            command = input("\n> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == "quit" or cmd == "exit":
                print("👋 再见!")
                break
            
            elif cmd == "test":
                if len(command) < 2:
                    print("❌ 用法: test <image_path> [task_type] [language]")
                    continue
                
                image_path = command[1]
                task_type = command[2] if len(command) > 2 else "document_ocr"
                language = command[3] if len(command) > 3 else "auto"
                
                await test_ocr(config_path, image_path, task_type, language)
            
            elif cmd == "health":
                health_check(config_path)
            
            elif cmd == "models":
                list_models(config_path)
            
            elif cmd == "capabilities":
                list_capabilities(config_path)
            
            elif cmd == "stats":
                if not mcp:
                    mcp = CloudSearchMCP(config_path)
                
                result = mcp.get_statistics()
                if result["status"] == "success":
                    print(json.dumps(result["statistics"], indent=2, ensure_ascii=False))
                else:
                    print(f"❌ 获取统计失败: {result.get('message')}")
            
            else:
                print(f"❌ 未知命令: {cmd}")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Cloud Search MCP CLI - 云端视觉搜索MCP命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 测试OCR功能
  python cli.py --test --image test.jpg --task-type document_ocr
  
  # 健康检查
  python cli.py --health-check
  
  # 列出支持的模型
  python cli.py --list-models
  
  # 交互模式
  python cli.py --interactive
        """
    )
    
    parser.add_argument("--config", default="config.toml", 
                       help="配置文件路径 (默认: config.toml)")
    
    # 测试相关参数
    parser.add_argument("--test", action="store_true", 
                       help="运行OCR测试")
    parser.add_argument("--image", 
                       help="测试图像路径")
    parser.add_argument("--task-type", default="document_ocr",
                       choices=[t.value for t in TaskType],
                       help="OCR任务类型")
    parser.add_argument("--language", default="auto",
                       help="识别语言 (默认: auto)")
    
    # 信息查询参数
    parser.add_argument("--health-check", action="store_true",
                       help="执行健康检查")
    parser.add_argument("--list-models", action="store_true",
                       help="列出支持的模型")
    parser.add_argument("--list-capabilities", action="store_true",
                       help="列出MCP能力")
    
    # 交互模式
    parser.add_argument("--interactive", action="store_true",
                       help="启动交互模式")
    
    args = parser.parse_args()
    
    # 检查配置文件
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print(f"请创建配置文件或使用 --config 指定正确的路径")
        return 1
    
    try:
        if args.test:
            if not args.image:
                print("❌ 测试模式需要指定图像路径: --image <path>")
                return 1
            
            asyncio.run(test_ocr(args.config, args.image, args.task_type, args.language))
        
        elif args.health_check:
            health_check(args.config)
        
        elif args.list_models:
            list_models(args.config)
        
        elif args.list_capabilities:
            list_capabilities(args.config)
        
        elif args.interactive:
            asyncio.run(interactive_mode(args.config))
        
        else:
            # 默认显示帮助
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

