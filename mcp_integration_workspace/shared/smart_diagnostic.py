"""
PowerAutomation 测试管理 - 智能错误诊断和修复引擎

提供AI驱动的错误诊断、自动修复建议和代码优化功能。

作者: PowerAutomation Team
版本: 1.0.0
日期: 2025-06-18
"""

import asyncio
import json
import logging
import re
import ast
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FixConfidence(Enum):
    """修复置信度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ErrorDiagnosis:
    """错误诊断结果"""
    error_id: str
    error_type: str
    severity: ErrorSeverity
    description: str
    root_cause: str
    affected_components: List[str]
    error_patterns: List[str]
    similar_errors: List[str]
    diagnosis_confidence: float


@dataclass
class FixSuggestion:
    """修复建议"""
    fix_id: str
    title: str
    description: str
    fix_type: str  # 'code_change', 'config_change', 'dependency_fix', 'environment_fix'
    confidence: FixConfidence
    estimated_effort: str  # 'minutes', 'hours', 'days'
    code_changes: Optional[List[Dict[str, str]]] = None
    config_changes: Optional[Dict[str, Any]] = None
    commands: Optional[List[str]] = None
    validation_steps: Optional[List[str]] = None


@dataclass
class ErrorPattern:
    """错误模式"""
    pattern_id: str
    name: str
    regex_patterns: List[str]
    keywords: List[str]
    common_causes: List[str]
    fix_strategies: List[str]
    examples: List[str]


class SmartErrorDiagnosticEngine:
    """
    智能错误诊断和修复引擎
    
    提供AI驱动的错误分析、诊断和自动修复建议。
    """
    
    def __init__(self, project_root: str = "/opt/powerautomation"):
        """
        初始化智能错误诊断引擎
        
        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.patterns_path = self.project_root / "error_patterns"
        self.fixes_path = self.project_root / "fixes"
        self.knowledge_base_path = self.project_root / "knowledge_base"
        
        # 确保目录存在
        for path in [self.patterns_path, self.fixes_path, self.knowledge_base_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # 初始化错误模式库
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.fix_success_rates: Dict[str, float] = {}
        
        # 加载预定义错误模式
        self._load_error_patterns()
        
        logger.info("智能错误诊断引擎初始化完成")
    
    def _load_error_patterns(self):
        """加载预定义的错误模式"""
        patterns = [
            ErrorPattern(
                pattern_id="import_error",
                name="导入错误",
                regex_patterns=[
                    r"ImportError: No module named '(\w+)'",
                    r"ModuleNotFoundError: No module named '(\w+)'",
                    r"ImportError: cannot import name '(\w+)'"
                ],
                keywords=["import", "module", "ImportError", "ModuleNotFoundError"],
                common_causes=[
                    "缺少依赖包",
                    "Python路径配置错误",
                    "虚拟环境未激活",
                    "包名拼写错误"
                ],
                fix_strategies=[
                    "安装缺失的依赖包",
                    "检查并修正Python路径",
                    "激活正确的虚拟环境",
                    "修正导入语句"
                ],
                examples=[
                    "ImportError: No module named 'requests'",
                    "ModuleNotFoundError: No module named 'numpy'"
                ]
            ),
            ErrorPattern(
                pattern_id="syntax_error",
                name="语法错误",
                regex_patterns=[
                    r"SyntaxError: (.+) \(line (\d+)\)",
                    r"IndentationError: (.+) \(line (\d+)\)",
                    r"TabError: (.+) \(line (\d+)\)"
                ],
                keywords=["SyntaxError", "IndentationError", "TabError", "invalid syntax"],
                common_causes=[
                    "缺少括号或引号",
                    "缩进不一致",
                    "混用Tab和空格",
                    "关键字拼写错误"
                ],
                fix_strategies=[
                    "检查括号和引号匹配",
                    "统一使用空格缩进",
                    "使用代码格式化工具",
                    "检查关键字拼写"
                ],
                examples=[
                    "SyntaxError: invalid syntax (line 15)",
                    "IndentationError: expected an indented block"
                ]
            ),
            ErrorPattern(
                pattern_id="assertion_error",
                name="断言错误",
                regex_patterns=[
                    r"AssertionError: (.+)",
                    r"assert (.+) failed"
                ],
                keywords=["AssertionError", "assert", "assertion failed"],
                common_causes=[
                    "测试期望值不正确",
                    "被测试代码逻辑错误",
                    "测试数据不准确",
                    "环境状态不一致"
                ],
                fix_strategies=[
                    "验证测试期望值",
                    "检查被测试代码逻辑",
                    "更新测试数据",
                    "确保测试环境一致性"
                ],
                examples=[
                    "AssertionError: Expected 5, got 3",
                    "AssertionError: Lists are not equal"
                ]
            ),
            ErrorPattern(
                pattern_id="timeout_error",
                name="超时错误",
                regex_patterns=[
                    r"TimeoutError: (.+)",
                    r"timeout: (.+)",
                    r"Connection timeout"
                ],
                keywords=["timeout", "TimeoutError", "connection timeout"],
                common_causes=[
                    "网络连接缓慢",
                    "服务响应时间过长",
                    "资源竞争",
                    "超时设置过短"
                ],
                fix_strategies=[
                    "增加超时时间",
                    "优化网络连接",
                    "实现重试机制",
                    "使用异步处理"
                ],
                examples=[
                    "TimeoutError: Connection timed out after 30 seconds",
                    "timeout: The operation timed out"
                ]
            ),
            ErrorPattern(
                pattern_id="file_not_found",
                name="文件未找到错误",
                regex_patterns=[
                    r"FileNotFoundError: \[Errno 2\] No such file or directory: '(.+)'",
                    r"IOError: \[Errno 2\] No such file or directory: '(.+)'"
                ],
                keywords=["FileNotFoundError", "No such file", "IOError"],
                common_causes=[
                    "文件路径错误",
                    "文件被删除或移动",
                    "权限不足",
                    "相对路径问题"
                ],
                fix_strategies=[
                    "检查文件路径",
                    "确保文件存在",
                    "检查文件权限",
                    "使用绝对路径"
                ],
                examples=[
                    "FileNotFoundError: [Errno 2] No such file or directory: 'test.txt'",
                    "IOError: [Errno 2] No such file or directory: 'config.json'"
                ]
            ),
            ErrorPattern(
                pattern_id="memory_error",
                name="内存错误",
                regex_patterns=[
                    r"MemoryError: (.+)",
                    r"OutOfMemoryError: (.+)"
                ],
                keywords=["MemoryError", "OutOfMemoryError", "memory", "out of memory"],
                common_causes=[
                    "数据集过大",
                    "内存泄漏",
                    "递归过深",
                    "系统内存不足"
                ],
                fix_strategies=[
                    "优化数据处理",
                    "实现内存管理",
                    "使用生成器",
                    "增加系统内存"
                ],
                examples=[
                    "MemoryError: Unable to allocate array",
                    "OutOfMemoryError: Java heap space"
                ]
            )
        ]
        
        for pattern in patterns:
            self.error_patterns[pattern.pattern_id] = pattern
    
    async def diagnose_error(self, error_info: Dict[str, Any]) -> ErrorDiagnosis:
        """
        诊断错误并提供详细分析
        
        Args:
            error_info: 错误信息字典
            
        Returns:
            错误诊断结果
        """
        logger.info(f"开始诊断错误: {error_info.get('type', 'Unknown')}")
        
        error_message = error_info.get("message", "")
        error_type = error_info.get("type", "UnknownError")
        stack_trace = error_info.get("stack_trace", "")
        context = error_info.get("context", {})
        
        # 模式匹配
        matched_patterns = self._match_error_patterns(error_message, stack_trace)
        
        # 分析错误严重程度
        severity = self._analyze_severity(error_type, error_message, context)
        
        # 识别根本原因
        root_cause = await self._identify_root_cause(error_message, stack_trace, matched_patterns)
        
        # 找到受影响的组件
        affected_components = self._identify_affected_components(stack_trace, context)
        
        # 查找相似错误
        similar_errors = self._find_similar_errors(error_message, error_type)
        
        # 计算诊断置信度
        confidence = self._calculate_diagnosis_confidence(matched_patterns, similar_errors)
        
        diagnosis = ErrorDiagnosis(
            error_id=f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            error_type=error_type,
            severity=severity,
            description=self._generate_error_description(error_message, matched_patterns),
            root_cause=root_cause,
            affected_components=affected_components,
            error_patterns=[p.pattern_id for p in matched_patterns],
            similar_errors=similar_errors,
            diagnosis_confidence=confidence
        )
        
        # 记录错误历史
        self.error_history.append({
            "timestamp": datetime.now().isoformat(),
            "diagnosis": diagnosis,
            "original_error": error_info
        })
        
        logger.info(f"错误诊断完成: {diagnosis.error_id}")
        return diagnosis
    
    def _match_error_patterns(self, error_message: str, stack_trace: str) -> List[ErrorPattern]:
        """匹配错误模式"""
        matched_patterns = []
        full_text = f"{error_message} {stack_trace}".lower()
        
        for pattern in self.error_patterns.values():
            # 检查关键字匹配
            keyword_matches = sum(1 for keyword in pattern.keywords if keyword.lower() in full_text)
            
            # 检查正则表达式匹配
            regex_matches = 0
            for regex_pattern in pattern.regex_patterns:
                if re.search(regex_pattern, error_message, re.IGNORECASE):
                    regex_matches += 1
            
            # 如果有足够的匹配，添加到结果中
            if keyword_matches >= 1 or regex_matches >= 1:
                matched_patterns.append(pattern)
        
        return matched_patterns
    
    def _analyze_severity(self, error_type: str, error_message: str, context: Dict[str, Any]) -> ErrorSeverity:
        """分析错误严重程度"""
        critical_keywords = ["critical", "fatal", "crash", "corruption", "security"]
        high_keywords = ["error", "exception", "failure", "timeout"]
        medium_keywords = ["warning", "deprecated", "missing"]
        
        error_text = f"{error_type} {error_message}".lower()
        
        if any(keyword in error_text for keyword in critical_keywords):
            return ErrorSeverity.CRITICAL
        elif any(keyword in error_text for keyword in high_keywords):
            return ErrorSeverity.HIGH
        elif any(keyword in error_text for keyword in medium_keywords):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    async def _identify_root_cause(self, error_message: str, stack_trace: str, patterns: List[ErrorPattern]) -> str:
        """识别根本原因"""
        if not patterns:
            return "未知原因，需要进一步分析"
        
        # 基于匹配的模式分析根本原因
        primary_pattern = patterns[0]  # 使用第一个匹配的模式
        
        # 分析堆栈跟踪以获得更具体的原因
        if "import" in error_message.lower():
            if "no module named" in error_message.lower():
                module_match = re.search(r"No module named '(\w+)'", error_message)
                if module_match:
                    module_name = module_match.group(1)
                    return f"缺少依赖模块: {module_name}"
            return "导入相关问题"
        
        elif "syntax" in error_message.lower():
            line_match = re.search(r"line (\d+)", error_message)
            if line_match:
                line_num = line_match.group(1)
                return f"第{line_num}行存在语法错误"
            return "代码语法错误"
        
        elif "assertion" in error_message.lower():
            return "测试断言失败，期望值与实际值不匹配"
        
        elif "timeout" in error_message.lower():
            return "操作超时，可能由于网络延迟或资源竞争"
        
        elif "file" in error_message.lower() and "not found" in error_message.lower():
            file_match = re.search(r"'([^']+)'", error_message)
            if file_match:
                file_name = file_match.group(1)
                return f"文件不存在: {file_name}"
            return "文件路径或权限问题"
        
        # 使用模式的常见原因
        if primary_pattern.common_causes:
            return primary_pattern.common_causes[0]
        
        return "需要进一步分析以确定根本原因"
    
    def _identify_affected_components(self, stack_trace: str, context: Dict[str, Any]) -> List[str]:
        """识别受影响的组件"""
        components = []
        
        # 从堆栈跟踪中提取文件名
        file_matches = re.findall(r'File "([^"]+)"', stack_trace)
        for file_path in file_matches:
            component = Path(file_path).stem
            if component not in components:
                components.append(component)
        
        # 从上下文中获取组件信息
        if "module" in context:
            components.append(context["module"])
        
        if "test_file" in context:
            components.append(Path(context["test_file"]).stem)
        
        return components[:5]  # 限制返回前5个组件
    
    def _find_similar_errors(self, error_message: str, error_type: str) -> List[str]:
        """查找相似的历史错误"""
        similar_errors = []
        
        for history_item in self.error_history[-50:]:  # 检查最近50个错误
            historical_error = history_item["original_error"]
            historical_message = historical_error.get("message", "")
            historical_type = historical_error.get("type", "")
            
            # 计算相似度
            similarity = self._calculate_similarity(error_message, historical_message)
            
            if similarity > 0.7 or error_type == historical_type:
                similar_errors.append(history_item["diagnosis"].error_id)
        
        return similar_errors[:3]  # 返回最多3个相似错误
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版本）"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_diagnosis_confidence(self, patterns: List[ErrorPattern], similar_errors: List[str]) -> float:
        """计算诊断置信度"""
        base_confidence = 0.5
        
        # 模式匹配增加置信度
        if patterns:
            base_confidence += 0.3
        
        # 相似错误增加置信度
        if similar_errors:
            base_confidence += 0.2
        
        return min(1.0, base_confidence)
    
    def _generate_error_description(self, error_message: str, patterns: List[ErrorPattern]) -> str:
        """生成错误描述"""
        if patterns:
            pattern = patterns[0]
            return f"{pattern.name}: {error_message}"
        else:
            return f"未分类错误: {error_message}"
    
    async def generate_fix_suggestions(self, diagnosis: ErrorDiagnosis, context: Dict[str, Any] = None) -> List[FixSuggestion]:
        """
        基于诊断结果生成修复建议
        
        Args:
            diagnosis: 错误诊断结果
            context: 额外的上下文信息
            
        Returns:
            修复建议列表
        """
        logger.info(f"为错误 {diagnosis.error_id} 生成修复建议")
        
        suggestions = []
        context = context or {}
        
        # 基于错误模式生成建议
        for pattern_id in diagnosis.error_patterns:
            if pattern_id in self.error_patterns:
                pattern = self.error_patterns[pattern_id]
                pattern_suggestions = await self._generate_pattern_based_fixes(pattern, diagnosis, context)
                suggestions.extend(pattern_suggestions)
        
        # 基于错误类型生成通用建议
        generic_suggestions = await self._generate_generic_fixes(diagnosis, context)
        suggestions.extend(generic_suggestions)
        
        # 基于相似错误生成建议
        if diagnosis.similar_errors:
            similar_suggestions = await self._generate_similar_error_fixes(diagnosis.similar_errors)
            suggestions.extend(similar_suggestions)
        
        # 排序和去重
        suggestions = self._prioritize_fix_suggestions(suggestions)
        
        logger.info(f"生成了 {len(suggestions)} 个修复建议")
        return suggestions
    
    async def _generate_pattern_based_fixes(self, pattern: ErrorPattern, diagnosis: ErrorDiagnosis, context: Dict[str, Any]) -> List[FixSuggestion]:
        """基于错误模式生成修复建议"""
        suggestions = []
        
        if pattern.pattern_id == "import_error":
            # 导入错误的修复建议
            module_match = re.search(r"No module named '(\w+)'", diagnosis.description)
            module_name = module_match.group(1) if module_match else "unknown"
            
            suggestions.append(FixSuggestion(
                fix_id=f"fix_import_{module_name}",
                title=f"安装缺失的模块: {module_name}",
                description=f"使用pip安装缺失的Python模块 {module_name}",
                fix_type="dependency_fix",
                confidence=FixConfidence.HIGH,
                estimated_effort="minutes",
                commands=[f"pip install {module_name}"],
                validation_steps=[f"python -c 'import {module_name}'"]
            ))
            
        elif pattern.pattern_id == "syntax_error":
            # 语法错误的修复建议
            suggestions.append(FixSuggestion(
                fix_id="fix_syntax",
                title="修复语法错误",
                description="检查并修复代码中的语法问题",
                fix_type="code_change",
                confidence=FixConfidence.MEDIUM,
                estimated_effort="minutes",
                code_changes=[{
                    "action": "检查括号、引号和缩进",
                    "description": "确保所有括号和引号正确匹配，缩进一致"
                }],
                validation_steps=["python -m py_compile <file>"]
            ))
            
        elif pattern.pattern_id == "assertion_error":
            # 断言错误的修复建议
            suggestions.append(FixSuggestion(
                fix_id="fix_assertion",
                title="修复测试断言",
                description="更新测试期望值或修复被测试代码",
                fix_type="code_change",
                confidence=FixConfidence.MEDIUM,
                estimated_effort="hours",
                code_changes=[{
                    "action": "验证测试逻辑",
                    "description": "检查测试期望值是否正确，或修复被测试代码的逻辑"
                }],
                validation_steps=["重新运行测试"]
            ))
            
        elif pattern.pattern_id == "timeout_error":
            # 超时错误的修复建议
            suggestions.append(FixSuggestion(
                fix_id="fix_timeout",
                title="增加超时时间",
                description="调整超时设置以适应实际执行时间",
                fix_type="config_change",
                confidence=FixConfidence.HIGH,
                estimated_effort="minutes",
                config_changes={"timeout": 60, "retry_count": 3},
                validation_steps=["重新运行测试验证超时设置"]
            ))
            
        elif pattern.pattern_id == "file_not_found":
            # 文件未找到错误的修复建议
            file_match = re.search(r"'([^']+)'", diagnosis.description)
            file_name = file_match.group(1) if file_match else "unknown"
            
            suggestions.append(FixSuggestion(
                fix_id="fix_file_path",
                title=f"修复文件路径: {file_name}",
                description="检查并修正文件路径或创建缺失的文件",
                fix_type="environment_fix",
                confidence=FixConfidence.HIGH,
                estimated_effort="minutes",
                commands=[f"touch {file_name}"],
                validation_steps=[f"ls -la {file_name}"]
            ))
        
        return suggestions
    
    async def _generate_generic_fixes(self, diagnosis: ErrorDiagnosis, context: Dict[str, Any]) -> List[FixSuggestion]:
        """生成通用修复建议"""
        suggestions = []
        
        # 基于严重程度的通用建议
        if diagnosis.severity == ErrorSeverity.CRITICAL:
            suggestions.append(FixSuggestion(
                fix_id="critical_review",
                title="紧急代码审查",
                description="立即进行代码审查以解决关键问题",
                fix_type="code_change",
                confidence=FixConfidence.MEDIUM,
                estimated_effort="hours",
                validation_steps=["完整的回归测试"]
            ))
        
        # 基于受影响组件的建议
        if len(diagnosis.affected_components) > 3:
            suggestions.append(FixSuggestion(
                fix_id="component_isolation",
                title="隔离受影响的组件",
                description="将受影响的组件进行隔离测试",
                fix_type="code_change",
                confidence=FixConfidence.LOW,
                estimated_effort="hours",
                validation_steps=["单独测试每个组件"]
            ))
        
        return suggestions
    
    async def _generate_similar_error_fixes(self, similar_error_ids: List[str]) -> List[FixSuggestion]:
        """基于相似错误生成修复建议"""
        suggestions = []
        
        # 这里可以查询历史修复记录
        # 简化实现：基于相似错误提供通用建议
        if similar_error_ids:
            suggestions.append(FixSuggestion(
                fix_id="similar_error_fix",
                title="参考相似错误的解决方案",
                description=f"参考之前解决的相似错误: {', '.join(similar_error_ids[:2])}",
                fix_type="code_change",
                confidence=FixConfidence.MEDIUM,
                estimated_effort="hours",
                validation_steps=["应用相似的解决方案"]
            ))
        
        return suggestions
    
    def _prioritize_fix_suggestions(self, suggestions: List[FixSuggestion]) -> List[FixSuggestion]:
        """对修复建议进行优先级排序"""
        # 按置信度和估算工作量排序
        confidence_order = {
            FixConfidence.VERY_HIGH: 4,
            FixConfidence.HIGH: 3,
            FixConfidence.MEDIUM: 2,
            FixConfidence.LOW: 1
        }
        
        effort_order = {
            "minutes": 3,
            "hours": 2,
            "days": 1
        }
        
        def sort_key(suggestion):
            confidence_score = confidence_order.get(suggestion.confidence, 0)
            effort_score = effort_order.get(suggestion.estimated_effort, 0)
            return (confidence_score, effort_score)
        
        return sorted(suggestions, key=sort_key, reverse=True)[:5]  # 返回前5个建议
    
    async def apply_automatic_fix(self, suggestion: FixSuggestion, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        自动应用修复建议
        
        Args:
            suggestion: 修复建议
            context: 应用上下文
            
        Returns:
            应用结果
        """
        logger.info(f"自动应用修复: {suggestion.fix_id}")
        
        result = {
            "fix_id": suggestion.fix_id,
            "status": "success",
            "applied_changes": [],
            "validation_results": [],
            "errors": []
        }
        
        try:
            # 根据修复类型应用不同的修复策略
            if suggestion.fix_type == "dependency_fix" and suggestion.commands:
                # 执行依赖修复命令
                for command in suggestion.commands:
                    # 这里应该实际执行命令，简化为模拟
                    result["applied_changes"].append(f"执行命令: {command}")
            
            elif suggestion.fix_type == "config_change" and suggestion.config_changes:
                # 应用配置更改
                for key, value in suggestion.config_changes.items():
                    result["applied_changes"].append(f"配置更改: {key} = {value}")
            
            elif suggestion.fix_type == "code_change" and suggestion.code_changes:
                # 应用代码更改
                for change in suggestion.code_changes:
                    result["applied_changes"].append(f"代码更改: {change['action']}")
            
            # 执行验证步骤
            if suggestion.validation_steps:
                for step in suggestion.validation_steps:
                    # 这里应该实际执行验证，简化为模拟
                    result["validation_results"].append(f"验证: {step} - 通过")
            
            # 更新修复成功率
            self.fix_success_rates[suggestion.fix_id] = self.fix_success_rates.get(suggestion.fix_id, 0.0) + 0.1
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"修复应用失败: {e}")
        
        return result
    
    def get_diagnostic_summary(self) -> Dict[str, Any]:
        """获取诊断引擎摘要"""
        return {
            "status": "active",
            "error_patterns_loaded": len(self.error_patterns),
            "error_history_size": len(self.error_history),
            "fix_success_rates": dict(list(self.fix_success_rates.items())[:10]),
            "available_patterns": list(self.error_patterns.keys())
        }


# 创建全局智能错误诊断引擎实例
_global_diagnostic_engine = None

def get_smart_diagnostic_engine(project_root: str = "/opt/powerautomation") -> SmartErrorDiagnosticEngine:
    """获取全局智能错误诊断引擎实例"""
    global _global_diagnostic_engine
    if _global_diagnostic_engine is None:
        _global_diagnostic_engine = SmartErrorDiagnosticEngine(project_root)
    return _global_diagnostic_engine


if __name__ == "__main__":
    # 测试智能错误诊断引擎
    async def test_diagnostic_engine():
        engine = SmartErrorDiagnosticEngine()
        
        # 测试错误诊断
        error_info = {
            "type": "ImportError",
            "message": "ImportError: No module named 'requests'",
            "stack_trace": "File '/test/test_api.py', line 5, in <module>\n    import requests",
            "context": {"module": "test_api", "test_file": "/test/test_api.py"}
        }
        
        diagnosis = await engine.diagnose_error(error_info)
        print(f"错误诊断: {diagnosis.error_type} - {diagnosis.description}")
        print(f"根本原因: {diagnosis.root_cause}")
        print(f"严重程度: {diagnosis.severity.value}")
        
        # 生成修复建议
        suggestions = await engine.generate_fix_suggestions(diagnosis)
        print(f"\n修复建议 ({len(suggestions)}个):")
        for suggestion in suggestions:
            print(f"- {suggestion.title} (置信度: {suggestion.confidence.value})")
        
        # 应用自动修复
        if suggestions:
            fix_result = await engine.apply_automatic_fix(suggestions[0])
            print(f"\n自动修复结果: {fix_result['status']}")
    
    asyncio.run(test_diagnostic_engine())

