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
PostgreSQL数据库管理器
====================

支持PostgreSQL的数据库管理器
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import asyncpg
from contextlib import asynccontextmanager
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.database_config import db_config
except ImportError:
    # 如果无法导入配置，使用默认配置
    db_config = type('Config', (), {
        'config': {
            'host': 'localhost',
            'port': 5432,
            'database': 'private_doctor_db',
            'user': 'doctor_user',
            'password': 'doctor_password',
            'pool_size': 10
        }
    })()

class PostgreSQLConnectionPool:
    """PostgreSQL连接池管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self):
        """初始化连接池"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                min_size=5,
                max_size=self.config['pool_size'],
                command_timeout=60
            )
            self.logger.info("PostgreSQL连接池初始化成功")
        except Exception as e:
            self.logger.error(f"PostgreSQL连接池初始化失败: {str(e)}")
            raise
    
    async def close(self):
        """关闭连接池"""
        if self.pool:
            await self.pool.close()
            self.logger.info("PostgreSQL连接池已关闭")
    
    @asynccontextmanager
    async def get_connection(self):
        """获取数据库连接"""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as connection:
            yield connection

class PostgreSQLDatabaseManager:
    """PostgreSQL数据库管理器"""
    
    def __init__(self):
        self.config = db_config.config
        self.pool = PostgreSQLConnectionPool(self.config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def initialize(self):
        """初始化数据库管理器"""
        await self.pool.initialize()
        self.logger.info("PostgreSQL数据库管理器初始化完成")
    
    async def close(self):
        """关闭数据库管理器"""
        await self.pool.close()
    
    # 用户相关操作
    async def create_user(self, user_id: str, username: str, email: str, 
                         password_hash: str, role: str = 'patient') -> bool:
        """创建用户"""
        try:
            async with self.pool.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username, email, password_hash, role)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        email = EXCLUDED.email,
                        password_hash = EXCLUDED.password_hash,
                        role = EXCLUDED.role,
                        updated_at = CURRENT_TIMESTAMP
                """, user_id, username, email, password_hash, role)
                return True
        except Exception as e:
            self.logger.error(f"创建用户失败: {str(e)}")
            return False
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            async with self.pool.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1", user_id
                )
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        try:
            async with self.pool.get_connection() as conn:
                rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取所有用户失败: {str(e)}")
            return []
    
    # 聊天历史操作
    async def store_chat_message(self, user_id: str, role: str, content: str, 
                                session_id: str = None, agent_name: str = None) -> bool:
        """存储聊天消息"""
        try:
            async with self.pool.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO chat_history (user_id, role, content, session_id, agent_name)
                    VALUES ($1, $2, $3, $4, $5)
                """, user_id, role, content, session_id, agent_name)
                return True
        except Exception as e:
            self.logger.error(f"存储聊天消息失败: {str(e)}")
            return False
    
    async def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取聊天历史"""
        try:
            async with self.pool.get_connection() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM chat_history 
                    WHERE user_id = $1 
                    ORDER BY timestamp DESC 
                    LIMIT $2
                """, user_id, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取聊天历史失败: {str(e)}")
            return []
    
    async def get_all_chat_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有聊天历史"""
        try:
            async with self.pool.get_connection() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM chat_history 
                    ORDER BY timestamp DESC 
                    LIMIT $1
                """, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取所有聊天历史失败: {str(e)}")
            return []
    
    # 医疗影像操作
    async def store_medical_image(self, user_id: str, hospital_id: str, 
                                 image_type: str, image_category: str,
                                 examination_date: str, description: str = None,
                                 filename: str = None, file_size: int = None,
                                 file_path: str = None) -> bool:
        """存储医疗影像"""
        try:
            async with self.pool.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO medical_images (user_id, hospital_id, image_type, 
                                              image_category, examination_date, 
                                              description, filename, file_size, file_path)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, user_id, hospital_id, image_type, image_category, 
                    examination_date, description, filename, file_size, file_path)
                return True
        except Exception as e:
            self.logger.error(f"存储医疗影像失败: {str(e)}")
            return False
    
    async def get_medical_images(self, user_id: str, hospital_id: str = None) -> List[Dict[str, Any]]:
        """获取医疗影像"""
        try:
            async with self.pool.get_connection() as conn:
                if hospital_id:
                    rows = await conn.fetch("""
                        SELECT * FROM medical_images 
                        WHERE user_id = $1 AND hospital_id = $2
                        ORDER BY created_at DESC
                    """, user_id, hospital_id)
                else:
                    rows = await conn.fetch("""
                        SELECT * FROM medical_images 
                        WHERE user_id = $1
                        ORDER BY created_at DESC
                    """, user_id)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取医疗影像失败: {str(e)}")
            return []
    
    async def get_all_medical_images(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有医疗影像"""
        try:
            async with self.pool.get_connection() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM medical_images 
                    ORDER BY created_at DESC 
                    LIMIT $1
                """, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取所有医疗影像失败: {str(e)}")
            return []
    
    # 医疗记录操作
    async def store_medical_record(self, user_id: str, hospital_id: str,
                                  record_data: str, record_type: str,
                                  description: str = None) -> bool:
        """存储医疗记录"""
        try:
            async with self.pool.get_connection() as conn:
                await conn.execute("""
                    INSERT INTO medical_records (user_id, hospital_id, record_data, record_type, description)
                    VALUES ($1, $2, $3, $4, $5)
                """, user_id, hospital_id, record_data, record_type, description)
                return True
        except Exception as e:
            self.logger.error(f"存储医疗记录失败: {str(e)}")
            return False
    
    async def get_medical_records(self, user_id: str, hospital_id: str = None) -> List[Dict[str, Any]]:
        """获取医疗记录"""
        try:
            async with self.pool.get_connection() as conn:
                if hospital_id:
                    rows = await conn.fetch("""
                        SELECT * FROM medical_records 
                        WHERE user_id = $1 AND hospital_id = $2
                        ORDER BY created_at DESC
                    """, user_id, hospital_id)
                else:
                    rows = await conn.fetch("""
                        SELECT * FROM medical_records 
                        WHERE user_id = $1
                        ORDER BY created_at DESC
                    """, user_id)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取医疗记录失败: {str(e)}")
            return []
    
    async def get_all_medical_records(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有医疗记录"""
        try:
            async with self.pool.get_connection() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM medical_records 
                    ORDER BY created_at DESC 
                    LIMIT $1
                """, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取所有医疗记录失败: {str(e)}")
            return []
    
    # 医院信息操作
    async def get_hospitals(self) -> List[Dict[str, Any]]:
        """获取所有医院信息"""
        try:
            async with self.pool.get_connection() as conn:
                rows = await conn.fetch("SELECT * FROM hospitals ORDER BY created_at")
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"获取医院信息失败: {str(e)}")
            return []
    
    # 统计信息
    async def get_statistics(self) -> Dict[str, int]:
        """获取数据库统计信息"""
        try:
            async with self.pool.get_connection() as conn:
                stats = {}
                
                # 用户数量
                stats['users'] = await conn.fetchval("SELECT COUNT(*) FROM users")
                
                # 聊天记录数量
                stats['chat_history'] = await conn.fetchval("SELECT COUNT(*) FROM chat_history")
                
                # 医疗影像数量
                stats['medical_images'] = await conn.fetchval("SELECT COUNT(*) FROM medical_images")
                
                # 医疗记录数量
                stats['medical_records'] = await conn.fetchval("SELECT COUNT(*) FROM medical_records")
                
                # 医院数量
                stats['hospitals'] = await conn.fetchval("SELECT COUNT(*) FROM hospitals")
                
                return stats
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {str(e)}")
            return {}

# 全局数据库管理器实例
postgresql_db_manager = PostgreSQLDatabaseManager()
