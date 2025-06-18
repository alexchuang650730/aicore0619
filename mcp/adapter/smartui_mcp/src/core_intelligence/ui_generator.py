"""
SmartUI MCP - UI生成器

实现智能的用户界面生成系统，基于用户分析和决策引擎的结果，
动态生成和优化用户界面配置。
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import copy

from ..common import (
    IUIGenerator, EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    UIConfiguration, UIComponent, ComponentType, LayoutType, ThemeType,
    ComponentProps, ComponentStyle, LayoutConfig, ThemeConfig,
    create_button_component, create_input_component, create_card_component,
    create_default_theme, create_default_layout, create_basic_ui_configuration
)


class GenerationStrategy(str, Enum):
    """生成策略枚举"""
    TEMPLATE_BASED = "template_based"
    RULE_BASED = "rule_based"
    AI_GENERATED = "ai_generated"
    HYBRID = "hybrid"
    USER_DRIVEN = "user_driven"
    ADAPTIVE = "adaptive"


class OptimizationTarget(str, Enum):
    """优化目标枚举"""
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    USER_EXPERIENCE = "user_experience"
    CONVERSION = "conversion"
    ENGAGEMENT = "engagement"
    EFFICIENCY = "efficiency"
    AESTHETICS = "aesthetics"


@dataclass
class GenerationContext:
    """生成上下文"""
    context_id: str
    user_profile: Dict[str, Any]
    device_info: Dict[str, Any]
    current_ui_state: Dict[str, Any]
    user_intents: List[Dict[str, Any]]
    performance_constraints: Dict[str, Any]
    accessibility_requirements: List[str]
    business_goals: List[str]
    timestamp: datetime
    
    def __post_init__(self):
        if self.context_id is None:
            self.context_id = generate_id("gen_context_")


@dataclass
class UITemplate:
    """UI模板"""
    template_id: str
    name: str
    description: str
    category: str
    base_configuration: UIConfiguration
    variables: Dict[str, Any]
    conditions: Dict[str, str]
    tags: List[str]
    created_at: datetime
    
    def __post_init__(self):
        if self.template_id is None:
            self.template_id = generate_id("template_")


@dataclass
class GenerationRule:
    """生成规则"""
    rule_id: str
    name: str
    description: str
    condition: str
    action: str
    priority: int
    enabled: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.rule_id is None:
            self.rule_id = generate_id("gen_rule_")
        if self.tags is None:
            self.tags = []


@dataclass
class GenerationResult:
    """生成结果"""
    result_id: str
    ui_configuration: UIConfiguration
    generation_strategy: GenerationStrategy
    optimization_targets: List[OptimizationTarget]
    confidence: float
    generation_time: float
    metadata: Dict[str, Any]
    alternatives: List[UIConfiguration]
    
    def __post_init__(self):
        if self.result_id is None:
            self.result_id = generate_id("gen_result_")


class TemplateEngine:
    """模板引擎"""
    
    def __init__(self):
        self.templates: Dict[str, UITemplate] = {}
        self.template_categories: Dict[str, List[str]] = {}
        self.template_cache = AsyncCache(max_size=100, ttl=1800)  # 30分钟缓存
    
    def register_template(self, template: UITemplate) -> None:
        """注册模板"""
        self.templates[template.template_id] = template
        
        # 更新分类索引
        category = template.category
        if category not in self.template_categories:
            self.template_categories[category] = []
        self.template_categories[category].append(template.template_id)
    
    def unregister_template(self, template_id: str) -> bool:
        """取消注册模板"""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        
        # 从分类索引中移除
        if template.category in self.template_categories:
            self.template_categories[template.category].remove(template_id)
            if not self.template_categories[template.category]:
                del self.template_categories[template.category]
        
        del self.templates[template_id]
        return True
    
    async def find_templates(
        self,
        context: GenerationContext,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[UITemplate]:
        """查找匹配的模板"""
        cache_key = f"find_templates_{category}_{tags}_{context.context_id}"
        
        # 尝试从缓存获取
        cached_result = await self.template_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        matching_templates = []
        
        for template in self.templates.values():
            # 分类过滤
            if category and template.category != category:
                continue
            
            # 标签过滤
            if tags and not any(tag in template.tags for tag in tags):
                continue
            
            # 条件评估
            if self._evaluate_template_conditions(template, context):
                matching_templates.append(template)
        
        # 按优先级排序（这里可以添加更复杂的排序逻辑）
        matching_templates.sort(key=lambda t: len(t.tags), reverse=True)
        
        # 缓存结果
        await self.template_cache.set(cache_key, matching_templates)
        
        return matching_templates
    
    async def apply_template(
        self,
        template: UITemplate,
        context: GenerationContext,
        variables: Optional[Dict[str, Any]] = None
    ) -> UIConfiguration:
        """应用模板"""
        # 合并变量
        template_variables = copy.deepcopy(template.variables)
        if variables:
            template_variables.update(variables)
        
        # 从上下文中提取变量
        context_variables = self._extract_context_variables(context)
        template_variables.update(context_variables)
        
        # 克隆基础配置
        ui_config = copy.deepcopy(template.base_configuration)
        
        # 应用变量替换
        ui_config = self._apply_variable_substitution(ui_config, template_variables)
        
        # 应用上下文优化
        ui_config = await self._apply_context_optimizations(ui_config, context)
        
        return ui_config
    
    def _evaluate_template_conditions(
        self,
        template: UITemplate,
        context: GenerationContext
    ) -> bool:
        """评估模板条件"""
        if not template.conditions:
            return True
        
        try:
            # 构建安全的评估环境
            safe_dict = {
                "context": context,
                "user_profile": context.user_profile,
                "device_info": context.device_info,
                "intents": context.user_intents,
                "len": len,
                "any": any,
                "all": all,
            }
            
            # 评估所有条件
            for condition_name, condition_expr in template.conditions.items():
                result = eval(condition_expr, {"__builtins__": {}}, safe_dict)
                if not result:
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error evaluating template conditions: {e}")
            return False
    
    def _extract_context_variables(self, context: GenerationContext) -> Dict[str, Any]:
        """从上下文中提取变量"""
        variables = {}
        
        # 用户信息
        user_profile = context.user_profile
        variables.update({
            "user_name": user_profile.get("name", "User"),
            "user_role": user_profile.get("role", "user"),
            "user_theme_preference": user_profile.get("preferences", {}).get("ui_theme", "auto"),
            "user_language": user_profile.get("language", "en"),
        })
        
        # 设备信息
        device_info = context.device_info
        variables.update({
            "device_type": device_info.get("type", "desktop"),
            "screen_width": device_info.get("screen_width", 1920),
            "screen_height": device_info.get("screen_height", 1080),
            "is_mobile": device_info.get("type") == "mobile",
            "is_tablet": device_info.get("type") == "tablet",
            "is_desktop": device_info.get("type") == "desktop",
        })
        
        # 时间信息
        now = datetime.now()
        variables.update({
            "current_hour": now.hour,
            "is_daytime": 6 <= now.hour <= 18,
            "is_nighttime": now.hour >= 20 or now.hour <= 6,
            "current_date": now.strftime("%Y-%m-%d"),
            "current_time": now.strftime("%H:%M:%S"),
        })
        
        # 意图信息
        if context.user_intents:
            primary_intent = context.user_intents[0] if context.user_intents else {}
            variables.update({
                "primary_intent": primary_intent.get("intent_type", "unknown"),
                "intent_confidence": primary_intent.get("confidence", 0.0),
            })
        
        return variables
    
    def _apply_variable_substitution(
        self,
        ui_config: UIConfiguration,
        variables: Dict[str, Any]
    ) -> UIConfiguration:
        """应用变量替换"""
        # 这里应该实现递归的变量替换逻辑
        # 简化实现，只处理字符串类型的替换
        
        def substitute_value(value):
            if isinstance(value, str):
                # 简单的变量替换 ${variable_name}
                for var_name, var_value in variables.items():
                    placeholder = f"${{{var_name}}}"
                    if placeholder in value:
                        value = value.replace(placeholder, str(var_value))
                return value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value
        
        # 应用替换
        config_dict = asdict(ui_config)
        substituted_dict = substitute_value(config_dict)
        
        # 重新构建UIConfiguration对象
        # 这里需要更复杂的逻辑来正确重建对象
        # 简化实现，直接返回原配置
        return ui_config
    
    async def _apply_context_optimizations(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext
    ) -> UIConfiguration:
        """应用上下文优化"""
        # 可访问性优化
        if context.accessibility_requirements:
            ui_config = self._apply_accessibility_optimizations(ui_config, context.accessibility_requirements)
        
        # 性能优化
        if context.performance_constraints:
            ui_config = self._apply_performance_optimizations(ui_config, context.performance_constraints)
        
        # 设备优化
        ui_config = self._apply_device_optimizations(ui_config, context.device_info)
        
        return ui_config
    
    def _apply_accessibility_optimizations(
        self,
        ui_config: UIConfiguration,
        requirements: List[str]
    ) -> UIConfiguration:
        """应用可访问性优化"""
        if "high_contrast" in requirements:
            # 应用高对比度主题
            ui_config.theme.name = "high_contrast"
            ui_config.theme.colors["primary"] = "#000000"
            ui_config.theme.colors["background"] = "#FFFFFF"
        
        if "large_text" in requirements:
            # 增大字体大小
            ui_config.theme.typography["base_size"] = "18px"
        
        if "keyboard_navigation" in requirements:
            # 增强键盘导航
            for component in ui_config.components:
                if component.props is None:
                    component.props = ComponentProps()
                component.props.tabindex = 0
        
        return ui_config
    
    def _apply_performance_optimizations(
        self,
        ui_config: UIConfiguration,
        constraints: Dict[str, Any]
    ) -> UIConfiguration:
        """应用性能优化"""
        max_components = constraints.get("max_components", 50)
        
        # 限制组件数量
        if len(ui_config.components) > max_components:
            ui_config.components = ui_config.components[:max_components]
        
        # 禁用动画（如果性能要求严格）
        if constraints.get("disable_animations", False):
            ui_config.theme.animations["enabled"] = False
        
        return ui_config
    
    def _apply_device_optimizations(
        self,
        ui_config: UIConfiguration,
        device_info: Dict[str, Any]
    ) -> UIConfiguration:
        """应用设备优化"""
        device_type = device_info.get("type", "desktop")
        
        if device_type == "mobile":
            # 移动设备优化
            ui_config.layout.type = LayoutType.MOBILE
            ui_config.layout.sidebar_collapsed = True
            
            # 增大触摸目标
            for component in ui_config.components:
                if component.type in [ComponentType.BUTTON, ComponentType.LINK]:
                    if component.style is None:
                        component.style = ComponentStyle()
                    component.style.min_height = "44px"
        
        elif device_type == "tablet":
            # 平板设备优化
            ui_config.layout.type = LayoutType.GRID
            ui_config.layout.columns = 2
        
        return ui_config


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, GenerationRule] = {}
        self.rule_groups: Dict[str, List[str]] = {}
    
    def add_rule(self, rule: GenerationRule, group: Optional[str] = None) -> None:
        """添加规则"""
        self.rules[rule.rule_id] = rule
        
        if group:
            if group not in self.rule_groups:
                self.rule_groups[group] = []
            self.rule_groups[group].append(rule.rule_id)
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        if rule_id not in self.rules:
            return False
        
        # 从所有组中移除
        for group_rules in self.rule_groups.values():
            if rule_id in group_rules:
                group_rules.remove(rule_id)
        
        del self.rules[rule_id]
        return True
    
    async def apply_rules(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext,
        group: Optional[str] = None
    ) -> UIConfiguration:
        """应用规则"""
        # 确定要应用的规则
        if group and group in self.rule_groups:
            rule_ids = self.rule_groups[group]
        else:
            rule_ids = list(self.rules.keys())
        
        # 按优先级排序
        sorted_rules = sorted(
            [self.rules[rid] for rid in rule_ids if rid in self.rules and self.rules[rid].enabled],
            key=lambda r: r.priority,
            reverse=True
        )
        
        # 应用每个规则
        for rule in sorted_rules:
            try:
                if self._evaluate_rule_condition(rule, context, ui_config):
                    ui_config = await self._apply_rule_action(rule, ui_config, context)
            except Exception as e:
                logging.error(f"Error applying rule {rule.rule_id}: {e}")
        
        return ui_config
    
    def _evaluate_rule_condition(
        self,
        rule: GenerationRule,
        context: GenerationContext,
        ui_config: UIConfiguration
    ) -> bool:
        """评估规则条件"""
        try:
            safe_dict = {
                "context": context,
                "ui_config": ui_config,
                "user_profile": context.user_profile,
                "device_info": context.device_info,
                "len": len,
                "any": any,
                "all": all,
            }
            
            result = eval(rule.condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
            
        except Exception as e:
            logging.error(f"Error evaluating rule condition: {e}")
            return False
    
    async def _apply_rule_action(
        self,
        rule: GenerationRule,
        ui_config: UIConfiguration,
        context: GenerationContext
    ) -> UIConfiguration:
        """应用规则动作"""
        try:
            safe_dict = {
                "context": context,
                "ui_config": ui_config,
                "user_profile": context.user_profile,
                "device_info": context.device_info,
                "add_component": self._add_component,
                "remove_component": self._remove_component,
                "modify_component": self._modify_component,
                "set_theme": self._set_theme,
                "set_layout": self._set_layout,
            }
            
            # 执行动作
            exec(rule.action, {"__builtins__": {}}, safe_dict)
            
            return ui_config
            
        except Exception as e:
            logging.error(f"Error applying rule action: {e}")
            return ui_config
    
    def _add_component(self, ui_config: UIConfiguration, component: UIComponent) -> None:
        """添加组件"""
        ui_config.components.append(component)
    
    def _remove_component(self, ui_config: UIConfiguration, component_id: str) -> None:
        """移除组件"""
        ui_config.components = [c for c in ui_config.components if c.id != component_id]
    
    def _modify_component(
        self,
        ui_config: UIConfiguration,
        component_id: str,
        modifications: Dict[str, Any]
    ) -> None:
        """修改组件"""
        for component in ui_config.components:
            if component.id == component_id:
                for key, value in modifications.items():
                    if hasattr(component, key):
                        setattr(component, key, value)
                break
    
    def _set_theme(self, ui_config: UIConfiguration, theme_config: Dict[str, Any]) -> None:
        """设置主题"""
        for key, value in theme_config.items():
            if hasattr(ui_config.theme, key):
                setattr(ui_config.theme, key, value)
    
    def _set_layout(self, ui_config: UIConfiguration, layout_config: Dict[str, Any]) -> None:
        """设置布局"""
        for key, value in layout_config.items():
            if hasattr(ui_config.layout, key):
                setattr(ui_config.layout, key, value)


class AIGenerator:
    """AI生成器"""
    
    def __init__(self):
        self.generation_models: Dict[str, Any] = {}
        self.generation_cache = AsyncCache(max_size=50, ttl=3600)  # 1小时缓存
    
    def register_model(self, model_name: str, model: Any) -> None:
        """注册AI模型"""
        self.generation_models[model_name] = model
    
    async def generate_ui(
        self,
        context: GenerationContext,
        requirements: Dict[str, Any]
    ) -> Optional[UIConfiguration]:
        """使用AI生成UI"""
        cache_key = f"ai_gen_{context.context_id}_{hash(str(requirements))}"
        
        # 尝试从缓存获取
        cached_result = await self.generation_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # 这里应该调用实际的AI模型
            # 简化实现，返回基础配置
            ui_config = create_basic_ui_configuration()
            
            # 基于上下文调整配置
            ui_config = await self._customize_ai_generated_ui(ui_config, context, requirements)
            
            # 缓存结果
            await self.generation_cache.set(cache_key, ui_config)
            
            return ui_config
            
        except Exception as e:
            logging.error(f"Error in AI generation: {e}")
            return None
    
    async def _customize_ai_generated_ui(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext,
        requirements: Dict[str, Any]
    ) -> UIConfiguration:
        """定制AI生成的UI"""
        # 基于用户偏好调整主题
        user_theme = context.user_profile.get("preferences", {}).get("ui_theme", "auto")
        if user_theme != "auto":
            ui_config.theme.name = user_theme
        
        # 基于设备类型调整布局
        device_type = context.device_info.get("type", "desktop")
        if device_type == "mobile":
            ui_config.layout.type = LayoutType.MOBILE
        elif device_type == "tablet":
            ui_config.layout.type = LayoutType.GRID
        
        # 基于用户意图添加相关组件
        for intent in context.user_intents:
            intent_type = intent.get("intent_type", "")
            if intent_type == "search":
                # 添加搜索组件
                search_component = create_input_component(
                    component_id="search_input",
                    placeholder="Search...",
                    input_type="search"
                )
                ui_config.components.insert(0, search_component)
            elif intent_type == "create":
                # 添加创建按钮
                create_button = create_button_component(
                    component_id="create_button",
                    text="Create New",
                    variant="primary"
                )
                ui_config.components.append(create_button)
        
        return ui_config


class SmartUIGenerator(IUIGenerator):
    """SmartUI生成器实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 子组件
        self.template_engine = TemplateEngine()
        self.rule_engine = RuleEngine()
        self.ai_generator = AIGenerator()
        
        # 生成历史
        self.generation_history: List[GenerationResult] = []
        
        # 性能监控
        self.performance_metrics: Dict[str, float] = {}
        
        # 缓存
        self.generation_cache = AsyncCache(max_size=200, ttl=600)  # 10分钟缓存
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        # 初始化默认模板和规则
        self._initialize_default_templates()
        self._initialize_default_rules()
        
        self.logger.info("SmartUI Generator initialized")
    
    @log_execution_time()
    async def generate_ui_configuration(
        self,
        context: Dict[str, Any],
        strategy: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成UI配置"""
        try:
            start_time = time.time()
            
            # 解析生成上下文
            gen_context = self._parse_generation_context(context)
            
            # 选择生成策略
            if strategy is None:
                strategy = self._select_generation_strategy(gen_context)
            
            generation_strategy = GenerationStrategy(strategy)
            
            # 执行生成
            ui_config = await self._execute_generation(gen_context, generation_strategy)
            
            if ui_config is None:
                return {
                    "success": False,
                    "error": "Failed to generate UI configuration",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 计算生成时间
            generation_time = time.time() - start_time
            
            # 创建生成结果
            result = GenerationResult(
                result_id=generate_id("gen_result_"),
                ui_configuration=ui_config,
                generation_strategy=generation_strategy,
                optimization_targets=[OptimizationTarget.USER_EXPERIENCE],
                confidence=0.8,
                generation_time=generation_time,
                metadata={
                    "context_id": gen_context.context_id,
                    "strategy": strategy,
                    "user_id": gen_context.user_profile.get("user_id")
                },
                alternatives=[]
            )
            
            # 记录生成历史
            self.generation_history.append(result)
            
            # 发布生成事件
            await publish_event(
                event_type=EventBusEventType.UI_GENERATED,
                data={
                    "result_id": result.result_id,
                    "strategy": strategy,
                    "generation_time": generation_time,
                    "component_count": len(ui_config.components)
                },
                source="ui_generator"
            )
            
            return {
                "success": True,
                "ui_configuration": asdict(ui_config),
                "generation_result": asdict(result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating UI configuration: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def optimize_ui_configuration(
        self,
        ui_config: Dict[str, Any],
        optimization_targets: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """优化UI配置"""
        try:
            # 解析输入
            gen_context = self._parse_generation_context(context)
            targets = [OptimizationTarget(target) for target in optimization_targets]
            
            # 重建UIConfiguration对象
            # 这里需要更复杂的逻辑来正确重建对象
            # 简化实现
            current_config = create_basic_ui_configuration()
            
            # 应用优化
            optimized_config = await self._apply_optimizations(current_config, targets, gen_context)
            
            return {
                "success": True,
                "optimized_configuration": asdict(optimized_config),
                "applied_optimizations": optimization_targets,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing UI configuration: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_ui_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """获取UI模板"""
        try:
            templates = []
            
            for template in self.template_engine.templates.values():
                # 分类过滤
                if category and template.category != category:
                    continue
                
                # 标签过滤
                if tags and not any(tag in template.tags for tag in tags):
                    continue
                
                templates.append(asdict(template))
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Error getting UI templates: {e}")
            return []
    
    async def register_ui_template(self, template_data: Dict[str, Any]) -> bool:
        """注册UI模板"""
        try:
            # 创建基础配置
            base_config = create_basic_ui_configuration()
            
            template = UITemplate(
                template_id=template_data.get("template_id"),
                name=template_data["name"],
                description=template_data.get("description", ""),
                category=template_data.get("category", "general"),
                base_configuration=base_config,
                variables=template_data.get("variables", {}),
                conditions=template_data.get("conditions", {}),
                tags=template_data.get("tags", []),
                created_at=datetime.now()
            )
            
            self.template_engine.register_template(template)
            
            self.logger.info(f"Registered UI template: {template.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering UI template: {e}")
            return False
    
    async def _execute_generation(
        self,
        context: GenerationContext,
        strategy: GenerationStrategy
    ) -> Optional[UIConfiguration]:
        """执行生成"""
        if strategy == GenerationStrategy.TEMPLATE_BASED:
            return await self._generate_from_template(context)
        elif strategy == GenerationStrategy.RULE_BASED:
            return await self._generate_from_rules(context)
        elif strategy == GenerationStrategy.AI_GENERATED:
            return await self._generate_from_ai(context)
        elif strategy == GenerationStrategy.HYBRID:
            return await self._generate_hybrid(context)
        else:
            # 默认使用模板生成
            return await self._generate_from_template(context)
    
    async def _generate_from_template(self, context: GenerationContext) -> Optional[UIConfiguration]:
        """基于模板生成"""
        # 查找匹配的模板
        templates = await self.template_engine.find_templates(context)
        
        if not templates:
            # 没有匹配的模板，使用默认模板
            return create_basic_ui_configuration()
        
        # 选择最佳模板
        best_template = templates[0]
        
        # 应用模板
        ui_config = await self.template_engine.apply_template(best_template, context)
        
        return ui_config
    
    async def _generate_from_rules(self, context: GenerationContext) -> Optional[UIConfiguration]:
        """基于规则生成"""
        # 从基础配置开始
        ui_config = create_basic_ui_configuration()
        
        # 应用生成规则
        ui_config = await self.rule_engine.apply_rules(ui_config, context)
        
        return ui_config
    
    async def _generate_from_ai(self, context: GenerationContext) -> Optional[UIConfiguration]:
        """基于AI生成"""
        requirements = {
            "user_intents": context.user_intents,
            "device_type": context.device_info.get("type", "desktop"),
            "accessibility_requirements": context.accessibility_requirements
        }
        
        ui_config = await self.ai_generator.generate_ui(context, requirements)
        
        return ui_config
    
    async def _generate_hybrid(self, context: GenerationContext) -> Optional[UIConfiguration]:
        """混合生成"""
        # 首先尝试模板生成
        ui_config = await self._generate_from_template(context)
        
        if ui_config is None:
            ui_config = create_basic_ui_configuration()
        
        # 应用规则优化
        ui_config = await self.rule_engine.apply_rules(ui_config, context)
        
        # 如果有AI模型，进一步优化
        if self.ai_generator.generation_models:
            ai_config = await self._generate_from_ai(context)
            if ai_config:
                # 合并AI生成的组件
                ui_config.components.extend(ai_config.components)
        
        return ui_config
    
    async def _apply_optimizations(
        self,
        ui_config: UIConfiguration,
        targets: List[OptimizationTarget],
        context: GenerationContext
    ) -> UIConfiguration:
        """应用优化"""
        for target in targets:
            if target == OptimizationTarget.PERFORMANCE:
                ui_config = self._optimize_for_performance(ui_config, context)
            elif target == OptimizationTarget.ACCESSIBILITY:
                ui_config = self._optimize_for_accessibility(ui_config, context)
            elif target == OptimizationTarget.USER_EXPERIENCE:
                ui_config = self._optimize_for_user_experience(ui_config, context)
            elif target == OptimizationTarget.AESTHETICS:
                ui_config = self._optimize_for_aesthetics(ui_config, context)
        
        return ui_config
    
    def _optimize_for_performance(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext
    ) -> UIConfiguration:
        """性能优化"""
        # 限制组件数量
        max_components = context.performance_constraints.get("max_components", 30)
        if len(ui_config.components) > max_components:
            ui_config.components = ui_config.components[:max_components]
        
        # 禁用复杂动画
        ui_config.theme.animations["enabled"] = False
        
        # 使用轻量级组件
        for component in ui_config.components:
            if component.type == ComponentType.RICH_TEXT_EDITOR:
                component.type = ComponentType.TEXTAREA
        
        return ui_config
    
    def _optimize_for_accessibility(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext
    ) -> UIConfiguration:
        """可访问性优化"""
        requirements = context.accessibility_requirements
        
        if "high_contrast" in requirements:
            ui_config.theme.name = "high_contrast"
        
        if "large_text" in requirements:
            ui_config.theme.typography["base_size"] = "18px"
        
        # 为所有交互元素添加适当的属性
        for component in ui_config.components:
            if component.type in [ComponentType.BUTTON, ComponentType.LINK, ComponentType.INPUT]:
                if component.props is None:
                    component.props = ComponentProps()
                component.props.tabindex = 0
                
                if not component.props.aria_label:
                    component.props.aria_label = component.text or f"{component.type} element"
        
        return ui_config
    
    def _optimize_for_user_experience(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext
    ) -> UIConfiguration:
        """用户体验优化"""
        user_profile = context.user_profile
        
        # 基于用户行为模式优化
        behavior_patterns = user_profile.get("behavior_patterns", [])
        
        if "power_user" in behavior_patterns:
            # 为专家用户添加快捷操作
            for component in ui_config.components:
                if component.type == ComponentType.BUTTON:
                    if component.props is None:
                        component.props = ComponentProps()
                    component.props.keyboard_shortcut = f"Ctrl+{component.text[0].upper()}"
        
        if "mobile_first" in behavior_patterns:
            # 移动优先优化
            ui_config.layout.type = LayoutType.MOBILE
            for component in ui_config.components:
                if component.style is None:
                    component.style = ComponentStyle()
                component.style.min_height = "44px"  # 触摸友好的最小高度
        
        return ui_config
    
    def _optimize_for_aesthetics(
        self,
        ui_config: UIConfiguration,
        context: GenerationContext
    ) -> UIConfiguration:
        """美学优化"""
        # 应用一致的间距
        ui_config.theme.spacing["base"] = "16px"
        ui_config.theme.spacing["small"] = "8px"
        ui_config.theme.spacing["large"] = "32px"
        
        # 优化颜色搭配
        if ui_config.theme.name == "light":
            ui_config.theme.colors["primary"] = "#007bff"
            ui_config.theme.colors["secondary"] = "#6c757d"
            ui_config.theme.colors["success"] = "#28a745"
        
        # 统一圆角
        for component in ui_config.components:
            if component.style is None:
                component.style = ComponentStyle()
            component.style.border_radius = "8px"
        
        return ui_config
    
    def _select_generation_strategy(self, context: GenerationContext) -> str:
        """选择生成策略"""
        # 基于上下文选择最适合的策略
        
        # 如果有明确的用户偏好
        user_preferences = context.user_profile.get("preferences", {})
        if "generation_strategy" in user_preferences:
            return user_preferences["generation_strategy"]
        
        # 基于用户行为模式选择
        behavior_patterns = context.user_profile.get("behavior_patterns", [])
        
        if "power_user" in behavior_patterns:
            return GenerationStrategy.RULE_BASED.value  # 专家用户适合规则生成
        elif "casual_user" in behavior_patterns:
            return GenerationStrategy.TEMPLATE_BASED.value  # 普通用户适合模板
        else:
            return GenerationStrategy.HYBRID.value  # 默认使用混合策略
    
    def _parse_generation_context(self, context: Dict[str, Any]) -> GenerationContext:
        """解析生成上下文"""
        return GenerationContext(
            context_id=context.get("context_id"),
            user_profile=context.get("user_profile", {}),
            device_info=context.get("device_info", {}),
            current_ui_state=context.get("current_ui_state", {}),
            user_intents=context.get("user_intents", []),
            performance_constraints=context.get("performance_constraints", {}),
            accessibility_requirements=context.get("accessibility_requirements", []),
            business_goals=context.get("business_goals", []),
            timestamp=datetime.now()
        )
    
    def _initialize_default_templates(self) -> None:
        """初始化默认模板"""
        # 仪表板模板
        dashboard_template = UITemplate(
            template_id="dashboard_default",
            name="Default Dashboard",
            description="A standard dashboard layout with sidebar and main content",
            category="dashboard",
            base_configuration=create_basic_ui_configuration(),
            variables={
                "sidebar_width": "250px",
                "header_height": "60px"
            },
            conditions={
                "is_dashboard": "context.current_ui_state.get('page_type') == 'dashboard'"
            },
            tags=["dashboard", "sidebar", "responsive"],
            created_at=datetime.now()
        )
        self.template_engine.register_template(dashboard_template)
        
        # 移动端模板
        mobile_template = UITemplate(
            template_id="mobile_default",
            name="Mobile Layout",
            description="Optimized layout for mobile devices",
            category="mobile",
            base_configuration=create_basic_ui_configuration(),
            variables={
                "touch_target_size": "44px",
                "font_size": "16px"
            },
            conditions={
                "is_mobile": "context.device_info.get('type') == 'mobile'"
            },
            tags=["mobile", "touch", "responsive"],
            created_at=datetime.now()
        )
        self.template_engine.register_template(mobile_template)
    
    def _initialize_default_rules(self) -> None:
        """初始化默认规则"""
        # 可访问性规则
        accessibility_rule = GenerationRule(
            rule_id="accessibility_enhancements",
            name="Accessibility Enhancements",
            description="Add accessibility features when required",
            condition="len(context.accessibility_requirements) > 0",
            action="""
for component in ui_config.components:
    if component.type in ['button', 'link', 'input']:
        if component.props is None:
            component.props = ComponentProps()
        component.props.tabindex = 0
        if not component.props.aria_label:
            component.props.aria_label = component.text or f'{component.type} element'
""",
            priority=100,
            tags=["accessibility"]
        )
        self.rule_engine.add_rule(accessibility_rule, "accessibility")
        
        # 性能规则
        performance_rule = GenerationRule(
            rule_id="performance_optimization",
            name="Performance Optimization",
            description="Optimize UI for performance when constraints are present",
            condition="len(context.performance_constraints) > 0",
            action="""
max_components = context.performance_constraints.get('max_components', 30)
if len(ui_config.components) > max_components:
    ui_config.components = ui_config.components[:max_components]
ui_config.theme.animations['enabled'] = False
""",
            priority=80,
            tags=["performance"]
        )
        self.rule_engine.add_rule(performance_rule, "performance")
    
    @event_handler(EventBusEventType.USER_INTERACTION)
    async def handle_user_intent_detected(self, event: EventBusEvent) -> None:
        """处理用户意图检测事件"""
        intent_data = event.data
        self.logger.debug(f"User intent detected: {intent_data.get('intent_type')}")
        
        # 可以在这里触发自动UI生成
    
    @event_handler(EventBusEventType.DECISION_MADE)
    async def handle_decision_made(self, event: EventBusEvent) -> None:
        """处理决策事件"""
        decision_data = event.data
        decision_type = decision_data.get("decision_type")
        
        if decision_type in ["ui_adaptation", "layout_optimization"]:
            # 基于决策结果生成新的UI配置
            self.logger.debug(f"Generating UI based on decision: {decision_type}")
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        total_generations = len(self.generation_history)
        
        if total_generations == 0:
            return {
                "total_generations": 0,
                "average_generation_time": 0.0,
                "strategy_distribution": {},
                "template_count": len(self.template_engine.templates),
                "rule_count": len(self.rule_engine.rules)
            }
        
        # 计算平均生成时间
        total_time = sum(result.generation_time for result in self.generation_history)
        average_time = total_time / total_generations
        
        # 策略分布
        strategy_counts = {}
        for result in self.generation_history:
            strategy = result.generation_strategy.value
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        strategy_distribution = {
            strategy: count / total_generations 
            for strategy, count in strategy_counts.items()
        }
        
        return {
            "total_generations": total_generations,
            "average_generation_time": average_time,
            "strategy_distribution": strategy_distribution,
            "template_count": len(self.template_engine.templates),
            "rule_count": len(self.rule_engine.rules),
            "cache_hit_rate": getattr(self.generation_cache, "hit_rate", 0.0)
        }


# 导出主要类
UIGenerator = SmartUIGenerator  # 为了向后兼容
__all__ = ['SmartUIGenerator', 'UIGenerator']

