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
医疗数据模型
============

定义医疗相关的Pydantic模型

作者: AI开发团队
版本: 1.0
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class MedicalImage(BaseModel):
    """医疗影像模型"""
    image_id: str
    user_id: str
    hospital_id: str
    image_type: str
    image_category: str
    examination_date: str
    description: Optional[str] = None
    upload_time: str
    file_size: int

class MedicalRecord(BaseModel):
    """医疗记录模型"""
    record_id: str
    user_id: str
    hospital_id: str
    record_type: str
    record_data: str
    upload_time: str
    file_size: int

class Hospital(BaseModel):
    """医院模型"""
    id: str
    name: str
    location: str
    api_endpoint: str
    model_config: Dict[str, Any]
