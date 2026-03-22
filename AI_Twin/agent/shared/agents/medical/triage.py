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
分诊智能体 (TriageAgent)
========================

专门处理医疗分诊建议和科室推荐。

主要功能：
1. 症状严重程度评估
2. 科室推荐
3. 就医紧急程度判断
4. 分诊建议

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent


class TriageAgent(BaseAgent):
    """
    分诊智能体
    
    专门处理医疗分诊相关的建议，包括：
    - 症状严重程度评估
    - 科室推荐
    - 就医紧急程度判断
    - 分诊建议
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化分诊智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "triage"
        self.name = "分诊推荐智能体"
        self.specialization = "医疗分诊"
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, summary: str, user_id: str, user_info: Optional[Dict] = None) -> str:
        """
        执行分诊建议
        
        参数：
            summary (str): 综合汇总结果
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            str: 分诊建议
        """
        try:
            # 验证输入
            if not summary or not summary.strip():
                return "⚠️ 没有可分析的汇总结果。"
            
            # 获取对话历史
            context = self.get_context_from_memory(user_id)
            
            # 构建分诊提示
            triage_prompt = self._build_triage_prompt(summary, context, user_info)
            
            # 调用LLM进行分诊
            triage = await self.caller(triage_prompt, self.model_config)
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, f"分诊分析：{summary[:100]}...", self.name, triage)
            
            self.logger.info(f"[{self.name}] 分诊建议完成")
            return triage
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 分诊建议错误：{str(e)}"
    
    def _build_triage_prompt(self, summary: str, context: str, user_info: Optional[Dict]) -> str:
        """
        构建分诊提示 - 医生人设优化版
        
        参数：
            summary (str): 综合汇总结果
            context (str): 对话上下文
            user_info (Dict, optional): 用户信息
            
        返回：
            str: 分诊提示
        """
        user_info_str = ""
        if user_info:
            user_info_str = f"""
用户信息：
- 年龄：{user_info.get('age', '未知')}
- 性别：{user_info.get('gender', '未知')}
- 既往病史：{user_info.get('medical_history', '无')}
"""
        
        prompt = f"""作为一位经验丰富的医疗分诊专家，请基于以下信息，用温柔亲切的语气为患者提供分诊建议：

综合汇总结果：
{summary}

对话历史：
{context}
{user_info_str}

请以温柔关怀的医生身份，提供分诊建议，让患者感到被关心和指导：

## 🚨 **紧急程度评估**
- 评估就医紧急程度（紧急/急症/非紧急）
- 用温和的语气解释紧急程度的原因
- 让患者了解时间安排的重要性

## 🏥 **推荐科室**
- 具体推荐的就诊科室
- 用通俗易懂的语言解释科室特点
- 让患者了解为什么选择这个科室

## ⏰ **就医时机**
- 建议的就医时间（具体到小时或天）
- 用关怀的语气解释时间安排的重要性
- 让患者有明确的时间规划

## 🚑 **就医方式**
- 建议的就医方式（急诊/门诊/专科门诊）
- 详细说明不同就医方式的特点
- 让患者知道如何选择合适的就医方式

## 📋 **准备事项**
- 就医前需要准备的事项（具体可操作）
- 用温和的语气提醒患者
- 让患者知道如何做好就医准备

## ⚠️ **注意事项**
- 就医过程中的注意事项
- 用关切的语气提醒患者
- 让患者了解就医时需要注意的问题

## 🔄 **替代方案**
- 如果无法及时就医的替代方案
- 用鼓励的语气提供备选方案
- 让患者知道在紧急情况下的应对方法

请用温柔亲切、专业负责的语气，让患者感到：
- 被理解和关心
- 获得专业的医疗指导
- 感到安心和希望
- 明确知道下一步该怎么做

请避免使用过于专业的医学术语，用患者能理解的语言表达。"""
        
        return prompt
    
    async def assess_urgency(self, summary: str) -> Dict[str, Any]:
        """
        评估就医紧急程度
        
        参数：
            summary (str): 综合汇总结果
            
        返回：
            Dict[str, Any]: 紧急程度评估
        """
        try:
            urgency_prompt = f"""基于以下医疗汇总结果，请评估就医紧急程度：

汇总结果：{summary}

请评估：
1. 紧急程度等级（1-5级，5为最紧急）
2. 紧急程度描述
3. 主要紧急因素
4. 建议就医时间
5. 紧急情况处理建议

请用简洁的语言回答。"""
            
            urgency_assessment = await self.caller(urgency_prompt, self.model_config)
            
            return {
                "content": urgency_assessment,
                "category": "紧急程度评估",
                "urgency": "需要专业医生进一步评估"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 紧急程度评估失败: {str(e)}")
            return {
                "content": "建议咨询专业医生进行紧急程度评估",
                "category": "紧急程度评估",
                "urgency": "需要专业医生进一步评估"
            }
    
    async def recommend_department(self, summary: str) -> Dict[str, Any]:
        """
        推荐就诊科室
        
        参数：
            summary (str): 综合汇总结果
            
        返回：
            Dict[str, Any]: 科室推荐
        """
        try:
            department_prompt = f"""基于以下医疗汇总结果，请推荐就诊科室：

汇总结果：{summary}

请推荐：
1. 主要推荐科室
2. 次要推荐科室
3. 推荐理由
4. 科室特点说明
5. 就诊建议

请用简洁明了的语言回答。"""
            
            department_recommendation = await self.caller(department_prompt, self.model_config)
            
            return {
                "content": department_recommendation,
                "category": "科室推荐",
                "priority": "high"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 科室推荐失败: {str(e)}")
            return {
                "content": "建议咨询专业医生进行科室推荐",
                "category": "科室推荐",
                "priority": "high"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的分诊智能体，提供医疗分诊建议和科室推荐",
            "capabilities": [
                "症状严重程度评估",
                "科室推荐",
                "就医紧急程度判断",
                "分诊建议"
            ]
        }
