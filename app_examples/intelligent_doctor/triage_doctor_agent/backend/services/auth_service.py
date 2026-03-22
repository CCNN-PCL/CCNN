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
import sys
import os
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 初始化logger（必须在导入前定义，以便在异常处理中使用）
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
# 在Docker容器中，工作目录是/app，项目根目录也是/app
# 方法1: 从当前文件路径计算（适用于Docker容器）
current_file = os.path.abspath(__file__)
# backend/services/auth_service.py -> backend/services -> backend -> cybertwin-agent-service -> /app
# 在Docker中，/app是工作目录，所以向上3级到/app
service_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))  # /app
project_root = service_root  # 在Docker容器中，service_root就是/app

# 方法2: 如果方法1失败，从当前工作目录计算
if not os.path.exists(os.path.join(project_root, 'shared', 'auth_manager.py')):
    cwd = os.getcwd()
    # 在Docker容器中，cwd通常是/app
    if os.path.exists(os.path.join(cwd, 'shared', 'auth_manager.py')):
        project_root = cwd
    else:
        # 查找包含 'microservices' 的路径，然后向上找到项目根目录
        parts = os.path.normpath(cwd).split(os.sep)
        if 'microservices' in parts:
            microservices_idx = parts.index('microservices')
            project_root = os.sep.join(parts[:microservices_idx]) if microservices_idx > 0 else os.path.dirname(cwd)
        elif 'cybertwin-agent-service' in cwd:
            # 如果在cybertwin-agent-service目录下，向上两级
            project_root = os.path.dirname(os.path.dirname(cwd))
        else:
            # 默认尝试当前目录（Docker容器中通常是/app）
            project_root = cwd

# 添加到sys.path
if project_root and project_root not in sys.path:
    sys.path.insert(0, project_root)

# 验证并导入
try:
    from shared.auth_manager import auth_manager, UserRole, UserStatus
except ImportError as e:
    logger.error(f"无法导入 shared.auth_manager: {e}")
    logger.error(f"当前工作目录: {os.getcwd()}")
    logger.error(f"项目根目录: {project_root}")
    logger.error(f"sys.path前5项: {sys.path[:5]}")
    logger.error(f"检查路径: {os.path.join(project_root, 'shared', 'auth_manager.py')}")
    logger.error(f"路径存在: {os.path.exists(os.path.join(project_root, 'shared', 'auth_manager.py'))}")
    # 列出shared目录内容（如果存在）
    shared_dir = os.path.join(project_root, 'shared')
    if os.path.exists(shared_dir):
        logger.error(f"shared目录内容: {os.listdir(shared_dir)}")
    raise
from backend.utils.database import get_database

class AuthService:
    """认证服务类"""
    
    def __init__(self):
        """初始化认证服务"""
        self.secret_key = "cybertwin-secret-key"  # 生产环境应该从环境变量获取
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[Any], Optional[str]]:
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
    
    def register_user(self, username: str, password: str, email: Optional[str] = None, role: str = "patient") -> Tuple[bool, str, Optional[Any]]:
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
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            payload = {
                "user_id": user_id,
                "exp": expire,
                "type": "access"
            }
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
            payload = {
                "user_id": user_id,
                "exp": expire,
                "type": "refresh"
            }
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
                "email": getattr(user, 'email', None),
                "role": user.role.value,
                "status": user.status.value,
                "created_at": getattr(user, 'created_at', None)
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
            # 路径已在文件开头设置
            from shared.auth_manager import PasswordManager
            return PasswordManager.verify_password(password, hashed_password)
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False
    
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
