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

# 直接定义配置变量
ISSUER_URL = os.getenv('ISSUER_URL', 'http://localhost:5000')
REDIRECT_URL = os.getenv('REDIRECT_URL', 'http://localhost:5050') 
ORIGINS_URL = os.getenv('ORIGINS_URL', 'http://localhost:8080')
JWR_URL = os.getenv('JWR_URL', 'http://172.25.21.129:5000')
RBAC_URL = os.getenv('RBAC_URL', 'http://192.168.193.9:31124')
MCP_URL = os.getenv('MCP_URL', 'http://192.168.193.12:31445')

# 配置字典
URL_CONFIG = {
    'issuer_url': ISSUER_URL,
    'redirect_url': REDIRECT_URL,
    'origins_url': ORIGINS_URL
}