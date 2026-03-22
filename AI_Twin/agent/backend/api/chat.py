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
聊天相关API
===========

提供智能体对话、聊天历史等API接口

作者: AI开发团队
版本: 1.0
"""

from fastapi import APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncGenerator
import logging
import asyncio
import json
import time
from datetime import datetime
import asyncio

from backend.services.chat_service import ChatService
from backend.services.redis_service import RedisService
from backend.utils.websocket_manager import connection_manager
#from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()
# 全局变量用于存储监听任务
user_listeners = {}

# 初始化服务
logger.info("=" * 80)
logger.info("正在初始化聊天服务...")
chat_service = ChatService()
redis_service = RedisService()
logger.info("聊天服务初始化完成")
logger.info("=" * 80)

#auth_service = AuthService()

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
    messages: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int

class StreamChatRequest(BaseModel):
    """流式聊天请求模型"""
    user_input: str
    user_id: str
    context: Optional[Dict[str, Any]] = None
    stream: bool = True

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest
):
    """
    发送聊天消息
    
    参数:
        request: 聊天请求数据
        current_user: 当前用户信息
        
    返回:
        ChatResponse: 智能体响应
    """
    try:
        # 使用print确保输出到终端
        print("\n" + "=" * 80)
        print("🎯🎯🎯 收到聊天请求！🎯🎯🎯")
        # print(f"用户: {current_user.get('username')} (ID: {request.user_id})")
        print(f"消息: {request.user_input[:50]}...")
        print("=" * 80 + "\n")
        
        logger.info("=" * 80)
        logger.info("🎯 收到聊天请求！")
        # logger.info(f"用户: {current_user.get('username')} (ID: {request.user_id})")
        logger.info(f"消息: {request.user_input[:50]}...")
        logger.info("=" * 80)
        
        # 验证用户权限
        # if current_user.get('user_id') != request.user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="无权访问其他用户的聊天"
        #     )
        
        # 处理聊天消息
        result = None
        BOOLEAN = True
        if(BOOLEAN):
            result = {
                'agent_name':'quwen',
                'response':'您好，识别到您在咨询健康问题，为您跳转到私人医生智能体',
                'metadata': {"redirect": 1},
                'timestamp' : datetime.now().isoformat()
            }
        else:    
            result = await chat_service.handle_chat(
                user_input=request.user_input,
                user_id=request.user_id,
                user_info=request.user_input,
                context=request.context
            )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="聊天处理失败"
            )
        
        # 构建响应
        response = ChatResponse(
            agent_name=result.get('agent_name', 'Unknown'),
            response=result.get('response', ''),
            metadata=result.get('metadata', {}),
            timestamp=result.get('timestamp', '')
        )

        # 使用print确保输出到终端
        print("\n" + "=" * 80)
        print("🎯🎯🎯 聊天响应！🎯🎯🎯")
        print(f"消息: {response}...")
        print("=" * 80 + "\n")
        
        logger.info(f"聊天响应生成成功: {result.get('agent_name')}")

        return JSONResponse(content=response.model_dump())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"聊天处理失败: {str(e)}"
        )
      
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式聊天处理失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"流式聊天处理失败: {str(e)}"
        )

@router.websocket("/ws/send")
async def websocket_send_message(websocket: WebSocket):
    """
    WebSocket聊天消息接口
    """
    # await websocket.accept()
    await connection_manager.connect(websocket)
    user_id = None
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 使用print确保输出到终端
            print("\n" + "=" * 80)
            print("🎯🎯🎯 收到WebSocket聊天请求！🎯🎯🎯")
            print(f"消息: {message_data.get('user_input', '')[:50]}...")
            print("=" * 80 + "\n")
            
            logger.info("=" * 80)
            logger.info("🎯 收到WebSocket聊天请求！")
            logger.info(f"消息: {message_data.get('user_input', '')[:50]}...")
            logger.info("=" * 80)

            # 获取用户ID并启动监听器
            user_id = message_data.get('user_id', '')
            logger.info(f"消息: {message_data.get('user_id', '')[:50]}...")
            if user_id and user_id not in user_listeners:
                await start_history_listener(user_id, websocket)
                     
            # 处理聊天消息
            result = None
            isHealth = True
            
            answer = await chat_service.judge_chat(
                user_input=message_data.get('user_input', ''),
                user_id=message_data.get('user_id', ''),
                user_info=message_data.get('user_info', {}),
                context=message_data.get('context', {})
            )
            if(answer.get('response', '') == 'False'):
                isHealth = False

            if isHealth:
                result = {
                    "status": "ok",
                    'agent_name': 'quwen',
                    'response': '您好，识别到您在咨询健康问题，为您跳转到私人医生智能体',
                    'metadata': {"redirect": 1},
                    'timestamp': datetime.now().isoformat()
                }
            else:    
                result = await chat_service.handle_chat(
                    user_input=message_data.get('user_input', ''),
                    user_id=message_data.get('user_id', ''),
                    user_info=message_data.get('user_info', {}),
                    context=message_data.get('context', {})
                )

                print("🎯🎯🎯 收到result消息！🎯🎯🎯")
                print(result)
                print("🎯🎯🎯 收到result消息！🎯🎯🎯")

            
            if not result:
                # 发送错误响应
                error_response = {
                    "event": "server_response",
                    "data": {
                        "status": "error",
                        "message": "聊天处理失败",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await websocket.send_text(json.dumps(error_response, ensure_ascii=False))
                continue
            
            # 对话响应：发送正常的聊天响应
            chat_response = {
                "event": "server_response",
                "data": {
                    "status": result.get('status', 'ok'),
                    "agent_name": result.get('agent_name', ''),
                    "response": result.get('response', ''),
                    "metadata": result.get('metadata', {}),
                    "timestamp": result.get('timestamp', datetime.now().isoformat())
                }
            }
            
            await websocket.send_text(json.dumps(chat_response, ensure_ascii=False))
            
            print("📤 发送第对话响应（聊天内容）")
            logger.info(f"聊天响应生成成功: {result.get('agent_name')}")
            
            # 使用print确保输出到终端
            print("\n" + "=" * 80)
            print("🎯🎯🎯 WebSocket聊天响应完成！🎯🎯🎯")
            print(f"响应: {chat_response}")
            print("=" * 80 + "\n")
          
    except WebSocketDisconnect:
        print("🔌 WebSocket连接断开")
        logger.info("WebSocket连接断开")
    except Exception as e:
        print(f"❌ WebSocket聊天处理失败: {str(e)}")
        logger.error(f"WebSocket聊天处理失败: {str(e)}")
        
        # 发送错误响应
        try:
            error_response = {
                "status": "error",
                "message": f"聊天处理失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_text(json.dumps(error_response, ensure_ascii=False))
        except:
            pass  # 如果发送错误也失败，忽略

async def start_history_listener(user_id: str, websocket: WebSocket):
    """启动历史记录监听器"""
    print(user_listeners)
    if user_id in user_listeners:
        return  # 已经有一个监听器在运行
    
    async def listen_for_history():
        """监听历史记录变化并发送给客户端"""
        try:
            while True:
                # 检查WebSocket是否还连接
                if connection_manager.active_connections != websocket:
                    break
                    
                # 检查redis中的历史记录
                history = redis_service.get_chat_history(user_id)
                if history:
                    respond = '\n'.join(item['content'] for item in history)
                    print("🎯🎯🎯 检测到history消息！🎯🎯🎯")
                    print(respond)
                    print("🎯🎯🎯 检测到history消息！🎯🎯🎯")            
                    
                    history_response = {
                        "event": "server_response",
                        "data": {
                            "status": "ok",
                            "response": respond,
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    # 使用connection_manager发送历史响应
                    await connection_manager.send_message(history_response)
                    
                    print("📤 主动发送history响应")
                    logger.info("主动发送history响应")
                    
                    # 清空历史记录
                    redis_service.clear_chat_history(user_id)
                
                # 每秒检查一次
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ 历史记录监听器错误: {str(e)}")
        finally:
            # 清理监听器
            if user_id in user_listeners:
                del user_listeners[user_id]

    # 启动监听任务
    task = asyncio.create_task(listen_for_history())
    user_listeners[user_id] = task

async def stop_history_listener(user_id: str):
    """停止历史记录监听器"""
    if user_id in user_listeners:
        user_listeners[user_id].cancel()
        try:
            await user_listeners[user_id]
        except asyncio.CancelledError:
            pass
        del user_listeners[user_id]

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
            logger.info("发送history响应（ok状态）")
            redis_service.clear_chat_history(user_id)        
    
    except WebSocketDisconnect:
        print("🔌 WebSocket连接断开")
        logger.info("WebSocket连接断开")
    except Exception as e:
        print(f"❌ WebSocket聊天处理失败: {str(e)}")
        logger.error(f"WebSocket聊天处理失败: {str(e)}")

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    page: int = 1,
    page_size: int = 50
):
    """
    获取聊天历史
    
    参数:
        user_id: 用户ID
        page: 页码
        page_size: 每页大小
        current_user: 当前用户信息
        
    返回:
        ChatHistoryResponse: 聊天历史记录
    """
    try:
        # 验证用户权限
        # if current_user.get('user_id') != user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="无权访问其他用户的聊天历史"
        #     )
        
        # 获取聊天历史
        history = await chat_service.get_chat_history(
            user_id=user_id,
            page=page,
            page_size=page_size
        )
        
        return ChatHistoryResponse(
            messages=history.get('messages', []),
            total_count=history.get('total_count', 0),
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取聊天历史失败: {str(e)}"
        )

@router.delete("/history")
async def clear_chat_history(
    user_id: str
):
    """
    清空聊天历史
    
    参数:
        user_id: 用户ID
        current_user: 当前用户信息
        
    返回:
        dict: 清空结果
    """
    try:
        # 验证用户权限
        # if current_user.get('user_id') != user_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="无权清空其他用户的聊天历史"
        #     )
        
        # 清空聊天历史
        success = await chat_service.clear_chat_history(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="清空聊天历史失败"
            )
        
        return {
            "message": "聊天历史已清空"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清空聊天历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空聊天历史失败: {str(e)}"
        )

@router.get("/agents")
async def get_available_agents(current_user: dict):
    """
    获取可用的智能体列表
    
    参数:
        current_user: 当前用户信息
        
    返回:
        dict: 智能体列表
    """
    try:
        # 获取用户角色
        user_role = current_user.get('role', 'patient')
        
        # 获取可用智能体
        agents = await chat_service.get_available_agents(user_role)
        
        return {
            "agents": agents,
            "user_role": user_role
        }
        
    except Exception as e:
        logger.error(f"获取智能体列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取智能体列表失败: {str(e)}"
        )

@router.get("/agents/{agent_id}/status")
async def get_agent_status(
    agent_id: str
):
    """
    获取指定智能体状态
    
    参数:
        agent_id: 智能体ID
        current_user: 当前用户信息
        
    返回:
        dict: 智能体状态信息
    """
    try:
        # 获取智能体状态
        status_info = await chat_service.get_agent_status(agent_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="智能体不存在"
            )
        
        return status_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取智能体状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取智能体状态失败: {str(e)}"
        )
