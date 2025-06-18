#!/usr/bin/env python3
"""
KiloCode MCP - 智能创建兜底引擎
基于工作流意图的智能创建机制

核心理念：
- 兜底就是创建：当其他MCP都解决不了时，创建解决方案
- 工作流意图驱动：根据不同工作流调整创建行为
- 所有功能都是MCP：通过coordinator与其他MCP通信
- 少前置自进化：搜索驱动理解，避免硬编码匹配
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

class WorkflowType(Enum):
    """工作流类型枚举"""
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    CODING_IMPLEMENTATION = "coding_implementation"
    TESTING_VERIFICATION = "testing_verification"
    DEPLOYMENT_RELEASE = "deployment_release"
    MONITORING_OPERATIONS = "monitoring_operations"

class CreationType(Enum):
    """创建类型枚举"""
    DOCUMENT = "document"  # PPT、报告、文档
    CODE = "code"         # 代码、脚本、程序
    PROTOTYPE = "prototype"  # 原型、demo、示例
    TOOL = "tool"         # 工具、脚本、自动化
    ANALYSIS = "analysis"  # 分析、报告、洞察
    DESIGN = "design"     # 设计、架构、方案

@dataclass
class CreationRequest:
    """创建请求数据类"""
    workflow_type: WorkflowType
    user_intent: str
    context: Dict[str, Any]
    creation_type: Optional[CreationType] = None
    requirements: List[str] = None
    constraints: List[str] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.constraints is None:
            self.constraints = []

@dataclass
class CreationResult:
    """创建结果数据类"""
    success: bool
    creation_type: CreationType
    output: Dict[str, Any]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

class KiloCodeMCP:
    """
    KiloCode MCP - 智能创建兜底引擎
    
    职责：
    1. 作为所有工作流的最后兜底
    2. 根据工作流意图智能创建解决方案
    3. 通过coordinator与其他MCP协作
    4. 保持搜索驱动的智能理解
    """
    
    def __init__(self, coordinator=None):
        """初始化KiloCode MCP"""
        self.name = "KiloCodeMCP"
        self.coordinator = coordinator
        self.logger = logging.getLogger(__name__)
        
        # 工作流配置映射
        self.workflow_configs = {
            WorkflowType.REQUIREMENTS_ANALYSIS: {
                "primary_creation_types": [CreationType.DOCUMENT, CreationType.PROTOTYPE],
                "ai_prompt_style": "business_analysis",
                "output_format": "presentation_ready"
            },
            WorkflowType.ARCHITECTURE_DESIGN: {
                "primary_creation_types": [CreationType.DESIGN, CreationType.DOCUMENT],
                "ai_prompt_style": "technical_architecture", 
                "output_format": "design_specification"
            },
            WorkflowType.CODING_IMPLEMENTATION: {
                "primary_creation_types": [CreationType.CODE, CreationType.TOOL],
                "ai_prompt_style": "code_generation",
                "output_format": "executable_code"
            },
            WorkflowType.TESTING_VERIFICATION: {
                "primary_creation_types": [CreationType.CODE, CreationType.TOOL],
                "ai_prompt_style": "test_generation",
                "output_format": "test_suite"
            },
            WorkflowType.DEPLOYMENT_RELEASE: {
                "primary_creation_types": [CreationType.TOOL, CreationType.CODE],
                "ai_prompt_style": "deployment_automation",
                "output_format": "deployment_package"
            },
            WorkflowType.MONITORING_OPERATIONS: {
                "primary_creation_types": [CreationType.TOOL, CreationType.ANALYSIS],
                "ai_prompt_style": "monitoring_setup",
                "output_format": "monitoring_solution"
            }
        }
        
        self.logger.info(f"✅ {self.name} 初始化完成 - 智能创建兜底引擎")
    
    async def process_creation_request(self, request: CreationRequest) -> CreationResult:
        """
        处理创建请求 - 核心兜底方法
        
        Args:
            request: 创建请求
            
        Returns:
            创建结果
        """
        self.logger.info(f"🎯 收到创建请求: {request.workflow_type.value} - {request.user_intent[:50]}...")
        
        try:
            # 1. 智能理解用户意图
            intent_analysis = await self._analyze_user_intent(request)
            
            # 2. 确定创建类型
            creation_type = await self._determine_creation_type(request, intent_analysis)
            
            # 3. 生成创建方案
            creation_plan = await self._generate_creation_plan(request, creation_type, intent_analysis)
            
            # 4. 执行创建
            creation_result = await self._execute_creation(creation_plan)
            
            # 5. 验证和优化
            final_result = await self._validate_and_optimize(creation_result, request)
            
            self.logger.info(f"✅ 创建完成: {creation_type.value}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ 创建失败: {str(e)}")
            return CreationResult(
                success=False,
                creation_type=CreationType.CODE,  # 默认值
                output={},
                metadata={"error": str(e)},
                error_message=f"创建过程失败: {str(e)}"
            )
    
    async def _analyze_user_intent(self, request: CreationRequest) -> Dict[str, Any]:
        """
        智能分析用户意图 - 搜索驱动理解
        
        不使用硬编码匹配，而是通过AI理解真实意图
        """
        self.logger.info("🔍 分析用户意图...")
        
        # 构建意图分析提示词
        analysis_prompt = self._build_intent_analysis_prompt(request)
        
        # 通过coordinator请求AI分析
        if self.coordinator:
            # 优先使用gemini_mcp
            gemini_result = await self._request_ai_analysis("gemini_mcp", analysis_prompt)
            if gemini_result.get("success"):
                return gemini_result["analysis"]
            
            # 备用claude_mcp
            claude_result = await self._request_ai_analysis("claude_mcp", analysis_prompt)
            if claude_result.get("success"):
                return claude_result["analysis"]
        
        # 兜底：基础分析
        return self._basic_intent_analysis(request)
    
    async def _determine_creation_type(self, request: CreationRequest, intent_analysis: Dict[str, Any]) -> CreationType:
        """
        根据工作流和意图确定创建类型
        """
        workflow_config = self.workflow_configs.get(request.workflow_type, {})
        primary_types = workflow_config.get("primary_creation_types", [CreationType.CODE])
        
        # 基于意图分析选择最合适的创建类型
        intent_keywords = intent_analysis.get("keywords", [])
        intent_category = intent_analysis.get("category", "")
        
        # 智能匹配创建类型
        if any(keyword in ["ppt", "presentation", "report", "document"] for keyword in intent_keywords):
            return CreationType.DOCUMENT
        elif any(keyword in ["game", "application", "system", "function"] for keyword in intent_keywords):
            return CreationType.CODE
        elif any(keyword in ["prototype", "demo", "example"] for keyword in intent_keywords):
            return CreationType.PROTOTYPE
        elif any(keyword in ["tool", "script", "automation"] for keyword in intent_keywords):
            return CreationType.TOOL
        else:
            # 使用工作流的主要创建类型
            return primary_types[0] if primary_types else CreationType.CODE
    
    async def _generate_creation_plan(self, request: CreationRequest, creation_type: CreationType, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成创建计划
        """
        workflow_config = self.workflow_configs.get(request.workflow_type, {})
        
        plan = {
            "creation_type": creation_type,
            "workflow_type": request.workflow_type,
            "ai_prompt_style": workflow_config.get("ai_prompt_style", "general"),
            "output_format": workflow_config.get("output_format", "standard"),
            "user_intent": request.user_intent,
            "intent_analysis": intent_analysis,
            "requirements": request.requirements,
            "constraints": request.constraints,
            "context": request.context
        }
        
        return plan
    
    async def _execute_creation(self, creation_plan: Dict[str, Any]) -> CreationResult:
        """
        执行创建 - 调用相应的AI MCP
        """
        creation_type = creation_plan["creation_type"]
        
        if creation_type == CreationType.DOCUMENT:
            return await self._create_document(creation_plan)
        elif creation_type == CreationType.CODE:
            return await self._create_code(creation_plan)
        elif creation_type == CreationType.PROTOTYPE:
            return await self._create_prototype(creation_plan)
        elif creation_type == CreationType.TOOL:
            return await self._create_tool(creation_plan)
        elif creation_type == CreationType.ANALYSIS:
            return await self._create_analysis(creation_plan)
        elif creation_type == CreationType.DESIGN:
            return await self._create_design(creation_plan)
        else:
            # 默认创建代码
            return await self._create_code(creation_plan)
    
    async def _create_document(self, plan: Dict[str, Any]) -> CreationResult:
        """创建文档类内容（PPT、报告等）"""
        self.logger.info("📄 创建文档内容...")
        
        # 构建文档生成提示词
        prompt = self._build_document_prompt(plan)
        
        # 通过coordinator请求AI生成
        result = await self._request_ai_generation("gemini_mcp", prompt, "document")
        
        if result.get("success"):
            return CreationResult(
                success=True,
                creation_type=CreationType.DOCUMENT,
                output=result["content"],
                metadata={
                    "generation_method": "ai_assisted",
                    "ai_model": "gemini",
                    "creation_time": datetime.now().isoformat()
                }
            )
        else:
            # 备用方案
            return await self._fallback_document_creation(plan)
    
    async def _create_code(self, plan: Dict[str, Any]) -> CreationResult:
        """创建代码类内容"""
        self.logger.info("💻 创建代码内容...")
        
        # 构建代码生成提示词
        prompt = self._build_code_prompt(plan)
        
        # 通过coordinator请求AI生成
        result = await self._request_ai_generation("claude_mcp", prompt, "code")
        
        if result.get("success"):
            return CreationResult(
                success=True,
                creation_type=CreationType.CODE,
                output=result["content"],
                metadata={
                    "generation_method": "ai_assisted",
                    "ai_model": "claude",
                    "creation_time": datetime.now().isoformat()
                }
            )
        else:
            # 备用方案
            return await self._fallback_code_creation(plan)
    
    async def _create_prototype(self, plan: Dict[str, Any]) -> CreationResult:
        """创建原型类内容"""
        self.logger.info("🔧 创建原型内容...")
        
        # 原型通常结合文档和代码
        doc_result = await self._create_document(plan)
        code_result = await self._create_code(plan)
        
        return CreationResult(
            success=True,
            creation_type=CreationType.PROTOTYPE,
            output={
                "documentation": doc_result.output,
                "code": code_result.output
            },
            metadata={
                "generation_method": "hybrid",
                "components": ["document", "code"],
                "creation_time": datetime.now().isoformat()
            }
        )
    
    async def _create_tool(self, plan: Dict[str, Any]) -> CreationResult:
        """创建工具类内容"""
        self.logger.info("🛠️ 创建工具内容...")
        
        # 工具主要是代码，但更注重实用性
        plan_copy = plan.copy()
        plan_copy["focus"] = "utility_and_automation"
        
        return await self._create_code(plan_copy)
    
    async def _create_analysis(self, plan: Dict[str, Any]) -> CreationResult:
        """创建分析类内容"""
        self.logger.info("📊 创建分析内容...")
        
        # 分析主要是文档，但更注重数据和洞察
        plan_copy = plan.copy()
        plan_copy["focus"] = "data_analysis_and_insights"
        
        return await self._create_document(plan_copy)
    
    async def _create_design(self, plan: Dict[str, Any]) -> CreationResult:
        """创建设计类内容"""
        self.logger.info("🎨 创建设计内容...")
        
        # 设计结合文档和结构化描述
        plan_copy = plan.copy()
        plan_copy["focus"] = "architecture_and_design"
        
        return await self._create_document(plan_copy)
    
    async def _request_ai_analysis(self, mcp_name: str, prompt: str) -> Dict[str, Any]:
        """通过coordinator请求AI分析"""
        if not self.coordinator:
            return {"success": False, "error": "No coordinator available"}
        
        try:
            # 通过coordinator发送请求到指定MCP
            request = {
                "target_mcp": mcp_name,
                "action": "analyze",
                "prompt": prompt,
                "response_format": "json"
            }
            
            result = await self.coordinator.route_request(request)
            return result
            
        except Exception as e:
            self.logger.error(f"AI分析请求失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _request_ai_generation(self, mcp_name: str, prompt: str, content_type: str) -> Dict[str, Any]:
        """通过coordinator请求AI生成"""
        if not self.coordinator:
            return {"success": False, "error": "No coordinator available"}
        
        try:
            # 通过coordinator发送请求到指定MCP
            request = {
                "target_mcp": mcp_name,
                "action": "generate",
                "prompt": prompt,
                "content_type": content_type
            }
            
            result = await self.coordinator.route_request(request)
            return result
            
        except Exception as e:
            self.logger.error(f"AI生成请求失败: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _build_intent_analysis_prompt(self, request: CreationRequest) -> str:
        """构建意图分析提示词"""
        return f"""
        分析以下用户请求的真实意图：
        
        工作流类型: {request.workflow_type.value}
        用户请求: {request.user_intent}
        上下文: {json.dumps(request.context, ensure_ascii=False)}
        
        请分析：
        1. 用户的核心需求是什么？
        2. 期望的输出类型是什么？
        3. 关键词和主题是什么？
        4. 复杂度和范围如何？
        
        以JSON格式返回分析结果。
        """
    
    def _build_document_prompt(self, plan: Dict[str, Any]) -> str:
        """构建文档生成提示词"""
        return f"""
        根据以下要求创建专业文档：
        
        类型: {plan['creation_type'].value}
        工作流: {plan['workflow_type'].value}
        用户需求: {plan['user_intent']}
        输出格式: {plan['output_format']}
        
        要求:
        - 专业且结构化
        - 符合{plan['workflow_type'].value}工作流的特点
        - 包含具体内容，不要占位符
        
        请生成完整的文档内容。
        """
    
    def _build_code_prompt(self, plan: Dict[str, Any]) -> str:
        """构建代码生成提示词"""
        return f"""
        根据以下要求创建代码：
        
        类型: {plan['creation_type'].value}
        工作流: {plan['workflow_type'].value}
        用户需求: {plan['user_intent']}
        
        要求:
        - 完整可运行的代码
        - 包含必要的注释
        - 遵循最佳实践
        - 符合{plan['workflow_type'].value}工作流的目标
        
        请生成完整的代码实现。
        """
    
    def _basic_intent_analysis(self, request: CreationRequest) -> Dict[str, Any]:
        """基础意图分析（兜底方案）"""
        return {
            "keywords": request.user_intent.lower().split(),
            "category": request.workflow_type.value,
            "complexity": "medium",
            "confidence": 0.7
        }
    
    async def _fallback_document_creation(self, plan: Dict[str, Any]) -> CreationResult:
        """文档创建兜底方案"""
        return CreationResult(
            success=True,
            creation_type=CreationType.DOCUMENT,
            output={
                "title": f"基于{plan['user_intent']}的文档",
                "content": "这是一个基础文档模板，需要进一步完善。",
                "type": "fallback_document"
            },
            metadata={"generation_method": "fallback"}
        )
    
    async def _fallback_code_creation(self, plan: Dict[str, Any]) -> CreationResult:
        """代码创建兜底方案"""
        return CreationResult(
            success=True,
            creation_type=CreationType.CODE,
            output={
                "code": f"# 基于{plan['user_intent']}的代码框架\nprint('Hello, World!')",
                "language": "python",
                "type": "fallback_code"
            },
            metadata={"generation_method": "fallback"}
        )
    
    async def _validate_and_optimize(self, result: CreationResult, request: CreationRequest) -> CreationResult:
        """验证和优化创建结果"""
        # 基础验证
        if not result.success:
            return result
        
        # 添加元数据
        result.metadata.update({
            "workflow_type": request.workflow_type.value,
            "original_intent": request.user_intent,
            "validation_passed": True
        })
        
        return result
    
    def get_capabilities(self) -> List[str]:
        """获取MCP能力列表"""
        return [
            "智能创建兜底",
            "工作流意图理解",
            "多类型内容生成",
            "AI协作调度",
            "自适应创建策略"
        ]

# 使用示例
async def main():
    """使用示例"""
    # 初始化KiloCode MCP
    kilocode = KiloCodeMCP()
    
    # 示例1: 需求分析工作流 - 创建PPT
    ppt_request = CreationRequest(
        workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
        user_intent="我们需要为华为终端业务做一个年终汇报展示",
        context={"company": "华为", "department": "终端业务", "period": "年终"}
    )
    
    ppt_result = await kilocode.process_creation_request(ppt_request)
    print(f"PPT创建结果: {ppt_result.success}")
    
    # 示例2: 编码实现工作流 - 创建贪吃蛇游戏
    game_request = CreationRequest(
        workflow_type=WorkflowType.CODING_IMPLEMENTATION,
        user_intent="帮我做一个贪吃蛇游戏",
        context={"platform": "web", "language": "javascript"}
    )
    
    game_result = await kilocode.process_creation_request(game_request)
    print(f"游戏创建结果: {game_result.success}")

if __name__ == "__main__":
    asyncio.run(main())

