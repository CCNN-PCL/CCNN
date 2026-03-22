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
医疗智能体模块
==============

这个模块包含所有医疗相关的智能体实现。

主要组件：
- InternalMedicineAgent: 内科智能体
- SurgicalAgent: 外科智能体
- HistoryAgent: 病史智能体
- SummaryAgent: 总结智能体
- TriageAgent: 分诊智能体
- ComprehensiveAgent: 综合智能体
"""

from .internal_medicine import InternalMedicineAgent
from .surgical import SurgicalAgent
from .history import HistoryAgent
from .summary import SummaryAgent
from .triage import TriageAgent
from .comprehensive import ComprehensiveAgent

__all__ = [
    'InternalMedicineAgent',
    'SurgicalAgent', 
    'HistoryAgent',
    'SummaryAgent',
    'TriageAgent',
    'ComprehensiveAgent'
]
