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

import redis
import json
import sys
import os
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.redis_service import RedisService
from backend.utils.websocket_manager import connection_manager

redis_service = RedisService()
user_id = "111"
redis_service.save_chat_message(user_id,"test1")
redis_service.save_chat_message(user_id,"Hello World!")
redis_service.save_chat_message(user_id,"test2")

async def websocket_send_history(user_id: str):
    try:
        history = redis_service.get_chat_history(user_id)
        if history:
            respond = '\n'.join(item['content'] for item in history)
            print("🎯🎯🎯 收到history消息！🎯🎯🎯")
            print(respond)
            print("🎯🎯🎯 收到history消息！🎯🎯🎯")            
            history_response = {
                "event": "server_response",
                "data": {
                    "status": "ok",
                    "response": respond,
                    "timestamp": datetime.now().isoformat()
                    }
            }
                        
            await connection_manager.send_message(history_response)
                        
            print("📤 发送第history响应（ok状态）")
            redis_service.clear_chat_history(user_id)    
    
    except WebSocketDisconnect:
        print("🔌 WebSocket连接断开")
    except Exception as e:
        print(f"❌ WebSocket聊天处理失败: {str(e)}")

# if __name__ == "__main__":
    # asyncio.run(websocket_send_history(user_id))

# # 连接到 Redis 数据库
# r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# try:
#     # 测试连接
#     print("🔗 连接Redis服务器...")
#     print(f"PING: {r.ping()}")
    
#     # 使用列表操作在队尾添加元素
#     print("\n📝 向队列添加元素...")
#     r.rpush("chat_history", "Hello world")
#     r.rpush("chat_history", "H1")
#     r.rpush("chat_history", "H2")
#     print("✅ 元素添加完成")
    
#     # 获取队列所有元素
#     print("\n📖 读取队列所有元素...")
#     all_values = r.lrange("chat_history", 0, -1)
#     print("队列中的所有元素:")
#     for i, value in enumerate(all_values, 1):
#         print(f"  {i}. {value}")
    
#     # 获取队列长度
#     queue_length = r.llen("chat_history")
#     print(f"队列长度: {queue_length}")
    
#     # 清空队列
#     print("\n🗑️  清空队列...")
#     r.delete("chat_history")
#     print("✅ 队列已清空")
    
#     # 验证队列是否为空
#     remaining = r.lrange("chat_history", 0, -1)
#     print(f"清空后队列内容: {remaining}")
#     print(f"清空后队列长度: {r.llen('chat_history')}")
    
# except redis.ConnectionError:
#     print("❌ 无法连接到Redis服务器，请检查Redis是否运行在localhost:6379")
# except Exception as e:
#     print(f"❌ 发生错误: {e}")