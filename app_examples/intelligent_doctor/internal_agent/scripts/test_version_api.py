#!/usr/bin/env python3
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
版本信息 API 调用示例

演示如何通过 API 获取应用的版本信息
"""

import asyncio
import json
from typing import Any, Dict, Optional

import httpx


class VersionAPIClient:
    """版本信息 API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端

        Args:
            base_url: 应用的基础 URL
        """
        self.base_url = base_url.rstrip("/")
        self.api_version = "/api/v1"

    async def get_version_info(self) -> Optional[Dict[str, Any]]:
        """
        获取版本信息

        Returns:
            版本信息字典，包含 version, version_string, git_commit, build_date
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{self.api_version}/version"
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                print(f"❌ 请求失败: {e}")
                return None
            except httpx.HTTPStatusError as e:
                print(f"❌ HTTP 错误: {e.response.status_code}")
                return None

    async def get_simple_version(self) -> Optional[str]:
        """
        获取简单版本号

        Returns:
            版本号字符串
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{self.api_version}/version/simple"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("version")
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"❌ 获取简单版本失败: {e}")
                return None

    async def get_version_string(self) -> Optional[str]:
        """
        获取版本字符串（包含 git 提交）

        Returns:
            版本字符串，格式: version+git_commit
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{self.api_version}/version/string"
                )
                response.raise_for_status()
                data = response.json()
                return data.get("version")
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"❌ 获取版本字符串失败: {e}")
                return None

    async def get_detailed_version(self) -> Optional[Dict[str, Any]]:
        """
        获取详细版本信息

        Returns:
            详细版本信息字典
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{self.api_version}/version/detail"
                )
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"❌ 获取详细版本信息失败: {e}")
                return None


def print_section(title: str) -> None:
    """打印章节标题"""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}\n")


def print_result(title: str, data: Any) -> None:
    """打印结果"""
    print(f"\n📌 {title}")
    print("-" * 50)
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"  {data}")


async def main():
    """主函数"""
    print("\n" + "🚀 " * 10)
    print("         版本信息 API 调用示例")
    print("🚀 " * 10 + "\n")

    client = VersionAPIClient("http://localhost:8000")

    print_section("检查应用连接")
    print("尝试连接到应用...")
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ 应用已连接并在线")
            else:
                print(f"⚠️  应用响应状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 无法连接到应用: {e}")
            print("\n💡 请先启动应用:")
            print("   make dev-run  (开发模式)")
            print("   make run      (生产模式)")
            return

    # 1. 获取简单版本号
    print_section("1. 获取简单版本号")
    print("API: GET /api/v1/version/simple")
    version = await client.get_simple_version()
    if version:
        print_result("简单版本号", version)

    # 2. 获取完整版本信息
    print_section("2. 获取完整版本信息")
    print("API: GET /api/v1/version")
    info = await client.get_version_info()
    if info:
        print_result("完整版本信息", info)

    # 3. 获取版本字符串
    print_section("3. 获取版本字符串（包含 git 提交）")
    print("API: GET /api/v1/version/string")
    version_str = await client.get_version_string()
    if version_str:
        print_result("版本字符串", version_str)

    # 4. 获取详细版本信息
    print_section("4. 获取详细版本信息")
    print("API: GET /api/v1/version/detail")
    detail = await client.get_detailed_version()
    if detail:
        print_result("详细版本信息", detail)

    # 完成提示
    print_section("API 端点总结")
    print("""
以下是所有可用的版本 API 端点:

1️⃣  GET /api/v1/version
   获取完整版本信息
   响应: {version, version_string, git_commit, build_date}

2️⃣  GET /api/v1/version/simple
   获取简单版本号
   响应: {version}

3️⃣  GET /api/v1/version/string
   获取版本字符串（版本号 + git提交）
   响应: {version}

4️⃣  GET /api/v1/version/detail
   获取详细版本信息
   响应: {version, version_string, git_commit, build_date}

💡 在 FastAPI Swagger UI 中也可以查看这些端点:
   http://localhost:8000/api/docs

📝 示例 curl 命令:

   # 获取完整版本信息
   curl -X GET "http://localhost:8000/api/v1/version"
   
   # 获取简单版本号
   curl -X GET "http://localhost:8000/api/v1/version/simple"
   
   # 获取详细版本信息
   curl -X GET "http://localhost:8000/api/v1/version/detail"
    """)

    print("\n✨ " * 15 + "\n")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
