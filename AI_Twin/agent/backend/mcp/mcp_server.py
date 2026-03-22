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
from aiohttp import web
import json
from typing import Dict, Any
from backend.mcp.mcp_client_bak import MCPClient

class MockMCPServer:
    """模拟 MCP 服务器用于测试"""
    
    def __init__(self):
        self.app = web.Application()
        self.app.router.add_post('/mcp', self.handle_mcp_request)
        
    async def handle_mcp_request(self, request):
        """处理 MCP 请求"""
        try:
            data = await request.json()
            method = data.get('method')
            request_id = data.get('id', 1)
            
            if method == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "Mock MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == 'tools/list':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "calculator",
                                "description": "简单的数学计算器",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "operation": {
                                            "type": "string",
                                            "enum": ["add", "subtract", "multiply", "divide"]
                                        },
                                        "a": {"type": "number"},
                                        "b": {"type": "number"}
                                    },
                                    "required": ["operation", "a", "b"]
                                }
                            },
                            {
                                "name": "weather",
                                "description": "获取天气信息",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "city": {"type": "string"}
                                    },
                                    "required": ["city"]
                                }
                            }
                        ]
                    }
                }
            elif method == 'tools/call':
                tool_name = data['params']['name']
                arguments = data['params']['arguments']
                
                if tool_name == 'calculator':
                    result = self._handle_calculator(arguments)
                elif tool_name == 'weather':
                    result = self._handle_weather(arguments)
                else:
                    result = {"error": f"未知工具: {tool_name}"}
                    
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            elif method == 'resources/list':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "resources": [
                            {
                                "uri": "file:///example.txt",
                                "name": "示例文件",
                                "description": "这是一个示例资源文件",
                                "mimeType": "text/plain"
                            }
                        ]
                    }
                }
            elif method == 'resources/read':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "contents": "这是一个示例资源文件的内容\nHello MCP!"
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"方法未找到: {method}"
                    }
                }
                
            return web.Response(
                text=json.dumps(response, ensure_ascii=False),
                content_type='application/json'
            )
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": data.get('id', 1),
                "error": {
                    "code": -32603,
                    "message": f"内部错误: {str(e)}"
                }
            }
            return web.Response(
                text=json.dumps(error_response),
                content_type='application/json'
            )
    
    def _handle_calculator(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理计算器工具调用"""
        operation = arguments['operation']
        a = arguments['a']
        b = arguments['b']
        
        if operation == 'add':
            result = a + b
        elif operation == 'subtract':
            result = a - b
        elif operation == 'multiply':
            result = a * b
        elif operation == 'divide':
            if b == 0:
                return {"error": "除数不能为零"}
            result = a / b
        else:
            return {"error": f"未知操作: {operation}"}
            
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"计算结果: {a} {operation} {b} = {result}"
                }
            ]
        }
    
    def _handle_weather(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """处理天气工具调用"""
        city = arguments['city']
        # 模拟天气数据
        weather_data = {
            "beijing": "晴，25°C",
            "shanghai": "多云，23°C", 
            "guangzhou": "雨，28°C",
            "shenzhen": "阴，26°C"
        }
        
        weather = weather_data.get(city.lower(), "未知城市")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"{city}的天气: {weather}"
                }
            ]
        }

async def test_mcp_client():
    """测试 MCP 客户端"""
    # 启动模拟服务器
    server = MockMCPServer()
    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8765)
    await site.start()
    
    print("🚀 模拟 MCP 服务器已启动在 http://localhost:8765")
    
    try:
        # 测试客户端
        async with MCPClient("http://localhost:8765") as client:
            print("\n📋 测试1: 列出可用工具")
            tools = await client.list_tools()
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n🧪 测试2: 调用计算器工具")
            result = await client.call_tool("calculator", {
                "operation": "add",
                "a": 10,
                "b": 5
            })
            print(f"  结果: {result}")
            
            print("\n🧪 测试3: 调用天气工具")
            result = await client.call_tool("weather", {
                "city": "Beijing"
            })
            print(f"  结果: {result}")
            
            print("\n📚 测试4: 列出资源")
            resources = await client.list_resources()
            for resource in resources:
                print(f"  - {resource.name}: {resource.uri}")
            
            print("\n📖 测试5: 读取资源")
            if resources:
                content = await client.read_resource(resources[0].uri)
                print(f"  资源内容: {content}")
            
            print("\n✅ 所有测试完成!")
            
    finally:
        await runner.cleanup()

# 实际可用的 MCP 服务器测试（如果存在）
async def test_real_mcp_server():
    """测试真实的 MCP 服务器（需要替换为实际的服务器地址）"""
    try:
        # 这里可以替换为真实的 MCP 服务器地址
        # 例如: "http://your-mcp-server.com"
        async with MCPClient("http://localhost:8000") as client:
            print("🔗 连接到真实 MCP 服务器...")
            
            # 列出工具
            tools = await client.list_tools()
            print(f"找到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
                
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确保 MCP 服务器正在运行")

if __name__ == "__main__":
    # 运行模拟服务器测试
    print("🧪 开始 MCP 客户端测试...")
    asyncio.run(test_mcp_client())
    
    # 如果需要测试真实服务器，取消下面的注释
    # print("\n🔗 测试真实 MCP 服务器...")
    # asyncio.run(test_real_mcp_server())