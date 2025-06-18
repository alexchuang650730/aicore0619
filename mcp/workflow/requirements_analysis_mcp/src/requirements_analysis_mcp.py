#!/usr/bin/env python3
"""
需求分析智能引擎 MCP
Requirements Analysis Intelligent Engine MCP

基于PowerAuto架构的智能需求分析工作流
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import toml
import yaml

# 导入基础工作流类
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from workflow_howto.base_workflow import BaseWorkflow

class RequirementType(Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"
    BUSINESS = "business"

class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class DomainType(Enum):
    OCR = "ocr"
    NLP = "nlp"
    WEB = "web"
    AI = "ai"
    VISION = "vision"
    OTHER = "other"

@dataclass
class Requirement:
    id: str
    text: str
    type: RequirementType
    priority: int
    complexity: float
    dependencies: List[str]
    domain: DomainType
    confidence: float

@dataclass
class Solution:
    id: str
    title: str
    description: str
    technology_stack: List[str]
    estimated_effort: int  # 人天
    confidence: float
    pros: List[str]
    cons: List[str]
    risks: List[str]
    implementation_steps: List[str]
    timeline_estimate: str
    cost_estimate: float

@dataclass
class FeasibilityReport:
    overall_feasibility: float
    technical_challenges: List[str]
    resource_requirements: Dict[str, Any]
    timeline_estimate: int
    risk_factors: List[str]
    confidence: float

@dataclass
class RequirementAnalysisRequest:
    requirement_text: str
    context: Dict[str, Any] = None
    constraints: List[str] = None
    priority_factors: Dict[str, float] = None
    domain_type: str = "other"
    complexity_level: str = "medium"
    analysis_depth: str = "detailed"
    language_type: str = "chinese"
    privacy_level: str = "normal"
    response_time: str = "normal"

@dataclass
class RequirementAnalysisResult:
    status: str
    parsed_requirements: List[Dict]
    feasibility_report: Dict
    solutions: List[Dict]
    roadmap: Dict
    confidence: float
    processing_time: float
    adapter_used: str
    error_message: str = None

class RequirementAnalysisMCP(BaseWorkflow):
    """需求分析智能引擎MCP主类"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"
        
        super().__init__(str(config_dir))
        self.name = "需求分析智能引擎"
        self.version = "1.0.0"
        
        # 初始化处理器
        self.processors = self._initialize_processors()
        
        # 加载测试用例
        self.test_cases = self._load_test_cases()
        
    def _initialize_adapters(self) -> Dict[str, Any]:
        """初始化所需的adapter"""
        adapters = {}
        
        # 这里应该初始化实际的adapter
        # 目前使用模拟adapter
        adapters["local_model_mcp"] = MockLocalModelAdapter()
        adapters["cloud_search_mcp"] = MockCloudSearchAdapter()
        
        return adapters
    
    def _initialize_processors(self) -> Dict[str, Any]:
        """初始化处理器"""
        return {
            "InputValidator": InputValidator(),
            "RequirementPreprocessor": RequirementPreprocessor(),
            "DomainClassifier": DomainClassifier(),
            "ComplexityAssessor": ComplexityAssessor(),
            "AdapterSelector": AdapterSelector(self.routing_rules),
            "RequirementParser": RequirementParser(),
            "FeasibilityAnalyzer": FeasibilityAnalyzer(),
            "SolutionGenerator": SolutionGenerator(),
            "RiskAssessor": RiskAssessor(),
            "CostEstimator": CostEstimator(),
            "PriorityRanker": PriorityRanker(),
            "ResultFormatter": ResultFormatter(),
            "QualityValidator": QualityValidator(self.quality_settings)
        }
    
    def _load_test_cases(self) -> Dict[str, Any]:
        """加载测试用例，包含OCR测试洞察"""
        return {
            "traditional_chinese_ocr": {
                "requirement_text": """
                需要开发一个能够准确识别繁体中文保险表单的OCR系统。
                系统需要处理复杂的手写内容，包括姓名、地址等个人信息。
                特别要求能够正确识别台湾地址格式，如'604 嘉義縣竹崎鄉灣橋村五間厝58-51號'。
                目前测试发现Mistral模型识别姓名'張家銓'时错误识别为'林志玲'，
                Claude模型识别地址时也出现严重偏差，需要专门优化繁体中文识别能力。
                """,
                "context": {
                    "domain": "document_processing",
                    "target_language": "traditional_chinese",
                    "document_type": "insurance_forms",
                    "accuracy_requirement": "95%+",
                    "processing_speed": "real_time",
                    "test_findings": {
                        "mistral_errors": ["姓名识别错误: 張家銓 -> 林志玲"],
                        "claude_errors": ["地址识别错误: 完全错误的地址"],
                        "accuracy_issues": "手写繁体中文识别准确度低于30%"
                    }
                },
                "constraints": [
                    "必须支持繁体中文",
                    "手写识别准确度要求高",
                    "需要处理复杂表格结构",
                    "保护隐私数据"
                ],
                "domain_type": "ocr",
                "complexity_level": "complex",
                "language_type": "chinese"
            },
            "ocr_accuracy_challenge": {
                "requirement_text": """
                当前OCR系统在识别繁体中文手写内容时准确度严重不足。
                具体问题包括：
                1. 姓名识别：'張家銓' 被Mistral错误识别为'林志玲'
                2. 地址识别：'604 嘉義縣竹崎鄉灣橋村五間厝58-51號' 被Claude完全识别错误
                3. 金额识别：保险费'13726元'经常被识别为其他数字
                需要提升手写繁体中文的识别准确度到90%以上。
                """,
                "context": {
                    "current_accuracy": "30-50%",
                    "target_accuracy": "90%+",
                    "error_types": ["姓名识别", "地址识别", "数字识别"],
                    "test_data": "台湾保险表单",
                    "failed_models": ["mistral", "claude"],
                    "specific_errors": {
                        "name_error": "張家銓 -> 林志玲",
                        "address_error": "604 嘉義縣竹崎鄉灣橋村五間厝58-51號 -> 错误地址",
                        "amount_error": "13726元 -> 其他数字"
                    }
                },
                "constraints": [
                    "不能降低处理速度",
                    "需要保持成本可控",
                    "必须支持实时处理"
                ],
                "domain_type": "ocr",
                "complexity_level": "complex",
                "language_type": "chinese"
            }
        }
    
    async def analyze_requirements(self, request: RequirementAnalysisRequest) -> RequirementAnalysisResult:
        """分析需求的主要方法"""
        start_time = time.time()
        
        try:
            # 转换为内部格式
            context = {
                "request": asdict(request),
                "results": {},
                "metadata": {
                    "start_time": start_time,
                    "workflow_version": self.version
                }
            }
            
            # 执行工作流
            result = await self.execute_workflow(context)
            
            processing_time = time.time() - start_time
            
            return RequirementAnalysisResult(
                status="success",
                parsed_requirements=result.get("parsed_requirements", []),
                feasibility_report=result.get("feasibility_report", {}),
                solutions=result.get("solutions", []),
                roadmap=result.get("roadmap", {}),
                confidence=result.get("confidence", 0.0),
                processing_time=processing_time,
                adapter_used=result.get("adapter_used", "unknown")
            )
            
        except Exception as e:
            self.logger.error(f"需求分析失败: {e}")
            processing_time = time.time() - start_time
            
            return RequirementAnalysisResult(
                status="error",
                parsed_requirements=[],
                feasibility_report={},
                solutions=[],
                roadmap={},
                confidence=0.0,
                processing_time=processing_time,
                adapter_used="none",
                error_message=str(e)
            )
    
    async def execute_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整工作流"""
        request = context["request"]
        
        # 执行所有处理步骤
        for step in self.processing_steps['steps']:
            if self._should_execute_step(step, context):
                try:
                    result = await self.execute_step(step, context)
                    context['results'][step['id']] = result
                    
                    # 记录关键步骤结果
                    if step['id'] == 'adapter_selection':
                        context['metadata']['adapter_used'] = result.get('selected_adapter', 'unknown')
                        
                except Exception as e:
                    self.logger.error(f"步骤 {step['id']} 执行失败: {e}")
                    if step.get('required', True):
                        raise e
                    else:
                        context['results'][step['id']] = {"error": str(e)}
        
        return self._format_final_result(context)
    
    async def execute_step(self, step_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个处理步骤"""
        processor_name = step_config['processor']
        processor = self.processors.get(processor_name)
        
        if not processor:
            raise ValueError(f"处理器 {processor_name} 未找到")
        
        # 执行处理器
        if hasattr(processor, 'process_async'):
            return await processor.process_async(context)
        else:
            return processor.process(context)
    
    def _should_execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """判断是否应该执行某个步骤"""
        # 检查条件
        conditions = step.get('conditions', {})
        if conditions:
            for condition_key, condition_value in conditions.items():
                if condition_key in self.config['analysis_settings']:
                    config_value = self.config['analysis_settings'][condition_key]
                    if not self._evaluate_condition(config_value, condition_value):
                        return False
        
        return True
    
    def _evaluate_condition(self, config_value: Any, condition_value: str) -> bool:
        """评估条件表达式"""
        if condition_value.startswith('>'):
            threshold = float(condition_value[1:].strip())
            return float(config_value) > threshold
        elif condition_value.startswith('<'):
            threshold = float(condition_value[1:].strip())
            return float(config_value) < threshold
        else:
            return str(config_value) == condition_value
    
    def _format_final_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """格式化最终结果"""
        results = context['results']
        
        return {
            "parsed_requirements": results.get('requirement_parsing', {}).get('requirements', []),
            "feasibility_report": results.get('feasibility_analysis', {}),
            "solutions": results.get('solution_generation', {}).get('solutions', []),
            "roadmap": results.get('priority_ranking', {}).get('roadmap', {}),
            "confidence": results.get('quality_validation', {}).get('overall_confidence', 0.0),
            "adapter_used": context['metadata'].get('adapter_used', 'unknown'),
            "processing_metadata": {
                "steps_executed": list(results.keys()),
                "total_steps": len(self.processing_steps['steps']),
                "workflow_version": self.version
            }
        }
    
    def _handle_workflow_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作流错误"""
        return {
            "status": "error",
            "error_message": str(error),
            "partial_results": context.get('results', {}),
            "failed_at": context.get('current_step', 'unknown')
        }

# 处理器实现类
class InputValidator:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context["request"]
        
        # 验证必需字段
        required_fields = ["requirement_text"]
        for field in required_fields:
            if not request.get(field):
                raise ValueError(f"缺少必需字段: {field}")
        
        # 验证文本长度
        text = request["requirement_text"]
        if len(text) < 10:
            raise ValueError("需求描述过短，至少需要10个字符")
        if len(text) > 10000:
            raise ValueError("需求描述过长，最多10000个字符")
        
        return {"status": "valid", "validated_fields": required_fields}

class RequirementPreprocessor:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context["request"]
        text = request["requirement_text"]
        
        # 清理文本
        cleaned_text = text.strip()
        cleaned_text = " ".join(cleaned_text.split())  # 标准化空白字符
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "text_length": len(cleaned_text)
        }

class DomainClassifier:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context["request"]
        text = request["requirement_text"].lower()
        
        # 简单的关键词分类
        domain_keywords = {
            "ocr": ["识别", "ocr", "文字", "图像", "扫描", "手写", "繁体", "表单"],
            "nlp": ["自然语言", "文本分析", "语言模型", "nlp"],
            "web": ["网站", "前端", "后端", "api", "web"],
            "ai": ["机器学习", "深度学习", "神经网络", "ai", "人工智能"],
            "vision": ["计算机视觉", "图像识别", "视觉"]
        }
        
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            domain_scores[domain] = score
        
        # 选择得分最高的领域
        classified_domain = max(domain_scores, key=domain_scores.get)
        confidence = domain_scores[classified_domain] / len(domain_keywords[classified_domain])
        
        return {
            "classified_domain": classified_domain,
            "confidence": confidence,
            "domain_scores": domain_scores
        }

class ComplexityAssessor:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context["request"]
        text = request["requirement_text"]
        
        # 简单的复杂度评估
        complexity_indicators = {
            "simple": ["简单", "基础", "基本"],
            "medium": ["中等", "一般", "标准"],
            "complex": ["复杂", "高级", "困难", "挑战", "多", "集成"]
        }
        
        complexity_score = 0
        for indicator in complexity_indicators["complex"]:
            if indicator in text:
                complexity_score += 1
        
        if complexity_score >= 2:
            level = "complex"
        elif complexity_score >= 1:
            level = "medium"
        else:
            level = "simple"
        
        return {
            "complexity_level": level,
            "complexity_score": complexity_score,
            "confidence": 0.8
        }

class AdapterSelector:
    def __init__(self, routing_rules: Dict[str, Any]):
        self.routing_rules = routing_rules
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context["request"]
        results = context["results"]
        
        # 获取分类结果
        domain = results.get("domain_classification", {}).get("classified_domain", "other")
        complexity = results.get("complexity_assessment", {}).get("complexity_level", "medium")
        
        # 根据路由规则选择适配器
        domain_adapter = self.routing_rules["routing_rules"]["domain_type"].get(domain, "local_model_mcp")
        complexity_adapter = self.routing_rules["routing_rules"]["complexity_level"].get(complexity, "local_model_mcp")
        
        # 简单的选择逻辑：优先考虑领域
        selected_adapter = domain_adapter
        
        return {
            "selected_adapter": selected_adapter,
            "domain_recommendation": domain_adapter,
            "complexity_recommendation": complexity_adapter,
            "confidence": 0.9
        }

class RequirementParser:
    async def process_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        request = context["request"]
        adapter_result = context["results"]["adapter_selection"]
        
        # 模拟AI解析
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        requirements = [
            {
                "id": "req_1",
                "text": "繁体中文OCR识别",
                "type": "functional",
                "priority": 1,
                "complexity": 0.9,
                "domain": "ocr",
                "confidence": 0.85
            },
            {
                "id": "req_2", 
                "text": "手写文字识别",
                "type": "functional",
                "priority": 2,
                "complexity": 0.95,
                "domain": "ocr",
                "confidence": 0.8
            }
        ]
        
        return {
            "requirements": requirements,
            "parsing_confidence": 0.85,
            "adapter_used": adapter_result["selected_adapter"]
        }

class FeasibilityAnalyzer:
    async def process_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 模拟可行性分析
        await asyncio.sleep(0.1)
        
        return {
            "overall_feasibility": 0.8,
            "technical_challenges": [
                "繁体中文字符复杂度高",
                "手写文字变形严重",
                "需要大量训练数据"
            ],
            "resource_requirements": {
                "development_time": "3-6个月",
                "team_size": "3-5人",
                "budget_estimate": "50-100万"
            },
            "confidence": 0.8
        }

class SolutionGenerator:
    async def process_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 模拟方案生成
        await asyncio.sleep(0.1)
        
        solutions = [
            {
                "id": "sol_1",
                "title": "多模型融合OCR方案",
                "description": "结合Mistral、Claude、Gemini等多个模型，通过投票机制提升准确度",
                "technology_stack": ["Mistral", "Claude", "Gemini", "Python", "FastAPI"],
                "estimated_effort": 90,
                "confidence": 0.9,
                "pros": ["准确度高", "鲁棒性强"],
                "cons": ["成本较高", "响应时间长"],
                "risks": ["API依赖", "成本控制"],
                "implementation_steps": [
                    "集成多个OCR模型API",
                    "实现投票算法",
                    "优化响应时间",
                    "建立质量监控"
                ],
                "timeline_estimate": "3-4个月",
                "cost_estimate": 80000
            },
            {
                "id": "sol_2",
                "title": "专用繁体中文OCR训练",
                "description": "基于大量繁体中文数据训练专用OCR模型",
                "technology_stack": ["PyTorch", "Transformers", "ONNX", "Docker"],
                "estimated_effort": 120,
                "confidence": 0.85,
                "pros": ["针对性强", "可控性高"],
                "cons": ["开发周期长", "需要大量数据"],
                "risks": ["训练数据获取", "模型性能不确定"],
                "implementation_steps": [
                    "收集繁体中文训练数据",
                    "设计模型架构",
                    "训练和优化模型",
                    "部署和测试"
                ],
                "timeline_estimate": "4-6个月",
                "cost_estimate": 120000
            }
        ]
        
        return {
            "solutions": solutions,
            "generation_confidence": 0.88
        }

class RiskAssessor:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "risk_factors": [
                "技术复杂度高",
                "数据质量依赖",
                "成本控制挑战"
            ],
            "risk_levels": {
                "technical": "high",
                "cost": "medium", 
                "timeline": "medium"
            },
            "confidence": 0.8
        }

class CostEstimator:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "development_cost": 100000,
            "operational_cost": 20000,
            "total_cost": 120000,
            "confidence": 0.75
        }

class PriorityRanker:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        solutions = context["results"]["solution_generation"]["solutions"]
        
        # 简单的优先级排序
        ranked_solutions = sorted(solutions, key=lambda x: x["confidence"], reverse=True)
        
        roadmap = {
            "phase_1": "需求分析和技术调研",
            "phase_2": "原型开发和测试",
            "phase_3": "系统集成和优化",
            "phase_4": "部署和运维"
        }
        
        return {
            "ranked_solutions": ranked_solutions,
            "roadmap": roadmap,
            "ranking_confidence": 0.85
        }

class ResultFormatter:
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "format": "json",
            "timestamp": time.time(),
            "version": "1.0.0"
        }

class QualityValidator:
    def __init__(self, quality_settings: Dict[str, Any]):
        self.quality_settings = quality_settings
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        results = context["results"]
        
        # 计算总体置信度
        confidences = []
        for step_result in results.values():
            if isinstance(step_result, dict) and "confidence" in step_result:
                confidences.append(step_result["confidence"])
        
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # 检查质量阈值
        min_threshold = self.quality_settings["quality"]["min_confidence"]
        quality_passed = overall_confidence >= min_threshold
        
        return {
            "overall_confidence": overall_confidence,
            "quality_passed": quality_passed,
            "individual_confidences": confidences,
            "quality_threshold": min_threshold
        }

# 模拟适配器类
class MockLocalModelAdapter:
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {"result": "local_model_result", "confidence": 0.8}

class MockCloudSearchAdapter:
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {"result": "cloud_search_result", "confidence": 0.9}

# 测试用例执行器
class RequirementAnalysisTestRunner:
    """需求分析测试用例执行器"""
    
    def __init__(self, mcp: RequirementAnalysisMCP):
        self.mcp = mcp
    
    async def run_ocr_test_cases(self) -> Dict[str, Any]:
        """运行OCR相关的测试用例"""
        results = {}
        
        # 测试繁体中文OCR需求分析
        traditional_chinese_case = self.mcp.test_cases["traditional_chinese_ocr"]
        traditional_chinese_request = RequirementAnalysisRequest(**traditional_chinese_case)
        
        traditional_chinese_result = await self.mcp.analyze_requirements(traditional_chinese_request)
        results["traditional_chinese_ocr"] = asdict(traditional_chinese_result)
        
        # 测试OCR准确度挑战分析
        accuracy_challenge_case = self.mcp.test_cases["ocr_accuracy_challenge"]
        accuracy_challenge_request = RequirementAnalysisRequest(**accuracy_challenge_case)
        
        accuracy_challenge_result = await self.mcp.analyze_requirements(accuracy_challenge_request)
        results["accuracy_challenge"] = asdict(accuracy_challenge_result)
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试用例"""
        ocr_results = await self.run_ocr_test_cases()
        
        return {
            "test_summary": {
                "total_tests": len(ocr_results),
                "passed_tests": sum(1 for r in ocr_results.values() if r["status"] == "success"),
                "failed_tests": sum(1 for r in ocr_results.values() if r["status"] == "error")
            },
            "test_results": ocr_results
        }

if __name__ == "__main__":
    # MCP启动入口
    async def main():
        # 初始化MCP
        config_dir = Path(__file__).parent / "config"
        mcp = RequirementAnalysisMCP(str(config_dir))
        
        print(f"🚀 启动 {mcp.name} v{mcp.version}")
        
        # 运行测试用例
        test_runner = RequirementAnalysisTestRunner(mcp)
        test_results = await test_runner.run_all_tests()
        
        print("\n📊 需求分析测试结果:")
        print(json.dumps(test_results, indent=2, ensure_ascii=False))
        
        # 运行单个测试示例
        print("\n🧪 运行单个测试示例:")
        sample_request = RequirementAnalysisRequest(
            requirement_text="需要开发一个繁体中文OCR系统，能够识别手写文字",
            domain_type="ocr",
            complexity_level="complex",
            language_type="chinese"
        )
        
        result = await mcp.analyze_requirements(sample_request)
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    
    asyncio.run(main())

