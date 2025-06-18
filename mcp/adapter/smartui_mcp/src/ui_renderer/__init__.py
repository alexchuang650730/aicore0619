"""
SmartUI MCP UI渲染层初始化文件

导出所有UI渲染相关组件，提供统一的导入接口。
"""

from .fixed_ui_renderer import SmartUIRenderer
from .smart_ui_adapter import SmartUIAdapter
from .reactive_components import (
    ReactiveComponent, 
    ReactiveComponentSystem,
    ComponentRegistry,
    IReactiveComponent
)
from .vscode_interface import (
    VSCodeInterface,
    VSCodeActivityBarComponent,
    VSCodeSidebarComponent,
    VSCodeEditorGroupComponent,
    VSCodeStatusBarComponent,
    VSCodeLayout,
    VSCodeTheme
)

__all__ = [
    # 核心渲染器
    "SmartUIRenderer",
    "SmartUIAdapter",
    
    # 响应式组件系统
    "ReactiveComponent",
    "ReactiveComponentSystem", 
    "ComponentRegistry",
    "IReactiveComponent",
    
    # VS Code界面组件
    "VSCodeInterface",
    "VSCodeActivityBarComponent",
    "VSCodeSidebarComponent", 
    "VSCodeEditorGroupComponent",
    "VSCodeStatusBarComponent",
    "VSCodeLayout",
    "VSCodeTheme"
]

# 版本信息
__version__ = "1.0.0"
__author__ = "SmartUI MCP Team"
__description__ = "SmartUI MCP UI渲染层组件"

