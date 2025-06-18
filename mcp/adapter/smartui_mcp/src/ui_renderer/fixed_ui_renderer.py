"""
SmartUI MCP - 基础UI渲染器

实现基础的UI渲染功能，负责将UIConfiguration转换为实际的HTML/CSS/JavaScript代码。
提供VS Code风格的专业界面基础，支持智能感知和动态更新。
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
import jinja2
import copy

from ..common import (
    IUIRenderer, EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    UIConfiguration, UIComponent, ComponentType, LayoutType, ThemeType,
    ComponentProps, ComponentStyle, LayoutConfig, ThemeConfig
)


class RenderMode(str, Enum):
    """渲染模式枚举"""
    STATIC = "static"
    DYNAMIC = "dynamic"
    REACTIVE = "reactive"
    STREAMING = "streaming"


class RenderTarget(str, Enum):
    """渲染目标枚举"""
    HTML = "html"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"


@dataclass
class RenderContext:
    """渲染上下文"""
    context_id: str
    render_mode: RenderMode
    render_target: RenderTarget
    user_preferences: Dict[str, Any]
    device_info: Dict[str, Any]
    theme_overrides: Dict[str, Any]
    accessibility_options: Dict[str, Any]
    performance_hints: Dict[str, Any]
    timestamp: datetime
    
    def __post_init__(self):
        if self.context_id is None:
            self.context_id = generate_id("render_ctx_")


@dataclass
class RenderResult:
    """渲染结果"""
    result_id: str
    html_content: str
    css_content: str
    js_content: str
    assets: List[str]
    metadata: Dict[str, Any]
    render_time: float
    cache_key: Optional[str] = None
    
    def __post_init__(self):
        if self.result_id is None:
            self.result_id = generate_id("render_result_")


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Jinja2环境
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 注册自定义过滤器
        self._register_custom_filters()
        
        # 模板缓存
        self.template_cache = {}
        
        # 创建默认模板
        self._create_default_templates()
    
    def get_template(self, template_name: str) -> jinja2.Template:
        """获取模板"""
        if template_name not in self.template_cache:
            try:
                template = self.jinja_env.get_template(template_name)
                self.template_cache[template_name] = template
            except jinja2.TemplateNotFound:
                # 使用默认模板
                template = self.jinja_env.get_template("base.html")
                self.template_cache[template_name] = template
        
        return self.template_cache[template_name]
    
    def render_template(
        self,
        template_name: str,
        context: Dict[str, Any]
    ) -> str:
        """渲染模板"""
        template = self.get_template(template_name)
        return template.render(**context)
    
    def _register_custom_filters(self) -> None:
        """注册自定义过滤器"""
        
        def component_class(component: UIComponent) -> str:
            """生成组件CSS类名"""
            classes = [f"smartui-{component.type.value}"]
            
            if component.props and component.props.variant:
                classes.append(f"smartui-{component.type.value}--{component.props.variant}")
            
            if component.props and component.props.size:
                classes.append(f"smartui-{component.type.value}--{component.props.size}")
            
            if component.props and component.props.disabled:
                classes.append("smartui-disabled")
            
            if component.props and component.props.css_class:
                classes.append(component.props.css_class)
            
            return " ".join(classes)
        
        def component_style(component: UIComponent) -> str:
            """生成组件内联样式"""
            if not component.style:
                return ""
            
            styles = []
            style_dict = asdict(component.style)
            
            for key, value in style_dict.items():
                if value is not None:
                    css_key = key.replace('_', '-')
                    styles.append(f"{css_key}: {value}")
            
            return "; ".join(styles)
        
        def theme_var(theme: ThemeConfig, var_name: str) -> str:
            """获取主题变量"""
            if var_name in theme.colors:
                return theme.colors[var_name]
            elif var_name in theme.spacing:
                return theme.spacing[var_name]
            elif var_name in theme.typography:
                return theme.typography[var_name]
            else:
                return f"var(--{var_name})"
        
        def accessibility_attrs(component: UIComponent) -> str:
            """生成可访问性属性"""
            attrs = []
            
            if component.props:
                if component.props.aria_label:
                    attrs.append(f'aria-label="{component.props.aria_label}"')
                if component.props.aria_describedby:
                    attrs.append(f'aria-describedby="{component.props.aria_describedby}"')
                if component.props.role:
                    attrs.append(f'role="{component.props.role}"')
                if component.props.tabindex is not None:
                    attrs.append(f'tabindex="{component.props.tabindex}"')
            
            return " ".join(attrs)
        
        # 注册过滤器
        self.jinja_env.filters['component_class'] = component_class
        self.jinja_env.filters['component_style'] = component_style
        self.jinja_env.filters['theme_var'] = theme_var
        self.jinja_env.filters['accessibility_attrs'] = accessibility_attrs
    
    def _create_default_templates(self) -> None:
        """创建默认模板"""
        
        # 基础HTML模板
        base_template = '''<!DOCTYPE html>
<html lang="{{ lang | default('en') }}" data-theme="{{ theme.name }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title | default('SmartUI MCP') }}</title>
    
    <!-- SmartUI Core Styles -->
    <link rel="stylesheet" href="/static/css/smartui-core.css">
    <link rel="stylesheet" href="/static/css/smartui-theme-{{ theme.name }}.css">
    
    <!-- Custom Styles -->
    <style>
        {{ custom_css | safe }}
    </style>
    
    {% block head %}{% endblock %}
</head>
<body class="smartui-body smartui-layout-{{ layout.type.value }}">
    <div id="smartui-app" class="smartui-app">
        <!-- Header -->
        {% if layout.header_visible %}
        <header class="smartui-header" style="height: {{ layout.header_height }}">
            {% block header %}
                <div class="smartui-header-content">
                    <h1 class="smartui-header-title">{{ title | default('SmartUI MCP') }}</h1>
                    <div class="smartui-header-actions">
                        {% for action in header_actions | default([]) %}
                            {{ render_component(action) }}
                        {% endfor %}
                    </div>
                </div>
            {% endblock %}
        </header>
        {% endif %}
        
        <div class="smartui-main-container">
            <!-- Sidebar -->
            {% if layout.sidebar_visible %}
            <aside class="smartui-sidebar {{ 'smartui-sidebar--collapsed' if layout.sidebar_collapsed }}" 
                   style="width: {{ layout.sidebar_width }}">
                {% block sidebar %}
                    <nav class="smartui-sidebar-nav">
                        {% for nav_item in sidebar_items | default([]) %}
                            {{ render_component(nav_item) }}
                        {% endfor %}
                    </nav>
                {% endblock %}
            </aside>
            {% endif %}
            
            <!-- Main Content -->
            <main class="smartui-main-content">
                {% block content %}
                    <div class="smartui-content-container">
                        {% for component in components %}
                            {{ render_component(component) }}
                        {% endfor %}
                    </div>
                {% endblock %}
            </main>
        </div>
        
        <!-- Footer -->
        {% if layout.footer_visible %}
        <footer class="smartui-footer" style="height: {{ layout.footer_height }}">
            {% block footer %}
                <div class="smartui-footer-content">
                    <p>&copy; 2024 SmartUI MCP. All rights reserved.</p>
                </div>
            {% endblock %}
        </footer>
        {% endif %}
    </div>
    
    <!-- SmartUI Core Scripts -->
    <script src="/static/js/smartui-core.js"></script>
    <script src="/static/js/smartui-components.js"></script>
    
    <!-- Custom Scripts -->
    <script>
        {{ custom_js | safe }}
    </script>
    
    {% block scripts %}{% endblock %}
</body>
</html>'''
        
        # 组件渲染宏
        component_macros = '''
{% macro render_component(component) %}
    {% set comp_type = component.type.value %}
    
    {% if comp_type == 'button' %}
        {{ render_button(component) }}
    {% elif comp_type == 'input' %}
        {{ render_input(component) }}
    {% elif comp_type == 'textarea' %}
        {{ render_textarea(component) }}
    {% elif comp_type == 'select' %}
        {{ render_select(component) }}
    {% elif comp_type == 'checkbox' %}
        {{ render_checkbox(component) }}
    {% elif comp_type == 'radio' %}
        {{ render_radio(component) }}
    {% elif comp_type == 'card' %}
        {{ render_card(component) }}
    {% elif comp_type == 'modal' %}
        {{ render_modal(component) }}
    {% elif comp_type == 'table' %}
        {{ render_table(component) }}
    {% elif comp_type == 'list' %}
        {{ render_list(component) }}
    {% elif comp_type == 'navigation' %}
        {{ render_navigation(component) }}
    {% elif comp_type == 'breadcrumb' %}
        {{ render_breadcrumb(component) }}
    {% elif comp_type == 'tabs' %}
        {{ render_tabs(component) }}
    {% elif comp_type == 'accordion' %}
        {{ render_accordion(component) }}
    {% elif comp_type == 'progress' %}
        {{ render_progress(component) }}
    {% elif comp_type == 'spinner' %}
        {{ render_spinner(component) }}
    {% elif comp_type == 'alert' %}
        {{ render_alert(component) }}
    {% elif comp_type == 'tooltip' %}
        {{ render_tooltip(component) }}
    {% elif comp_type == 'popover' %}
        {{ render_popover(component) }}
    {% elif comp_type == 'dropdown' %}
        {{ render_dropdown(component) }}
    {% elif comp_type == 'slider' %}
        {{ render_slider(component) }}
    {% elif comp_type == 'switch' %}
        {{ render_switch(component) }}
    {% elif comp_type == 'badge' %}
        {{ render_badge(component) }}
    {% elif comp_type == 'avatar' %}
        {{ render_avatar(component) }}
    {% elif comp_type == 'image' %}
        {{ render_image(component) }}
    {% elif comp_type == 'video' %}
        {{ render_video(component) }}
    {% elif comp_type == 'audio' %}
        {{ render_audio(component) }}
    {% elif comp_type == 'chart' %}
        {{ render_chart(component) }}
    {% elif comp_type == 'calendar' %}
        {{ render_calendar(component) }}
    {% elif comp_type == 'date_picker' %}
        {{ render_date_picker(component) }}
    {% elif comp_type == 'time_picker' %}
        {{ render_time_picker(component) }}
    {% elif comp_type == 'color_picker' %}
        {{ render_color_picker(component) }}
    {% elif comp_type == 'file_upload' %}
        {{ render_file_upload(component) }}
    {% elif comp_type == 'code_editor' %}
        {{ render_code_editor(component) }}
    {% elif comp_type == 'rich_text_editor' %}
        {{ render_rich_text_editor(component) }}
    {% elif comp_type == 'markdown_editor' %}
        {{ render_markdown_editor(component) }}
    {% elif comp_type == 'search' %}
        {{ render_search(component) }}
    {% elif comp_type == 'pagination' %}
        {{ render_pagination(component) }}
    {% elif comp_type == 'tree' %}
        {{ render_tree(component) }}
    {% elif comp_type == 'kanban' %}
        {{ render_kanban(component) }}
    {% elif comp_type == 'timeline' %}
        {{ render_timeline(component) }}
    {% elif comp_type == 'stepper' %}
        {{ render_stepper(component) }}
    {% elif comp_type == 'rating' %}
        {{ render_rating(component) }}
    {% elif comp_type == 'divider' %}
        {{ render_divider(component) }}
    {% elif comp_type == 'spacer' %}
        {{ render_spacer(component) }}
    {% elif comp_type == 'container' %}
        {{ render_container(component) }}
    {% elif comp_type == 'grid' %}
        {{ render_grid(component) }}
    {% elif comp_type == 'flex' %}
        {{ render_flex(component) }}
    {% elif comp_type == 'link' %}
        {{ render_link(component) }}
    {% elif comp_type == 'text' %}
        {{ render_text(component) }}
    {% elif comp_type == 'heading' %}
        {{ render_heading(component) }}
    {% elif comp_type == 'paragraph' %}
        {{ render_paragraph(component) }}
    {% elif comp_type == 'blockquote' %}
        {{ render_blockquote(component) }}
    {% elif comp_type == 'code' %}
        {{ render_code(component) }}
    {% elif comp_type == 'pre' %}
        {{ render_pre(component) }}
    {% elif comp_type == 'hr' %}
        {{ render_hr(component) }}
    {% elif comp_type == 'br' %}
        {{ render_br(component) }}
    {% else %}
        {{ render_custom_component(component) }}
    {% endif %}
{% endmacro %}

{% macro render_button(component) %}
<button id="{{ component.id }}" 
        class="{{ component | component_class }}"
        style="{{ component | component_style }}"
        {{ component | accessibility_attrs | safe }}
        {% if component.props %}
            {% if component.props.disabled %}disabled{% endif %}
            {% if component.props.onclick %}onclick="{{ component.props.onclick }}"{% endif %}
            {% if component.props.type %}type="{{ component.props.type }}"{% endif %}
        {% endif %}>
    {% if component.props and component.props.icon %}
        <i class="smartui-icon {{ component.props.icon }}"></i>
    {% endif %}
    {{ component.text | default('Button') }}
</button>
{% endmacro %}

{% macro render_input(component) %}
<div class="smartui-input-wrapper">
    {% if component.props and component.props.label %}
        <label for="{{ component.id }}" class="smartui-input-label">
            {{ component.props.label }}
            {% if component.props.required %}<span class="smartui-required">*</span>{% endif %}
        </label>
    {% endif %}
    <input id="{{ component.id }}"
           class="{{ component | component_class }}"
           style="{{ component | component_style }}"
           {{ component | accessibility_attrs | safe }}
           {% if component.props %}
               {% if component.props.type %}type="{{ component.props.type }}"{% endif %}
               {% if component.props.placeholder %}placeholder="{{ component.props.placeholder }}"{% endif %}
               {% if component.props.value %}value="{{ component.props.value }}"{% endif %}
               {% if component.props.disabled %}disabled{% endif %}
               {% if component.props.readonly %}readonly{% endif %}
               {% if component.props.required %}required{% endif %}
               {% if component.props.min %}min="{{ component.props.min }}"{% endif %}
               {% if component.props.max %}max="{{ component.props.max }}"{% endif %}
               {% if component.props.step %}step="{{ component.props.step }}"{% endif %}
               {% if component.props.pattern %}pattern="{{ component.props.pattern }}"{% endif %}
               {% if component.props.maxlength %}maxlength="{{ component.props.maxlength }}"{% endif %}
           {% endif %}>
    {% if component.props and component.props.help_text %}
        <div class="smartui-input-help">{{ component.props.help_text }}</div>
    {% endif %}
</div>
{% endmacro %}

{% macro render_card(component) %}
<div id="{{ component.id }}"
     class="{{ component | component_class }}"
     style="{{ component | component_style }}"
     {{ component | accessibility_attrs | safe }}>
    {% if component.props and component.props.header %}
        <div class="smartui-card-header">
            {% if component.props.title %}
                <h3 class="smartui-card-title">{{ component.props.title }}</h3>
            {% endif %}
            {% if component.props.subtitle %}
                <p class="smartui-card-subtitle">{{ component.props.subtitle }}</p>
            {% endif %}
        </div>
    {% endif %}
    
    <div class="smartui-card-content">
        {{ component.text | default('') | safe }}
        {% if component.children %}
            {% for child in component.children %}
                {{ render_component(child) }}
            {% endfor %}
        {% endif %}
    </div>
    
    {% if component.props and component.props.footer %}
        <div class="smartui-card-footer">
            {% if component.props.actions %}
                {% for action in component.props.actions %}
                    {{ render_component(action) }}
                {% endfor %}
            {% endif %}
        </div>
    {% endif %}
</div>
{% endmacro %}

{% macro render_custom_component(component) %}
<div id="{{ component.id }}"
     class="{{ component | component_class }} smartui-custom-component"
     style="{{ component | component_style }}"
     {{ component | accessibility_attrs | safe }}
     data-component-type="{{ component.type.value }}">
    {{ component.text | default('') | safe }}
    {% if component.children %}
        {% for child in component.children %}
            {{ render_component(child) }}
        {% endfor %}
    {% endif %}
</div>
{% endmacro %}
'''
        
        # 保存模板文件
        (self.template_dir / "base.html").write_text(base_template, encoding='utf-8')
        (self.template_dir / "components.html").write_text(component_macros, encoding='utf-8')


class StyleGenerator:
    """样式生成器"""
    
    def __init__(self, static_dir: str):
        self.static_dir = Path(static_dir)
        self.css_dir = self.static_dir / "css"
        self.css_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建核心样式文件
        self._create_core_styles()
        self._create_theme_styles()
    
    def generate_theme_css(self, theme: ThemeConfig) -> str:
        """生成主题CSS"""
        css_vars = []
        
        # 颜色变量
        for name, value in theme.colors.items():
            css_vars.append(f"  --smartui-color-{name}: {value};")
        
        # 间距变量
        for name, value in theme.spacing.items():
            css_vars.append(f"  --smartui-spacing-{name}: {value};")
        
        # 字体变量
        for name, value in theme.typography.items():
            css_vars.append(f"  --smartui-typography-{name}: {value};")
        
        # 阴影变量
        for name, value in theme.shadows.items():
            css_vars.append(f"  --smartui-shadow-{name}: {value};")
        
        # 边框变量
        for name, value in theme.borders.items():
            css_vars.append(f"  --smartui-border-{name}: {value};")
        
        # 动画变量
        for name, value in theme.animations.items():
            if isinstance(value, (str, int, float)):
                css_vars.append(f"  --smartui-animation-{name}: {value};")
        
        css_content = f"""/* SmartUI Theme: {theme.name} */
:root {{
{chr(10).join(css_vars)}
}}

/* Theme-specific overrides */
[data-theme="{theme.name}"] {{
  background-color: var(--smartui-color-background);
  color: var(--smartui-color-text);
}}
"""
        
        return css_content
    
    def generate_component_css(self, component_type: ComponentType) -> str:
        """生成组件CSS"""
        component_name = component_type.value
        
        css_content = f"""/* SmartUI Component: {component_name} */
.smartui-{component_name} {{
  /* Base styles */
  box-sizing: border-box;
  font-family: var(--smartui-typography-font-family);
  font-size: var(--smartui-typography-base-size);
  line-height: var(--smartui-typography-line-height);
  
  /* Default spacing */
  margin: 0;
  padding: var(--smartui-spacing-base);
  
  /* Default colors */
  color: var(--smartui-color-text);
  background-color: transparent;
  
  /* Default borders */
  border: var(--smartui-border-width) solid var(--smartui-color-border);
  border-radius: var(--smartui-border-radius);
  
  /* Transitions */
  transition: all var(--smartui-animation-duration) var(--smartui-animation-easing);
}}

.smartui-{component_name}:hover {{
  /* Hover states */
  background-color: var(--smartui-color-hover);
  border-color: var(--smartui-color-border-hover);
}}

.smartui-{component_name}:focus {{
  /* Focus states */
  outline: 2px solid var(--smartui-color-focus);
  outline-offset: 2px;
}}

.smartui-{component_name}.smartui-disabled {{
  /* Disabled states */
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}}
"""
        
        # 添加特定组件的样式
        if component_type == ComponentType.BUTTON:
            css_content += self._get_button_styles()
        elif component_type == ComponentType.INPUT:
            css_content += self._get_input_styles()
        elif component_type == ComponentType.CARD:
            css_content += self._get_card_styles()
        
        return css_content
    
    def _create_core_styles(self) -> None:
        """创建核心样式"""
        core_css = """/* SmartUI MCP - Core Styles */

/* Reset and base styles */
* {
  box-sizing: border-box;
}

html {
  font-size: 16px;
  line-height: 1.5;
}

body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  background-color: var(--smartui-color-background);
  color: var(--smartui-color-text);
}

/* Layout components */
.smartui-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.smartui-header {
  flex-shrink: 0;
  background-color: var(--smartui-color-surface);
  border-bottom: 1px solid var(--smartui-color-border);
  padding: 0 var(--smartui-spacing-large);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.smartui-main-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.smartui-sidebar {
  flex-shrink: 0;
  background-color: var(--smartui-color-surface);
  border-right: 1px solid var(--smartui-color-border);
  overflow-y: auto;
  transition: width var(--smartui-animation-duration) var(--smartui-animation-easing);
}

.smartui-sidebar--collapsed {
  width: 60px !important;
}

.smartui-main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--smartui-spacing-large);
}

.smartui-footer {
  flex-shrink: 0;
  background-color: var(--smartui-color-surface);
  border-top: 1px solid var(--smartui-color-border);
  padding: var(--smartui-spacing-base) var(--smartui-spacing-large);
  text-align: center;
}

/* Responsive layout */
@media (max-width: 768px) {
  .smartui-layout-mobile .smartui-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
  }
  
  .smartui-layout-mobile .smartui-sidebar.smartui-sidebar--open {
    transform: translateX(0);
  }
  
  .smartui-layout-mobile .smartui-main-content {
    margin-left: 0;
  }
}

/* Utility classes */
.smartui-hidden {
  display: none !important;
}

.smartui-sr-only {
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

.smartui-loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Animation classes */
.smartui-fade-in {
  animation: smartui-fadeIn var(--smartui-animation-duration) var(--smartui-animation-easing);
}

.smartui-slide-in {
  animation: smartui-slideIn var(--smartui-animation-duration) var(--smartui-animation-easing);
}

@keyframes smartui-fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes smartui-slideIn {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
"""
        
        (self.css_dir / "smartui-core.css").write_text(core_css, encoding='utf-8')
    
    def _create_theme_styles(self) -> None:
        """创建主题样式"""
        
        # Light theme
        light_theme_css = """/* SmartUI Light Theme */
:root {
  /* Colors */
  --smartui-color-primary: #007acc;
  --smartui-color-secondary: #6c757d;
  --smartui-color-success: #28a745;
  --smartui-color-warning: #ffc107;
  --smartui-color-error: #dc3545;
  --smartui-color-info: #17a2b8;
  
  --smartui-color-background: #ffffff;
  --smartui-color-surface: #f8f9fa;
  --smartui-color-text: #212529;
  --smartui-color-text-secondary: #6c757d;
  --smartui-color-border: #dee2e6;
  --smartui-color-border-hover: #adb5bd;
  --smartui-color-hover: #e9ecef;
  --smartui-color-focus: #007acc;
  
  /* Spacing */
  --smartui-spacing-xs: 4px;
  --smartui-spacing-small: 8px;
  --smartui-spacing-base: 16px;
  --smartui-spacing-large: 24px;
  --smartui-spacing-xl: 32px;
  
  /* Typography */
  --smartui-typography-font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  --smartui-typography-base-size: 14px;
  --smartui-typography-line-height: 1.5;
  --smartui-typography-font-weight: 400;
  --smartui-typography-font-weight-bold: 600;
  
  /* Shadows */
  --smartui-shadow-small: 0 1px 3px rgba(0, 0, 0, 0.1);
  --smartui-shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.1);
  --smartui-shadow-large: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Borders */
  --smartui-border-width: 1px;
  --smartui-border-radius: 4px;
  --smartui-border-radius-large: 8px;
  
  /* Animations */
  --smartui-animation-duration: 0.2s;
  --smartui-animation-easing: ease-in-out;
}
"""
        
        # Dark theme (VS Code style)
        dark_theme_css = """/* SmartUI Dark Theme (VS Code Style) */
[data-theme="dark"] {
  /* Colors */
  --smartui-color-primary: #007acc;
  --smartui-color-secondary: #858585;
  --smartui-color-success: #4ec9b0;
  --smartui-color-warning: #dcdcaa;
  --smartui-color-error: #f44747;
  --smartui-color-info: #9cdcfe;
  
  --smartui-color-background: #1e1e1e;
  --smartui-color-surface: #252526;
  --smartui-color-text: #cccccc;
  --smartui-color-text-secondary: #858585;
  --smartui-color-border: #3c3c3c;
  --smartui-color-border-hover: #464647;
  --smartui-color-hover: #2a2d2e;
  --smartui-color-focus: #007acc;
  
  /* Shadows */
  --smartui-shadow-small: 0 1px 3px rgba(0, 0, 0, 0.3);
  --smartui-shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.3);
  --smartui-shadow-large: 0 10px 15px rgba(0, 0, 0, 0.3);
}
"""
        
        # High contrast theme
        high_contrast_css = """/* SmartUI High Contrast Theme */
[data-theme="high_contrast"] {
  /* Colors */
  --smartui-color-primary: #ffffff;
  --smartui-color-secondary: #ffffff;
  --smartui-color-success: #00ff00;
  --smartui-color-warning: #ffff00;
  --smartui-color-error: #ff0000;
  --smartui-color-info: #00ffff;
  
  --smartui-color-background: #000000;
  --smartui-color-surface: #000000;
  --smartui-color-text: #ffffff;
  --smartui-color-text-secondary: #ffffff;
  --smartui-color-border: #ffffff;
  --smartui-color-border-hover: #ffffff;
  --smartui-color-hover: #333333;
  --smartui-color-focus: #ffff00;
  
  /* Borders */
  --smartui-border-width: 2px;
}
"""
        
        (self.css_dir / "smartui-theme-light.css").write_text(light_theme_css, encoding='utf-8')
        (self.css_dir / "smartui-theme-dark.css").write_text(dark_theme_css, encoding='utf-8')
        (self.css_dir / "smartui-theme-high_contrast.css").write_text(high_contrast_css, encoding='utf-8')
    
    def _get_button_styles(self) -> str:
        """获取按钮样式"""
        return """
/* Button variants */
.smartui-button--primary {
  background-color: var(--smartui-color-primary);
  color: white;
  border-color: var(--smartui-color-primary);
}

.smartui-button--secondary {
  background-color: var(--smartui-color-secondary);
  color: white;
  border-color: var(--smartui-color-secondary);
}

.smartui-button--outline {
  background-color: transparent;
  color: var(--smartui-color-primary);
  border-color: var(--smartui-color-primary);
}

.smartui-button--ghost {
  background-color: transparent;
  color: var(--smartui-color-primary);
  border-color: transparent;
}

/* Button sizes */
.smartui-button--small {
  padding: var(--smartui-spacing-xs) var(--smartui-spacing-small);
  font-size: 12px;
}

.smartui-button--large {
  padding: var(--smartui-spacing-base) var(--smartui-spacing-large);
  font-size: 16px;
}

/* Button states */
.smartui-button:hover:not(.smartui-disabled) {
  transform: translateY(-1px);
  box-shadow: var(--smartui-shadow-medium);
}

.smartui-button:active:not(.smartui-disabled) {
  transform: translateY(0);
}
"""
    
    def _get_input_styles(self) -> str:
        """获取输入框样式"""
        return """
/* Input wrapper */
.smartui-input-wrapper {
  margin-bottom: var(--smartui-spacing-base);
}

.smartui-input-label {
  display: block;
  margin-bottom: var(--smartui-spacing-xs);
  font-weight: var(--smartui-typography-font-weight-bold);
  color: var(--smartui-color-text);
}

.smartui-required {
  color: var(--smartui-color-error);
  margin-left: 2px;
}

.smartui-input-help {
  margin-top: var(--smartui-spacing-xs);
  font-size: 12px;
  color: var(--smartui-color-text-secondary);
}

/* Input states */
.smartui-input:focus {
  border-color: var(--smartui-color-focus);
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
}

.smartui-input:invalid {
  border-color: var(--smartui-color-error);
}

.smartui-input:disabled {
  background-color: var(--smartui-color-surface);
  cursor: not-allowed;
}
"""
    
    def _get_card_styles(self) -> str:
        """获取卡片样式"""
        return """
/* Card structure */
.smartui-card {
  background-color: var(--smartui-color-surface);
  border: var(--smartui-border-width) solid var(--smartui-color-border);
  border-radius: var(--smartui-border-radius);
  box-shadow: var(--smartui-shadow-small);
  overflow: hidden;
}

.smartui-card-header {
  padding: var(--smartui-spacing-base);
  border-bottom: var(--smartui-border-width) solid var(--smartui-color-border);
  background-color: var(--smartui-color-background);
}

.smartui-card-title {
  margin: 0 0 var(--smartui-spacing-xs) 0;
  font-size: 18px;
  font-weight: var(--smartui-typography-font-weight-bold);
  color: var(--smartui-color-text);
}

.smartui-card-subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--smartui-color-text-secondary);
}

.smartui-card-content {
  padding: var(--smartui-spacing-base);
}

.smartui-card-footer {
  padding: var(--smartui-spacing-base);
  border-top: var(--smartui-border-width) solid var(--smartui-color-border);
  background-color: var(--smartui-color-background);
  display: flex;
  gap: var(--smartui-spacing-small);
  justify-content: flex-end;
}

/* Card hover effect */
.smartui-card:hover {
  box-shadow: var(--smartui-shadow-medium);
  transform: translateY(-2px);
}
"""


class ScriptGenerator:
    """脚本生成器"""
    
    def __init__(self, static_dir: str):
        self.static_dir = Path(static_dir)
        self.js_dir = self.static_dir / "js"
        self.js_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建核心脚本文件
        self._create_core_scripts()
        self._create_component_scripts()
    
    def generate_component_js(self, component_type: ComponentType) -> str:
        """生成组件JavaScript"""
        component_name = component_type.value
        
        js_content = f"""// SmartUI Component: {component_name}
class SmartUI{component_name.title()}Component {{
  constructor(element) {{
    this.element = element;
    this.id = element.id;
    this.init();
  }}
  
  init() {{
    this.bindEvents();
    this.setupAccessibility();
  }}
  
  bindEvents() {{
    // Component-specific event binding
  }}
  
  setupAccessibility() {{
    // Accessibility enhancements
    if (!this.element.getAttribute('role')) {{
      this.element.setAttribute('role', '{component_name}');
    }}
  }}
  
  destroy() {{
    // Cleanup
  }}
}}

// Register component
SmartUI.registerComponent('{component_name}', SmartUI{component_name.title()}Component);
"""
        
        return js_content
    
    def _create_core_scripts(self) -> None:
        """创建核心脚本"""
        core_js = """// SmartUI MCP - Core JavaScript

class SmartUI {
  constructor() {
    this.components = new Map();
    this.componentClasses = new Map();
    this.eventBus = new EventTarget();
    this.state = new Map();
    this.observers = new Map();
    
    this.init();
  }
  
  init() {
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
    } else {
      this.initializeComponents();
    }
    
    // Setup global event listeners
    this.setupGlobalEvents();
    
    // Setup mutation observer for dynamic content
    this.setupMutationObserver();
  }
  
  initializeComponents() {
    // Find and initialize all SmartUI components
    const elements = document.querySelectorAll('[class*="smartui-"]');
    elements.forEach(element => this.initializeComponent(element));
  }
  
  initializeComponent(element) {
    const classList = Array.from(element.classList);
    const componentClass = classList.find(cls => cls.startsWith('smartui-') && !cls.includes('--'));
    
    if (componentClass) {
      const componentType = componentClass.replace('smartui-', '');
      const ComponentClass = this.componentClasses.get(componentType);
      
      if (ComponentClass && !this.components.has(element)) {
        const component = new ComponentClass(element);
        this.components.set(element, component);
        
        // Emit component initialized event
        this.emit('component:initialized', {
          element,
          component,
          type: componentType
        });
      }
    }
  }
  
  setupGlobalEvents() {
    // Keyboard navigation
    document.addEventListener('keydown', (e) => this.handleGlobalKeydown(e));
    
    // Focus management
    document.addEventListener('focusin', (e) => this.handleFocusIn(e));
    document.addEventListener('focusout', (e) => this.handleFocusOut(e));
    
    // Theme switching
    this.on('theme:change', (e) => this.handleThemeChange(e.detail));
  }
  
  setupMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.initializeComponent(node);
            // Also check children
            const children = node.querySelectorAll('[class*="smartui-"]');
            children.forEach(child => this.initializeComponent(child));
          }
        });
        
        mutation.removedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            this.destroyComponent(node);
          }
        });
      });
    });
    
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }
  
  destroyComponent(element) {
    const component = this.components.get(element);
    if (component && typeof component.destroy === 'function') {
      component.destroy();
      this.components.delete(element);
    }
  }
  
  handleGlobalKeydown(e) {
    // Global keyboard shortcuts
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'k':
          e.preventDefault();
          this.emit('search:focus');
          break;
        case '/':
          e.preventDefault();
          this.emit('help:toggle');
          break;
      }
    }
    
    // Escape key handling
    if (e.key === 'Escape') {
      this.emit('escape:pressed');
    }
  }
  
  handleFocusIn(e) {
    // Add focus class for styling
    e.target.classList.add('smartui-focused');
  }
  
  handleFocusOut(e) {
    // Remove focus class
    e.target.classList.remove('smartui-focused');
  }
  
  handleThemeChange(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('smartui-theme', theme);
    
    // Emit theme changed event
    this.emit('theme:changed', { theme });
  }
  
  // Event system
  on(event, handler) {
    this.eventBus.addEventListener(event, handler);
  }
  
  off(event, handler) {
    this.eventBus.removeEventListener(event, handler);
  }
  
  emit(event, data = {}) {
    this.eventBus.dispatchEvent(new CustomEvent(event, { detail: data }));
  }
  
  // State management
  setState(key, value) {
    const oldValue = this.state.get(key);
    this.state.set(key, value);
    
    // Notify observers
    const observers = this.observers.get(key) || [];
    observers.forEach(observer => observer(value, oldValue));
    
    // Emit state change event
    this.emit('state:change', { key, value, oldValue });
  }
  
  getState(key, defaultValue = null) {
    return this.state.get(key) || defaultValue;
  }
  
  observeState(key, observer) {
    if (!this.observers.has(key)) {
      this.observers.set(key, []);
    }
    this.observers.get(key).push(observer);
    
    // Return unsubscribe function
    return () => {
      const observers = this.observers.get(key) || [];
      const index = observers.indexOf(observer);
      if (index > -1) {
        observers.splice(index, 1);
      }
    };
  }
  
  // Component registration
  static registerComponent(type, ComponentClass) {
    if (!window.smartUI) {
      window.smartUI = new SmartUI();
    }
    window.smartUI.componentClasses.set(type, ComponentClass);
  }
  
  // Utility methods
  static generateId(prefix = 'smartui') {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  
  static throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
}

// Initialize SmartUI
window.smartUI = new SmartUI();

// Expose utilities globally
window.SmartUI = SmartUI;
"""
        
        (self.js_dir / "smartui-core.js").write_text(core_js, encoding='utf-8')
    
    def _create_component_scripts(self) -> None:
        """创建组件脚本"""
        components_js = """// SmartUI MCP - Component Scripts

// Base Component Class
class SmartUIBaseComponent {
  constructor(element) {
    this.element = element;
    this.id = element.id || SmartUI.generateId();
    this.element.id = this.id;
    
    this.state = new Map();
    this.listeners = [];
    
    this.init();
  }
  
  init() {
    this.bindEvents();
    this.setupAccessibility();
    this.setupState();
  }
  
  bindEvents() {
    // Override in subclasses
  }
  
  setupAccessibility() {
    // Basic accessibility setup
    if (!this.element.getAttribute('tabindex') && this.isInteractive()) {
      this.element.setAttribute('tabindex', '0');
    }
  }
  
  setupState() {
    // Initialize component state
  }
  
  isInteractive() {
    return ['button', 'input', 'select', 'textarea', 'a'].includes(this.element.tagName.toLowerCase());
  }
  
  addEventListener(event, handler, options = {}) {
    this.element.addEventListener(event, handler, options);
    this.listeners.push({ event, handler, options });
  }
  
  setState(key, value) {
    this.state.set(key, value);
    this.onStateChange(key, value);
  }
  
  getState(key, defaultValue = null) {
    return this.state.get(key) || defaultValue;
  }
  
  onStateChange(key, value) {
    // Override in subclasses
  }
  
  destroy() {
    // Remove event listeners
    this.listeners.forEach(({ event, handler, options }) => {
      this.element.removeEventListener(event, handler, options);
    });
    this.listeners = [];
    
    // Clear state
    this.state.clear();
  }
}

// Button Component
class SmartUIButtonComponent extends SmartUIBaseComponent {
  bindEvents() {
    this.addEventListener('click', (e) => this.handleClick(e));
    this.addEventListener('keydown', (e) => this.handleKeydown(e));
  }
  
  handleClick(e) {
    if (this.element.disabled) {
      e.preventDefault();
      return;
    }
    
    // Add click animation
    this.element.classList.add('smartui-button--clicked');
    setTimeout(() => {
      this.element.classList.remove('smartui-button--clicked');
    }, 150);
    
    // Emit custom event
    window.smartUI.emit('button:click', {
      id: this.id,
      element: this.element
    });
  }
  
  handleKeydown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      this.element.click();
    }
  }
}

// Input Component
class SmartUIInputComponent extends SmartUIBaseComponent {
  bindEvents() {
    this.addEventListener('input', (e) => this.handleInput(e));
    this.addEventListener('focus', (e) => this.handleFocus(e));
    this.addEventListener('blur', (e) => this.handleBlur(e));
  }
  
  handleInput(e) {
    const value = e.target.value;
    this.setState('value', value);
    
    // Emit input event
    window.smartUI.emit('input:change', {
      id: this.id,
      value: value,
      element: this.element
    });
  }
  
  handleFocus(e) {
    this.element.parentElement?.classList.add('smartui-input-wrapper--focused');
  }
  
  handleBlur(e) {
    this.element.parentElement?.classList.remove('smartui-input-wrapper--focused');
    
    // Validate input
    this.validate();
  }
  
  validate() {
    const isValid = this.element.checkValidity();
    this.element.classList.toggle('smartui-input--invalid', !isValid);
    
    return isValid;
  }
}

// Card Component
class SmartUICardComponent extends SmartUIBaseComponent {
  bindEvents() {
    this.addEventListener('mouseenter', (e) => this.handleMouseEnter(e));
    this.addEventListener('mouseleave', (e) => this.handleMouseLeave(e));
  }
  
  handleMouseEnter(e) {
    this.element.classList.add('smartui-card--hovered');
  }
  
  handleMouseLeave(e) {
    this.element.classList.remove('smartui-card--hovered');
  }
}

// Modal Component
class SmartUIModalComponent extends SmartUIBaseComponent {
  bindEvents() {
    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });
    
    // Close on backdrop click
    this.addEventListener('click', (e) => {
      if (e.target === this.element) {
        this.close();
      }
    });
  }
  
  open() {
    this.element.classList.add('smartui-modal--open');
    document.body.classList.add('smartui-modal-open');
    
    // Focus management
    this.previousFocus = document.activeElement;
    const focusableElement = this.element.querySelector('[autofocus], button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusableElement) {
      focusableElement.focus();
    }
    
    window.smartUI.emit('modal:open', { id: this.id });
  }
  
  close() {
    this.element.classList.remove('smartui-modal--open');
    document.body.classList.remove('smartui-modal-open');
    
    // Restore focus
    if (this.previousFocus) {
      this.previousFocus.focus();
    }
    
    window.smartUI.emit('modal:close', { id: this.id });
  }
  
  isOpen() {
    return this.element.classList.contains('smartui-modal--open');
  }
}

// Register components
SmartUI.registerComponent('button', SmartUIButtonComponent);
SmartUI.registerComponent('input', SmartUIInputComponent);
SmartUI.registerComponent('card', SmartUICardComponent);
SmartUI.registerComponent('modal', SmartUIModalComponent);

// Theme utilities
window.SmartUITheme = {
  setTheme(theme) {
    window.smartUI.emit('theme:change', theme);
  },
  
  getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  },
  
  toggleTheme() {
    const currentTheme = this.getTheme();
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }
};

// Initialize theme from localStorage
const savedTheme = localStorage.getItem('smartui-theme');
if (savedTheme) {
  window.SmartUITheme.setTheme(savedTheme);
}
"""
        
        (self.js_dir / "smartui-components.js").write_text(components_js, encoding='utf-8')


class SmartUIRenderer(IUIRenderer):
    """SmartUI渲染器实现"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 设置目录路径
        self.base_dir = Path(self.config.get("base_dir", "/home/ubuntu/aicore0615/mcp/adapter/smartui_mcp/frontend"))
        self.template_dir = self.base_dir / "templates"
        self.static_dir = self.base_dir / "static"
        
        # 子组件
        self.template_manager = TemplateManager(str(self.template_dir))
        self.style_generator = StyleGenerator(str(self.static_dir))
        self.script_generator = ScriptGenerator(str(self.static_dir))
        
        # 渲染缓存
        self.render_cache = AsyncCache(max_size=100, ttl=600)  # 10分钟缓存
        
        # 性能监控
        self.performance_metrics: Dict[str, float] = {}
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        self.logger.info("SmartUI Renderer initialized")
    
    @log_execution_time()
    async def render_ui_configuration(
        self,
        ui_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """渲染UI配置"""
        try:
            start_time = time.time()
            
            # 解析渲染上下文
            render_context = self._parse_render_context(context or {})
            
            # 生成缓存键
            cache_key = self._generate_cache_key(ui_config, render_context)
            
            # 尝试从缓存获取
            cached_result = await self.render_cache.get(cache_key)
            if cached_result:
                return {
                    "success": True,
                    "render_result": cached_result,
                    "from_cache": True,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 执行渲染
            render_result = await self._execute_render(ui_config, render_context)
            
            # 计算渲染时间
            render_time = time.time() - start_time
            render_result.render_time = render_time
            
            # 缓存结果
            if render_result.cache_key:
                await self.render_cache.set(render_result.cache_key, asdict(render_result))
            
            # 发布渲染事件
            await publish_event(
                event_type=EventBusEventType.UI_RENDERED,
                data={
                    "result_id": render_result.result_id,
                    "render_time": render_time,
                    "component_count": len(ui_config.get("components", [])),
                    "render_mode": render_context.render_mode.value
                },
                source="ui_renderer"
            )
            
            return {
                "success": True,
                "render_result": asdict(render_result),
                "from_cache": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error rendering UI configuration: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_ui_component(
        self,
        component_id: str,
        updates: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """更新UI组件"""
        try:
            # 这里应该实现组件的增量更新逻辑
            # 简化实现，返回成功状态
            
            await publish_event(
                event_type=EventBusEventType.UI_COMPONENT_UPDATED,
                data={
                    "component_id": component_id,
                    "updates": updates
                },
                source="ui_renderer"
            )
            
            return {
                "success": True,
                "component_id": component_id,
                "updates_applied": updates,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error updating UI component {component_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_render_templates(self) -> List[str]:
        """获取可用的渲染模板"""
        try:
            templates = []
            for template_file in self.template_dir.glob("*.html"):
                templates.append(template_file.stem)
            return templates
            
        except Exception as e:
            self.logger.error(f"Error getting render templates: {e}")
            return []
    
    async def _execute_render(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> RenderResult:
        """执行渲染"""
        
        # 准备模板上下文
        template_context = self._prepare_template_context(ui_config, context)
        
        # 选择模板
        template_name = self._select_template(ui_config, context)
        
        # 渲染HTML
        html_content = self.template_manager.render_template(template_name, template_context)
        
        # 生成CSS
        css_content = await self._generate_css(ui_config, context)
        
        # 生成JavaScript
        js_content = await self._generate_js(ui_config, context)
        
        # 收集资源文件
        assets = self._collect_assets(ui_config, context)
        
        return RenderResult(
            result_id=generate_id("render_result_"),
            html_content=html_content,
            css_content=css_content,
            js_content=js_content,
            assets=assets,
            metadata={
                "template": template_name,
                "render_mode": context.render_mode.value,
                "render_target": context.render_target.value,
                "component_count": len(ui_config.get("components", []))
            },
            render_time=0.0,  # 将在调用处设置
            cache_key=self._generate_cache_key(ui_config, context)
        )
    
    def _prepare_template_context(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> Dict[str, Any]:
        """准备模板上下文"""
        
        # 重建UIConfiguration对象（简化实现）
        # 在实际实现中，这里需要更复杂的逻辑来正确重建对象
        
        template_context = {
            "title": ui_config.get("title", "SmartUI MCP"),
            "lang": context.user_preferences.get("language", "en"),
            "components": ui_config.get("components", []),
            "theme": ui_config.get("theme", {}),
            "layout": ui_config.get("layout", {}),
            "custom_css": "",
            "custom_js": "",
            "header_actions": [],
            "sidebar_items": [],
            "render_component": lambda comp: self._render_component_inline(comp)
        }
        
        # 应用主题覆盖
        if context.theme_overrides:
            template_context["theme"].update(context.theme_overrides)
        
        # 应用设备特定的调整
        device_type = context.device_info.get("type", "desktop")
        if device_type == "mobile":
            template_context["layout"]["sidebar_collapsed"] = True
        
        return template_context
    
    def _select_template(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> str:
        """选择模板"""
        
        # 根据渲染目标选择模板
        if context.render_target == RenderTarget.REACT:
            return "react_base.html"
        elif context.render_target == RenderTarget.VUE:
            return "vue_base.html"
        else:
            return "base.html"
    
    async def _generate_css(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> str:
        """生成CSS"""
        css_parts = []
        
        # 添加主题CSS
        theme = ui_config.get("theme", {})
        if theme:
            # 这里需要重建ThemeConfig对象
            # 简化实现，直接使用字典
            theme_css = self.style_generator.generate_theme_css(theme)
            css_parts.append(theme_css)
        
        # 添加组件CSS
        components = ui_config.get("components", [])
        component_types = set()
        for component in components:
            comp_type = component.get("type")
            if comp_type and comp_type not in component_types:
                component_types.add(comp_type)
                # 这里需要ComponentType枚举
                # 简化实现，跳过组件CSS生成
        
        # 添加自定义CSS
        custom_css = context.user_preferences.get("custom_css", "")
        if custom_css:
            css_parts.append(custom_css)
        
        return "\n\n".join(css_parts)
    
    async def _generate_js(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> str:
        """生成JavaScript"""
        js_parts = []
        
        # 添加组件初始化代码
        components = ui_config.get("components", [])
        if components:
            init_code = "// Component initialization\n"
            init_code += "document.addEventListener('DOMContentLoaded', function() {\n"
            
            for component in components:
                comp_id = component.get("id")
                comp_type = component.get("type")
                if comp_id and comp_type:
                    init_code += f"  window.smartUI.initializeComponent(document.getElementById('{comp_id}'));\n"
            
            init_code += "});\n"
            js_parts.append(init_code)
        
        # 添加自定义JavaScript
        custom_js = context.user_preferences.get("custom_js", "")
        if custom_js:
            js_parts.append(custom_js)
        
        return "\n\n".join(js_parts)
    
    def _collect_assets(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> List[str]:
        """收集资源文件"""
        assets = []
        
        # 核心资源
        assets.extend([
            "/static/css/smartui-core.css",
            "/static/js/smartui-core.js",
            "/static/js/smartui-components.js"
        ])
        
        # 主题资源
        theme = ui_config.get("theme", {})
        theme_name = theme.get("name", "light")
        assets.append(f"/static/css/smartui-theme-{theme_name}.css")
        
        # 组件特定资源
        components = ui_config.get("components", [])
        for component in components:
            comp_type = component.get("type")
            if comp_type in ["chart", "calendar", "code_editor"]:
                # 这些组件可能需要额外的库
                if comp_type == "chart":
                    assets.append("/static/js/chart.min.js")
                elif comp_type == "calendar":
                    assets.append("/static/js/calendar.min.js")
                elif comp_type == "code_editor":
                    assets.append("/static/js/monaco-editor.min.js")
        
        return assets
    
    def _render_component_inline(self, component: Dict[str, Any]) -> str:
        """内联渲染组件"""
        # 这是一个简化的组件渲染实现
        comp_type = component.get("type", "div")
        comp_id = component.get("id", "")
        comp_text = component.get("text", "")
        
        if comp_type == "button":
            return f'<button id="{comp_id}" class="smartui-button">{comp_text}</button>'
        elif comp_type == "input":
            return f'<input id="{comp_id}" class="smartui-input" type="text" placeholder="{comp_text}">'
        else:
            return f'<div id="{comp_id}" class="smartui-{comp_type}">{comp_text}</div>'
    
    def _parse_render_context(self, context: Dict[str, Any]) -> RenderContext:
        """解析渲染上下文"""
        return RenderContext(
            context_id=context.get("context_id"),
            render_mode=RenderMode(context.get("render_mode", "dynamic")),
            render_target=RenderTarget(context.get("render_target", "html")),
            user_preferences=context.get("user_preferences", {}),
            device_info=context.get("device_info", {}),
            theme_overrides=context.get("theme_overrides", {}),
            accessibility_options=context.get("accessibility_options", {}),
            performance_hints=context.get("performance_hints", {}),
            timestamp=datetime.now()
        )
    
    def _generate_cache_key(
        self,
        ui_config: Dict[str, Any],
        context: RenderContext
    ) -> str:
        """生成缓存键"""
        import hashlib
        
        # 创建缓存键的组成部分
        cache_parts = [
            str(ui_config),
            context.render_mode.value,
            context.render_target.value,
            str(context.user_preferences),
            str(context.device_info),
            str(context.theme_overrides)
        ]
        
        # 生成哈希
        cache_string = "|".join(cache_parts)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"render_{cache_hash}"
    
    @event_handler(EventBusEventType.UI_RENDER_COMPLETE)
    async def handle_ui_generated(self, event: EventBusEvent) -> None:
        """处理UI生成事件"""
        generation_data = event.data
        ui_config = generation_data.get("ui_configuration")
        
        if ui_config:
            # 自动渲染生成的UI配置
            await self.render_ui_configuration(ui_config)
    
    @event_handler(EventBusEventType.API_STATE_CHANGED)
    async def handle_state_changed(self, event: EventBusEvent) -> None:
        """处理状态变化事件"""
        state_data = event.data
        path = state_data.get("path")
        
        # 如果是UI相关的状态变化，触发重新渲染
        if path and path.startswith("ui."):
            self.logger.debug(f"UI state changed: {path}")
            # 这里可以实现增量更新逻辑
    
    async def get_render_statistics(self) -> Dict[str, Any]:
        """获取渲染统计信息"""
        return {
            "cache_size": len(self.render_cache._cache) if hasattr(self.render_cache, '_cache') else 0,
            "cache_hit_rate": getattr(self.render_cache, "hit_rate", 0.0),
            "template_count": len(self.template_manager.template_cache),
            "performance_metrics": dict(self.performance_metrics)
        }
    
    async def cleanup(self) -> Dict[str, int]:
        """清理资源"""
        cleanup_stats = {
            "cleared_cache_entries": 0,
            "cleared_templates": 0
        }
        
        try:
            # 清理渲染缓存
            await self.render_cache.clear()
            cleanup_stats["cleared_cache_entries"] = 1
            
            # 清理模板缓存
            template_count = len(self.template_manager.template_cache)
            self.template_manager.template_cache.clear()
            cleanup_stats["cleared_templates"] = template_count
            
            self.logger.info(f"UI Renderer cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during UI Renderer cleanup: {e}")
            return cleanup_stats


# 导出主要类
FixedUIRenderer = SmartUIRenderer  # 为了向后兼容
__all__ = ['SmartUIRenderer', 'FixedUIRenderer']

