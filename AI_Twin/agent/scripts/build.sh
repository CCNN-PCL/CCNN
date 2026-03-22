#!/bin/bash
# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# 构建脚本 - 自动注入版本信息

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 日志函数
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取Git信息
get_git_info() {
    local git_commit=""
    local git_branch=""
    
    if command -v git &> /dev/null && [ -d "$PROJECT_ROOT/.git" ]; then
        git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "")
        git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
    fi
    
    echo "$git_commit $git_branch"
}

# 获取版本信息
get_version_info() {
    local version_file="$PROJECT_ROOT/VERSION.json"
    local version="1.0.0"
    local build="dev"
    
    if [ -f "$version_file" ]; then
        version=$(python3 -c "import json; import sys; data=json.load(open('$version_file')); print(data.get('version', '1.0.0'))" 2>/dev/null || echo "1.0.0")
        build=$(python3 -c "import json; import sys; data=json.load(open('$version_file')); print(data.get('build', 'dev'))" 2>/dev/null || echo "dev")
    fi
    
    echo "$version $build"
}

# 构建Docker镜像
build_docker() {
    log_info "开始构建Docker镜像..."
    
    # 获取版本和Git信息
    read version build <<< $(get_version_info)
    read git_commit git_branch <<< $(get_git_info)
    
    local build_date=$(date -Iseconds)
    local image_name="user-agent"
    local image_tag="${version}-${build}"
    
    log_info "构建信息:"
    log_info "  - 版本: ${version}"
    log_info "  - 构建: ${build}"
    log_info "  - Git提交: ${git_commit:-N/A}"
    log_info "  - Git分支: ${git_branch:-N/A}"
    log_info "  - 构建时间: ${build_date}"
    log_info "  - 镜像标签: ${image_tag}"
    
    # 构建命令
    docker build \
        --build-arg BUILD_VERSION="${version}-${build}" \
        --build-arg BUILD_DATE="${build_date}" \
        --build-arg GIT_COMMIT="${git_commit}" \
        --build-arg GIT_BRANCH="${git_branch}" \
        -t "${image_name}:${image_tag}" \
        -t "${image_name}:latest" \
        -f Dockerfile \
        .
    
    if [ $? -eq 0 ]; then
        log_success "Docker镜像构建成功: ${image_name}:${image_tag}"
        
        # 显示镜像信息
        log_info "已构建的镜像:"
        docker images | grep "${image_name}"
    else
        log_error "Docker镜像构建失败"
        exit 1
    fi
}

# 推送Docker镜像
push_docker() {
    local registry="$1"
    
    if [ -z "$registry" ]; then
        log_error "请指定镜像仓库地址"
        echo "用法: $0 push <registry>"
        exit 1
    fi
    
    # 获取版本信息
    read version build <<< $(get_version_info)
    local image_name="user-agent"
    local image_tag="${version}-${build}"
    
    log_info "推送镜像到 ${registry}..."
    
    # 标记镜像
    docker tag "${image_name}:${image_tag}" "${registry}/${image_name}:${image_tag}"
    docker tag "${image_name}:latest" "${registry}/${image_name}:latest"
    
    # 推送镜像
    docker push "${registry}/${image_name}:${image_tag}"
    docker push "${registry}/${image_name}:latest"
    
    if [ $? -eq 0 ]; then
        log_success "镜像推送成功: ${registry}/${image_name}:${image_tag}"
    else
        log_error "镜像推送失败"
        exit 1
    fi
}

# 清理构建缓存
clean_build() {
    log_info "清理构建缓存..."
    
    # 停止并删除容器
    docker stop user-agent-container 2>/dev/null || true
    docker rm user-agent-container 2>/dev/null || true
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除构建缓存
    docker builder prune -f
    
    log_success "构建缓存已清理"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  build             构建Docker镜像（自动注入版本信息）"
    echo "  push <registry>   推送镜像到指定仓库"
    echo "  clean             清理构建缓存"
    echo "  version           显示版本信息"
    echo "  help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build          构建Docker镜像"
    echo "  $0 push registry.example.com  推送镜像到私有仓库"
    echo "  $0 clean          清理构建缓存"
}

# 显示版本信息
show_version() {
    read version build <<< $(get_version_info)
    read git_commit git_branch <<< $(get_git_info)
    
    echo "项目版本信息:"
    echo "  - 版本号: ${version}"
    echo "  - 构建标识: ${build}"
    echo "  - Git提交: ${git_commit:-N/A}"
    echo "  - Git分支: ${git_branch:-N/A}"
    
    if [ -f "$PROJECT_ROOT/VERSION.json" ]; then
        echo ""
        echo "详细版本信息:"
        python3 -m json.tool "$PROJECT_ROOT/VERSION.json" 2>/dev/null || cat "$PROJECT_ROOT/VERSION.json"
    fi
}

# 主函数
main() {
    local command="$1"
    
    case "$command" in
        build)
            build_docker
            ;;
        push)
            push_docker "$2"
            ;;
        clean)
            clean_build
            ;;
        version)
            show_version
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            if [ -z "$command" ]; then
                build_docker
            else
                log_error "未知命令: $command"
                show_help
                exit 1
            fi
            ;;
    esac
}

# 执行主函数
main "$@"
