"""
SmartUI MCP - 智能UI适配器

实现智能UI适配功能，连接智能决策层和UI渲染层。
负责根据用户分析结果和决策引擎输出，动态调整UI配置和渲染参数。
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import copy

from ..common import (
    EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    UIConfiguration, UIComponent, ComponentType, LayoutType, ThemeType,
    ComponentProps, ComponentStyle, LayoutConfig, ThemeConfig
)


class AdaptationStrategy(str, Enum):
    """适配策略枚举"""
    CONSERVATIVE = "conservative"  # 保守策略，最小化改动
    MODERATE = "moderate"         # 适中策略，平衡改动和效果
    AGGRESSIVE = "aggressive"     # 激进策略，最大化适配效果
    CUSTOM = "custom"            # 自定义策略


class AdaptationScope(str, Enum):
    """适配范围枚举"""
    GLOBAL = "global"           # 全局适配
    LAYOUT = "layout"           # 布局适配
    THEME = "theme"             # 主题适配
    COMPONENT = "component"     # 组件适配
    ACCESSIBILITY = "accessibility"  # 可访问性适配
    PERFORMANCE = "performance"  # 性能适配


@dataclass
class AdaptationRule:
    """适配规则"""
    rule_id: str
    name: str
    description: str
    scope: AdaptationScope
    strategy: AdaptationStrategy
    conditions: Dict[str, Any]  # 触发条件
    actions: Dict[str, Any]     # 执行动作
    priority: int = 50          # 优先级 (0-100)
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.rule_id is None:
            self.rule_id = generate_id("adapt_rule_")
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AdaptationContext:
    """适配上下文"""
    context_id: str
    user_profile: Dict[str, Any]
    device_info: Dict[str, Any]
    environment_info: Dict[str, Any]
    performance_constraints: Dict[str, Any]
    accessibility_requirements: Dict[str, Any]
    current_ui_config: Dict[str, Any]
    adaptation_history: List[Dict[str, Any]]
    timestamp: datetime
    
    def __post_init__(self):
        if self.context_id is None:
            self.context_id = generate_id("adapt_ctx_")


@dataclass
class AdaptationResult:
    """适配结果"""
    result_id: str
    original_config: Dict[str, Any]
    adapted_config: Dict[str, Any]
    applied_rules: List[str]
    adaptation_score: float  # 适配效果评分 (0-1)
    performance_impact: float  # 性能影响评分 (0-1)
    changes_summary: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.result_id is None:
            self.result_id = generate_id("adapt_result_")


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, AdaptationRule] = {}
        self.rule_groups: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(f"{__name__}.RuleEngine")
        
        # 初始化默认规则
        self._initialize_default_rules()
    
    def add_rule(self, rule: AdaptationRule) -> bool:
        """添加规则"""
        try:
            self.rules[rule.rule_id] = rule
            self.logger.debug(f"Added adaptation rule: {rule.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding rule {rule.rule_id}: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        try:
            if rule_id in self.rules:
                del self.rules[rule_id]
                self.logger.debug(f"Removed adaptation rule: {rule_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing rule {rule_id}: {e}")
            return False
    
    def evaluate_rules(
        self,
        context: AdaptationContext,
        scope: Optional[AdaptationScope] = None
    ) -> List[AdaptationRule]:
        """评估规则"""
        applicable_rules = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # 检查范围过滤
            if scope and rule.scope != scope:
                continue
            
            # 评估条件
            if self._evaluate_conditions(rule.conditions, context):
                applicable_rules.append(rule)
        
        # 按优先级排序
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        return applicable_rules
    
    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: AdaptationContext
    ) -> bool:
        """评估条件"""
        try:
            for condition_type, condition_value in conditions.items():
                if condition_type == "user_type":
                    user_type = context.user_profile.get("type")
                    if user_type != condition_value:
                        return False
                
                elif condition_type == "device_type":
                    device_type = context.device_info.get("type")
                    if device_type != condition_value:
                        return False
                
                elif condition_type == "screen_size":
                    screen_width = context.device_info.get("screen_width", 0)
                    if condition_value == "small" and screen_width >= 768:
                        return False
                    elif condition_value == "medium" and (screen_width < 768 or screen_width >= 1200):
                        return False
                    elif condition_value == "large" and screen_width < 1200:
                        return False
                
                elif condition_type == "accessibility_needs":
                    needs = context.accessibility_requirements.get("needs", [])
                    if condition_value not in needs:
                        return False
                
                elif condition_type == "performance_level":
                    performance = context.performance_constraints.get("level", "medium")
                    if performance != condition_value:
                        return False
                
                elif condition_type == "time_of_day":
                    current_hour = datetime.now().hour
                    if condition_value == "morning" and not (6 <= current_hour < 12):
                        return False
                    elif condition_value == "afternoon" and not (12 <= current_hour < 18):
                        return False
                    elif condition_value == "evening" and not (18 <= current_hour < 24):
                        return False
                    elif condition_value == "night" and not (0 <= current_hour < 6):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {e}")
            return False
    
    def _initialize_default_rules(self) -> None:
        """初始化默认规则"""
        
        # 移动端适配规则
        mobile_rule = AdaptationRule(
            rule_id="mobile_adaptation",
            name="移动端界面适配",
            description="针对移动设备优化界面布局和交互",
            scope=AdaptationScope.LAYOUT,
            strategy=AdaptationStrategy.MODERATE,
            conditions={
                "device_type": "mobile",
                "screen_size": "small"
            },
            actions={
                "collapse_sidebar": True,
                "increase_touch_targets": True,
                "simplify_navigation": True,
                "reduce_content_density": True
            },
            priority=80
        )
        
        # 暗色主题规则
        dark_theme_rule = AdaptationRule(
            rule_id="dark_theme_evening",
            name="晚间暗色主题",
            description="在晚间时段自动切换到暗色主题",
            scope=AdaptationScope.THEME,
            strategy=AdaptationStrategy.CONSERVATIVE,
            conditions={
                "time_of_day": "evening"
            },
            actions={
                "set_theme": "dark",
                "reduce_brightness": True,
                "increase_contrast": True
            },
            priority=60
        )
        
        # 可访问性规则
        accessibility_rule = AdaptationRule(
            rule_id="high_contrast_accessibility",
            name="高对比度可访问性",
            description="为视觉障碍用户提供高对比度界面",
            scope=AdaptationScope.ACCESSIBILITY,
            strategy=AdaptationStrategy.AGGRESSIVE,
            conditions={
                "accessibility_needs": "high_contrast"
            },
            actions={
                "set_theme": "high_contrast",
                "increase_font_size": True,
                "bold_text": True,
                "remove_animations": True
            },
            priority=90
        )
        
        # 性能优化规则
        performance_rule = AdaptationRule(
            rule_id="low_performance_optimization",
            name="低性能设备优化",
            description="为低性能设备减少资源消耗",
            scope=AdaptationScope.PERFORMANCE,
            strategy=AdaptationStrategy.AGGRESSIVE,
            conditions={
                "performance_level": "low"
            },
            actions={
                "disable_animations": True,
                "reduce_image_quality": True,
                "lazy_load_components": True,
                "minimize_effects": True
            },
            priority=85
        )
        
        # 专家用户规则
        expert_user_rule = AdaptationRule(
            rule_id="expert_user_interface",
            name="专家用户界面",
            description="为专家用户提供更多功能和快捷操作",
            scope=AdaptationScope.COMPONENT,
            strategy=AdaptationStrategy.MODERATE,
            conditions={
                "user_type": "expert"
            },
            actions={
                "show_advanced_controls": True,
                "enable_keyboard_shortcuts": True,
                "add_quick_actions": True,
                "show_detailed_info": True
            },
            priority=70
        )
        
        # 添加规则
        for rule in [mobile_rule, dark_theme_rule, accessibility_rule, performance_rule, expert_user_rule]:
            self.add_rule(rule)


class UIConfigurationAdapter:
    """UI配置适配器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.UIConfigurationAdapter")
    
    def adapt_layout(
        self,
        layout_config: Dict[str, Any],
        actions: Dict[str, Any],
        context: AdaptationContext
    ) -> Dict[str, Any]:
        """适配布局配置"""
        adapted_layout = copy.deepcopy(layout_config)
        
        try:
            # 侧边栏折叠
            if actions.get("collapse_sidebar"):
                adapted_layout["sidebar_collapsed"] = True
                adapted_layout["sidebar_width"] = "60px"
            
            # 简化导航
            if actions.get("simplify_navigation"):
                adapted_layout["header_visible"] = True
                adapted_layout["breadcrumb_visible"] = False
            
            # 减少内容密度
            if actions.get("reduce_content_density"):
                adapted_layout["content_padding"] = "large"
                adapted_layout["component_spacing"] = "large"
            
            # 增加触摸目标
            if actions.get("increase_touch_targets"):
                adapted_layout["min_touch_target"] = "44px"
                adapted_layout["button_padding"] = "large"
            
            self.logger.debug("Layout configuration adapted")
            return adapted_layout
            
        except Exception as e:
            self.logger.error(f"Error adapting layout: {e}")
            return layout_config
    
    def adapt_theme(
        self,
        theme_config: Dict[str, Any],
        actions: Dict[str, Any],
        context: AdaptationContext
    ) -> Dict[str, Any]:
        """适配主题配置"""
        adapted_theme = copy.deepcopy(theme_config)
        
        try:
            # 设置主题
            if actions.get("set_theme"):
                adapted_theme["name"] = actions["set_theme"]
                adapted_theme["type"] = ThemeType(actions["set_theme"])
            
            # 调整亮度
            if actions.get("reduce_brightness"):
                # 降低背景亮度
                if "colors" in adapted_theme:
                    adapted_theme["colors"]["background"] = "#1a1a1a"
                    adapted_theme["colors"]["surface"] = "#2a2a2a"
            
            # 增加对比度
            if actions.get("increase_contrast"):
                if "colors" in adapted_theme:
                    adapted_theme["colors"]["text"] = "#ffffff"
                    adapted_theme["colors"]["border"] = "#555555"
            
            # 增加字体大小
            if actions.get("increase_font_size"):
                if "typography" in adapted_theme:
                    adapted_theme["typography"]["base_size"] = "16px"
                    adapted_theme["typography"]["scale_factor"] = 1.2
            
            # 粗体文本
            if actions.get("bold_text"):
                if "typography" in adapted_theme:
                    adapted_theme["typography"]["font_weight"] = "600"
            
            self.logger.debug("Theme configuration adapted")
            return adapted_theme
            
        except Exception as e:
            self.logger.error(f"Error adapting theme: {e}")
            return theme_config
    
    def adapt_components(
        self,
        components: List[Dict[str, Any]],
        actions: Dict[str, Any],
        context: AdaptationContext
    ) -> List[Dict[str, Any]]:
        """适配组件配置"""
        adapted_components = copy.deepcopy(components)
        
        try:
            for component in adapted_components:
                # 显示高级控件
                if actions.get("show_advanced_controls"):
                    if component.get("type") == "button":
                        component.setdefault("props", {})["show_tooltip"] = True
                    elif component.get("type") == "input":
                        component.setdefault("props", {})["show_validation"] = True
                
                # 启用键盘快捷键
                if actions.get("enable_keyboard_shortcuts"):
                    component.setdefault("props", {})["keyboard_shortcuts"] = True
                
                # 添加快速操作
                if actions.get("add_quick_actions"):
                    if component.get("type") == "card":
                        component.setdefault("props", {})["quick_actions"] = [
                            {"type": "edit", "shortcut": "e"},
                            {"type": "delete", "shortcut": "d"}
                        ]
                
                # 显示详细信息
                if actions.get("show_detailed_info"):
                    component.setdefault("props", {})["show_metadata"] = True
                
                # 禁用动画
                if actions.get("disable_animations") or actions.get("remove_animations"):
                    if "style" in component:
                        component["style"]["transition"] = "none"
                        component["style"]["animation"] = "none"
                
                # 懒加载
                if actions.get("lazy_load_components"):
                    component.setdefault("props", {})["lazy_load"] = True
                
                # 最小化效果
                if actions.get("minimize_effects"):
                    if "style" in component:
                        component["style"]["box_shadow"] = "none"
                        component["style"]["border_radius"] = "2px"
            
            self.logger.debug(f"Adapted {len(adapted_components)} components")
            return adapted_components
            
        except Exception as e:
            self.logger.error(f"Error adapting components: {e}")
            return components
    
    def adapt_accessibility(
        self,
        ui_config: Dict[str, Any],
        actions: Dict[str, Any],
        context: AdaptationContext
    ) -> Dict[str, Any]:
        """适配可访问性配置"""
        adapted_config = copy.deepcopy(ui_config)
        
        try:
            # 设置可访问性选项
            accessibility_options = adapted_config.setdefault("accessibility", {})
            
            if actions.get("high_contrast"):
                accessibility_options["high_contrast"] = True
            
            if actions.get("large_text"):
                accessibility_options["large_text"] = True
            
            if actions.get("keyboard_navigation"):
                accessibility_options["keyboard_navigation"] = True
            
            if actions.get("screen_reader"):
                accessibility_options["screen_reader_support"] = True
            
            if actions.get("reduce_motion"):
                accessibility_options["reduce_motion"] = True
            
            # 为所有组件添加ARIA属性
            if "components" in adapted_config:
                for component in adapted_config["components"]:
                    props = component.setdefault("props", {})
                    
                    # 添加基本ARIA属性
                    if not props.get("aria_label") and component.get("text"):
                        props["aria_label"] = component["text"]
                    
                    # 设置角色
                    if not props.get("role"):
                        comp_type = component.get("type")
                        if comp_type == "button":
                            props["role"] = "button"
                        elif comp_type == "input":
                            props["role"] = "textbox"
                        elif comp_type == "card":
                            props["role"] = "article"
                    
                    # 设置tabindex
                    if props.get("tabindex") is None:
                        if comp_type in ["button", "input", "select", "textarea"]:
                            props["tabindex"] = 0
            
            self.logger.debug("Accessibility configuration adapted")
            return adapted_config
            
        except Exception as e:
            self.logger.error(f"Error adapting accessibility: {e}")
            return ui_config


class SmartUIAdapter:
    """智能UI适配器主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 子组件
        self.rule_engine = RuleEngine()
        self.config_adapter = UIConfigurationAdapter()
        
        # 适配缓存
        self.adaptation_cache = AsyncCache(max_size=50, ttl=300)  # 5分钟缓存
        
        # 适配历史
        self.adaptation_history: List[AdaptationResult] = []
        self.max_history_size = 100
        
        # 性能监控
        self.performance_metrics: Dict[str, float] = {}
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        self.logger.info("Smart UI Adapter initialized")
    
    @log_execution_time()
    async def adapt_ui_configuration(
        self,
        ui_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """适配UI配置"""
        try:
            start_time = time.time()
            
            # 解析适配上下文
            adaptation_context = self._parse_adaptation_context(context)
            
            # 生成缓存键
            cache_key = self._generate_cache_key(ui_config, adaptation_context)
            
            # 尝试从缓存获取
            cached_result = await self.adaptation_cache.get(cache_key)
            if cached_result:
                return {
                    "success": True,
                    "adapted_config": cached_result["adapted_config"],
                    "adaptation_result": cached_result,
                    "from_cache": True,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 执行适配
            adaptation_result = await self._execute_adaptation(ui_config, adaptation_context)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            adaptation_result.execution_time = execution_time
            
            # 缓存结果
            await self.adaptation_cache.set(cache_key, asdict(adaptation_result))
            
            # 记录历史
            self._record_adaptation_history(adaptation_result)
            
            # 发布适配事件
            await publish_event(
                event_type=EventBusEventType.UI_ADAPTED,
                data={
                    "result_id": adaptation_result.result_id,
                    "adaptation_score": adaptation_result.adaptation_score,
                    "applied_rules": adaptation_result.applied_rules,
                    "execution_time": execution_time
                },
                source="ui_adapter"
            )
            
            return {
                "success": True,
                "adapted_config": adaptation_result.adapted_config,
                "adaptation_result": asdict(adaptation_result),
                "from_cache": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error adapting UI configuration: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_adaptation(
        self,
        ui_config: Dict[str, Any],
        context: AdaptationContext
    ) -> AdaptationResult:
        """执行适配"""
        
        # 评估适用的规则
        applicable_rules = self.rule_engine.evaluate_rules(context)
        
        # 初始化适配结果
        adapted_config = copy.deepcopy(ui_config)
        applied_rules = []
        changes_summary = {
            "layout_changes": [],
            "theme_changes": [],
            "component_changes": [],
            "accessibility_changes": []
        }
        
        # 应用规则
        for rule in applicable_rules:
            try:
                # 根据规则范围应用适配
                if rule.scope == AdaptationScope.LAYOUT:
                    if "layout" in adapted_config:
                        original_layout = copy.deepcopy(adapted_config["layout"])
                        adapted_config["layout"] = self.config_adapter.adapt_layout(
                            adapted_config["layout"], rule.actions, context
                        )
                        if adapted_config["layout"] != original_layout:
                            changes_summary["layout_changes"].append(rule.name)
                
                elif rule.scope == AdaptationScope.THEME:
                    if "theme" in adapted_config:
                        original_theme = copy.deepcopy(adapted_config["theme"])
                        adapted_config["theme"] = self.config_adapter.adapt_theme(
                            adapted_config["theme"], rule.actions, context
                        )
                        if adapted_config["theme"] != original_theme:
                            changes_summary["theme_changes"].append(rule.name)
                
                elif rule.scope == AdaptationScope.COMPONENT:
                    if "components" in adapted_config:
                        original_components = copy.deepcopy(adapted_config["components"])
                        adapted_config["components"] = self.config_adapter.adapt_components(
                            adapted_config["components"], rule.actions, context
                        )
                        if adapted_config["components"] != original_components:
                            changes_summary["component_changes"].append(rule.name)
                
                elif rule.scope == AdaptationScope.ACCESSIBILITY:
                    original_config = copy.deepcopy(adapted_config)
                    adapted_config = self.config_adapter.adapt_accessibility(
                        adapted_config, rule.actions, context
                    )
                    if adapted_config != original_config:
                        changes_summary["accessibility_changes"].append(rule.name)
                
                elif rule.scope == AdaptationScope.GLOBAL:
                    # 全局适配，可能影响多个方面
                    for action_key, action_value in rule.actions.items():
                        if action_key.startswith("layout_"):
                            # 布局相关的全局设置
                            adapted_config.setdefault("layout", {})[action_key[7:]] = action_value
                        elif action_key.startswith("theme_"):
                            # 主题相关的全局设置
                            adapted_config.setdefault("theme", {})[action_key[6:]] = action_value
                
                applied_rules.append(rule.rule_id)
                
            except Exception as e:
                self.logger.error(f"Error applying rule {rule.rule_id}: {e}")
                continue
        
        # 计算适配评分
        adaptation_score = self._calculate_adaptation_score(
            ui_config, adapted_config, applied_rules, context
        )
        
        # 计算性能影响
        performance_impact = self._calculate_performance_impact(
            ui_config, adapted_config, applied_rules
        )
        
        return AdaptationResult(
            result_id=generate_id("adapt_result_"),
            original_config=ui_config,
            adapted_config=adapted_config,
            applied_rules=applied_rules,
            adaptation_score=adaptation_score,
            performance_impact=performance_impact,
            changes_summary=changes_summary,
            execution_time=0.0,  # 将在调用处设置
            timestamp=datetime.now()
        )
    
    def _calculate_adaptation_score(
        self,
        original_config: Dict[str, Any],
        adapted_config: Dict[str, Any],
        applied_rules: List[str],
        context: AdaptationContext
    ) -> float:
        """计算适配评分"""
        try:
            score = 0.0
            max_score = 0.0
            
            # 基于应用的规则数量
            rule_score = min(len(applied_rules) * 0.1, 0.3)
            score += rule_score
            max_score += 0.3
            
            # 基于配置变化程度
            change_score = self._calculate_change_score(original_config, adapted_config)
            score += change_score * 0.4
            max_score += 0.4
            
            # 基于上下文匹配度
            context_score = self._calculate_context_match_score(adapted_config, context)
            score += context_score * 0.3
            max_score += 0.3
            
            return score / max_score if max_score > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptation score: {e}")
            return 0.0
    
    def _calculate_change_score(
        self,
        original_config: Dict[str, Any],
        adapted_config: Dict[str, Any]
    ) -> float:
        """计算配置变化评分"""
        try:
            total_changes = 0
            total_items = 0
            
            # 比较布局变化
            if "layout" in original_config and "layout" in adapted_config:
                layout_changes = sum(
                    1 for key in original_config["layout"]
                    if original_config["layout"].get(key) != adapted_config["layout"].get(key)
                )
                total_changes += layout_changes
                total_items += len(original_config["layout"])
            
            # 比较主题变化
            if "theme" in original_config and "theme" in adapted_config:
                theme_changes = sum(
                    1 for key in original_config["theme"]
                    if original_config["theme"].get(key) != adapted_config["theme"].get(key)
                )
                total_changes += theme_changes
                total_items += len(original_config["theme"])
            
            # 比较组件变化
            if "components" in original_config and "components" in adapted_config:
                component_changes = 0
                original_components = original_config["components"]
                adapted_components = adapted_config["components"]
                
                for i, orig_comp in enumerate(original_components):
                    if i < len(adapted_components):
                        adapted_comp = adapted_components[i]
                        if orig_comp != adapted_comp:
                            component_changes += 1
                
                total_changes += component_changes
                total_items += len(original_components)
            
            return total_changes / total_items if total_items > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating change score: {e}")
            return 0.0
    
    def _calculate_context_match_score(
        self,
        adapted_config: Dict[str, Any],
        context: AdaptationContext
    ) -> float:
        """计算上下文匹配评分"""
        try:
            score = 0.0
            checks = 0
            
            # 检查设备适配
            device_type = context.device_info.get("type")
            if device_type == "mobile":
                layout = adapted_config.get("layout", {})
                if layout.get("sidebar_collapsed"):
                    score += 1
                checks += 1
            
            # 检查可访问性适配
            accessibility_needs = context.accessibility_requirements.get("needs", [])
            if "high_contrast" in accessibility_needs:
                theme = adapted_config.get("theme", {})
                if theme.get("name") == "high_contrast":
                    score += 1
                checks += 1
            
            # 检查性能适配
            performance_level = context.performance_constraints.get("level")
            if performance_level == "low":
                # 检查是否禁用了动画
                components = adapted_config.get("components", [])
                disabled_animations = sum(
                    1 for comp in components
                    if comp.get("style", {}).get("animation") == "none"
                )
                if disabled_animations > 0:
                    score += 1
                checks += 1
            
            return score / checks if checks > 0 else 1.0
            
        except Exception as e:
            self.logger.error(f"Error calculating context match score: {e}")
            return 0.0
    
    def _calculate_performance_impact(
        self,
        original_config: Dict[str, Any],
        adapted_config: Dict[str, Any],
        applied_rules: List[str]
    ) -> float:
        """计算性能影响"""
        try:
            impact = 0.0
            
            # 基于应用的规则数量
            impact += len(applied_rules) * 0.05
            
            # 基于组件数量变化
            original_components = len(original_config.get("components", []))
            adapted_components = len(adapted_config.get("components", []))
            component_change_ratio = abs(adapted_components - original_components) / max(original_components, 1)
            impact += component_change_ratio * 0.3
            
            # 基于样式复杂度变化
            original_styles = sum(
                len(comp.get("style", {})) for comp in original_config.get("components", [])
            )
            adapted_styles = sum(
                len(comp.get("style", {})) for comp in adapted_config.get("components", [])
            )
            style_change_ratio = abs(adapted_styles - original_styles) / max(original_styles, 1)
            impact += style_change_ratio * 0.2
            
            return min(impact, 1.0)  # 限制在0-1范围内
            
        except Exception as e:
            self.logger.error(f"Error calculating performance impact: {e}")
            return 0.0
    
    def _parse_adaptation_context(self, context: Dict[str, Any]) -> AdaptationContext:
        """解析适配上下文"""
        return AdaptationContext(
            context_id=context.get("context_id"),
            user_profile=context.get("user_profile", {}),
            device_info=context.get("device_info", {}),
            environment_info=context.get("environment_info", {}),
            performance_constraints=context.get("performance_constraints", {}),
            accessibility_requirements=context.get("accessibility_requirements", {}),
            current_ui_config=context.get("current_ui_config", {}),
            adaptation_history=context.get("adaptation_history", []),
            timestamp=datetime.now()
        )
    
    def _generate_cache_key(
        self,
        ui_config: Dict[str, Any],
        context: AdaptationContext
    ) -> str:
        """生成缓存键"""
        import hashlib
        
        cache_parts = [
            str(ui_config),
            str(context.user_profile),
            str(context.device_info),
            str(context.accessibility_requirements),
            str(context.performance_constraints)
        ]
        
        cache_string = "|".join(cache_parts)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"adapt_{cache_hash}"
    
    def _record_adaptation_history(self, result: AdaptationResult) -> None:
        """记录适配历史"""
        self.adaptation_history.append(result)
        
        # 限制历史记录大小
        if len(self.adaptation_history) > self.max_history_size:
            self.adaptation_history = self.adaptation_history[-self.max_history_size:]
    
    @event_handler(EventBusEventType.USER_BEHAVIOR_CHANGE)
    async def handle_user_behavior_analyzed(self, event: EventBusEvent) -> None:
        """处理用户行为分析事件"""
        behavior_data = event.data
        user_profile = behavior_data.get("user_profile")
        
        if user_profile:
            # 基于用户行为分析结果触发UI适配
            self.logger.debug("Triggering UI adaptation based on user behavior analysis")
    
    @event_handler(EventBusEventType.DECISION_MADE)
    async def handle_decision_made(self, event: EventBusEvent) -> None:
        """处理决策事件"""
        decision_data = event.data
        decision_type = decision_data.get("decision_type")
        
        if decision_type and decision_type.startswith("ui_"):
            # UI相关的决策，触发适配
            self.logger.debug(f"Triggering UI adaptation based on decision: {decision_type}")
    
    async def get_adaptation_rules(self) -> List[Dict[str, Any]]:
        """获取适配规则"""
        return [asdict(rule) for rule in self.rule_engine.rules.values()]
    
    async def add_adaptation_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """添加适配规则"""
        try:
            rule = AdaptationRule(**rule_data)
            success = self.rule_engine.add_rule(rule)
            
            return {
                "success": success,
                "rule_id": rule.rule_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error adding adaptation rule: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_adaptation_statistics(self) -> Dict[str, Any]:
        """获取适配统计信息"""
        return {
            "total_adaptations": len(self.adaptation_history),
            "cache_size": len(self.adaptation_cache._cache) if hasattr(self.adaptation_cache, '_cache') else 0,
            "active_rules": len([r for r in self.rule_engine.rules.values() if r.enabled]),
            "average_adaptation_score": sum(r.adaptation_score for r in self.adaptation_history) / len(self.adaptation_history) if self.adaptation_history else 0.0,
            "average_performance_impact": sum(r.performance_impact for r in self.adaptation_history) / len(self.adaptation_history) if self.adaptation_history else 0.0
        }
    
    async def cleanup(self) -> Dict[str, int]:
        """清理资源"""
        cleanup_stats = {
            "cleared_cache_entries": 0,
            "cleared_history_entries": 0
        }
        
        try:
            # 清理适配缓存
            await self.adaptation_cache.clear()
            cleanup_stats["cleared_cache_entries"] = 1
            
            # 清理历史记录
            history_count = len(self.adaptation_history)
            self.adaptation_history.clear()
            cleanup_stats["cleared_history_entries"] = history_count
            
            self.logger.info(f"UI Adapter cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during UI Adapter cleanup: {e}")
            return cleanup_stats

