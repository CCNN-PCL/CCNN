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
数据库配置文件
=============

支持SQLite和MySQL双模式
注意：PostgreSQL支持已迁移到MySQL，相关代码已注释
"""

import os
from typing import Dict, Any
from pathlib import Path

# 尝试加载 .env 文件
def load_env_file():
    """从 .env 文件加载环境变量"""
    env_file = Path('.env')
    if env_file.exists():
        # 尝试多种编码方式读取文件
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(env_file, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # 如果所有编码都失败，使用 errors='replace' 强制读取
        if content is None:
            try:
                with open(env_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception:
                # 如果还是失败，跳过加载 .env 文件
                return
        
        # 解析内容
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # 只有当前环境变量未设置时才设置
                if key not in os.environ:
                    os.environ[key] = value

# 加载 .env 文件
load_env_file()

class DatabaseConfig:
    """数据库配置类"""
    
    def __init__(self):
        self.database_type = os.getenv('DATABASE_TYPE', 'sqlite')  # sqlite 或 mysql (PostgreSQL已迁移到MySQL)
        self.config = self._get_config()
    
    def _get_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        # PostgreSQL支持已迁移到MySQL，相关代码已注释
        # if self.database_type == 'postgresql':
        #     return self._get_postgresql_config()
        if self.database_type == 'mysql':
            return self._get_mysql_config()
        else:
            return self._get_sqlite_config()
    
    # PostgreSQL配置已注释 - 已迁移到MySQL
    # def _get_postgresql_config(self) -> Dict[str, Any]:
    #     """PostgreSQL配置"""
    #     return {
    #         'type': 'postgresql',
    #         'host': os.getenv('POSTGRES_HOST', 'localhost'),
    #         'port': int(os.getenv('POSTGRES_PORT', 5432)),
    #         'database': os.getenv('POSTGRES_DB', 'private_doctor_db'),
    #         'user': os.getenv('POSTGRES_USER', 'doctor_user'),
    #         'password': os.getenv('POSTGRES_PASSWORD', 'doctor_password'),
    #         'pool_size': int(os.getenv('POSTGRES_POOL_SIZE', 10)),
    #         'max_overflow': int(os.getenv('POSTGRES_MAX_OVERFLOW', 20)),
    #         'echo': os.getenv('POSTGRES_ECHO', 'False').lower() == 'true'
    #     }
    
    def _get_mysql_config(self) -> Dict[str, Any]:
        """MySQL配置"""
        # MySQL地址和端口从环境变量获取，其他信息与PostgreSQL相同
        # 注意：MySQL默认端口是3306，不是PostgreSQL的5432
        return {
            'type': 'mysql',
            'host': os.getenv('MYSQL_HOST', os.getenv('POSTGRES_HOST', 'localhost')),
            'port': int(os.getenv('MYSQL_PORT', 3306)),  # MySQL默认端口3306
            'database': os.getenv('MYSQL_DATABASE', os.getenv('POSTGRES_DB', 'private_doctor_db')),
            'user': os.getenv('MYSQL_USER', os.getenv('POSTGRES_USER', 'doctor_user')),
            'password': os.getenv('MYSQL_PASSWORD', os.getenv('POSTGRES_PASSWORD', 'doctor_password')),
            'pool_size': int(os.getenv('MYSQL_POOL_SIZE', os.getenv('POSTGRES_POOL_SIZE', 10))),
            'max_overflow': int(os.getenv('MYSQL_MAX_OVERFLOW', os.getenv('POSTGRES_MAX_OVERFLOW', 20))),
            'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4'),
            'connect_timeout': int(os.getenv('MYSQL_CONNECT_TIMEOUT', 10)),
            'read_timeout': int(os.getenv('MYSQL_READ_TIMEOUT', 30)),
            'write_timeout': int(os.getenv('MYSQL_WRITE_TIMEOUT', 30)),
            'echo': os.getenv('MYSQL_ECHO', 'False').lower() == 'true'
        }
    
    def _get_sqlite_config(self) -> Dict[str, Any]:
        """SQLite配置"""
        return {
            'type': 'sqlite',
            'databases': {
                'auth': 'data/auth.db',
                'chat_history': 'data/chat_history.db',
                'medical_records': 'data/medical_records.db',
                'user_profiles': 'data/user_profiles.db',
                'permissions': 'data/permissions.db',
                'audit': 'data/audit.db'
            }
        }

# 全局配置实例
db_config = DatabaseConfig()
