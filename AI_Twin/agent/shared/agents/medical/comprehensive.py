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
综合智能体 (ComprehensiveAgent)
==============================

专门处理综合性的医疗分析和建议。

主要功能：
1. 综合症状分析
2. 多角度诊断
3. 综合治疗建议
4. 整体健康评估

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent


class ComprehensiveAgent(BaseAgent):
    """
    综合智能体
    
    专门处理综合性的医疗分析，包括：
    - 综合症状分析
    - 多角度诊断
    - 综合治疗建议
    - 整体健康评估
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化综合智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "comprehensive"
        self.name = "综合分析智能体"
        self.specialization = "综合医疗分析"
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Any:
        """
        执行综合分析
        
        参数：
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Any: 综合分析结果
        """
        try:
            # 验证输入
            if not self.validate_input(user_input):
                return "⚠️ 输入无效，请提供有效的症状描述。"
            
            # 获取对话历史
            context = self.get_context_from_memory(user_id)
            
            # 构建综合分析提示
            analysis_prompt = self._build_analysis_prompt(user_input, context, user_info)
            
            # 调用LLM进行分析
            analysis = await self.caller(analysis_prompt, self.model_config)
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, user_input, self.name, analysis)
            
            # 构建分析结果
            result = {
                "analysis": analysis,
                "specialization": self.specialization,
                "comprehensive_assessment": await self._comprehensive_assessment(user_input, context),
                "health_recommendations": await self._generate_health_recommendations(analysis)
            }
            
            self.logger.info(f"[{self.name}] 综合分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 综合分析错误：{str(e)}"
    
    def _build_analysis_prompt(self, user_input: str, context: str, user_info: Optional[Dict]) -> str:
        """
        构建综合分析提示
        
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
- 生活习惯：{user_info.get('lifestyle', '无')}
"""
        
        prompt = f"""作为专业的综合医疗分析专家，请对以下情况进行全面分析：

患者症状描述：{user_input}

对话历史：
{context}
{user_info_str}

请以资深医疗专家的身份，用全面、系统的视角进行分析：

## 🔍 **症状综合分析**
- 从多个医学角度深入分析症状表现
- 评估症状的严重程度和紧急程度
- 分析症状之间的关联性和发展规律
- 识别关键症状和次要症状

## 🎯 **可能病因分析**
- 基于症状和病史分析可能的疾病原因
- 按医学概率从高到低排序可能病因
- 详细解释每种可能性的医学依据
- 分析病因的复杂性和多因素性

## ⚕️ **系统影响评估**
- 评估症状对各身体系统的影响
- 分析系统间的相互影响关系
- 识别潜在的系统性风险
- 评估整体健康状况

## 🏥 **综合诊断建议**
- 基于所有信息的综合诊断建议
- 说明诊断的置信度和不确定性
- 指出需要进一步确认的关键点
- 提供诊断的优先级排序

## 💊 **治疗策略建议**
- 制定个性化的综合治疗方案
- 药物治疗建议（如有需要）
- 非药物治疗建议
- 生活方式和饮食调整建议

## 🛡️ **预防措施建议**
- 针对性的预防措施
- 健康管理和监测建议
- 风险因素控制建议
- 长期健康维护策略

## 📊 **监测计划建议**
- 制定详细的监测计划
- 确定监测指标和频率
- 提供自我监测指导
- 安排定期复诊计划

## 🌟 **生活质量建议**
- 改善生活质量的实用建议
- 心理调节和情绪管理
- 社会支持和家庭关怀
- 康复和恢复指导

## ❓ **后续建议**
- 是否需要进一步追问症状细节
- 建议患者补充的关键信息
- 下次咨询的重点和方向
- 紧急情况下的处理建议

请用专业但易懂的语言回答，体现医疗专家的专业性和人文关怀，让患者感受到被理解和被关心。"""
        
        return prompt
    
    async def _comprehensive_assessment(self, user_input: str, context: str) -> Dict[str, Any]:
        """
        进行综合评估
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            
        返回：
            Dict[str, Any]: 综合评估结果
        """
        try:
            assessment_prompt = f"""基于以下信息，请进行综合健康评估：

症状描述：{user_input}

对话历史：
{context}

请评估：
1. 整体健康状况（优秀/良好/一般/较差）
2. 主要健康风险
3. 需要关注的系统
4. 生活方式影响
5. 心理状态影响
6. 社会环境影响
7. 综合健康建议

请用简洁明了的语言回答。"""
            
            assessment = await self.caller(assessment_prompt, self.model_config)
            
            return {
                "content": assessment,
                "category": "综合健康评估",
                "priority": "high"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 综合评估失败: {str(e)}")
            return {
                "content": "建议咨询专业医生进行详细综合评估",
                "category": "综合健康评估",
                "priority": "high"
            }
    
    async def _generate_health_recommendations(self, analysis: str) -> Dict[str, Any]:
        """
        生成健康建议
        
        参数：
            analysis (str): 分析结果
            
        返回：
            Dict[str, Any]: 健康建议
        """
        try:
            recommendations_prompt = f"""基于以下综合分析结果，请提供健康建议：

分析结果：{analysis}

请提供：
1. 生活方式建议
2. 饮食建议
3. 运动建议
4. 心理调节建议
5. 环境改善建议
6. 定期检查建议
7. 紧急情况处理建议

请用简洁明了的语言回答。"""
            
            recommendations = await self.caller(recommendations_prompt, self.model_config)
            
            return {
                "content": recommendations,
                "category": "综合健康建议",
                "priority": "medium"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成健康建议失败: {str(e)}")
            return {
                "content": "建议咨询专业医生获取详细健康建议",
                "category": "综合健康建议",
                "priority": "medium"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的综合智能体，提供全面的医疗分析和健康建议",
            "capabilities": [
                "综合症状分析",
                "多角度诊断",
                "综合治疗建议",
                "整体健康评估"
            ]
        }
