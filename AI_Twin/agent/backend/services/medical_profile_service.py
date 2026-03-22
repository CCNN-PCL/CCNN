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
医疗档案聚合服务 (MedicalProfileService)
=====================================

功能：
- 直接查询多个数据库（global medical_records、user_profiles、auth）
- 聚合为统一的医疗档案视图，供各智能体按需使用
- 无缓存、每次直查，确保实时性
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# 依赖全局与用户档案管理器（均已存在于shared模块中）
from shared.database_manager import GlobalDatabaseManager
from shared.user_manager import UserProfileManager
from shared.auth_manager import AuthDatabaseManager


logger = logging.getLogger(__name__)


@dataclass
class MedicalProfile:
    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: Optional[str] = None
    family_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    birth_date: Optional[str] = None
    last_update: Optional[str] = None  # ISO 字符串，便于序列化
    vitals: Optional[List[Dict[str, Any]]] = None  # 新增：体征（日期、收缩压、舒张压、心率）


class MedicalProfileService:
    """聚合用户医疗档案服务（无缓存，每次直查）。"""

    def __init__(self) -> None:
        self.global_db = GlobalDatabaseManager()
        self.user_profile_manager = UserProfileManager()
        self.auth_db = AuthDatabaseManager()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_medical_profile(self, user_id: str) -> Optional[MedicalProfile]:
        """
        聚合并返回用户医疗档案：
        - 基于 data/medical_records.db 的 records（纯文本病史）
        - 基于 data/user_profiles.db 的结构化档案
        - 基于 data/auth.db 的基础profile（如存在）
        """
        try:
            # 1) 读取纯文本病史（records 表）
            records = None
            medical_history_text = None
            last_update = None
            try:
                records = await self.global_db.get_user_info(user_id)
                if records:
                    medical_history_text = records.get("medical_history")
                    last_update = records.get("last_update")
            except Exception as e:
                self.logger.warning(f"[MedicalProfileService] 获取医疗记录失败: {str(e)}")

            # 2) 读取结构化档案（user_profiles 表）
            user_profile = None
            gender = None
            birth_date = None
            allergies: Optional[List[str]] = None
            medications: Optional[List[str]] = None
            medical_conditions: Optional[List[str]] = None
            try:
                user_profile = self.user_profile_manager.get_user_profile(user_id)
                if user_profile:
                    gender = getattr(user_profile, "gender", None)
                    birth_date = getattr(user_profile, "birth_date", None)
                    allergies = getattr(user_profile, "allergies", None)
                    medications = getattr(user_profile, "medications", None)
                    medical_conditions = getattr(user_profile, "medical_conditions", None)
            except Exception as e:
                self.logger.warning(f"[MedicalProfileService] 获取用户档案失败: {str(e)}")

            # 3) 读取认证库中的profile（如果存在）
            auth_user = None
            auth_profile = {}
            family_history = None
            age = None
            try:
                auth_user = self.auth_db.get_user_by_id(user_id)
                if auth_user:
                    auth_profile = getattr(auth_user, "profile", {}) or {}
                    family_history = auth_profile.get("family_history")
                    age = auth_profile.get("age")
                    # 同步性别/生日（若档案缺失而认证库有）
                    if not gender:
                        gender = auth_profile.get("gender")
                    if not birth_date:
                        birth_date = auth_profile.get("birth_date")
            except Exception as e:
                self.logger.warning(f"[MedicalProfileService] 获取认证档案失败: {str(e)}")

            # 4) 体征（vitals 表，近90天）
            vitals: List[Dict[str, Any]] = []
            try:
                vitals = await self.global_db.get_user_vitals(user_id, limit=90) or []
            except Exception as e:
                self.logger.warning(f"[MedicalProfileService] 获取体征失败: {str(e)}")

            profile = MedicalProfile(
                user_id=user_id,
                age=age,
                gender=gender,
                medical_history=medical_history_text,
                family_history=family_history,
                allergies=allergies,
                medications=medications,
                medical_conditions=medical_conditions,
                birth_date=birth_date,
                last_update=last_update or datetime.now().isoformat(),
                vitals=vitals,
            )
            return profile
        except Exception as e:
            self.logger.error(f"[MedicalProfileService] 获取医疗档案失败: {str(e)}")
            return None


# 单例实例
medical_profile_service = MedicalProfileService()


