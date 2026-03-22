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

from typing import Optional, Dict
from mcp.shared.auth import Auth                      # 基础抽象
import aiohttp

class BearerTokenAuth(Auth):
    """极简 Bearer Token 鉴权，兼容 MCP SDK 的 Auth 协议"""
    def __init__(self, token: str):
        self.token = token

    async def get_access_token(self) -> Optional[str]:
        return self.token

    async def auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}