#!/usr/bin/env python3
"""
Git Monitor Module for Developer Intervention MCP
基础Git监控模块 - 实现实时checkin状态监控
"""

import os
import subprocess
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class GitStatus:
    """Git状态数据模型"""
    repository_path: str
    current_branch: str
    last_commit_hash: str
    last_commit_message: str
    last_commit_time: datetime
    uncommitted_changes: List[str]
    untracked_files: List[str]
    staged_files: List[str]
    is_clean: bool
    ahead_commits: int
    behind_commits: int

@dataclass
class CheckinEvent:
    """Checkin事件数据模型"""
    event_id: str
    developer_id: str
    event_type: str  # 'file_modified', 'staged', 'committed', 'pushed'
    timestamp: datetime
    files_affected: List[str]
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None
    branch_name: Optional[str] = None

class GitMonitor:
    """Git监控器 - 实时监控Git状态和checkin活动"""
    
    def __init__(self, repository_path: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repository_path = repository_path
        self.monitoring = False
        self.monitor_thread = None
        self.last_status = None
        self.checkin_events = []
        self.callbacks = []
        
        # 监控配置
        self.monitor_interval = 5  # 秒
        self.max_events_history = 100
        
        logger.info(f"🔍 Git监控器初始化: {repository_path}")
    
    def start_monitoring(self) -> Dict[str, Any]:
        """启动Git监控"""
        try:
            if self.monitoring:
                return {"success": False, "error": "监控已在运行"}
            
            if not self._validate_git_repository():
                return {"success": False, "error": "无效的Git仓库"}
            
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            logger.info("🚀 Git监控启动成功")
            return {
                "success": True,
                "message": "Git监控启动成功",
                "repository_path": self.repository_path,
                "monitor_interval": self.monitor_interval
            }
            
        except Exception as e:
            logger.error(f"❌ 启动Git监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止Git监控"""
        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            
            logger.info("⏹️ Git监控已停止")
            return {"success": True, "message": "Git监控已停止"}
            
        except Exception as e:
            logger.error(f"❌ 停止Git监控失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前Git状态"""
        try:
            status = self._get_git_status()
            return {
                "success": True,
                "git_status": asdict(status),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 获取Git状态失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_recent_events(self, limit: int = 20) -> Dict[str, Any]:
        """获取最近的checkin事件"""
        try:
            recent_events = self.checkin_events[-limit:] if self.checkin_events else []
            return {
                "success": True,
                "events": [asdict(event) for event in recent_events],
                "total_events": len(self.checkin_events)
            }
        except Exception as e:
            logger.error(f"❌ 获取checkin事件失败: {e}")
            return {"success": False, "error": str(e)}
    
    def add_status_callback(self, callback):
        """添加状态变更回调函数"""
        self.callbacks.append(callback)
    
    def _validate_git_repository(self) -> bool:
        """验证Git仓库"""
        try:
            git_dir = Path(self.repository_path) / ".git"
            return git_dir.exists()
        except Exception:
            return False
    
    def _monitor_loop(self):
        """监控循环"""
        logger.info("🔄 Git监控循环启动")
        
        while self.monitoring:
            try:
                current_status = self._get_git_status()
                
                # 检测状态变更
                if self.last_status:
                    events = self._detect_changes(self.last_status, current_status)
                    for event in events:
                        self._handle_checkin_event(event)
                
                self.last_status = current_status
                
                # 通知回调函数
                for callback in self.callbacks:
                    try:
                        callback(current_status)
                    except Exception as e:
                        logger.error(f"回调函数执行失败: {e}")
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                time.sleep(self.monitor_interval)
        
        logger.info("⏹️ Git监控循环结束")
    
    def _get_git_status(self) -> GitStatus:
        """获取Git状态"""
        try:
            # 切换到仓库目录
            original_cwd = os.getcwd()
            os.chdir(self.repository_path)
            
            # 获取当前分支
            current_branch = self._run_git_command(['git', 'branch', '--show-current']).strip()
            
            # 获取最后一次提交信息
            last_commit_info = self._run_git_command([
                'git', 'log', '-1', '--format=%H|%s|%ct'
            ]).strip()
            
            if last_commit_info:
                commit_hash, commit_message, commit_timestamp = last_commit_info.split('|', 2)
                last_commit_time = datetime.fromtimestamp(int(commit_timestamp))
            else:
                commit_hash = ""
                commit_message = ""
                last_commit_time = datetime.now()
            
            # 获取未提交的更改
            status_output = self._run_git_command(['git', 'status', '--porcelain'])
            uncommitted_changes = []
            untracked_files = []
            staged_files = []
            
            for line in status_output.split('\n'):
                if line.strip():
                    status_code = line[:2]
                    file_path = line[3:]
                    
                    if status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                        staged_files.append(file_path)
                    if status_code[1] in ['M', 'D']:
                        uncommitted_changes.append(file_path)
                    if status_code == '??':
                        untracked_files.append(file_path)
            
            # 检查是否有远程跟踪分支
            ahead_commits = 0
            behind_commits = 0
            
            try:
                # 获取ahead/behind信息
                ahead_behind = self._run_git_command([
                    'git', 'rev-list', '--left-right', '--count', f'{current_branch}...origin/{current_branch}'
                ]).strip()
                
                if ahead_behind:
                    ahead_str, behind_str = ahead_behind.split('\t')
                    ahead_commits = int(ahead_str)
                    behind_commits = int(behind_str)
            except:
                # 如果没有远程分支，忽略错误
                pass
            
            is_clean = not (uncommitted_changes or untracked_files or staged_files)
            
            return GitStatus(
                repository_path=self.repository_path,
                current_branch=current_branch,
                last_commit_hash=commit_hash,
                last_commit_message=commit_message,
                last_commit_time=last_commit_time,
                uncommitted_changes=uncommitted_changes,
                untracked_files=untracked_files,
                staged_files=staged_files,
                is_clean=is_clean,
                ahead_commits=ahead_commits,
                behind_commits=behind_commits
            )
            
        finally:
            os.chdir(original_cwd)
    
    def _run_git_command(self, command: List[str]) -> str:
        """执行Git命令"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning(f"Git命令执行警告: {' '.join(command)} - {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            logger.error(f"Git命令超时: {' '.join(command)}")
            return ""
        except Exception as e:
            logger.error(f"Git命令执行失败: {' '.join(command)} - {e}")
            return ""
    
    def _detect_changes(self, old_status: GitStatus, new_status: GitStatus) -> List[CheckinEvent]:
        """检测Git状态变更"""
        events = []
        event_time = datetime.now()
        
        # 检测新的提交
        if old_status.last_commit_hash != new_status.last_commit_hash:
            event = CheckinEvent(
                event_id=f"commit_{int(time.time())}",
                developer_id="current_user",  # 可以从Git配置获取
                event_type="committed",
                timestamp=event_time,
                files_affected=new_status.staged_files,
                commit_hash=new_status.last_commit_hash,
                commit_message=new_status.last_commit_message,
                branch_name=new_status.current_branch
            )
            events.append(event)
        
        # 检测文件修改
        new_modified = set(new_status.uncommitted_changes) - set(old_status.uncommitted_changes)
        if new_modified:
            event = CheckinEvent(
                event_id=f"modified_{int(time.time())}",
                developer_id="current_user",
                event_type="file_modified",
                timestamp=event_time,
                files_affected=list(new_modified),
                branch_name=new_status.current_branch
            )
            events.append(event)
        
        # 检测文件暂存
        new_staged = set(new_status.staged_files) - set(old_status.staged_files)
        if new_staged:
            event = CheckinEvent(
                event_id=f"staged_{int(time.time())}",
                developer_id="current_user",
                event_type="staged",
                timestamp=event_time,
                files_affected=list(new_staged),
                branch_name=new_status.current_branch
            )
            events.append(event)
        
        # 检测推送 (通过ahead_commits变化检测)
        if old_status.ahead_commits > new_status.ahead_commits:
            event = CheckinEvent(
                event_id=f"pushed_{int(time.time())}",
                developer_id="current_user",
                event_type="pushed",
                timestamp=event_time,
                files_affected=[],
                commit_hash=new_status.last_commit_hash,
                branch_name=new_status.current_branch
            )
            events.append(event)
        
        return events
    
    def _handle_checkin_event(self, event: CheckinEvent):
        """处理checkin事件"""
        # 添加到事件历史
        self.checkin_events.append(event)
        
        # 保持事件历史大小限制
        if len(self.checkin_events) > self.max_events_history:
            self.checkin_events = self.checkin_events[-self.max_events_history:]
        
        logger.info(f"📝 Checkin事件: {event.event_type} - {event.files_affected}")
    
    def get_developer_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取开发者活动摘要"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_events = [
                event for event in self.checkin_events 
                if event.timestamp > cutoff_time
            ]
            
            # 统计活动
            activity_stats = {
                "total_events": len(recent_events),
                "commits": len([e for e in recent_events if e.event_type == "committed"]),
                "file_modifications": len([e for e in recent_events if e.event_type == "file_modified"]),
                "files_staged": len([e for e in recent_events if e.event_type == "staged"]),
                "pushes": len([e for e in recent_events if e.event_type == "pushed"]),
                "unique_files": len(set(
                    file_path 
                    for event in recent_events 
                    for file_path in event.files_affected
                )),
                "time_period_hours": hours,
                "last_activity": recent_events[-1].timestamp.isoformat() if recent_events else None
            }
            
            return {
                "success": True,
                "activity_summary": activity_stats,
                "recent_events": [asdict(event) for event in recent_events[-10:]]  # 最近10个事件
            }
            
        except Exception as e:
            logger.error(f"❌ 获取活动摘要失败: {e}")
            return {"success": False, "error": str(e)}

# 集成到Developer Intervention MCP的扩展
class DeveloperInterventionMCPExtension:
    """Developer Intervention MCP的Git监控扩展"""
    
    def __init__(self, dev_intervention_mcp):
        self.dev_intervention_mcp = dev_intervention_mcp
        self.git_monitor = GitMonitor()
        
        # 添加Git监控回调
        self.git_monitor.add_status_callback(self._on_git_status_change)
        
        logger.info("🔗 Git监控扩展已集成到Developer Intervention MCP")
    
    def _on_git_status_change(self, git_status: GitStatus):
        """Git状态变更回调"""
        try:
            # 检查是否有违规行为需要检测
            if not git_status.is_clean:
                # 对修改的文件进行合规性检查
                for file_path in git_status.uncommitted_changes:
                    if file_path.endswith('.py'):
                        full_path = os.path.join(git_status.repository_path, file_path)
                        if os.path.exists(full_path):
                            # 触发文件合规性检查
                            asyncio.create_task(
                                self.dev_intervention_mcp._scan_file_compliance(Path(full_path))
                            )
            
        except Exception as e:
            logger.error(f"Git状态变更处理失败: {e}")
    
    def get_git_monitoring_status(self) -> Dict[str, Any]:
        """获取Git监控状态"""
        return {
            "monitoring_active": self.git_monitor.monitoring,
            "repository_path": self.git_monitor.repository_path,
            "monitor_interval": self.git_monitor.monitor_interval,
            "events_count": len(self.git_monitor.checkin_events)
        }

if __name__ == "__main__":
    # 测试Git监控功能
    monitor = GitMonitor()
    
    print("🔍 测试Git监控功能...")
    
    # 获取当前状态
    status_result = monitor.get_current_status()
    print(f"当前Git状态: {json.dumps(status_result, indent=2, ensure_ascii=False)}")
    
    # 启动监控
    start_result = monitor.start_monitoring()
    print(f"启动监控: {start_result}")
    
    # 等待一段时间观察
    time.sleep(10)
    
    # 获取活动摘要
    activity_result = monitor.get_developer_activity_summary()
    print(f"活动摘要: {json.dumps(activity_result, indent=2, ensure_ascii=False)}")
    
    # 停止监控
    stop_result = monitor.stop_monitoring()
    print(f"停止监控: {stop_result}")

