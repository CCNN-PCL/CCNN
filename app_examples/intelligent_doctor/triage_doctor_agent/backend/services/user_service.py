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
用户服务
========

提供用户信息、偏好设置等管理服务

作者: QSIR
版本: 1.0
"""

import logging
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.utils.database import get_database

logger = logging.getLogger(__name__)

class UserService:
    """用户服务类"""
    
    def __init__(self):
        """初始化用户服务"""
        pass
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户资料
        
        参数:
            user_id: 用户ID
            
        返回:
            Optional[Dict[str, Any]]: 用户资料
        """
        try:
            db = get_database()
            if not db:
                return None
            
            query = "SELECT profile FROM users WHERE user_id = ?"
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row and row[0]:
                import json
                return json.loads(row[0])
            else:
                # 返回默认资料
                return {
                    "full_name": "",
                    "phone": "",
                    "email": "",
                    "address": "",
                    "birth_date": None,
                    "gender": "",
                    "emergency_contact": "",
                    "allergies": [],
                    "medications": []
                }
                
        except Exception as e:
            logger.error(f"获取用户资料失败: {str(e)}")
            return None
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> tuple:
        """
        更新用户资料
        
        参数:
            user_id: 用户ID
            profile_data: 资料数据
            
        返回:
            tuple: (成功标志, 消息)
        """
        try:
            db = get_database()
            if not db:
                return False, "数据库连接失败"
            
            import json
            profile_json = json.dumps(profile_data, ensure_ascii=False)
            
            query = "UPDATE users SET profile = ? WHERE user_id = ?"
            cursor = db.cursor()
            cursor.execute(query, (profile_json, user_id))
            db.commit()
            
            if cursor.rowcount > 0:
                return True, "用户资料更新成功"
            else:
                return False, "用户不存在"
                
        except Exception as e:
            logger.error(f"更新用户资料失败: {str(e)}")
            return False, f"更新失败: {str(e)}"
    
    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户偏好设置
        
        参数:
            user_id: 用户ID
            
        返回:
            Optional[Dict[str, Any]]: 偏好设置
        """
        try:
            db = get_database()
            if not db:
                return None
            
            query = "SELECT preferences FROM users WHERE user_id = ?"
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row and row[0]:
                import json
                return json.loads(row[0])
            else:
                # 返回默认偏好设置
                return {
                    "language": "zh-CN",
                    "theme": "light",
                    "timezone": "Asia/Shanghai",
                    "notifications": {
                        "email_notifications": True,
                        "push_notifications": True,
                        "sms_notifications": False
                    },
                    "privacy_settings": {
                        "profile_public": False,
                        "data_sharing": False,
                        "analytics_tracking": True,
                        "marketing_emails": False
                    },
                    "display_settings": {
                        "font_size": "medium",
                        "color_scheme": "default",
                        "layout": "standard"
                    }
                }
                
        except Exception as e:
            logger.error(f"获取用户偏好设置失败: {str(e)}")
            return None
    
    async def update_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> tuple:
        """
        更新用户偏好设置
        
        参数:
            user_id: 用户ID
            preferences_data: 偏好设置数据
            
        返回:
            tuple: (成功标志, 消息)
        """
        try:
            db = get_database()
            if not db:
                return False, "数据库连接失败"
            
            import json
            preferences_json = json.dumps(preferences_data, ensure_ascii=False)
            
            query = "UPDATE users SET preferences = ? WHERE user_id = ?"
            cursor = db.cursor()
            cursor.execute(query, (preferences_json, user_id))
            db.commit()
            
            if cursor.rowcount > 0:
                return True, "用户偏好设置更新成功"
            else:
                return False, "用户不存在"
                
        except Exception as e:
            logger.error(f"更新用户偏好设置失败: {str(e)}")
            return False, f"更新失败: {str(e)}"
    
    async def change_password(self, user_id: str, new_password: str) -> tuple:
        """
        修改用户密码
        
        参数:
            user_id: 用户ID
            new_password: 新密码
            
        返回:
            tuple: (成功标志, 消息)
        """
        try:
            # 确保项目根目录在路径中
            import sys
            import os
            from pathlib import Path
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from shared.auth_manager import PasswordManager
            
            # 生成密码哈希
            password_hash = PasswordManager.hash_password(new_password)
            
            db = get_database()
            if not db:
                return False, "数据库连接失败"
            
            query = "UPDATE users SET password_hash = ? WHERE user_id = ?"
            cursor = db.cursor()
            cursor.execute(query, (password_hash, user_id))
            db.commit()
            
            if cursor.rowcount > 0:
                return True, "密码修改成功"
            else:
                return False, "用户不存在"
                
        except Exception as e:
            logger.error(f"修改密码失败: {str(e)}")
            return False, f"修改失败: {str(e)}"
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        参数:
            user_id: 用户ID
            
        返回:
            Dict[str, Any]: 统计信息
        """
        try:
            db = get_database()
            if not db:
                return {}
            
            # 获取聊天消息数
            chat_query = "SELECT COUNT(*) FROM history WHERE user_id = ?"
            cursor = db.cursor()
            cursor.execute(chat_query, (user_id,))
            total_chat_messages = cursor.fetchone()[0]
            
            # 获取医疗影像数
            image_query = "SELECT COUNT(*) FROM medical_images WHERE user_id = ?"
            cursor.execute(image_query, (user_id,))
            total_medical_images = cursor.fetchone()[0]
            
            # 获取医疗记录数
            record_query = "SELECT COUNT(*) FROM medical_records WHERE user_id = ?"
            cursor.execute(record_query, (user_id,))
            total_medical_records = cursor.fetchone()[0]
            
            # 获取最后登录时间
            user_query = "SELECT last_login, created_at FROM users WHERE user_id = ?"
            cursor.execute(user_query, (user_id,))
            user_row = cursor.fetchone()
            
            last_login = user_row[0] if user_row and user_row[0] else None
            account_created = user_row[1] if user_row and user_row[1] else None
            
            return {
                "total_chat_messages": total_chat_messages,
                "total_medical_images": total_medical_images,
                "total_medical_records": total_medical_records,
                "last_login": last_login,
                "account_created": account_created
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            return {}
    
    async def get_user_activities(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户活动记录
        
        参数:
            user_id: 用户ID
            limit: 记录数量限制
            
        返回:
            List[Dict[str, Any]]: 活动记录
        """
        try:
            db = get_database()
            if not db:
                return []
            
            query = """
                SELECT activity_type, description, metadata, timestamp
                FROM user_activities 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """
            
            cursor = db.cursor()
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
            
            activities = []
            for row in rows:
                activities.append({
                    "activity_type": row[0],
                    "description": row[1],
                    "metadata": row[2] if row[2] else {},
                    "timestamp": row[3]
                })
            
            return activities
            
        except Exception as e:
            logger.error(f"获取用户活动记录失败: {str(e)}")
            return []
    
    async def log_user_activity(self, user_id: str, activity_type: str, description: str, metadata: Dict[str, Any] = None) -> bool:
        """
        记录用户活动
        
        参数:
            user_id: 用户ID
            activity_type: 活动类型
            description: 活动描述
            metadata: 元数据
            
        返回:
            bool: 记录结果
        """
        try:
            db = get_database()
            if not db:
                return False
            
            import json
            metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
            
            query = """
                INSERT INTO user_activities (user_id, activity_type, description, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """
            
            cursor = db.cursor()
            cursor.execute(query, (user_id, activity_type, description, metadata_json, datetime.now()))
            db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"记录用户活动失败: {str(e)}")
            return False
