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
PostgreSQL 认证适配器
===================

为 AuthManager 提供 PostgreSQL 支持
使用同步 psycopg2 库避免异步问题
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import psycopg2
from psycopg2 import pool

logger = logging.getLogger(__name__)

class PostgreSQLAuthAdapter:
    """PostgreSQL 认证适配器 - 提供与 SQLite AuthDatabaseManager 相同的接口"""
    
    def __init__(self, db_path: str = None):
        """初始化 PostgreSQL 认证适配器"""
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # PostgreSQL 连接信息
        from config.database_config import db_config
        self.config = db_config.config
        self.pool = None
        self._init_pool()
    
    def _init_database(self):
        """初始化数据库（保持兼容性，实际不执行）"""
        pass
    
    def _init_pool(self):
        """初始化连接池"""
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            self.logger.info("PostgreSQL connection pool initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.pool is None:
            self._init_pool()
        return self.pool.getconn()
    
    def _return_connection(self, conn):
        """归还数据库连接"""
        self.pool.putconn(conn)
    
    def create_user(self, user, password: str) -> bool:
        """创建用户"""
        try:
            conn = self._get_connection()
            try:
                from shared.auth_manager import PasswordManager
                password_hash = PasswordManager.hash_password(password)
                
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (
                            user_id, username, email, password_hash, role, status, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, 
                        (user.user_id, user.username, user.email, password_hash,
                         user.role.value, user.status.value, user.created_at)
                    )
                    conn.commit()
                    return True
            finally:
                self._return_connection(conn)
        except Exception as e:
            self.logger.error(f"创建用户失败: {str(e)}")
            return False
    
    def get_user_by_username(self, username: str):
        """根据用户名获取用户"""
        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, username, email, password_hash, role, status, created_at
                        FROM users WHERE username = %s
                    """, (username,))
                    
                    row = cur.fetchone()
                    
                    if row:
                        from shared.auth_manager import User, UserRole, UserStatus
                        return User(
                            user_id=row[0],
                            username=row[1],
                            email=row[2],
                            role=UserRole(row[4]),
                            status=UserStatus(row[5]),
                            created_at=row[6],
                            last_login=None,
                            login_attempts=0,
                            locked_until=None,
                            profile={}
                        )
                    return None
            finally:
                self._return_connection(conn)
        except Exception as e:
            self.logger.error(f"获取用户失败: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str):
        """根据用户ID获取用户"""
        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, username, email, password_hash, role, status, created_at
                        FROM users WHERE user_id = %s
                    """, (user_id,))
                    
                    row = cur.fetchone()
                    
                    if row:
                        from shared.auth_manager import User, UserRole, UserStatus
                        return User(
                            user_id=row[0],
                            username=row[1],
                            email=row[2],
                            role=UserRole(row[4]),
                            status=UserStatus(row[5]),
                            created_at=row[6],
                            last_login=None,
                            login_attempts=0,
                            locked_until=None,
                            profile={}
                        )
                    return None
            finally:
                self._return_connection(conn)
        except Exception as e:
            self.logger.error(f"获取用户失败: {str(e)}")
            return None
    
    def update_user(self, user) -> bool:
        """更新用户信息"""
        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users SET 
                            username = %s, email = %s, role = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s
                    """, 
                        (user.username, user.email, user.role.value, user.status.value, user.user_id)
                    )
                    conn.commit()
                    return True
            finally:
                self._return_connection(conn)
        except Exception as e:
            self.logger.error(f"更新用户失败: {str(e)}")
            return False
    
    def verify_password(self, username: str, password: str) -> bool:
        """验证用户密码"""
        try:
            conn = self._get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT password_hash FROM users WHERE username = %s
                    """, (username,))
                    
                    row = cur.fetchone()
                    
                    if row:
                        password_hash = row[0]
                        from shared.auth_manager import PasswordManager
                        return PasswordManager.verify_password(password, password_hash)
                    return False
            finally:
                self._return_connection(conn)
        except Exception as e:
            self.logger.error(f"密码验证失败: {str(e)}")
            return False
    
    def record_login_attempt(self, attempt) -> bool:
        """记录登录尝试"""
        # 简化实现，跳过登录尝试记录
        return True
    
    def create_session(self, session_id: str, user_id: str, token: str, 
                     expires_at, ip_address: str = None, user_agent: str = None) -> bool:
        """创建会话"""
        # 简化实现，跳过会话创建
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        return True
    
    def log_audit_event(self, user_id: str, action: str, resource: str = None,
                       ip_address: str = None, details: str = None) -> bool:
        """记录审计日志"""
        try:
            conn = self._get_connection()
            try:
                # 检查 audit_logs 表是否存在
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' AND table_name = 'audit_logs'
                        )
                    """)
                    
                    table_exists = cur.fetchone()[0]
                    
                    if not table_exists:
                        self.logger.warning("audit_logs 表不存在，跳过审计日志记录")
                        return True
                    
                    # 插入审计日志
                    details_json = f'{{"details": "{details}"}}' if details else None
                    ip_str = str(ip_address) if ip_address and ip_address != 'unknown' else None
                    
                    cur.execute("""
                        INSERT INTO audit_logs (user_id, action, resource, details, ip_address, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, action, resource, details_json, ip_str, datetime.now()))
                    
                    conn.commit()
                    return True
            finally:
                self._return_connection(conn)
        except Exception as e:
            self.logger.error(f"记录审计日志失败: {str(e)}")
            return False
