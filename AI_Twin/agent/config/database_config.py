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

支持SQLite和PostgreSQL双模式
"""

import os
from typing import Dict, Any
from pathlib import Path

# 尝试加载 .env 文件
def load_env_file():
    """从 .env 文件加载环境变量"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
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
        self.database_type = os.getenv('DATABASE_TYPE', 'sqlite')  # sqlite 或 postgresql
        self.config = self._get_config()
    
    def _get_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        if self.database_type == 'postgresql':
            return self._get_postgresql_config()
        else:
            return self._get_sqlite_config()
    
    def _get_postgresql_config(self) -> Dict[str, Any]:
        """PostgreSQL配置"""
        return {
            'type': 'postgresql',
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'private_doctor_db'),
            'user': os.getenv('POSTGRES_USER', 'doctor_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'doctor_password'),
            'pool_size': int(os.getenv('POSTGRES_POOL_SIZE', 10)),
            'max_overflow': int(os.getenv('POSTGRES_MAX_OVERFLOW', 20)),
            'echo': os.getenv('POSTGRES_ECHO', 'False').lower() == 'true'
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
