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

import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass
class MCPResource:
    uri: str
    name: str
    description: str
    mime_type: str

class MCPClient:
    """
    MCP 客户端实现
    """
    
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def connect(self):
        """连接到 MCP 服务器"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                base_url=self.server_url,
                headers={'Content-Type': 'application/json',"Authorization": "123"}
            )
        await self.initialize()
        
    async def close(self):
        """关闭连接"""
        if self.session:
            await self.session.close()
            self.session = None
        self.initialized = False
        
    async def initialize(self):
        """初始化 MCP 连接"""
        if self.initialized:
            return
            
        try:
            # 发送初始化请求
            # init_request = {
            #     "jsonrpc": "2.0",
            #     "id": 1,
            #     "method": "initialize",
            #     "headers": {
            #         "Authorization": "123"
            #     },
            #     "params": {
            #         "protocolVersion": "2024-11-05",
            #         "capabilities": {
            #             "roots": {"listChanged": True},
            #             "tools": {"listChanged": True}
            #         },
            #         "clientInfo": {
            #             "name": "Python MCP Client",
            #             "version": "1.0.0"
            #         }
            #     }
            # }

            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize"
            }
            
            print(init_request)
            response = await self._send_request(init_request)
            
            if response and 'result' in response:
                self.initialized = True
                logger.info("MCP 客户端初始化成功")
            else:
                logger.error("MCP 客户端初始化失败")
                
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
            
    async def _send_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送 JSON-RPC 请求"""
        if not self.session:
            raise RuntimeError("客户端未连接")
            
        try:
            async with self.session.post('/mcp', json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"请求失败，状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求发送失败: {e}")
            return None
            
    async def list_tools(self) -> List[MCPTool]:
        """列出所有可用工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await self._send_request(request)
        if response and 'result' in response:
            tools = []
            for tool_data in response['result'].get('tools', []):
                tool = MCPTool(
                    name=tool_data['name'],
                    description=tool_data.get('description', ''),
                    input_schema=tool_data.get('inputSchema', {})
                )
                tools.append(tool)
            return tools
        return []
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        if response and 'result' in response:
            return response['result']
        elif response and 'error' in response:
            raise Exception(f"工具调用失败: {response['error']}")
        else:
            raise Exception("工具调用失败: 未知错误")

    async def call_hospital_medical_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """查询医院数据"""
        request = {
            "method": "tools/call",
            "params": {
                "name":  "query_hospital_medical_data",
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        if response and 'result' in response:
            return response['result']
        elif response and 'error' in response:
            raise Exception(f"工具调用失败: {response['error']}")
        else:
            raise Exception("工具调用失败: 未知错误")

    async def list_resources(self) -> List[MCPResource]:
        """列出所有可用资源"""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/list"
        }
        
        response = await self._send_request(request)
        if response and 'result' in response:
            resources = []
            for resource_data in response['result'].get('resources', []):
                resource = MCPResource(
                    uri=resource_data['uri'],
                    name=resource_data.get('name', ''),
                    description=resource_data.get('description', ''),
                    mime_type=resource_data.get('mimeType', 'text/plain')
                )
                resources.append(resource)
            return resources
        return []

    async def read_resource(self, uri: str) -> str:
        """读取资源内容"""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }
        
        response = await self._send_request(request)
        if response and 'result' in response:
            return response['result'].get('contents', '')
        elif response and 'error' in response:
            raise Exception(f"资源读取失败: {response['error']}")
        else:
            raise Exception("资源读取失败: 未知错误")