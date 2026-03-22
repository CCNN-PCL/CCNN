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
病史智能体 (HistoryAgent)
========================

专门处理病史分析和关联分析。

主要功能：
1. 病史信息提取
2. 症状关联分析
3. 病史风险评估
4. 病史建议

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent


class HistoryAgent(BaseAgent):
    """
    病史智能体
    
    专门处理病史相关的分析，包括：
    - 病史信息提取
    - 症状关联分析
    - 病史风险评估
    - 病史建议
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化病史智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "history"
        self.name = "病史分析智能体"
        self.specialization = "病史分析"
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Any:
        """
        执行病史分析
        
        参数：
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Any: 病史分析结果
        """
        try:
            # 验证输入
            if not self.validate_input(user_input):
                return "⚠️ 输入无效，请提供有效的症状描述。"
            
            # 若关键字段缺失，实时直查聚合医疗档案，补全user_info
            try:
                needs_profile = (
                    user_info is None or
                    any(k not in user_info or user_info.get(k) in (None, "", []) for k in ["age", "gender", "medical_history"])  # 关键字段
                )
                if needs_profile:
                    from backend.services.medical_profile_service import medical_profile_service
                    profile = await medical_profile_service.get_medical_profile(user_id)
                    if profile:
                        base = user_info or {}
                        # 合并为新的 user_info（以已有信息为主，缺失才补）
                        user_info = {
                            **base,
                            "age": base.get("age") or profile.age,
                            "gender": base.get("gender") or profile.gender,
                            "medical_history": base.get("medical_history") or profile.medical_history,
                            "family_history": base.get("family_history") or profile.family_history,
                            "allergies": base.get("allergies") or profile.allergies,
                            "medications": base.get("medications") or profile.medications,
                            "medical_conditions": base.get("medical_conditions") or profile.medical_conditions,
                            "birth_date": base.get("birth_date") or profile.birth_date,
                            "last_update": base.get("last_update") or profile.last_update,
                        }
            except Exception as e:
                self.logger.warning(f"[{self.name}] 自动补全user_info失败: {str(e)}")

            # 获取对话历史
            context = self.get_context_from_memory(user_id)
            
            # 构建病史分析提示
            analysis_prompt = self._build_analysis_prompt(user_input, context, user_info)
            
            # 调用LLM进行分析
            analysis = await self.caller(analysis_prompt, self.model_config)
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, user_input, self.name, analysis)
            
            # 构建分析结果
            result = {
                "analysis": analysis,
                "specialization": self.specialization,
                "risk_assessment": await self._assess_risk(user_input, context),
                "recommendations": await self._generate_history_recommendations(analysis)
            }
            
            self.logger.info(f"[{self.name}] 分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 病史分析错误：{str(e)}"
    
    def _build_analysis_prompt(self, user_input: str, context: str, user_info: Optional[Dict]) -> str:
        """
        构建病史分析提示
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            user_info (Dict, optional): 用户信息
            
        返回：
            str: 分析提示
        """
        user_info_str = ""
        if user_info:
            user_info_str = f"""
用户信息：
- 年龄：{user_info.get('age', '未知')}
- 性别：{user_info.get('gender', '未知')}
- 既往病史：{user_info.get('medical_history', '无')}
- 家族病史：{user_info.get('family_history', '无')}
"""
        
        prompt = f"""作为一位经验丰富的病史分析专家，请分析以下信息，用温柔亲切的语气为患者提供病史分析：

当前症状：{user_input}

对话历史：
{context}
{user_info_str}

请以温柔关怀的医生身份，用系统性的方法进行病史分析，让患者感到被理解和关心：

## 📋 **病史信息提取**
- 从患者描述中提取关键病史信息，用温和的语气
- 识别既往疾病、手术史、过敏史等，让患者了解重要性
- 提取家族病史和遗传因素，用关怀的语气解释
- 整理用药史和疫苗接种史，帮助患者了解自己的健康状况

## 🔗 **症状关联分析**
- 分析当前症状与既往病史的关联性，用患者能理解的语言
- 识别可能的疾病进展模式，让患者了解病情发展
- 分析症状的复发或加重因素，用温和的语气提醒
- 评估既往治疗的效果，给予患者希望和指导

## ⏰ **时间线分析**
- 构建详细的症状发展时间线，让患者了解病情发展过程
- 分析症状的急慢性特征，用通俗易懂的语言解释
- 识别症状的诱发和缓解因素，帮助患者了解控制方法
- 评估症状的发展趋势，用关怀的语气提供预防建议

## ⚠️ **风险因素识别**
- 识别可能的危险因素和预警信号，用关切的语气提醒
- 评估疾病的严重程度和紧急程度，让患者了解重要性
- 分析并发症的风险，用温和的语气解释
- 识别需要紧急处理的情况，让患者有安全感

## ✅ **病史完整性评估**
- 评估当前病史信息的完整性，用鼓励的语气
- 识别缺失的关键信息，用温和的语气提醒
- 评估信息的可靠性和准确性，让患者了解重要性
- 确定需要进一步核实的内容，用关怀的语气指导

## ❓ **进一步询问建议**
- 建议需要进一步了解的关键信息，用鼓励的语气
- 提供具体的追问问题，让患者知道如何配合
- 指导如何收集更完整的病史，用温和的语气
- 建议需要补充的检查项目，用关怀的语气解释

## 🎯 **综合评估**
- 基于病史分析的综合评估，用患者能理解的语言
- 提供个性化的健康建议，让患者感到被关心
- 建议预防措施和监测计划，用温和的语气指导
- 指导后续的医疗决策，让患者有明确的方向

请用温柔亲切、专业负责的语气，让患者感到：
- 被理解和关心
- 获得专业的医疗指导
- 感到安心和希望
- 明确知道下一步该怎么做

请避免使用过于专业的医学术语，用患者能理解的语言表达。"""
        
        return prompt
    
    async def _assess_risk(self, user_input: str, context: str) -> Dict[str, Any]:
        """
        评估病史风险
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            
        返回：
            Dict[str, Any]: 风险评估结果
        """
        try:
            risk_prompt = f"""基于以下信息，请评估病史相关风险：

当前症状：{user_input}

对话历史：
{context}

请评估：
1. 急性风险等级（低/中/高）
2. 慢性风险等级（低/中/高）
3. 主要风险因素
4. 需要紧急关注的问题
5. 建议的监测频率

请用简洁的语言回答。"""
            
            risk_assessment = await self.caller(risk_prompt, self.model_config)
            
            return {
                "content": risk_assessment,
                "category": "病史风险评估",
                "urgency": "需要专业医生进一步评估"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 风险评估失败: {str(e)}")
            return {
                "content": "建议咨询专业医生进行详细风险评估",
                "category": "病史风险评估",
                "urgency": "需要专业医生进一步评估"
            }
    
    async def _generate_history_recommendations(self, analysis: str) -> Dict[str, Any]:
        """
        生成病史建议
        
        参数：
            analysis (str): 分析结果
            
        返回：
            Dict[str, Any]: 病史建议
        """
        try:
            recommendations_prompt = f"""基于以下病史分析结果，请提供建议：

分析结果：{analysis}

请提供：
1. 病史记录建议
2. 症状监测建议
3. 就医时机建议
4. 病史补充建议
5. 预防措施建议

请用简洁明了的语言回答。"""
            
            recommendations = await self.caller(recommendations_prompt, self.model_config)
            
            return {
                "content": recommendations,
                "category": "病史管理建议",
                "priority": "medium"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成病史建议失败: {str(e)}")
            return {
                "content": "建议咨询专业医生获取详细病史管理建议",
                "category": "病史管理建议",
                "priority": "medium"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的病史分析智能体，提供病史分析和风险评估",
            "capabilities": [
                "病史信息提取",
                "症状关联分析",
                "病史风险评估",
                "病史管理建议"
            ]
        }
