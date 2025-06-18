#!/usr/bin/env python3
"""
SmartUI Enhanced - 用户输入分析器
实现实时分析用户交互模式、识别用户意图和预测用户行为
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class UserAction:
    """用户行为记录"""
    action_type: str  # click, input, navigation, scroll, etc.
    target: str       # 目标元素或页面
    timestamp: datetime
    context: Dict[str, Any]
    session_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class UserIntent:
    """用户意图"""
    intent_type: str
    confidence: float
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[str]
    
@dataclass
class UserPreference:
    """用户偏好"""
    preference_type: str
    value: Any
    confidence: float
    last_updated: datetime
    frequency: int = 1

class UserBehaviorPattern:
    """用户行为模式"""
    
    def __init__(self, pattern_id: str):
        self.pattern_id = pattern_id
        self.actions: List[UserAction] = []
        self.frequency = 0
        self.last_occurrence = None
        self.confidence = 0.0
        self.next_action_predictions: Dict[str, float] = {}
    
    def add_action(self, action: UserAction):
        """添加行为到模式"""
        self.actions.append(action)
        self.frequency += 1
        self.last_occurrence = action.timestamp
        self._update_predictions()
    
    def _update_predictions(self):
        """更新下一步行为预测"""
        if len(self.actions) < 2:
            return
        
        # 分析行为序列，预测下一步可能的行为
        action_sequences = []
        for i in range(len(self.actions) - 1):
            current_action = self.actions[i].action_type
            next_action = self.actions[i + 1].action_type
            action_sequences.append((current_action, next_action))
        
        # 计算转移概率
        transition_counts = defaultdict(int)
        for current, next_action in action_sequences:
            transition_counts[next_action] += 1
        
        total_transitions = sum(transition_counts.values())
        if total_transitions > 0:
            self.next_action_predictions = {
                action: count / total_transitions
                for action, count in transition_counts.items()
            }

class IntentClassifier:
    """意图分类器"""
    
    def __init__(self):
        self.intent_patterns = {
            "search": [
                r"search|find|look|query",
                r"where.*is|how.*to|what.*is"
            ],
            "create": [
                r"create|new|add|make|build",
                r"start.*project|begin.*task"
            ],
            "edit": [
                r"edit|modify|change|update|alter",
                r"fix|correct|adjust"
            ],
            "delete": [
                r"delete|remove|clear|clean",
                r"trash|discard"
            ],
            "navigate": [
                r"go.*to|navigate|visit|open",
                r"back|forward|home|menu"
            ],
            "analyze": [
                r"analyze|review|check|examine",
                r"report|statistics|metrics"
            ],
            "configure": [
                r"config|setting|preference|option",
                r"setup|install|enable|disable"
            ]
        }
        
        self.context_weights = {
            "page_type": 0.3,
            "recent_actions": 0.4,
            "time_of_day": 0.1,
            "session_duration": 0.2
        }
    
    async def classify_intent(self, action: UserAction, context: Dict[str, Any]) -> UserIntent:
        """分类用户意图"""
        intent_scores = {}
        
        # 基于行为类型的基础分数
        base_scores = self._get_base_intent_scores(action)
        
        # 基于文本内容的分数（如果有输入文本）
        text_scores = self._analyze_text_intent(action)
        
        # 基于上下文的分数
        context_scores = self._analyze_context_intent(action, context)
        
        # 综合计算意图分数
        for intent_type in self.intent_patterns.keys():
            score = (
                base_scores.get(intent_type, 0.0) * 0.4 +
                text_scores.get(intent_type, 0.0) * 0.3 +
                context_scores.get(intent_type, 0.0) * 0.3
            )
            intent_scores[intent_type] = score
        
        # 选择最高分数的意图
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_type, confidence = best_intent
        
        # 提取意图参数
        parameters = self._extract_intent_parameters(action, intent_type)
        
        # 生成建议行为
        suggested_actions = self._generate_suggested_actions(intent_type, parameters, context)
        
        return UserIntent(
            intent_type=intent_type,
            confidence=confidence,
            parameters=parameters,
            context=context,
            suggested_actions=suggested_actions
        )
    
    def _get_base_intent_scores(self, action: UserAction) -> Dict[str, float]:
        """基于行为类型获取基础意图分数"""
        action_intent_mapping = {
            "click": {"navigate": 0.6, "edit": 0.3, "create": 0.1},
            "input": {"create": 0.5, "edit": 0.4, "search": 0.1},
            "search": {"search": 0.9, "analyze": 0.1},
            "scroll": {"navigate": 0.7, "analyze": 0.3},
            "form_submit": {"create": 0.6, "edit": 0.3, "configure": 0.1},
            "button_click": {"navigate": 0.4, "create": 0.3, "edit": 0.3},
            "menu_select": {"navigate": 0.8, "configure": 0.2}
        }
        
        return action_intent_mapping.get(action.action_type, {})
    
    def _analyze_text_intent(self, action: UserAction) -> Dict[str, float]:
        """分析文本内容的意图"""
        text_content = ""
        
        # 提取文本内容
        if "text" in action.context:
            text_content = action.context["text"].lower()
        elif "value" in action.context:
            text_content = str(action.context["value"]).lower()
        
        if not text_content:
            return {}
        
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                if re.search(pattern, text_content):
                    score += 0.5
            
            intent_scores[intent_type] = min(score, 1.0)
        
        return intent_scores
    
    def _analyze_context_intent(self, action: UserAction, context: Dict[str, Any]) -> Dict[str, float]:
        """分析上下文的意图"""
        context_scores = {}
        
        # 页面类型上下文
        page_type = context.get("page_type", "")
        if "dashboard" in page_type:
            context_scores["analyze"] = 0.6
            context_scores["navigate"] = 0.4
        elif "form" in page_type:
            context_scores["create"] = 0.5
            context_scores["edit"] = 0.5
        elif "settings" in page_type:
            context_scores["configure"] = 0.8
            context_scores["edit"] = 0.2
        
        # 最近行为上下文
        recent_actions = context.get("recent_actions", [])
        if recent_actions:
            last_action = recent_actions[-1] if recent_actions else None
            if last_action and last_action.get("action_type") == "search":
                context_scores["analyze"] = 0.7
        
        return context_scores
    
    def _extract_intent_parameters(self, action: UserAction, intent_type: str) -> Dict[str, Any]:
        """提取意图参数"""
        parameters = {}
        
        if intent_type == "search":
            if "text" in action.context:
                parameters["query"] = action.context["text"]
            if "filters" in action.context:
                parameters["filters"] = action.context["filters"]
        
        elif intent_type == "create":
            if "form_data" in action.context:
                parameters["data"] = action.context["form_data"]
            if "template" in action.context:
                parameters["template"] = action.context["template"]
        
        elif intent_type == "navigate":
            if "target_url" in action.context:
                parameters["destination"] = action.context["target_url"]
            if "target_element" in action.context:
                parameters["target"] = action.context["target_element"]
        
        return parameters
    
    def _generate_suggested_actions(self, intent_type: str, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> List[str]:
        """生成建议行为"""
        suggestions = []
        
        if intent_type == "search":
            suggestions.extend([
                "show_search_filters",
                "enable_advanced_search",
                "show_search_history"
            ])
        
        elif intent_type == "create":
            suggestions.extend([
                "show_templates",
                "enable_auto_save",
                "show_creation_wizard"
            ])
        
        elif intent_type == "edit":
            suggestions.extend([
                "show_edit_toolbar",
                "enable_version_control",
                "show_change_history"
            ])
        
        elif intent_type == "analyze":
            suggestions.extend([
                "show_analytics_dashboard",
                "enable_real_time_updates",
                "show_export_options"
            ])
        
        return suggestions

class UserPreferenceTracker:
    """用户偏好跟踪器"""
    
    def __init__(self):
        self.preferences: Dict[str, UserPreference] = {}
        self.preference_categories = {
            "ui_theme": ["dark", "light", "auto"],
            "layout_density": ["compact", "comfortable", "spacious"],
            "notification_frequency": ["high", "medium", "low", "off"],
            "default_view": ["list", "grid", "card"],
            "language": ["en", "zh", "auto"],
            "timezone": ["auto", "utc", "local"]
        }
    
    async def update_preferences(self, action: UserAction) -> Dict[str, UserPreference]:
        """更新用户偏好"""
        updated_preferences = {}
        
        # 分析行为中的偏好信号
        preference_signals = self._extract_preference_signals(action)
        
        for pref_type, value in preference_signals.items():
            if pref_type in self.preference_categories:
                # 更新或创建偏好
                if pref_type in self.preferences:
                    existing_pref = self.preferences[pref_type]
                    if existing_pref.value == value:
                        # 增强现有偏好
                        existing_pref.frequency += 1
                        existing_pref.confidence = min(existing_pref.confidence + 0.1, 1.0)
                        existing_pref.last_updated = datetime.now()
                    else:
                        # 创建新偏好或替换
                        confidence = 0.3  # 新偏好的初始置信度
                        self.preferences[pref_type] = UserPreference(
                            preference_type=pref_type,
                            value=value,
                            confidence=confidence,
                            last_updated=datetime.now()
                        )
                else:
                    # 创建新偏好
                    self.preferences[pref_type] = UserPreference(
                        preference_type=pref_type,
                        value=value,
                        confidence=0.5,
                        last_updated=datetime.now()
                    )
                
                updated_preferences[pref_type] = self.preferences[pref_type]
        
        return updated_preferences
    
    def _extract_preference_signals(self, action: UserAction) -> Dict[str, Any]:
        """从用户行为中提取偏好信号"""
        signals = {}
        
        # UI主题偏好
        if action.action_type == "theme_change":
            signals["ui_theme"] = action.context.get("theme", "light")
        
        # 布局密度偏好
        if action.action_type == "layout_change":
            signals["layout_density"] = action.context.get("density", "comfortable")
        
        # 视图偏好
        if action.action_type == "view_change":
            signals["default_view"] = action.context.get("view_type", "list")
        
        # 语言偏好
        if action.action_type == "language_change":
            signals["language"] = action.context.get("language", "en")
        
        # 从时间模式推断偏好
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 18:
            # 白天使用，可能偏好亮色主题
            if "ui_theme" not in signals:
                signals["ui_theme"] = "light"
        else:
            # 夜间使用，可能偏好暗色主题
            if "ui_theme" not in signals:
                signals["ui_theme"] = "dark"
        
        return signals
    
    def get_preferences(self) -> Dict[str, UserPreference]:
        """获取用户偏好"""
        return self.preferences.copy()
    
    def get_preference_recommendations(self) -> Dict[str, Any]:
        """获取偏好推荐"""
        recommendations = {}
        
        for category, options in self.preference_categories.items():
            if category not in self.preferences:
                # 为未设置的偏好提供默认推荐
                recommendations[category] = {
                    "recommended_value": options[0],  # 默认第一个选项
                    "reason": "default_recommendation",
                    "confidence": 0.3
                }
            else:
                pref = self.preferences[category]
                if pref.confidence < 0.7:
                    # 为低置信度偏好提供替代建议
                    alternative_options = [opt for opt in options if opt != pref.value]
                    if alternative_options:
                        recommendations[category] = {
                            "recommended_value": alternative_options[0],
                            "reason": "low_confidence_alternative",
                            "confidence": 0.5
                        }
        
        return recommendations

class UserAnalyzer:
    """用户输入分析器 - 主类"""
    
    def __init__(self):
        self.interaction_history: deque = deque(maxlen=1000)  # 保留最近1000个交互
        self.behavior_patterns: Dict[str, UserBehaviorPattern] = {}
        self.intent_classifier = IntentClassifier()
        self.preference_tracker = UserPreferenceTracker()
        self.session_data: Dict[str, Any] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
    
    async def analyze_user_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户输入并提取意图"""
        try:
            # 创建用户行为记录
            action = UserAction(
                action_type=input_data.get("action_type", "unknown"),
                target=input_data.get("target", ""),
                timestamp=datetime.now(),
                context=input_data.get("context", {}),
                session_id=input_data.get("session_id", "default"),
                user_id=input_data.get("user_id"),
                metadata=input_data.get("metadata", {})
            )
            
            # 添加到历史记录
            self.interaction_history.append(action)
            
            # 更新会话数据
            await self._update_session_data(action)
            
            # 分析用户意图
            context = await self._build_analysis_context(action)
            intent = await self.intent_classifier.classify_intent(action, context)
            
            # 更新用户偏好
            preferences = await self.preference_tracker.update_preferences(action)
            
            # 更新行为模式
            await self._update_behavior_patterns(action)
            
            # 预测下一步行为
            next_action_predictions = await self._predict_next_actions(action, context)
            
            # 生成个性化建议
            personalized_suggestions = await self._generate_personalized_suggestions(
                intent, preferences, context
            )
            
            return {
                "intent": asdict(intent),
                "preferences": {k: asdict(v) for k, v in preferences.items()},
                "next_action_predictions": next_action_predictions,
                "personalized_suggestions": personalized_suggestions,
                "context": context,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"用户输入分析失败: {e}")
            return {
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def _update_session_data(self, action: UserAction):
        """更新会话数据"""
        session_id = action.session_id
        
        if session_id not in self.session_data:
            self.session_data[session_id] = {
                "start_time": action.timestamp,
                "action_count": 0,
                "unique_targets": set(),
                "action_types": defaultdict(int)
            }
        
        session = self.session_data[session_id]
        session["action_count"] += 1
        session["unique_targets"].add(action.target)
        session["action_types"][action.action_type] += 1
        session["last_activity"] = action.timestamp
    
    async def _build_analysis_context(self, action: UserAction) -> Dict[str, Any]:
        """构建分析上下文"""
        session_id = action.session_id
        session = self.session_data.get(session_id, {})
        
        # 获取最近的行为
        recent_actions = [
            asdict(a) for a in list(self.interaction_history)[-5:]
            if a.session_id == session_id
        ]
        
        # 计算会话持续时间
        session_duration = 0
        if "start_time" in session:
            session_duration = (action.timestamp - session["start_time"]).total_seconds()
        
        # 分析页面类型
        page_type = self._infer_page_type(action.target, action.context)
        
        return {
            "session_id": session_id,
            "session_duration": session_duration,
            "action_count": session.get("action_count", 0),
            "recent_actions": recent_actions,
            "page_type": page_type,
            "time_of_day": action.timestamp.hour,
            "day_of_week": action.timestamp.weekday(),
            "user_id": action.user_id
        }
    
    def _infer_page_type(self, target: str, context: Dict[str, Any]) -> str:
        """推断页面类型"""
        target_lower = target.lower()
        
        if "dashboard" in target_lower:
            return "dashboard"
        elif "form" in target_lower or "input" in target_lower:
            return "form"
        elif "settings" in target_lower or "config" in target_lower:
            return "settings"
        elif "list" in target_lower or "table" in target_lower:
            return "list"
        elif "detail" in target_lower or "view" in target_lower:
            return "detail"
        else:
            return "unknown"
    
    async def _update_behavior_patterns(self, action: UserAction):
        """更新行为模式"""
        # 生成模式ID（基于行为序列）
        recent_actions = list(self.interaction_history)[-3:]  # 最近3个行为
        if len(recent_actions) >= 2:
            pattern_sequence = " -> ".join([a.action_type for a in recent_actions])
            pattern_id = hashlib.md5(pattern_sequence.encode()).hexdigest()[:8]
            
            if pattern_id not in self.behavior_patterns:
                self.behavior_patterns[pattern_id] = UserBehaviorPattern(pattern_id)
            
            self.behavior_patterns[pattern_id].add_action(action)
    
    async def _predict_next_actions(self, action: UserAction, context: Dict[str, Any]) -> Dict[str, float]:
        """预测下一步行为"""
        predictions = {}
        
        # 基于行为模式预测
        for pattern in self.behavior_patterns.values():
            if pattern.next_action_predictions:
                for next_action, probability in pattern.next_action_predictions.items():
                    if next_action in predictions:
                        predictions[next_action] = max(predictions[next_action], probability)
                    else:
                        predictions[next_action] = probability
        
        # 基于上下文预测
        context_predictions = self._predict_from_context(action, context)
        for next_action, probability in context_predictions.items():
            if next_action in predictions:
                predictions[next_action] = (predictions[next_action] + probability) / 2
            else:
                predictions[next_action] = probability
        
        # 归一化概率
        total_prob = sum(predictions.values())
        if total_prob > 0:
            predictions = {k: v / total_prob for k, v in predictions.items()}
        
        return predictions
    
    def _predict_from_context(self, action: UserAction, context: Dict[str, Any]) -> Dict[str, float]:
        """基于上下文预测下一步行为"""
        predictions = {}
        
        # 基于页面类型预测
        page_type = context.get("page_type", "")
        if page_type == "form":
            predictions["form_submit"] = 0.6
            predictions["input"] = 0.3
            predictions["navigate"] = 0.1
        elif page_type == "list":
            predictions["click"] = 0.5
            predictions["search"] = 0.3
            predictions["navigate"] = 0.2
        elif page_type == "dashboard":
            predictions["navigate"] = 0.4
            predictions["click"] = 0.4
            predictions["analyze"] = 0.2
        
        # 基于当前行为预测
        if action.action_type == "input":
            predictions["form_submit"] = 0.7
            predictions["input"] = 0.2
            predictions["navigate"] = 0.1
        elif action.action_type == "search":
            predictions["click"] = 0.6
            predictions["navigate"] = 0.3
            predictions["search"] = 0.1
        
        return predictions
    
    async def _generate_personalized_suggestions(self, intent: UserIntent, 
                                               preferences: Dict[str, UserPreference],
                                               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成个性化建议"""
        suggestions = []
        
        # 基于意图的建议
        intent_suggestions = self._get_intent_based_suggestions(intent)
        suggestions.extend(intent_suggestions)
        
        # 基于偏好的建议
        preference_suggestions = self._get_preference_based_suggestions(preferences)
        suggestions.extend(preference_suggestions)
        
        # 基于上下文的建议
        context_suggestions = self._get_context_based_suggestions(context)
        suggestions.extend(context_suggestions)
        
        # 去重并排序
        unique_suggestions = []
        seen_types = set()
        
        for suggestion in suggestions:
            if suggestion["type"] not in seen_types:
                unique_suggestions.append(suggestion)
                seen_types.add(suggestion["type"])
        
        # 按优先级排序
        unique_suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        return unique_suggestions[:5]  # 返回前5个建议
    
    def _get_intent_based_suggestions(self, intent: UserIntent) -> List[Dict[str, Any]]:
        """基于意图的建议"""
        suggestions = []
        
        if intent.intent_type == "search" and intent.confidence > 0.7:
            suggestions.append({
                "type": "enable_advanced_search",
                "title": "启用高级搜索",
                "description": "使用更多筛选条件来精确搜索",
                "priority": 8
            })
        
        if intent.intent_type == "create" and intent.confidence > 0.6:
            suggestions.append({
                "type": "show_templates",
                "title": "使用模板",
                "description": "选择预设模板快速开始",
                "priority": 7
            })
        
        return suggestions
    
    def _get_preference_based_suggestions(self, preferences: Dict[str, UserPreference]) -> List[Dict[str, Any]]:
        """基于偏好的建议"""
        suggestions = []
        
        # 检查主题偏好
        if "ui_theme" in preferences:
            theme_pref = preferences["ui_theme"]
            if theme_pref.confidence < 0.5:
                suggestions.append({
                    "type": "theme_recommendation",
                    "title": "主题建议",
                    "description": f"尝试{theme_pref.value}主题以获得更好体验",
                    "priority": 5
                })
        
        return suggestions
    
    def _get_context_based_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于上下文的建议"""
        suggestions = []
        
        # 基于时间的建议
        hour = context.get("time_of_day", 12)
        if 22 <= hour or hour <= 6:  # 夜间
            suggestions.append({
                "type": "night_mode",
                "title": "夜间模式",
                "description": "启用夜间模式保护视力",
                "priority": 6
            })
        
        # 基于会话时长的建议
        session_duration = context.get("session_duration", 0)
        if session_duration > 1800:  # 超过30分钟
            suggestions.append({
                "type": "break_reminder",
                "title": "休息提醒",
                "description": "您已连续使用30分钟，建议休息一下",
                "priority": 4
            })
        
        return suggestions
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        if user_id not in self.user_profiles:
            return {}
        
        return self.user_profiles[user_id]
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        total_interactions = len(self.interaction_history)
        
        if total_interactions == 0:
            return {"total_interactions": 0}
        
        # 统计行为类型分布
        action_type_counts = defaultdict(int)
        for action in self.interaction_history:
            action_type_counts[action.action_type] += 1
        
        # 统计会话信息
        active_sessions = len(self.session_data)
        
        # 统计行为模式
        pattern_count = len(self.behavior_patterns)
        
        return {
            "total_interactions": total_interactions,
            "action_type_distribution": dict(action_type_counts),
            "active_sessions": active_sessions,
            "behavior_patterns": pattern_count,
            "analysis_period": {
                "start": self.interaction_history[0].timestamp.isoformat() if self.interaction_history else None,
                "end": self.interaction_history[-1].timestamp.isoformat() if self.interaction_history else None
            }
        }

if __name__ == "__main__":
    # 测试代码
    async def test_user_analyzer():
        analyzer = UserAnalyzer()
        
        # 模拟用户输入
        test_inputs = [
            {
                "action_type": "click",
                "target": "search_button",
                "context": {"page": "dashboard"},
                "session_id": "test_session_1"
            },
            {
                "action_type": "input",
                "target": "search_box",
                "context": {"text": "find user data", "page": "dashboard"},
                "session_id": "test_session_1"
            },
            {
                "action_type": "form_submit",
                "target": "search_form",
                "context": {"query": "user data", "page": "dashboard"},
                "session_id": "test_session_1"
            }
        ]
        
        for input_data in test_inputs:
            result = await analyzer.analyze_user_input(input_data)
            print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print("-" * 50)
        
        # 获取分析摘要
        summary = analyzer.get_analytics_summary()
        print(f"分析摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
    
    # 运行测试
    asyncio.run(test_user_analyzer())

