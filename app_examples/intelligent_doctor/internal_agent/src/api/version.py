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

# -*- coding: utf-8 -*-
"""
版本信息API端点

提供获取应用版本信息的接口
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.version import get_version, get_version_info, get_version_string

router = APIRouter(prefix="/version", tags=["version"])


class VersionResponse(BaseModel):
    """版本信息响应模型"""

    version: str
    version_string: str
    git_commit: str
    build_date: str


class VersionDetailResponse(BaseModel):
    """详细版本信息响应模型"""

    version: str
    version_string: str
    git_commit: str
    build_date: str


@router.get("", response_model=VersionResponse)
async def get_version_info_endpoint():
    """
    获取版本信息

    Returns:
        VersionResponse: 包含版本号、完整版本字符串、git提交和构建时间的版本信息

    Example:
        GET /version
        {
            "version": "0.1.3",
            "version_string": "0.1.3+abc1234",
            "git_commit": "abc1234",
            "build_date": "2026-02-27T10:30:00Z"
        }
    """
    info = get_version_info()
    return VersionResponse(
        version=info["version"],
        version_string=info["version_string"],
        git_commit=info["git_commit"],
        build_date=info["build_date"],
    )


@router.get("/simple")
async def get_simple_version():
    """
    获取简单版本号

    Returns:
        dict: 包含版本号的简单响应

    Example:
        GET /version/simple
        {
            "version": "0.1.3"
        }
    """
    return {"version": get_version()}


@router.get("/string")
async def get_version_string_endpoint():
    """
    获取版本字符串（包含git提交）

    Returns:
        dict: 包含版本字符串的响应

    Example:
        GET /version/string
        {
            "version": "0.1.3+abc1234"
        }
    """
    return {"version": get_version_string()}


@router.get("/detail", response_model=VersionDetailResponse)
async def get_detailed_version_info():
    """
    获取详细版本信息

    Returns:
        VersionDetailResponse: 完整的版本信息，包括所有构建和版本相关的元数据

    Example:
        GET /version/detail
        {
            "version": "0.1.3",
            "version_string": "0.1.3+abc1234",
            "git_commit": "abc1234",
            "build_date": "2026-02-27T10:30:00Z"
        }
    """
    info = get_version_info()
    return VersionDetailResponse(
        version=info["version"],
        version_string=info["version_string"],
        git_commit=info["git_commit"],
        build_date=info["build_date"],
    )
