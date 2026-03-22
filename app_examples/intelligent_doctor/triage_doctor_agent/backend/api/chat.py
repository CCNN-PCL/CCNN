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

from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncGenerator
import logging
import asyncio
import json
import time

from backend.services.chat_service import ChatService
from backend.services.auth_service import AuthService
from backend.api.oidc_rp import userinfo
from pathlib import Path
from shared.utils.diagnosis_logger import DiagnosisLogger
logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化服务
logger.info("=" * 80)
logger.info("正在初始化聊天服务...")
chat_service = ChatService()
logger.info("聊天服务初始化完成")
logger.info("=" * 80)

auth_service = AuthService()

class ChatRequest(BaseModel):
    """聊天请求模型"""
    user_input: str
    user_id: str
    username: str
    id_token: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """聊天响应模型"""
    agent_name: str
    details: str #过程内容
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
# -----------  复用：OIDC 会话版当前用户  -----------
async def get_current_user(request: Request) -> dict:
    """
    获取当前用户信息
    
    支持两种认证方式：
    1. Session cookie（浏览器登录）
    2. Authorization Bearer token（API调用）
    """
    # 方式1: 从session获取（浏览器登录）
    user_info = request.scope["session"].get("user_info")
    id_token = request.scope["session"].get("id_token")
    global userinfo
    # 方式2: 从Authorization header获取token（API调用）
    if not user_info and not userinfo:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            id_token = auth_header.replace("Bearer ", "").strip()
            try:
                import jwt
                # 解析token获取用户信息（不验证签名，仅用于测试）
                payload = jwt.decode(id_token, options={"verify_signature": False})
                user_info = {
                    "sub": payload.get("sub"),
                    "name": payload.get("name", payload.get("sub")),
                    "email": payload.get("email", "")
                }
                logger.info(f"[get_current_user] 从Authorization header获取token，用户ID: {user_info['sub']}")
            except Exception as e:
                logger.error(f"[get_current_user] 解析token失败: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证令牌",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    
    if not user_info and not userinfo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或会话已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user_info:
        return {
            "userid": user_info["sub"], 
            "username": user_info.get("name", user_info["sub"]),
            "id_token": id_token  # 添加 id_token 到返回的用户信息中
        }
    else:
        return {
            "userid": userinfo["userid"], 
            "username": userinfo["username"],
            # "id_token": userinfo["id_token"] # 添加 id_token 到返回的用户信息中
        }

#===========hzl==================
async def read_and_clear_diagnosis_log():
    log_path = Path(__file__).parent / 'diagnosis.log.md'

    if not log_path.exists():
        return ""

    content = log_path.read_text(encoding='utf-8')
    log_path.write_text('', encoding='utf-8')  # 清空
    return content
#===========hzl==================

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    发送聊天消息
    
    参数:
        request: 聊天请求数据
        current_user: 当前用户信息
        
    返回:
        ChatResponse: 智能体响应
    """
    print("request: ",request)
    # 使用print确保输出到终端
    print("\n" + "=" * 80)
    print("🎯🎯🎯 收到聊天请求！🎯🎯🎯")
    print(f"用户: {current_user.get('username')} (ID: {request.user_id})")
    print(f"消息: {request.user_input[:50]}...")
    print("=" * 80 + "\n")
    
    logger.info("=" * 80)
    logger.info("🎯 收到聊天请求！")
    logger.info(f"用户: {current_user.get('username')} (ID: {request.user_id})")
    logger.info(f"消息: {request.user_input[:50]}...")
    logger.info("=" * 80)
    current_user_info ={
        "userid": request.user_id, 
        "username": request.username,
        "id_token": request.id_token
    }
    
    # 初始化诊断日志记录器
    diagnosis_logger = DiagnosisLogger()
    await diagnosis_logger.clear_log()  # 清空之前的日志
    await diagnosis_logger.start_diagnosis_session(
        user_id=request.user_id,
        user_input=request.user_input,
        user_info=current_user_info
    )
    
    # 验证用户权限
    # print("当前用户信息:", current_user, "系统用户ID:", request.user_id)
    # if current_user.get('userid') != request.user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="无权访问其他用户的聊天"
    #     )
    
    try:
        # 处理聊天消息
        result = await chat_service.handle_chat(
            user_input=request.user_input,
            user_id=request.user_id,
            user_info=current_user_info,
            context=request.context,
            diagnosis_logger=diagnosis_logger  # 传递日志记录器
        )
        
        # 结束诊断会话
        if result:
            await diagnosis_logger.end_diagnosis_session({
                "status": result.get("status", "success"),
                "rounds": result.get("rounds", 0),
                "specialist_count": len(result.get("specialist_results", [])),
                "data_sources": result.get("data_sources", []),
                "duration": result.get("duration", 0),
                "avg_confidence": result.get("avg_confidence", 0.0)
            })
    except Exception as e:
        await diagnosis_logger.log_error(str(e), e)
        raise
    
    diagnosis = await read_and_clear_diagnosis_log()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="聊天处理失败"
        )
    
    # 构建响应
    response = ChatResponse(
        agent_name=result.get('agent_name', 'Unknown'),
        details=diagnosis,      # 添加过程内容
        response=result.get('response', ''),
        metadata=result.get('metadata', {}),
        timestamp=result.get('timestamp', '')
    )
    
    logger.info(f"聊天响应生成成功: {result.get('agent_name')}")
    return response
    
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     logger.error(f"聊天处理失败: {str(e)}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"聊天处理失败: {str(e)}"
    #     )

# 流式聊天功能已禁用
# @router.post("/send/stream")
# async def send_message_stream(
#     request: StreamChatRequest,
#     current_user: dict = Depends(auth_service.get_current_user)
# ):
#     """
#     发送流式聊天消息
#     
#     参数:
#         request: 流式聊天请求数据
#         current_user: 当前用户信息
#         
#     返回:
#         StreamingResponse: 流式响应
#     """
#     try:
#         logger.info(f"用户 {current_user.get('username')} 发送流式消息: {request.user_input[:50]}...")
#         
#         # 验证用户权限
#         if current_user.get('user_id') != request.user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="无权访问其他用户的聊天"
#             )
#         
#         async def generate_stream():
#             """生成流式响应"""
#             try:
#                 # 发送开始信号
#                 yield f"data: {json.dumps({'type': 'start', 'message': '开始处理您的请求...'})}\n\n"
#                 
#                 # 处理聊天消息并流式返回
#                 async for chunk in chat_service.handle_chat_stream(
#                     user_input=request.user_input,
#                     user_id=request.user_id,
#                     user_info=current_user,
#                     context=request.context
#                 ):
#                     yield f"data: {json.dumps(chunk)}\n\n"
#                     await asyncio.sleep(0.01)  # 小延迟确保流式效果
#                 
#                 # 发送结束信号
#                 yield f"data: {json.dumps({'type': 'end', 'message': '处理完成'})}\n\n"
#                 
#             except Exception as e:
#                 logger.error(f"流式处理失败: {str(e)}")
#                 yield f"data: {json.dumps({'type': 'error', 'message': f'处理失败: {str(e)}'})}\n\n"
#         
#         return StreamingResponse(
#             generate_stream(),
#             media_type="text/plain",
#             headers={
#                 "Cache-Control": "no-cache",
#                 "Connection": "keep-alive",
#                 "Content-Type": "text/event-stream"
#             }
#         )
        
    # except HTTPException:
    #     raise
    # except Exception as e:
    #     logger.error(f"流式聊天处理失败: {str(e)}")
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"流式聊天处理失败: {str(e)}"
    #     )

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(auth_service.get_current_user)
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
        if current_user.get('user_id') != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问其他用户的聊天历史"
            )
        
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
    user_id: str,
    current_user: dict = Depends(auth_service.get_current_user)
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
        if current_user.get('user_id') != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权清空其他用户的聊天历史"
            )
        
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
async def get_available_agents(current_user: dict = Depends(auth_service.get_current_user)):
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
    agent_id: str,
    current_user: dict = Depends(auth_service.get_current_user)
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
