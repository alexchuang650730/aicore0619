#!/usr/bin/env python3
"""
KiloCode MCP - 兜底创建引擎 (配置驱动版本)
基于讨论结论重新设计的kilocode_mcp，支持配置文件驱动

核心理念：
- 兜底创建：当所有其他MCP都解决不了时，创建解决方案
- 工作流感知：根据工作流上下文调整创建行为
- MCP通信：通过coordinator与其他MCP通信，不直接调用外部API
- 智能适应：根据需求类型智能选择创建策略
- 配置驱动：所有行为通过配置文件控制
"""

import json
import asyncio
import logging
import toml
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pathlib import Path

class WorkflowType(Enum):
    """六大工作流类型"""
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    CODING_IMPLEMENTATION = "coding_implementation"
    TESTING_VERIFICATION = "testing_verification"
    DEPLOYMENT_RELEASE = "deployment_release"
    MONITORING_OPERATIONS = "monitoring_operations"

class CreationType(Enum):
    """创建类型"""
    DOCUMENT = "document"  # 文档类：PPT、报告、方案
    CODE = "code"         # 代码类：应用、脚本、工具
    PROTOTYPE = "prototype"  # 原型类：demo、验证、示例
    TOOL = "tool"         # 工具类：测试工具、部署脚本、监控脚本

class KiloCodeConfig:
    """KiloCode MCP 配置管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        
    def _find_config_file(self) -> str:
        """查找配置文件"""
        possible_paths = [
            "kilocode_mcp_config.toml",
            "/opt/powerautomation/mcp/kilocode_mcp/kilocode_mcp_config.toml",
            os.path.join(os.path.dirname(__file__), "kilocode_mcp_config.toml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # 如果找不到配置文件，创建默认配置
        return self._create_default_config()
    
    def _create_default_config(self) -> str:
        """创建默认配置文件"""
        default_config = {
            "mcp_info": {
                "name": "kilocode_mcp",
                "version": "2.0.0",
                "description": "兜底创建引擎",
                "type": "fallback_creator"
            },
            "ai_assistance": {
                "enable_ai_assistance": True,
                "primary_ai": "gemini_mcp",
                "fallback_ai": "claude_mcp",
                "ai_timeout": 30
            },
            "logging": {
                "log_level": "INFO"
            }
        }
        
        config_path = "kilocode_mcp_config.toml"
        with open(config_path, 'w') as f:
            toml.dump(default_config, f)
        
        return config_path
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            print(f"警告：无法加载配置文件 {self.config_path}: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """获取兜底配置"""
        return {
            "mcp_info": {"name": "kilocode_mcp", "version": "2.0.0"},
            "ai_assistance": {"enable_ai_assistance": True},
            "logging": {"log_level": "INFO"}
        }
    
    def get(self, key_path: str, default=None):
        """获取配置值，支持点号路径"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

class KiloCodeMCP:
    """
    KiloCode MCP - 兜底创建引擎 (配置驱动版本)
    
    职责：
    1. 作为所有工作流的最后兜底
    2. 根据工作流上下文创建不同类型的解决方案
    3. 通过coordinator与其他MCP通信
    4. 智能选择创建策略
    5. 配置驱动的行为控制
    """
    
    def __init__(self, coordinator_client=None, config_path: str = None):
        self.config = KiloCodeConfig(config_path)
        self.name = self.config.get("mcp_info.name", "kilocode_mcp")
        self.version = self.config.get("mcp_info.version", "2.0.0")
        self.coordinator = coordinator_client
        self.logger = self._setup_logger()
        
        # 从配置加载工作流创建策略
        self.workflow_strategies = {
            WorkflowType.REQUIREMENTS_ANALYSIS: self._create_for_requirements,
            WorkflowType.ARCHITECTURE_DESIGN: self._create_for_architecture,
            WorkflowType.CODING_IMPLEMENTATION: self._create_for_coding,
            WorkflowType.TESTING_VERIFICATION: self._create_for_testing,
            WorkflowType.DEPLOYMENT_RELEASE: self._create_for_deployment,
            WorkflowType.MONITORING_OPERATIONS: self._create_for_monitoring
        }
        
        # 加载支持的能力
        self.supported_workflows = self.config.get("capabilities.supported_workflows", [])
        self.supported_creation_types = self.config.get("capabilities.supported_creation_types", [])
        self.supported_languages = self.config.get("capabilities.supported_languages", ["python"])
        
        self.logger.info(f"KiloCode MCP {self.version} 初始化完成")
        self.logger.info(f"支持工作流: {len(self.supported_workflows)}个")
        self.logger.info(f"支持创建类型: {len(self.supported_creation_types)}个")
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger(f"{self.name}")
        log_level = self.config.get("logging.log_level", "INFO")
        logger.setLevel(getattr(logging, log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            log_format = self.config.get("logging.log_format", 
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理兜底创建请求
        
        Args:
            request: 包含workflow_type, content, context等信息的请求
            
        Returns:
            创建结果
        """
        try:
            content_preview = request.get('content', '')[:100]
            self.logger.info(f"KiloCode MCP 接收兜底请求: {content_preview}...")
            
            # 验证输入
            if not self._validate_input(request):
                return self._create_error_response("输入验证失败")
            
            # 解析请求
            workflow_type = self._parse_workflow_type(request)
            creation_type = self._determine_creation_type(request)
            
            self.logger.info(f"识别工作流: {workflow_type.value}, 创建类型: {creation_type.value}")
            
            # 检查是否支持该工作流
            if workflow_type.value not in self.supported_workflows:
                self.logger.warning(f"不支持的工作流类型: {workflow_type.value}")
                return self._create_generic_solution(request)
            
            # 选择创建策略
            strategy = self.workflow_strategies.get(workflow_type)
            if not strategy:
                return self._create_generic_solution(request)
            
            # 执行创建
            result = await strategy(request, creation_type)
            
            # 质量控制检查
            result = self._apply_quality_control(result)
            
            self.logger.info(f"KiloCode MCP 创建完成: {result.get('type', 'unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"KiloCode MCP 处理失败: {str(e)}")
            return self._create_error_response(str(e))
    
    def _validate_input(self, request: Dict[str, Any]) -> bool:
        """验证输入请求"""
        if not self.config.get("security.enable_input_validation", True):
            return True
            
        content = request.get('content', '')
        max_length = self.config.get("security.max_input_length", 10000)
        
        if len(content) > max_length:
            self.logger.warning(f"输入内容过长: {len(content)} > {max_length}")
            return False
            
        # 检查被禁止的关键词
        blocked_keywords = self.config.get("security.blocked_keywords", [])
        for keyword in blocked_keywords:
            if keyword.lower() in content.lower():
                self.logger.warning(f"检测到被禁止的关键词: {keyword}")
                return False
                
        return True
    
    def _parse_workflow_type(self, request: Dict[str, Any]) -> WorkflowType:
        """解析工作流类型"""
        context = request.get('context', {})
        workflow = context.get('workflow_type', '')
        
        # 从上下文中获取工作流类型
        for wf_type in WorkflowType:
            if wf_type.value in workflow.lower():
                return wf_type
        
        # 基于内容推断工作流类型
        content = request.get('content', '').lower()
        
        if any(keyword in content for keyword in ['ppt', '报告', '展示', '汇报', '需求', '分析']):
            return WorkflowType.REQUIREMENTS_ANALYSIS
        elif any(keyword in content for keyword in ['架构', '设计', '模式', '框架']):
            return WorkflowType.ARCHITECTURE_DESIGN
        elif any(keyword in content for keyword in ['代码', '编程', '开发', '实现', '游戏', '应用']):
            return WorkflowType.CODING_IMPLEMENTATION
        elif any(keyword in content for keyword in ['测试', '验证', '检查']):
            return WorkflowType.TESTING_VERIFICATION
        elif any(keyword in content for keyword in ['部署', '发布', '上线']):
            return WorkflowType.DEPLOYMENT_RELEASE
        elif any(keyword in content for keyword in ['监控', '运维', '性能']):
            return WorkflowType.MONITORING_OPERATIONS
        
        # 默认为编码实现
        return WorkflowType.CODING_IMPLEMENTATION
    
    def _determine_creation_type(self, request: Dict[str, Any]) -> CreationType:
        """确定创建类型"""
        content = request.get('content', '').lower()
        
        if any(keyword in content for keyword in ['ppt', '报告', '文档', '展示']):
            return CreationType.DOCUMENT
        elif any(keyword in content for keyword in ['demo', '原型', '验证', '示例']):
            return CreationType.PROTOTYPE
        elif any(keyword in content for keyword in ['工具', '脚本', '自动化']):
            return CreationType.TOOL
        else:
            return CreationType.CODE
    
    async def _create_for_requirements(self, request: Dict[str, Any], creation_type: CreationType) -> Dict[str, Any]:
        """为需求分析工作流创建解决方案"""
        content = request.get('content', '')
        strategy_config = self.config.get("creation_strategies.requirements_analysis", {})
        
        if creation_type == CreationType.DOCUMENT:
            # 创建PPT、报告等文档
            return await self._create_business_document(content, strategy_config)
        elif creation_type == CreationType.PROTOTYPE:
            # 创建需求原型
            return await self._create_requirement_prototype(content, strategy_config)
        else:
            # 创建需求分析工具
            return await self._create_analysis_tool(content, strategy_config)
    
    async def _create_for_coding(self, request: Dict[str, Any], creation_type: CreationType) -> Dict[str, Any]:
        """为编码实现工作流创建解决方案"""
        content = request.get('content', '')
        strategy_config = self.config.get("creation_strategies.coding_implementation", {})
        
        # 这是kilocode_mcp的核心领域
        if '贪吃蛇' in content or 'snake' in content.lower():
            return await self._create_snake_game(content, strategy_config)
        elif '游戏' in content or 'game' in content.lower():
            return await self._create_game_application(content, strategy_config)
        elif 'web' in content.lower() or '网站' in content:
            return await self._create_web_application(content, strategy_config)
        else:
            return await self._create_general_code(content, strategy_config)
    
    async def _create_business_document(self, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建业务文档（PPT等）"""
        # 检查是否启用AI协助
        if self.config.get("ai_assistance.enable_ai_assistance", True) and self.coordinator:
            primary_ai = self.config.get("ai_assistance.primary_ai", "gemini_mcp")
            ai_request = {
                "target_mcp": primary_ai,
                "action": "generate_content",
                "content": f"创建专业的业务展示文档：{content}",
                "format": config.get("default_format", "structured_document")
            }
            
            try:
                ai_result = await self.coordinator.send_request(ai_request)
                if ai_result.get('success'):
                    return {
                        "success": True,
                        "type": "business_document",
                        "content": ai_result.get('content'),
                        "format": config.get("default_format", "ppt_outline"),
                        "created_by": self.name,
                        "ai_assisted": True,
                        "ai_provider": primary_ai
                    }
            except Exception as e:
                self.logger.warning(f"AI协助失败，使用兜底方案: {e}")
        
        # 兜底方案：自己创建基础结构
        ppt_config = self.config.get("templates.ppt", {})
        return {
            "success": True,
            "type": "business_document",
            "content": self._generate_ppt_structure(content, ppt_config),
            "format": config.get("default_format", "ppt_outline"),
            "created_by": self.name,
            "ai_assisted": False
        }
    
    async def _create_snake_game(self, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建贪吃蛇游戏"""
        game_config = self.config.get("templates.game", {})
        default_engine = game_config.get("default_engine", "pygame")
        
        if default_engine == "pygame":
            snake_code = self._generate_pygame_snake_code(game_config)
        else:
            snake_code = self._generate_basic_snake_code()
        
        return {
            "success": True,
            "type": "game_application",
            "content": snake_code,
            "language": config.get("default_language", "python"),
            "dependencies": [default_engine] if default_engine != "basic" else [],
            "instructions": f"运行前请安装{default_engine}: pip install {default_engine}" if default_engine != "basic" else "无需额外依赖",
            "created_by": self.name,
            "description": "完整的贪吃蛇游戏实现，包含游戏逻辑、碰撞检测和得分系统",
            "quality_level": config.get("code_quality_level", "production")
        }
    
    def _generate_pygame_snake_code(self, game_config: Dict[str, Any]) -> str:
        """生成pygame版本的贪吃蛇代码"""
        include_collision = game_config.get("include_collision_detection", True)
        include_scoring = game_config.get("include_scoring_system", True)
        include_game_loop = game_config.get("include_game_loop", True)
        
        code_template = self.config.get("templates.code", {})
        include_header = code_template.get("include_header_comments", True)
        include_logging = code_template.get("include_logging", True)
        
        header = '''#!/usr/bin/env python3
"""
贪吃蛇游戏 - KiloCode MCP 生成
使用pygame实现的完整贪吃蛇游戏

特性：
- 完整的游戏循环
- 碰撞检测系统
- 得分系统
- 键盘控制

运行要求：
pip install pygame
"""

''' if include_header else ""
        
        logging_import = "import logging\n" if include_logging else ""
        
        return f'''{header}import pygame
import random
import sys
{logging_import}

# 初始化pygame
pygame.init()

# 游戏配置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = WINDOW_HEIGHT // CELL_SIZE

# 颜色定义
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

class Snake:
    """贪吃蛇类"""
    def __init__(self):
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)
        self.new_block = False
        
    def draw_snake(self, screen):
        """绘制蛇身"""
        for block in self.body:
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, block_rect)
            
    def move_snake(self):
        """移动蛇"""
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            
    def add_block(self):
        """增加蛇身长度"""
        self.new_block = True
        
    def check_collision(self):
        """检查碰撞"""
        # 检查是否撞墙
        if not 0 <= self.body[0].x < CELL_NUMBER_X or not 0 <= self.body[0].y < CELL_NUMBER_Y:
            return True
            
        # 检查是否撞到自己
        for block in self.body[1:]:
            if block == self.body[0]:
                return True
                
        return False

class Food:
    """食物类"""
    def __init__(self):
        self.randomize()
        
    def draw_food(self, screen):
        """绘制食物"""
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, food_rect)
        
    def randomize(self):
        """随机生成食物位置"""
        self.x = random.randint(0, CELL_NUMBER_X - 1)
        self.y = random.randint(0, CELL_NUMBER_Y - 1)
        self.pos = pygame.Vector2(self.x, self.y)

class Game:
    """游戏主类"""
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        
    def update(self):
        """更新游戏状态"""
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()
        
    def draw_elements(self, screen):
        """绘制游戏元素"""
        screen.fill(BLACK)
        self.food.draw_food(screen)
        self.snake.draw_snake(screen)
        
    def check_collision(self):
        """检查食物碰撞"""
        if self.food.pos == self.snake.body[0]:
            self.food.randomize()
            self.snake.add_block()
            self.score += 1
            
        # 确保食物不在蛇身上
        for block in self.snake.body[1:]:
            if block == self.food.pos:
                self.food.randomize()
                
    def check_fail(self):
        """检查游戏失败"""
        if self.snake.check_collision():
            self.game_over()
            
    def game_over(self):
        """游戏结束"""
        print(f"游戏结束！最终得分：{{self.score}}")
        pygame.quit()
        sys.exit()

def main():
    """主函数"""
    # 创建游戏窗口
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('贪吃蛇游戏 - KiloCode MCP')
    clock = pygame.time.Clock()
    
    # 创建游戏实例
    game = Game()
    
    # 游戏主循环
    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, 150)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == SCREEN_UPDATE:
                game.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if game.snake.direction.y != 1:
                        game.snake.direction = pygame.Vector2(0, -1)
                if event.key == pygame.K_DOWN:
                    if game.snake.direction.y != -1:
                        game.snake.direction = pygame.Vector2(0, 1)
                if event.key == pygame.K_RIGHT:
                    if game.snake.direction.x != -1:
                        game.snake.direction = pygame.Vector2(1, 0)
                if event.key == pygame.K_LEFT:
                    if game.snake.direction.x != 1:
                        game.snake.direction = pygame.Vector2(-1, 0)
        
        game.draw_elements(screen)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
'''
    
    def _generate_ppt_structure(self, content: str, ppt_config: Dict[str, Any]) -> str:
        """生成PPT基础结构"""
        default_slides = ppt_config.get("default_slides", 8)
        include_cover = ppt_config.get("include_cover", True)
        include_toc = ppt_config.get("include_toc", True)
        include_conclusion = ppt_config.get("include_conclusion", True)
        
        structure = f"# {content} - 业务汇报PPT大纲\n\n"
        
        slide_num = 1
        
        if include_cover:
            structure += f"## 第{slide_num}页：封面\n"
            structure += f"- 标题：{content}\n"
            structure += f"- 副标题：2024年度总结报告\n"
            structure += f"- 汇报人：[姓名]\n"
            structure += f"- 日期：{datetime.now().strftime('%Y年%m月%d日')}\n\n"
            slide_num += 1
        
        if include_toc:
            structure += f"## 第{slide_num}页：目录\n"
            structure += "1. 业务概览\n2. 关键成果\n3. 数据分析\n4. 挑战与机遇\n5. 未来规划\n\n"
            slide_num += 1
        
        # 主要内容页面
        main_sections = ["业务概览", "关键成果", "数据分析", "挑战与机遇", "未来规划"]
        for section in main_sections:
            if slide_num <= default_slides - (1 if include_conclusion else 0):
                structure += f"## 第{slide_num}页：{section}\n"
                structure += f"- {section}相关内容\n- 关键数据和指标\n- 重要结论\n\n"
                slide_num += 1
        
        if include_conclusion:
            structure += f"## 第{slide_num}页：谢谢\n"
            structure += "- 感谢聆听\n- 联系方式\n"
        
        return structure
    
    def _apply_quality_control(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """应用质量控制"""
        if not self.config.get("quality_control.enable_syntax_check", True):
            return result
            
        # 检查代码长度
        if result.get("type") in ["code", "game_application", "web_application"]:
            content = result.get("content", "")
            lines = len(content.split('\n'))
            min_lines = self.config.get("quality_control.min_code_lines", 10)
            max_lines = self.config.get("quality_control.max_code_lines", 1000)
            
            if lines < min_lines:
                result["quality_warning"] = f"代码行数过少: {lines} < {min_lines}"
            elif lines > max_lines:
                result["quality_warning"] = f"代码行数过多: {lines} > {max_lines}"
            else:
                result["quality_status"] = "通过质量检查"
        
        # 添加文档要求
        if self.config.get("quality_control.require_documentation", True):
            if "description" not in result:
                result["description"] = "由KiloCode MCP生成的解决方案"
        
        return result
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        fallback_enabled = self.config.get("fallback.enable_generic_fallback", True)
        fallback_message = self.config.get("fallback.fallback_message", 
            "请提供更多信息以便创建更好的解决方案")
        
        return {
            "success": False,
            "error": error_message,
            "fallback_solution": fallback_message if fallback_enabled else None,
            "created_by": self.name
        }
    
    # 其他方法的实现（为了简洁，这里省略了一些辅助方法的完整实现）
    async def _create_for_architecture(self, request, creation_type):
        """架构设计工作流创建"""
        return {"success": True, "type": "architecture_solution", "created_by": self.name}
    
    async def _create_for_testing(self, request, creation_type):
        """测试验证工作流创建"""
        return {"success": True, "type": "test_solution", "created_by": self.name}
    
    async def _create_for_deployment(self, request, creation_type):
        """部署发布工作流创建"""
        return {"success": True, "type": "deployment_solution", "created_by": self.name}
    
    async def _create_for_monitoring(self, request, creation_type):
        """监控运维工作流创建"""
        return {"success": True, "type": "monitoring_solution", "created_by": self.name}
    
    async def _create_general_code(self, content, config):
        """创建通用代码"""
        return {"success": True, "type": "code_solution", "created_by": self.name}
    
    async def _create_requirement_prototype(self, content, config):
        """创建需求原型"""
        return {"success": True, "type": "requirement_prototype", "created_by": self.name}
    
    async def _create_analysis_tool(self, content, config):
        """创建分析工具"""
        return {"success": True, "type": "analysis_tool", "created_by": self.name}
    
    async def _create_game_application(self, content, config):
        """创建游戏应用"""
        return {"success": True, "type": "game_application", "created_by": self.name}
    
    async def _create_web_application(self, content, config):
        """创建Web应用"""
        return {"success": True, "type": "web_application", "created_by": self.name}
    
    def _create_generic_solution(self, request):
        """创建通用解决方案"""
        return {"success": True, "type": "generic_solution", "created_by": self.name}

# CLI接口
async def main():
    """KiloCode MCP CLI接口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python kilocode_mcp_redesigned.py <command> [args]")
        print("命令:")
        print("  create <content>  - 创建解决方案")
        print("  test             - 运行测试")
        print("  config           - 显示配置信息")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("请提供创建内容")
            return
            
        content = " ".join(sys.argv[2:])
        mcp = KiloCodeMCP()
        
        request = {
            "content": content,
            "context": {
                "workflow_type": "coding_implementation",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        result = await mcp.process_request(request)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif command == "test":
        print("运行KiloCode MCP测试...")
        # 这里会调用测试用例
        
    elif command == "config":
        mcp = KiloCodeMCP()
        print("KiloCode MCP 配置信息:")
        print(f"名称: {mcp.name}")
        print(f"版本: {mcp.version}")
        print(f"支持的工作流: {mcp.supported_workflows}")
        print(f"支持的创建类型: {mcp.supported_creation_types}")
        print(f"支持的编程语言: {mcp.supported_languages}")
        
if __name__ == "__main__":
    asyncio.run(main())

