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

# build-x86.sh - 在 Apple Silicon 上构建 x86 Docker 镜像

set -e

IMAGE_NAME="your-app"
TAG="x86-latest"

echo "🔧 在 Apple Silicon 上构建 x86 Docker 镜像..."

# 检查是否使用 buildx
if ! docker buildx version > /dev/null 2>&1; then
    echo "❌ Docker Buildx 不可用，请确保 Docker Desktop 已安装并启用 Buildx"
    exit 1
fi

# 创建并使用 buildx 构建器（如果不存在）
docker buildx create --name apple-silicon-x86-builder --use 2>/dev/null || true
docker buildx inspect --bootstrap

echo "📦 开始构建 x86 镜像..."

# 构建 x86 镜像
docker buildx build \
    --platform linux/amd64 \
    --tag $IMAGE_NAME:$TAG \
    --tag $IMAGE_NAME:latest \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --load .  # 将镜像加载到本地 Docker

if [ $? -eq 0 ]; then
    echo "✅ 构建成功!"
else
    echo "❌ 构建失败"
    exit 1
fi

echo "🔍 验证镜像架构..."
# 验证架构
ARCH=$(docker run --rm $IMAGE_NAME:$TAG uname -m)
if [ "$ARCH" = "x86_64" ]; then
    echo "✅ 镜像架构验证通过: $ARCH"
else
    echo "❌ 架构不匹配: $ARCH"
    exit 1
fi

echo "🧪 测试 PyTorch 功能..."
# 测试 PyTorch 是否能正常导入
docker run --rm $IMAGE_NAME:$TAG python -c "
import torch
print(f'PyTorch 版本: {torch.__version__}')
print(f'设备: {torch.device(\"cpu\")}')
print(f'张量测试: {torch.ones(2,3).shape}')
print('✅ PyTorch 测试通过')
"

echo ""
echo "🎉 镜像构建完成!"
echo "📦 镜像名称: $IMAGE_NAME:$TAG"
echo "🏗️  架构: x86_64 (amd64)"
echo ""
echo "运行命令:"
echo "  docker run -it --rm $IMAGE_NAME:$TAG"
echo "  docker run -p 8000:8000 $IMAGE_NAME:$TAG"