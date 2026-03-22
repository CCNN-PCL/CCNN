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
路径设置工具
用于正确设置Python路径以导入项目根目录的shared模块
"""

import sys
import os
from pathlib import Path

def setup_project_path():
    """设置项目根目录到Python路径"""
    # 获取当前文件的绝对路径
    current_file = Path(__file__).resolve()
    
    # backend/utils/path_setup.py -> backend/utils -> backend -> cybertwin-agent-service -> microservices -> 项目根目录
    # 向上5级到达项目根目录
    project_root = current_file.parent.parent.parent.parent.parent
    
    # 添加到sys.path（如果还没有）
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    # 验证shared目录存在
    shared_path = Path(project_root_str) / 'shared' / 'auth_manager.py'
    if not shared_path.exists():
        # 如果不存在，尝试从当前工作目录查找
        cwd = Path.cwd()
        # 如果在cybertwin-agent-service目录下，向上两级到项目根目录
        if 'cybertwin-agent-service' in str(cwd):
            project_root = cwd.parent.parent
            project_root_str = str(project_root)
            if project_root_str not in sys.path:
                sys.path.insert(0, project_root_str)
    
    return project_root_str

# 自动执行路径设置
setup_project_path()
