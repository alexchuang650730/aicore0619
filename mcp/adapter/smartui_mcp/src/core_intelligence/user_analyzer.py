"""
SmartUI MCP - 用户分析器

实现智能用户行为分析、意图识别和偏好学习的核心组件。
基于用户交互数据，提供深度的用户洞察和个性化建议。
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
import hashlib
import numpy as np
from enum import Enum

from ..common import (
    IUserAnalyzer, EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    SingletonMeta
)


class InteractionType(str, Enum):
    """交互类型枚举"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    HOVER = "hover"
    FOCUS = "focus"
    BLUR = "blur"
    INPUT = "input"
    CHANGE = "change"
    SUBMIT = "submit"
    SCROLL = "scroll"
    RESIZE = "resize"
    NAVIGATION = "navigation"
    SEARCH = "search"
    SELECTION = "selection"
    DRAG = "drag"
    DROP = "drop"
    KEY_PRESS = "key_press"
    TOUCH = "touch"
    GESTURE = "gesture"
    VOICE = "voice"
    CUSTOM = "custom"


class IntentType(str, Enum):
    """意图类型枚举"""
    BROWSE = "browse"
    SEARCH = "search"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    SAVE = "save"
    SHARE = "share"
    EXPORT = "export"
    IMPORT = "import"
    CONFIGURE = "configure"
    NAVIGATE = "navigate"
    LEARN = "learn"
    HELP = "help"
    COMPARE = "compare"
    ANALYZE = "analyze"
    COLLABORATE = "collaborate"
    AUTOMATE = "automate"
    OPTIMIZE = "optimize"
    TROUBLESHOOT = "troubleshoot"
    UNKNOWN = "unknown"


class BehaviorPattern(str, Enum):
    """行为模式枚举"""
    POWER_USER = "power_user"
    CASUAL_USER = "casual_user"
    EXPLORER = "explorer"
    GOAL_ORIENTED = "goal_oriented"
    METHODICAL = "methodical"
    IMPATIENT = "impatient"
    DETAIL_ORIENTED = "detail_oriented"
    VISUAL_LEARNER = "visual_learner"
    KEYBOARD_HEAVY = "keyboard_heavy"
    MOUSE_HEAVY = "mouse_heavy"
    MOBILE_FIRST = "mobile_first"
    ACCESSIBILITY_USER = "accessibility_user"


@dataclass
class UserAction:
    """用户行为记录"""
    action_id: str
    action_type: InteractionType
    target: str
    timestamp: datetime
    context: Dict[str, Any]
    session_id: str
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    duration: Optional[float] = None
    coordinates: Optional[Tuple[int, int]] = None
    device_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.action_id is None:
            self.action_id = generate_id("action_")


@dataclass
class UserIntent:
    """用户意图"""
    intent_id: str
    intent_type: IntentType
    confidence: float
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[str]
    detected_at: datetime
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.intent_id is None:
            self.intent_id = generate_id("intent_")


@dataclass
class UserPreference:
    """用户偏好"""
    preference_id: str
    preference_type: str
    value: Any
    confidence: float
    last_updated: datetime
    source: str = "inferred"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preference_id is None:
            self.preference_id = generate_id("pref_")
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    session_id: str
    behavior_patterns: List[BehaviorPattern]
    preferences: Dict[str, UserPreference]
    intents: List[UserIntent]
    interaction_stats: Dict[str, Any]
    device_info: Dict[str, Any]
    accessibility_needs: List[str]
    skill_level: str  # beginner, intermediate, advanced, expert
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        if not self.behavior_patterns:
            self.behavior_patterns = []
        if not self.preferences:
            self.preferences = {}
        if not self.intents:
            self.intents = []
        if not self.interaction_stats:
            self.interaction_stats = {}
        if not self.device_info:
            self.device_info = {}
        if not self.accessibility_needs:
            self.accessibility_needs = []


class UserSessionManager:
    """用户会话管理器"""
    
    def __init__(self, session_timeout: int = 1800):  # 30分钟
        self.session_timeout = session_timeout
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """创建新会话"""
        session_id = generate_id("session_")
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "actions": deque(maxlen=1000),
            "context": {},
            "device_info": {},
            "is_active": True
        }
        
        if user_id:
            self.user_sessions[user_id].add(session_id)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        session = self.sessions.get(session_id)
        if session and self._is_session_active(session):
            return session
        return None
    
    def update_session_activity(self, session_id: str) -> None:
        """更新会话活动时间"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.now()
    
    def end_session(self, session_id: str) -> None:
        """结束会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["is_active"] = False
            session["ended_at"] = datetime.now()
            
            user_id = session.get("user_id")
            if user_id and session_id in self.user_sessions[user_id]:
                self.user_sessions[user_id].remove(session_id)
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if not self._is_session_active(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.end_session(session_id)
        
        return len(expired_sessions)
    
    def _is_session_active(self, session: Dict[str, Any]) -> bool:
        """检查会话是否活跃"""
        if not session.get("is_active", True):
            return False
        
        last_activity = session.get("last_activity")
        if last_activity:
            return (datetime.now() - last_activity).total_seconds() < self.session_timeout
        
        return False


class IntentDetector:
    """意图检测器"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.context_weights = {
            "recent_actions": 0.4,
            "current_page": 0.3,
            "user_history": 0.2,
            "time_context": 0.1
        }
    
    def detect_intent(
        self,
        actions: List[UserAction],
        context: Dict[str, Any]
    ) -> List[UserIntent]:
        """检测用户意图"""
        intents = []
        
        # 基于行为序列检测意图
        sequence_intents = self._detect_sequence_intents(actions)
        intents.extend(sequence_intents)
        
        # 基于上下文检测意图
        context_intents = self._detect_context_intents(actions, context)
        intents.extend(context_intents)
        
        # 基于时间模式检测意图
        temporal_intents = self._detect_temporal_intents(actions)
        intents.extend(temporal_intents)
        
        # 去重和排序
        intents = self._deduplicate_and_rank_intents(intents)
        
        return intents
    
    def _detect_sequence_intents(self, actions: List[UserAction]) -> List[UserIntent]:
        """基于行为序列检测意图"""
        intents = []
        
        if len(actions) < 2:
            return intents
        
        # 检测搜索意图
        if self._is_search_sequence(actions):
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.SEARCH,
                confidence=0.8,
                parameters={"query": self._extract_search_query(actions)},
                context={"sequence_length": len(actions)},
                suggested_actions=["show_search_suggestions", "filter_results"],
                detected_at=datetime.now()
            ))
        
        # 检测创建意图
        if self._is_creation_sequence(actions):
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.CREATE,
                confidence=0.7,
                parameters={"creation_type": self._infer_creation_type(actions)},
                context={"sequence_length": len(actions)},
                suggested_actions=["show_templates", "provide_guidance"],
                detected_at=datetime.now()
            ))
        
        # 检测编辑意图
        if self._is_editing_sequence(actions):
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.EDIT,
                confidence=0.75,
                parameters={"edit_target": self._identify_edit_target(actions)},
                context={"sequence_length": len(actions)},
                suggested_actions=["show_edit_tools", "enable_auto_save"],
                detected_at=datetime.now()
            ))
        
        return intents
    
    def _detect_context_intents(
        self,
        actions: List[UserAction],
        context: Dict[str, Any]
    ) -> List[UserIntent]:
        """基于上下文检测意图"""
        intents = []
        
        current_page = context.get("current_page", "")
        user_role = context.get("user_role", "")
        time_of_day = context.get("time_of_day", "")
        
        # 基于页面上下文
        if "dashboard" in current_page.lower():
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.ANALYZE,
                confidence=0.6,
                parameters={"analysis_type": "dashboard_overview"},
                context={"page": current_page},
                suggested_actions=["highlight_key_metrics", "show_trends"],
                detected_at=datetime.now()
            ))
        
        # 基于用户角色
        if user_role == "admin" and any(action.action_type == InteractionType.CLICK for action in actions):
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.CONFIGURE,
                confidence=0.5,
                parameters={"config_scope": "system"},
                context={"role": user_role},
                suggested_actions=["show_admin_tools", "provide_config_help"],
                detected_at=datetime.now()
            ))
        
        return intents
    
    def _detect_temporal_intents(self, actions: List[UserAction]) -> List[UserIntent]:
        """基于时间模式检测意图"""
        intents = []
        
        if not actions:
            return intents
        
        # 检测急迫性
        recent_actions = [a for a in actions if (datetime.now() - a.timestamp).total_seconds() < 60]
        if len(recent_actions) > 10:  # 1分钟内超过10个操作
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.TROUBLESHOOT,
                confidence=0.6,
                parameters={"urgency": "high"},
                context={"action_frequency": len(recent_actions)},
                suggested_actions=["show_quick_help", "simplify_interface"],
                detected_at=datetime.now()
            ))
        
        # 检测学习模式
        exploration_actions = [a for a in actions if a.action_type in [InteractionType.HOVER, InteractionType.NAVIGATION]]
        if len(exploration_actions) > len(actions) * 0.6:
            intents.append(UserIntent(
                intent_id=generate_id("intent_"),
                intent_type=IntentType.LEARN,
                confidence=0.7,
                parameters={"learning_style": "exploratory"},
                context={"exploration_ratio": len(exploration_actions) / len(actions)},
                suggested_actions=["show_tooltips", "provide_guided_tour"],
                detected_at=datetime.now()
            ))
        
        return intents
    
    def _load_intent_patterns(self) -> Dict[str, Any]:
        """加载意图模式"""
        return {
            "search_keywords": ["search", "find", "look", "query"],
            "creation_keywords": ["new", "create", "add", "make"],
            "editing_keywords": ["edit", "modify", "change", "update"],
            "navigation_keywords": ["go", "navigate", "move", "switch"],
            "help_keywords": ["help", "how", "what", "why", "guide"]
        }
    
    def _is_search_sequence(self, actions: List[UserAction]) -> bool:
        """检测是否为搜索序列"""
        search_indicators = 0
        for action in actions[-5:]:  # 检查最近5个操作
            if action.action_type == InteractionType.INPUT and "search" in action.target.lower():
                search_indicators += 2
            elif action.action_type == InteractionType.CLICK and "search" in action.target.lower():
                search_indicators += 1
            elif action.action_type == InteractionType.KEY_PRESS and action.metadata.get("key") == "Enter":
                search_indicators += 1
        
        return search_indicators >= 2
    
    def _is_creation_sequence(self, actions: List[UserAction]) -> bool:
        """检测是否为创建序列"""
        creation_indicators = 0
        for action in actions[-5:]:
            if any(keyword in action.target.lower() for keyword in ["new", "create", "add"]):
                creation_indicators += 1
            elif action.action_type == InteractionType.CLICK and "button" in action.target.lower():
                creation_indicators += 0.5
        
        return creation_indicators >= 1.5
    
    def _is_editing_sequence(self, actions: List[UserAction]) -> bool:
        """检测是否为编辑序列"""
        editing_indicators = 0
        for action in actions[-5:]:
            if action.action_type == InteractionType.INPUT:
                editing_indicators += 1
            elif action.action_type == InteractionType.FOCUS:
                editing_indicators += 0.5
            elif any(keyword in action.target.lower() for keyword in ["edit", "modify"]):
                editing_indicators += 1
        
        return editing_indicators >= 2
    
    def _extract_search_query(self, actions: List[UserAction]) -> str:
        """提取搜索查询"""
        for action in reversed(actions):
            if action.action_type == InteractionType.INPUT and action.metadata.get("value"):
                return action.metadata["value"]
        return ""
    
    def _infer_creation_type(self, actions: List[UserAction]) -> str:
        """推断创建类型"""
        for action in actions:
            target = action.target.lower()
            if "document" in target:
                return "document"
            elif "project" in target:
                return "project"
            elif "file" in target:
                return "file"
        return "unknown"
    
    def _identify_edit_target(self, actions: List[UserAction]) -> str:
        """识别编辑目标"""
        for action in actions:
            if action.action_type == InteractionType.FOCUS:
                return action.target
        return "unknown"
    
    def _deduplicate_and_rank_intents(self, intents: List[UserIntent]) -> List[UserIntent]:
        """去重和排序意图"""
        # 按意图类型去重，保留置信度最高的
        intent_map = {}
        for intent in intents:
            key = intent.intent_type
            if key not in intent_map or intent.confidence > intent_map[key].confidence:
                intent_map[key] = intent
        
        # 按置信度排序
        sorted_intents = sorted(intent_map.values(), key=lambda x: x.confidence, reverse=True)
        
        return sorted_intents[:5]  # 最多返回5个意图


class BehaviorAnalyzer:
    """行为分析器"""
    
    def __init__(self):
        self.pattern_cache = AsyncCache(max_size=100, ttl=3600)  # 1小时缓存
    
    async def analyze_behavior_patterns(
        self,
        user_id: str,
        actions: List[UserAction],
        time_window: timedelta = timedelta(hours=24)
    ) -> List[BehaviorPattern]:
        """分析用户行为模式"""
        cache_key = f"behavior_{user_id}_{int(time_window.total_seconds())}"
        
        # 尝试从缓存获取
        cached_patterns = await self.pattern_cache.get(cache_key)
        if cached_patterns:
            return cached_patterns
        
        patterns = []
        
        # 过滤时间窗口内的行为
        cutoff_time = datetime.now() - time_window
        recent_actions = [a for a in actions if a.timestamp >= cutoff_time]
        
        if not recent_actions:
            return patterns
        
        # 分析交互频率
        interaction_frequency = len(recent_actions) / time_window.total_seconds() * 3600  # 每小时操作数
        
        if interaction_frequency > 100:
            patterns.append(BehaviorPattern.POWER_USER)
        elif interaction_frequency < 10:
            patterns.append(BehaviorPattern.CASUAL_USER)
        
        # 分析操作类型分布
        action_types = [a.action_type for a in recent_actions]
        type_counts = defaultdict(int)
        for action_type in action_types:
            type_counts[action_type] += 1
        
        total_actions = len(recent_actions)
        
        # 键盘vs鼠标偏好
        keyboard_actions = type_counts[InteractionType.KEY_PRESS] + type_counts[InteractionType.INPUT]
        mouse_actions = type_counts[InteractionType.CLICK] + type_counts[InteractionType.HOVER]
        
        if keyboard_actions > mouse_actions * 1.5:
            patterns.append(BehaviorPattern.KEYBOARD_HEAVY)
        elif mouse_actions > keyboard_actions * 1.5:
            patterns.append(BehaviorPattern.MOUSE_HEAVY)
        
        # 探索性行为
        navigation_ratio = type_counts[InteractionType.NAVIGATION] / total_actions
        hover_ratio = type_counts[InteractionType.HOVER] / total_actions
        
        if navigation_ratio > 0.3 or hover_ratio > 0.2:
            patterns.append(BehaviorPattern.EXPLORER)
        
        # 目标导向性
        submit_ratio = type_counts[InteractionType.SUBMIT] / total_actions
        if submit_ratio > 0.1:
            patterns.append(BehaviorPattern.GOAL_ORIENTED)
        
        # 耐心程度分析
        quick_sequences = self._detect_quick_sequences(recent_actions)
        if len(quick_sequences) > total_actions * 0.3:
            patterns.append(BehaviorPattern.IMPATIENT)
        else:
            patterns.append(BehaviorPattern.METHODICAL)
        
        # 设备偏好
        device_types = set(a.device_info.get("type", "desktop") for a in recent_actions if a.device_info)
        if "mobile" in device_types and len(device_types) == 1:
            patterns.append(BehaviorPattern.MOBILE_FIRST)
        
        # 缓存结果
        await self.pattern_cache.set(cache_key, patterns)
        
        return patterns
    
    def _detect_quick_sequences(self, actions: List[UserAction]) -> List[List[UserAction]]:
        """检测快速操作序列"""
        sequences = []
        current_sequence = []
        
        for i, action in enumerate(actions):
            if i == 0:
                current_sequence = [action]
                continue
            
            time_diff = (action.timestamp - actions[i-1].timestamp).total_seconds()
            
            if time_diff < 1.0:  # 1秒内的操作认为是快速序列
                current_sequence.append(action)
            else:
                if len(current_sequence) >= 3:  # 至少3个连续快速操作
                    sequences.append(current_sequence)
                current_sequence = [action]
        
        # 检查最后一个序列
        if len(current_sequence) >= 3:
            sequences.append(current_sequence)
        
        return sequences


class PreferenceEngine:
    """偏好引擎"""
    
    def __init__(self):
        self.preference_weights = {
            "ui_theme": 1.0,
            "layout_preference": 0.8,
            "interaction_style": 0.9,
            "content_density": 0.7,
            "animation_preference": 0.6,
            "notification_preference": 0.8,
            "accessibility_needs": 1.0
        }
    
    def infer_preferences(
        self,
        actions: List[UserAction],
        context: Dict[str, Any]
    ) -> Dict[str, UserPreference]:
        """推断用户偏好"""
        preferences = {}
        
        # 主题偏好
        theme_pref = self._infer_theme_preference(actions, context)
        if theme_pref:
            preferences["ui_theme"] = theme_pref
        
        # 布局偏好
        layout_pref = self._infer_layout_preference(actions)
        if layout_pref:
            preferences["layout_preference"] = layout_pref
        
        # 交互风格偏好
        interaction_pref = self._infer_interaction_preference(actions)
        if interaction_pref:
            preferences["interaction_style"] = interaction_pref
        
        # 内容密度偏好
        density_pref = self._infer_content_density_preference(actions)
        if density_pref:
            preferences["content_density"] = density_pref
        
        # 动画偏好
        animation_pref = self._infer_animation_preference(actions)
        if animation_pref:
            preferences["animation_preference"] = animation_pref
        
        # 通知偏好
        notification_pref = self._infer_notification_preference(actions)
        if notification_pref:
            preferences["notification_preference"] = notification_pref
        
        # 可访问性需求
        accessibility_pref = self._infer_accessibility_needs(actions, context)
        if accessibility_pref:
            preferences["accessibility_needs"] = accessibility_pref
        
        return preferences
    
    def _infer_theme_preference(
        self,
        actions: List[UserAction],
        context: Dict[str, Any]
    ) -> Optional[UserPreference]:
        """推断主题偏好"""
        # 基于时间推断
        current_hour = datetime.now().hour
        if 20 <= current_hour or current_hour <= 6:
            return UserPreference(
                preference_id=generate_id("pref_"),
                preference_type="ui_theme",
                value="dark",
                confidence=0.7,
                last_updated=datetime.now(),
                source="time_based"
            )
        
        # 基于设备类型推断
        device_info = context.get("device_info", {})
        if device_info.get("type") == "mobile":
            return UserPreference(
                preference_id=generate_id("pref_"),
                preference_type="ui_theme",
                value="auto",
                confidence=0.6,
                last_updated=datetime.now(),
                source="device_based"
            )
        
        return None
    
    def _infer_layout_preference(self, actions: List[UserAction]) -> Optional[UserPreference]:
        """推断布局偏好"""
        # 分析用户点击的区域分布
        click_positions = []
        for action in actions:
            if action.action_type == InteractionType.CLICK and action.coordinates:
                click_positions.append(action.coordinates)
        
        if not click_positions:
            return None
        
        # 分析点击位置的分布
        x_positions = [pos[0] for pos in click_positions]
        avg_x = sum(x_positions) / len(x_positions)
        
        # 假设屏幕宽度为1920px
        screen_width = 1920
        
        if avg_x < screen_width * 0.3:
            layout_value = "sidebar_left"
        elif avg_x > screen_width * 0.7:
            layout_value = "sidebar_right"
        else:
            layout_value = "centered"
        
        return UserPreference(
            preference_id=generate_id("pref_"),
            preference_type="layout_preference",
            value=layout_value,
            confidence=0.6,
            last_updated=datetime.now(),
            source="interaction_pattern"
        )
    
    def _infer_interaction_preference(self, actions: List[UserAction]) -> Optional[UserPreference]:
        """推断交互风格偏好"""
        keyboard_actions = sum(1 for a in actions if a.action_type in [InteractionType.KEY_PRESS, InteractionType.INPUT])
        mouse_actions = sum(1 for a in actions if a.action_type in [InteractionType.CLICK, InteractionType.HOVER])
        
        total_actions = len(actions)
        if total_actions == 0:
            return None
        
        keyboard_ratio = keyboard_actions / total_actions
        
        if keyboard_ratio > 0.6:
            interaction_style = "keyboard_focused"
            confidence = 0.8
        elif keyboard_ratio < 0.3:
            interaction_style = "mouse_focused"
            confidence = 0.8
        else:
            interaction_style = "balanced"
            confidence = 0.6
        
        return UserPreference(
            preference_id=generate_id("pref_"),
            preference_type="interaction_style",
            value=interaction_style,
            confidence=confidence,
            last_updated=datetime.now(),
            source="behavior_analysis"
        )
    
    def _infer_content_density_preference(self, actions: List[UserAction]) -> Optional[UserPreference]:
        """推断内容密度偏好"""
        scroll_actions = [a for a in actions if a.action_type == InteractionType.SCROLL]
        
        if not scroll_actions:
            return None
        
        # 分析滚动频率
        scroll_frequency = len(scroll_actions) / len(actions)
        
        if scroll_frequency > 0.3:
            density_value = "compact"  # 频繁滚动可能偏好紧凑布局
            confidence = 0.7
        else:
            density_value = "comfortable"
            confidence = 0.6
        
        return UserPreference(
            preference_id=generate_id("pref_"),
            preference_type="content_density",
            value=density_value,
            confidence=confidence,
            last_updated=datetime.now(),
            source="scroll_behavior"
        )
    
    def _infer_animation_preference(self, actions: List[UserAction]) -> Optional[UserPreference]:
        """推断动画偏好"""
        # 基于操作速度推断动画偏好
        quick_actions = 0
        for i in range(1, len(actions)):
            time_diff = (actions[i].timestamp - actions[i-1].timestamp).total_seconds()
            if time_diff < 0.5:  # 0.5秒内的连续操作
                quick_actions += 1
        
        if quick_actions > len(actions) * 0.4:
            animation_value = "reduced"  # 快速操作用户可能不喜欢动画
            confidence = 0.7
        else:
            animation_value = "normal"
            confidence = 0.5
        
        return UserPreference(
            preference_id=generate_id("pref_"),
            preference_type="animation_preference",
            value=animation_value,
            confidence=confidence,
            last_updated=datetime.now(),
            source="interaction_speed"
        )
    
    def _infer_notification_preference(self, actions: List[UserAction]) -> Optional[UserPreference]:
        """推断通知偏好"""
        # 分析用户对通知的响应
        notification_interactions = [
            a for a in actions 
            if "notification" in a.target.lower() or "alert" in a.target.lower()
        ]
        
        if not notification_interactions:
            return UserPreference(
                preference_id=generate_id("pref_"),
                preference_type="notification_preference",
                value="minimal",
                confidence=0.5,
                last_updated=datetime.now(),
                source="no_interaction"
            )
        
        # 分析响应时间
        quick_responses = sum(
            1 for a in notification_interactions 
            if a.action_type == InteractionType.CLICK
        )
        
        if quick_responses > len(notification_interactions) * 0.7:
            notification_value = "immediate"
            confidence = 0.8
        else:
            notification_value = "batched"
            confidence = 0.6
        
        return UserPreference(
            preference_id=generate_id("pref_"),
            preference_type="notification_preference",
            value=notification_value,
            confidence=confidence,
            last_updated=datetime.now(),
            source="notification_behavior"
        )
    
    def _infer_accessibility_needs(
        self,
        actions: List[UserAction],
        context: Dict[str, Any]
    ) -> Optional[UserPreference]:
        """推断可访问性需求"""
        accessibility_needs = []
        
        # 检测键盘导航使用
        tab_actions = [
            a for a in actions 
            if a.action_type == InteractionType.KEY_PRESS and a.metadata.get("key") == "Tab"
        ]
        
        if len(tab_actions) > len(actions) * 0.2:
            accessibility_needs.append("keyboard_navigation")
        
        # 检测屏幕阅读器使用（基于特定的交互模式）
        focus_actions = [a for a in actions if a.action_type == InteractionType.FOCUS]
        if len(focus_actions) > len(actions) * 0.3:
            accessibility_needs.append("screen_reader")
        
        # 检测高对比度需求（基于设备设置）
        device_info = context.get("device_info", {})
        if device_info.get("high_contrast"):
            accessibility_needs.append("high_contrast")
        
        if accessibility_needs:
            return UserPreference(
                preference_id=generate_id("pref_"),
                preference_type="accessibility_needs",
                value=accessibility_needs,
                confidence=0.9,
                last_updated=datetime.now(),
                source="interaction_analysis"
            )
        
        return None


class SmartUIUserAnalyzer(IUserAnalyzer):
    """SmartUI用户分析器实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 初始化子组件
        self.session_manager = UserSessionManager(
            session_timeout=self.config.get("session_timeout", 1800)
        )
        self.intent_detector = IntentDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.preference_engine = PreferenceEngine()
        
        # 数据存储
        self.user_profiles: Dict[str, UserProfile] = {}
        self.action_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # 缓存
        self.analysis_cache = AsyncCache(max_size=200, ttl=300)  # 5分钟缓存
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        # 性能监控
        self.performance_timer = Timer()
        
        self.logger.info("SmartUI User Analyzer initialized")
    
    @log_execution_time()
    async def analyze_user_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户交互数据"""
        try:
            # 解析交互数据
            user_action = self._parse_interaction_data(interaction_data)
            
            # 更新会话活动
            self.session_manager.update_session_activity(user_action.session_id)
            
            # 存储行为记录
            self.action_history[user_action.user_id or user_action.session_id].append(user_action)
            
            # 获取用户画像
            user_profile = await self.get_user_profile(user_action.user_id or user_action.session_id)
            
            # 检测意图
            recent_actions = list(self.action_history[user_action.user_id or user_action.session_id])[-10:]
            intents = self.intent_detector.detect_intent(recent_actions, interaction_data.get("context", {}))
            
            # 更新用户画像中的意图
            user_profile.intents = intents
            user_profile.updated_at = datetime.now()
            
            # 发布用户交互事件
            await publish_event(
                event_type=EventBusEventType.USER_INTERACTION,
                data={
                    "user_id": user_action.user_id,
                    "session_id": user_action.session_id,
                    "action": asdict(user_action),
                    "intents": [asdict(intent) for intent in intents]
                },
                source="user_analyzer"
            )
            
            return {
                "success": True,
                "user_action": asdict(user_action),
                "detected_intents": [asdict(intent) for intent in intents],
                "user_profile_updated": True,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing user interaction: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """获取用户画像"""
        if user_id not in self.user_profiles:
            # 创建新的用户画像
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                session_id=user_id,  # 如果没有明确的session_id，使用user_id
                behavior_patterns=[],
                preferences={},
                intents=[],
                interaction_stats={},
                device_info={},
                accessibility_needs=[],
                skill_level="intermediate",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        return self.user_profiles[user_id]
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """更新用户画像"""
        user_profile = await self.get_user_profile(user_id)
        
        # 更新行为模式
        if "behavior_patterns" in profile_data:
            user_profile.behavior_patterns = profile_data["behavior_patterns"]
        
        # 更新偏好
        if "preferences" in profile_data:
            for pref_type, pref_data in profile_data["preferences"].items():
                if isinstance(pref_data, dict):
                    user_profile.preferences[pref_type] = UserPreference(**pref_data)
                else:
                    user_profile.preferences[pref_type] = pref_data
        
        # 更新其他字段
        for field in ["skill_level", "accessibility_needs", "device_info"]:
            if field in profile_data:
                setattr(user_profile, field, profile_data[field])
        
        user_profile.updated_at = datetime.now()
        
        # 发布用户画像更新事件
        await publish_event(
            event_type=EventBusEventType.USER_PROFILE_UPDATE,
            data={
                "user_id": user_id,
                "updated_fields": list(profile_data.keys()),
                "profile": asdict(user_profile)
            },
            source="user_analyzer"
        )
    
    async def detect_behavior_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """检测用户行为模式"""
        cache_key = f"behavior_patterns_{user_id}"
        
        # 尝试从缓存获取
        cached_patterns = await self.analysis_cache.get(cache_key)
        if cached_patterns:
            return cached_patterns
        
        # 获取用户行为历史
        actions = list(self.action_history[user_id])
        
        if not actions:
            return []
        
        # 分析行为模式
        patterns = await self.behavior_analyzer.analyze_behavior_patterns(user_id, actions)
        
        # 转换为字典格式
        pattern_dicts = [
            {
                "pattern": pattern.value,
                "confidence": 0.8,  # 默认置信度
                "detected_at": datetime.now().isoformat(),
                "evidence": self._get_pattern_evidence(pattern, actions)
            }
            for pattern in patterns
        ]
        
        # 缓存结果
        await self.analysis_cache.set(cache_key, pattern_dicts)
        
        return pattern_dicts
    
    async def predict_user_intent(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """预测用户意图"""
        try:
            user_id = interaction_data.get("user_id") or interaction_data.get("session_id")
            if not user_id:
                return {"success": False, "error": "Missing user_id or session_id"}
            
            # 获取最近的行为历史
            recent_actions = list(self.action_history[user_id])[-20:]
            
            # 检测意图
            intents = self.intent_detector.detect_intent(
                recent_actions,
                interaction_data.get("context", {})
            )
            
            # 获取最高置信度的意图
            primary_intent = intents[0] if intents else None
            
            result = {
                "success": True,
                "primary_intent": asdict(primary_intent) if primary_intent else None,
                "all_intents": [asdict(intent) for intent in intents],
                "prediction_timestamp": datetime.now().isoformat()
            }
            
            # 如果有主要意图，提供相应的建议
            if primary_intent:
                result["recommendations"] = self._get_intent_recommendations(primary_intent)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error predicting user intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "prediction_timestamp": datetime.now().isoformat()
            }
    
    def _parse_interaction_data(self, interaction_data: Dict[str, Any]) -> UserAction:
        """解析交互数据为UserAction对象"""
        return UserAction(
            action_id=interaction_data.get("action_id") or generate_id("action_"),
            action_type=InteractionType(interaction_data.get("action_type", "click")),
            target=interaction_data.get("target", ""),
            timestamp=datetime.fromisoformat(interaction_data.get("timestamp", datetime.now().isoformat())),
            context=interaction_data.get("context", {}),
            session_id=interaction_data.get("session_id", ""),
            user_id=interaction_data.get("user_id"),
            metadata=interaction_data.get("metadata", {}),
            duration=interaction_data.get("duration"),
            coordinates=interaction_data.get("coordinates"),
            device_info=interaction_data.get("device_info", {})
        )
    
    def _get_pattern_evidence(self, pattern: BehaviorPattern, actions: List[UserAction]) -> Dict[str, Any]:
        """获取行为模式的证据"""
        evidence = {}
        
        if pattern == BehaviorPattern.POWER_USER:
            evidence["action_frequency"] = len(actions) / 24  # 每小时操作数
            evidence["keyboard_shortcuts"] = sum(
                1 for a in actions 
                if a.action_type == InteractionType.KEY_PRESS and a.metadata.get("ctrl", False)
            )
        
        elif pattern == BehaviorPattern.EXPLORER:
            evidence["navigation_ratio"] = sum(
                1 for a in actions if a.action_type == InteractionType.NAVIGATION
            ) / len(actions)
            evidence["hover_ratio"] = sum(
                1 for a in actions if a.action_type == InteractionType.HOVER
            ) / len(actions)
        
        elif pattern == BehaviorPattern.KEYBOARD_HEAVY:
            evidence["keyboard_action_ratio"] = sum(
                1 for a in actions 
                if a.action_type in [InteractionType.KEY_PRESS, InteractionType.INPUT]
            ) / len(actions)
        
        return evidence
    
    def _get_intent_recommendations(self, intent: UserIntent) -> List[str]:
        """根据意图获取推荐操作"""
        recommendations = []
        
        if intent.intent_type == IntentType.SEARCH:
            recommendations.extend([
                "Show search suggestions",
                "Enable advanced search filters",
                "Highlight search results",
                "Provide search history"
            ])
        
        elif intent.intent_type == IntentType.CREATE:
            recommendations.extend([
                "Show creation templates",
                "Provide step-by-step guidance",
                "Enable auto-save",
                "Suggest related tools"
            ])
        
        elif intent.intent_type == IntentType.LEARN:
            recommendations.extend([
                "Show interactive tutorials",
                "Provide contextual help",
                "Enable guided tour",
                "Display tooltips and hints"
            ])
        
        elif intent.intent_type == IntentType.TROUBLESHOOT:
            recommendations.extend([
                "Show quick help",
                "Simplify interface",
                "Provide error explanations",
                "Offer alternative approaches"
            ])
        
        return recommendations
    
    @event_handler(EventBusEventType.UI_COMPONENT_MOUNTED)
    async def handle_component_mounted(self, event: EventBusEvent) -> None:
        """处理UI组件挂载事件"""
        component_data = event.data
        self.logger.debug(f"Component mounted: {component_data.get('component_id')}")
        
        # 可以在这里分析用户对新组件的交互
    
    @event_handler(EventBusEventType.API_STATE_CHANGED)
    async def handle_api_state_changed(self, event: EventBusEvent) -> None:
        """处理API状态变化事件"""
        state_data = event.data
        self.logger.debug(f"API state changed: {state_data.get('path')}")
        
        # 可以在这里分析状态变化对用户行为的影响
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """清理过期数据"""
        cleanup_stats = {
            "expired_sessions": 0,
            "cleaned_profiles": 0,
            "cleared_cache_entries": 0
        }
        
        # 清理过期会话
        cleanup_stats["expired_sessions"] = self.session_manager.cleanup_expired_sessions()
        
        # 清理长时间未活动的用户画像
        cutoff_time = datetime.now() - timedelta(days=30)
        expired_profiles = [
            user_id for user_id, profile in self.user_profiles.items()
            if profile.updated_at < cutoff_time
        ]
        
        for user_id in expired_profiles:
            del self.user_profiles[user_id]
            if user_id in self.action_history:
                del self.action_history[user_id]
        
        cleanup_stats["cleaned_profiles"] = len(expired_profiles)
        
        # 清理缓存
        await self.analysis_cache.clear()
        cleanup_stats["cleared_cache_entries"] = 1  # 全部清理
        
        self.logger.info(f"Cleanup completed: {cleanup_stats}")
        
        return cleanup_stats
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        return {
            "total_users": len(self.user_profiles),
            "active_sessions": len([
                s for s in self.session_manager.sessions.values()
                if s.get("is_active", False)
            ]),
            "total_actions": sum(len(actions) for actions in self.action_history.values()),
            "cache_hit_rate": getattr(self.analysis_cache, "hit_rate", 0.0),
            "last_cleanup": datetime.now().isoformat()
        }


# 导出主要类
UserAnalyzer = SmartUIUserAnalyzer  # 为了向后兼容
__all__ = ['SmartUIUserAnalyzer', 'UserAnalyzer']

