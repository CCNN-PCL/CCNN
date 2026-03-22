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
数据库管理器 - 全局数据库访问接口
==================================

提供统一的数据库访问接口，支持MySQL和SQLite
"""

import logging
import sys
import os
from typing import Optional, Dict, Any, List

# 添加项目根目录到Python路径
# 在Docker容器中，工作目录是/app，shared目录在/app/shared
# 所以项目根目录就是/app（即当前shared目录的父目录）
current_file = os.path.abspath(__file__)
# shared/database_manager.py -> shared -> /app
project_root = os.path.dirname(os.path.dirname(current_file))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

class GlobalDatabaseManager:
    """
    全局数据库管理器
    
    提供统一的数据库访问接口，根据配置使用MySQL或SQLite
    """
    
    def __init__(self):
        """初始化数据库管理器"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._db_manager = None
        self._init_database_manager()
    
    def _init_database_manager(self):
        """初始化底层数据库管理器"""
        try:
            # 尝试导入数据库配置
            try:
                from config.database_config import db_config
                database_type = db_config.database_type
            except ImportError:
                # 从环境变量获取
                database_type = os.getenv('DATABASE_TYPE', 'mysql').lower()
            
            if database_type == 'mysql':
                # 使用MySQL数据库管理器
                from shared.mysql_database_manager import mysql_db_manager
                self._db_manager = mysql_db_manager
                self.logger.info("使用MySQL数据库管理器")
            else:
                # 使用SQLite（通过UnifiedDatabaseManager）
                from shared.unified_database_manager import UnifiedDatabaseManager
                self._db_manager = UnifiedDatabaseManager()
                self.logger.info("使用SQLite数据库管理器")
        except Exception as e:
            self.logger.error(f"数据库管理器初始化失败: {str(e)}")
            # 使用UnifiedDatabaseManager作为后备
            try:
                from shared.unified_database_manager import UnifiedDatabaseManager
                self._db_manager = UnifiedDatabaseManager()
                self.logger.warning("使用UnifiedDatabaseManager作为后备")
            except Exception as e2:
                self.logger.error(f"后备数据库管理器初始化也失败: {str(e2)}")
                self._db_manager = None
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息（包括医疗历史）
        
        参数:
            user_id: 用户ID
            
        返回:
            Optional[Dict[str, Any]]: 用户信息字典，包含medical_history和last_update
        """
        if not self._db_manager:
            self.logger.error("数据库管理器未初始化")
            return None
        
        try:
            # 如果是MySQL数据库管理器
            if hasattr(self._db_manager, 'get_user'):
                user_info = await self._db_manager.get_user(user_id)
                if user_info:
                    # 转换为期望的格式
                    return {
                        "user_id": user_id,
                        "medical_history": user_info.get("medical_history") or user_info.get("record_data"),
                        "last_update": user_info.get("last_update") or user_info.get("created_at")
                    }
            
            # 如果是UnifiedDatabaseManager，尝试查询医疗记录
            if hasattr(self._db_manager, 'execute_query'):
                # 查询医疗记录表
                query = "SELECT record_data, created_at FROM medical_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1"
                result = self._db_manager.execute_query(query, (user_id,), 'medical_records')
                if result:
                    return {
                        "user_id": user_id,
                        "medical_history": result[0][0] if isinstance(result[0], (list, tuple)) else result[0].get("record_data"),
                        "last_update": result[0][1] if isinstance(result[0], (list, tuple)) else result[0].get("created_at")
                    }
            
            return None
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
    
    async def get_user_vitals(self, user_id: str, limit: int = 90) -> List[Dict[str, Any]]:
        """
        获取用户体征数据（近N天）
        
        参数:
            user_id: 用户ID
            limit: 天数限制，默认90天
            
        返回:
            List[Dict[str, Any]]: 体征数据列表
        """
        if not self._db_manager:
            self.logger.error("数据库管理器未初始化")
            return []
        
        try:
            # 如果是MySQL数据库管理器
            if hasattr(self._db_manager, 'get_vitals'):
                vitals = await self._db_manager.get_vitals(user_id, limit=limit)
                return vitals if vitals else []
            
            # 如果是UnifiedDatabaseManager，尝试查询vitals表
            if hasattr(self._db_manager, 'execute_query'):
                # 查询体征表（假设表名为vitals）
                query = """
                    SELECT date, systolic_bp, diastolic_bp, heart_rate 
                    FROM vitals 
                    WHERE user_id = ? AND date >= DATE('now', '-' || ? || ' days')
                    ORDER BY date DESC
                """
                result = self._db_manager.execute_query(query, (user_id, limit), 'medical_records')
                if result:
                    return [
                        {
                            "date": row[0] if isinstance(row, (list, tuple)) else row.get("date"),
                            "systolic_bp": row[1] if isinstance(row, (list, tuple)) else row.get("systolic_bp"),
                            "diastolic_bp": row[2] if isinstance(row, (list, tuple)) else row.get("diastolic_bp"),
                            "heart_rate": row[3] if isinstance(row, (list, tuple)) else row.get("heart_rate")
                        }
                        for row in result
                    ]
            
            return []
        except Exception as e:
            self.logger.warning(f"获取用户体征失败: {str(e)}")
            return []

