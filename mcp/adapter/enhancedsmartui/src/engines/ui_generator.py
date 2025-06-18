#!/usr/bin/env python3
"""
SmartUI Enhanced - 动态界面生成引擎
实现根据需求动态生成HTML/CSS/JavaScript，响应式布局适配，组件化界面构建
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib
import re

logger = logging.getLogger(__name__)

class ComponentType(Enum):
    """组件类型"""
    LAYOUT = "layout"
    FORM = "form"
    TABLE = "table"
    CHART = "chart"
    NAVIGATION = "navigation"
    BUTTON = "button"
    INPUT = "input"
    MODAL = "modal"
    CARD = "card"
    LIST = "list"

class LayoutType(Enum):
    """布局类型"""
    GRID = "grid"
    FLEXBOX = "flexbox"
    SIDEBAR = "sidebar"
    DASHBOARD = "dashboard"
    MOBILE_STACK = "mobile_stack"
    COMPACT = "compact"
    SPACIOUS = "spacious"

class ThemeType(Enum):
    """主题类型"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"
    HIGH_CONTRAST = "high_contrast"
    COLORFUL = "colorful"

@dataclass
class ComponentConfig:
    """组件配置"""
    component_type: ComponentType
    component_id: str
    props: Dict[str, Any]
    styles: Dict[str, Any]
    events: Dict[str, str]
    children: List['ComponentConfig'] = None
    conditional_rendering: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class UIRequirements:
    """UI需求定义"""
    layout_type: LayoutType
    theme: ThemeType
    components: List[ComponentConfig]
    responsive_breakpoints: Dict[str, int]
    accessibility_features: List[str]
    performance_requirements: Dict[str, Any]
    user_preferences: Dict[str, Any]
    context: Dict[str, Any]

class ComponentLibrary:
    """组件库"""
    
    def __init__(self):
        self.components = {}
        self.templates = {}
        self._register_default_components()
    
    def _register_default_components(self):
        """注册默认组件"""
        
        # 按钮组件
        self.register_component("button", {
            "html_template": """
            <button class="{classes}" id="{id}" {attributes}>
                {icon}{text}
            </button>
            """,
            "css_template": """
            .btn-{variant} {
                padding: {padding};
                background-color: {bg_color};
                color: {text_color};
                border: {border};
                border-radius: {border_radius};
                font-size: {font_size};
                font-weight: {font_weight};
                cursor: pointer;
                transition: all 0.3s ease;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }
            .btn-{variant}:hover {
                background-color: {hover_bg_color};
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .btn-{variant}:active {
                transform: translateY(0);
            }
            .btn-{variant}:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            """,
            "js_template": """
            document.getElementById('{id}').addEventListener('click', function(e) {
                {click_handler}
            });
            """,
            "variants": {
                "primary": {
                    "bg_color": "#3b82f6",
                    "text_color": "#ffffff",
                    "hover_bg_color": "#2563eb",
                    "border": "none"
                },
                "secondary": {
                    "bg_color": "#6b7280",
                    "text_color": "#ffffff", 
                    "hover_bg_color": "#4b5563",
                    "border": "none"
                },
                "outline": {
                    "bg_color": "transparent",
                    "text_color": "#3b82f6",
                    "hover_bg_color": "#3b82f6",
                    "border": "2px solid #3b82f6"
                }
            }
        })
        
        # 输入框组件
        self.register_component("input", {
            "html_template": """
            <div class="input-group-{id}">
                {label}
                <input type="{input_type}" class="{classes}" id="{id}" 
                       placeholder="{placeholder}" {attributes} />
                {help_text}
                {error_message}
            </div>
            """,
            "css_template": """
            .input-group-{id} {
                margin-bottom: 1rem;
            }
            .input-{variant} {
                width: 100%;
                padding: {padding};
                border: {border};
                border-radius: {border_radius};
                font-size: {font_size};
                background-color: {bg_color};
                color: {text_color};
                transition: all 0.3s ease;
            }
            .input-{variant}:focus {
                outline: none;
                border-color: {focus_border_color};
                box-shadow: 0 0 0 3px {focus_shadow_color};
            }
            .input-{variant}:invalid {
                border-color: #ef4444;
            }
            .label-{id} {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: {label_color};
            }
            .help-text-{id} {
                font-size: 0.875rem;
                color: {help_color};
                margin-top: 0.25rem;
            }
            .error-message-{id} {
                font-size: 0.875rem;
                color: #ef4444;
                margin-top: 0.25rem;
            }
            """,
            "js_template": """
            const input_{id} = document.getElementById('{id}');
            input_{id}.addEventListener('input', function(e) {
                {input_handler}
            });
            input_{id}.addEventListener('blur', function(e) {
                {blur_handler}
            });
            """,
            "variants": {
                "default": {
                    "bg_color": "#ffffff",
                    "text_color": "#1f2937",
                    "border": "2px solid #d1d5db",
                    "focus_border_color": "#3b82f6",
                    "focus_shadow_color": "rgba(59, 130, 246, 0.1)"
                },
                "dark": {
                    "bg_color": "#374151",
                    "text_color": "#f9fafb",
                    "border": "2px solid #4b5563",
                    "focus_border_color": "#60a5fa",
                    "focus_shadow_color": "rgba(96, 165, 250, 0.1)"
                }
            }
        })
        
        # 卡片组件
        self.register_component("card", {
            "html_template": """
            <div class="card-{variant} {classes}" id="{id}">
                {header}
                <div class="card-body-{id}">
                    {content}
                </div>
                {footer}
            </div>
            """,
            "css_template": """
            .card-{variant} {
                background-color: {bg_color};
                border: {border};
                border-radius: {border_radius};
                box-shadow: {box_shadow};
                overflow: hidden;
                transition: all 0.3s ease;
            }
            .card-{variant}:hover {
                box-shadow: {hover_shadow};
                transform: translateY(-2px);
            }
            .card-header-{id} {
                padding: {header_padding};
                background-color: {header_bg_color};
                border-bottom: {header_border};
                font-weight: 600;
                color: {header_text_color};
            }
            .card-body-{id} {
                padding: {body_padding};
                color: {body_text_color};
            }
            .card-footer-{id} {
                padding: {footer_padding};
                background-color: {footer_bg_color};
                border-top: {footer_border};
            }
            """,
            "variants": {
                "default": {
                    "bg_color": "#ffffff",
                    "border": "1px solid #e5e7eb",
                    "box_shadow": "0 1px 3px rgba(0,0,0,0.1)",
                    "hover_shadow": "0 4px 12px rgba(0,0,0,0.15)"
                },
                "elevated": {
                    "bg_color": "#ffffff",
                    "border": "none",
                    "box_shadow": "0 4px 6px rgba(0,0,0,0.1)",
                    "hover_shadow": "0 8px 25px rgba(0,0,0,0.15)"
                }
            }
        })
        
        # 表格组件
        self.register_component("table", {
            "html_template": """
            <div class="table-container-{id}">
                <table class="table-{variant}" id="{id}">
                    <thead class="table-header-{id}">
                        {header_rows}
                    </thead>
                    <tbody class="table-body-{id}">
                        {body_rows}
                    </tbody>
                    {footer}
                </table>
            </div>
            """,
            "css_template": """
            .table-container-{id} {
                overflow-x: auto;
                border-radius: {border_radius};
                border: {container_border};
            }
            .table-{variant} {
                width: 100%;
                border-collapse: collapse;
                background-color: {bg_color};
            }
            .table-header-{id} th {
                padding: {header_padding};
                background-color: {header_bg_color};
                color: {header_text_color};
                font-weight: 600;
                text-align: left;
                border-bottom: {header_border};
            }
            .table-body-{id} td {
                padding: {cell_padding};
                border-bottom: {cell_border};
                color: {cell_text_color};
            }
            .table-body-{id} tr:hover {
                background-color: {hover_bg_color};
            }
            .table-body-{id} tr:nth-child(even) {
                background-color: {stripe_bg_color};
            }
            """,
            "variants": {
                "default": {
                    "bg_color": "#ffffff",
                    "header_bg_color": "#f9fafb",
                    "hover_bg_color": "#f3f4f6",
                    "stripe_bg_color": "#f9fafb"
                },
                "dark": {
                    "bg_color": "#1f2937",
                    "header_bg_color": "#374151",
                    "hover_bg_color": "#374151",
                    "stripe_bg_color": "#2d3748"
                }
            }
        })
        
        # 导航组件
        self.register_component("navigation", {
            "html_template": """
            <nav class="nav-{variant}" id="{id}">
                <div class="nav-container-{id}">
                    {brand}
                    <div class="nav-menu-{id}">
                        {menu_items}
                    </div>
                    {actions}
                </div>
            </nav>
            """,
            "css_template": """
            .nav-{variant} {
                background-color: {bg_color};
                border-bottom: {border};
                box-shadow: {box_shadow};
                position: {position};
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
            }
            .nav-container-{id} {
                max-width: {max_width};
                margin: 0 auto;
                padding: {padding};
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .nav-menu-{id} {
                display: flex;
                align-items: center;
                gap: {menu_gap};
            }
            .nav-item-{id} {
                color: {text_color};
                text-decoration: none;
                padding: {item_padding};
                border-radius: {item_border_radius};
                transition: all 0.3s ease;
            }
            .nav-item-{id}:hover {
                background-color: {hover_bg_color};
                color: {hover_text_color};
            }
            .nav-item-{id}.active {
                background-color: {active_bg_color};
                color: {active_text_color};
            }
            """,
            "variants": {
                "horizontal": {
                    "position": "sticky",
                    "bg_color": "#ffffff",
                    "border": "1px solid #e5e7eb",
                    "box_shadow": "0 1px 3px rgba(0,0,0,0.1)"
                },
                "sidebar": {
                    "position": "fixed",
                    "bg_color": "#1f2937",
                    "border": "none",
                    "box_shadow": "2px 0 4px rgba(0,0,0,0.1)"
                }
            }
        })
    
    def register_component(self, component_name: str, component_def: Dict[str, Any]):
        """注册组件"""
        self.components[component_name] = component_def
        logger.info(f"注册组件: {component_name}")
    
    def get_component(self, component_name: str) -> Optional[Dict[str, Any]]:
        """获取组件定义"""
        return self.components.get(component_name)
    
    def list_components(self) -> List[str]:
        """列出所有组件"""
        return list(self.components.keys())

class LayoutEngine:
    """布局引擎"""
    
    def __init__(self):
        self.layout_templates = {}
        self._register_default_layouts()
    
    def _register_default_layouts(self):
        """注册默认布局"""
        
        # 网格布局
        self.register_layout("grid", {
            "html_template": """
            <div class="layout-grid-{id}" id="{id}">
                {grid_items}
            </div>
            """,
            "css_template": """
            .layout-grid-{id} {
                display: grid;
                grid-template-columns: {columns};
                grid-template-rows: {rows};
                gap: {gap};
                padding: {padding};
                min-height: {min_height};
            }
            .grid-item-{id} {
                background-color: {item_bg_color};
                border-radius: {item_border_radius};
                padding: {item_padding};
                overflow: hidden;
            }
            @media (max-width: 768px) {
                .layout-grid-{id} {
                    grid-template-columns: 1fr;
                    gap: {mobile_gap};
                }
            }
            """,
            "responsive_rules": {
                "mobile": "grid-template-columns: 1fr;",
                "tablet": "grid-template-columns: repeat(2, 1fr);",
                "desktop": "grid-template-columns: {columns};"
            }
        })
        
        # Flexbox布局
        self.register_layout("flexbox", {
            "html_template": """
            <div class="layout-flex-{id}" id="{id}">
                {flex_items}
            </div>
            """,
            "css_template": """
            .layout-flex-{id} {
                display: flex;
                flex-direction: {direction};
                justify-content: {justify_content};
                align-items: {align_items};
                gap: {gap};
                padding: {padding};
                flex-wrap: {flex_wrap};
            }
            .flex-item-{id} {
                flex: {flex_grow} {flex_shrink} {flex_basis};
                background-color: {item_bg_color};
                border-radius: {item_border_radius};
                padding: {item_padding};
            }
            @media (max-width: 768px) {
                .layout-flex-{id} {
                    flex-direction: column;
                }
            }
            """,
            "responsive_rules": {
                "mobile": "flex-direction: column;",
                "tablet": "flex-direction: {direction};",
                "desktop": "flex-direction: {direction};"
            }
        })
        
        # 侧边栏布局
        self.register_layout("sidebar", {
            "html_template": """
            <div class="layout-sidebar-{id}" id="{id}">
                <aside class="sidebar-{id}">
                    {sidebar_content}
                </aside>
                <main class="main-content-{id}">
                    {main_content}
                </main>
            </div>
            """,
            "css_template": """
            .layout-sidebar-{id} {
                display: flex;
                min-height: 100vh;
            }
            .sidebar-{id} {
                width: {sidebar_width};
                background-color: {sidebar_bg_color};
                border-right: {sidebar_border};
                padding: {sidebar_padding};
                overflow-y: auto;
                transition: transform 0.3s ease;
            }
            .main-content-{id} {
                flex: 1;
                padding: {main_padding};
                background-color: {main_bg_color};
                overflow-y: auto;
            }
            @media (max-width: 768px) {
                .sidebar-{id} {
                    position: fixed;
                    top: 0;
                    left: 0;
                    height: 100vh;
                    z-index: 1000;
                    transform: translateX(-100%);
                }
                .sidebar-{id}.open {
                    transform: translateX(0);
                }
                .main-content-{id} {
                    margin-left: 0;
                }
            }
            """,
            "responsive_rules": {
                "mobile": "sidebar: fixed; main: full-width;",
                "tablet": "sidebar: {sidebar_width}; main: flex-1;",
                "desktop": "sidebar: {sidebar_width}; main: flex-1;"
            }
        })
        
        # 仪表板布局
        self.register_layout("dashboard", {
            "html_template": """
            <div class="layout-dashboard-{id}" id="{id}">
                <header class="dashboard-header-{id}">
                    {header_content}
                </header>
                <div class="dashboard-body-{id}">
                    <aside class="dashboard-sidebar-{id}">
                        {sidebar_content}
                    </aside>
                    <main class="dashboard-main-{id}">
                        <div class="dashboard-widgets-{id}">
                            {widgets}
                        </div>
                    </main>
                </div>
            </div>
            """,
            "css_template": """
            .layout-dashboard-{id} {
                display: grid;
                grid-template-rows: auto 1fr;
                min-height: 100vh;
            }
            .dashboard-header-{id} {
                background-color: {header_bg_color};
                border-bottom: {header_border};
                padding: {header_padding};
                box-shadow: {header_shadow};
            }
            .dashboard-body-{id} {
                display: grid;
                grid-template-columns: {sidebar_width} 1fr;
            }
            .dashboard-sidebar-{id} {
                background-color: {sidebar_bg_color};
                border-right: {sidebar_border};
                padding: {sidebar_padding};
            }
            .dashboard-main-{id} {
                padding: {main_padding};
                background-color: {main_bg_color};
            }
            .dashboard-widgets-{id} {
                display: grid;
                grid-template-columns: {widget_columns};
                gap: {widget_gap};
            }
            @media (max-width: 1024px) {
                .dashboard-body-{id} {
                    grid-template-columns: 1fr;
                }
                .dashboard-sidebar-{id} {
                    display: none;
                }
            }
            """,
            "responsive_rules": {
                "mobile": "single-column; sidebar: hidden;",
                "tablet": "single-column; sidebar: hidden;",
                "desktop": "sidebar + main; widgets: grid;"
            }
        })
    
    def register_layout(self, layout_name: str, layout_def: Dict[str, Any]):
        """注册布局"""
        self.layout_templates[layout_name] = layout_def
        logger.info(f"注册布局: {layout_name}")
    
    def get_layout(self, layout_name: str) -> Optional[Dict[str, Any]]:
        """获取布局定义"""
        return self.layout_templates.get(layout_name)
    
    def generate_responsive_css(self, layout_name: str, config: Dict[str, Any]) -> str:
        """生成响应式CSS"""
        layout_def = self.get_layout(layout_name)
        if not layout_def:
            return ""
        
        css = layout_def["css_template"].format(**config)
        
        # 添加响应式规则
        responsive_rules = layout_def.get("responsive_rules", {})
        for breakpoint, rules in responsive_rules.items():
            breakpoint_config = config.get(f"{breakpoint}_config", {})
            if breakpoint_config:
                css += f"\n@media {self._get_media_query(breakpoint)} {{\n"
                css += f"  {rules.format(**breakpoint_config)}\n"
                css += "}\n"
        
        return css
    
    def _get_media_query(self, breakpoint: str) -> str:
        """获取媒体查询"""
        media_queries = {
            "mobile": "(max-width: 767px)",
            "tablet": "(min-width: 768px) and (max-width: 1023px)",
            "desktop": "(min-width: 1024px)"
        }
        return media_queries.get(breakpoint, "(min-width: 0px)")

class ThemeEngine:
    """主题引擎"""
    
    def __init__(self):
        self.themes = {}
        self._register_default_themes()
    
    def _register_default_themes(self):
        """注册默认主题"""
        
        # 亮色主题
        self.register_theme("light", {
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#6b7280",
                "success": "#10b981",
                "warning": "#f59e0b",
                "error": "#ef4444",
                "background": "#ffffff",
                "surface": "#f9fafb",
                "text_primary": "#1f2937",
                "text_secondary": "#6b7280",
                "border": "#e5e7eb"
            },
            "typography": {
                "font_family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                "font_size_base": "16px",
                "font_weight_normal": "400",
                "font_weight_medium": "500",
                "font_weight_bold": "600",
                "line_height": "1.5"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "2xl": "3rem"
            },
            "shadows": {
                "sm": "0 1px 2px rgba(0,0,0,0.05)",
                "md": "0 4px 6px rgba(0,0,0,0.1)",
                "lg": "0 10px 15px rgba(0,0,0,0.1)",
                "xl": "0 20px 25px rgba(0,0,0,0.1)"
            },
            "border_radius": {
                "sm": "0.25rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "xl": "0.75rem"
            }
        })
        
        # 暗色主题
        self.register_theme("dark", {
            "colors": {
                "primary": "#60a5fa",
                "secondary": "#9ca3af",
                "success": "#34d399",
                "warning": "#fbbf24",
                "error": "#f87171",
                "background": "#111827",
                "surface": "#1f2937",
                "text_primary": "#f9fafb",
                "text_secondary": "#d1d5db",
                "border": "#374151"
            },
            "typography": {
                "font_family": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                "font_size_base": "16px",
                "font_weight_normal": "400",
                "font_weight_medium": "500",
                "font_weight_bold": "600",
                "line_height": "1.5"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "2xl": "3rem"
            },
            "shadows": {
                "sm": "0 1px 2px rgba(0,0,0,0.3)",
                "md": "0 4px 6px rgba(0,0,0,0.3)",
                "lg": "0 10px 15px rgba(0,0,0,0.3)",
                "xl": "0 20px 25px rgba(0,0,0,0.3)"
            },
            "border_radius": {
                "sm": "0.25rem",
                "md": "0.375rem",
                "lg": "0.5rem",
                "xl": "0.75rem"
            }
        })
        
        # 高对比度主题
        self.register_theme("high_contrast", {
            "colors": {
                "primary": "#0000ff",
                "secondary": "#000000",
                "success": "#008000",
                "warning": "#ff8c00",
                "error": "#ff0000",
                "background": "#ffffff",
                "surface": "#f0f0f0",
                "text_primary": "#000000",
                "text_secondary": "#333333",
                "border": "#000000"
            },
            "typography": {
                "font_family": "'Arial', sans-serif",
                "font_size_base": "18px",
                "font_weight_normal": "400",
                "font_weight_medium": "600",
                "font_weight_bold": "700",
                "line_height": "1.6"
            },
            "spacing": {
                "xs": "0.5rem",
                "sm": "0.75rem",
                "md": "1.25rem",
                "lg": "2rem",
                "xl": "2.5rem",
                "2xl": "3.5rem"
            },
            "shadows": {
                "sm": "0 2px 4px rgba(0,0,0,0.5)",
                "md": "0 4px 8px rgba(0,0,0,0.5)",
                "lg": "0 8px 16px rgba(0,0,0,0.5)",
                "xl": "0 16px 32px rgba(0,0,0,0.5)"
            },
            "border_radius": {
                "sm": "0.125rem",
                "md": "0.25rem",
                "lg": "0.375rem",
                "xl": "0.5rem"
            }
        })
    
    def register_theme(self, theme_name: str, theme_def: Dict[str, Any]):
        """注册主题"""
        self.themes[theme_name] = theme_def
        logger.info(f"注册主题: {theme_name}")
    
    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """获取主题定义"""
        return self.themes.get(theme_name)
    
    def generate_css_variables(self, theme_name: str) -> str:
        """生成CSS变量"""
        theme = self.get_theme(theme_name)
        if not theme:
            return ""
        
        css_vars = ":root {\n"
        
        # 颜色变量
        for color_name, color_value in theme.get("colors", {}).items():
            css_vars += f"  --color-{color_name.replace('_', '-')}: {color_value};\n"
        
        # 字体变量
        typography = theme.get("typography", {})
        for typo_name, typo_value in typography.items():
            css_vars += f"  --{typo_name.replace('_', '-')}: {typo_value};\n"
        
        # 间距变量
        for spacing_name, spacing_value in theme.get("spacing", {}).items():
            css_vars += f"  --spacing-{spacing_name}: {spacing_value};\n"
        
        # 阴影变量
        for shadow_name, shadow_value in theme.get("shadows", {}).items():
            css_vars += f"  --shadow-{shadow_name}: {shadow_value};\n"
        
        # 圆角变量
        for radius_name, radius_value in theme.get("border_radius", {}).items():
            css_vars += f"  --border-radius-{radius_name}: {radius_value};\n"
        
        css_vars += "}\n"
        return css_vars

class UIGenerator:
    """界面生成引擎 - 主类"""
    
    def __init__(self):
        self.component_library = ComponentLibrary()
        self.layout_engine = LayoutEngine()
        self.theme_engine = ThemeEngine()
        self.generated_interfaces = {}
        self.template_cache = {}
    
    async def generate_interface(self, requirements: UIRequirements) -> Dict[str, str]:
        """根据需求生成界面"""
        try:
            start_time = time.time()
            
            # 1. 选择和配置主题
            theme_css = await self._generate_theme_css(requirements.theme, requirements.user_preferences)
            
            # 2. 生成布局
            layout_html, layout_css = await self._generate_layout(
                requirements.layout_type, 
                requirements.components,
                requirements.responsive_breakpoints
            )
            
            # 3. 生成组件
            components_html, components_css, components_js = await self._generate_components(
                requirements.components,
                requirements.theme,
                requirements.user_preferences
            )
            
            # 4. 应用可访问性特性
            accessibility_css = await self._generate_accessibility_css(requirements.accessibility_features)
            
            # 5. 性能优化
            optimized_css = await self._optimize_css(theme_css + layout_css + components_css + accessibility_css)
            optimized_js = await self._optimize_js(components_js)
            
            # 6. 生成完整HTML
            complete_html = await self._generate_complete_html(
                layout_html + components_html,
                optimized_css,
                optimized_js,
                requirements
            )
            
            generation_time = time.time() - start_time
            
            # 7. 缓存生成结果
            interface_id = self._generate_interface_id(requirements)
            self.generated_interfaces[interface_id] = {
                "html": complete_html,
                "css": optimized_css,
                "js": optimized_js,
                "generation_time": generation_time,
                "requirements": asdict(requirements),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "html": complete_html,
                "css": optimized_css,
                "js": optimized_js,
                "interface_id": interface_id,
                "generation_time": generation_time
            }
            
        except Exception as e:
            logger.error(f"界面生成失败: {e}")
            return {
                "error": str(e),
                "html": "",
                "css": "",
                "js": ""
            }
    
    async def _generate_theme_css(self, theme: ThemeType, user_preferences: Dict[str, Any]) -> str:
        """生成主题CSS"""
        theme_name = theme.value
        
        # 根据用户偏好调整主题
        if user_preferences.get("auto_theme") and theme == ThemeType.AUTO:
            current_hour = datetime.now().hour
            theme_name = "dark" if 20 <= current_hour or current_hour <= 6 else "light"
        
        theme_css = self.theme_engine.generate_css_variables(theme_name)
        
        # 添加基础样式
        base_css = """
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: var(--font-family);
            font-size: var(--font-size-base);
            line-height: var(--line-height);
            color: var(--color-text-primary);
            background-color: var(--color-background);
            transition: all 0.3s ease;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }
        
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        """
        
        return theme_css + base_css
    
    async def _generate_layout(self, layout_type: LayoutType, 
                             components: List[ComponentConfig],
                             breakpoints: Dict[str, int]) -> Tuple[str, str]:
        """生成布局"""
        layout_name = layout_type.value
        layout_def = self.layout_engine.get_layout(layout_name)
        
        if not layout_def:
            logger.warning(f"未找到布局定义: {layout_name}")
            return "", ""
        
        # 配置布局参数
        layout_config = await self._build_layout_config(layout_type, components, breakpoints)
        
        # 生成HTML
        layout_html = layout_def["html_template"].format(**layout_config)
        
        # 生成CSS
        layout_css = self.layout_engine.generate_responsive_css(layout_name, layout_config)
        
        return layout_html, layout_css
    
    async def _build_layout_config(self, layout_type: LayoutType,
                                 components: List[ComponentConfig],
                                 breakpoints: Dict[str, int]) -> Dict[str, Any]:
        """构建布局配置"""
        config = {
            "id": f"layout_{int(time.time())}",
            "padding": "var(--spacing-md)",
            "gap": "var(--spacing-md)",
            "min_height": "100vh"
        }
        
        if layout_type == LayoutType.GRID:
            # 根据组件数量计算网格列数
            component_count = len(components)
            if component_count <= 2:
                config["columns"] = "repeat(2, 1fr)"
            elif component_count <= 4:
                config["columns"] = "repeat(2, 1fr)"
            else:
                config["columns"] = "repeat(3, 1fr)"
            
            config["rows"] = "auto"
            config["mobile_gap"] = "var(--spacing-sm)"
            
        elif layout_type == LayoutType.FLEXBOX:
            config.update({
                "direction": "row",
                "justify_content": "flex-start",
                "align_items": "stretch",
                "flex_wrap": "wrap"
            })
            
        elif layout_type == LayoutType.SIDEBAR:
            config.update({
                "sidebar_width": "250px",
                "sidebar_bg_color": "var(--color-surface)",
                "sidebar_border": "1px solid var(--color-border)",
                "sidebar_padding": "var(--spacing-lg)",
                "main_padding": "var(--spacing-lg)",
                "main_bg_color": "var(--color-background)"
            })
            
        elif layout_type == LayoutType.DASHBOARD:
            config.update({
                "header_bg_color": "var(--color-surface)",
                "header_border": "1px solid var(--color-border)",
                "header_padding": "var(--spacing-md) var(--spacing-lg)",
                "header_shadow": "var(--shadow-sm)",
                "sidebar_width": "200px",
                "sidebar_bg_color": "var(--color-surface)",
                "sidebar_border": "1px solid var(--color-border)",
                "sidebar_padding": "var(--spacing-lg)",
                "main_padding": "var(--spacing-lg)",
                "main_bg_color": "var(--color-background)",
                "widget_columns": "repeat(auto-fit, minmax(300px, 1fr))",
                "widget_gap": "var(--spacing-lg)"
            })
        
        return config
    
    async def _generate_components(self, components: List[ComponentConfig],
                                 theme: ThemeType,
                                 user_preferences: Dict[str, Any]) -> Tuple[str, str, str]:
        """生成组件"""
        all_html = ""
        all_css = ""
        all_js = ""
        
        for component_config in components:
            component_html, component_css, component_js = await self._generate_single_component(
                component_config, theme, user_preferences
            )
            
            all_html += component_html + "\n"
            all_css += component_css + "\n"
            all_js += component_js + "\n"
        
        return all_html, all_css, all_js
    
    async def _generate_single_component(self, config: ComponentConfig,
                                       theme: ThemeType,
                                       user_preferences: Dict[str, Any]) -> Tuple[str, str, str]:
        """生成单个组件"""
        component_type = config.component_type.value
        component_def = self.component_library.get_component(component_type)
        
        if not component_def:
            logger.warning(f"未找到组件定义: {component_type}")
            return "", "", ""
        
        # 构建组件配置
        component_config = await self._build_component_config(config, theme, user_preferences)
        
        # 生成HTML
        html = component_def["html_template"].format(**component_config)
        
        # 生成CSS
        css = component_def["css_template"].format(**component_config)
        
        # 生成JavaScript
        js = component_def.get("js_template", "").format(**component_config)
        
        return html, css, js
    
    async def _build_component_config(self, config: ComponentConfig,
                                    theme: ThemeType,
                                    user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """构建组件配置"""
        # 基础配置
        component_config = {
            "id": config.component_id,
            "classes": f"{config.component_type.value}-component",
            "attributes": "",
        }
        
        # 合并props
        component_config.update(config.props)
        
        # 应用样式
        component_config.update(config.styles)
        
        # 根据组件类型设置默认值
        component_type = config.component_type
        
        if component_type == ComponentType.BUTTON:
            component_config.setdefault("variant", "primary")
            component_config.setdefault("padding", "var(--spacing-sm) var(--spacing-md)")
            component_config.setdefault("border_radius", "var(--border-radius-md)")
            component_config.setdefault("font_size", "var(--font-size-base)")
            component_config.setdefault("font_weight", "var(--font-weight-medium)")
            
        elif component_type == ComponentType.INPUT:
            component_config.setdefault("variant", "default")
            component_config.setdefault("padding", "var(--spacing-sm)")
            component_config.setdefault("border_radius", "var(--border-radius-md)")
            component_config.setdefault("font_size", "var(--font-size-base)")
            
        elif component_type == ComponentType.CARD:
            component_config.setdefault("variant", "default")
            component_config.setdefault("border_radius", "var(--border-radius-lg)")
            component_config.setdefault("header_padding", "var(--spacing-md)")
            component_config.setdefault("body_padding", "var(--spacing-md)")
            component_config.setdefault("footer_padding", "var(--spacing-md)")
        
        # 应用主题变体
        variant = component_config.get("variant", "default")
        component_def = self.component_library.get_component(config.component_type.value)
        if component_def and "variants" in component_def:
            variant_config = component_def["variants"].get(variant, {})
            component_config.update(variant_config)
        
        # 应用用户偏好
        if user_preferences.get("large_fonts"):
            component_config["font_size"] = "1.125em"
        
        if user_preferences.get("high_contrast"):
            component_config["border"] = "2px solid var(--color-border)"
        
        return component_config
    
    async def _generate_accessibility_css(self, accessibility_features: List[str]) -> str:
        """生成可访问性CSS"""
        accessibility_css = ""
        
        if "high_contrast" in accessibility_features:
            accessibility_css += """
            .high-contrast {
                filter: contrast(150%);
            }
            """
        
        if "large_fonts" in accessibility_features:
            accessibility_css += """
            .large-fonts {
                font-size: 1.25em;
            }
            """
        
        if "focus_indicators" in accessibility_features:
            accessibility_css += """
            *:focus {
                outline: 3px solid var(--color-primary);
                outline-offset: 2px;
            }
            """
        
        if "reduced_motion" in accessibility_features:
            accessibility_css += """
            @media (prefers-reduced-motion: reduce) {
                * {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
            """
        
        return accessibility_css
    
    async def _optimize_css(self, css: str) -> str:
        """优化CSS"""
        # 移除多余的空白和注释
        optimized = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = re.sub(r';\s*}', '}', optimized)
        optimized = re.sub(r'{\s*', '{', optimized)
        optimized = re.sub(r'}\s*', '}', optimized)
        
        return optimized.strip()
    
    async def _optimize_js(self, js: str) -> str:
        """优化JavaScript"""
        # 移除多余的空白和注释
        optimized = re.sub(r'//.*?\n', '\n', js)
        optimized = re.sub(r'/\*.*?\*/', '', optimized, flags=re.DOTALL)
        optimized = re.sub(r'\s+', ' ', optimized)
        
        return optimized.strip()
    
    async def _generate_complete_html(self, body_html: str, css: str, js: str,
                                    requirements: UIRequirements) -> str:
        """生成完整HTML"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <style>
        {css}
    </style>
</head>
<body class="{body_classes}">
    {body_content}
    
    <script>
        {javascript}
    </script>
</body>
</html>
        """
        
        # 构建HTML配置
        html_config = {
            "title": requirements.context.get("title", "SmartUI Generated Interface"),
            "description": requirements.context.get("description", "Dynamically generated user interface"),
            "css": css,
            "body_content": body_html,
            "javascript": js,
            "body_classes": f"theme-{requirements.theme.value} " + " ".join(requirements.accessibility_features)
        }
        
        return html_template.format(**html_config)
    
    def _generate_interface_id(self, requirements: UIRequirements) -> str:
        """生成界面ID"""
        # 基于需求生成唯一ID
        requirements_str = json.dumps(asdict(requirements), sort_keys=True)
        return hashlib.md5(requirements_str.encode()).hexdigest()[:12]
    
    async def update_interface(self, interface_id: str, updates: Dict[str, Any]) -> Dict[str, str]:
        """更新现有界面"""
        if interface_id not in self.generated_interfaces:
            raise ValueError(f"界面不存在: {interface_id}")
        
        interface_data = self.generated_interfaces[interface_id]
        requirements = UIRequirements(**interface_data["requirements"])
        
        # 应用更新
        if "theme" in updates:
            requirements.theme = ThemeType(updates["theme"])
        
        if "layout_type" in updates:
            requirements.layout_type = LayoutType(updates["layout_type"])
        
        if "accessibility_features" in updates:
            requirements.accessibility_features = updates["accessibility_features"]
        
        if "user_preferences" in updates:
            requirements.user_preferences.update(updates["user_preferences"])
        
        # 重新生成界面
        return await self.generate_interface(requirements)
    
    def get_interface(self, interface_id: str) -> Optional[Dict[str, Any]]:
        """获取界面"""
        return self.generated_interfaces.get(interface_id)
    
    def list_interfaces(self) -> List[Dict[str, Any]]:
        """列出所有界面"""
        return [
            {
                "interface_id": interface_id,
                "created_at": data["created_at"],
                "generation_time": data["generation_time"],
                "theme": data["requirements"]["theme"],
                "layout_type": data["requirements"]["layout_type"]
            }
            for interface_id, data in self.generated_interfaces.items()
        ]
    
    def get_generation_analytics(self) -> Dict[str, Any]:
        """获取生成分析"""
        if not self.generated_interfaces:
            return {"total_interfaces": 0}
        
        total_interfaces = len(self.generated_interfaces)
        avg_generation_time = sum(
            data["generation_time"] for data in self.generated_interfaces.values()
        ) / total_interfaces
        
        # 统计主题分布
        theme_counts = {}
        layout_counts = {}
        
        for data in self.generated_interfaces.values():
            theme = data["requirements"]["theme"]
            layout = data["requirements"]["layout_type"]
            
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
            layout_counts[layout] = layout_counts.get(layout, 0) + 1
        
        return {
            "total_interfaces": total_interfaces,
            "average_generation_time": avg_generation_time,
            "theme_distribution": theme_counts,
            "layout_distribution": layout_counts,
            "cache_size": len(self.template_cache)
        }

if __name__ == "__main__":
    # 测试代码
    async def test_ui_generator():
        generator = UIGenerator()
        
        # 创建测试需求
        test_requirements = UIRequirements(
            layout_type=LayoutType.DASHBOARD,
            theme=ThemeType.LIGHT,
            components=[
                ComponentConfig(
                    component_type=ComponentType.BUTTON,
                    component_id="test_button",
                    props={"text": "Click Me", "variant": "primary"},
                    styles={},
                    events={"click": "alert('Button clicked!')"}
                ),
                ComponentConfig(
                    component_type=ComponentType.CARD,
                    component_id="test_card",
                    props={"header": "Test Card", "content": "This is a test card"},
                    styles={"variant": "elevated"},
                    events={}
                )
            ],
            responsive_breakpoints={"mobile": 768, "tablet": 1024, "desktop": 1200},
            accessibility_features=["focus_indicators", "high_contrast"],
            performance_requirements={"max_load_time": 2000},
            user_preferences={"theme": "light", "large_fonts": False},
            context={"title": "Test Interface", "description": "Generated test interface"}
        )
        
        # 生成界面
        result = await generator.generate_interface(test_requirements)
        
        print("生成结果:")
        print(f"Interface ID: {result.get('interface_id')}")
        print(f"Generation Time: {result.get('generation_time'):.3f}s")
        print(f"HTML Length: {len(result.get('html', ''))}")
        print(f"CSS Length: {len(result.get('css', ''))}")
        print(f"JS Length: {len(result.get('js', ''))}")
        
        # 获取分析报告
        analytics = generator.get_generation_analytics()
        print(f"\n分析报告: {json.dumps(analytics, indent=2, ensure_ascii=False)}")
    
    # 运行测试
    asyncio.run(test_ui_generator())

