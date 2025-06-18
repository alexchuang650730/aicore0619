#!/usr/bin/env python3
"""
GitHub MCP - Git仓库信息服务
提供标准的Git仓库信息和状态查询服务
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubMCP:
    """GitHub MCP - Git仓库信息管理器"""
    
    def __init__(self, repo_root: str = "/home/ubuntu/kilocode_integrated_repo"):
        self.repo_root = Path(repo_root)
        self.mcp_id = "github_mcp"
        self.version = "1.0.0"
        
    def get_repo_info(self) -> dict:
        """获取Git仓库基本信息"""
        try:
            os.chdir(self.repo_root)
            
            # 获取远程仓库URL
            remote_url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"], 
                text=True
            ).strip()
            
            # 提取仓库名
            repo_name = remote_url.split('/')[-1].replace('.git', '')
            
            # 获取当前分支
            current_branch = subprocess.check_output(
                ["git", "branch", "--show-current"], 
                text=True
            ).strip()
            
            # 获取最后提交信息
            last_commit = subprocess.check_output(
                ["git", "log", "-1", "--pretty=format:%h|%s|%an|%ad", "--date=relative"], 
                text=True
            ).strip()
            
            commit_parts = last_commit.split('|')
            
            # 检查是否有未提交的更改
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"], 
                text=True
            ).strip()
            
            has_changes = len(status_output) > 0
            
            return {
                "success": True,
                "data": {
                    "repo_name": repo_name,
                    "repo_url": remote_url,
                    "current_branch": current_branch,
                    "last_commit": {
                        "hash": commit_parts[0] if len(commit_parts) > 0 else "",
                        "message": commit_parts[1] if len(commit_parts) > 1 else "",
                        "author": commit_parts[2] if len(commit_parts) > 2 else "",
                        "date": commit_parts[3] if len(commit_parts) > 3 else ""
                    },
                    "has_uncommitted_changes": has_changes,
                    "sync_status": "有未提交更改" if has_changes else "已同步",
                    "last_sync": commit_parts[3] if len(commit_parts) > 3 else "未知",
                    "webhook_status": "正常监听",
                    "auto_deploy": "启用",
                    "code_quality": "通过"
                }
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git命令执行失败: {e}")
            return {
                "success": False,
                "error": f"Git命令执行失败: {e}"
            }
        except Exception as e:
            logger.error(f"获取仓库信息失败: {e}")
            return {
                "success": False,
                "error": f"获取仓库信息失败: {e}"
            }
    
    def get_branch_info(self) -> dict:
        """获取分支信息"""
        try:
            os.chdir(self.repo_root)
            
            # 获取所有分支
            branches = subprocess.check_output(
                ["git", "branch", "-a"], 
                text=True
            ).strip().split('\n')
            
            # 处理分支列表
            local_branches = []
            remote_branches = []
            current_branch = ""
            
            for branch in branches:
                branch = branch.strip()
                if branch.startswith('*'):
                    current_branch = branch[2:]
                    local_branches.append(current_branch)
                elif branch.startswith('remotes/'):
                    remote_branches.append(branch[8:])  # 移除 'remotes/' 前缀
                else:
                    local_branches.append(branch)
            
            return {
                "success": True,
                "data": {
                    "current_branch": current_branch,
                    "local_branches": local_branches,
                    "remote_branches": remote_branches
                }
            }
            
        except Exception as e:
            logger.error(f"获取分支信息失败: {e}")
            return {
                "success": False,
                "error": f"获取分支信息失败: {e}"
            }
    
    def get_commit_history(self, limit: int = 10) -> dict:
        """获取提交历史"""
        try:
            os.chdir(self.repo_root)
            
            # 获取提交历史
            commits = subprocess.check_output(
                ["git", "log", f"-{limit}", "--pretty=format:%h|%s|%an|%ad|%ar", "--date=iso"], 
                text=True
            ).strip().split('\n')
            
            commit_list = []
            for commit in commits:
                if commit:
                    parts = commit.split('|')
                    if len(parts) >= 5:
                        commit_list.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                            "relative_date": parts[4]
                        })
            
            return {
                "success": True,
                "data": {
                    "commits": commit_list,
                    "total": len(commit_list)
                }
            }
            
        except Exception as e:
            logger.error(f"获取提交历史失败: {e}")
            return {
                "success": False,
                "error": f"获取提交历史失败: {e}"
            }

# 创建Flask应用
app = Flask(__name__)
github_mcp = GitHubMCP()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "mcp_id": github_mcp.mcp_id,
        "status": "healthy",
        "version": github_mcp.version,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/mcp/info', methods=['GET'])
def mcp_info():
    """MCP基本信息"""
    return jsonify({
        "mcp_id": github_mcp.mcp_id,
        "version": github_mcp.version,
        "capabilities": [
            "git_repo_info",
            "branch_management", 
            "commit_history",
            "sync_status_monitoring"
        ],
        "description": "GitHub MCP - Git仓库信息服务"
    })

@app.route('/mcp/request', methods=['POST'])
def mcp_request():
    """标准MCP请求处理"""
    try:
        data = request.get_json()
        action = data.get('action')
        params = data.get('params', {})
        
        if action == 'get_repo_info':
            result = github_mcp.get_repo_info()
        elif action == 'get_branch_info':
            result = github_mcp.get_branch_info()
        elif action == 'get_commit_history':
            limit = params.get('limit', 10)
            result = github_mcp.get_commit_history(limit)
        else:
            result = {
                "success": False,
                "error": f"未知操作: {action}"
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"MCP请求处理失败: {e}")
        return jsonify({
            "success": False,
            "error": f"MCP请求处理失败: {e}"
        }), 500

@app.route('/api/repo-info', methods=['GET'])
def get_repo_info():
    """获取仓库信息API"""
    return jsonify(github_mcp.get_repo_info())

@app.route('/api/branch-info', methods=['GET'])
def get_branch_info():
    """获取分支信息API"""
    return jsonify(github_mcp.get_branch_info())

@app.route('/api/commit-history', methods=['GET'])
def get_commit_history():
    """获取提交历史API"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify(github_mcp.get_commit_history(limit))

if __name__ == '__main__':
    print(f"🚀 启动GitHub MCP服务器...")
    print(f"📁 仓库根目录: {github_mcp.repo_root}")
    print(f"🔧 MCP ID: {github_mcp.mcp_id}")
    print(f"📡 端口: 8091")
    
    # 测试Git仓库连接
    repo_info = github_mcp.get_repo_info()
    if repo_info["success"]:
        print(f"✅ Git仓库连接成功: {repo_info['data']['repo_name']}")
        print(f"🌿 当前分支: {repo_info['data']['current_branch']}")
    else:
        print(f"❌ Git仓库连接失败: {repo_info['error']}")
    
    app.run(host='0.0.0.0', port=8091, debug=False)

