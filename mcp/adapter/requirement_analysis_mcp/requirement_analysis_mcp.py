"""
需求分析工作流MCP - Requirement Analysis Workflow MCP
专门处理需求分析相关的工作流任务
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class RequirementType(Enum):
    """需求类型枚举"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER_STORY = "user_story"
    USE_CASE = "use_case"

class AnalysisPhase(Enum):
    """分析阶段枚举"""
    COLLECTION = "collection"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    APPROVAL = "approval"

class RequirementPriority(Enum):
    """需求优先级枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Requirement:
    """需求类"""
    def __init__(self, req_id: str, title: str, description: str, 
                 req_type: RequirementType, priority: RequirementPriority):
        self.req_id = req_id
        self.title = title
        self.description = description
        self.req_type = req_type
        self.priority = priority
        self.status = "draft"
        self.created_time = datetime.now()
        self.stakeholders = []
        self.acceptance_criteria = []
        self.dependencies = []
        self.estimated_effort = 0
        self.business_value = 0
        self.risk_level = "medium"

class RequirementAnalysisMcp:
    """
    需求分析工作流MCP
    专门处理需求分析相关的工作流任务
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.name = "RequirementAnalysisMcp"
        self.module_name = "requirement_analysis_mcp"
        self.module_type = "workflow_adapter"
        self.config = config or {}
        self.initialized = False
        self.version = "1.0.0"
        self.status = "inactive"
        
        # 需求管理
        self.requirements: Dict[str, Requirement] = {}
        self.analysis_sessions: Dict[str, Dict[str, Any]] = {}
        self.operation_count = 0
        
        # 分析模板和规则
        self.analysis_templates = self._initialize_analysis_templates()
        self.validation_rules = self._initialize_validation_rules()
        
        # 性能统计
        self.performance_stats = {
            "total_requirements": 0,
            "completed_analyses": 0,
            "active_sessions": 0,
            "average_analysis_time": 0.0,
            "quality_score": 0.0
        }

    def _initialize_analysis_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化分析模板"""
        return {
            "functional_requirement": {
                "sections": [
                    "需求描述", "功能规格", "输入输出", "业务规则", 
                    "异常处理", "性能要求", "接受标准"
                ],
                "questions": [
                    "这个功能的主要目的是什么？",
                    "用户如何与这个功能交互？",
                    "预期的输入和输出是什么？",
                    "有哪些业务规则需要遵循？",
                    "如何处理异常情况？"
                ]
            },
            "non_functional_requirement": {
                "sections": [
                    "性能要求", "可用性要求", "安全要求", "兼容性要求",
                    "可维护性要求", "可扩展性要求", "合规要求"
                ],
                "questions": [
                    "系统的性能指标是什么？",
                    "可用性要求是什么？",
                    "有哪些安全要求？",
                    "需要支持哪些平台和浏览器？",
                    "维护和更新的要求是什么？"
                ]
            },
            "user_story": {
                "sections": [
                    "用户角色", "用户目标", "用户价值", "接受标准", 
                    "优先级", "估算", "依赖关系"
                ],
                "template": "作为[用户角色]，我希望[功能描述]，以便[业务价值]",
                "questions": [
                    "谁是这个功能的用户？",
                    "用户想要实现什么目标？",
                    "这个功能为用户带来什么价值？",
                    "如何验证功能是否满足需求？"
                ]
            }
        }

    def _initialize_validation_rules(self) -> Dict[str, List[str]]:
        """初始化验证规则"""
        return {
            "completeness": [
                "需求描述是否完整？",
                "接受标准是否明确？",
                "优先级是否已设定？",
                "相关干系人是否已识别？"
            ],
            "consistency": [
                "需求之间是否存在冲突？",
                "术语使用是否一致？",
                "优先级设定是否合理？"
            ],
            "feasibility": [
                "技术实现是否可行？",
                "资源需求是否合理？",
                "时间估算是否现实？"
            ],
            "testability": [
                "需求是否可测试？",
                "接受标准是否可验证？",
                "测试场景是否明确？"
            ]
        }

    async def initialize(self) -> bool:
        """初始化需求分析MCP"""
        try:
            self.initialized = True
            self.status = "active"
            return True
        except Exception as e:
            self.status = "error"
            return False

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理需求分析请求"""
        try:
            self.operation_count += 1
            
            # 解析请求类型
            request_type = data.get("type", "analyze_requirement")
            
            if request_type == "analyze_requirement":
                return await self._analyze_requirement(data)
            elif request_type == "create_requirement":
                return await self._create_requirement(data)
            elif request_type == "validate_requirements":
                return await self._validate_requirements(data)
            elif request_type == "generate_documentation":
                return await self._generate_documentation(data)
            elif request_type == "estimate_effort":
                return await self._estimate_effort(data)
            elif request_type == "prioritize_requirements":
                return await self._prioritize_requirements(data)
            elif request_type == "start_analysis_session":
                return await self._start_analysis_session(data)
            elif request_type == "get_analysis_status":
                return await self._get_analysis_status(data)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown request type: {request_type}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _analyze_requirement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个需求"""
        requirement_text = data.get("requirement", "")
        req_type = data.get("requirement_type", "functional")
        session_id = data.get("session_id")
        
        # 创建需求对象
        req_id = str(uuid.uuid4())
        requirement = Requirement(
            req_id=req_id,
            title=data.get("title", "未命名需求"),
            description=requirement_text,
            req_type=RequirementType(req_type),
            priority=RequirementPriority(data.get("priority", "medium"))
        )
        
        # 执行分析
        analysis_result = await self._perform_requirement_analysis(requirement)
        
        # 保存需求
        self.requirements[req_id] = requirement
        self.performance_stats["total_requirements"] += 1
        
        return {
            "status": "success",
            "requirement_id": req_id,
            "analysis_result": analysis_result,
            "requirement_summary": {
                "title": requirement.title,
                "type": requirement.req_type.value,
                "priority": requirement.priority.value,
                "status": requirement.status
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _perform_requirement_analysis(self, requirement: Requirement) -> Dict[str, Any]:
        """执行需求分析"""
        req_type = requirement.req_type.value
        template = self.analysis_templates.get(req_type, self.analysis_templates["functional_requirement"])
        
        analysis_result = {
            "requirement_id": requirement.req_id,
            "analysis_type": req_type,
            "analysis_sections": {},
            "identified_issues": [],
            "recommendations": [],
            "quality_score": 0.0,
            "completeness_score": 0.0
        }
        
        # 分析各个部分
        for section in template["sections"]:
            section_analysis = await self._analyze_section(requirement, section)
            analysis_result["analysis_sections"][section] = section_analysis
        
        # 识别问题和建议
        issues, recommendations = await self._identify_issues_and_recommendations(requirement)
        analysis_result["identified_issues"] = issues
        analysis_result["recommendations"] = recommendations
        
        # 计算质量分数
        quality_score = await self._calculate_quality_score(requirement, analysis_result)
        analysis_result["quality_score"] = quality_score
        
        # 计算完整性分数
        completeness_score = await self._calculate_completeness_score(requirement)
        analysis_result["completeness_score"] = completeness_score
        
        return analysis_result

    async def _analyze_section(self, requirement: Requirement, section: str) -> Dict[str, Any]:
        """分析需求的特定部分"""
        # 这里实现具体的分析逻辑
        # 在实际实现中，可以使用NLP技术或规则引擎
        
        section_result = {
            "section_name": section,
            "content_found": True,
            "quality": "good",
            "suggestions": [],
            "missing_elements": []
        }
        
        # 根据不同部分进行分析
        if section == "需求描述":
            if len(requirement.description) < 50:
                section_result["quality"] = "poor"
                section_result["suggestions"].append("需求描述过于简短，建议提供更详细的说明")
        
        elif section == "接受标准":
            if not requirement.acceptance_criteria:
                section_result["content_found"] = False
                section_result["missing_elements"].append("缺少接受标准")
                section_result["suggestions"].append("请定义明确的接受标准")
        
        elif section == "优先级":
            if requirement.priority == RequirementPriority.MEDIUM:
                section_result["suggestions"].append("建议重新评估优先级，确保准确性")
        
        return section_result

    async def _identify_issues_and_recommendations(self, requirement: Requirement) -> tuple:
        """识别问题和建议"""
        issues = []
        recommendations = []
        
        # 检查需求完整性
        if len(requirement.description) < 100:
            issues.append("需求描述过于简短")
            recommendations.append("提供更详细的需求描述，包括背景、目标和约束条件")
        
        if not requirement.acceptance_criteria:
            issues.append("缺少接受标准")
            recommendations.append("定义明确的接受标准，确保需求可测试")
        
        if not requirement.stakeholders:
            issues.append("未识别相关干系人")
            recommendations.append("识别并记录所有相关干系人")
        
        # 检查需求质量
        if "应该" in requirement.description or "可能" in requirement.description:
            issues.append("需求描述存在模糊表述")
            recommendations.append("使用明确的语言，避免模糊词汇")
        
        return issues, recommendations

    async def _calculate_quality_score(self, requirement: Requirement, analysis_result: Dict[str, Any]) -> float:
        """计算需求质量分数"""
        score = 100.0
        
        # 根据发现的问题扣分
        issues_count = len(analysis_result["identified_issues"])
        score -= issues_count * 10
        
        # 根据描述长度调整分数
        if len(requirement.description) < 50:
            score -= 20
        elif len(requirement.description) < 100:
            score -= 10
        
        # 根据接受标准调整分数
        if not requirement.acceptance_criteria:
            score -= 15
        
        return max(0.0, min(100.0, score))

    async def _calculate_completeness_score(self, requirement: Requirement) -> float:
        """计算需求完整性分数"""
        total_elements = 7  # 总的必要元素数量
        present_elements = 0
        
        if requirement.title and requirement.title != "未命名需求":
            present_elements += 1
        if requirement.description and len(requirement.description) > 20:
            present_elements += 1
        if requirement.req_type:
            present_elements += 1
        if requirement.priority:
            present_elements += 1
        if requirement.acceptance_criteria:
            present_elements += 1
        if requirement.stakeholders:
            present_elements += 1
        if requirement.estimated_effort > 0:
            present_elements += 1
        
        return (present_elements / total_elements) * 100

    async def _create_requirement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新需求"""
        req_id = str(uuid.uuid4())
        
        requirement = Requirement(
            req_id=req_id,
            title=data.get("title", "新需求"),
            description=data.get("description", ""),
            req_type=RequirementType(data.get("type", "functional")),
            priority=RequirementPriority(data.get("priority", "medium"))
        )
        
        # 设置其他属性
        requirement.stakeholders = data.get("stakeholders", [])
        requirement.acceptance_criteria = data.get("acceptance_criteria", [])
        requirement.dependencies = data.get("dependencies", [])
        requirement.estimated_effort = data.get("estimated_effort", 0)
        requirement.business_value = data.get("business_value", 0)
        
        self.requirements[req_id] = requirement
        self.performance_stats["total_requirements"] += 1
        
        return {
            "status": "success",
            "requirement_id": req_id,
            "requirement": {
                "title": requirement.title,
                "type": requirement.req_type.value,
                "priority": requirement.priority.value,
                "status": requirement.status
            },
            "timestamp": datetime.now().isoformat()
        }

    async def _validate_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证需求集合"""
        requirement_ids = data.get("requirement_ids", [])
        validation_type = data.get("validation_type", "all")
        
        validation_results = {
            "total_requirements": len(requirement_ids),
            "validation_type": validation_type,
            "results": {},
            "overall_score": 0.0,
            "issues_summary": {},
            "recommendations": []
        }
        
        total_score = 0.0
        all_issues = []
        
        for req_id in requirement_ids:
            if req_id in self.requirements:
                requirement = self.requirements[req_id]
                req_validation = await self._validate_single_requirement(requirement, validation_type)
                validation_results["results"][req_id] = req_validation
                total_score += req_validation["score"]
                all_issues.extend(req_validation["issues"])
        
        # 计算总体分数
        if requirement_ids:
            validation_results["overall_score"] = total_score / len(requirement_ids)
        
        # 汇总问题
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        validation_results["issues_summary"] = issue_counts
        
        # 生成建议
        validation_results["recommendations"] = await self._generate_validation_recommendations(issue_counts)
        
        return {
            "status": "success",
            "validation_results": validation_results,
            "timestamp": datetime.now().isoformat()
        }

    async def _validate_single_requirement(self, requirement: Requirement, validation_type: str) -> Dict[str, Any]:
        """验证单个需求"""
        validation_result = {
            "requirement_id": requirement.req_id,
            "score": 0.0,
            "issues": [],
            "passed_checks": [],
            "failed_checks": []
        }
        
        checks_to_run = []
        if validation_type == "all":
            checks_to_run = ["completeness", "consistency", "feasibility", "testability"]
        else:
            checks_to_run = [validation_type]
        
        total_checks = 0
        passed_checks = 0
        
        for check_type in checks_to_run:
            if check_type in self.validation_rules:
                for rule in self.validation_rules[check_type]:
                    total_checks += 1
                    check_result = await self._apply_validation_rule(requirement, rule)
                    if check_result["passed"]:
                        passed_checks += 1
                        validation_result["passed_checks"].append(rule)
                    else:
                        validation_result["failed_checks"].append(rule)
                        validation_result["issues"].append(check_result["issue"])
        
        # 计算分数
        if total_checks > 0:
            validation_result["score"] = (passed_checks / total_checks) * 100
        
        return validation_result

    async def _apply_validation_rule(self, requirement: Requirement, rule: str) -> Dict[str, Any]:
        """应用验证规则"""
        # 这里实现具体的验证逻辑
        # 在实际实现中，可以使用更复杂的规则引擎
        
        if "描述是否完整" in rule:
            if len(requirement.description) > 50:
                return {"passed": True, "issue": None}
            else:
                return {"passed": False, "issue": "需求描述不够完整"}
        
        elif "接受标准是否明确" in rule:
            if requirement.acceptance_criteria:
                return {"passed": True, "issue": None}
            else:
                return {"passed": False, "issue": "缺少明确的接受标准"}
        
        elif "优先级是否已设定" in rule:
            if requirement.priority:
                return {"passed": True, "issue": None}
            else:
                return {"passed": False, "issue": "未设定优先级"}
        
        else:
            # 默认通过
            return {"passed": True, "issue": None}

    async def _generate_validation_recommendations(self, issue_counts: Dict[str, int]) -> List[str]:
        """生成验证建议"""
        recommendations = []
        
        if issue_counts.get("需求描述不够完整", 0) > 0:
            recommendations.append("建议为所有需求提供更详细的描述，包括背景、目标和约束条件")
        
        if issue_counts.get("缺少明确的接受标准", 0) > 0:
            recommendations.append("为每个需求定义明确的接受标准，确保需求可测试")
        
        if issue_counts.get("未设定优先级", 0) > 0:
            recommendations.append("为所有需求设定合适的优先级，便于项目规划")
        
        return recommendations

    async def _generate_documentation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成需求文档"""
        requirement_ids = data.get("requirement_ids", [])
        doc_format = data.get("format", "markdown")
        doc_type = data.get("type", "requirements_specification")
        
        documentation = {
            "document_type": doc_type,
            "format": doc_format,
            "generated_time": datetime.now().isoformat(),
            "content": "",
            "sections": [],
            "metadata": {
                "total_requirements": len(requirement_ids),
                "functional_count": 0,
                "non_functional_count": 0
            }
        }
        
        # 生成文档内容
        if doc_type == "requirements_specification":
            documentation["content"] = await self._generate_requirements_spec(requirement_ids, doc_format)
        elif doc_type == "user_stories":
            documentation["content"] = await self._generate_user_stories_doc(requirement_ids, doc_format)
        elif doc_type == "analysis_report":
            documentation["content"] = await self._generate_analysis_report(requirement_ids, doc_format)
        
        return {
            "status": "success",
            "documentation": documentation,
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_requirements_spec(self, requirement_ids: List[str], doc_format: str) -> str:
        """生成需求规格说明书"""
        content = []
        
        if doc_format == "markdown":
            content.append("# 需求规格说明书\n")
            content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            content.append("---\n")
            
            for req_id in requirement_ids:
                if req_id in self.requirements:
                    req = self.requirements[req_id]
                    content.append(f"## {req.title}\n")
                    content.append(f"**需求ID**: {req.req_id}\n")
                    content.append(f"**类型**: {req.req_type.value}\n")
                    content.append(f"**优先级**: {req.priority.value}\n")
                    content.append(f"**状态**: {req.status}\n")
                    content.append(f"**描述**: {req.description}\n")
                    
                    if req.acceptance_criteria:
                        content.append("**接受标准**:\n")
                        for criteria in req.acceptance_criteria:
                            content.append(f"- {criteria}\n")
                    
                    content.append("\n---\n")
        
        return "\n".join(content)

    async def _generate_user_stories_doc(self, requirement_ids: List[str], doc_format: str) -> str:
        """生成用户故事文档"""
        content = []
        
        if doc_format == "markdown":
            content.append("# 用户故事\n")
            content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            content.append("---\n")
            
            for req_id in requirement_ids:
                if req_id in self.requirements:
                    req = self.requirements[req_id]
                    if req.req_type == RequirementType.USER_STORY:
                        content.append(f"## {req.title}\n")
                        content.append(f"**故事ID**: {req.req_id}\n")
                        content.append(f"**优先级**: {req.priority.value}\n")
                        content.append(f"**描述**: {req.description}\n")
                        content.append("\n---\n")
        
        return "\n".join(content)

    async def _generate_analysis_report(self, requirement_ids: List[str], doc_format: str) -> str:
        """生成分析报告"""
        content = []
        
        if doc_format == "markdown":
            content.append("# 需求分析报告\n")
            content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            content.append("---\n")
            
            # 统计信息
            total_reqs = len(requirement_ids)
            functional_count = 0
            non_functional_count = 0
            
            for req_id in requirement_ids:
                if req_id in self.requirements:
                    req = self.requirements[req_id]
                    if req.req_type == RequirementType.FUNCTIONAL:
                        functional_count += 1
                    elif req.req_type == RequirementType.NON_FUNCTIONAL:
                        non_functional_count += 1
            
            content.append("## 统计概览\n")
            content.append(f"- 总需求数量: {total_reqs}\n")
            content.append(f"- 功能性需求: {functional_count}\n")
            content.append(f"- 非功能性需求: {non_functional_count}\n")
            content.append("\n")
        
        return "\n".join(content)

    async def _estimate_effort(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """估算工作量"""
        requirement_ids = data.get("requirement_ids", [])
        estimation_method = data.get("method", "story_points")
        
        estimation_results = {
            "method": estimation_method,
            "total_effort": 0,
            "individual_estimates": {},
            "confidence_level": "medium"
        }
        
        total_effort = 0
        
        for req_id in requirement_ids:
            if req_id in self.requirements:
                req = self.requirements[req_id]
                effort = await self._estimate_single_requirement(req, estimation_method)
                estimation_results["individual_estimates"][req_id] = effort
                total_effort += effort
        
        estimation_results["total_effort"] = total_effort
        
        return {
            "status": "success",
            "estimation_results": estimation_results,
            "timestamp": datetime.now().isoformat()
        }

    async def _estimate_single_requirement(self, requirement: Requirement, method: str) -> int:
        """估算单个需求的工作量"""
        # 简单的估算逻辑，实际实现中可以使用更复杂的算法
        base_effort = 1
        
        # 根据描述长度调整
        if len(requirement.description) > 200:
            base_effort += 2
        elif len(requirement.description) > 100:
            base_effort += 1
        
        # 根据类型调整
        if requirement.req_type == RequirementType.NON_FUNCTIONAL:
            base_effort += 1
        
        # 根据优先级调整
        if requirement.priority == RequirementPriority.CRITICAL:
            base_effort += 1
        
        return base_effort

    async def _prioritize_requirements(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """需求优先级排序"""
        requirement_ids = data.get("requirement_ids", [])
        criteria = data.get("criteria", ["business_value", "effort", "risk"])
        
        prioritized_requirements = []
        
        for req_id in requirement_ids:
            if req_id in self.requirements:
                req = self.requirements[req_id]
                priority_score = await self._calculate_priority_score(req, criteria)
                prioritized_requirements.append({
                    "requirement_id": req_id,
                    "title": req.title,
                    "priority": req.priority.value,
                    "priority_score": priority_score
                })
        
        # 按优先级分数排序
        prioritized_requirements.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return {
            "status": "success",
            "prioritized_requirements": prioritized_requirements,
            "criteria_used": criteria,
            "timestamp": datetime.now().isoformat()
        }

    async def _calculate_priority_score(self, requirement: Requirement, criteria: List[str]) -> float:
        """计算优先级分数"""
        score = 0.0
        
        if "business_value" in criteria:
            score += requirement.business_value * 0.4
        
        if "effort" in criteria:
            # 工作量越小，分数越高
            effort_score = max(0, 10 - requirement.estimated_effort)
            score += effort_score * 0.3
        
        if "risk" in criteria:
            # 风险越低，分数越高
            risk_scores = {"low": 10, "medium": 5, "high": 2, "critical": 0}
            score += risk_scores.get(requirement.risk_level, 5) * 0.3
        
        return score

    async def _start_analysis_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """开始分析会话"""
        session_id = data.get("session_id", str(uuid.uuid4()))
        session_type = data.get("session_type", "requirement_analysis")
        
        session_data = {
            "session_id": session_id,
            "session_type": session_type,
            "status": "active",
            "created_time": datetime.now().isoformat(),
            "requirements": [],
            "analysis_results": {},
            "current_phase": AnalysisPhase.COLLECTION.value
        }
        
        self.analysis_sessions[session_id] = session_data
        self.performance_stats["active_sessions"] = len(self.analysis_sessions)
        
        return {
            "status": "success",
            "session_id": session_id,
            "session_data": session_data,
            "timestamp": datetime.now().isoformat()
        }

    async def _get_analysis_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """获取分析状态"""
        session_id = data.get("session_id")
        
        if session_id and session_id in self.analysis_sessions:
            session_data = self.analysis_sessions[session_id]
            return {
                "status": "success",
                "session_data": session_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "error": "Analysis session not found",
                "timestamp": datetime.now().isoformat()
            }

    async def get_status(self) -> Dict[str, Any]:
        """获取MCP状态"""
        return {
            "name": self.name,
            "module_name": self.module_name,
            "type": self.module_type,
            "initialized": self.initialized,
            "status": self.status,
            "version": self.version,
            "operation_count": self.operation_count,
            "total_requirements": len(self.requirements),
            "active_sessions": len(self.analysis_sessions),
            "performance_stats": self.performance_stats,
            "timestamp": datetime.now().isoformat()
        }

    def get_info(self) -> Dict[str, Any]:
        """获取模块信息"""
        return {
            "name": self.name,
            "module_name": self.module_name,
            "type": self.module_type,
            "version": self.version,
            "description": "Requirement Analysis Workflow MCP for comprehensive requirement processing",
            "capabilities": [
                "analyze_requirement", "create_requirement", "validate_requirements",
                "generate_documentation", "estimate_effort", "prioritize_requirements",
                "start_analysis_session", "get_analysis_status"
            ],
            "supported_requirement_types": [rt.value for rt in RequirementType],
            "supported_analysis_phases": [ap.value for ap in AnalysisPhase],
            "supported_priorities": [rp.value for rp in RequirementPriority]
        }

    async def cleanup(self) -> bool:
        """清理资源"""
        try:
            self.analysis_sessions.clear()
            self.status = "inactive"
            return True
        except Exception:
            return False

# 为了兼容性，也导出原始名称
Requirementanalysismcp = RequirementAnalysisMcp

