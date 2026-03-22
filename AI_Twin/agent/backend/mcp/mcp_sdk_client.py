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
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

SERVER_URL = "http://192.168.193.12:31445/mcp"  # 确保使用 /mcp 端点
TOKEN = os.getenv("MCP_TOKEN", "123")

async def main():
    if not TOKEN:
        print("❌ 请先 export MCP_TOKEN=<your_bearer_token>")
        return

    headers = {"Authorization": f"Bearer {TOKEN}","Content-Type": "application/json","Accept": "application/json, text/event-stream"}

    print(f"🔗 连接到: {SERVER_URL}")
    
    try:
        # 尝试使用 streamable HTTP 传输
        print("📡 尝试 streamable HTTP 传输...")
        async with streamablehttp_client(url=SERVER_URL, headers=headers) as (read, write, get_session_id):
            await run_session(read, write)
            
    except Exception as e:
        print(f"❌ Streamable HTTP 失败: {e}")
        print("📡 尝试 SSE 传输...")
        
        try:
            async with sse_client(url=SERVER_URL, headers=headers) as (read, write, get_session_id):
                await run_session(read, write)
        except Exception as e2:
            print(f"❌ SSE 也失败: {e2}")
            print("🔄 尝试直接 HTTP 请求...")
            await test_direct_http()

async def run_session(read, write):
    """运行 MCP 会话"""
    async with ClientSession(read, write) as session:
        # 初始化会话
        await session.initialize(
            protocol_version="2024-11-05",
            client_name="BearerTokenClient",
            client_version="1.0.0",
        )
        print("✅ MCP 握手完成")

        # 业务调用
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

async def test_direct_http():
    """测试直接 HTTP 请求"""
    import aiohttp
    import json
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    init_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "TestClient", "version": "1.0.0"}
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(SERVER_URL, json=init_data, headers=headers) as response:
            print(f"📊 直接 HTTP 测试状态码: {response.status}")
            if response.status == 200:
                print("✅ 直接 HTTP 连接成功")
                # 读取 SSE 流
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            print(f"📨 收到: {json.dumps(data, indent=2)}")
                        except:
                            print(f"📨 收到: {line[6:]}")
            else:
                error_text = await response.text()
                print(f"❌ 直接 HTTP 失败: {error_text}")

if __name__ == "__main__":
    asyncio.run(main())