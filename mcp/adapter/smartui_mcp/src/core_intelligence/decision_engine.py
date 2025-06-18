"""
SmartUI MCP - 智能决策引擎

实现基于规则、机器学习和启发式算法的智能决策系统，
为SmartUI提供自适应和个性化的用户界面决策能力。
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, deque
import heapq

from ..common import (
    IDecisionEngine, EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    UIConfiguration, UIComponent, ComponentType
)


class DecisionType(str, Enum):
    """决策类型枚举"""
    UI_ADAPTATION = "ui_adaptation"
    LAYOUT_OPTIMIZATION = "layout_optimization"
    COMPONENT_SELECTION = "component_selection"
    THEME_ADJUSTMENT = "theme_adjustment"
    INTERACTION_ENHANCEMENT = "interaction_enhancement"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ACCESSIBILITY_IMPROVEMENT = "accessibility_improvement"
    PERSONALIZATION = "personalization"
    ERROR_RECOVERY = "error_recovery"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"


class DecisionPriority(str, Enum):
    """决策优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DecisionStrategy(str, Enum):
    """决策策略枚举"""
    RULE_BASED = "rule_based"
    ML_BASED = "ml_based"
    HEURISTIC = "heuristic"
    HYBRID = "hybrid"
    USER_PREFERENCE = "user_preference"
    A_B_TEST = "a_b_test"
    CONSENSUS = "consensus"


@dataclass
class DecisionContext:
    """决策上下文"""
    context_id: str
    user_id: Optional[str]
    session_id: str
    current_ui_state: Dict[str, Any]
    user_profile: Dict[str, Any]
    interaction_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    constraints: Dict[str, Any]
    goals: List[str]
    timestamp: datetime
    
    def __post_init__(self):
        if self.context_id is None:
            self.context_id = generate_id("context_")


@dataclass
class DecisionRule:
    """决策规则"""
    rule_id: str
    name: str
    description: str
    condition: str  # 条件表达式
    action: str     # 动作表达式
    priority: int
    weight: float
    enabled: bool = True
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.rule_id is None:
            self.rule_id = generate_id("rule_")
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DecisionOption:
    """决策选项"""
    option_id: str
    name: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    confidence: float
    cost: float
    risk: float
    benefits: List[str]
    drawbacks: List[str]
    
    def __post_init__(self):
        if self.option_id is None:
            self.option_id = generate_id("option_")


@dataclass
class DecisionResult:
    """决策结果"""
    decision_id: str
    decision_type: DecisionType
    selected_option: DecisionOption
    alternative_options: List[DecisionOption]
    reasoning: str
    confidence: float
    strategy_used: DecisionStrategy
    execution_plan: Dict[str, Any]
    success_metrics: Dict[str, Any]
    rollback_plan: Optional[Dict[str, Any]]
    timestamp: datetime
    
    def __post_init__(self):
        if self.decision_id is None:
            self.decision_id = generate_id("decision_")


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, DecisionRule] = {}
        self.rule_groups: Dict[str, List[str]] = defaultdict(list)
        self.execution_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "executions": 0,
            "successes": 0,
            "failures": 0,
            "avg_execution_time": 0.0
        })
    
    def add_rule(self, rule: DecisionRule, group: Optional[str] = None) -> None:
        """添加规则"""
        self.rules[rule.rule_id] = rule
        
        if group:
            self.rule_groups[group].append(rule.rule_id)
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            
            # 从所有组中移除
            for group_rules in self.rule_groups.values():
                if rule_id in group_rules:
                    group_rules.remove(rule_id)
            
            return True
        return False
    
    def evaluate_rules(
        self,
        context: DecisionContext,
        rule_group: Optional[str] = None
    ) -> List[Tuple[DecisionRule, bool, Any]]:
        """评估规则"""
        results = []
        
        # 确定要评估的规则
        if rule_group and rule_group in self.rule_groups:
            rule_ids = self.rule_groups[rule_group]
        else:
            rule_ids = list(self.rules.keys())
        
        # 按优先级排序
        sorted_rules = sorted(
            [self.rules[rid] for rid in rule_ids if rid in self.rules],
            key=lambda r: r.priority,
            reverse=True
        )
        
        # 评估每个规则
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            start_time = time.time()
            try:
                # 评估条件
                condition_result = self._evaluate_condition(rule.condition, context)
                
                # 如果条件满足，执行动作
                action_result = None
                if condition_result:
                    action_result = self._evaluate_action(rule.action, context)
                
                results.append((rule, condition_result, action_result))
                
                # 更新统计
                execution_time = time.time() - start_time
                stats = self.execution_stats[rule.rule_id]
                stats["executions"] += 1
                if condition_result:
                    stats["successes"] += 1
                
                # 更新平均执行时间
                total_time = stats["avg_execution_time"] * (stats["executions"] - 1) + execution_time
                stats["avg_execution_time"] = total_time / stats["executions"]
                
            except Exception as e:
                logging.error(f"Error evaluating rule {rule.rule_id}: {e}")
                self.execution_stats[rule.rule_id]["failures"] += 1
                results.append((rule, False, None))
        
        return results
    
    def _evaluate_condition(self, condition: str, context: DecisionContext) -> bool:
        """评估条件表达式"""
        try:
            # 构建安全的评估环境
            safe_dict = {
                "context": context,
                "user_profile": context.user_profile,
                "ui_state": context.current_ui_state,
                "performance": context.performance_metrics,
                "len": len,
                "sum": sum,
                "max": max,
                "min": min,
                "abs": abs,
                "round": round,
                "datetime": datetime,
                "timedelta": timedelta,
            }
            
            # 执行条件表达式
            result = eval(condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
            
        except Exception as e:
            logging.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def _evaluate_action(self, action: str, context: DecisionContext) -> Any:
        """评估动作表达式"""
        try:
            # 构建安全的评估环境
            safe_dict = {
                "context": context,
                "user_profile": context.user_profile,
                "ui_state": context.current_ui_state,
                "performance": context.performance_metrics,
                "generate_id": generate_id,
                "datetime": datetime,
            }
            
            # 执行动作表达式
            result = eval(action, {"__builtins__": {}}, safe_dict)
            return result
            
        except Exception as e:
            logging.error(f"Error evaluating action '{action}': {e}")
            return None
    
    def get_rule_statistics(self) -> Dict[str, Dict[str, Any]]:
        """获取规则统计信息"""
        return dict(self.execution_stats)


class MLDecisionModel:
    """机器学习决策模型"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.training_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.feature_extractors: Dict[str, Callable] = {}
        self.model_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    def register_model(
        self,
        model_name: str,
        model: Any,
        feature_extractor: Callable[[DecisionContext], np.ndarray]
    ) -> None:
        """注册模型"""
        self.models[model_name] = model
        self.feature_extractors[model_name] = feature_extractor
    
    def predict(
        self,
        model_name: str,
        context: DecisionContext
    ) -> Optional[Tuple[Any, float]]:
        """使用模型进行预测"""
        if model_name not in self.models:
            return None
        
        try:
            # 提取特征
            features = self.feature_extractors[model_name](context)
            
            # 进行预测
            model = self.models[model_name]
            
            if hasattr(model, 'predict_proba'):
                # 分类模型
                prediction = model.predict(features.reshape(1, -1))[0]
                probabilities = model.predict_proba(features.reshape(1, -1))[0]
                confidence = max(probabilities)
            else:
                # 回归模型
                prediction = model.predict(features.reshape(1, -1))[0]
                confidence = 0.8  # 默认置信度
            
            return prediction, confidence
            
        except Exception as e:
            logging.error(f"Error in ML prediction for model {model_name}: {e}")
            return None
    
    def add_training_data(
        self,
        model_name: str,
        context: DecisionContext,
        decision_result: DecisionResult,
        outcome: Dict[str, Any]
    ) -> None:
        """添加训练数据"""
        training_sample = {
            "context": asdict(context),
            "decision": asdict(decision_result),
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        }
        
        self.training_data[model_name].append(training_sample)
    
    def retrain_model(self, model_name: str) -> bool:
        """重新训练模型"""
        if model_name not in self.training_data or not self.training_data[model_name]:
            return False
        
        try:
            # 这里应该实现具体的模型训练逻辑
            # 由于这是一个框架，我们只是记录训练请求
            logging.info(f"Retraining model {model_name} with {len(self.training_data[model_name])} samples")
            return True
            
        except Exception as e:
            logging.error(f"Error retraining model {model_name}: {e}")
            return False


class HeuristicEngine:
    """启发式引擎"""
    
    def __init__(self):
        self.heuristics: Dict[str, Callable] = {}
        self.heuristic_weights: Dict[str, float] = {}
    
    def register_heuristic(
        self,
        name: str,
        heuristic_func: Callable[[DecisionContext], float],
        weight: float = 1.0
    ) -> None:
        """注册启发式函数"""
        self.heuristics[name] = heuristic_func
        self.heuristic_weights[name] = weight
    
    def evaluate_heuristics(self, context: DecisionContext) -> Dict[str, float]:
        """评估所有启发式函数"""
        results = {}
        
        for name, heuristic_func in self.heuristics.items():
            try:
                score = heuristic_func(context)
                weighted_score = score * self.heuristic_weights[name]
                results[name] = weighted_score
            except Exception as e:
                logging.error(f"Error evaluating heuristic {name}: {e}")
                results[name] = 0.0
        
        return results
    
    def get_combined_score(self, context: DecisionContext) -> float:
        """获取组合启发式分数"""
        scores = self.evaluate_heuristics(context)
        
        if not scores:
            return 0.0
        
        # 加权平均
        total_weight = sum(self.heuristic_weights.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(scores.values())
        return weighted_sum / total_weight


class DecisionOptimizer:
    """决策优化器"""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        self.performance_cache = AsyncCache(max_size=100, ttl=3600)
    
    async def optimize_decision(
        self,
        options: List[DecisionOption],
        context: DecisionContext,
        optimization_criteria: Dict[str, float]
    ) -> DecisionOption:
        """优化决策选择"""
        if not options:
            raise ValueError("No decision options provided")
        
        if len(options) == 1:
            return options[0]
        
        # 计算每个选项的综合分数
        scored_options = []
        
        for option in options:
            score = await self._calculate_option_score(option, context, optimization_criteria)
            scored_options.append((option, score))
        
        # 按分数排序
        scored_options.sort(key=lambda x: x[1], reverse=True)
        
        # 记录优化历史
        self.optimization_history.append({
            "context_id": context.context_id,
            "options_count": len(options),
            "selected_option": scored_options[0][0].option_id,
            "optimization_criteria": optimization_criteria,
            "timestamp": datetime.now().isoformat()
        })
        
        return scored_options[0][0]
    
    async def _calculate_option_score(
        self,
        option: DecisionOption,
        context: DecisionContext,
        criteria: Dict[str, float]
    ) -> float:
        """计算选项分数"""
        cache_key = f"option_score_{option.option_id}_{context.context_id}"
        
        # 尝试从缓存获取
        cached_score = await self.performance_cache.get(cache_key)
        if cached_score is not None:
            return cached_score
        
        score = 0.0
        
        # 基础分数：置信度
        score += option.confidence * criteria.get("confidence_weight", 0.3)
        
        # 成本因子（成本越低分数越高）
        cost_factor = 1.0 / (1.0 + option.cost)
        score += cost_factor * criteria.get("cost_weight", 0.2)
        
        # 风险因子（风险越低分数越高）
        risk_factor = 1.0 / (1.0 + option.risk)
        score += risk_factor * criteria.get("risk_weight", 0.2)
        
        # 收益因子
        benefit_score = len(option.benefits) * 0.1
        score += benefit_score * criteria.get("benefit_weight", 0.15)
        
        # 用户偏好匹配
        preference_score = self._calculate_preference_match(option, context)
        score += preference_score * criteria.get("preference_weight", 0.15)
        
        # 缓存结果
        await self.performance_cache.set(cache_key, score)
        
        return score
    
    def _calculate_preference_match(
        self,
        option: DecisionOption,
        context: DecisionContext
    ) -> float:
        """计算选项与用户偏好的匹配度"""
        user_preferences = context.user_profile.get("preferences", {})
        
        if not user_preferences:
            return 0.5  # 中性分数
        
        match_score = 0.0
        total_preferences = 0
        
        # 检查选项参数与用户偏好的匹配
        for pref_key, pref_value in user_preferences.items():
            if pref_key in option.parameters:
                total_preferences += 1
                option_value = option.parameters[pref_key]
                
                # 简单的匹配逻辑
                if option_value == pref_value:
                    match_score += 1.0
                elif isinstance(option_value, (int, float)) and isinstance(pref_value, (int, float)):
                    # 数值类型的相似度
                    similarity = 1.0 - abs(option_value - pref_value) / max(abs(option_value), abs(pref_value), 1.0)
                    match_score += max(0.0, similarity)
        
        return match_score / max(total_preferences, 1)


class SmartUIDecisionEngine(IDecisionEngine):
    """SmartUI智能决策引擎实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 初始化子组件
        self.rule_engine = RuleEngine()
        self.ml_model = MLDecisionModel()
        self.heuristic_engine = HeuristicEngine()
        self.optimizer = DecisionOptimizer()
        
        # 决策历史
        self.decision_history: deque = deque(maxlen=10000)
        
        # 性能监控
        self.performance_metrics: Dict[str, float] = defaultdict(float)
        
        # 缓存
        self.decision_cache = AsyncCache(max_size=500, ttl=300)  # 5分钟缓存
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        # 初始化默认规则和启发式函数
        self._initialize_default_rules()
        self._initialize_default_heuristics()
        
        self.logger.info("SmartUI Decision Engine initialized")
    
    @log_execution_time()
    async def make_decision(
        self,
        decision_type: str,
        context: Dict[str, Any],
        options: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """做出决策"""
        try:
            # 解析决策上下文
            decision_context = self._parse_decision_context(context)
            
            # 生成决策选项（如果未提供）
            if not options:
                options = await self._generate_decision_options(decision_type, decision_context)
            
            # 转换为DecisionOption对象
            decision_options = [self._parse_decision_option(opt) for opt in options]
            
            # 选择决策策略
            strategy = self._select_decision_strategy(decision_type, decision_context)
            
            # 执行决策
            decision_result = await self._execute_decision(
                decision_type, decision_context, decision_options, strategy
            )
            
            # 记录决策历史
            self.decision_history.append(decision_result)
            
            # 发布决策事件
            await publish_event(
                event_type=EventBusEventType.DECISION_MADE,
                data={
                    "decision_id": decision_result.decision_id,
                    "decision_type": decision_type,
                    "selected_option": asdict(decision_result.selected_option),
                    "confidence": decision_result.confidence,
                    "strategy": decision_result.strategy_used.value
                },
                source="decision_engine"
            )
            
            return {
                "success": True,
                "decision": asdict(decision_result),
                "execution_plan": decision_result.execution_plan,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error making decision: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """评估规则"""
        try:
            decision_context = self._parse_decision_context(context)
            
            # 评估所有规则
            rule_results = self.rule_engine.evaluate_rules(decision_context)
            
            # 转换为字典格式
            results = []
            for rule, condition_result, action_result in rule_results:
                results.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "condition_met": condition_result,
                    "action_result": action_result,
                    "priority": rule.priority,
                    "weight": rule.weight
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating rules: {e}")
            return []
    
    async def add_decision_rule(self, rule_data: Dict[str, Any]) -> bool:
        """添加决策规则"""
        try:
            rule = DecisionRule(
                rule_id=rule_data.get("rule_id"),
                name=rule_data["name"],
                description=rule_data.get("description", ""),
                condition=rule_data["condition"],
                action=rule_data["action"],
                priority=rule_data.get("priority", 0),
                weight=rule_data.get("weight", 1.0),
                enabled=rule_data.get("enabled", True),
                tags=rule_data.get("tags", []),
                metadata=rule_data.get("metadata", {})
            )
            
            group = rule_data.get("group")
            self.rule_engine.add_rule(rule, group)
            
            self.logger.info(f"Added decision rule: {rule.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding decision rule: {e}")
            return False
    
    async def update_decision_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新决策规则"""
        try:
            if rule_id not in self.rule_engine.rules:
                return False
            
            rule = self.rule_engine.rules[rule_id]
            
            # 更新规则属性
            for field, value in updates.items():
                if hasattr(rule, field):
                    setattr(rule, field, value)
            
            self.logger.info(f"Updated decision rule: {rule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating decision rule: {e}")
            return False
    
    async def remove_decision_rule(self, rule_id: str) -> bool:
        """移除决策规则"""
        try:
            success = self.rule_engine.remove_rule(rule_id)
            if success:
                self.logger.info(f"Removed decision rule: {rule_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error removing decision rule: {e}")
            return False
    
    async def _generate_decision_options(
        self,
        decision_type: str,
        context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """生成决策选项"""
        options = []
        
        if decision_type == DecisionType.UI_ADAPTATION.value:
            options = self._generate_ui_adaptation_options(context)
        elif decision_type == DecisionType.LAYOUT_OPTIMIZATION.value:
            options = self._generate_layout_optimization_options(context)
        elif decision_type == DecisionType.THEME_ADJUSTMENT.value:
            options = self._generate_theme_adjustment_options(context)
        elif decision_type == DecisionType.COMPONENT_SELECTION.value:
            options = self._generate_component_selection_options(context)
        else:
            # 默认选项
            options = [{
                "option_id": generate_id("option_"),
                "name": "No Action",
                "description": "Take no action",
                "action_type": "none",
                "parameters": {},
                "expected_outcome": {},
                "confidence": 0.5,
                "cost": 0.0,
                "risk": 0.0,
                "benefits": [],
                "drawbacks": []
            }]
        
        return options
    
    def _generate_ui_adaptation_options(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """生成UI适配选项"""
        options = []
        
        # 基于用户行为模式的适配
        user_patterns = context.user_profile.get("behavior_patterns", [])
        
        if "power_user" in user_patterns:
            options.append({
                "option_id": generate_id("option_"),
                "name": "Enable Advanced Features",
                "description": "Show advanced tools and shortcuts for power users",
                "action_type": "ui_enhancement",
                "parameters": {
                    "show_advanced_tools": True,
                    "enable_keyboard_shortcuts": True,
                    "compact_layout": True
                },
                "expected_outcome": {"user_efficiency": 0.8},
                "confidence": 0.9,
                "cost": 0.2,
                "risk": 0.1,
                "benefits": ["Increased efficiency", "Better user experience"],
                "drawbacks": ["Potential complexity"]
            })
        
        if "casual_user" in user_patterns:
            options.append({
                "option_id": generate_id("option_"),
                "name": "Simplify Interface",
                "description": "Hide advanced features and provide guided experience",
                "action_type": "ui_simplification",
                "parameters": {
                    "hide_advanced_tools": True,
                    "show_tooltips": True,
                    "guided_mode": True
                },
                "expected_outcome": {"user_satisfaction": 0.8},
                "confidence": 0.8,
                "cost": 0.1,
                "risk": 0.05,
                "benefits": ["Easier to use", "Less overwhelming"],
                "drawbacks": ["Limited functionality"]
            })
        
        return options
    
    def _generate_layout_optimization_options(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """生成布局优化选项"""
        options = []
        
        # 基于屏幕尺寸优化
        device_info = context.user_profile.get("device_info", {})
        screen_width = device_info.get("screen_width", 1920)
        
        if screen_width < 768:  # 移动设备
            options.append({
                "option_id": generate_id("option_"),
                "name": "Mobile Optimized Layout",
                "description": "Optimize layout for mobile devices",
                "action_type": "layout_change",
                "parameters": {
                    "layout_type": "mobile",
                    "sidebar_collapsed": True,
                    "touch_friendly": True
                },
                "expected_outcome": {"mobile_usability": 0.9},
                "confidence": 0.95,
                "cost": 0.3,
                "risk": 0.1,
                "benefits": ["Better mobile experience"],
                "drawbacks": ["Less information density"]
            })
        
        elif screen_width > 1920:  # 大屏幕
            options.append({
                "option_id": generate_id("option_"),
                "name": "Wide Screen Layout",
                "description": "Utilize wide screen real estate",
                "action_type": "layout_change",
                "parameters": {
                    "layout_type": "wide",
                    "multi_column": True,
                    "sidebar_expanded": True
                },
                "expected_outcome": {"information_density": 0.9},
                "confidence": 0.8,
                "cost": 0.2,
                "risk": 0.15,
                "benefits": ["More information visible"],
                "drawbacks": ["Potential cognitive overload"]
            })
        
        return options
    
    def _generate_theme_adjustment_options(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """生成主题调整选项"""
        options = []
        
        # 基于时间的主题调整
        current_hour = datetime.now().hour
        
        if 20 <= current_hour or current_hour <= 6:  # 夜间
            options.append({
                "option_id": generate_id("option_"),
                "name": "Dark Theme",
                "description": "Switch to dark theme for night time",
                "action_type": "theme_change",
                "parameters": {
                    "theme": "dark",
                    "reduce_blue_light": True
                },
                "expected_outcome": {"eye_strain_reduction": 0.8},
                "confidence": 0.9,
                "cost": 0.1,
                "risk": 0.05,
                "benefits": ["Reduced eye strain", "Better for night use"],
                "drawbacks": ["May affect readability for some users"]
            })
        
        # 基于可访问性需求
        accessibility_needs = context.user_profile.get("accessibility_needs", [])
        
        if "high_contrast" in accessibility_needs:
            options.append({
                "option_id": generate_id("option_"),
                "name": "High Contrast Theme",
                "description": "Apply high contrast theme for better visibility",
                "action_type": "theme_change",
                "parameters": {
                    "theme": "high_contrast",
                    "bold_text": True,
                    "large_focus_indicators": True
                },
                "expected_outcome": {"accessibility_score": 0.95},
                "confidence": 0.95,
                "cost": 0.2,
                "risk": 0.05,
                "benefits": ["Better accessibility", "Improved visibility"],
                "drawbacks": ["May look less aesthetically pleasing"]
            })
        
        return options
    
    def _generate_component_selection_options(self, context: DecisionContext) -> List[Dict[str, Any]]:
        """生成组件选择选项"""
        options = []
        
        # 基于用户交互偏好选择组件
        interaction_style = context.user_profile.get("preferences", {}).get("interaction_style", "balanced")
        
        if interaction_style == "keyboard_focused":
            options.append({
                "option_id": generate_id("option_"),
                "name": "Keyboard-Friendly Components",
                "description": "Use components optimized for keyboard navigation",
                "action_type": "component_selection",
                "parameters": {
                    "prefer_keyboard_components": True,
                    "add_keyboard_shortcuts": True,
                    "focus_management": "enhanced"
                },
                "expected_outcome": {"keyboard_efficiency": 0.9},
                "confidence": 0.8,
                "cost": 0.3,
                "risk": 0.1,
                "benefits": ["Better keyboard navigation"],
                "drawbacks": ["May be less intuitive for mouse users"]
            })
        
        elif interaction_style == "mouse_focused":
            options.append({
                "option_id": generate_id("option_"),
                "name": "Mouse-Friendly Components",
                "description": "Use components optimized for mouse interaction",
                "action_type": "component_selection",
                "parameters": {
                    "prefer_mouse_components": True,
                    "hover_effects": True,
                    "drag_and_drop": True
                },
                "expected_outcome": {"mouse_efficiency": 0.9},
                "confidence": 0.8,
                "cost": 0.2,
                "risk": 0.1,
                "benefits": ["Better mouse interaction"],
                "drawbacks": ["May be less accessible"]
            })
        
        return options
    
    async def _execute_decision(
        self,
        decision_type: str,
        context: DecisionContext,
        options: List[DecisionOption],
        strategy: DecisionStrategy
    ) -> DecisionResult:
        """执行决策"""
        if strategy == DecisionStrategy.RULE_BASED:
            return await self._execute_rule_based_decision(decision_type, context, options)
        elif strategy == DecisionStrategy.ML_BASED:
            return await self._execute_ml_based_decision(decision_type, context, options)
        elif strategy == DecisionStrategy.HEURISTIC:
            return await self._execute_heuristic_decision(decision_type, context, options)
        elif strategy == DecisionStrategy.HYBRID:
            return await self._execute_hybrid_decision(decision_type, context, options)
        else:
            # 默认使用优化器
            return await self._execute_optimized_decision(decision_type, context, options)
    
    async def _execute_optimized_decision(
        self,
        decision_type: str,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> DecisionResult:
        """执行优化决策"""
        optimization_criteria = {
            "confidence_weight": 0.3,
            "cost_weight": 0.2,
            "risk_weight": 0.2,
            "benefit_weight": 0.15,
            "preference_weight": 0.15
        }
        
        selected_option = await self.optimizer.optimize_decision(
            options, context, optimization_criteria
        )
        
        return DecisionResult(
            decision_id=generate_id("decision_"),
            decision_type=DecisionType(decision_type),
            selected_option=selected_option,
            alternative_options=[opt for opt in options if opt != selected_option],
            reasoning="Selected based on multi-criteria optimization",
            confidence=selected_option.confidence,
            strategy_used=DecisionStrategy.HYBRID,
            execution_plan=self._create_execution_plan(selected_option),
            success_metrics={"optimization_score": 0.8},
            rollback_plan=self._create_rollback_plan(selected_option),
            timestamp=datetime.now()
        )
    
    async def _execute_rule_based_decision(
        self,
        decision_type: str,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> DecisionResult:
        """执行基于规则的决策"""
        # 评估规则
        rule_results = self.rule_engine.evaluate_rules(context, decision_type)
        
        # 找到匹配的规则
        matched_rules = [
            (rule, action_result) for rule, condition_result, action_result 
            in rule_results if condition_result and action_result
        ]
        
        if matched_rules:
            # 选择优先级最高的规则
            best_rule, action_result = max(matched_rules, key=lambda x: x[0].priority)
            
            # 根据规则结果选择选项
            selected_option = self._select_option_by_rule_result(options, action_result)
            
            reasoning = f"Selected based on rule: {best_rule.name}"
            confidence = best_rule.weight
        else:
            # 没有匹配的规则，选择默认选项
            selected_option = options[0] if options else None
            reasoning = "No matching rules found, using default option"
            confidence = 0.5
        
        return DecisionResult(
            decision_id=generate_id("decision_"),
            decision_type=DecisionType(decision_type),
            selected_option=selected_option,
            alternative_options=[opt for opt in options if opt != selected_option],
            reasoning=reasoning,
            confidence=confidence,
            strategy_used=DecisionStrategy.RULE_BASED,
            execution_plan=self._create_execution_plan(selected_option),
            success_metrics={"rule_match_count": len(matched_rules)},
            rollback_plan=self._create_rollback_plan(selected_option),
            timestamp=datetime.now()
        )
    
    async def _execute_heuristic_decision(
        self,
        decision_type: str,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> DecisionResult:
        """执行基于启发式的决策"""
        # 评估启发式函数
        heuristic_scores = self.heuristic_engine.evaluate_heuristics(context)
        combined_score = self.heuristic_engine.get_combined_score(context)
        
        # 基于启发式分数选择选项
        if combined_score > 0.7:
            # 高分数，选择激进选项
            selected_option = max(options, key=lambda x: x.confidence - x.risk)
            reasoning = "High heuristic score, selecting aggressive option"
        elif combined_score < 0.3:
            # 低分数，选择保守选项
            selected_option = min(options, key=lambda x: x.risk + x.cost)
            reasoning = "Low heuristic score, selecting conservative option"
        else:
            # 中等分数，选择平衡选项
            selected_option = max(options, key=lambda x: x.confidence)
            reasoning = "Moderate heuristic score, selecting balanced option"
        
        return DecisionResult(
            decision_id=generate_id("decision_"),
            decision_type=DecisionType(decision_type),
            selected_option=selected_option,
            alternative_options=[opt for opt in options if opt != selected_option],
            reasoning=reasoning,
            confidence=combined_score,
            strategy_used=DecisionStrategy.HEURISTIC,
            execution_plan=self._create_execution_plan(selected_option),
            success_metrics={"heuristic_score": combined_score, "heuristic_details": heuristic_scores},
            rollback_plan=self._create_rollback_plan(selected_option),
            timestamp=datetime.now()
        )
    
    async def _execute_ml_based_decision(
        self,
        decision_type: str,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> DecisionResult:
        """执行基于机器学习的决策"""
        # 尝试使用ML模型预测
        model_name = f"{decision_type}_model"
        prediction_result = self.ml_model.predict(model_name, context)
        
        if prediction_result:
            prediction, confidence = prediction_result
            
            # 根据预测结果选择选项
            selected_option = self._select_option_by_prediction(options, prediction)
            reasoning = f"Selected based on ML model prediction: {prediction}"
        else:
            # ML模型不可用，回退到启发式方法
            return await self._execute_heuristic_decision(decision_type, context, options)
        
        return DecisionResult(
            decision_id=generate_id("decision_"),
            decision_type=DecisionType(decision_type),
            selected_option=selected_option,
            alternative_options=[opt for opt in options if opt != selected_option],
            reasoning=reasoning,
            confidence=confidence,
            strategy_used=DecisionStrategy.ML_BASED,
            execution_plan=self._create_execution_plan(selected_option),
            success_metrics={"ml_confidence": confidence, "model_used": model_name},
            rollback_plan=self._create_rollback_plan(selected_option),
            timestamp=datetime.now()
        )
    
    async def _execute_hybrid_decision(
        self,
        decision_type: str,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> DecisionResult:
        """执行混合策略决策"""
        # 组合多种策略的结果
        strategies_results = []
        
        # 规则基础决策
        try:
            rule_result = await self._execute_rule_based_decision(decision_type, context, options)
            strategies_results.append(("rule", rule_result))
        except Exception as e:
            self.logger.warning(f"Rule-based decision failed: {e}")
        
        # 启发式决策
        try:
            heuristic_result = await self._execute_heuristic_decision(decision_type, context, options)
            strategies_results.append(("heuristic", heuristic_result))
        except Exception as e:
            self.logger.warning(f"Heuristic decision failed: {e}")
        
        # ML决策
        try:
            ml_result = await self._execute_ml_based_decision(decision_type, context, options)
            strategies_results.append(("ml", ml_result))
        except Exception as e:
            self.logger.warning(f"ML-based decision failed: {e}")
        
        if not strategies_results:
            # 所有策略都失败，使用默认选项
            selected_option = options[0] if options else None
            confidence = 0.1
            reasoning = "All strategies failed, using default option"
        else:
            # 选择置信度最高的结果
            best_strategy, best_result = max(strategies_results, key=lambda x: x[1].confidence)
            selected_option = best_result.selected_option
            confidence = best_result.confidence
            reasoning = f"Hybrid decision based on {best_strategy} strategy (confidence: {confidence:.2f})"
        
        return DecisionResult(
            decision_id=generate_id("decision_"),
            decision_type=DecisionType(decision_type),
            selected_option=selected_option,
            alternative_options=[opt for opt in options if opt != selected_option],
            reasoning=reasoning,
            confidence=confidence,
            strategy_used=DecisionStrategy.HYBRID,
            execution_plan=self._create_execution_plan(selected_option),
            success_metrics={
                "strategies_used": len(strategies_results),
                "strategy_details": {name: result.confidence for name, result in strategies_results}
            },
            rollback_plan=self._create_rollback_plan(selected_option),
            timestamp=datetime.now()
        )
    
    def _select_decision_strategy(
        self,
        decision_type: str,
        context: DecisionContext
    ) -> DecisionStrategy:
        """选择决策策略"""
        # 基于决策类型和上下文选择策略
        
        # 如果有明确的用户偏好，优先使用
        user_preferences = context.user_profile.get("preferences", {})
        if "decision_strategy" in user_preferences:
            return DecisionStrategy(user_preferences["decision_strategy"])
        
        # 基于决策类型选择
        if decision_type in [DecisionType.ACCESSIBILITY_IMPROVEMENT.value, DecisionType.ERROR_RECOVERY.value]:
            return DecisionStrategy.RULE_BASED  # 这些场景适合规则
        
        elif decision_type in [DecisionType.PERSONALIZATION.value, DecisionType.UI_ADAPTATION.value]:
            return DecisionStrategy.ML_BASED  # 个性化适合ML
        
        elif decision_type in [DecisionType.PERFORMANCE_OPTIMIZATION.value]:
            return DecisionStrategy.HEURISTIC  # 性能优化适合启发式
        
        else:
            return DecisionStrategy.HYBRID  # 默认使用混合策略
    
    def _parse_decision_context(self, context: Dict[str, Any]) -> DecisionContext:
        """解析决策上下文"""
        return DecisionContext(
            context_id=context.get("context_id"),
            user_id=context.get("user_id"),
            session_id=context.get("session_id", ""),
            current_ui_state=context.get("current_ui_state", {}),
            user_profile=context.get("user_profile", {}),
            interaction_history=context.get("interaction_history", []),
            performance_metrics=context.get("performance_metrics", {}),
            constraints=context.get("constraints", {}),
            goals=context.get("goals", []),
            timestamp=datetime.now()
        )
    
    def _parse_decision_option(self, option: Dict[str, Any]) -> DecisionOption:
        """解析决策选项"""
        return DecisionOption(
            option_id=option.get("option_id"),
            name=option.get("name", ""),
            description=option.get("description", ""),
            action_type=option.get("action_type", ""),
            parameters=option.get("parameters", {}),
            expected_outcome=option.get("expected_outcome", {}),
            confidence=option.get("confidence", 0.5),
            cost=option.get("cost", 0.0),
            risk=option.get("risk", 0.0),
            benefits=option.get("benefits", []),
            drawbacks=option.get("drawbacks", [])
        )
    
    def _select_option_by_rule_result(
        self,
        options: List[DecisionOption],
        action_result: Any
    ) -> DecisionOption:
        """根据规则结果选择选项"""
        if isinstance(action_result, str):
            # 如果结果是字符串，尝试匹配选项名称
            for option in options:
                if action_result.lower() in option.name.lower():
                    return option
        
        elif isinstance(action_result, dict) and "option_id" in action_result:
            # 如果结果包含选项ID
            option_id = action_result["option_id"]
            for option in options:
                if option.option_id == option_id:
                    return option
        
        # 默认返回第一个选项
        return options[0] if options else None
    
    def _select_option_by_prediction(
        self,
        options: List[DecisionOption],
        prediction: Any
    ) -> DecisionOption:
        """根据ML预测结果选择选项"""
        if isinstance(prediction, (int, float)):
            # 如果预测是数值，选择对应索引的选项
            index = int(prediction) % len(options)
            return options[index]
        
        elif isinstance(prediction, str):
            # 如果预测是字符串，尝试匹配选项
            for option in options:
                if prediction.lower() in option.name.lower():
                    return option
        
        # 默认返回置信度最高的选项
        return max(options, key=lambda x: x.confidence)
    
    def _create_execution_plan(self, option: DecisionOption) -> Dict[str, Any]:
        """创建执行计划"""
        return {
            "action_type": option.action_type,
            "parameters": option.parameters,
            "steps": [
                {
                    "step": 1,
                    "action": "validate_parameters",
                    "description": "Validate execution parameters"
                },
                {
                    "step": 2,
                    "action": "execute_action",
                    "description": f"Execute {option.action_type} action"
                },
                {
                    "step": 3,
                    "action": "monitor_outcome",
                    "description": "Monitor execution outcome"
                }
            ],
            "estimated_duration": 5.0,  # 秒
            "success_criteria": option.expected_outcome
        }
    
    def _create_rollback_plan(self, option: DecisionOption) -> Dict[str, Any]:
        """创建回滚计划"""
        return {
            "rollback_action": f"revert_{option.action_type}",
            "rollback_parameters": {},
            "rollback_steps": [
                {
                    "step": 1,
                    "action": "save_current_state",
                    "description": "Save current state before rollback"
                },
                {
                    "step": 2,
                    "action": "revert_changes",
                    "description": "Revert changes made by the decision"
                },
                {
                    "step": 3,
                    "action": "verify_rollback",
                    "description": "Verify rollback was successful"
                }
            ],
            "rollback_triggers": [
                "user_dissatisfaction",
                "performance_degradation",
                "error_occurrence"
            ]
        }
    
    def _initialize_default_rules(self) -> None:
        """初始化默认规则"""
        # 可访问性规则
        accessibility_rule = DecisionRule(
            rule_id="accessibility_high_contrast",
            name="High Contrast for Accessibility",
            description="Enable high contrast theme for users with accessibility needs",
            condition="'high_contrast' in context.user_profile.get('accessibility_needs', [])",
            action="{'action_type': 'theme_change', 'theme': 'high_contrast'}",
            priority=100,
            weight=1.0,
            tags=["accessibility", "theme"]
        )
        self.rule_engine.add_rule(accessibility_rule, "accessibility")
        
        # 性能规则
        performance_rule = DecisionRule(
            rule_id="performance_optimization",
            name="Performance Optimization",
            description="Optimize UI when performance is poor",
            condition="context.performance_metrics.get('response_time', 0) > 2.0",
            action="{'action_type': 'ui_optimization', 'reduce_animations': True}",
            priority=80,
            weight=0.9,
            tags=["performance", "optimization"]
        )
        self.rule_engine.add_rule(performance_rule, "performance")
        
        # 移动设备规则
        mobile_rule = DecisionRule(
            rule_id="mobile_optimization",
            name="Mobile Device Optimization",
            description="Optimize for mobile devices",
            condition="context.user_profile.get('device_info', {}).get('type') == 'mobile'",
            action="{'action_type': 'layout_change', 'layout': 'mobile'}",
            priority=70,
            weight=0.8,
            tags=["mobile", "layout"]
        )
        self.rule_engine.add_rule(mobile_rule, "layout")
    
    def _initialize_default_heuristics(self) -> None:
        """初始化默认启发式函数"""
        
        def user_activity_heuristic(context: DecisionContext) -> float:
            """用户活跃度启发式"""
            interaction_count = len(context.interaction_history)
            if interaction_count > 50:
                return 0.9  # 高活跃度
            elif interaction_count > 20:
                return 0.7  # 中等活跃度
            else:
                return 0.3  # 低活跃度
        
        def performance_heuristic(context: DecisionContext) -> float:
            """性能启发式"""
            response_time = context.performance_metrics.get("response_time", 1.0)
            if response_time < 1.0:
                return 0.9  # 性能良好
            elif response_time < 2.0:
                return 0.6  # 性能一般
            else:
                return 0.2  # 性能较差
        
        def time_of_day_heuristic(context: DecisionContext) -> float:
            """时间启发式"""
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 17:
                return 0.8  # 工作时间
            elif 18 <= current_hour <= 22:
                return 0.6  # 晚间时间
            else:
                return 0.4  # 深夜/早晨
        
        # 注册启发式函数
        self.heuristic_engine.register_heuristic("user_activity", user_activity_heuristic, 0.3)
        self.heuristic_engine.register_heuristic("performance", performance_heuristic, 0.4)
        self.heuristic_engine.register_heuristic("time_of_day", time_of_day_heuristic, 0.3)
    
    @event_handler(EventBusEventType.USER_INTERACTION)
    async def handle_user_interaction(self, event: EventBusEvent) -> None:
        """处理用户交互事件"""
        interaction_data = event.data
        self.logger.debug(f"Processing user interaction for decision making")
        
        # 可以在这里触发自动决策
        # 例如，如果检测到用户困惑，自动提供帮助
    
    @event_handler(EventBusEventType.PERFORMANCE_METRIC)
    async def handle_performance_alert(self, event: EventBusEvent) -> None:
        """处理性能警报事件"""
        alert_data = event.data
        self.logger.info(f"Performance alert received: {alert_data}")
        
        # 自动触发性能优化决策
        context = {
            "context_id": generate_id("context_"),
            "session_id": alert_data.get("session_id", ""),
            "current_ui_state": {},
            "user_profile": {},
            "interaction_history": [],
            "performance_metrics": alert_data.get("metrics", {}),
            "constraints": {},
            "goals": ["improve_performance"]
        }
        
        await self.make_decision(
            DecisionType.PERFORMANCE_OPTIMIZATION.value,
            context
        )
    
    async def get_decision_statistics(self) -> Dict[str, Any]:
        """获取决策统计信息"""
        total_decisions = len(self.decision_history)
        
        if total_decisions == 0:
            return {
                "total_decisions": 0,
                "average_confidence": 0.0,
                "strategy_distribution": {},
                "decision_type_distribution": {}
            }
        
        # 计算平均置信度
        total_confidence = sum(decision.confidence for decision in self.decision_history)
        average_confidence = total_confidence / total_decisions
        
        # 策略分布
        strategy_counts = defaultdict(int)
        for decision in self.decision_history:
            strategy_counts[decision.strategy_used.value] += 1
        
        strategy_distribution = {
            strategy: count / total_decisions 
            for strategy, count in strategy_counts.items()
        }
        
        # 决策类型分布
        type_counts = defaultdict(int)
        for decision in self.decision_history:
            type_counts[decision.decision_type.value] += 1
        
        type_distribution = {
            decision_type: count / total_decisions 
            for decision_type, count in type_counts.items()
        }
        
        return {
            "total_decisions": total_decisions,
            "average_confidence": average_confidence,
            "strategy_distribution": strategy_distribution,
            "decision_type_distribution": type_distribution,
            "rule_statistics": self.rule_engine.get_rule_statistics(),
            "cache_hit_rate": getattr(self.decision_cache, "hit_rate", 0.0)
        }


# 导出主要类
DecisionEngine = SmartUIDecisionEngine  # 为了向后兼容
__all__ = ['SmartUIDecisionEngine', 'DecisionEngine']

