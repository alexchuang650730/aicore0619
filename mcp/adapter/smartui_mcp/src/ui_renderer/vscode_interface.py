"""
SmartUI MCP - VS Code风格界面集成

实现VS Code风格的专业界面组件，包括活动栏、侧边栏、编辑器区域、状态栏等。
提供完整的VS Code用户体验，支持主题切换、布局调整和扩展功能。
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

from ..common import (
    EventBusEvent, EventBusEventType,
    publish_event, event_handler, EventHandlerRegistry,
    AsyncCache, Timer, generate_id, log_execution_time,
    UIConfiguration, UIComponent, ComponentType, LayoutType, ThemeType,
    ComponentProps, ComponentStyle, LayoutConfig, ThemeConfig
)
from .reactive_components import ReactiveComponent, ReactiveComponentSystem


class VSCodeArea(str, Enum):
    """VS Code区域枚举"""
    ACTIVITY_BAR = "activity_bar"
    SIDEBAR = "sidebar"
    EDITOR_GROUP = "editor_group"
    PANEL = "panel"
    STATUS_BAR = "status_bar"
    TITLE_BAR = "title_bar"
    MENU_BAR = "menu_bar"


class VSCodeViewType(str, Enum):
    """VS Code视图类型枚举"""
    EXPLORER = "explorer"
    SEARCH = "search"
    SOURCE_CONTROL = "source_control"
    DEBUG = "debug"
    EXTENSIONS = "extensions"
    TERMINAL = "terminal"
    PROBLEMS = "problems"
    OUTPUT = "output"
    DEBUG_CONSOLE = "debug_console"


@dataclass
class VSCodeLayout:
    """VS Code布局配置"""
    title_bar_visible: bool = True
    menu_bar_visible: bool = True
    activity_bar_visible: bool = True
    sidebar_visible: bool = True
    sidebar_position: str = "left"  # left, right
    sidebar_width: int = 300
    panel_visible: bool = True
    panel_position: str = "bottom"  # bottom, right
    panel_height: int = 200
    status_bar_visible: bool = True
    minimap_enabled: bool = True
    breadcrumbs_enabled: bool = True
    tabs_visible: bool = True
    zen_mode: bool = False


@dataclass
class VSCodeTheme:
    """VS Code主题配置"""
    name: str
    type: str  # light, dark, high_contrast
    colors: Dict[str, str]
    token_colors: Dict[str, str]
    ui_colors: Dict[str, str]
    
    @classmethod
    def create_dark_theme(cls) -> 'VSCodeTheme':
        """创建暗色主题"""
        return cls(
            name="Dark+ (default dark)",
            type="dark",
            colors={
                "editor.background": "#1e1e1e",
                "editor.foreground": "#d4d4d4",
                "activityBar.background": "#333333",
                "activityBar.foreground": "#ffffff",
                "sideBar.background": "#252526",
                "sideBar.foreground": "#cccccc",
                "statusBar.background": "#007acc",
                "statusBar.foreground": "#ffffff",
                "titleBar.activeBackground": "#3c3c3c",
                "titleBar.activeForeground": "#cccccc",
                "panel.background": "#1e1e1e",
                "panel.border": "#3c3c3c"
            },
            token_colors={
                "comment": "#6a9955",
                "keyword": "#569cd6",
                "string": "#ce9178",
                "number": "#b5cea8",
                "function": "#dcdcaa"
            },
            ui_colors={
                "button.background": "#0e639c",
                "button.foreground": "#ffffff",
                "input.background": "#3c3c3c",
                "input.foreground": "#cccccc",
                "dropdown.background": "#3c3c3c",
                "dropdown.foreground": "#cccccc"
            }
        )
    
    @classmethod
    def create_light_theme(cls) -> 'VSCodeTheme':
        """创建亮色主题"""
        return cls(
            name="Light+ (default light)",
            type="light",
            colors={
                "editor.background": "#ffffff",
                "editor.foreground": "#000000",
                "activityBar.background": "#2c2c2c",
                "activityBar.foreground": "#ffffff",
                "sideBar.background": "#f3f3f3",
                "sideBar.foreground": "#000000",
                "statusBar.background": "#007acc",
                "statusBar.foreground": "#ffffff",
                "titleBar.activeBackground": "#dddddd",
                "titleBar.activeForeground": "#000000",
                "panel.background": "#ffffff",
                "panel.border": "#e5e5e5"
            },
            token_colors={
                "comment": "#008000",
                "keyword": "#0000ff",
                "string": "#a31515",
                "number": "#098658",
                "function": "#795e26"
            },
            ui_colors={
                "button.background": "#0e639c",
                "button.foreground": "#ffffff",
                "input.background": "#ffffff",
                "input.foreground": "#000000",
                "dropdown.background": "#ffffff",
                "dropdown.foreground": "#000000"
            }
        )


class VSCodeActivityBarComponent(ReactiveComponent):
    """VS Code活动栏组件"""
    
    def __init__(self, component_id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(component_id, ComponentType.NAVIGATION, props)
        
        # 默认活动项
        self.state.update({
            "active_view": VSCodeViewType.EXPLORER.value,
            "items": [
                {"id": "explorer", "icon": "files", "title": "Explorer", "view": VSCodeViewType.EXPLORER.value},
                {"id": "search", "icon": "search", "title": "Search", "view": VSCodeViewType.SEARCH.value},
                {"id": "scm", "icon": "source-control", "title": "Source Control", "view": VSCodeViewType.SOURCE_CONTROL.value},
                {"id": "debug", "icon": "debug", "title": "Run and Debug", "view": VSCodeViewType.DEBUG.value},
                {"id": "extensions", "icon": "extensions", "title": "Extensions", "view": VSCodeViewType.EXTENSIONS.value}
            ]
        })
    
    async def _render(self) -> None:
        """渲染活动栏"""
        await self.emit_event("render_request", {
            "component_id": self.component_id,
            "template": "vscode_activity_bar",
            "data": {
                "active_view": self.state["active_view"],
                "items": self.state["items"]
            }
        })
    
    async def set_active_view(self, view_type: str) -> None:
        """设置活动视图"""
        await self.set_state({"active_view": view_type})
        await self.emit_event("view_changed", {"view": view_type})


class VSCodeSidebarComponent(ReactiveComponent):
    """VS Code侧边栏组件"""
    
    def __init__(self, component_id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(component_id, ComponentType.CONTAINER, props)
        
        self.state.update({
            "current_view": VSCodeViewType.EXPLORER.value,
            "width": 300,
            "collapsed": False,
            "views": {
                VSCodeViewType.EXPLORER.value: {
                    "title": "Explorer",
                    "content": [],
                    "actions": []
                },
                VSCodeViewType.SEARCH.value: {
                    "title": "Search",
                    "content": [],
                    "actions": []
                }
            }
        })
    
    async def _render(self) -> None:
        """渲染侧边栏"""
        current_view_data = self.state["views"].get(self.state["current_view"], {})
        
        await self.emit_event("render_request", {
            "component_id": self.component_id,
            "template": "vscode_sidebar",
            "data": {
                "current_view": self.state["current_view"],
                "width": self.state["width"],
                "collapsed": self.state["collapsed"],
                "view_data": current_view_data
            }
        })
    
    async def switch_view(self, view_type: str) -> None:
        """切换视图"""
        await self.set_state({"current_view": view_type})
    
    async def toggle_collapse(self) -> None:
        """切换折叠状态"""
        await self.set_state({"collapsed": not self.state["collapsed"]})


class VSCodeEditorGroupComponent(ReactiveComponent):
    """VS Code编辑器组组件"""
    
    def __init__(self, component_id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(component_id, ComponentType.CONTAINER, props)
        
        self.state.update({
            "tabs": [],
            "active_tab": None,
            "split_layout": "single",  # single, horizontal, vertical
            "groups": []
        })
    
    async def _render(self) -> None:
        """渲染编辑器组"""
        await self.emit_event("render_request", {
            "component_id": self.component_id,
            "template": "vscode_editor_group",
            "data": {
                "tabs": self.state["tabs"],
                "active_tab": self.state["active_tab"],
                "split_layout": self.state["split_layout"],
                "groups": self.state["groups"]
            }
        })
    
    async def open_tab(self, tab_data: Dict[str, Any]) -> None:
        """打开标签页"""
        tabs = self.state["tabs"].copy()
        
        # 检查是否已存在
        existing_tab = next((tab for tab in tabs if tab["id"] == tab_data["id"]), None)
        if existing_tab:
            await self.set_state({"active_tab": tab_data["id"]})
            return
        
        # 添加新标签页
        tabs.append(tab_data)
        await self.set_state({
            "tabs": tabs,
            "active_tab": tab_data["id"]
        })
    
    async def close_tab(self, tab_id: str) -> None:
        """关闭标签页"""
        tabs = [tab for tab in self.state["tabs"] if tab["id"] != tab_id]
        active_tab = self.state["active_tab"]
        
        # 如果关闭的是活动标签页，切换到其他标签页
        if active_tab == tab_id:
            active_tab = tabs[0]["id"] if tabs else None
        
        await self.set_state({
            "tabs": tabs,
            "active_tab": active_tab
        })


class VSCodeStatusBarComponent(ReactiveComponent):
    """VS Code状态栏组件"""
    
    def __init__(self, component_id: str, props: Optional[Dict[str, Any]] = None):
        super().__init__(component_id, ComponentType.CONTAINER, props)
        
        self.state.update({
            "left_items": [
                {"id": "branch", "text": "main", "icon": "git-branch"},
                {"id": "sync", "text": "0↓ 0↑", "icon": "sync"}
            ],
            "right_items": [
                {"id": "selection", "text": "Ln 1, Col 1"},
                {"id": "language", "text": "Python"},
                {"id": "encoding", "text": "UTF-8"},
                {"id": "eol", "text": "LF"}
            ]
        })
    
    async def _render(self) -> None:
        """渲染状态栏"""
        await self.emit_event("render_request", {
            "component_id": self.component_id,
            "template": "vscode_status_bar",
            "data": {
                "left_items": self.state["left_items"],
                "right_items": self.state["right_items"]
            }
        })
    
    async def update_item(self, item_id: str, text: str, side: str = "right") -> None:
        """更新状态栏项目"""
        items_key = f"{side}_items"
        items = self.state[items_key].copy()
        
        for item in items:
            if item["id"] == item_id:
                item["text"] = text
                break
        
        await self.set_state({items_key: items})


class VSCodeInterface:
    """VS Code界面管理器"""
    
    def __init__(self, component_system: ReactiveComponentSystem):
        self.component_system = component_system
        self.logger = logging.getLogger(f"{__name__}.VSCodeInterface")
        
        # 布局和主题
        self.layout = VSCodeLayout()
        self.theme = VSCodeTheme.create_dark_theme()
        
        # 组件引用
        self.activity_bar: Optional[VSCodeActivityBarComponent] = None
        self.sidebar: Optional[VSCodeSidebarComponent] = None
        self.editor_group: Optional[VSCodeEditorGroupComponent] = None
        self.status_bar: Optional[VSCodeStatusBarComponent] = None
        
        # 事件处理器注册
        self.event_registry = EventHandlerRegistry()
        
        self.logger.info("VS Code Interface initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化VS Code界面"""
        try:
            # 创建主要组件
            await self._create_core_components()
            
            # 设置组件关系
            await self._setup_component_relationships()
            
            # 应用主题
            await self._apply_theme()
            
            # 设置事件监听
            await self._setup_event_listeners()
            
            return {
                "success": True,
                "layout": asdict(self.layout),
                "theme": asdict(self.theme),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error initializing VS Code interface: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _create_core_components(self) -> None:
        """创建核心组件"""
        
        # 创建活动栏
        activity_bar_result = await self.component_system.create_component({
            "id": "vscode_activity_bar",
            "type": "navigation",
            "props": {"area": VSCodeArea.ACTIVITY_BAR.value}
        })
        
        if activity_bar_result["success"]:
            self.activity_bar = VSCodeActivityBarComponent("vscode_activity_bar")
            await self.activity_bar.mount()
        
        # 创建侧边栏
        sidebar_result = await self.component_system.create_component({
            "id": "vscode_sidebar",
            "type": "container",
            "props": {"area": VSCodeArea.SIDEBAR.value}
        })
        
        if sidebar_result["success"]:
            self.sidebar = VSCodeSidebarComponent("vscode_sidebar")
            await self.sidebar.mount()
        
        # 创建编辑器组
        editor_result = await self.component_system.create_component({
            "id": "vscode_editor_group",
            "type": "container",
            "props": {"area": VSCodeArea.EDITOR_GROUP.value}
        })
        
        if editor_result["success"]:
            self.editor_group = VSCodeEditorGroupComponent("vscode_editor_group")
            await self.editor_group.mount()
        
        # 创建状态栏
        status_bar_result = await self.component_system.create_component({
            "id": "vscode_status_bar",
            "type": "container",
            "props": {"area": VSCodeArea.STATUS_BAR.value}
        })
        
        if status_bar_result["success"]:
            self.status_bar = VSCodeStatusBarComponent("vscode_status_bar")
            await self.status_bar.mount()
    
    async def _setup_component_relationships(self) -> None:
        """设置组件关系"""
        
        # 活动栏和侧边栏的关联
        if self.activity_bar and self.sidebar:
            self.activity_bar.add_event_handler(
                "view_changed",
                lambda data: asyncio.create_task(self.sidebar.switch_view(data["view"]))
            )
    
    async def _apply_theme(self) -> None:
        """应用主题"""
        
        # 发布主题变更事件
        await publish_event(
            event_type=EventBusEventType.UI_THEME_CHANGED,
            data={
                "theme": asdict(self.theme),
                "layout": asdict(self.layout)
            },
            source="vscode_interface"
        )
    
    async def _setup_event_listeners(self) -> None:
        """设置事件监听"""
        
        # 监听组件渲染请求
        async def handle_render_request(event: EventBusEvent):
            render_data = event.data
            component_id = render_data.get("component_id")
            template = render_data.get("template")
            data = render_data.get("data", {})
            
            # 发布渲染事件
            await publish_event(
                event_type=EventBusEventType.UI_RENDER_REQUESTED,
                data={
                    "component_id": component_id,
                    "template": template,
                    "data": data,
                    "theme": asdict(self.theme),
                    "layout": asdict(self.layout)
                },
                source="vscode_interface"
            )
        
        # 注册事件处理器
        self.event_registry.register("render_request", handle_render_request)
    
    async def switch_theme(self, theme_type: str) -> Dict[str, Any]:
        """切换主题"""
        try:
            if theme_type == "dark":
                self.theme = VSCodeTheme.create_dark_theme()
            elif theme_type == "light":
                self.theme = VSCodeTheme.create_light_theme()
            else:
                return {
                    "success": False,
                    "error": f"Unknown theme type: {theme_type}",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 应用新主题
            await self._apply_theme()
            
            # 触发所有组件重新渲染
            await self._refresh_all_components()
            
            return {
                "success": True,
                "theme": asdict(self.theme),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error switching theme: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_layout(self, layout_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新布局"""
        try:
            # 更新布局配置
            for key, value in layout_updates.items():
                if hasattr(self.layout, key):
                    setattr(self.layout, key, value)
            
            # 应用布局变更
            await self._apply_layout_changes(layout_updates)
            
            return {
                "success": True,
                "layout": asdict(self.layout),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error updating layout: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _apply_layout_changes(self, changes: Dict[str, Any]) -> None:
        """应用布局变更"""
        
        # 侧边栏相关变更
        if "sidebar_visible" in changes and self.sidebar:
            if changes["sidebar_visible"]:
                await self.sidebar.set_state({"collapsed": False})
            else:
                await self.sidebar.set_state({"collapsed": True})
        
        if "sidebar_width" in changes and self.sidebar:
            await self.sidebar.set_state({"width": changes["sidebar_width"]})
        
        # 发布布局变更事件
        await publish_event(
            event_type=EventBusEventType.UI_LAYOUT_CHANGED,
            data={
                "layout": asdict(self.layout),
                "changes": changes
            },
            source="vscode_interface"
        )
    
    async def _refresh_all_components(self) -> None:
        """刷新所有组件"""
        components = [self.activity_bar, self.sidebar, self.editor_group, self.status_bar]
        
        for component in components:
            if component and component.is_mounted:
                await component.update({"theme_changed": True})
    
    async def open_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """打开文件"""
        try:
            if not self.editor_group:
                return {
                    "success": False,
                    "error": "Editor group not initialized",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 创建标签页数据
            tab_data = {
                "id": generate_id("tab_"),
                "title": file_path.split("/")[-1],
                "path": file_path,
                "content": content,
                "modified": False,
                "language": self._detect_language(file_path)
            }
            
            # 打开标签页
            await self.editor_group.open_tab(tab_data)
            
            return {
                "success": True,
                "tab_id": tab_data["id"],
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error opening file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_language(self, file_path: str) -> str:
        """检测文件语言"""
        extension = file_path.split(".")[-1].lower()
        
        language_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "html": "html",
            "css": "css",
            "json": "json",
            "md": "markdown",
            "yaml": "yaml",
            "yml": "yaml",
            "xml": "xml",
            "sql": "sql"
        }
        
        return language_map.get(extension, "plaintext")
    
    async def get_interface_state(self) -> Dict[str, Any]:
        """获取界面状态"""
        state = {
            "layout": asdict(self.layout),
            "theme": asdict(self.theme),
            "components": {}
        }
        
        # 收集组件状态
        if self.activity_bar:
            state["components"]["activity_bar"] = self.activity_bar.get_state()
        
        if self.sidebar:
            state["components"]["sidebar"] = self.sidebar.get_state()
        
        if self.editor_group:
            state["components"]["editor_group"] = self.editor_group.get_state()
        
        if self.status_bar:
            state["components"]["status_bar"] = self.status_bar.get_state()
        
        return state
    
    @event_handler(EventBusEventType.USER_BEHAVIOR_CHANGE)
    async def handle_user_behavior_analyzed(self, event: EventBusEvent) -> None:
        """处理用户行为分析事件"""
        behavior_data = event.data
        user_preferences = behavior_data.get("user_preferences", {})
        
        # 根据用户偏好调整界面
        if user_preferences.get("theme_preference") == "dark":
            await self.switch_theme("dark")
        elif user_preferences.get("theme_preference") == "light":
            await self.switch_theme("light")
        
        # 根据用户习惯调整布局
        if user_preferences.get("sidebar_usage") == "low":
            await self.update_layout({"sidebar_width": 200})
    
    async def cleanup(self) -> Dict[str, int]:
        """清理资源"""
        cleanup_stats = {
            "unmounted_components": 0
        }
        
        try:
            # 卸载所有组件
            components = [self.activity_bar, self.sidebar, self.editor_group, self.status_bar]
            
            for component in components:
                if component and component.is_mounted:
                    await component.unmount()
                    cleanup_stats["unmounted_components"] += 1
            
            self.logger.info(f"VS Code Interface cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return cleanup_stats

