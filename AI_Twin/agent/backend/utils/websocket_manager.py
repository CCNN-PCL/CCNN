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
WebSocket 连接管理器
用于管理 WebSocket 连接和主动推送消息
"""

from fastapi import WebSocket
from typing import Dict, List, Set, Optional
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    _instance = None
    _initialized = False  # 添加初始化标志

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 确保只初始化一次
        if not ConnectionManager._initialized:
            # 存储活跃连接: {WebSocket}
            self.active_connections: Optional[WebSocket] = None
            ConnectionManager._initialized = True  
    
    async def connect(self, websocket: WebSocket):
        """接受 WebSocket 连接并存储"""
        await websocket.accept()
        self.active_connections= websocket
        logger.info(f"✅ WebSocket 连接建立")
        print(f"✅ ConnectionManager连接建立，active_connections: {self.active_connections is not None}")
    
    def disconnect(self, websocket: WebSocket) -> bool:
        """断开 WebSocket 连接"""
        if self.active_connections == websocket:
            self.active_connections = None  # 设置为 None 而不是删除属性
            logger.info("🔌 WebSocket 连接断开")
        else:
            logger.warning("⚠️ 尝试断开不匹配的连接")
    
    async def send_message(self, message: Dict):
        """向连接的用户发送消息"""
        # 检查是否有活跃连接
        if self.active_connections is None:
            logger.warning("⚠️ 没有活跃连接，无法发送消息")
            print("🔌 没有活跃连接，无法发送消息")
            return False

        websocket = self.active_connections
        try:          
            await websocket.send_text(json.dumps(message, ensure_ascii=False))
            logger.debug(f"📤 向用户发送消息: {message.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"❌ 向用户发送消息失败: {e}")
            # 连接可能已断开，清理
            self.disconnect(websocket)
            return False

# 创建全局连接管理器实例
connection_manager = ConnectionManager()