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

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
import logging
import json
import time

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

class AuthenticatedMCPClient:
    """
    使用官方 MCP SDK 的带 Bearer Token 鉴权的客户端（支持 SSE）
    """
    
    def __init__(self, server_url: str = "http://localhost:8000", token: Optional[str] = None):
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.initialized = False
        self.request_counter = 0
        self.id = self._generate_id()
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    def set_token(self, token: str):
        """设置或更新 Bearer Token"""
        self.token = token
        logger.info("Bearer Token 已更新")
        
    def _get_headers(self) -> Dict[str, str]:
        """获取 HTTP 请求头，包含认证信息"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
        
    async def connect(self):
        """连接到 MCP 服务器"""
        if self.http_session is None:
            self.http_session = aiohttp.ClientSession()
        
        await self.initialize()
        
    async def close(self):
        """关闭连接"""
        if self.http_session:
            await self.http_session.close()
        self.initialized = False
        
    async def initialize(self):
        """初始化 MCP 连接 - 完整的初始化流程"""
        if self.initialized:
            return
            
        try:
            # 步骤1: 发送 initialize 请求
            init_request = {
                "jsonrpc": "2.0",
                "id": self.id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                    },
                    "clientInfo": {
                        "name": "Python MCP Client",
                        "version": "1.0.0"
                    }
                }
            }
            
            logger.info("发送初始化请求...")
            init_response = await self._send_sse_request(init_request)
            
            if init_response and 'result' in init_response:
                logger.info("✅ 初始化请求成功")
                
                # 步骤2: 发送 initialized 通知（没有 id，因为是通知不是请求）
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {}
                }
                
                # 对于通知，我们不需要等待响应
                await self._send_notification(initialized_notification)
                logger.info("✅ 发送 initialized 通知")
                
                # 给服务器就绪时间
                await asyncio.sleep(1)

                self.initialized = True
                logger.info("MCP 客户端初始化完成")
                
            elif init_response and 'error' in init_response:
                error_msg = init_response['error']
                if error_msg.get('code') == -32001:
                    raise Exception("认证失败: 无效的 Token 或未授权访问")
                else:
                    raise Exception(f"初始化失败: {error_msg}")
            else:
                logger.error("MCP 客户端初始化失败：没有收到有效响应")
                
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise

    async def _send_notification(self, notification_data: Dict[str, Any]):
        """发送通知（不需要响应的消息）"""
        if not self.http_session:
            raise RuntimeError("HTTP 客户端未连接")
            
        try:
            headers = self._get_headers()
            
            async with self.http_session.post(
                f'{self.server_url}/mcp', 
                json=notification_data, 
                headers=headers
            ) as response:
                # 通知不需要处理响应
                if response.status != 200:
                    logger.warning(f"通知发送失败，状态码: {response.status}")
                    
        except Exception as e:
            logger.warning(f"通知发送失败: {e}")
            
    async def _send_sse_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """通过 SSE 发送 JSON-RPC 请求并处理流式响应"""
        if not self.http_session:
            raise RuntimeError("HTTP 客户端未连接")
            
        try:
            headers = self._get_headers()
            request_id = request_data.get('id')
            
            logger.info(f"发送 SSE 请求到: {self.server_url}/mcp")
            logger.info(f"请求方法: {request_data.get('method')}")
            logger.info(f"请求ID: {request_id}")           

            async with self.http_session.post(
                f'{self.server_url}/mcp', 
                json=request_data, 
                headers=headers
            ) as response:
                
                # logger.info(f"响应状态码: {response.status}")
                # async for line in response.content:
                #     line = line.decode('utf-8').strip()
                #     if line:
                #         print(f"Raw: {line}")
                #         if line.startswith('data: '):
                #             try:
                #                 json_data = json.loads(line[6:])
                #                 print(f"JSON: {json.dumps(json_data, indent=2)}")
                #             except:
                #                 print(f"Non-JSON: {line[6:]}")
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"HTTP 请求失败，状态码: {response.status}, 响应: {error_text}")
                    if response.status == 401:
                        raise Exception("认证失败: 无效的 Bearer Token")
                    elif response.status == 403:
                        raise Exception("权限不足: 没有访问权限")
                    else:
                        raise Exception(f"服务器错误: {response.status} - {error_text}")
                
                # 处理 SSE 流
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if not line:
                        continue
                        
                    logger.debug(f"SSE 原始数据: {line}")
                    
                    # 解析 SSE 数据
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 'data: ' 前缀
                        if data_str == '[DONE]':
                            break
                            
                        try:
                            data = json.loads(data_str)
                            # 检查是否是对应请求的响应
                            if data.get('id') == request_id:
                                logger.debug(f"找到匹配的响应: {data}")
                                return data
                            else:
                                logger.debug(f"忽略不匹配的响应 ID: {data.get('id')}")
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON 解析失败: {e}, 原始数据: {data_str}")
                            continue
                            
            logger.warning(f"未找到匹配请求 ID {request_id} 的响应")
            return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"网络请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"请求发送失败: {e}")
            raise

    async def list_tools(self) -> List[MCPTool]:
        """列出所有可用工具"""
        if not self.initialized:
            raise RuntimeError("客户端未初始化，请先完成初始化流程")
            
        request = {
            "jsonrpc": "2.0",
            "id": self.id,
            "method": "tools/list"
        }
        
        logger.info("请求工具列表...")
        response = await self._send_sse_request(request)
        
        if response and 'result' in response:
            tools = []
            for tool_data in response['result'].get('tools', []):
                tool = MCPTool(
                    name=tool_data['name'],
                    description=tool_data.get('description', ''),
                    input_schema=tool_data.get('inputSchema', {})
                )
                tools.append(tool)
            logger.info(f"找到 {len(tools)} 个工具")
            return tools
            
        elif response and 'error' in response:
            error_msg = response['error']
            raise Exception(f"获取工具列表失败: {error_msg}")
            
        return []
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.initialized:
            raise RuntimeError("客户端未初始化，请先完成初始化流程")
            
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        logger.info(f"调用工具: {tool_name}")
        response = await self._send_sse_request(request)
        
        if response and 'result' in response:
            logger.info(f"工具调用成功: {tool_name}")
            return response['result']
        elif response and 'error' in response:
            error_msg = response['error']
            if error_msg.get('code') == -32001:
                raise Exception(f"工具调用失败: 认证错误 - {error_msg.get('message')}")
            else:
                raise Exception(f"工具调用失败: {error_msg}")
        else:
            raise Exception("工具调用失败: 未知错误")
            
    async def list_resources(self) -> List[MCPResource]:
        """列出所有可用资源"""
        if not self.initialized:
            raise RuntimeError("客户端未初始化，请先完成初始化流程")
            
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "resources/list"
        }
        
        logger.info("请求资源列表...")
        response = await self._send_sse_request(request)
        
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
            logger.info(f"找到 {len(resources)} 个资源")
            return resources
            
        elif response and 'error' in response:
            error_msg = response['error']
            raise Exception(f"获取资源列表失败: {error_msg}")
            
        return []
        
    async def read_resource(self, uri: str) -> str:
        """读取资源内容"""
        if not self.initialized:
            raise RuntimeError("客户端未初始化，请先完成初始化流程")
            
        request = {
            "jsonrpc": "2.0",
            "id": self._generate_id(),
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }
        
        logger.info(f"读取资源: {uri}")
        response = await self._send_sse_request(request)
        
        if response and 'result' in response:
            contents = response['result'].get('contents', '')
            if isinstance(contents, list):
                # 处理内容列表
                text_content = ""
                for content in contents:
                    if content.get('type') == 'text':
                        text_content += content.get('text', '')
                return text_content
            elif isinstance(contents, str):
                return contents
            else:
                return str(contents)
        elif response and 'error' in response:
            error_msg = response['error']
            if error_msg.get('code') == -32001:
                raise Exception(f"资源读取失败: 认证错误 - {error_msg.get('message')}")
            else:
                raise Exception(f"资源读取失败: {error_msg}")
        else:
            raise Exception("资源读取失败: 未知错误")
            
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.initialized:
                return False
                
            # tools = await self.list_tools()
            return True
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False
            
    def _generate_id(self) -> int:
        """生成唯一的请求 ID"""
        self.request_counter += 1
        return int(time.time() * 1000) + self.request_counter
    
    async def retry_request(self,func, max_retries=3, delay=3):
        """重试请求，直到成功或达到最大重试次数"""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                print(f"尝试失败 ({attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise  # 最后一次重试仍然失败则抛出异常
                await asyncio.sleep(delay)
                delay *= 2  # 延迟逐渐增加（指数退避）

    async def list_tools_with_retry(self) -> List[MCPTool]:
        """带重试的工具列表请求"""
        return await self.retry_request(self.list_tools)    