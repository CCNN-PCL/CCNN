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
医疗数据服务
============

提供医疗影像、病历等数据管理服务

作者: AI开发团队
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

class MedicalService:
    """医疗数据服务类"""
    
    def __init__(self):
        """初始化医疗数据服务"""
        pass
    
    async def upload_medical_image(self, user_id: str, hospital_id: str, image_data: bytes, 
                                 image_type: str, examination_date: str, description: str = None, 
                                 filename: str = None) -> Dict[str, Any]:
        """
        上传医疗影像
        
        参数:
            user_id: 用户ID
            hospital_id: 医院ID
            image_data: 影像数据
            image_type: 影像类型
            examination_date: 检查日期
            description: 影像描述
            filename: 文件名
            
        返回:
            Dict[str, Any]: 上传结果
        """
        try:
            db = get_database()
            if not db:
                return {"success": False, "message": "数据库连接失败"}
            
            # 检查是否已存在相同记录
            check_query = """
                SELECT id FROM medical_images 
                WHERE user_id = ? AND hospital_id = ? AND image_type = ? AND examination_date = ?
            """
            cursor = db.cursor()
            cursor.execute(check_query, (user_id, hospital_id, image_type, examination_date))
            existing = cursor.fetchone()
            
            if existing:
                return {"success": False, "message": "该用户在同一天、同一医院、同一影像类型已有记录，请选择不同的日期或影像类型"}
            
            # 插入影像记录
            query = """
                INSERT INTO medical_images 
                (user_id, hospital_id, image_data, image_type, image_category, examination_date, description, filename, file_size, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # 确定影像分类
            image_category = self._get_image_category(image_type)
            
            cursor.execute(query, (
                user_id, hospital_id, image_data, image_type, image_category,
                examination_date, description, filename, len(image_data), datetime.now()
            ))
            db.commit()
            
            image_id = cursor.lastrowid
            
            # 验证插入是否成功
            if not image_id:
                return {"success": False, "message": "影像插入失败"}
            
            # 立即验证数据是否已插入
            verify_query = "SELECT id FROM medical_images WHERE id = ? AND user_id = ?"
            cursor.execute(verify_query, (image_id, user_id))
            verify_result = cursor.fetchone()
            
            if not verify_result:
                return {"success": False, "message": "影像插入验证失败"}
            
            # 构建响应
            image_info = {
                "image_id": str(image_id),
                "user_id": user_id,
                "hospital_id": hospital_id,
                "image_type": image_type,
                "image_category": image_category,
                "examination_date": examination_date,
                "description": description,
                "upload_time": datetime.now().isoformat(),
                "file_size": len(image_data)
            }
            
            return {
                "success": True,
                "message": "影像上传成功",
                "image_id": str(image_id),
                "image_info": image_info
            }
            
        except Exception as e:
            logger.error(f"上传医疗影像失败: {str(e)}")
            return {"success": False, "message": f"上传失败: {str(e)}"}
    
    async def get_medical_images(self, user_id: str, hospital_id: str = None, 
                               image_type: str = None) -> List[Dict[str, Any]]:
        """
        获取医疗影像列表
        
        参数:
            user_id: 用户ID
            hospital_id: 医院ID过滤
            image_type: 影像类型过滤
            
        返回:
            List[Dict[str, Any]]: 影像列表
        """
        try:
            # 使用新的数据库连接，避免缓存问题
            import sqlite3
            import os
            
            data_dir = "data"
            db_path = os.path.join(data_dir, "chat_history.db")
            db = sqlite3.connect(db_path)
            db.row_factory = sqlite3.Row
            
            # 构建查询条件
            where_conditions = ["user_id = ?"]
            params = [user_id]
            
            if hospital_id:
                where_conditions.append("hospital_id = ?")
                params.append(hospital_id)
            
            if image_type:
                where_conditions.append("image_type = ?")
                params.append(image_type)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, user_id, hospital_id, image_data, image_type, image_category, 
                       examination_date, description, filename, file_size, timestamp
                FROM medical_images 
                WHERE {where_clause}
                ORDER BY timestamp DESC
            """
            
            cursor = db.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            images = []
            for row in rows:
                images.append({
                    "image_id": str(row[0]),
                    "user_id": row[1],
                    "hospital_id": row[2],
                    "image_data": row[3],  # 添加image_data字段
                    "image_type": row[4],
                    "image_category": row[5],
                    "examination_date": row[6],
                    "description": row[7],
                    "filename": row[8],
                    "file_size": row[9],
                    "upload_time": row[10]
                })
            
            db.close()
            return images
            
        except Exception as e:
            logger.error(f"获取医疗影像失败: {str(e)}")
            return []
    
    async def get_medical_image(self, image_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定医疗影像
        
        参数:
            image_id: 影像ID
            user_id: 用户ID
            
        返回:
            Optional[Dict[str, Any]]: 影像数据
        """
        try:
            db = get_database()
            if not db:
                return None
            
            query = """
                SELECT id, user_id, hospital_id, image_data, image_type, image_category,
                       examination_date, description, filename, file_size, timestamp
                FROM medical_images 
                WHERE id = ? AND user_id = ?
            """
            
            cursor = db.cursor()
            cursor.execute(query, (image_id, user_id))
            row = cursor.fetchone()
            
            if row:
                return {
                    "image_id": str(row[0]),
                    "user_id": row[1],
                    "hospital_id": row[2],
                    "image_data": row[3],
                    "image_type": row[4],
                    "image_category": row[5],
                    "examination_date": row[6],
                    "description": row[7],
                    "filename": row[8],
                    "file_size": row[9],
                    "upload_time": row[10]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"获取医疗影像失败: {str(e)}")
            return None
    
    async def delete_medical_image(self, image_id: str, user_id: str) -> Dict[str, Any]:
        """
        删除医疗影像
        
        参数:
            image_id: 影像ID
            user_id: 用户ID
            
        返回:
            Dict[str, Any]: 删除结果
        """
        try:
            # 直接创建新的数据库连接，避免缓存问题
            import sqlite3
            import os
            
            data_dir = "data"
            db_path = os.path.join(data_dir, "chat_history.db")
            db = sqlite3.connect(db_path)
            cursor = db.cursor()
            
            # 先检查影像是否存在
            check_query = "SELECT id FROM medical_images WHERE id = ? AND user_id = ?"
            cursor.execute(check_query, (image_id, user_id))
            existing = cursor.fetchone()
            
            if not existing:
                db.close()
                return {"success": False, "message": "影像不存在或无权限删除"}
            
            # 删除影像
            delete_query = "DELETE FROM medical_images WHERE id = ? AND user_id = ?"
            cursor.execute(delete_query, (image_id, user_id))
            db.commit()
            
            # 验证删除结果
            cursor.execute(check_query, (image_id, user_id))
            remaining = cursor.fetchone()
            
            db.close()
            
            if not remaining:
                return {"success": True, "message": "影像删除成功"}
            else:
                return {"success": False, "message": "删除操作失败"}
            
        except Exception as e:
            logger.error(f"删除医疗影像失败: {str(e)}")
            return {"success": False, "message": f"删除失败: {str(e)}"}
    
    async def upload_medical_record(self, user_id: str, hospital_id: str, record_data: bytes,
                                  record_type: str, description: str = None, filename: str = None) -> Dict[str, Any]:
        """
        上传医疗记录
        
        参数:
            user_id: 用户ID
            hospital_id: 医院ID
            record_data: 记录数据
            record_type: 记录类型
            description: 记录描述
            filename: 文件名
            
        返回:
            Dict[str, Any]: 上传结果
        """
        try:
            # 使用医疗记录专用数据库
            import sqlite3
            import os
            data_dir = "data"
            db_path = os.path.join(data_dir, "medical_records.db")
            
            if not os.path.exists(db_path):
                return {"success": False, "message": "医疗记录数据库不存在"}
            
            db = sqlite3.connect(db_path, check_same_thread=False)
            db.row_factory = sqlite3.Row
            
            # 检查是否已存在相同记录
            check_query = """
                SELECT user_id FROM records 
                WHERE user_id = ? AND medical_history LIKE ?
            """
            cursor = db.cursor()
            # 构建医疗历史记录内容
            from datetime import datetime
            medical_history = f"记录类型: {record_type}\n医院ID: {hospital_id}\n描述: {description or '无'}\n文件名: {filename or '无'}\n文件大小: {len(record_data)} bytes\n上传时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            cursor.execute(check_query, (user_id, f"%{record_type}%"))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                update_query = """
                    UPDATE records 
                    SET medical_history = ?, timestamp = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """
                cursor.execute(update_query, (medical_history, user_id))
                record_id = user_id
            else:
                # 插入新记录
                query = """
                    INSERT INTO records (user_id, medical_history)
                    VALUES (?, ?)
                """
                cursor.execute(query, (user_id, medical_history))
                record_id = user_id
            
            db.commit()
            db.close()
            
            return {
                "success": True,
                "message": "医疗记录上传成功",
                "record_id": str(record_id)
            }
            
        except Exception as e:
            logger.error(f"上传医疗记录失败: {str(e)}")
            return {"success": False, "message": f"上传失败: {str(e)}"}
    
    async def get_medical_records(self, user_id: str, hospital_id: str = None,
                                record_type: str = None) -> List[Dict[str, Any]]:
        """
        获取医疗记录列表
        
        参数:
            user_id: 用户ID
            hospital_id: 医院ID过滤
            record_type: 记录类型过滤
            
        返回:
            List[Dict[str, Any]]: 记录列表
        """
        try:
            logger.info(f"获取医疗记录列表 - 用户ID: {user_id}")
            
            # 简化实现，直接返回测试数据
            records = [
                {
                    "record_id": "1",
                    "user_id": user_id,
                    "hospital_id": "TEST001",
                    "record_type": "test_record",
                    "description": "测试医疗记录",
                    "filename": "test_record.txt",
                    "file_size": 96,
                    "upload_time": "2025-10-09 09:07:44"
                }
            ]
            
            logger.info(f"返回 {len(records)} 条记录")
            return records
            
        except Exception as e:
            logger.error(f"获取医疗记录失败: {str(e)}", exc_info=True)
            return []
    
    async def get_hospitals(self) -> List[Dict[str, Any]]:
        """
        获取医院列表
        
        返回:
            List[Dict[str, Any]]: 医院列表
        """
        try:
            # 这里应该从数据库或配置文件获取医院信息
            # 暂时返回硬编码的医院列表
            hospitals = [
                {
                    "id": "BJ001",
                    "name": "北京协和医院",
                    "location": "北京",
                    "api_endpoint": "http://api-endpoint",
                    "model_config": {}
                },
                {
                    "id": "SH001",
                    "name": "上海瑞金医院",
                    "location": "上海",
                    "api_endpoint": "http://api-endpoint",
                    "model_config": {}
                }
            ]
            
            return hospitals
            
        except Exception as e:
            logger.error(f"获取医院列表失败: {str(e)}")
            return []
    
    def _get_image_category(self, image_type: str) -> str:
        """
        根据影像类型获取分类
        
        参数:
            image_type: 影像类型
            
        返回:
            str: 影像分类
        """
        category_mapping = {
            # 放射影像
            "chest_xray": "radiology", "chest_ct": "radiology",
            "heart_ct": "radiology", "head_ct": "radiology",
            "abdominal_ct": "radiology", "bone_xray": "radiology",
            "bone_ct": "radiology", "joint_xray": "radiology",
            
            # 超声影像
            "ultrasound": "ultrasound", "color_ultrasound": "ultrasound",
            "heart_ultrasound": "ultrasound", "abdominal_ultrasound": "ultrasound",
            
            # 皮肤影像
            "skin_photo": "dermatology", "dermoscopy": "dermatology",
            
            # 内窥镜影像
            "gastroscopy": "endoscopy", "colonoscopy": "endoscopy", "endoscopy": "endoscopy",
            
            # 电生理
            "ecg": "electrophysiology", "eeg": "electrophysiology", "emg": "electrophysiology"
        }
        
        return category_mapping.get(image_type, "other")
