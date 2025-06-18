#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态工作流生成器
Dynamic Workflow Generator

根据需求自动生成优化的工作流结构
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowTemplate(Enum):
    """工作流模板类型"""
    BASIC = "basic"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    DATA_PROCESSING = "data_processing"
    ML_PIPELINE = "ml_pipeline"
    CUSTOM = "custom"

class ComplexityLevel(Enum):
    """复杂度级别"""
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

@dataclass
class WorkflowRequirement:
    """工作流需求定义"""
    name: str
    description: str
    template: WorkflowTemplate = WorkflowTemplate.BASIC
    complexity: ComplexityLevel = ComplexityLevel.STANDARD
    
    # 功能需求
    required_capabilities: List[str] = None
    optional_capabilities: List[str] = None
    
    # 性能需求
    max_execution_time: int = 3600
    max_parallel_tasks: int = 5
    resource_constraints: Dict[str, Any] = None
    
    # 业务需求
    priority: str = "normal"
    deadline: Optional[datetime] = None
    stakeholders: List[str] = None
    
    def __post_init__(self):
        if self.required_capabilities is None:
            self.required_capabilities = []
        if self.optional_capabilities is None:
            self.optional_capabilities = []
        if self.resource_constraints is None:
            self.resource_constraints = {}
        if self.stakeholders is None:
            self.stakeholders = []

class DynamicWorkflowGenerator:
    """动态工作流生成器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 初始化模板库
        self._initialize_templates()
        
        # 初始化能力映射
        self._initialize_capability_mapping()
        
        # 初始化优化规则
        self._initialize_optimization_rules()
        
        logger.info("DynamicWorkflowGenerator 初始化完成")
    
    def _initialize_templates(self):
        """初始化工作流模板库"""
        self.templates = {
            WorkflowTemplate.BASIC: {
                "nodes": [
                    {"type": "requirement_analysis", "name": "需求分析"},
                    {"type": "implementation", "name": "实现"},
                    {"type": "verification", "name": "验证"}
                ],
                "edges": [
                    {"source": 0, "target": 1},
                    {"source": 1, "target": 2}
                ]
            },
            
            WorkflowTemplate.DEVELOPMENT: {
                "nodes": [
                    {"type": "requirement_analysis", "name": "需求分析"},
                    {"type": "architecture_design", "name": "架构设计"},
                    {"type": "code_implementation", "name": "代码实现"},
                    {"type": "unit_testing", "name": "单元测试"},
                    {"type": "integration_testing", "name": "集成测试"},
                    {"type": "code_review", "name": "代码审查"}
                ],
                "edges": [
                    {"source": 0, "target": 1},
                    {"source": 1, "target": 2},
                    {"source": 2, "target": 3},
                    {"source": 2, "target": 4},
                    {"source": 3, "target": 5},
                    {"source": 4, "target": 5}
                ]
            },
            
            WorkflowTemplate.TESTING: {
                "nodes": [
                    {"type": "test_planning", "name": "测试规划"},
                    {"type": "test_case_design", "name": "测试用例设计"},
                    {"type": "test_environment_setup", "name": "测试环境搭建"},
                    {"type": "test_execution", "name": "测试执行"},
                    {"type": "defect_tracking", "name": "缺陷跟踪"},
                    {"type": "test_reporting", "name": "测试报告"}
                ],
                "edges": [
                    {"source": 0, "target": 1},
                    {"source": 0, "target": 2},
                    {"source": 1, "target": 3},
                    {"source": 2, "target": 3},
                    {"source": 3, "target": 4},
                    {"source": 3, "target": 5}
                ]
            },
            
            WorkflowTemplate.DEPLOYMENT: {
                "nodes": [
                    {"type": "deployment_planning", "name": "部署规划"},
                    {"type": "environment_preparation", "name": "环境准备"},
                    {"type": "build_packaging", "name": "构建打包"},
                    {"type": "deployment_execution", "name": "部署执行"},
                    {"type": "smoke_testing", "name": "冒烟测试"},
                    {"type": "monitoring_setup", "name": "监控配置"},
                    {"type": "rollback_preparation", "name": "回滚准备"}
                ],
                "edges": [
                    {"source": 0, "target": 1},
                    {"source": 0, "target": 2},
                    {"source": 0, "target": 6},
                    {"source": 1, "target": 3},
                    {"source": 2, "target": 3},
                    {"source": 3, "target": 4},
                    {"source": 4, "target": 5}
                ]
            },
            
            WorkflowTemplate.DATA_PROCESSING: {
                "nodes": [
                    {"type": "data_ingestion", "name": "数据摄取"},
                    {"type": "data_validation", "name": "数据验证"},
                    {"type": "data_cleaning", "name": "数据清洗"},
                    {"type": "data_transformation", "name": "数据转换"},
                    {"type": "data_enrichment", "name": "数据丰富"},
                    {"type": "data_storage", "name": "数据存储"},
                    {"type": "data_quality_check", "name": "数据质量检查"}
                ],
                "edges": [
                    {"source": 0, "target": 1},
                    {"source": 1, "target": 2},
                    {"source": 2, "target": 3},
                    {"source": 3, "target": 4},
                    {"source": 4, "target": 5},
                    {"source": 5, "target": 6}
                ]
            },
            
            WorkflowTemplate.ML_PIPELINE: {
                "nodes": [
                    {"type": "data_collection", "name": "数据收集"},
                    {"type": "data_preprocessing", "name": "数据预处理"},
                    {"type": "feature_engineering", "name": "特征工程"},
                    {"type": "model_training", "name": "模型训练"},
                    {"type": "model_validation", "name": "模型验证"},
                    {"type": "model_evaluation", "name": "模型评估"},
                    {"type": "model_deployment", "name": "模型部署"},
                    {"type": "model_monitoring", "name": "模型监控"}
                ],
                "edges": [
                    {"source": 0, "target": 1},
                    {"source": 1, "target": 2},
                    {"source": 2, "target": 3},
                    {"source": 3, "target": 4},
                    {"source": 4, "target": 5},
                    {"source": 5, "target": 6},
                    {"source": 6, "target": 7}
                ]
            }
        }
    
    def _initialize_capability_mapping(self):
        """初始化能力映射"""
        self.capability_mapping = {
            # 开发相关能力
            "code_generation": ["code_implementation", "architecture_design"],
            "testing": ["unit_testing", "integration_testing", "test_execution"],
            "deployment": ["deployment_execution", "environment_preparation"],
            "monitoring": ["monitoring_setup", "model_monitoring"],
            
            # 数据相关能力
            "data_processing": ["data_ingestion", "data_transformation", "data_cleaning"],
            "data_analysis": ["data_validation", "data_quality_check"],
            "machine_learning": ["model_training", "model_validation", "feature_engineering"],
            
            # 项目管理能力
            "project_management": ["requirement_analysis", "test_planning", "deployment_planning"],
            "quality_assurance": ["code_review", "defect_tracking", "test_reporting"],
            
            # 基础设施能力
            "infrastructure": ["environment_preparation", "build_packaging"],
            "security": ["security_scanning", "vulnerability_assessment"],
            "performance": ["performance_testing", "load_testing"]
        }
    
    def _initialize_optimization_rules(self):
        """初始化优化规则"""
        self.optimization_rules = {
            # 并行化规则
            "parallel_rules": [
                {
                    "condition": "independent_tasks",
                    "action": "enable_parallel",
                    "node_types": ["unit_testing", "integration_testing"]
                },
                {
                    "condition": "resource_available",
                    "action": "enable_parallel",
                    "node_types": ["data_validation", "data_cleaning"]
                }
            ],
            
            # 优化规则
            "optimization_rules": [
                {
                    "condition": "high_priority",
                    "action": "reduce_timeout",
                    "factor": 0.8
                },
                {
                    "condition": "low_complexity",
                    "action": "merge_nodes",
                    "node_types": ["requirement_analysis", "architecture_design"]
                }
            ],
            
            # 资源分配规则
            "resource_rules": [
                {
                    "node_type": "model_training",
                    "cpu_requirement": 4.0,
                    "memory_requirement": 8192,
                    "gpu_requirement": 1
                },
                {
                    "node_type": "data_processing",
                    "cpu_requirement": 2.0,
                    "memory_requirement": 4096
                }
            ]
        }
    
    async def generate_workflow(self, requirements) -> 'EnhancedWorkflow':
        """生成动态工作流"""
        try:
            # 解析需求 - 支持字典和WorkflowRequirement对象
            if isinstance(requirements, WorkflowRequirement):
                workflow_req = requirements
            else:
                workflow_req = self._parse_requirements(requirements)
            
            # 选择基础模板
            base_template = self._select_base_template(workflow_req)
            
            # 根据能力需求调整模板
            adjusted_template = await self._adjust_template_by_capabilities(base_template, workflow_req)
            
            # 根据复杂度优化模板
            optimized_template = await self._optimize_by_complexity(adjusted_template, workflow_req)
            
            # 生成工作流对象
            workflow = await self._create_workflow_from_template(optimized_template, workflow_req)
            
            # 应用优化规则
            optimized_workflow = await self._apply_optimization_rules(workflow, workflow_req)
            
            logger.info(f"成功生成动态工作流: {workflow_req.name}")
            return optimized_workflow
            
        except Exception as e:
            logger.error(f"生成动态工作流失败: {e}")
            raise
    
    def _parse_requirements(self, requirements: Dict[str, Any]) -> WorkflowRequirement:
        """解析需求"""
        return WorkflowRequirement(
            name=requirements.get("name", "动态工作流"),
            description=requirements.get("description", ""),
            template=WorkflowTemplate(requirements.get("template", "basic")),
            complexity=ComplexityLevel(requirements.get("complexity", "standard")),
            required_capabilities=requirements.get("required_capabilities", []),
            optional_capabilities=requirements.get("optional_capabilities", []),
            max_execution_time=requirements.get("max_execution_time", 3600),
            max_parallel_tasks=requirements.get("max_parallel_tasks", 5),
            resource_constraints=requirements.get("resource_constraints", {}),
            priority=requirements.get("priority", "normal"),
            deadline=requirements.get("deadline"),
            stakeholders=requirements.get("stakeholders", [])
        )
    
    def _select_base_template(self, requirements: WorkflowRequirement) -> Dict[str, Any]:
        """选择基础模板"""
        if requirements.template in self.templates:
            return self.templates[requirements.template].copy()
        else:
            # 根据能力需求智能选择模板
            return self._intelligent_template_selection(requirements)
    
    def _intelligent_template_selection(self, requirements: WorkflowRequirement) -> Dict[str, Any]:
        """智能模板选择"""
        capability_scores = {}
        
        for template_name, template in self.templates.items():
            score = 0
            template_capabilities = set()
            
            # 收集模板中的能力
            for node in template["nodes"]:
                node_type = node["type"]
                for capability, node_types in self.capability_mapping.items():
                    if node_type in node_types:
                        template_capabilities.add(capability)
            
            # 计算匹配分数
            required_capabilities = set(requirements.required_capabilities)
            optional_capabilities = set(requirements.optional_capabilities)
            
            # 必需能力匹配分数
            required_match = len(required_capabilities & template_capabilities)
            required_total = len(required_capabilities)
            if required_total > 0:
                score += (required_match / required_total) * 100
            
            # 可选能力匹配分数
            optional_match = len(optional_capabilities & template_capabilities)
            optional_total = len(optional_capabilities)
            if optional_total > 0:
                score += (optional_match / optional_total) * 50
            
            capability_scores[template_name] = score
        
        # 选择得分最高的模板
        best_template = max(capability_scores, key=capability_scores.get)
        return self.templates[best_template].copy()
    
    async def _adjust_template_by_capabilities(self, template: Dict[str, Any], requirements: WorkflowRequirement) -> Dict[str, Any]:
        """根据能力需求调整模板"""
        adjusted_template = template.copy()
        
        # 添加缺失的必需能力节点
        existing_capabilities = self._get_template_capabilities(template)
        missing_capabilities = set(requirements.required_capabilities) - existing_capabilities
        
        for capability in missing_capabilities:
            if capability in self.capability_mapping:
                node_types = self.capability_mapping[capability]
                for node_type in node_types:
                    # 添加新节点
                    new_node = {
                        "type": node_type,
                        "name": self._generate_node_name(node_type),
                        "required_by_capability": capability
                    }
                    adjusted_template["nodes"].append(new_node)
        
        # 添加可选能力节点（根据优先级）
        if requirements.priority in ["high", "critical"]:
            for capability in requirements.optional_capabilities:
                if capability in self.capability_mapping:
                    node_types = self.capability_mapping[capability]
                    for node_type in node_types[:1]:  # 只添加第一个节点类型
                        new_node = {
                            "type": node_type,
                            "name": self._generate_node_name(node_type),
                            "optional": True
                        }
                        adjusted_template["nodes"].append(new_node)
        
        # 重新计算边关系
        adjusted_template["edges"] = self._recalculate_edges(adjusted_template["nodes"])
        
        return adjusted_template
    
    def _get_template_capabilities(self, template: Dict[str, Any]) -> set:
        """获取模板中的能力"""
        capabilities = set()
        for node in template["nodes"]:
            node_type = node["type"]
            for capability, node_types in self.capability_mapping.items():
                if node_type in node_types:
                    capabilities.add(capability)
        return capabilities
    
    def _generate_node_name(self, node_type: str) -> str:
        """生成节点名称"""
        name_mapping = {
            "requirement_analysis": "需求分析",
            "architecture_design": "架构设计",
            "code_implementation": "代码实现",
            "unit_testing": "单元测试",
            "integration_testing": "集成测试",
            "code_review": "代码审查",
            "deployment_execution": "部署执行",
            "monitoring_setup": "监控配置",
            "data_ingestion": "数据摄取",
            "data_validation": "数据验证",
            "data_cleaning": "数据清洗",
            "data_transformation": "数据转换",
            "model_training": "模型训练",
            "model_validation": "模型验证",
            "security_scanning": "安全扫描",
            "performance_testing": "性能测试"
        }
        return name_mapping.get(node_type, node_type.replace("_", " ").title())
    
    def _recalculate_edges(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """重新计算边关系"""
        edges = []
        
        # 基于节点类型的依赖关系规则
        dependency_rules = {
            "requirement_analysis": [],
            "architecture_design": ["requirement_analysis"],
            "code_implementation": ["architecture_design"],
            "unit_testing": ["code_implementation"],
            "integration_testing": ["code_implementation"],
            "code_review": ["unit_testing", "integration_testing"],
            "deployment_execution": ["code_review"],
            "monitoring_setup": ["deployment_execution"],
            "data_validation": ["data_ingestion"],
            "data_cleaning": ["data_validation"],
            "data_transformation": ["data_cleaning"],
            "model_training": ["data_transformation"],
            "model_validation": ["model_training"]
        }
        
        # 创建节点索引映射
        node_index_map = {}
        for i, node in enumerate(nodes):
            node_type = node["type"]
            if node_type not in node_index_map:
                node_index_map[node_type] = []
            node_index_map[node_type].append(i)
        
        # 根据依赖规则创建边
        for i, node in enumerate(nodes):
            node_type = node["type"]
            if node_type in dependency_rules:
                dependencies = dependency_rules[node_type]
                for dep_type in dependencies:
                    if dep_type in node_index_map:
                        for dep_index in node_index_map[dep_type]:
                            edges.append({"source": dep_index, "target": i})
        
        return edges
    
    async def _optimize_by_complexity(self, template: Dict[str, Any], requirements: WorkflowRequirement) -> Dict[str, Any]:
        """根据复杂度优化模板"""
        optimized_template = template.copy()
        
        if requirements.complexity == ComplexityLevel.SIMPLE:
            # 简化工作流：合并相似节点，减少步骤
            optimized_template = self._simplify_workflow(optimized_template)
        elif requirements.complexity == ComplexityLevel.COMPLEX:
            # 复杂工作流：添加更多检查点和验证步骤
            optimized_template = self._complexify_workflow(optimized_template)
        elif requirements.complexity == ComplexityLevel.ENTERPRISE:
            # 企业级工作流：添加审批、合规、监控等步骤
            optimized_template = self._enterpriseify_workflow(optimized_template)
        
        return optimized_template
    
    def _simplify_workflow(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """简化工作流"""
        # 移除可选节点
        simplified_nodes = [node for node in template["nodes"] if not node.get("optional", False)]
        
        # 合并相似节点
        merged_nodes = []
        skip_indices = set()
        
        for i, node in enumerate(simplified_nodes):
            if i in skip_indices:
                continue
                
            # 查找可以合并的节点
            mergeable_indices = [i]
            for j in range(i + 1, len(simplified_nodes)):
                if j not in skip_indices and self._can_merge_nodes(node, simplified_nodes[j]):
                    mergeable_indices.append(j)
                    skip_indices.add(j)
            
            if len(mergeable_indices) > 1:
                # 创建合并节点
                merged_node = self._merge_nodes([simplified_nodes[idx] for idx in mergeable_indices])
                merged_nodes.append(merged_node)
            else:
                merged_nodes.append(node)
        
        # 重新计算边
        simplified_edges = self._recalculate_edges(merged_nodes)
        
        return {"nodes": merged_nodes, "edges": simplified_edges}
    
    def _complexify_workflow(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """复杂化工作流"""
        complex_nodes = template["nodes"].copy()
        
        # 添加额外的验证和检查节点
        additional_nodes = []
        for node in template["nodes"]:
            node_type = node["type"]
            
            # 为关键节点添加验证步骤
            if node_type in ["code_implementation", "deployment_execution", "model_training"]:
                validation_node = {
                    "type": f"{node_type}_validation",
                    "name": f"{node['name']}验证",
                    "validation_for": node_type
                }
                additional_nodes.append(validation_node)
            
            # 为数据处理节点添加质量检查
            if "data" in node_type:
                quality_node = {
                    "type": f"{node_type}_quality_check",
                    "name": f"{node['name']}质量检查",
                    "quality_check_for": node_type
                }
                additional_nodes.append(quality_node)
        
        complex_nodes.extend(additional_nodes)
        complex_edges = self._recalculate_edges(complex_nodes)
        
        return {"nodes": complex_nodes, "edges": complex_edges}
    
    def _enterpriseify_workflow(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """企业级工作流"""
        enterprise_nodes = template["nodes"].copy()
        
        # 添加企业级节点
        enterprise_additions = [
            {"type": "compliance_check", "name": "合规检查"},
            {"type": "security_review", "name": "安全审查"},
            {"type": "approval_process", "name": "审批流程"},
            {"type": "documentation", "name": "文档生成"},
            {"type": "audit_logging", "name": "审计日志"},
            {"type": "risk_assessment", "name": "风险评估"}
        ]
        
        enterprise_nodes.extend(enterprise_additions)
        enterprise_edges = self._recalculate_edges(enterprise_nodes)
        
        return {"nodes": enterprise_nodes, "edges": enterprise_edges}
    
    def _can_merge_nodes(self, node1: Dict[str, Any], node2: Dict[str, Any]) -> bool:
        """判断两个节点是否可以合并"""
        # 相同类型的节点可以合并
        if node1["type"] == node2["type"]:
            return True
        
        # 相似功能的节点可以合并
        similar_groups = [
            ["unit_testing", "integration_testing"],
            ["data_validation", "data_quality_check"],
            ["requirement_analysis", "architecture_design"]
        ]
        
        for group in similar_groups:
            if node1["type"] in group and node2["type"] in group:
                return True
        
        return False
    
    def _merge_nodes(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并节点"""
        merged_name = " + ".join([node["name"] for node in nodes])
        merged_types = [node["type"] for node in nodes]
        
        return {
            "type": "merged_node",
            "name": merged_name,
            "merged_types": merged_types,
            "original_nodes": nodes
        }
    
    async def _create_workflow_from_template(self, template: Dict[str, Any], requirements: WorkflowRequirement) -> 'EnhancedWorkflow':
        """从模板创建工作流对象"""
        from enhanced_workflow_engine import EnhancedWorkflow, WorkflowNode, WorkflowEdge
        
        # 创建节点
        nodes = []
        for i, node_template in enumerate(template["nodes"]):
            node = WorkflowNode(
                id=f"node_{i}_{node_template['type']}",
                type=node_template["type"],
                name=node_template["name"],
                description=node_template.get("description", f"执行{node_template['name']}"),
                config=node_template.get("config", {}),
                timeout=self._calculate_node_timeout(node_template, requirements),
                can_parallel=self._can_node_parallel(node_template),
                parallel_group=self._get_parallel_group(node_template)
            )
            
            # 应用资源需求规则
            self._apply_resource_requirements(node, node_template)
            
            nodes.append(node)
        
        # 创建边
        edges = []
        for edge_template in template["edges"]:
            source_idx = edge_template["source"]
            target_idx = edge_template["target"]
            
            if source_idx < len(nodes) and target_idx < len(nodes):
                edge = WorkflowEdge(
                    source=nodes[source_idx].id,
                    target=nodes[target_idx].id,
                    condition=edge_template.get("condition"),
                    data_mapping=edge_template.get("data_mapping", {})
                )
                edges.append(edge)
        
        # 创建工作流
        workflow = EnhancedWorkflow(
            id=str(uuid.uuid4()),
            name=requirements.name,
            description=requirements.description,
            nodes=nodes,
            edges=edges,
            metadata={
                "template": requirements.template.value,
                "complexity": requirements.complexity.value,
                "generated_at": datetime.now().isoformat(),
                "requirements": {
                    "required_capabilities": requirements.required_capabilities,
                    "optional_capabilities": requirements.optional_capabilities,
                    "max_execution_time": requirements.max_execution_time,
                    "max_parallel_tasks": requirements.max_parallel_tasks,
                    "priority": requirements.priority
                }
            }
        )
        
        return workflow
    
    def _calculate_node_timeout(self, node_template: Dict[str, Any], requirements: WorkflowRequirement) -> int:
        """计算节点超时时间"""
        base_timeout = 300  # 5分钟基础超时
        
        # 根据节点类型调整
        type_multipliers = {
            "model_training": 10,
            "data_processing": 5,
            "deployment_execution": 3,
            "testing": 2,
            "analysis": 1.5
        }
        
        node_type = node_template["type"]
        multiplier = 1
        
        for type_key, mult in type_multipliers.items():
            if type_key in node_type:
                multiplier = mult
                break
        
        # 根据复杂度调整
        complexity_multipliers = {
            ComplexityLevel.SIMPLE: 0.5,
            ComplexityLevel.STANDARD: 1.0,
            ComplexityLevel.COMPLEX: 2.0,
            ComplexityLevel.ENTERPRISE: 3.0
        }
        
        complexity_mult = complexity_multipliers.get(requirements.complexity, 1.0)
        
        return int(base_timeout * multiplier * complexity_mult)
    
    def _can_node_parallel(self, node_template: Dict[str, Any]) -> bool:
        """判断节点是否可以并行执行"""
        parallel_types = [
            "testing", "validation", "quality_check", 
            "data_processing", "analysis"
        ]
        
        node_type = node_template["type"]
        return any(ptype in node_type for ptype in parallel_types)
    
    def _get_parallel_group(self, node_template: Dict[str, Any]) -> Optional[str]:
        """获取并行组"""
        node_type = node_template["type"]
        
        if "testing" in node_type:
            return "testing_group"
        elif "data" in node_type:
            return "data_group"
        elif "validation" in node_type:
            return "validation_group"
        
        return None
    
    def _apply_resource_requirements(self, node: 'WorkflowNode', node_template: Dict[str, Any]):
        """应用资源需求规则"""
        for rule in self.optimization_rules["resource_rules"]:
            if rule["node_type"] in node_template["type"]:
                node.cpu_requirement = rule.get("cpu_requirement", node.cpu_requirement)
                node.memory_requirement = rule.get("memory_requirement", node.memory_requirement)
                if "gpu_requirement" in rule:
                    node.config["gpu_requirement"] = rule["gpu_requirement"]
                break
    
    async def _apply_optimization_rules(self, workflow: 'EnhancedWorkflow', requirements: WorkflowRequirement) -> 'EnhancedWorkflow':
        """应用优化规则"""
        optimized_workflow = workflow
        
        # 应用并行化规则
        for rule in self.optimization_rules["parallel_rules"]:
            if rule["condition"] == "independent_tasks":
                self._enable_parallel_for_types(optimized_workflow, rule["node_types"])
            elif rule["condition"] == "resource_available" and requirements.max_parallel_tasks > 3:
                self._enable_parallel_for_types(optimized_workflow, rule["node_types"])
        
        # 应用优化规则
        for rule in self.optimization_rules["optimization_rules"]:
            if rule["condition"] == "high_priority" and requirements.priority in ["high", "critical"]:
                if rule["action"] == "reduce_timeout":
                    self._reduce_timeouts(optimized_workflow, rule["factor"])
            elif rule["condition"] == "low_complexity" and requirements.complexity == ComplexityLevel.SIMPLE:
                if rule["action"] == "merge_nodes":
                    self._merge_similar_nodes(optimized_workflow, rule["node_types"])
        
        return optimized_workflow
    
    def _enable_parallel_for_types(self, workflow: 'EnhancedWorkflow', node_types: List[str]):
        """为指定类型的节点启用并行"""
        for node in workflow.nodes:
            if any(ntype in node.type for ntype in node_types):
                node.can_parallel = True
                if not node.parallel_group:
                    node.parallel_group = f"parallel_{node_types[0]}"
    
    def _reduce_timeouts(self, workflow: 'EnhancedWorkflow', factor: float):
        """减少超时时间"""
        for node in workflow.nodes:
            node.timeout = int(node.timeout * factor)
    
    def _merge_similar_nodes(self, workflow: 'EnhancedWorkflow', node_types: List[str]):
        """合并相似节点"""
        # 这里可以实现节点合并逻辑
        # 由于涉及到边的重新计算，这里先保留接口
        pass
    
    async def get_available_templates(self) -> Dict[str, Any]:
        """获取可用模板列表"""
        templates_info = {}
        for template_type, template in self.templates.items():
            templates_info[template_type.value] = {
                "name": template_type.value,
                "node_count": len(template["nodes"]),
                "edge_count": len(template["edges"]),
                "capabilities": list(self._get_template_capabilities(template)),
                "description": self._get_template_description(template_type)
            }
        
        return {
            "templates": templates_info,
            "total_count": len(templates_info),
            "capability_mapping": self.capability_mapping
        }
    
    def _get_template_description(self, template_type: WorkflowTemplate) -> str:
        """获取模板描述"""
        descriptions = {
            WorkflowTemplate.BASIC: "基础工作流，适用于简单任务",
            WorkflowTemplate.DEVELOPMENT: "软件开发工作流，包含完整的开发生命周期",
            WorkflowTemplate.TESTING: "测试工作流，专注于质量保证",
            WorkflowTemplate.DEPLOYMENT: "部署工作流，用于应用发布",
            WorkflowTemplate.DATA_PROCESSING: "数据处理工作流，用于数据ETL",
            WorkflowTemplate.ML_PIPELINE: "机器学习管道，用于模型训练和部署"
        }
        return descriptions.get(template_type, "自定义工作流模板")

