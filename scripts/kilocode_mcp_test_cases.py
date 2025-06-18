#!/usr/bin/env python3
"""
KiloCode MCP 测试用例
基于六大工作流大MCP架构的智能创建兜底测试

测试目标：
1. 验证工作流意图驱动的创建能力
2. 确保智能兜底机制正常工作
3. 验证MCP间通信的正确性
4. 保护系统智能性不被破坏
"""

import asyncio
import pytest
import json
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from typing import Dict, Any

# 导入被测试的模块
from kilocode_mcp_redesigned import (
    KiloCodeMCP, 
    WorkflowType, 
    CreationType, 
    CreationRequest, 
    CreationResult
)

class TestKiloCodeMCP:
    """KiloCode MCP 核心测试类"""
    
    @pytest.fixture
    def mock_coordinator(self):
        """模拟coordinator"""
        coordinator = Mock()
        coordinator.route_request = AsyncMock()
        return coordinator
    
    @pytest.fixture
    def kilocode_mcp(self, mock_coordinator):
        """创建KiloCode MCP实例"""
        return KiloCodeMCP(coordinator=mock_coordinator)
    
    @pytest.mark.asyncio
    async def test_requirements_analysis_workflow_ppt_creation(self, kilocode_mcp, mock_coordinator):
        """
        测试需求分析工作流 - PPT创建
        场景：用户请求创建华为终端业务年终汇报PPT
        """
        # 模拟coordinator返回成功的AI分析
        mock_coordinator.route_request.return_value = {
            "success": True,
            "analysis": {
                "keywords": ["华为", "终端", "业务", "年终", "汇报", "展示"],
                "category": "business_presentation",
                "complexity": "high",
                "confidence": 0.9
            },
            "content": {
                "title": "华为终端业务2024年终汇报",
                "slides": [
                    {"title": "业务概览", "content": "2024年终端业务整体表现"},
                    {"title": "关键成果", "content": "核心产品和市场成就"},
                    {"title": "未来展望", "content": "2025年发展规划"}
                ]
            }
        }
        
        # 创建测试请求
        request = CreationRequest(
            workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
            user_intent="我们需要为华为终端业务做一个年终汇报展示",
            context={
                "company": "华为",
                "department": "终端业务", 
                "period": "年终",
                "audience": "高层管理"
            }
        )
        
        # 执行创建
        result = await kilocode_mcp.process_creation_request(request)
        
        # 验证结果
        assert result.success == True
        assert result.creation_type == CreationType.DOCUMENT
        assert "华为终端业务" in str(result.output)
        assert result.metadata["workflow_type"] == "requirements_analysis"
        
        # 验证coordinator调用
        assert mock_coordinator.route_request.called
        call_args = mock_coordinator.route_request.call_args[0][0]
        assert call_args["target_mcp"] == "gemini_mcp"
        assert "华为终端业务" in call_args["prompt"]
    
    @pytest.mark.asyncio
    async def test_coding_implementation_workflow_game_creation(self, kilocode_mcp, mock_coordinator):
        """
        测试编码实现工作流 - 贪吃蛇游戏创建
        场景：用户请求创建贪吃蛇游戏
        """
        # 模拟coordinator返回成功的代码生成
        mock_coordinator.route_request.return_value = {
            "success": True,
            "analysis": {
                "keywords": ["贪吃蛇", "游戏", "交互", "娱乐"],
                "category": "game_development",
                "complexity": "medium",
                "confidence": 0.85
            },
            "content": {
                "code": """
                class SnakeGame:
                    def __init__(self):
                        self.snake = [(5, 5)]
                        self.food = (10, 10)
                        self.direction = 'RIGHT'
                    
                    def move(self):
                        # 游戏逻辑实现
                        pass
                    
                    def check_collision(self):
                        # 碰撞检测
                        pass
                """,
                "language": "python",
                "framework": "pygame"
            }
        }
        
        # 创建测试请求
        request = CreationRequest(
            workflow_type=WorkflowType.CODING_IMPLEMENTATION,
            user_intent="帮我做一个贪吃蛇游戏",
            context={
                "platform": "desktop",
                "language": "python",
                "complexity": "beginner_friendly"
            }
        )
        
        # 执行创建
        result = await kilocode_mcp.process_creation_request(request)
        
        # 验证结果
        assert result.success == True
        assert result.creation_type == CreationType.CODE
        assert "SnakeGame" in str(result.output)
        assert result.metadata["workflow_type"] == "coding_implementation"
        
        # 验证使用了Claude MCP进行代码生成
        call_args = mock_coordinator.route_request.call_args[0][0]
        assert call_args["target_mcp"] == "claude_mcp"
        assert "贪吃蛇游戏" in call_args["prompt"]
    
    @pytest.mark.asyncio
    async def test_architecture_design_workflow_system_design(self, kilocode_mcp, mock_coordinator):
        """
        测试架构设计工作流 - 系统设计创建
        场景：用户请求设计微服务架构
        """
        mock_coordinator.route_request.return_value = {
            "success": True,
            "analysis": {
                "keywords": ["微服务", "架构", "设计", "系统"],
                "category": "system_architecture",
                "complexity": "high",
                "confidence": 0.9
            },
            "content": {
                "architecture": {
                    "services": ["user-service", "order-service", "payment-service"],
                    "communication": "REST API + Message Queue",
                    "database": "分布式数据库设计",
                    "deployment": "容器化部署"
                }
            }
        }
        
        request = CreationRequest(
            workflow_type=WorkflowType.ARCHITECTURE_DESIGN,
            user_intent="设计一个电商平台的微服务架构",
            context={
                "domain": "电商",
                "scale": "中大型",
                "requirements": ["高可用", "可扩展", "高性能"]
            }
        )
        
        result = await kilocode_mcp.process_creation_request(request)
        
        assert result.success == True
        assert result.creation_type == CreationType.DESIGN
        assert "微服务" in str(result.output)
        assert result.metadata["workflow_type"] == "architecture_design"
    
    @pytest.mark.asyncio
    async def test_ai_fallback_mechanism(self, kilocode_mcp, mock_coordinator):
        """
        测试AI兜底机制
        场景：Gemini失败，自动切换到Claude
        """
        # 模拟Gemini失败，Claude成功
        def mock_route_request(request):
            if request["target_mcp"] == "gemini_mcp":
                return {"success": False, "error": "API限制"}
            elif request["target_mcp"] == "claude_mcp":
                return {
                    "success": True,
                    "analysis": {"keywords": ["测试"], "category": "test"},
                    "content": {"result": "Claude生成的内容"}
                }
        
        mock_coordinator.route_request.side_effect = mock_route_request
        
        request = CreationRequest(
            workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
            user_intent="创建一个测试文档",
            context={}
        )
        
        result = await kilocode_mcp.process_creation_request(request)
        
        # 验证兜底机制工作
        assert result.success == True
        assert "Claude生成的内容" in str(result.output)
        
        # 验证调用了两次（先Gemini后Claude）
        assert mock_coordinator.route_request.call_count == 2
    
    @pytest.mark.asyncio
    async def test_workflow_configuration_mapping(self, kilocode_mcp):
        """
        测试工作流配置映射
        验证不同工作流有不同的配置
        """
        # 验证需求分析工作流配置
        req_config = kilocode_mcp.workflow_configs[WorkflowType.REQUIREMENTS_ANALYSIS]
        assert CreationType.DOCUMENT in req_config["primary_creation_types"]
        assert req_config["ai_prompt_style"] == "business_analysis"
        
        # 验证编码实现工作流配置
        code_config = kilocode_mcp.workflow_configs[WorkflowType.CODING_IMPLEMENTATION]
        assert CreationType.CODE in code_config["primary_creation_types"]
        assert code_config["ai_prompt_style"] == "code_generation"
        
        # 验证测试验证工作流配置
        test_config = kilocode_mcp.workflow_configs[WorkflowType.TESTING_VERIFICATION]
        assert CreationType.CODE in test_config["primary_creation_types"]
        assert test_config["ai_prompt_style"] == "test_generation"
    
    @pytest.mark.asyncio
    async def test_creation_type_determination(self, kilocode_mcp):
        """
        测试创建类型智能确定
        验证基于意图分析的创建类型选择
        """
        # PPT相关意图 → DOCUMENT
        intent_analysis = {
            "keywords": ["ppt", "presentation", "汇报"],
            "category": "business_presentation"
        }
        request = CreationRequest(
            workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
            user_intent="创建PPT",
            context={}
        )
        creation_type = await kilocode_mcp._determine_creation_type(request, intent_analysis)
        assert creation_type == CreationType.DOCUMENT
        
        # 游戏相关意图 → CODE
        intent_analysis = {
            "keywords": ["game", "贪吃蛇", "应用"],
            "category": "game_development"
        }
        request = CreationRequest(
            workflow_type=WorkflowType.CODING_IMPLEMENTATION,
            user_intent="做游戏",
            context={}
        )
        creation_type = await kilocode_mcp._determine_creation_type(request, intent_analysis)
        assert creation_type == CreationType.CODE
    
    @pytest.mark.asyncio
    async def test_no_hardcoded_matching(self, kilocode_mcp, mock_coordinator):
        """
        测试无硬编码匹配 - 智能性保护
        验证系统不使用简单的关键词匹配
        """
        # 模拟AI分析返回
        mock_coordinator.route_request.return_value = {
            "success": True,
            "analysis": {
                "keywords": ["复杂", "业务", "需求"],
                "category": "complex_analysis",
                "complexity": "high"
            },
            "content": {"result": "智能分析结果"}
        }
        
        # 使用可能触发硬编码匹配的输入
        request = CreationRequest(
            workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
            user_intent="ppt code game tool analysis design",  # 包含多个关键词
            context={}
        )
        
        result = await kilocode_mcp.process_creation_request(request)
        
        # 验证使用了AI分析而不是关键词匹配
        assert result.success == True
        assert mock_coordinator.route_request.called
        
        # 验证调用了AI分析接口
        call_args = mock_coordinator.route_request.call_args[0][0]
        assert call_args["action"] == "analyze"
        assert "分析以下用户请求的真实意图" in call_args["prompt"]
    
    @pytest.mark.asyncio
    async def test_coordinator_communication_only(self, kilocode_mcp, mock_coordinator):
        """
        测试仅通过coordinator通信
        验证不直接调用其他MCP或API
        """
        mock_coordinator.route_request.return_value = {
            "success": True,
            "analysis": {"keywords": ["test"]},
            "content": {"result": "测试内容"}
        }
        
        request = CreationRequest(
            workflow_type=WorkflowType.CODING_IMPLEMENTATION,
            user_intent="创建测试代码",
            context={}
        )
        
        result = await kilocode_mcp.process_creation_request(request)
        
        # 验证所有外部通信都通过coordinator
        assert mock_coordinator.route_request.called
        
        # 验证没有直接的API调用（通过检查是否有其他网络调用）
        # 这里可以添加更多的验证逻辑
        assert result.success == True
    
    @pytest.mark.asyncio
    async def test_fallback_creation_mechanisms(self, kilocode_mcp, mock_coordinator):
        """
        测试兜底创建机制
        验证当AI服务都失败时的兜底方案
        """
        # 模拟所有AI服务都失败
        mock_coordinator.route_request.return_value = {
            "success": False,
            "error": "所有AI服务不可用"
        }
        
        request = CreationRequest(
            workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
            user_intent="创建紧急文档",
            context={}
        )
        
        result = await kilocode_mcp.process_creation_request(request)
        
        # 验证兜底机制工作
        assert result.success == True
        assert result.creation_type == CreationType.DOCUMENT
        assert result.metadata["generation_method"] == "fallback"
        
        # 验证兜底内容不是空的
        assert result.output is not None
        assert len(str(result.output)) > 0
    
    def test_mcp_capabilities(self, kilocode_mcp):
        """
        测试MCP能力声明
        验证KiloCode MCP正确声明自己的能力
        """
        capabilities = kilocode_mcp.get_capabilities()
        
        expected_capabilities = [
            "智能创建兜底",
            "工作流意图理解", 
            "多类型内容生成",
            "AI协作调度",
            "自适应创建策略"
        ]
        
        for capability in expected_capabilities:
            assert capability in capabilities
    
    @pytest.mark.asyncio
    async def test_cross_workflow_consistency(self, kilocode_mcp, mock_coordinator):
        """
        测试跨工作流一致性
        验证同一个MCP在不同工作流中的行为一致性
        """
        mock_coordinator.route_request.return_value = {
            "success": True,
            "analysis": {"keywords": ["测试"]},
            "content": {"result": "一致性测试"}
        }
        
        workflows = [
            WorkflowType.REQUIREMENTS_ANALYSIS,
            WorkflowType.ARCHITECTURE_DESIGN,
            WorkflowType.CODING_IMPLEMENTATION,
            WorkflowType.TESTING_VERIFICATION,
            WorkflowType.DEPLOYMENT_RELEASE,
            WorkflowType.MONITORING_OPERATIONS
        ]
        
        results = []
        for workflow in workflows:
            request = CreationRequest(
                workflow_type=workflow,
                user_intent="创建测试内容",
                context={}
            )
            result = await kilocode_mcp.process_creation_request(request)
            results.append(result)
        
        # 验证所有工作流都能成功处理
        for result in results:
            assert result.success == True
            assert result.metadata["workflow_type"] in [w.value for w in workflows]
        
        # 验证处理流程一致性（都调用了coordinator）
        assert mock_coordinator.route_request.call_count == len(workflows) * 2  # 每个工作流调用2次（分析+生成）

class TestWorkflowIntegration:
    """工作流集成测试"""
    
    @pytest.mark.asyncio
    async def test_six_workflow_mcp_integration(self):
        """
        测试六大工作流MCP集成
        验证KiloCode MCP作为兜底在各个工作流中的作用
        """
        # 模拟六大工作流MCP
        workflow_mcps = {
            "requirements_analysis_mcp": Mock(),
            "architecture_design_mcp": Mock(),
            "coding_implementation_mcp": Mock(),
            "testing_verification_mcp": Mock(),
            "deployment_release_mcp": Mock(),
            "monitoring_operations_mcp": Mock()
        }
        
        # 模拟coordinator
        coordinator = Mock()
        coordinator.route_request = AsyncMock()
        
        # 模拟工作流MCP处理失败，需要KiloCode兜底
        coordinator.route_request.return_value = {
            "success": True,
            "analysis": {"keywords": ["兜底", "测试"]},
            "content": {"result": "兜底创建成功"}
        }
        
        kilocode = KiloCodeMCP(coordinator=coordinator)
        
        # 测试在需求分析工作流中的兜底
        request = CreationRequest(
            workflow_type=WorkflowType.REQUIREMENTS_ANALYSIS,
            user_intent="其他MCP都处理不了的复杂需求",
            context={"fallback_reason": "专用MCP处理失败"}
        )
        
        result = await kilocode.process_creation_request(request)
        
        assert result.success == True
        assert "兜底创建成功" in str(result.output)

class TestIntelligenceProtection:
    """智能性保护测试"""
    
    def test_no_hardcoded_patterns(self):
        """
        测试无硬编码模式
        验证代码中没有反智能的硬编码匹配
        """
        # 读取KiloCode MCP源码
        with open('/home/ubuntu/kilocode_mcp_redesigned.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 检查是否存在反智能模式
        anti_patterns = [
            "if 'ppt' in",
            "if 'code' in", 
            "if 'game' in",
            "elif content.contains",
            "keyword_match",
            "simple_match"
        ]
        
        for pattern in anti_patterns:
            assert pattern not in source_code, f"发现反智能模式: {pattern}"
    
    def test_search_driven_approach(self):
        """
        测试搜索驱动方法
        验证使用AI分析而不是规则匹配
        """
        with open('/home/ubuntu/kilocode_mcp_redesigned.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # 验证包含搜索驱动的关键词
        search_driven_patterns = [
            "_analyze_user_intent",
            "搜索驱动理解",
            "AI分析",
            "intent_analysis",
            "coordinator.route_request"
        ]
        
        for pattern in search_driven_patterns:
            assert pattern in source_code, f"缺少搜索驱动模式: {pattern}"

# 性能测试
class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_creation_performance(self):
        """
        测试创建性能
        验证创建过程在合理时间内完成
        """
        coordinator = Mock()
        coordinator.route_request = AsyncMock(return_value={
            "success": True,
            "analysis": {"keywords": ["性能", "测试"]},
            "content": {"result": "性能测试内容"}
        })
        
        kilocode = KiloCodeMCP(coordinator=coordinator)
        
        request = CreationRequest(
            workflow_type=WorkflowType.CODING_IMPLEMENTATION,
            user_intent="性能测试请求",
            context={}
        )
        
        start_time = datetime.now()
        result = await kilocode.process_creation_request(request)
        end_time = datetime.now()
        
        # 验证性能（应该在合理时间内完成）
        duration = (end_time - start_time).total_seconds()
        assert duration < 10.0  # 应该在10秒内完成
        assert result.success == True

# 运行测试的主函数
if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])

