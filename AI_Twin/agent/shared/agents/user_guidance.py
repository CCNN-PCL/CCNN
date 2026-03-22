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
用户引导系统 (UserGuidance)
=========================

帮助用户更好地描述症状，提供交互式引导。

主要功能：
1. 症状描述引导
2. 交互式问诊
3. 用户教育
4. 症状检查清单

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class UserGuidance:
    """
    用户引导系统
    
    提供交互式引导功能，包括：
    - 症状描述引导
    - 交互式问诊
    - 用户教育
    - 症状检查清单
    """
    
    def __init__(self):
        """
        初始化用户引导系统
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 症状引导模板
        self.symptom_guidance = {
            "疼痛": {
                "description": "请详细描述疼痛的情况",
                "questions": [
                    "疼痛的具体位置在哪里？",
                    "疼痛是什么性质的？（刺痛、胀痛、隐痛、烧灼痛等）",
                    "疼痛的强度如何？（1-10分，10分最痛）",
                    "疼痛是持续的还是间歇性的？",
                    "什么情况下疼痛会加重或缓解？",
                    "疼痛持续多长时间了？",
                    "有没有伴随其他症状？"
                ],
                "tips": [
                    "尽量用具体的位置描述，如'右上腹'、'左胸'等",
                    "描述疼痛性质时，可以用比喻，如'像针扎一样'",
                    "记录疼痛的时间规律，如'早上严重'、'夜间加重'等"
                ]
            },
            "发热": {
                "description": "请详细描述发热的情况",
                "questions": [
                    "体温大概多少度？",
                    "发热是持续的还是间歇性的？",
                    "发热时有没有其他症状？",
                    "发热多长时间了？",
                    "有没有寒战或出汗？",
                    "发热前有没有诱因？",
                    "有没有测量过体温？"
                ],
                "tips": [
                    "如果可能，请提供具体的体温数值",
                    "描述发热的时间规律，如'下午开始发热'",
                    "注意观察是否有寒战、出汗等症状"
                ]
            },
            "消化系统": {
                "description": "请详细描述消化系统症状",
                "questions": [
                    "有没有恶心、呕吐？",
                    "食欲如何？",
                    "大便情况怎么样？",
                    "有没有腹痛、腹胀？",
                    "最近饮食有什么变化？",
                    "有没有反酸、烧心？",
                    "体重有没有变化？"
                ],
                "tips": [
                    "描述大便的颜色、形状、频率",
                    "注意饮食与症状的关系",
                    "记录症状出现的时间规律"
                ]
            },
            "呼吸系统": {
                "description": "请详细描述呼吸系统症状",
                "questions": [
                    "有没有咳嗽？",
                    "咳嗽有痰吗？痰是什么颜色？",
                    "有没有胸闷、气短？",
                    "有没有呼吸困难？",
                    "咳嗽多长时间了？",
                    "什么情况下咳嗽会加重？",
                    "有没有发热？"
                ],
                "tips": [
                    "描述痰的颜色和性质，如'黄色粘痰'、'白色泡沫痰'",
                    "注意呼吸困难的严重程度",
                    "记录咳嗽的时间规律"
                ]
            },
            "神经系统": {
                "description": "请详细描述神经系统症状",
                "questions": [
                    "有没有头痛、头晕？",
                    "有没有失眠或嗜睡？",
                    "有没有记忆力减退？",
                    "有没有肢体麻木或无力？",
                    "有没有意识障碍？",
                    "有没有视力、听力问题？",
                    "有没有平衡问题？"
                ],
                "tips": [
                    "描述头痛的性质和位置",
                    "注意症状的持续时间",
                    "记录症状的诱发因素"
                ]
            }
        }
        
        self.logger.info(f"[{self.__class__.__name__}] 初始化完成")
    
    def get_symptom_guidance(self, symptom_type: str) -> Dict[str, Any]:
        """
        获取症状引导信息
        
        参数：
            symptom_type (str): 症状类型
            
        返回：
            Dict[str, Any]: 引导信息
        """
        return self.symptom_guidance.get(symptom_type, {
            "description": "请详细描述您的症状",
            "questions": [
                "症状的具体表现是什么？",
                "症状持续多长时间了？",
                "什么情况下症状会加重或缓解？",
                "有没有伴随其他症状？"
            ],
            "tips": [
                "尽量详细描述症状",
                "提供症状的时间信息",
                "描述症状的严重程度"
            ]
        })
    
    def generate_guidance_html(self, symptom_type: str) -> str:
        """
        生成引导HTML
        
        参数：
            symptom_type (str): 症状类型
            
        返回：
            str: 引导HTML
        """
        guidance = self.get_symptom_guidance(symptom_type)
        
        questions_html = ""
        for i, question in enumerate(guidance["questions"], 1):
            questions_html += f"""
<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 8px; border-left: 3px solid #007bff;'>
    <strong>问题 {i}:</strong> {question}
</div>"""
        
        tips_html = ""
        for tip in guidance["tips"]:
            tips_html += f"""
<li style='margin-bottom: 5px;'>{tip}</li>"""
        
        return f"""
<div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h3 style='color: #1976d2; margin-bottom: 15px;'>📋 症状描述引导</h3>
    <p style='color: #666; margin-bottom: 15px;'>{guidance['description']}</p>
    
    <h4 style='color: #1976d2; margin-bottom: 10px;'>请回答以下问题：</h4>
    {questions_html}
    
    <h4 style='color: #1976d2; margin-bottom: 10px; margin-top: 20px;'>💡 描述技巧：</h4>
    <ul style='color: #666; margin-left: 20px;'>
        {tips_html}
    </ul>
</div>"""
    
    def generate_symptom_checklist(self, symptom_type: str) -> str:
        """
        生成症状检查清单
        
        参数：
            symptom_type (str): 症状类型
            
        返回：
            str: 检查清单HTML
        """
        guidance = self.get_symptom_guidance(symptom_type)
        
        checklist_items = ""
        for i, question in enumerate(guidance["questions"], 1):
            checklist_items += f"""
<div style='display: flex; align-items: center; margin-bottom: 8px;'>
    <input type='checkbox' id='symptom_{i}' style='margin-right: 10px;'>
    <label for='symptom_{i}' style='color: #333;'>{question}</label>
</div>"""
        
        return f"""
<div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h3 style='color: #1976d2; margin-bottom: 15px;'>✅ 症状检查清单</h3>
    <p style='color: #666; margin-bottom: 15px;'>请勾选您已经考虑过的问题：</p>
    {checklist_items}
    <p style='color: #666; font-style: italic; margin-top: 15px;'>
        完成检查清单后，请详细描述您的症状，这样医生就能更好地帮助您。
    </p>
</div>"""
    
    def get_emergency_guidance(self) -> str:
        """
        获取紧急情况引导
        
        返回：
            str: 紧急情况引导HTML
        """
        return """
<div style='background-color: #ffebee; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #f44336;'>
    <h3 style='color: #d32f2f; margin-bottom: 15px;'>🚨 紧急情况提醒</h3>
    <p style='color: #666; margin-bottom: 15px;'>如果您出现以下症状，请立即就医：</p>
    <ul style='color: #666; margin-left: 20px;'>
        <li>严重的胸痛、呼吸困难</li>
        <li>突然的剧烈头痛</li>
        <li>意识不清、昏迷</li>
        <li>严重的腹痛</li>
        <li>大量出血</li>
        <li>高热不退（体温超过39°C）</li>
        <li>严重的过敏反应</li>
    </ul>
    <p style='color: #d32f2f; font-weight: bold; margin-top: 15px;'>
        紧急情况请拨打120或立即前往最近的急诊科！
    </p>
</div>"""
    
    def get_health_tips(self) -> str:
        """
        获取健康提示
        
        返回：
            str: 健康提示HTML
        """
        return """
<div style='background-color: #e8f5e8; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
    <h3 style='color: #2e7d32; margin-bottom: 15px;'>💡 健康提示</h3>
    <ul style='color: #666; margin-left: 20px;'>
        <li>定期体检，预防胜于治疗</li>
        <li>保持规律作息，充足睡眠</li>
        <li>均衡饮食，适量运动</li>
        <li>保持心情愉快，减少压力</li>
        <li>及时就医，不要拖延</li>
        <li>遵医嘱用药，不要自行停药</li>
    </ul>
</div>"""
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": "user_guidance",
            "name": "用户引导系统",
            "description": "帮助用户更好地描述症状，提供交互式引导",
            "capabilities": [
                "症状描述引导",
                "交互式问诊",
                "用户教育",
                "症状检查清单"
            ]
        }
