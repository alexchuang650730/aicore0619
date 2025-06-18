#!/usr/bin/env python3
"""
SmartUI MCP 命令行接口
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp.adapter.smartui_mcp.smartui_mcp import SmartUIMcp

async def main():
    parser = argparse.ArgumentParser(description='SmartUI MCP CLI')
    parser.add_argument('command', choices=['start', 'status', 'test', 'interact'], 
                       help='Command to execute')
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--session-id', type=str, help='Session ID for interaction')
    parser.add_argument('--input', type=str, help='User input for interaction')
    parser.add_argument('--workflow-type', type=str, help='Workflow type to create')
    
    args = parser.parse_args()
    
    # 加载配置
    config = {}
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return 1
    
    # 创建SmartUI MCP实例
    smartui_mcp = SmartUIMcp(config)
    
    try:
        if args.command == 'start':
            print("Starting SmartUI MCP...")
            await smartui_mcp.initialize()
            print(f"SmartUI MCP started successfully. Status: {smartui_mcp.status}")
            
        elif args.command == 'status':
            await smartui_mcp.initialize()
            status = await smartui_mcp.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif args.command == 'test':
            await smartui_mcp.initialize()
            
            # 测试用户输入
            test_data = {
                "type": "user_input",
                "session_id": "test_session_001",
                "user_id": "test_user",
                "input": "我想创建一个需求分析工作流",
                "input_type": "text"
            }
            
            result = await smartui_mcp.process(test_data)
            print("Test Result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.command == 'interact':
            await smartui_mcp.initialize()
            
            session_id = args.session_id or "cli_session_001"
            user_input = args.input or "Hello, SmartUI!"
            
            if args.workflow_type:
                # 创建工作流请求
                data = {
                    "type": "workflow_request",
                    "session_id": session_id,
                    "workflow_type": args.workflow_type,
                    "workflow_name": f"CLI_Workflow_{args.workflow_type}",
                    "description": f"Workflow created via CLI for {args.workflow_type}"
                }
            else:
                # 普通用户输入
                data = {
                    "type": "user_input",
                    "session_id": session_id,
                    "user_id": "cli_user",
                    "input": user_input,
                    "input_type": "text"
                }
            
            result = await smartui_mcp.process(data)
            print("Interaction Result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        await smartui_mcp.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

