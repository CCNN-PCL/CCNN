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
用户管理相关API
===============

提供用户信息、偏好设置等管理API接口

作者: QSIR
版本: 1.0
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from backend.services.user_service import UserService
from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化服务
user_service = UserService()
auth_service = AuthService()

class UserProfileUpdate(BaseModel):
    """用户资料更新模型"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[list] = None
    medications: Optional[list] = None

class UserPreferencesUpdate(BaseModel):
    """用户偏好设置更新模型"""
    language: Optional[str] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    notifications: Optional[Dict[str, bool]] = None
    privacy_settings: Optional[Dict[str, bool]] = None
    display_settings: Optional[Dict[str, str]] = None

class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str
    new_password: str

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(auth_service.get_current_user)):
    """
    获取用户资料
    
    参数:
        current_user: 当前用户信息
        
    返回:
        dict: 用户资料信息
    """
    try:
        user_id = current_user.get('user_id')
        
        # 获取用户资料
        profile = await user_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户资料不存在"
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )

@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    更新用户资料
    
    参数:
        profile_data: 资料更新数据
        current_user: 当前用户信息
        
    返回:
        dict: 更新结果
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"用户 {current_user.get('username')} 更新资料")
        
        # 更新用户资料
        success, message = await user_service.update_user_profile(
            user_id=user_id,
            profile_data=profile_data.dict(exclude_unset=True)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "message": "用户资料更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )

@router.get("/preferences")
async def get_user_preferences(current_user: dict = Depends(auth_service.get_current_user)):
    """
    获取用户偏好设置
    
    参数:
        current_user: 当前用户信息
        
    返回:
        dict: 用户偏好设置
    """
    try:
        user_id = current_user.get('user_id')
        
        # 获取用户偏好设置
        preferences = await user_service.get_user_preferences(user_id)
        
        if not preferences:
            # 返回默认设置
            return {
                "language": "zh-CN",
                "theme": "light",
                "timezone": "Asia/Shanghai",
                "notifications": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "sms_notifications": False
                },
                "privacy_settings": {
                    "profile_public": False,
                    "data_sharing": False,
                    "analytics_tracking": True,
                    "marketing_emails": False
                },
                "display_settings": {
                    "font_size": "medium",
                    "color_scheme": "default",
                    "layout": "standard"
                }
            }
        
        return preferences
        
    except Exception as e:
        logger.error(f"获取用户偏好设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户偏好设置失败: {str(e)}"
        )

@router.put("/preferences")
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    更新用户偏好设置
    
    参数:
        preferences_data: 偏好设置更新数据
        current_user: 当前用户信息
        
    返回:
        dict: 更新结果
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"用户 {current_user.get('username')} 更新偏好设置")
        
        # 更新用户偏好设置
        success, message = await user_service.update_user_preferences(
            user_id=user_id,
            preferences_data=preferences_data.dict(exclude_unset=True)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "message": "用户偏好设置更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户偏好设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户偏好设置失败: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    修改用户密码
    
    参数:
        password_data: 密码修改数据
        current_user: 当前用户信息
        
    返回:
        dict: 修改结果
    """
    try:
        user_id = current_user.get('user_id')
        logger.info(f"用户 {current_user.get('username')} 修改密码")
        
        # 验证旧密码
        if not auth_service.verify_password(password_data.old_password, current_user.get('password_hash')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        
        # 修改密码
        success, message = await user_service.change_password(
            user_id=user_id,
            new_password=password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return {
            "message": "密码修改成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )

@router.get("/stats")
async def get_user_stats(current_user: dict = Depends(auth_service.get_current_user)):
    """
    获取用户使用统计
    
    参数:
        current_user: 当前用户信息
        
    返回:
        dict: 用户统计信息
    """
    try:
        user_id = current_user.get('user_id')
        
        # 获取用户统计信息
        stats = await user_service.get_user_stats(user_id)
        
        return stats
        
    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户统计失败: {str(e)}"
        )

@router.get("/activities")
async def get_user_activities(
    limit: int = 20,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    获取用户活动记录
    
    参数:
        limit: 返回记录数量限制
        current_user: 当前用户信息
        
    返回:
        dict: 用户活动记录
    """
    try:
        user_id = current_user.get('user_id')
        
        # 获取用户活动记录
        activities = await user_service.get_user_activities(user_id, limit)
        
        return {
            "activities": activities,
            "total_count": len(activities)
        }
        
    except Exception as e:
        logger.error(f"获取用户活动记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户活动记录失败: {str(e)}"
        )
