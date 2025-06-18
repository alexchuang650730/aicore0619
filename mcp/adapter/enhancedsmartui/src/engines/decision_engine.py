#!/usr/bin/env python3
"""
SmartUI Enhanced - 智能决策引擎
基于多源数据做出界面调整决策，优化用户体验，自动化工作流程
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import math

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """决策类型"""
    UI_LAYOUT = "ui_layout"
    API_OPTIMIZATION = "api_optimization"
    WORKFLOW_AUTOMATION = "workflow_automation"
    PERFORMANCE_TUNING = "performance_tuning"
    USER_EXPERIENCE = "user_experience"

class DecisionPriority(Enum):
    """决策优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class DecisionContext:
    """决策上下文"""
    user_intent: str
    current_task: str
    available_mcps: List[str]
    system_load: float
    user_expertise: str
    time_constraints: Optional[int]
    environment_data: Dict[str, Any]
    user_preferences: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    
@dataclass
class Decision:
    """决策结果"""
    decision_id: str
    decision_type: DecisionType
    priority: DecisionPriority
    confidence: float
    actions: List[Dict[str, Any]]
    reasoning: str
    expected_impact: Dict[str, Any]
    execution_time: Optional[datetime] = None
    dependencies: List[str] = None
    rollback_plan: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, Callable] = {}
        self.rule_priorities: Dict[str, int] = {}
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认规则"""
        
        # UI布局规则
        self.register_rule("mobile_layout_optimization", self._mobile_layout_rule, priority=8)
        self.register_rule("high_load_simplification", self._high_load_rule, priority=9)
        self.register_rule("user_expertise_adaptation", self._expertise_rule, priority=7)
        self.register_rule("time_constraint_optimization", self._time_constraint_rule, priority=8)
        
        # 性能优化规则
        self.register_rule("api_caching_optimization", self._api_caching_rule, priority=6)
        self.register_rule("resource_load_balancing", self._load_balancing_rule, priority=7)
        self.register_rule("response_time_optimization", self._response_time_rule, priority=8)
        
        # 用户体验规则
        self.register_rule("personalization_enhancement", self._personalization_rule, priority=6)
        self.register_rule("accessibility_improvement", self._accessibility_rule, priority=7)
        self.register_rule("workflow_streamlining", self._workflow_rule, priority=5)
    
    def register_rule(self, rule_name: str, rule_func: Callable, priority: int = 5):
        """注册规则"""
        self.rules[rule_name] = rule_func
        self.rule_priorities[rule_name] = priority
        logger.info(f"注册规则: {rule_name} (优先级: {priority})")
    
    async def evaluate_rules(self, context: DecisionContext) -> List[Decision]:
        """评估所有规则"""
        decisions = []
        
        # 按优先级排序规则
        sorted_rules = sorted(
            self.rules.items(),
            key=lambda x: self.rule_priorities.get(x[0], 5),
            reverse=True
        )
        
        for rule_name, rule_func in sorted_rules:
            try:
                decision = await rule_func(context)
                if decision:
                    decisions.append(decision)
            except Exception as e:
                logger.error(f"规则评估失败 {rule_name}: {e}")
        
        return decisions
    
    async def _mobile_layout_rule(self, context: DecisionContext) -> Optional[Decision]:
        """移动端布局优化规则"""
        env_data = context.environment_data
        screen_width = env_data.get("screen_width", 1920)
        
        if screen_width <= 768:  # 移动端
            return Decision(
                decision_id=f"mobile_layout_{int(time.time())}",
                decision_type=DecisionType.UI_LAYOUT,
                priority=DecisionPriority.HIGH,
                confidence=0.9,
                actions=[
                    {
                        "type": "layout_change",
                        "target": "main_layout",
                        "changes": {
                            "layout_type": "mobile_stack",
                            "sidebar_collapsed": True,
                            "font_size_increase": 1.2
                        }
                    }
                ],
                reasoning="检测到移动端设备，应用移动端优化布局",
                expected_impact={
                    "user_experience": 0.8,
                    "performance": 0.6,
                    "accessibility": 0.7
                }
            )
        return None
    
    async def _high_load_rule(self, context: DecisionContext) -> Optional[Decision]:
        """高负载简化规则"""
        if context.system_load > 0.8:
            return Decision(
                decision_id=f"high_load_{int(time.time())}",
                decision_type=DecisionType.PERFORMANCE_TUNING,
                priority=DecisionPriority.CRITICAL,
                confidence=0.95,
                actions=[
                    {
                        "type": "ui_simplification",
                        "changes": {
                            "disable_animations": True,
                            "reduce_polling_frequency": True,
                            "lazy_load_components": True
                        }
                    },
                    {
                        "type": "api_optimization",
                        "changes": {
                            "enable_aggressive_caching": True,
                            "reduce_data_payload": True
                        }
                    }
                ],
                reasoning="系统负载过高，需要简化界面和优化性能",
                expected_impact={
                    "performance": 0.9,
                    "system_stability": 0.8,
                    "user_experience": -0.2  # 可能轻微影响用户体验
                }
            )
        return None
    
    async def _expertise_rule(self, context: DecisionContext) -> Optional[Decision]:
        """用户专业度适应规则"""
        expertise = context.user_expertise
        
        if expertise == "beginner":
            return Decision(
                decision_id=f"beginner_ui_{int(time.time())}",
                decision_type=DecisionType.USER_EXPERIENCE,
                priority=DecisionPriority.MEDIUM,
                confidence=0.8,
                actions=[
                    {
                        "type": "ui_enhancement",
                        "changes": {
                            "show_help_tooltips": True,
                            "enable_guided_tour": True,
                            "simplify_navigation": True,
                            "show_progress_indicators": True
                        }
                    }
                ],
                reasoning="检测到新手用户，启用辅助功能",
                expected_impact={
                    "user_experience": 0.9,
                    "learning_curve": 0.8,
                    "task_completion_rate": 0.7
                }
            )
        elif expertise == "expert":
            return Decision(
                decision_id=f"expert_ui_{int(time.time())}",
                decision_type=DecisionType.USER_EXPERIENCE,
                priority=DecisionPriority.MEDIUM,
                confidence=0.8,
                actions=[
                    {
                        "type": "ui_enhancement",
                        "changes": {
                            "show_advanced_options": True,
                            "enable_keyboard_shortcuts": True,
                            "compact_layout": True,
                            "show_detailed_metrics": True
                        }
                    }
                ],
                reasoning="检测到专家用户，启用高级功能",
                expected_impact={
                    "user_experience": 0.8,
                    "efficiency": 0.9,
                    "productivity": 0.8
                }
            )
        return None
    
    async def _time_constraint_rule(self, context: DecisionContext) -> Optional[Decision]:
        """时间约束优化规则"""
        if context.time_constraints and context.time_constraints < 300:  # 5分钟内
            return Decision(
                decision_id=f"time_constraint_{int(time.time())}",
                decision_type=DecisionType.WORKFLOW_AUTOMATION,
                priority=DecisionPriority.HIGH,
                confidence=0.85,
                actions=[
                    {
                        "type": "workflow_acceleration",
                        "changes": {
                            "auto_fill_forms": True,
                            "skip_confirmations": True,
                            "enable_batch_operations": True,
                            "prioritize_quick_actions": True
                        }
                    }
                ],
                reasoning="检测到时间约束，启用快速操作模式",
                expected_impact={
                    "task_completion_speed": 0.9,
                    "user_efficiency": 0.8,
                    "error_risk": 0.3  # 可能增加错误风险
                }
            )
        return None
    
    async def _api_caching_rule(self, context: DecisionContext) -> Optional[Decision]:
        """API缓存优化规则"""
        perf_metrics = context.performance_metrics
        avg_response_time = perf_metrics.get("avg_api_response_time", 0)
        
        if avg_response_time > 1000:  # 超过1秒
            return Decision(
                decision_id=f"api_caching_{int(time.time())}",
                decision_type=DecisionType.API_OPTIMIZATION,
                priority=DecisionPriority.HIGH,
                confidence=0.8,
                actions=[
                    {
                        "type": "enable_caching",
                        "targets": ["frequently_accessed_apis"],
                        "config": {
                            "cache_ttl": 300,  # 5分钟
                            "cache_strategy": "lru",
                            "max_cache_size": "100MB"
                        }
                    }
                ],
                reasoning="API响应时间过长，启用缓存优化",
                expected_impact={
                    "api_response_time": 0.7,
                    "user_experience": 0.6,
                    "system_load": -0.1
                }
            )
        return None
    
    async def _load_balancing_rule(self, context: DecisionContext) -> Optional[Decision]:
        """负载均衡规则"""
        available_mcps = context.available_mcps
        system_load = context.system_load
        
        if len(available_mcps) > 1 and system_load > 0.6:
            return Decision(
                decision_id=f"load_balancing_{int(time.time())}",
                decision_type=DecisionType.PERFORMANCE_TUNING,
                priority=DecisionPriority.HIGH,
                confidence=0.85,
                actions=[
                    {
                        "type": "enable_load_balancing",
                        "config": {
                            "strategy": "round_robin",
                            "health_check_interval": 30,
                            "failover_enabled": True
                        }
                    }
                ],
                reasoning="多个MCP可用且系统负载较高，启用负载均衡",
                expected_impact={
                    "system_stability": 0.8,
                    "response_time": 0.6,
                    "fault_tolerance": 0.9
                }
            )
        return None
    
    async def _response_time_rule(self, context: DecisionContext) -> Optional[Decision]:
        """响应时间优化规则"""
        perf_metrics = context.performance_metrics
        response_time = perf_metrics.get("avg_response_time", 0)
        
        if response_time > 2000:  # 超过2秒
            return Decision(
                decision_id=f"response_time_{int(time.time())}",
                decision_type=DecisionType.PERFORMANCE_TUNING,
                priority=DecisionPriority.HIGH,
                confidence=0.9,
                actions=[
                    {
                        "type": "response_optimization",
                        "changes": {
                            "enable_compression": True,
                            "optimize_database_queries": True,
                            "reduce_payload_size": True,
                            "enable_cdn": True
                        }
                    }
                ],
                reasoning="响应时间过长，需要优化性能",
                expected_impact={
                    "response_time": 0.8,
                    "user_satisfaction": 0.7,
                    "bounce_rate": -0.3
                }
            )
        return None
    
    async def _personalization_rule(self, context: DecisionContext) -> Optional[Decision]:
        """个性化增强规则"""
        user_prefs = context.user_preferences
        
        if user_prefs and len(user_prefs) > 3:  # 有足够的偏好数据
            return Decision(
                decision_id=f"personalization_{int(time.time())}",
                decision_type=DecisionType.USER_EXPERIENCE,
                priority=DecisionPriority.MEDIUM,
                confidence=0.7,
                actions=[
                    {
                        "type": "apply_personalization",
                        "changes": {
                            "customize_dashboard": True,
                            "personalized_recommendations": True,
                            "adaptive_navigation": True
                        }
                    }
                ],
                reasoning="用户有足够的偏好数据，应用个性化设置",
                expected_impact={
                    "user_engagement": 0.8,
                    "user_satisfaction": 0.7,
                    "retention_rate": 0.6
                }
            )
        return None
    
    async def _accessibility_rule(self, context: DecisionContext) -> Optional[Decision]:
        """可访问性改进规则"""
        env_data = context.environment_data
        
        # 检查是否需要可访问性增强
        needs_accessibility = (
            env_data.get("high_contrast_mode", False) or
            env_data.get("screen_reader_detected", False) or
            env_data.get("keyboard_navigation_only", False)
        )
        
        if needs_accessibility:
            return Decision(
                decision_id=f"accessibility_{int(time.time())}",
                decision_type=DecisionType.USER_EXPERIENCE,
                priority=DecisionPriority.HIGH,
                confidence=0.9,
                actions=[
                    {
                        "type": "accessibility_enhancement",
                        "changes": {
                            "high_contrast_theme": True,
                            "large_font_sizes": True,
                            "keyboard_navigation_hints": True,
                            "screen_reader_optimization": True,
                            "focus_indicators": True
                        }
                    }
                ],
                reasoning="检测到可访问性需求，启用辅助功能",
                expected_impact={
                    "accessibility": 0.9,
                    "inclusivity": 0.8,
                    "user_experience": 0.7
                }
            )
        return None
    
    async def _workflow_rule(self, context: DecisionContext) -> Optional[Decision]:
        """工作流优化规则"""
        current_task = context.current_task
        user_intent = context.user_intent
        
        # 检查是否可以自动化工作流
        if current_task and user_intent in ["create", "edit", "analyze"]:
            return Decision(
                decision_id=f"workflow_{int(time.time())}",
                decision_type=DecisionType.WORKFLOW_AUTOMATION,
                priority=DecisionPriority.MEDIUM,
                confidence=0.6,
                actions=[
                    {
                        "type": "workflow_optimization",
                        "changes": {
                            "suggest_next_steps": True,
                            "auto_save_progress": True,
                            "smart_form_completion": True,
                            "contextual_tools": True
                        }
                    }
                ],
                reasoning="检测到可优化的工作流，启用智能辅助",
                expected_impact={
                    "workflow_efficiency": 0.7,
                    "task_completion_rate": 0.6,
                    "user_productivity": 0.8
                }
            )
        return None

class MLPredictor:
    """机器学习预测器"""
    
    def __init__(self):
        self.models = {}
        self.training_data = []
        self.prediction_cache = {}
    
    async def predict(self, context: DecisionContext) -> Dict[str, Any]:
        """基于机器学习模型进行预测"""
        try:
            # 简化的预测逻辑（实际应用中会使用真实的ML模型）
            features = self._extract_features(context)
            
            predictions = {
                "user_satisfaction_score": self._predict_satisfaction(features),
                "task_completion_probability": self._predict_completion(features),
                "optimal_ui_layout": self._predict_layout(features),
                "performance_bottlenecks": self._predict_bottlenecks(features)
            }
            
            return predictions
            
        except Exception as e:
            logger.error(f"ML预测失败: {e}")
            return {}
    
    def _extract_features(self, context: DecisionContext) -> Dict[str, float]:
        """提取特征向量"""
        features = {
            "system_load": context.system_load,
            "user_expertise_score": self._encode_expertise(context.user_expertise),
            "time_pressure": 1.0 if context.time_constraints and context.time_constraints < 600 else 0.0,
            "mcp_availability": len(context.available_mcps) / 10.0,  # 归一化
            "preference_completeness": len(context.user_preferences) / 10.0
        }
        
        # 添加性能指标特征
        perf_metrics = context.performance_metrics
        features.update({
            "avg_response_time_norm": min(perf_metrics.get("avg_response_time", 0) / 5000.0, 1.0),
            "error_rate": perf_metrics.get("error_rate", 0) / 100.0,
            "throughput_norm": min(perf_metrics.get("throughput", 0) / 1000.0, 1.0)
        })
        
        return features
    
    def _encode_expertise(self, expertise: str) -> float:
        """编码用户专业度"""
        expertise_map = {
            "beginner": 0.0,
            "intermediate": 0.5,
            "expert": 1.0
        }
        return expertise_map.get(expertise, 0.5)
    
    def _predict_satisfaction(self, features: Dict[str, float]) -> float:
        """预测用户满意度"""
        # 简化的线性模型
        weights = {
            "system_load": -0.3,
            "user_expertise_score": 0.2,
            "time_pressure": -0.2,
            "avg_response_time_norm": -0.4,
            "error_rate": -0.5
        }
        
        score = 0.7  # 基础分数
        for feature, value in features.items():
            if feature in weights:
                score += weights[feature] * value
        
        return max(0.0, min(1.0, score))
    
    def _predict_completion(self, features: Dict[str, float]) -> float:
        """预测任务完成概率"""
        # 基于特征的简单预测
        completion_prob = 0.8  # 基础概率
        
        if features.get("time_pressure", 0) > 0.5:
            completion_prob -= 0.2
        
        if features.get("system_load", 0) > 0.8:
            completion_prob -= 0.3
        
        if features.get("user_expertise_score", 0) > 0.7:
            completion_prob += 0.1
        
        return max(0.0, min(1.0, completion_prob))
    
    def _predict_layout(self, features: Dict[str, float]) -> str:
        """预测最优UI布局"""
        if features.get("user_expertise_score", 0) > 0.7:
            return "compact"
        elif features.get("time_pressure", 0) > 0.5:
            return "simplified"
        else:
            return "standard"
    
    def _predict_bottlenecks(self, features: Dict[str, float]) -> List[str]:
        """预测性能瓶颈"""
        bottlenecks = []
        
        if features.get("avg_response_time_norm", 0) > 0.6:
            bottlenecks.append("api_response_time")
        
        if features.get("system_load", 0) > 0.8:
            bottlenecks.append("system_resources")
        
        if features.get("error_rate", 0) > 0.05:
            bottlenecks.append("error_handling")
        
        return bottlenecks

class DecisionEngine:
    """智能决策引擎 - 主类"""
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.ml_predictor = MLPredictor()
        self.decision_history: List[Decision] = []
        self.execution_results: Dict[str, Dict[str, Any]] = {}
        self.learning_enabled = True
    
    async def make_decision(self, context: DecisionContext) -> Dict[str, Any]:
        """基于上下文做出智能决策"""
        try:
            start_time = time.time()
            
            # 1. 规则引擎决策
            rule_decisions = await self.rule_engine.evaluate_rules(context)
            
            # 2. 机器学习预测
            ml_predictions = await self.ml_predictor.predict(context)
            
            # 3. 综合决策
            final_decisions = await self._combine_decisions(rule_decisions, ml_predictions, context)
            
            # 4. 决策优化
            optimized_decisions = await self._optimize_decisions(final_decisions, context)
            
            # 5. 生成执行计划
            execution_plan = await self._generate_execution_plan(optimized_decisions)
            
            # 6. 记录决策历史
            for decision in optimized_decisions:
                self.decision_history.append(decision)
            
            processing_time = time.time() - start_time
            
            return {
                "decisions": [asdict(d) for d in optimized_decisions],
                "ml_predictions": ml_predictions,
                "execution_plan": execution_plan,
                "processing_time": processing_time,
                "context_summary": self._summarize_context(context),
                "confidence_score": self._calculate_overall_confidence(optimized_decisions)
            }
            
        except Exception as e:
            logger.error(f"决策制定失败: {e}")
            return {
                "error": str(e),
                "decisions": [],
                "processing_time": 0
            }
    
    async def _combine_decisions(self, rule_decisions: List[Decision], 
                                ml_predictions: Dict[str, Any],
                                context: DecisionContext) -> List[Decision]:
        """综合规则决策和ML预测"""
        combined_decisions = []
        
        # 基于ML预测调整规则决策的置信度
        for decision in rule_decisions:
            adjusted_decision = decision
            
            # 根据用户满意度预测调整置信度
            satisfaction_score = ml_predictions.get("user_satisfaction_score", 0.5)
            if satisfaction_score < 0.3:
                adjusted_decision.confidence *= 0.8  # 降低置信度
            elif satisfaction_score > 0.8:
                adjusted_decision.confidence *= 1.1  # 提高置信度
            
            # 根据任务完成概率调整优先级
            completion_prob = ml_predictions.get("task_completion_probability", 0.5)
            if completion_prob < 0.3 and decision.decision_type == DecisionType.WORKFLOW_AUTOMATION:
                if decision.priority == DecisionPriority.MEDIUM:
                    adjusted_decision.priority = DecisionPriority.HIGH
            
            combined_decisions.append(adjusted_decision)
        
        # 基于ML预测生成额外决策
        ml_decisions = await self._generate_ml_based_decisions(ml_predictions, context)
        combined_decisions.extend(ml_decisions)
        
        return combined_decisions
    
    async def _generate_ml_based_decisions(self, ml_predictions: Dict[str, Any],
                                         context: DecisionContext) -> List[Decision]:
        """基于ML预测生成决策"""
        ml_decisions = []
        
        # 基于预测的UI布局决策
        optimal_layout = ml_predictions.get("optimal_ui_layout", "standard")
        if optimal_layout != "standard":
            ml_decisions.append(Decision(
                decision_id=f"ml_layout_{int(time.time())}",
                decision_type=DecisionType.UI_LAYOUT,
                priority=DecisionPriority.MEDIUM,
                confidence=0.7,
                actions=[
                    {
                        "type": "layout_optimization",
                        "changes": {"layout_style": optimal_layout}
                    }
                ],
                reasoning=f"ML预测最优布局为: {optimal_layout}",
                expected_impact={"user_experience": 0.6}
            ))
        
        # 基于预测的性能瓶颈决策
        bottlenecks = ml_predictions.get("performance_bottlenecks", [])
        for bottleneck in bottlenecks:
            if bottleneck == "api_response_time":
                ml_decisions.append(Decision(
                    decision_id=f"ml_api_opt_{int(time.time())}",
                    decision_type=DecisionType.API_OPTIMIZATION,
                    priority=DecisionPriority.HIGH,
                    confidence=0.8,
                    actions=[
                        {
                            "type": "api_optimization",
                            "changes": {"enable_response_caching": True}
                        }
                    ],
                    reasoning="ML预测API响应时间瓶颈",
                    expected_impact={"performance": 0.7}
                ))
        
        return ml_decisions
    
    async def _optimize_decisions(self, decisions: List[Decision],
                                context: DecisionContext) -> List[Decision]:
        """优化决策列表"""
        if not decisions:
            return decisions
        
        # 1. 去重相似决策
        unique_decisions = self._deduplicate_decisions(decisions)
        
        # 2. 解决决策冲突
        conflict_resolved = await self._resolve_conflicts(unique_decisions)
        
        # 3. 按优先级和置信度排序
        sorted_decisions = sorted(
            conflict_resolved,
            key=lambda d: (d.priority.value, d.confidence),
            reverse=True
        )
        
        # 4. 限制决策数量（避免过度优化）
        max_decisions = 5
        optimized_decisions = sorted_decisions[:max_decisions]
        
        return optimized_decisions
    
    def _deduplicate_decisions(self, decisions: List[Decision]) -> List[Decision]:
        """去重相似决策"""
        unique_decisions = []
        seen_types = set()
        
        for decision in decisions:
            decision_key = f"{decision.decision_type.value}_{decision.actions[0].get('type', '')}"
            
            if decision_key not in seen_types:
                unique_decisions.append(decision)
                seen_types.add(decision_key)
            else:
                # 如果类型相同，保留置信度更高的
                for i, existing in enumerate(unique_decisions):
                    existing_key = f"{existing.decision_type.value}_{existing.actions[0].get('type', '')}"
                    if existing_key == decision_key and decision.confidence > existing.confidence:
                        unique_decisions[i] = decision
                        break
        
        return unique_decisions
    
    async def _resolve_conflicts(self, decisions: List[Decision]) -> List[Decision]:
        """解决决策冲突"""
        # 简化的冲突解决逻辑
        resolved_decisions = []
        
        # 检查UI相关决策冲突
        ui_decisions = [d for d in decisions if d.decision_type == DecisionType.UI_LAYOUT]
        if len(ui_decisions) > 1:
            # 保留置信度最高的UI决策
            best_ui_decision = max(ui_decisions, key=lambda d: d.confidence)
            resolved_decisions.append(best_ui_decision)
            
            # 添加非UI决策
            resolved_decisions.extend([d for d in decisions if d.decision_type != DecisionType.UI_LAYOUT])
        else:
            resolved_decisions = decisions
        
        return resolved_decisions
    
    async def _generate_execution_plan(self, decisions: List[Decision]) -> Dict[str, Any]:
        """生成执行计划"""
        execution_plan = {
            "total_decisions": len(decisions),
            "execution_order": [],
            "estimated_duration": 0,
            "dependencies": {},
            "rollback_strategy": {}
        }
        
        # 按优先级和依赖关系排序
        sorted_decisions = self._sort_by_dependencies(decisions)
        
        for i, decision in enumerate(sorted_decisions):
            execution_step = {
                "step": i + 1,
                "decision_id": decision.decision_id,
                "decision_type": decision.decision_type.value,
                "estimated_time": self._estimate_execution_time(decision),
                "prerequisites": decision.dependencies
            }
            
            execution_plan["execution_order"].append(execution_step)
            execution_plan["estimated_duration"] += execution_step["estimated_time"]
            
            # 记录依赖关系
            if decision.dependencies:
                execution_plan["dependencies"][decision.decision_id] = decision.dependencies
            
            # 记录回滚策略
            if decision.rollback_plan:
                execution_plan["rollback_strategy"][decision.decision_id] = decision.rollback_plan
        
        return execution_plan
    
    def _sort_by_dependencies(self, decisions: List[Decision]) -> List[Decision]:
        """按依赖关系排序决策"""
        # 简化的拓扑排序
        sorted_decisions = []
        remaining_decisions = decisions.copy()
        
        while remaining_decisions:
            # 找到没有未满足依赖的决策
            ready_decisions = []
            for decision in remaining_decisions:
                if not decision.dependencies or all(
                    dep_id in [d.decision_id for d in sorted_decisions]
                    for dep_id in decision.dependencies
                ):
                    ready_decisions.append(decision)
            
            if not ready_decisions:
                # 如果有循环依赖，按优先级排序
                ready_decisions = sorted(
                    remaining_decisions,
                    key=lambda d: d.priority.value,
                    reverse=True
                )[:1]
            
            # 添加到已排序列表
            for decision in ready_decisions:
                sorted_decisions.append(decision)
                remaining_decisions.remove(decision)
        
        return sorted_decisions
    
    def _estimate_execution_time(self, decision: Decision) -> int:
        """估算决策执行时间（秒）"""
        time_estimates = {
            DecisionType.UI_LAYOUT: 2,
            DecisionType.API_OPTIMIZATION: 5,
            DecisionType.WORKFLOW_AUTOMATION: 3,
            DecisionType.PERFORMANCE_TUNING: 10,
            DecisionType.USER_EXPERIENCE: 1
        }
        
        base_time = time_estimates.get(decision.decision_type, 5)
        
        # 根据行动数量调整时间
        action_count = len(decision.actions)
        return base_time * action_count
    
    def _summarize_context(self, context: DecisionContext) -> Dict[str, Any]:
        """总结决策上下文"""
        return {
            "user_intent": context.user_intent,
            "current_task": context.current_task,
            "system_load": context.system_load,
            "user_expertise": context.user_expertise,
            "available_mcps_count": len(context.available_mcps),
            "has_time_constraints": context.time_constraints is not None,
            "preference_count": len(context.user_preferences)
        }
    
    def _calculate_overall_confidence(self, decisions: List[Decision]) -> float:
        """计算整体置信度"""
        if not decisions:
            return 0.0
        
        # 加权平均置信度
        total_weight = 0
        weighted_confidence = 0
        
        for decision in decisions:
            weight = self._get_decision_weight(decision)
            weighted_confidence += decision.confidence * weight
            total_weight += weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _get_decision_weight(self, decision: Decision) -> float:
        """获取决策权重"""
        priority_weights = {
            DecisionPriority.CRITICAL: 1.0,
            DecisionPriority.HIGH: 0.8,
            DecisionPriority.MEDIUM: 0.6,
            DecisionPriority.LOW: 0.4
        }
        
        return priority_weights.get(decision.priority, 0.5)
    
    async def execute_decisions(self, decisions: List[Decision]) -> Dict[str, Any]:
        """执行决策（模拟）"""
        execution_results = {
            "executed_decisions": [],
            "failed_decisions": [],
            "total_execution_time": 0,
            "overall_success": True
        }
        
        start_time = time.time()
        
        for decision in decisions:
            try:
                # 模拟执行决策
                await asyncio.sleep(0.1)  # 模拟执行时间
                
                execution_result = {
                    "decision_id": decision.decision_id,
                    "status": "success",
                    "execution_time": 0.1,
                    "impact_achieved": decision.expected_impact
                }
                
                execution_results["executed_decisions"].append(execution_result)
                
                # 记录执行结果用于学习
                self.execution_results[decision.decision_id] = execution_result
                
            except Exception as e:
                execution_result = {
                    "decision_id": decision.decision_id,
                    "status": "failed",
                    "error": str(e)
                }
                
                execution_results["failed_decisions"].append(execution_result)
                execution_results["overall_success"] = False
        
        execution_results["total_execution_time"] = time.time() - start_time
        
        return execution_results
    
    def get_decision_analytics(self) -> Dict[str, Any]:
        """获取决策分析"""
        if not self.decision_history:
            return {"total_decisions": 0}
        
        # 统计决策类型分布
        type_counts = {}
        for decision in self.decision_history:
            decision_type = decision.decision_type.value
            type_counts[decision_type] = type_counts.get(decision_type, 0) + 1
        
        # 统计优先级分布
        priority_counts = {}
        for decision in self.decision_history:
            priority = decision.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # 计算平均置信度
        avg_confidence = sum(d.confidence for d in self.decision_history) / len(self.decision_history)
        
        # 统计执行成功率
        executed_count = len(self.execution_results)
        success_count = sum(1 for r in self.execution_results.values() if r.get("status") == "success")
        success_rate = success_count / executed_count if executed_count > 0 else 0
        
        return {
            "total_decisions": len(self.decision_history),
            "decision_type_distribution": type_counts,
            "priority_distribution": priority_counts,
            "average_confidence": avg_confidence,
            "execution_success_rate": success_rate,
            "recent_decisions": [
                {
                    "decision_id": d.decision_id,
                    "type": d.decision_type.value,
                    "confidence": d.confidence,
                    "reasoning": d.reasoning
                }
                for d in self.decision_history[-5:]
            ]
        }

if __name__ == "__main__":
    # 测试代码
    async def test_decision_engine():
        engine = DecisionEngine()
        
        # 创建测试上下文
        test_context = DecisionContext(
            user_intent="search",
            current_task="data_analysis",
            available_mcps=["mcp1", "mcp2", "mcp3"],
            system_load=0.7,
            user_expertise="intermediate",
            time_constraints=300,
            environment_data={
                "screen_width": 1920,
                "screen_height": 1080
            },
            user_preferences={
                "theme": "dark",
                "layout": "compact"
            },
            performance_metrics={
                "avg_response_time": 1500,
                "error_rate": 2.5,
                "throughput": 500
            }
        )
        
        # 执行决策
        result = await engine.make_decision(test_context)
        print(f"决策结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 获取分析报告
        analytics = engine.get_decision_analytics()
        print(f"决策分析: {json.dumps(analytics, indent=2, ensure_ascii=False)}")
    
    # 运行测试
    asyncio.run(test_decision_engine())

