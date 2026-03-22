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
认证服务
========

提供用户认证、权限验证等服务

作者: AI开发团队
版本: 1.0
"""

import logging
import sys
import os
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

#from shared.auth_manager import auth_manager, UserRole, UserStatus
#from backend.utils.database import get_database

logger = logging.getLogger(__name__)

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self.secret_key = "cybertwin-secret-key"  # 生产环境应该从环境变量获取
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def jwt_generate(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
        """
        同步发送 POST 请求传递 JSON 数据
        
        Args:
            url: 请求的 URL
            json_data: 要发送的 JSON 数据
            headers: 请求头，默认为 {'Content-Type': 'application/json'}
            timeout: 请求超时时间（秒）
        
        Returns:
            Dict: 响应数据，如果失败返回错误信息
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        # 设置默认请求头
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            newURL = url + '/jwt/generate'
            response = requests.post(
                url=newURL,
                json=json_data,
                headers=headers,
                timeout=timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 尝试解析 JSON 响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"text": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            error_info = {
                "error": str(e),
                "type": type(e).__name__,
                "url": url
            }
            if hasattr(e, 'response') and e.response is not None:
                error_info["status_code"] = e.response.status_code
                error_info["response_text"] = e.response.text
            raise Exception(f"请求失败: {error_info}")

    def jwt_verify(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
        """
        同步发送 POST 请求传递 JSON 数据
        
        Args:
            url: 请求的 URL
            json_data: 要发送的 JSON 数据
            headers: 请求头，默认为 {'Content-Type': 'application/json'}
            timeout: 请求超时时间（秒）
        
        Returns:
            Dict: 响应数据，如果失败返回错误信息
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        # 设置默认请求头
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            print("url:",url)
            newURL = url + '/jwt/verify'
            response = requests.post(
                url=newURL,
                json=json_data,
                headers=headers,
                timeout=timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 尝试解析 JSON 响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"text": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            error_info = {
                "error": str(e),
                "type": type(e).__name__,
                "url": url
            }
            if hasattr(e, 'response') and e.response is not None:
                error_info["status_code"] = e.response.status_code
                error_info["response_text"] = e.response.text
            raise Exception(f"请求失败: {error_info}")

    def rbac_verify(self, url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
        # 设置默认请求头
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        try:
            newURL = url + '/auth/app-role'
            response = requests.post(
                url=newURL,
                json=json_data,
                headers=headers,
                timeout=timeout
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 尝试解析 JSON 响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"text": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            error_info = {
                "error": str(e),
                "type": type(e).__name__,
                "url": url
            }
            if hasattr(e, 'response') and e.response is not None:
                error_info["status_code"] = e.response.status_code
                error_info["response_text"] = e.response.text
            raise Exception(f"请求失败: {error_info}")


    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        """
        获取当前用户信息（用于依赖注入）
        
        参数:
            credentials: 认证凭据
            
        返回:
            Dict[str, Any]: 用户信息
        """
        try:
            token = credentials.credentials
            user_info = self.verify_token(token)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的认证令牌",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user_info
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取当前用户失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="认证失败",
                headers={"WWW-Authenticate": "Bearer"},
            )
