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
用户数据模型
============

定义用户相关的Pydantic模型

作者: QSIR
版本: 1.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """用户基础模型"""

    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """用户创建模型"""

    password: str
    role: str = "patient"


class UserLogin(BaseModel):
    """用户登录模型"""

    username: str
    password: str


class UserResponse(UserBase):
    """用户响应模型"""

    user_id: str
    role: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户资料模型"""

    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    emergency_contact: Optional[str] = None
    allergies: Optional[List[str]] = []
    medications: Optional[List[str]] = []


class UserPreferences(BaseModel):
    """用户偏好设置模型"""

    language: str = "zh-CN"
    theme: str = "light"
    timezone: str = "Asia/Shanghai"
    notifications: Dict[str, bool] = {
        "email_notifications": True,
        "push_notifications": True,
        "sms_notifications": False,
    }
    privacy_settings: Dict[str, bool] = {
        "profile_public": False,
        "data_sharing": False,
        "analytics_tracking": True,
        "marketing_emails": False,
    }
    display_settings: Dict[str, str] = {
        "font_size": "medium",
        "color_scheme": "default",
        "layout": "standard",
    }


class UserStats(BaseModel):
    """用户统计模型"""

    total_chat_messages: int = 0
    total_medical_images: int = 0
    total_medical_records: int = 0
    last_login: Optional[datetime] = None
    account_created: Optional[datetime] = None


class UserActivity(BaseModel):
    """用户活动模型"""

    activity_type: str
    description: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = {}
