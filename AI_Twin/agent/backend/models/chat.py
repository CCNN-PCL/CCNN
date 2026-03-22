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
聊天数据模型
============

定义聊天相关的Pydantic模型

作者: AI开发团队
版本: 1.0
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str
    content: str
    timestamp: datetime

class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_input: str
    user_id: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    agent_name: str
    response: str
    metadata: Dict[str, Any]
    timestamp: str

class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    messages: List[ChatMessage]
    total_count: int
    page: int
    page_size: int
