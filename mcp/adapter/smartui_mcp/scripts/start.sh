#!/bin/bash

# SmartUI MCP 启动脚本

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 默认配置
DEFAULT_CONFIG="$PROJECT_DIR/config/smartui_config.yaml"
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8000"
DEFAULT_LOG_LEVEL="INFO"

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

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
SmartUI MCP 启动脚本

用法: $0 [选项]

选项:
    -c, --config FILE       配置文件路径 (默认: $DEFAULT_CONFIG)
    -h, --host HOST         服务器主机 (默认: $DEFAULT_HOST)
    -p, --port PORT         服务器端口 (默认: $DEFAULT_PORT)
    -d, --debug             启用调试模式
    -l, --log-level LEVEL   日志级别 (默认: $DEFAULT_LOG_LEVEL)
    --daemon                后台运行
    --pid-file FILE         PID文件路径 (仅在daemon模式下)
    --help                  显示此帮助信息

环境变量:
    SMARTUI_CONFIG          配置文件路径
    SMARTUI_HOST            服务器主机
    SMARTUI_PORT            服务器端口
    SMARTUI_DEBUG           调试模式 (true/false)
    SMARTUI_LOG_LEVEL       日志级别

示例:
    $0                                          # 使用默认配置启动
    $0 -c /path/to/config.yaml                  # 使用指定配置文件
    $0 -h 127.0.0.1 -p 8080 -d                 # 指定主机、端口并启用调试
    $0 --daemon --pid-file /var/run/smartui.pid # 后台运行

EOF
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 检查虚拟环境
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warn "未检测到虚拟环境，建议使用虚拟环境运行"
    fi
    
    log_info "依赖检查完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
        pip3 install -r "$PROJECT_DIR/requirements.txt"
    else
        log_warn "requirements.txt 文件不存在，跳过依赖安装"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/data"
    mkdir -p "$PROJECT_DIR/cache"
    mkdir -p "$PROJECT_DIR/tmp"
    
    log_info "目录创建完成"
}

# 验证配置文件
validate_config() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        log_error "配置文件不存在: $config_file"
        exit 1
    fi
    
    log_info "配置文件验证通过: $config_file"
}

# 启动服务器
start_server() {
    local config_file="$1"
    local host="$2"
    local port="$3"
    local debug="$4"
    local log_level="$5"
    local daemon="$6"
    local pid_file="$7"
    
    log_info "启动 SmartUI MCP 服务器..."
    log_info "配置文件: $config_file"
    log_info "主机: $host"
    log_info "端口: $port"
    log_info "调试模式: $debug"
    log_info "日志级别: $log_level"
    
    # 构建启动命令
    local cmd="python3 -m src.main_server"
    
    if [[ -n "$config_file" ]]; then
        cmd="$cmd --config $config_file"
    fi
    
    if [[ -n "$host" ]]; then
        cmd="$cmd --host $host"
    fi
    
    if [[ -n "$port" ]]; then
        cmd="$cmd --port $port"
    fi
    
    if [[ "$debug" == "true" ]]; then
        cmd="$cmd --debug"
    fi
    
    # 设置环境变量
    export SMARTUI_LOG_LEVEL="$log_level"
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    
    # 切换到项目目录
    cd "$PROJECT_DIR"
    
    if [[ "$daemon" == "true" ]]; then
        # 后台运行
        log_info "以守护进程模式启动..."
        
        if [[ -n "$pid_file" ]]; then
            nohup $cmd > logs/smartui_mcp.out 2>&1 &
            echo $! > "$pid_file"
            log_info "PID文件: $pid_file"
        else
            nohup $cmd > logs/smartui_mcp.out 2>&1 &
        fi
        
        log_info "服务器已在后台启动，PID: $!"
    else
        # 前台运行
        log_info "启动服务器..."
        exec $cmd
    fi
}

# 主函数
main() {
    # 默认参数
    local config_file="${SMARTUI_CONFIG:-$DEFAULT_CONFIG}"
    local host="${SMARTUI_HOST:-$DEFAULT_HOST}"
    local port="${SMARTUI_PORT:-$DEFAULT_PORT}"
    local debug="${SMARTUI_DEBUG:-false}"
    local log_level="${SMARTUI_LOG_LEVEL:-$DEFAULT_LOG_LEVEL}"
    local daemon="false"
    local pid_file=""
    local install_deps="false"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                config_file="$2"
                shift 2
                ;;
            -h|--host)
                host="$2"
                shift 2
                ;;
            -p|--port)
                port="$2"
                shift 2
                ;;
            -d|--debug)
                debug="true"
                shift
                ;;
            -l|--log-level)
                log_level="$2"
                shift 2
                ;;
            --daemon)
                daemon="true"
                shift
                ;;
            --pid-file)
                pid_file="$2"
                shift 2
                ;;
            --install-deps)
                install_deps="true"
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
    
    # 显示启动信息
    log_info "SmartUI MCP 服务器启动脚本"
    log_info "项目目录: $PROJECT_DIR"
    
    # 检查依赖
    check_dependencies
    
    # 安装依赖（如果需要）
    if [[ "$install_deps" == "true" ]]; then
        install_dependencies
    fi
    
    # 创建目录
    create_directories
    
    # 验证配置
    validate_config "$config_file"
    
    # 启动服务器
    start_server "$config_file" "$host" "$port" "$debug" "$log_level" "$daemon" "$pid_file"
}

# 信号处理
trap 'log_info "收到中断信号，正在停止..."; exit 0' INT TERM

# 运行主函数
main "$@"

