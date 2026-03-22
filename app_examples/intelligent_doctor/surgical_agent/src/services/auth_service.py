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

作者: QSIR
版本: 1.0
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.shared.auth_manager import UserRole, auth_manager

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    def __init__(self):
        """初始化认证服务"""
        self.secret_key = "cybertwin-secret-key"  # 生产环境应该从环境变量获取
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def authenticate_user(
        self, username: str, password: str
    ) -> Tuple[bool, str, Optional[Any], Optional[str]]:
        """
        用户认证

        参数:
            username: 用户名
            password: 密码

        返回:
            Tuple[bool, str, Optional[Any], Optional[str]]: (成功标志, 消息, 用户对象, 令牌)
        """
        try:
            logger.info(f"API认证服务开始认证用户: {username}")
            result = auth_manager.authenticate_user(username, password)
            logger.info(f"API认证服务认证结果: {result[0]}, {result[1]}")
            return result
        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            return False, f"认证失败: {str(e)}", None, None

    def register_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        role: str = "patient",
    ) -> Tuple[bool, str, Optional[Any]]:
        """
        用户注册

        参数:
            username: 用户名
            password: 密码
            email: 邮箱
            role: 用户角色

        返回:
            Tuple[bool, str, Optional[Any]]: (成功标志, 消息, 用户对象)
        """
        try:
            # 转换角色字符串为枚举
            try:
                user_role = UserRole(role)
            except ValueError:
                return False, f"无效的用户角色: {role}", None

            return auth_manager.register_user(username, password, email, user_role)
        except Exception as e:
            logger.error(f"用户注册失败: {str(e)}")
            return False, f"注册失败: {str(e)}", None

    def create_access_token(self, user_id: str) -> str:
        """
        创建访问令牌

        参数:
            user_id: 用户ID

        返回:
            str: 访问令牌
        """
        try:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
            payload = {"user_id": user_id, "exp": expire, "type": "access"}
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"创建访问令牌失败: {str(e)}")
            raise

    def create_refresh_token(self, user_id: str) -> str:
        """
        创建刷新令牌

        参数:
            user_id: 用户ID

        返回:
            str: 刷新令牌
        """
        try:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
            payload = {"user_id": user_id, "exp": expire, "type": "refresh"}
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"创建刷新令牌失败: {str(e)}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌

        参数:
            token: 令牌

        返回:
            Optional[Dict[str, Any]]: 用户信息，验证失败返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 检查令牌类型
            if payload.get("type") != "access":
                return None

            user_id = payload.get("user_id")
            if not user_id:
                return None

            # 获取用户信息
            user = auth_manager.get_user_by_id(user_id)
            if not user:
                return None

            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": getattr(user, "email", None),
                "role": user.role.value,
                "status": user.status.value,
                "created_at": getattr(user, "created_at", None),
            }
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的令牌")
            return None
        except Exception as e:
            logger.error(f"令牌验证失败: {str(e)}")
            return None

    def verify_refresh_token(self, token: str) -> Optional[str]:
        """
        验证刷新令牌

        参数:
            token: 刷新令牌

        返回:
            Optional[str]: 用户ID，验证失败返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 检查令牌类型
            if payload.get("type") != "refresh":
                return None

            user_id = payload.get("user_id")
            if not user_id:
                return None

            # 验证用户是否存在
            user = auth_manager.get_user_by_id(user_id)
            if not user:
                return None

            return user_id
        except jwt.ExpiredSignatureError:
            logger.warning("刷新令牌已过期")
            return None
        except jwt.InvalidTokenError:
            logger.warning("无效的刷新令牌")
            return None
        except Exception as e:
            logger.error(f"刷新令牌验证失败: {str(e)}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Any]:
        """
        根据用户名获取用户

        参数:
            username: 用户名

        返回:
            Optional[Any]: 用户对象
        """
        try:
            return auth_manager.get_user_by_username(username)
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Any]:
        """
        根据用户ID获取用户

        参数:
            user_id: 用户ID

        返回:
            Optional[Any]: 用户对象
        """
        try:
            return auth_manager.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            return None

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        验证密码

        参数:
            password: 明文密码
            hashed_password: 哈希密码

        返回:
            bool: 验证结果
        """
        try:
            from shared.auth_manager import PasswordManager

            return PasswordManager.verify_password(password, hashed_password)
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False

    def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> Dict[str, Any]:
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
