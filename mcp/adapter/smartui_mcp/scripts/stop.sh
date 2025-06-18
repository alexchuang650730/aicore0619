#!/bin/bash

# SmartUI MCP 停止脚本

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
SmartUI MCP 停止脚本

用法: $0 [选项]

选项:
    --pid-file FILE         PID文件路径
    --force                 强制停止（使用SIGKILL）
    --timeout SECONDS       等待超时时间（默认: 30秒）
    --help                  显示此帮助信息

示例:
    $0                                      # 停止所有SmartUI MCP进程
    $0 --pid-file /var/run/smartui.pid      # 使用PID文件停止
    $0 --force                              # 强制停止
    $0 --timeout 60                         # 设置60秒超时

EOF
}

# 查找进程
find_processes() {
    local processes
    processes=$(pgrep -f "smartui.*main_server" 2>/dev/null || true)
    echo "$processes"
}

# 停止进程（通过PID文件）
stop_by_pid_file() {
    local pid_file="$1"
    local force="$2"
    local timeout="$3"
    
    if [[ ! -f "$pid_file" ]]; then
        log_error "PID文件不存在: $pid_file"
        return 1
    fi
    
    local pid
    pid=$(cat "$pid_file")
    
    if [[ -z "$pid" ]]; then
        log_error "PID文件为空: $pid_file"
        return 1
    fi
    
    # 检查进程是否存在
    if ! kill -0 "$pid" 2>/dev/null; then
        log_warn "进程 $pid 不存在，删除PID文件"
        rm -f "$pid_file"
        return 0
    fi
    
    log_info "停止进程 $pid..."
    
    if [[ "$force" == "true" ]]; then
        # 强制停止
        kill -KILL "$pid"
        log_info "进程 $pid 已强制停止"
    else
        # 优雅停止
        kill -TERM "$pid"
        
        # 等待进程停止
        local count=0
        while kill -0 "$pid" 2>/dev/null && [[ $count -lt $timeout ]]; do
            sleep 1
            ((count++))
        done
        
        if kill -0 "$pid" 2>/dev/null; then
            log_warn "进程 $pid 在 $timeout 秒内未停止，强制停止"
            kill -KILL "$pid"
        fi
        
        log_info "进程 $pid 已停止"
    fi
    
    # 删除PID文件
    rm -f "$pid_file"
}

# 停止所有进程
stop_all_processes() {
    local force="$1"
    local timeout="$2"
    
    local processes
    processes=$(find_processes)
    
    if [[ -z "$processes" ]]; then
        log_info "未找到运行中的SmartUI MCP进程"
        return 0
    fi
    
    log_info "找到以下进程:"
    echo "$processes" | while read -r pid; do
        if [[ -n "$pid" ]]; then
            local cmd
            cmd=$(ps -p "$pid" -o cmd= 2>/dev/null || echo "未知")
            log_info "  PID: $pid, 命令: $cmd"
        fi
    done
    
    # 停止进程
    echo "$processes" | while read -r pid; do
        if [[ -n "$pid" ]]; then
            log_info "停止进程 $pid..."
            
            if [[ "$force" == "true" ]]; then
                kill -KILL "$pid" 2>/dev/null || true
            else
                kill -TERM "$pid" 2>/dev/null || true
            fi
        fi
    done
    
    if [[ "$force" != "true" ]]; then
        # 等待进程停止
        log_info "等待进程停止..."
        local count=0
        while [[ $count -lt $timeout ]]; do
            local remaining
            remaining=$(find_processes)
            
            if [[ -z "$remaining" ]]; then
                log_info "所有进程已停止"
                return 0
            fi
            
            sleep 1
            ((count++))
        done
        
        # 强制停止剩余进程
        local remaining
        remaining=$(find_processes)
        if [[ -n "$remaining" ]]; then
            log_warn "在 $timeout 秒内未完全停止，强制停止剩余进程"
            echo "$remaining" | while read -r pid; do
                if [[ -n "$pid" ]]; then
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            done
        fi
    fi
    
    log_info "所有进程已停止"
}

# 清理资源
cleanup_resources() {
    log_info "清理资源..."
    
    # 清理临时文件
    if [[ -d "$PROJECT_DIR/tmp" ]]; then
        rm -rf "$PROJECT_DIR/tmp"/*
    fi
    
    # 清理缓存（可选）
    if [[ -d "$PROJECT_DIR/cache" ]]; then
        find "$PROJECT_DIR/cache" -type f -mtime +7 -delete 2>/dev/null || true
    fi
    
    # 清理日志（保留最近的）
    if [[ -d "$PROJECT_DIR/logs" ]]; then
        find "$PROJECT_DIR/logs" -name "*.log.*" -mtime +30 -delete 2>/dev/null || true
    fi
    
    log_info "资源清理完成"
}

# 主函数
main() {
    local pid_file=""
    local force="false"
    local timeout="30"
    local cleanup="false"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --pid-file)
                pid_file="$2"
                shift 2
                ;;
            --force)
                force="true"
                shift
                ;;
            --timeout)
                timeout="$2"
                shift 2
                ;;
            --cleanup)
                cleanup="true"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "SmartUI MCP 服务器停止脚本"
    log_info "项目目录: $PROJECT_DIR"
    
    if [[ -n "$pid_file" ]]; then
        # 使用PID文件停止
        stop_by_pid_file "$pid_file" "$force" "$timeout"
    else
        # 停止所有进程
        stop_all_processes "$force" "$timeout"
    fi
    
    # 清理资源（如果需要）
    if [[ "$cleanup" == "true" ]]; then
        cleanup_resources
    fi
    
    log_info "SmartUI MCP 服务器已停止"
}

# 运行主函数
main "$@"

