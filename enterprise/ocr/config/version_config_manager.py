#!/usr/bin/env python3
"""
版本配置管理器
管理Enterprise、Personal、Opensource三种版本的智能体配置
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("version_config_manager")

class VersionType(Enum):
    """版本类型枚举"""
    ENTERPRISE = "enterprise"
    PERSONAL = "personal"
    OPENSOURCE = "opensource"

@dataclass
class AgentConfig:
    """智能体配置"""
    agent_id: str
    name: str
    description: str
    capabilities: List[str]
    mcp_endpoint: str
    quality_threshold: float
    enabled: bool
    priority: int

@dataclass
class VersionLimitations:
    """版本限制"""
    concurrent_workflows: int
    monthly_executions: str  # "unlimited" or number
    storage_limit: str
    support_level: str

@dataclass
class VersionConfig:
    """版本配置"""
    version: str
    display_name: str
    description: str
    target_audience: str
    pricing_tier: str
    agents: List[AgentConfig]
    workflow_features: Dict[str, bool]
    limitations: VersionLimitations

class VersionConfigManager:
    """版本配置管理器"""
    
    def __init__(self):
        self.configs = self._initialize_configs()
        self.upgrade_paths = {
            VersionType.OPENSOURCE: [VersionType.PERSONAL, VersionType.ENTERPRISE],
            VersionType.PERSONAL: [VersionType.ENTERPRISE],
            VersionType.ENTERPRISE: []
        }
        logger.info("版本配置管理器初始化完成")
    
    def _initialize_configs(self) -> Dict[str, VersionConfig]:
        """初始化版本配置"""
        return {
            VersionType.ENTERPRISE.value: self._create_enterprise_config(),
            VersionType.PERSONAL.value: self._create_personal_config(),
            VersionType.OPENSOURCE.value: self._create_opensource_config()
        }
    
    def _create_enterprise_config(self) -> VersionConfig:
        """创建Enterprise版配置"""
        agents = [
            AgentConfig(
                agent_id="requirements_analysis",
                name="需求分析智能体",
                description="AI理解业务需求，生成技术方案",
                capabilities=[
                    "自然语言需求理解",
                    "技术可行性分析", 
                    "复杂度评估",
                    "资源需求分析",
                    "风险评估"
                ],
                mcp_endpoint="http://98.81.255.168:8094",
                quality_threshold=0.85,
                enabled=True,
                priority=1
            ),
            AgentConfig(
                agent_id="architecture_design",
                name="架构设计智能体",
                description="智能架构建议，最佳实践推荐",
                capabilities=[
                    "系统架构设计",
                    "模式识别和推荐",
                    "性能优化建议",
                    "扩展性设计",
                    "安全架构规划"
                ],
                mcp_endpoint="http://98.81.255.168:8095",
                quality_threshold=0.80,
                enabled=True,
                priority=2
            ),
            AgentConfig(
                agent_id="implementation",
                name="编码实现智能体",
                description="AI编程助手，代码自动生成",
                capabilities=[
                    "多语言代码生成",
                    "智能代码补全",
                    "框架适配",
                    "代码质量检查",
                    "性能优化"
                ],
                mcp_endpoint="http://98.81.255.168:8093",
                quality_threshold=0.90,
                enabled=True,
                priority=3
            ),
            AgentConfig(
                agent_id="testing_verification",
                name="测试验证智能体",
                description="自动化测试，质量保障",
                capabilities=[
                    "测试用例生成",
                    "自动化测试执行",
                    "质量评估",
                    "性能测试",
                    "安全测试"
                ],
                mcp_endpoint="http://98.81.255.168:8092",
                quality_threshold=0.95,
                enabled=True,
                priority=4
            ),
            AgentConfig(
                agent_id="deployment_release",
                name="部署发布智能体",
                description="一键部署，环境管理",
                capabilities=[
                    "多环境部署",
                    "容器化部署",
                    "蓝绿部署",
                    "版本管理",
                    "回滚机制"
                ],
                mcp_endpoint="http://98.81.255.168:8091",
                quality_threshold=0.88,
                enabled=True,
                priority=5
            ),
            AgentConfig(
                agent_id="monitoring_operations",
                name="监控运维智能体",
                description="性能监控，问题预警",
                capabilities=[
                    "实时监控",
                    "智能告警",
                    "性能分析",
                    "容量规划",
                    "自动化运维"
                ],
                mcp_endpoint="http://98.81.255.168:8090",
                quality_threshold=0.85,
                enabled=True,
                priority=6
            )
        ]
        
        return VersionConfig(
            version="enterprise",
            display_name="Enterprise版 - 完整智能工作流",
            description="面向企业用户的完整六大智能体协作系统，提供端到端的产品开发和运营解决方案",
            target_audience="大型企业、软件公司、系统集成商",
            pricing_tier="premium",
            agents=agents,
            workflow_features={
                "end_to_end_automation": True,
                "quality_gates": True,
                "advanced_monitoring": True,
                "enterprise_support": True,
                "custom_integrations": True,
                "sla_guarantees": True
            },
            limitations=VersionLimitations(
                concurrent_workflows=100,
                monthly_executions="unlimited",
                storage_limit="1TB",
                support_level="24/7 premium"
            )
        )
    
    def _create_personal_config(self) -> VersionConfig:
        """创建Personal版配置"""
        agents = [
            AgentConfig(
                agent_id="implementation",
                name="编码实现智能体",
                description="AI编程助手，代码自动生成",
                capabilities=[
                    "多语言代码生成",
                    "智能代码补全",
                    "基础框架适配",
                    "代码质量检查"
                ],
                mcp_endpoint="http://98.81.255.168:8093",
                quality_threshold=0.85,
                enabled=True,
                priority=1
            ),
            AgentConfig(
                agent_id="testing_verification",
                name="测试验证智能体",
                description="自动化测试，质量保障",
                capabilities=[
                    "基础测试用例生成",
                    "单元测试执行",
                    "基础质量评估"
                ],
                mcp_endpoint="http://98.81.255.168:8092",
                quality_threshold=0.80,
                enabled=True,
                priority=2
            ),
            AgentConfig(
                agent_id="deployment_release",
                name="部署发布智能体",
                description="简化部署，版本管理",
                capabilities=[
                    "基础部署功能",
                    "版本管理",
                    "简单回滚"
                ],
                mcp_endpoint="http://98.81.255.168:8091",
                quality_threshold=0.75,
                enabled=True,
                priority=3
            )
        ]
        
        return VersionConfig(
            version="personal",
            display_name="Personal版 - 核心开发工作流",
            description="面向个人开发者的核心三大智能体，专注于编码、测试和部署",
            target_audience="个人开发者、自由职业者、小型团队",
            pricing_tier="standard",
            agents=agents,
            workflow_features={
                "end_to_end_automation": False,
                "quality_gates": True,
                "advanced_monitoring": False,
                "enterprise_support": False,
                "custom_integrations": False,
                "sla_guarantees": False
            },
            limitations=VersionLimitations(
                concurrent_workflows=5,
                monthly_executions="1000",
                storage_limit="10GB",
                support_level="community"
            )
        )
    
    def _create_opensource_config(self) -> VersionConfig:
        """创建Opensource版配置"""
        agents = [
            AgentConfig(
                agent_id="implementation",
                name="编码实现智能体",
                description="开源AI编程助手",
                capabilities=[
                    "基础代码生成",
                    "开源框架适配",
                    "社区最佳实践"
                ],
                mcp_endpoint="http://98.81.255.168:8093",
                quality_threshold=0.70,
                enabled=True,
                priority=1
            ),
            AgentConfig(
                agent_id="testing_verification",
                name="测试验证智能体",
                description="开源测试工具",
                capabilities=[
                    "开源测试框架",
                    "基础测试执行",
                    "社区测试标准"
                ],
                mcp_endpoint="http://98.81.255.168:8092",
                quality_threshold=0.70,
                enabled=True,
                priority=2
            ),
            AgentConfig(
                agent_id="deployment_release",
                name="部署发布智能体",
                description="开源部署工具",
                capabilities=[
                    "开源部署平台",
                    "基础版本控制",
                    "社区部署实践"
                ],
                mcp_endpoint="http://98.81.255.168:8091",
                quality_threshold=0.65,
                enabled=True,
                priority=3
            )
        ]
        
        return VersionConfig(
            version="opensource",
            display_name="Opensource版 - 开源开发工作流",
            description="开源社区版本，提供基础的编码、测试和部署功能",
            target_audience="开源项目、学习者、研究机构",
            pricing_tier="free",
            agents=agents,
            workflow_features={
                "end_to_end_automation": False,
                "quality_gates": False,
                "advanced_monitoring": False,
                "enterprise_support": False,
                "custom_integrations": False,
                "sla_guarantees": False
            },
            limitations=VersionLimitations(
                concurrent_workflows=2,
                monthly_executions="100",
                storage_limit="1GB",
                support_level="community"
            )
        )
    
    def get_version_config(self, version: str) -> VersionConfig:
        """获取指定版本的配置"""
        if version not in self.configs:
            raise ValueError(f"不支持的版本: {version}")
        return self.configs[version]
    
    def get_enabled_agents(self, version: str) -> List[AgentConfig]:
        """获取指定版本启用的智能体"""
        config = self.get_version_config(version)
        return [agent for agent in config.agents if agent.enabled]
    
    def get_agent_endpoints(self, version: str) -> Dict[str, str]:
        """获取指定版本的智能体端点"""
        agents = self.get_enabled_agents(version)
        return {agent.agent_id: agent.mcp_endpoint for agent in agents}
    
    def get_quality_thresholds(self, version: str) -> Dict[str, float]:
        """获取指定版本的质量阈值"""
        agents = self.get_enabled_agents(version)
        return {agent.agent_id: agent.quality_threshold for agent in agents}
    
    def validate_version_limits(self, version: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """验证版本限制"""
        config = self.get_version_config(version)
        limitations = config.limitations
        
        validation_result = {
            "valid": True,
            "violations": [],
            "warnings": []
        }
        
        # 检查并发限制
        concurrent_workflows = request.get("concurrent_workflows", 1)
        if concurrent_workflows > limitations.concurrent_workflows:
            validation_result["valid"] = False
            validation_result["violations"].append(
                f"并发工作流超限: {concurrent_workflows} > {limitations.concurrent_workflows}"
            )
        
        # 检查月度执行限制
        if limitations.monthly_executions != "unlimited":
            monthly_usage = request.get("monthly_usage", 0)
            monthly_limit = int(limitations.monthly_executions)
            if monthly_usage >= monthly_limit:
                validation_result["valid"] = False
                validation_result["violations"].append(
                    f"月度执行次数超限: {monthly_usage} >= {monthly_limit}"
                )
            elif monthly_usage > monthly_limit * 0.8:
                validation_result["warnings"].append(
                    f"月度执行次数接近限制: {monthly_usage}/{monthly_limit}"
                )
        
        return validation_result
    
    def get_upgrade_options(self, current_version: str) -> List[str]:
        """获取升级选项"""
        try:
            version_enum = VersionType(current_version)
            return [v.value for v in self.upgrade_paths.get(version_enum, [])]
        except ValueError:
            return []
    
    def calculate_upgrade_benefits(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """计算升级收益"""
        from_config = self.get_version_config(from_version)
        to_config = self.get_version_config(to_version)
        
        # 计算新增智能体
        from_agents = {agent.agent_id for agent in from_config.agents}
        to_agents = {agent.agent_id for agent in to_config.agents}
        new_agents = to_agents - from_agents
        
        # 计算新增功能
        new_features = []
        for feature, enabled in to_config.workflow_features.items():
            if enabled and not from_config.workflow_features.get(feature, False):
                new_features.append(feature)
        
        # 计算限制改进
        limit_improvements = {}
        if to_config.limitations.concurrent_workflows > from_config.limitations.concurrent_workflows:
            limit_improvements["concurrent_workflows"] = {
                "from": from_config.limitations.concurrent_workflows,
                "to": to_config.limitations.concurrent_workflows
            }
        
        if (to_config.limitations.monthly_executions == "unlimited" or 
            (from_config.limitations.monthly_executions != "unlimited" and
             int(to_config.limitations.monthly_executions) > int(from_config.limitations.monthly_executions))):
            limit_improvements["monthly_executions"] = {
                "from": from_config.limitations.monthly_executions,
                "to": to_config.limitations.monthly_executions
            }
        
        return {
            "new_agents": list(new_agents),
            "new_features": new_features,
            "limit_improvements": limit_improvements,
            "support_upgrade": {
                "from": from_config.limitations.support_level,
                "to": to_config.limitations.support_level
            }
        }
    
    def get_version_comparison(self) -> Dict[str, Any]:
        """获取版本对比信息"""
        comparison = {
            "versions": {},
            "feature_matrix": {},
            "limitation_matrix": {}
        }
        
        # 版本基本信息
        for version_name, config in self.configs.items():
            comparison["versions"][version_name] = {
                "display_name": config.display_name,
                "description": config.description,
                "target_audience": config.target_audience,
                "pricing_tier": config.pricing_tier,
                "agent_count": len(config.agents)
            }
        
        # 功能对比矩阵
        all_features = set()
        for config in self.configs.values():
            all_features.update(config.workflow_features.keys())
        
        for feature in all_features:
            comparison["feature_matrix"][feature] = {}
            for version_name, config in self.configs.items():
                comparison["feature_matrix"][feature][version_name] = config.workflow_features.get(feature, False)
        
        # 限制对比矩阵
        limitation_fields = ["concurrent_workflows", "monthly_executions", "storage_limit", "support_level"]
        for field in limitation_fields:
            comparison["limitation_matrix"][field] = {}
            for version_name, config in self.configs.items():
                comparison["limitation_matrix"][field][version_name] = getattr(config.limitations, field)
        
        return comparison
    
    def export_config_json(self, version: Optional[str] = None) -> str:
        """导出配置为JSON格式"""
        if version:
            config = self.get_version_config(version)
            return json.dumps(self._config_to_dict(config), indent=2, ensure_ascii=False)
        else:
            all_configs = {}
            for version_name, config in self.configs.items():
                all_configs[version_name] = self._config_to_dict(config)
            return json.dumps(all_configs, indent=2, ensure_ascii=False)
    
    def _config_to_dict(self, config: VersionConfig) -> Dict[str, Any]:
        """将配置对象转换为字典"""
        return {
            "version": config.version,
            "display_name": config.display_name,
            "description": config.description,
            "target_audience": config.target_audience,
            "pricing_tier": config.pricing_tier,
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "description": agent.description,
                    "capabilities": agent.capabilities,
                    "mcp_endpoint": agent.mcp_endpoint,
                    "quality_threshold": agent.quality_threshold,
                    "enabled": agent.enabled,
                    "priority": agent.priority
                }
                for agent in config.agents
            ],
            "workflow_features": config.workflow_features,
            "limitations": {
                "concurrent_workflows": config.limitations.concurrent_workflows,
                "monthly_executions": config.limitations.monthly_executions,
                "storage_limit": config.limitations.storage_limit,
                "support_level": config.limitations.support_level
            }
        }

# 创建全局版本配置管理器实例
version_manager = VersionConfigManager()

if __name__ == "__main__":
    # 测试版本配置管理器
    print("=== PowerAuto.ai 版本配置管理器测试 ===\n")
    
    # 测试获取版本配置
    for version in ["enterprise", "personal", "opensource"]:
        print(f"--- {version.upper()}版配置 ---")
        config = version_manager.get_version_config(version)
        print(f"显示名称: {config.display_name}")
        print(f"目标用户: {config.target_audience}")
        print(f"智能体数量: {len(config.agents)}")
        print(f"启用的智能体: {[agent.agent_id for agent in version_manager.get_enabled_agents(version)]}")
        print()
    
    # 测试版本对比
    print("--- 版本对比信息 ---")
    comparison = version_manager.get_version_comparison()
    print(f"支持的版本: {list(comparison['versions'].keys())}")
    print()
    
    # 测试升级路径
    print("--- 升级路径测试 ---")
    for version in ["opensource", "personal", "enterprise"]:
        upgrades = version_manager.get_upgrade_options(version)
        print(f"{version} -> {upgrades}")
    print()
    
    # 测试升级收益计算
    print("--- 升级收益计算 ---")
    benefits = version_manager.calculate_upgrade_benefits("opensource", "enterprise")
    print(f"从Opensource升级到Enterprise的收益:")
    print(f"新增智能体: {benefits['new_agents']}")
    print(f"新增功能: {benefits['new_features']}")
    print(f"限制改进: {benefits['limit_improvements']}")
    print()
    
    print("版本配置管理器测试完成！")

