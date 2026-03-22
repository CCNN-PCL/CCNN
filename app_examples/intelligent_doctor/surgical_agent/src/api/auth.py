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
认证相关API
===========

提供用户登录、注册、权限验证等API接口

作者: QSIR
版本: 1.0
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.models.user import UserResponse
from src.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化认证服务
auth_service = AuthService()


class LoginRequest(BaseModel):
    """登录请求模型"""

    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""

    access_token: str
    refresh_token: str
    user: UserResponse
    message: str


class RegisterRequest(BaseModel):
    """注册请求模型"""

    username: str
    password: str
    confirm_password: str
    email: Optional[str] = None
    role: str = "patient"


class RegisterResponse(BaseModel):
    """注册响应模型"""

    user: UserResponse
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录

    参数:
        request: 登录请求数据

    返回:
        LoginResponse: 包含访问令牌和用户信息
    """
    try:
        logger.info(f"用户登录请求: {request.username}")

        # 验证用户凭据
        success, message, user, token = auth_service.authenticate_user(
            request.username, request.password
        )

        if not success or not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=message
            )

        # 生成访问令牌
        access_token = auth_service.create_access_token(user.user_id)
        refresh_token = auth_service.create_refresh_token(user.user_id)

        logger.info(f"用户 {request.username} 登录成功")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=getattr(user, "email", None),
                role=user.role.value,
                status=user.status.value,
                created_at=getattr(user, "created_at", None),
            ),
            message="登录成功",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}",
        )


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    用户注册

    参数:
        request: 注册请求数据

    返回:
        RegisterResponse: 注册结果和用户信息
    """
    try:
        logger.info(f"用户注册请求: {request.username}")

        # 验证输入数据
        if not request.username or not request.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名和密码不能为空"
            )

        # 验证密码确认
        if request.password != request.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="密码和确认密码不一致"
            )

        # 检查用户名是否已存在
        if auth_service.get_user_by_username(request.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
            )

        # 创建用户
        success, message, user = auth_service.register_user(
            request.username, request.password, request.email, request.role
        )

        if not success or not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

        logger.info(f"用户 {request.username} 注册成功")

        return RegisterResponse(
            user=UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=getattr(user, "email", None),
                role=user.role.value,
                status=user.status.value,
                created_at=getattr(user, "created_at", None),
            ),
            message="注册成功",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}",
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    刷新访问令牌

    参数:
        refresh_token: 刷新令牌

    返回:
        dict: 新的访问令牌
    """
    try:
        # 验证刷新令牌
        user_id = auth_service.verify_refresh_token(refresh_token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
            )

        # 生成新的访问令牌
        new_access_token = auth_service.create_access_token(user_id)

        return {"access_token": new_access_token, "message": "令牌刷新成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}",
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(auth_service.get_current_user)):
    """
    用户登出

    参数:
        current_user: 当前用户信息

    返回:
        dict: 登出结果
    """
    try:
        # 这里可以实现令牌黑名单等登出逻辑
        logger.info(f"用户 {current_user.get('username')} 登出")

        return {"message": "登出成功"}

    except Exception as e:
        logger.error(f"登出失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(auth_service.get_current_user),
):
    """
    获取当前用户信息

    参数:
        current_user: 当前用户信息

    返回:
        UserResponse: 用户信息
    """
    try:
        return UserResponse(
            user_id=current_user.get("user_id"),
            username=current_user.get("username"),
            email=current_user.get("email"),
            role=current_user.get("role"),
            status=current_user.get("status"),
            created_at=current_user.get("created_at"),
        )

    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}",
        )
