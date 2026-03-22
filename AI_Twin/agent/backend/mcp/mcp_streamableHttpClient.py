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

"""
Bearer-Token MCP Client (HTTP streamable transport)
Server: http://192.168.193.12:31445/mcp
"""
import asyncio
import os
from mcp import ClientSession
#from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client

SERVER_URL = "http://192.168.193.12:31445/mcp"
TOKEN = os.getenv("MCP_TOKEN", "123")      # export MCP_TOKEN=your_token

async def main():
    if not TOKEN:
        print("❌ 请先 export MCP_TOKEN=<your_bearer_token>")
        return

    # 1. 构造 Bearer 鉴权
    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 2. 建立长连接（sse_client）
    async with sse_client(url=SERVER_URL, headers=headers) as (read, write, get_session_id):
        # 3. 创建会话
        async with ClientSession(read, write) as session:
            # 4. 握手
            await session.initialize(
                protocol_version="2024-11-05",
                client_name="BearerTokenClient",
                client_version="1.0.0",
            )
            print("✅ MCP 握手完成")

            # 5. 业务调用
            tools = await session.list_tools()
            print("📋 工具列表:", [t.name for t in tools.tools])

            if tools.tools:
                tool = tools.tools[0]
                result = await session.call_tool(tool.name, {})
                print(f"🔧 调用 {tool.name} 结果:")
                for item in result.content:
                    if item.type == "text":
                        print(item.text)

            resources = await session.list_resources()
            if resources.resources:
                uri = resources.resources[0].uri
                content = await session.read_resource(uri)
                print(f"📄 资源 {uri} 前 200 字符:\n{content[:200]}")

if __name__ == "__main__":
    asyncio.run(main())