#!/bin/bash

# Makfile 使用示例脚本
# 此脚本演示了如何使用 Makfile 进行完整的开发和部署流程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

log_info "开始演示 Makfile 使用..."
log_info "项目目录: $(pwd)"
echo ""

# 1. 检查环境
log_info "===== 步骤 1: 检查环境 ====="
make check-env
echo ""

# 2. 显示版本信息
log_info "===== 步骤 2: 显示版本信息 ====="
make version
echo ""

# 3. 显示详细构建信息
log_info "===== 步骤 3: 显示詳細構建信息 ====="
make info
echo ""

# 4. 安装依赖（仅在第一次运行时）
if [ ! -d ".venv" ]; then
    log_info "===== 步骤 4: 安装依赖 ====="
    make install
    log_success "依赖安装完成"
    echo ""
else
    log_warn "虚拟环境已存在, 跳过依赖安装"
    echo ""
fi


# 5. 显示版本信息文件内容
log_info "===== 步骤 5: 显示版本信息文件 ====="
if [ -f "src/version.py" ]; then
    head -20 src/version.py
    log_success "版本文件已生成"
else
    log_error "版本文件未找到"
fi
echo ""

# 6. 构建项目
log_info "===== 步骤 6: 构建项目 ====="
make build
log_success "项目构建完成"
echo ""

# 7. 清理缓存
log_info "===== 步骤 7: 清理缓存 ====="
make clean
log_success "缓存清理完成"
echo ""

# 可选: Docker 构建（需要安装 Docker）
if command -v docker &> /dev/null; then
    read -p "是否构建 Docker 镜像? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "===== 步骤 8: 构建 Docker 镜像 ====="
        make docker-build
        log_success "Docker 镜像构建完成"
        echo ""
        
        # 显示镜像信息
        log_info "===== 可用的 Docker 镜像 ====="
        docker images | grep cybertwin || true
        echo ""
    fi
else
    log_warn "Docker 未安装，跳过 Docker 镜像构建"
    echo ""
fi

# 完成提示
log_success "===== 演示完成 ====="
echo ""
echo "接下来可以运行:"
echo "  - 开发模式: ${GREEN}make dev-run${NC}"
echo "  - 生产模式: ${GREEN}make run${NC}"
echo "  - 运行测试: ${GREEN}make test${NC}"
echo "  - 查看帮助: ${GREEN}make help${NC}"
echo ""
