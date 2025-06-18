#!/usr/bin/env python3
"""
SmartUI MCP 组件启动脚本
用于启动和管理SmartUI MCP的各个智能组件
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.main_server import SmartUIMCPServer
    from src.config.config_manager import ConfigManager
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在SmartUI MCP项目根目录运行此脚本")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_components():
    """启动SmartUI MCP组件"""
    try:
        logger.info("🚀 开始启动SmartUI MCP组件...")
        
        # 初始化配置管理器
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # 创建服务器实例
        server = SmartUIMCPServer(config)
        
        # 启动组件
        logger.info("📦 正在启动核心组件...")
        await server.start()
        
        logger.info("✅ SmartUI MCP组件启动成功!")
        logger.info("🌐 服务器运行在: http://localhost:8080")
        logger.info("📊 健康检查: http://localhost:8080/health")
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 收到停止信号...")
            await server.stop()
            logger.info("✅ SmartUI MCP组件已停止")
            
    except Exception as e:
        logger.error(f"❌ 组件启动失败: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(start_components())
    except KeyboardInterrupt:
        logger.info("👋 用户中断，程序退出")
    except Exception as e:
        logger.error(f"💥 程序异常退出: {e}")
        sys.exit(1)

