"""
SmartUI MCP 统一UI配置数据模型

这个模块定义了SmartUI MCP系统中使用的所有数据模型，
包括UI配置、组件定义、主题设置等核心数据结构。
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime


class ComponentType(str, Enum):
    """UI组件类型枚举"""
    BUTTON = "button"
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    CARD = "card"
    TABLE = "table"
    LIST = "list"
    NAVIGATION = "navigation"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    MODAL = "modal"
    TOOLTIP = "tooltip"
    PROGRESS = "progress"
    CODE_EDITOR = "code_editor"
    FILE_UPLOAD = "file_upload"
    IMAGE = "image"
    VIDEO = "video"
    CHART = "chart"
    FORM = "form"
    TABS = "tabs"
    ACCORDION = "accordion"
    BREADCRUMB = "breadcrumb"
    PAGINATION = "pagination"
    SEARCH = "search"
    FILTER = "filter"
    CALENDAR = "calendar"
    DATETIME_PICKER = "datetime_picker"
    SLIDER = "slider"
    TOGGLE = "toggle"
    BADGE = "badge"
    ALERT = "alert"
    NOTIFICATION = "notification"
    LOADING = "loading"
    DIVIDER = "divider"
    SPACER = "spacer"


class LayoutType(str, Enum):
    """布局类型枚举"""
    GRID = "grid"
    FLEXBOX = "flexbox"
    SIDEBAR = "sidebar"
    DASHBOARD = "dashboard"
    SINGLE_COLUMN = "single_column"
    TWO_COLUMN = "two_column"
    THREE_COLUMN = "three_column"
    HEADER_CONTENT = "header_content"
    HEADER_SIDEBAR_CONTENT = "header_sidebar_content"
    FULL_SCREEN = "full_screen"
    MODAL_OVERLAY = "modal_overlay"
    CODING_WORKSPACE = "coding_workspace"
    TESTING_WORKSPACE = "testing_workspace"
    DESIGN_WORKSPACE = "design_workspace"


class ThemeType(str, Enum):
    """主题类型枚举"""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"
    AUTO = "auto"
    CUSTOM = "custom"


class ComponentVariant(str, Enum):
    """组件变体枚举"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    OUTLINE = "outline"
    GHOST = "ghost"
    LINK = "link"
    SOLID = "solid"
    SUBTLE = "subtle"


class ResponsiveBreakpoint(str, Enum):
    """响应式断点枚举"""
    XS = "xs"  # < 576px
    SM = "sm"  # >= 576px
    MD = "md"  # >= 768px
    LG = "lg"  # >= 992px
    XL = "xl"  # >= 1200px
    XXL = "xxl"  # >= 1400px


class EventType(str, Enum):
    """事件类型枚举"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    HOVER = "hover"
    FOCUS = "focus"
    BLUR = "blur"
    CHANGE = "change"
    INPUT = "input"
    SUBMIT = "submit"
    RESET = "reset"
    SCROLL = "scroll"
    RESIZE = "resize"
    LOAD = "load"
    UNLOAD = "unload"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    KEY_PRESS = "key_press"
    MOUSE_ENTER = "mouse_enter"
    MOUSE_LEAVE = "mouse_leave"
    DRAG_START = "drag_start"
    DRAG_END = "drag_end"
    DROP = "drop"
    CUSTOM = "custom"


class AccessibilityFeature(str, Enum):
    """可访问性特性枚举"""
    SCREEN_READER = "screen_reader"
    KEYBOARD_NAVIGATION = "keyboard_navigation"
    HIGH_CONTRAST = "high_contrast"
    LARGE_FONTS = "large_fonts"
    FOCUS_INDICATORS = "focus_indicators"
    REDUCED_MOTION = "reduced_motion"
    COLOR_BLIND_FRIENDLY = "color_blind_friendly"
    VOICE_CONTROL = "voice_control"


class ComponentStyle(BaseModel):
    """组件样式配置"""
    width: Optional[str] = None
    height: Optional[str] = None
    margin: Optional[str] = None
    padding: Optional[str] = None
    background_color: Optional[str] = None
    color: Optional[str] = None
    border: Optional[str] = None
    border_radius: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    font_family: Optional[str] = None
    text_align: Optional[str] = None
    display: Optional[str] = None
    position: Optional[str] = None
    top: Optional[str] = None
    left: Optional[str] = None
    right: Optional[str] = None
    bottom: Optional[str] = None
    z_index: Optional[int] = None
    opacity: Optional[float] = None
    transform: Optional[str] = None
    transition: Optional[str] = None
    animation: Optional[str] = None
    box_shadow: Optional[str] = None
    custom_css: Optional[Dict[str, str]] = None


class ComponentEvent(BaseModel):
    """组件事件配置"""
    event_type: EventType
    handler: str = Field(..., description="事件处理函数名或JavaScript代码")
    prevent_default: bool = False
    stop_propagation: bool = False
    debounce: Optional[int] = None  # 防抖延迟（毫秒）
    throttle: Optional[int] = None  # 节流延迟（毫秒）
    conditions: Optional[Dict[str, Any]] = None  # 触发条件


class ComponentValidation(BaseModel):
    """组件验证规则"""
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None  # 正则表达式
    custom_validator: Optional[str] = None  # 自定义验证函数
    error_message: Optional[str] = None


class ComponentProps(BaseModel):
    """组件属性配置"""
    # 通用属性
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    class_name: Optional[str] = None
    style: Optional[ComponentStyle] = None
    variant: Optional[ComponentVariant] = None
    size: Optional[Literal["xs", "sm", "md", "lg", "xl"]] = "md"
    disabled: bool = False
    hidden: bool = False
    readonly: bool = False
    
    # 内容属性
    text: Optional[str] = None
    placeholder: Optional[str] = None
    value: Optional[Any] = None
    default_value: Optional[Any] = None
    
    # 交互属性
    events: List[ComponentEvent] = Field(default_factory=list)
    validation: Optional[ComponentValidation] = None
    
    # 可访问性属性
    aria_label: Optional[str] = None
    aria_describedby: Optional[str] = None
    role: Optional[str] = None
    tabindex: Optional[int] = None
    
    # 响应式属性
    responsive: Optional[Dict[ResponsiveBreakpoint, Dict[str, Any]]] = None
    
    # 自定义属性
    custom_props: Optional[Dict[str, Any]] = None


class UIComponent(BaseModel):
    """UI组件定义"""
    type: ComponentType
    props: ComponentProps
    children: List["UIComponent"] = Field(default_factory=list)
    
    # 组件元数据
    name: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0.0"
    
    # 数据绑定
    data_binding: Optional[str] = None  # API状态绑定路径
    
    # 条件渲染
    render_condition: Optional[str] = None  # 渲染条件表达式
    
    # 组件生命周期
    on_mount: Optional[str] = None  # 组件挂载时执行的代码
    on_unmount: Optional[str] = None  # 组件卸载时执行的代码
    on_update: Optional[str] = None  # 组件更新时执行的代码


class LayoutConfig(BaseModel):
    """布局配置"""
    type: LayoutType
    grid_columns: Optional[int] = None
    grid_rows: Optional[int] = None
    gap: Optional[str] = None
    align_items: Optional[str] = None
    justify_content: Optional[str] = None
    flex_direction: Optional[str] = None
    flex_wrap: Optional[str] = None
    sidebar_width: Optional[str] = None
    header_height: Optional[str] = None
    footer_height: Optional[str] = None
    responsive_breakpoints: Optional[Dict[ResponsiveBreakpoint, Dict[str, Any]]] = None
    custom_layout_css: Optional[str] = None


class ThemeConfig(BaseModel):
    """主题配置"""
    type: ThemeType
    primary_color: str = "#007acc"
    secondary_color: str = "#6c757d"
    success_color: str = "#28a745"
    warning_color: str = "#ffc107"
    error_color: str = "#dc3545"
    info_color: str = "#17a2b8"
    background_color: str = "#ffffff"
    surface_color: str = "#f8f9fa"
    text_color: str = "#212529"
    text_secondary_color: str = "#6c757d"
    border_color: str = "#dee2e6"
    shadow_color: str = "rgba(0, 0, 0, 0.1)"
    
    # 字体配置
    font_family: str = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    font_size_base: str = "16px"
    font_size_sm: str = "14px"
    font_size_lg: str = "18px"
    font_size_xl: str = "20px"
    line_height: str = "1.5"
    
    # 间距配置
    spacing_xs: str = "4px"
    spacing_sm: str = "8px"
    spacing_md: str = "16px"
    spacing_lg: str = "24px"
    spacing_xl: str = "32px"
    
    # 圆角配置
    border_radius_sm: str = "4px"
    border_radius_md: str = "8px"
    border_radius_lg: str = "12px"
    border_radius_xl: str = "16px"
    
    # 阴影配置
    shadow_sm: str = "0 1px 3px rgba(0, 0, 0, 0.1)"
    shadow_md: str = "0 4px 6px rgba(0, 0, 0, 0.1)"
    shadow_lg: str = "0 10px 15px rgba(0, 0, 0, 0.1)"
    shadow_xl: str = "0 20px 25px rgba(0, 0, 0, 0.1)"
    
    # 自定义CSS变量
    custom_variables: Optional[Dict[str, str]] = None


class APIStateBinding(BaseModel):
    """API状态绑定配置"""
    component_id: str
    component_property: str
    api_path: str
    transform: Optional[str] = None  # 数据转换函数
    default_value: Optional[Any] = None
    update_trigger: Optional[str] = None  # 更新触发条件


class InteractionRule(BaseModel):
    """交互规则配置"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    condition: str  # 触发条件表达式
    action: str  # 执行动作
    priority: int = 0  # 优先级，数字越大优先级越高
    enabled: bool = True
    
    # 规则元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)


class AdaptationRule(BaseModel):
    """自适应规则配置"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    
    # 触发条件
    user_behavior_patterns: Optional[List[str]] = None
    environment_conditions: Optional[Dict[str, Any]] = None
    api_state_conditions: Optional[Dict[str, Any]] = None
    time_conditions: Optional[Dict[str, Any]] = None
    
    # 适应动作
    ui_modifications: Optional[Dict[str, Any]] = None
    theme_adjustments: Optional[Dict[str, Any]] = None
    layout_changes: Optional[Dict[str, Any]] = None
    component_updates: Optional[List[Dict[str, Any]]] = None
    
    # 规则配置
    priority: int = 0
    enabled: bool = True
    learning_enabled: bool = False  # 是否启用机器学习优化
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UIConfiguration(BaseModel):
    """统一UI配置模型"""
    # 基础信息
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    
    # 布局和主题
    layout: LayoutConfig
    theme: ThemeConfig
    
    # 组件树
    components: List[UIComponent]
    
    # 数据绑定
    api_state_bindings: List[APIStateBinding] = Field(default_factory=list)
    
    # 交互和自适应规则
    interaction_rules: List[InteractionRule] = Field(default_factory=list)
    adaptation_rules: List[AdaptationRule] = Field(default_factory=list)
    
    # 可访问性配置
    accessibility_features: List[AccessibilityFeature] = Field(default_factory=list)
    
    # 性能配置
    lazy_loading: bool = True
    virtual_scrolling: bool = False
    code_splitting: bool = True
    preload_components: List[str] = Field(default_factory=list)
    
    # 国际化配置
    locale: str = "en-US"
    rtl: bool = False
    translations: Optional[Dict[str, Dict[str, str]]] = None
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # 自定义配置
    custom_config: Optional[Dict[str, Any]] = None


class UIModificationRequest(BaseModel):
    """UI修改请求模型"""
    # 请求信息
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    source_mcp_id: str
    target_mcp_id: str = "smartui_mcp"
    
    # 协议版本
    protocol_version: str = "1.0"
    
    # 工作流上下文
    workflow_context: Dict[str, Any]
    
    # UI需求配置
    ui_requirements: Dict[str, Any]
    
    # 适配规则
    adaptation_rules: Optional[Dict[str, Any]] = None
    
    # 回调配置
    callback_config: Optional[Dict[str, Any]] = None
    
    # 优先级和超时
    priority: int = 0
    timeout: Optional[int] = None  # 超时时间（秒）
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = None


class UIModificationResponse(BaseModel):
    """UI修改响应模型"""
    # 响应信息
    request_id: str
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # 处理结果
    success: bool
    ui_configuration: Optional[UIConfiguration] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # 性能指标
    processing_time: float  # 处理时间（秒）
    generation_time: float  # UI生成时间（秒）
    memory_usage: Optional[float] = None  # 内存使用（MB）
    
    # 回调端点
    callback_endpoints: Optional[Dict[str, str]] = None
    
    # 元数据
    metadata: Optional[Dict[str, Any]] = None


# 更新前向引用
UIComponent.model_rebuild()


# 工厂函数和辅助方法

def create_button_component(
    text: str,
    variant: ComponentVariant = ComponentVariant.PRIMARY,
    on_click: Optional[str] = None,
    **kwargs
) -> UIComponent:
    """创建按钮组件的工厂函数"""
    events = []
    if on_click:
        events.append(ComponentEvent(event_type=EventType.CLICK, handler=on_click))
    
    props = ComponentProps(
        text=text,
        variant=variant,
        events=events,
        **kwargs
    )
    
    return UIComponent(type=ComponentType.BUTTON, props=props)


def create_input_component(
    placeholder: str,
    input_type: str = "text",
    required: bool = False,
    **kwargs
) -> UIComponent:
    """创建输入组件的工厂函数"""
    validation = ComponentValidation(required=required) if required else None
    
    props = ComponentProps(
        placeholder=placeholder,
        validation=validation,
        custom_props={"type": input_type},
        **kwargs
    )
    
    return UIComponent(type=ComponentType.INPUT, props=props)


def create_card_component(
    title: Optional[str] = None,
    content: Optional[str] = None,
    children: Optional[List[UIComponent]] = None,
    **kwargs
) -> UIComponent:
    """创建卡片组件的工厂函数"""
    props = ComponentProps(
        custom_props={"title": title, "content": content},
        **kwargs
    )
    
    return UIComponent(
        type=ComponentType.CARD,
        props=props,
        children=children or []
    )


def create_default_theme(theme_type: ThemeType = ThemeType.LIGHT) -> ThemeConfig:
    """创建默认主题配置"""
    if theme_type == ThemeType.DARK:
        return ThemeConfig(
            type=ThemeType.DARK,
            primary_color="#007acc",
            background_color="#1e1e1e",
            surface_color="#252526",
            text_color="#cccccc",
            text_secondary_color="#969696",
            border_color="#3c3c3c"
        )
    elif theme_type == ThemeType.HIGH_CONTRAST:
        return ThemeConfig(
            type=ThemeType.HIGH_CONTRAST,
            primary_color="#ffff00",
            background_color="#000000",
            surface_color="#000000",
            text_color="#ffffff",
            text_secondary_color="#ffffff",
            border_color="#ffffff"
        )
    else:
        return ThemeConfig(type=theme_type)


def create_default_layout(layout_type: LayoutType = LayoutType.SINGLE_COLUMN) -> LayoutConfig:
    """创建默认布局配置"""
    return LayoutConfig(type=layout_type)


def create_basic_ui_configuration(
    name: str,
    components: List[UIComponent],
    layout_type: LayoutType = LayoutType.SINGLE_COLUMN,
    theme_type: ThemeType = ThemeType.LIGHT
) -> UIConfiguration:
    """创建基础UI配置"""
    return UIConfiguration(
        name=name,
        layout=create_default_layout(layout_type),
        theme=create_default_theme(theme_type),
        components=components
    )

