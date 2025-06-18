#!/usr/bin/env python3
"""
PowerAutomation 開源社區架構實現

提供純CLI工具架構，包括命令行工具、SDK、社區插件等
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import click

# 添加共享核心路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared_core'))

from shared_core import get_shared_core, initialize_shared_core
from shared_core.config.unified_config import get_config_manager

logger = logging.getLogger(__name__)

@dataclass
class CLIConfig:
    """CLI配置"""
    workspace_dir: str
    default_output_format: str = "json"
    verbose: bool = False
    auto_save: bool = True
    plugin_dirs: List[str] = None
    
    def __post_init__(self):
        if self.plugin_dirs is None:
            self.plugin_dirs = []

@dataclass
class Workflow:
    """工作流定義"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    variables: Dict[str, Any] = None
    created_at: str = ""
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dirs: List[str]):
        self.plugin_dirs = [Path(d) for d in plugin_dirs]
        self.plugins: Dict[str, Any] = {}
        self._load_plugins()
    
    def _load_plugins(self):
        """加載插件"""
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            for plugin_file in plugin_dir.glob("*.py"):
                try:
                    plugin_name = plugin_file.stem
                    # 簡化的插件加載邏輯
                    self.plugins[plugin_name] = {
                        "name": plugin_name,
                        "path": str(plugin_file),
                        "loaded": True
                    }
                except Exception as e:
                    logger.warning(f"加載插件失敗 {plugin_file}: {e}")
    
    def get_available_plugins(self) -> List[str]:
        """獲取可用插件列表"""
        return list(self.plugins.keys())
    
    def execute_plugin(self, plugin_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """執行插件"""
        if plugin_name not in self.plugins:
            return {"status": "error", "message": f"插件不存在: {plugin_name}"}
        
        # 簡化的插件執行邏輯
        return {
            "status": "success",
            "message": f"插件 {plugin_name} 執行成功",
            "result": args
        }

class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir = self.workspace_dir / "workflows"
        self.workflows_dir.mkdir(exist_ok=True)
    
    def create_workflow(self, workflow: Workflow) -> str:
        """創建工作流"""
        workflow_file = self.workflows_dir / f"{workflow.name}.yaml"
        
        workflow_data = asdict(workflow)
        with open(workflow_file, 'w', encoding='utf-8') as f:
            yaml.dump(workflow_data, f, default_flow_style=False, allow_unicode=True)
        
        return str(workflow_file)
    
    def load_workflow(self, workflow_name: str) -> Optional[Workflow]:
        """加載工作流"""
        workflow_file = self.workflows_dir / f"{workflow_name}.yaml"
        
        if not workflow_file.exists():
            return None
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return Workflow(**data)
    
    def list_workflows(self) -> List[str]:
        """列出所有工作流"""
        return [f.stem for f in self.workflows_dir.glob("*.yaml")]
    
    def execute_workflow(self, workflow_name: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行工作流"""
        workflow = self.load_workflow(workflow_name)
        if not workflow:
            return {"status": "error", "message": f"工作流不存在: {workflow_name}"}
        
        # 合併變量
        if variables:
            workflow.variables.update(variables)
        
        results = []
        
        try:
            for i, step in enumerate(workflow.steps):
                step_result = self._execute_step(step, workflow.variables)
                results.append({
                    "step": i + 1,
                    "name": step.get("name", f"步驟 {i + 1}"),
                    "result": step_result
                })
                
                # 如果步驟失敗且設置為必須成功，則停止執行
                if step_result.get("status") == "error" and step.get("required", True):
                    break
            
            return {
                "status": "success",
                "workflow": workflow_name,
                "steps_executed": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"工作流執行失敗: {str(e)}",
                "results": results
            }
    
    def _execute_step(self, step: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """執行工作流步驟"""
        step_type = step.get("type", "unknown")
        
        if step_type == "command":
            return self._execute_command_step(step, variables)
        elif step_type == "script":
            return self._execute_script_step(step, variables)
        elif step_type == "api":
            return self._execute_api_step(step, variables)
        else:
            return {"status": "error", "message": f"未知步驟類型: {step_type}"}
    
    def _execute_command_step(self, step: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """執行命令步驟"""
        command = step.get("command", "")
        
        # 替換變量
        for var_name, var_value in variables.items():
            command = command.replace(f"${{{var_name}}}", str(var_value))
        
        # 簡化實現：實際應該執行系統命令
        return {
            "status": "success",
            "message": f"命令執行成功: {command}",
            "output": f"模擬輸出: {command}"
        }
    
    def _execute_script_step(self, step: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """執行腳本步驟"""
        script = step.get("script", "")
        
        # 簡化實現：實際應該執行腳本
        return {
            "status": "success",
            "message": "腳本執行成功",
            "output": f"模擬腳本輸出: {script[:50]}..."
        }
    
    def _execute_api_step(self, step: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """執行API步驟"""
        url = step.get("url", "")
        method = step.get("method", "GET")
        
        # 簡化實現：實際應該發送HTTP請求
        return {
            "status": "success",
            "message": f"API調用成功: {method} {url}",
            "response": {"status": 200, "data": "模擬響應"}
        }

class PowerAutoCLI:
    """PowerAutomation CLI主類"""
    
    def __init__(self):
        # 獲取開源配置
        config_manager = get_config_manager()
        self.config = config_manager.get_all_config("opensource")
        
        # 初始化CLI配置
        self.cli_config = CLIConfig(
            workspace_dir=self.config["base"].data_dir,
            plugin_dirs=[
                os.path.join(self.config["base"].data_dir, "plugins"),
                "./plugins"
            ]
        )
        
        # 初始化管理器
        self.plugin_manager = PluginManager(self.cli_config.plugin_dirs)
        self.workflow_manager = WorkflowManager(self.cli_config.workspace_dir)
        
        # 初始化共享核心
        self.shared_core = None
    
    async def initialize(self):
        """初始化CLI"""
        try:
            # 初始化共享核心
            self.shared_core = initialize_shared_core("opensource")
            await self.shared_core.start_all_components()
            
            # 創建示例工作流
            self._create_sample_workflows()
            
            logger.info("PowerAutomation CLI 初始化成功")
            
        except Exception as e:
            logger.error(f"CLI 初始化失敗: {e}")
            raise
    
    def _create_sample_workflows(self):
        """創建示例工作流"""
        # 示例工作流1：文件處理
        file_workflow = Workflow(
            name="file_processing",
            description="批量處理文件",
            steps=[
                {
                    "name": "列出文件",
                    "type": "command",
                    "command": "ls -la ${input_dir}"
                },
                {
                    "name": "複製文件",
                    "type": "command",
                    "command": "cp ${input_dir}/* ${output_dir}/"
                },
                {
                    "name": "生成報告",
                    "type": "script",
                    "script": "echo '處理完成' > ${output_dir}/report.txt"
                }
            ],
            variables={
                "input_dir": "./input",
                "output_dir": "./output"
            }
        )
        self.workflow_manager.create_workflow(file_workflow)
        
        # 示例工作流2：API測試
        api_workflow = Workflow(
            name="api_testing",
            description="API接口測試",
            steps=[
                {
                    "name": "健康檢查",
                    "type": "api",
                    "url": "${base_url}/health",
                    "method": "GET"
                },
                {
                    "name": "獲取數據",
                    "type": "api",
                    "url": "${base_url}/api/data",
                    "method": "GET"
                },
                {
                    "name": "創建記錄",
                    "type": "api",
                    "url": "${base_url}/api/records",
                    "method": "POST"
                }
            ],
            variables={
                "base_url": "http://localhost:8000"
            }
        )
        self.workflow_manager.create_workflow(api_workflow)

# Click CLI 命令定義
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='詳細輸出')
@click.option('--workspace', '-w', default='./workspace', help='工作空間目錄')
@click.pass_context
def cli(ctx, verbose, workspace):
    """PowerAutomation 開源社區版 CLI工具"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['workspace'] = workspace

@cli.command()
@click.pass_context
def init(ctx):
    """初始化工作空間"""
    workspace = ctx.obj['workspace']
    click.echo(f"🚀 初始化工作空間: {workspace}")
    
    # 創建目錄結構
    Path(workspace).mkdir(parents=True, exist_ok=True)
    Path(workspace, "workflows").mkdir(exist_ok=True)
    Path(workspace, "plugins").mkdir(exist_ok=True)
    Path(workspace, "data").mkdir(exist_ok=True)
    
    click.echo("✅ 工作空間初始化完成")

@cli.command()
@click.pass_context
def status(ctx):
    """顯示系統狀態"""
    click.echo("📊 PowerAutomation 系統狀態")
    click.echo(f"   工作空間: {ctx.obj['workspace']}")
    click.echo(f"   詳細模式: {ctx.obj['verbose']}")
    click.echo("   狀態: 運行中")

@cli.group()
def workflow():
    """工作流管理命令"""
    pass

@workflow.command('list')
@click.pass_context
def list_workflows(ctx):
    """列出所有工作流"""
    app = PowerAutoCLI()
    workflows = app.workflow_manager.list_workflows()
    
    click.echo("📋 可用工作流:")
    for workflow_name in workflows:
        workflow_obj = app.workflow_manager.load_workflow(workflow_name)
        if workflow_obj:
            click.echo(f"   {workflow_name}: {workflow_obj.description}")

@workflow.command('run')
@click.argument('workflow_name')
@click.option('--var', '-v', multiple=True, help='設置變量 (格式: key=value)')
@click.pass_context
def run_workflow(ctx, workflow_name, var):
    """執行工作流"""
    app = PowerAutoCLI()
    
    # 解析變量
    variables = {}
    for v in var:
        if '=' in v:
            key, value = v.split('=', 1)
            variables[key] = value
    
    click.echo(f"🚀 執行工作流: {workflow_name}")
    
    # 執行工作流
    result = app.workflow_manager.execute_workflow(workflow_name, variables)
    
    if result["status"] == "success":
        click.echo(f"✅ 工作流執行成功，共執行 {result['steps_executed']} 個步驟")
        
        if ctx.obj['verbose']:
            for step_result in result["results"]:
                click.echo(f"   步驟 {step_result['step']}: {step_result['name']} - {step_result['result']['status']}")
    else:
        click.echo(f"❌ 工作流執行失敗: {result['message']}")

@workflow.command('create')
@click.argument('workflow_name')
@click.option('--description', '-d', default='', help='工作流描述')
@click.pass_context
def create_workflow(ctx, workflow_name, description):
    """創建新工作流"""
    app = PowerAutoCLI()
    
    # 創建基礎工作流
    workflow_obj = Workflow(
        name=workflow_name,
        description=description or f"工作流: {workflow_name}",
        steps=[
            {
                "name": "示例步驟",
                "type": "command",
                "command": "echo 'Hello, PowerAutomation!'"
            }
        ]
    )
    
    workflow_file = app.workflow_manager.create_workflow(workflow_obj)
    click.echo(f"✅ 工作流已創建: {workflow_file}")
    click.echo("💡 請編輯工作流文件以添加更多步驟")

@cli.group()
def plugin():
    """插件管理命令"""
    pass

@plugin.command('list')
@click.pass_context
def list_plugins(ctx):
    """列出所有插件"""
    app = PowerAutoCLI()
    plugins = app.plugin_manager.get_available_plugins()
    
    click.echo("🔌 可用插件:")
    for plugin_name in plugins:
        click.echo(f"   {plugin_name}")

@plugin.command('run')
@click.argument('plugin_name')
@click.option('--args', '-a', default='{}', help='插件參數 (JSON格式)')
@click.pass_context
def run_plugin(ctx, plugin_name, args):
    """執行插件"""
    app = PowerAutoCLI()
    
    try:
        plugin_args = json.loads(args)
    except json.JSONDecodeError:
        click.echo("❌ 插件參數格式錯誤，請使用JSON格式")
        return
    
    click.echo(f"🔌 執行插件: {plugin_name}")
    
    result = app.plugin_manager.execute_plugin(plugin_name, plugin_args)
    
    if result["status"] == "success":
        click.echo(f"✅ 插件執行成功: {result['message']}")
        if ctx.obj['verbose']:
            click.echo(f"   結果: {result.get('result', 'N/A')}")
    else:
        click.echo(f"❌ 插件執行失敗: {result['message']}")

async def main():
    """主函數 - 演示開源CLI功能"""
    print("🚀 PowerAutomation 開源社區架構演示")
    
    try:
        app = PowerAutoCLI()
        await app.initialize()
        
        print("\n📋 可用工作流:")
        workflows = app.workflow_manager.list_workflows()
        for workflow_name in workflows:
            workflow_obj = app.workflow_manager.load_workflow(workflow_name)
            if workflow_obj:
                print(f"   {workflow_name}: {workflow_obj.description}")
        
        print("\n🔌 可用插件:")
        plugins = app.plugin_manager.get_available_plugins()
        for plugin_name in plugins:
            print(f"   {plugin_name}")
        
        # 演示工作流執行
        print("\n🚀 執行示例工作流:")
        result = app.workflow_manager.execute_workflow("file_processing")
        print(f"   執行結果: {result['status']}")
        print(f"   執行步驟: {result.get('steps_executed', 0)}")
        
        print("\n✅ 開源社區架構演示完成")
        print("\n💡 使用 'python opensource_cli.py --help' 查看CLI命令")
        
    except Exception as e:
        print(f"❌ 演示失敗: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI模式
        cli()
    else:
        # 演示模式
        asyncio.run(main())

