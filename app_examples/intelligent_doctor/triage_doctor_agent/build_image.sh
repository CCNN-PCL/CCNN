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

# 构建并导出 triage-agent 镜像为 tar 包

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}构建 triage-agent 镜像${NC}"
echo -e "${GREEN}========================================${NC}"

# 镜像名称和标签
IMAGE_NAME="triage-agent"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# tar包文件名
TAR_FILE="${IMAGE_NAME}.tar"

# 检查Dockerfile是否存在
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}错误: 未找到 Dockerfile${NC}"
    exit 1
fi

# 检查requirements.txt是否存在
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}错误: 未找到 requirements.txt${NC}"
    exit 1
fi

echo -e "${YELLOW}步骤 1: 构建 Docker 镜像...${NC}"
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -ne 0 ]; then
    echo -e "${RED}镜像构建失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 镜像构建成功${NC}"

# 显示镜像信息
echo -e "\n${YELLOW}镜像信息:${NC}"
docker images "${FULL_IMAGE_NAME}"

echo -e "\n${YELLOW}步骤 2: 导出镜像为 tar 包...${NC}"
docker save -o "${TAR_FILE}" "${FULL_IMAGE_NAME}"

if [ $? -ne 0 ]; then
    echo -e "${RED}镜像导出失败${NC}"
    exit 1
fi

# 检查tar包是否生成
if [ -f "${TAR_FILE}" ]; then
    TAR_SIZE=$(du -h "${TAR_FILE}" | cut -f1)
    echo -e "${GREEN}✓ 镜像导出成功${NC}"
    echo -e "${GREEN}文件: ${TAR_FILE}${NC}"
    echo -e "${GREEN}大小: ${TAR_SIZE}${NC}"
    echo -e "\n${YELLOW}可以使用以下命令加载镜像:${NC}"
    echo -e "docker load -i ${TAR_FILE}"
else
    echo -e "${RED}错误: tar包未生成${NC}"
    exit 1
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}完成！${NC}"
echo -e "${GREEN}========================================${NC}"




