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
import os
from mcp_client import AuthenticatedMCPClient
from typing import Dict, Any, List, Optional, AsyncGenerator
from mcp_client_new import Server
import json


async def _main():
    """Main entry point."""
    # Default server URL - can be overridden with environment variable
    # Most MCP streamable HTTP servers use /mcp as the endpoint
    server_url = os.getenv("MCP_SERVER_PORT", 8000)
    transport_type = os.getenv("MCP_TRANSPORT_TYPE", "streamable-http")
    server_url = (
        f"http://192.168.193.12:31445/mcp"
        if transport_type == "streamable-http"
        else f"http://192.168.193.12:31445/sse"
    )



    print("🚀 Simple MCP Auth Client")
    print(f"Connecting to: {server_url}")
    print(f"Transport type: {transport_type}")

    server = Server(name="test", token="test", server_url=server_url, config=None, transport_type="streamable-http")
    await server.initialize()
    print("init sucess ===============")
    tools = await server.list_tools()

    for v in tools:
        print(f"===== get tools {v.format_for_llm()} === \n")
    
    result = await server.execute_tool("query_hospital_medical_data", {
        "department": "内分泌科",
        "user_id": "70133600"
    })
    print(f"{result}\n")
    print("*********************************************************")
    if hasattr(result, 'model_dump'):
        result_dict = result.model_dump()
        structured_content = result_dict.get('structuredContent')
        print(structured_content)
        structured_content_str = json.dumps(structured_content, ensure_ascii=False, indent=2)
        print(structured_content_str)
        print(type(structured_content_str))
        print(structured_content["datas"][0]["data_types"])
    print("*********************************************************")
    await server.cleanup()


def _cli():
    """CLI entry point for uv script."""
    asyncio.run(_main())


if __name__ == "__main__":
    _cli()