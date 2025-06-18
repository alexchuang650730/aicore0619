#!/usr/bin/env python3
"""
Local Model MCP 命令行接口
支持Qwen 8B和Mistral 12B的环境自适应端云模型，集成OCR功能
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

from mcp.adapter.local_model_mcp import LocalModelMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalModelMCPCLI:
    """Local Model MCP 命令行接口"""
    
    def __init__(self):
        self.mcp = None
        
    async def initialize_mcp(self, config_path: Optional[str] = None) -> bool:
        """初始化MCP"""
        try:
            self.mcp = LocalModelMCP(config_path)
            return await self.mcp.initialize()
        except Exception as e:
            logger.error(f"MCP初始化失败: {e}")
            return False
    
    async def cmd_status(self, args) -> Dict[str, Any]:
        """获取MCP状态"""
        if not self.mcp:
            return {"error": "MCP未初始化"}
        
        return await self.mcp.get_status()
    
    async def cmd_capabilities(self, args) -> Dict[str, Any]:
        """获取MCP能力"""
        if not self.mcp:
            return {"error": "MCP未初始化"}
        
        return await self.mcp.get_capabilities()
    
    async def cmd_generate(self, args) -> Dict[str, Any]:
        """文本生成"""
        if not self.mcp:
            return {"error": "MCP未初始化"}
        
        kwargs = {}
        if args.model:
            kwargs["model"] = args.model
        if args.max_tokens:
            kwargs["max_tokens"] = args.max_tokens
        if args.temperature:
            kwargs["temperature"] = args.temperature
        
        return await self.mcp.text_generation(args.prompt, **kwargs)
    
    async def cmd_chat(self, args) -> Dict[str, Any]:
        """聊天对话"""
        if not self.mcp:
            return {"error": "MCP未初始化"}
        
        # 构建消息列表
        messages = []
        if args.system:
            messages.append({"role": "system", "content": args.system})
        messages.append({"role": "user", "content": args.message})
        
        kwargs = {}
        if args.model:
            kwargs["model"] = args.model
        if args.max_tokens:
            kwargs["max_tokens"] = args.max_tokens
        if args.temperature:
            kwargs["temperature"] = args.temperature
        
        return await self.mcp.chat_completion(messages, **kwargs)
    
    async def cmd_ocr(self, args) -> Dict[str, Any]:
        """OCR文本识别"""
        if not self.mcp:
            return {"error": "MCP未初始化"}
        
        try:
            # 读取图像文件
            with open(args.image, 'rb') as f:
                image_data = f.read()
            
            kwargs = {}
            if args.clean_text:
                kwargs["clean_text"] = True
            if args.remove_special_chars:
                kwargs["remove_special_chars"] = True
            
            return await self.mcp.ocr_processing(image_data, **kwargs)
            
        except FileNotFoundError:
            return {"error": f"图像文件不存在: {args.image}"}
        except Exception as e:
            return {"error": f"OCR处理失败: {e}"}
    
    async def cmd_interactive(self, args):
        """交互式模式"""
        if not self.mcp:
            print("错误: MCP未初始化")
            return
        
        print("=== Local Model MCP 交互式模式 ===")
        print("命令:")
        print("  /status - 查看状态")
        print("  /switch <model> - 切换模型 (qwen/mistral)")
        print("  /ocr <image_path> - OCR识别")
        print("  /quit - 退出")
        print("  其他输入将作为对话消息发送")
        print()
        
        conversation_history = []
        
        while True:
            try:
                user_input = input(">>> ").strip()
                
                if not user_input:
                    continue
                
                if user_input == "/quit":
                    break
                elif user_input == "/status":
                    status = await self.mcp.get_status()
                    print(json.dumps(status, indent=2, ensure_ascii=False))
                elif user_input.startswith("/switch "):
                    model_name = user_input[8:].strip()
                    if model_name in ["qwen", "mistral"]:
                        result = await self.mcp._switch_model(model_name)
                        if result:
                            print(f"已切换到模型: {model_name}")
                        else:
                            print(f"模型切换失败: {model_name}")
                    else:
                        print("支持的模型: qwen, mistral")
                elif user_input.startswith("/ocr "):
                    image_path = user_input[5:].strip()
                    try:
                        with open(image_path, 'rb') as f:
                            image_data = f.read()
                        result = await self.mcp.ocr_processing(image_data)
                        if result["success"]:
                            print(f"OCR结果:\n{result['result']['text']}")
                        else:
                            print(f"OCR失败: {result['error']}")
                    except Exception as e:
                        print(f"OCR处理失败: {e}")
                else:
                    # 普通对话
                    conversation_history.append({"role": "user", "content": user_input})
                    
                    result = await self.mcp.chat_completion(conversation_history)
                    
                    if result["success"]:
                        response = result["response"]["message"]["content"]
                        print(f"Assistant: {response}")
                        conversation_history.append({"role": "assistant", "content": response})
                    else:
                        print(f"对话失败: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n退出交互模式")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    async def cleanup(self):
        """清理资源"""
        if self.mcp:
            await self.mcp.shutdown()

def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Local Model MCP - 环境自适应的本地模型MCP适配器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s status                           # 查看状态
  %(prog)s generate "你好，请介绍一下你自己"      # 文本生成
  %(prog)s chat "什么是人工智能？"             # 聊天对话
  %(prog)s ocr image.png                   # OCR识别
  %(prog)s interactive                     # 交互式模式
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # status命令
    status_parser = subparsers.add_parser("status", help="查看MCP状态")
    
    # capabilities命令
    capabilities_parser = subparsers.add_parser("capabilities", help="查看MCP能力")
    
    # generate命令
    generate_parser = subparsers.add_parser("generate", help="文本生成")
    generate_parser.add_argument("prompt", help="生成提示")
    generate_parser.add_argument("--model", choices=["qwen", "mistral"], help="指定模型")
    generate_parser.add_argument("--max-tokens", type=int, help="最大token数")
    generate_parser.add_argument("--temperature", type=float, help="温度参数")
    
    # chat命令
    chat_parser = subparsers.add_parser("chat", help="聊天对话")
    chat_parser.add_argument("message", help="对话消息")
    chat_parser.add_argument("--system", help="系统提示")
    chat_parser.add_argument("--model", choices=["qwen", "mistral"], help="指定模型")
    chat_parser.add_argument("--max-tokens", type=int, help="最大token数")
    chat_parser.add_argument("--temperature", type=float, help="温度参数")
    
    # ocr命令
    ocr_parser = subparsers.add_parser("ocr", help="OCR文本识别")
    ocr_parser.add_argument("image", help="图像文件路径")
    ocr_parser.add_argument("--clean-text", action="store_true", help="清理文本")
    ocr_parser.add_argument("--remove-special-chars", action="store_true", help="移除特殊字符")
    
    # interactive命令
    interactive_parser = subparsers.add_parser("interactive", help="交互式模式")
    
    return parser

async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建CLI实例
    cli = LocalModelMCPCLI()
    
    try:
        # 初始化MCP
        if not await cli.initialize_mcp(args.config):
            print("错误: MCP初始化失败", file=sys.stderr)
            return 1
        
        # 执行命令
        if args.command == "status":
            result = await cli.cmd_status(args)
        elif args.command == "capabilities":
            result = await cli.cmd_capabilities(args)
        elif args.command == "generate":
            result = await cli.cmd_generate(args)
        elif args.command == "chat":
            result = await cli.cmd_chat(args)
        elif args.command == "ocr":
            result = await cli.cmd_ocr(args)
        elif args.command == "interactive":
            await cli.cmd_interactive(args)
            return 0
        else:
            parser.print_help()
            return 1
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return 0
        
    except KeyboardInterrupt:
        print("\n操作被用户中断", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

