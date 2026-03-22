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

import aiohttp
import asyncio
import json

async def simple_mcp_test():
    """简单的 MCP 测试"""
    token = "123"
    server_url = "http://192.168.193.12:31445/mcp"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': f'Bearer {token}'
    }
    
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "Test", "version": "1.0.0"}
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=data, headers=headers) as response:
            print(f"Status: {response.status}")
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line:
                    print(f"Raw: {line}")
                    if line.startswith('data: '):
                        try:
                            json_data = json.loads(line[6:])
                            print(f"JSON: {json.dumps(json_data, indent=2)}")
                        except:
                            print(f"Non-JSON: {line[6:]}")

if __name__ == "__main__":
    asyncio.run(simple_mcp_test())