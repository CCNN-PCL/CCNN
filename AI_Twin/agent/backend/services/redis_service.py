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
聊天服务层
使用 Redis 工具类进行数据存储
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# 导入 Redis 工具类
from backend.utils.redis import get_redis_client

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client = get_redis_client()
        self.chat_history_key = "chat_history"
        self.user_sessions_key = "user_sessions"
    
    def save_chat_message(self, user_id: str, content: str, 
                         metadata: Optional[Dict] = None) -> bool:
        """
        保存聊天消息到 Redis
        
        Args:
            user_id: 用户ID
            content: 消息内容
            metadata: 元数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            message_data = {
                "user_id": user_id,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            # 使用用户ID作为键的一部分
            user_chat_key = f"{self.chat_history_key}:{user_id}"
            
            # 添加到列表尾部
            self.redis_client.list_append(user_chat_key, message_data)
            
            # 限制聊天记录长度（保留最近100条）
            current_length = self.redis_client.list_length(user_chat_key)
            if current_length > 100:
                self.redis_client.list_trim(user_chat_key, -100, -1)
            
            logger.debug(f"保存聊天消息: {user_id} ")
            return True
            
        except Exception as e:
            logger.error(f"保存聊天消息失败: {e}")
            return False
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取用户聊天历史
        
        Args:
            user_id: 用户ID
            limit: 返回的消息数量限制
            
        Returns:
            List[Dict]: 聊天历史记录
        """
        try:
            user_chat_key = f"{self.chat_history_key}:{user_id}"
            
            # 获取最近的聊天记录
            messages = self.redis_client.list_get_range(
                user_chat_key, 
                start=-limit, 
                end=-1
            )
            
            logger.debug(f"获取用户 {user_id} 的聊天历史，共 {len(messages)} 条消息")
            return messages
            
        except Exception as e:
            logger.error(f"获取聊天历史失败: {e}")
            return []
    
    def clear_chat_history(self, user_id: str) -> bool:
        """
        清空用户聊天历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否清空成功
        """
        try:
            user_chat_key = f"{self.chat_history_key}:{user_id}"
            result = self.redis_client.delete(user_chat_key)
            
            logger.debug(f"清空用户 {user_id} 的聊天历史")
            return result > 0
            
        except Exception as e:
            logger.error(f"清空聊天历史失败: {e}")
            return False
    
    def save_user_session(self, user_id: str, session_data: Dict[str, Any], 
                         expire_seconds: int = 3600) -> bool:
        """
        保存用户会话数据
        
        Args:
            user_id: 用户ID
            session_data: 会话数据
            expire_seconds: 过期时间（秒）
            
        Returns:
            bool: 是否保存成功
        """
        try:
            session_key = f"{self.user_sessions_key}:{user_id}"
            
            # 设置会话数据并添加过期时间
            success = self.redis_client.set_value(
                session_key, 
                session_data, 
                expire=expire_seconds
            )
            
            logger.debug(f"保存用户会话: {user_id}, 过期时间: {expire_seconds}秒")
            return success
            
        except Exception as e:
            logger.error(f"保存用户会话失败: {e}")
            return False
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户会话数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 会话数据，如果不存在返回 None
        """
        try:
            session_key = f"{self.user_sessions_key}:{user_id}"
            session_data = self.redis_client.get_value(session_key)
            
            logger.debug(f"获取用户会话: {user_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return None

# 创建全局实例
redis_service = RedisService()