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
外科智能体 (SurgicalAgent)
=========================

专门处理外科相关的医疗咨询，包括手术建议和外科诊断。

主要功能：
1. 外科症状分析
2. 手术适应症评估
3. 外科诊断建议
4. 手术方案推荐

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent
from agents.medical.history import HistoryAgent


class SurgicalAgent(BaseAgent):
    """
    外科智能体
    
    专门处理外科相关的医疗咨询，包括：
    - 外科症状分析
    - 手术适应症评估
    - 外科诊断建议
    - 手术方案推荐
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化外科智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "surgical"
        self.name = "外科专家智能体"
        self.specialization = "外科"
        
        # 初始化病史智能体
        self.history_agent = HistoryAgent(model_config)
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Any:
        """
        执行外科诊断
        
        参数：
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Any: 外科诊断结果
        """
        try:
            # 记录输入参数
            self.logger.info(f"[{self.name}] 开始执行外科诊断")
            self.logger.info(f"[{self.name}] 输入参数 - 用户ID: {user_id}")
            self.logger.info(f"[{self.name}] 输入参数 - 症状描述: {user_input[:100]}...")
            self.logger.info(f"[{self.name}] 输入参数 - 用户信息: {user_info}")
            
            # 验证输入
            if not self.validate_input(user_input):
                self.logger.warning(f"[{self.name}] 输入验证失败")
                return "⚠️ 输入无效，请提供有效的症状描述。"
            
            # 获取对话历史
            context = self.get_context_from_memory(user_id)
            self.logger.info(f"[{self.name}] 获取对话历史: {context[:100] if context else '无'}...")
            
            # 验证用户信息
            if not user_info:
                self.logger.warning(f"[{self.name}] 用户 {user_id} 信息缺失")
                return "⚠️ 用户信息缺失，无法进行诊断。"
            
            # 获取用户病史
            self.logger.info(f"[{self.name}] 开始获取用户病史")
            history_result = await self.history_agent.safe_execute(user_input, user_id, user_info)
            self.logger.info(f"[{self.name}] 病史分析完成: {str(history_result)[:100]}...")
            
            # 构建外科诊断提示
            self.logger.info(f"[{self.name}] 开始构建诊断提示")
            diagnosis_prompt = self._build_diagnosis_prompt(user_input, context, history_result)
            self.logger.info(f"[{self.name}] 诊断提示构建完成，长度: {len(diagnosis_prompt)} 字符")
            
            # 调用LLM进行诊断
            self.logger.info(f"[{self.name}] 开始调用LLM进行诊断")
            diagnosis = await self.caller(diagnosis_prompt, self.model_config)
            self.logger.info(f"[{self.name}] LLM诊断完成，原始响应长度: {len(diagnosis)} 字符")
            
            # 过滤掉"Thinking"内容，只保留最终诊断结果
            diagnosis = self._filter_thinking_content(diagnosis)
            self.logger.info(f"[{self.name}] 过滤后诊断结果长度: {len(diagnosis)} 字符")
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, user_input, self.name, diagnosis)
            
            # 构建诊断结果
            self.logger.info(f"[{self.name}] 开始构建最终诊断结果")
            result = {
                "diagnosis": diagnosis,
                "specialization": self.specialization,
                "history_analysis": history_result,
                "surgical_assessment": await self._assess_surgical_need(user_input),
                "recommendations": await self._generate_surgical_recommendations(diagnosis)
            }
            
            self.logger.info(f"[{self.name}] 诊断完成")
            self.logger.info(f"[{self.name}] 输出结果 - 诊断内容长度: {len(diagnosis)} 字符")
            self.logger.info(f"[{self.name}] 输出结果 - 专业领域: {self.specialization}")
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 外科诊断错误：{str(e)}"
    
    def _build_diagnosis_prompt(self, user_input: str, context: str, history_result: Any) -> str:
        """
        构建外科诊断提示 - 医生人设优化版
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            history_result (Any): 病史分析结果
            
        返回：
            str: 诊断提示
        """
        prompt = f"""作为一位经验丰富的外科医生，请根据以下信息进行诊断：

患者症状描述：{user_input}

对话历史：
{context}

病史分析：
{history_result}

请以温柔亲切、专业负责的医生身份进行外科诊断，让患者感到被理解和关怀：

## 🔍 **症状分析**
- 详细分析患者的外科症状，用患者能理解的语言解释
- 评估症状的严重程度和紧急程度，给予患者安心感
- 分析症状的可能发展轨迹，提供预防建议

## 🩺 **可能病因分析**
- 分析可能的外科疾病原因，按可能性排序
- 结合病史分析，说明症状与既往病史的关联
- 用温和的语气解释，避免引起患者过度担心
- 解释每种可能性的依据，让患者了解病情

## 📊 **病史关联分析**
- 分析当前外科症状与既往病史的关联性
- 评估既往疾病对外科症状的影响
- 考虑既往手术史对当前症状的影响
- 提供基于病史的个性化外科建议

## 💡 **诊断建议**
- 基于症状的外科诊断建议
- 说明诊断的置信度，诚实但不过分担心
- 指出需要进一步确认的方面，给予患者希望

## ⚕️ **手术适应症评估**
- 详细评估是否需要手术治疗
- 用通俗易懂的语言解释手术的必要性
- 分析手术的紧急程度和时机选择
- 让患者了解手术的重要性和安全性

## 🧪 **检查建议**
- 建议进行的外科相关检查（按重要性排序）
- 用通俗易懂的语言解释每项检查的目的
- 提供检查的时机建议，让患者有明确安排
- 解释检查结果的意义

## 💊 **治疗建议**
- 外科治疗方案建议（手术和保守治疗）
- 详细说明每种治疗方案的优缺点
- 提供具体的生活方式调整建议
- 让患者知道如何配合治疗

## ⚠️ **注意事项**
- 手术前后的注意事项（具体可操作）
- 需要患者密切观察的症状
- 紧急情况下的处理建议
- 复诊时间安排，体现持续关怀

请用温柔亲切、专业负责的语气回答，让患者感到：
- 被理解和关心
- 获得专业的医疗指导
- 感到安心和希望
- 明确知道下一步该怎么做

请避免使用过于专业的医学术语，用患者能理解的语言表达。"""
        
        return prompt
    
    def _filter_thinking_content(self, content: str) -> str:
        """
        过滤掉"Thinking"内容，只保留最终诊断结果
        
        参数：
            content (str): 原始LLM响应内容
            
        返回：
            str: 过滤后的内容
        """
        try:
            if not content:
                return content
                
            # 如果包含Thinking标记，尝试提取最终响应
            if "Thinking" in content or "思考" in content:
                lines = content.split('\n')
                filtered_lines = []
                in_thinking = False
                in_final_response = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 检测Thinking开始
                    if "Thinking" in line or "思考" in line:
                        in_thinking = True
                        continue
                    
                    # 检测Final Response开始
                    if "Final Response" in line or "最终响应" in line or "最终回答" in line:
                        in_thinking = False
                        in_final_response = True
                        continue
                    
                    # 如果还在Thinking阶段，跳过
                    if in_thinking and not in_final_response:
                        continue
                    
                    # 保留最终响应内容
                    if in_final_response or not in_thinking:
                        filtered_lines.append(line)
                
                # 如果成功提取到最终响应，返回
                if filtered_lines:
                    return '\n'.join(filtered_lines)
            
            # 如果没有Thinking标记，直接返回原内容
            return content
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 过滤Thinking内容失败: {str(e)}")
            return content
    
    async def _assess_surgical_need(self, user_input: str) -> Dict[str, Any]:
        """
        评估手术需求 - 医生人设优化版
        
        参数：
            user_input (str): 用户输入
            
        返回：
            Dict[str, Any]: 手术评估结果
        """
        try:
            assessment_prompt = f"""作为一位经验丰富的外科医生，基于以下症状描述，请用温柔亲切的语气评估手术需求：

症状描述：{user_input}

请用关怀的语气评估以下方面：

## 🔍 **手术必要性评估**
- 是否需要手术治疗（是/否/需要进一步检查）
- 用患者能理解的语言解释评估依据
- 让患者了解手术的重要性和必要性

## ⏰ **手术紧急程度**
- 手术紧急程度（紧急/择期/观察）
- 详细说明紧急程度的原因
- 让患者了解时间安排的重要性

## ⚕️ **手术类型建议**
- 建议的手术类型和方式
- 用通俗易懂的语言解释手术过程
- 让患者了解手术的基本情况

## ⚠️ **手术风险等级**
- 手术风险等级评估
- 详细说明可能的风险和并发症
- 用温和的语气解释，避免引起过度担心

## 📋 **术前准备建议**
- 具体的术前准备事项
- 术前需要做的检查和准备
- 让患者知道如何配合术前准备

请用温柔关怀的语气，让患者感到被关心和指导。"""
            
            assessment = await self.caller(assessment_prompt, self.model_config)
            
            return {
                "content": assessment,
                "category": "手术适应症评估",
                "urgency": "需要专业医生进一步评估",
                "doctor_tone": "温柔亲切",
                "patient_care": "体现人文关怀"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 手术需求评估失败: {str(e)}")
            return {
                "content": "建议咨询专业外科医生进行详细评估，我会继续为您提供关怀和支持。",
                "category": "手术适应症评估",
                "urgency": "需要专业医生进一步评估",
                "doctor_tone": "温柔亲切"
            }
    
    async def _generate_surgical_recommendations(self, diagnosis: str) -> Dict[str, Any]:
        """
        生成外科治疗建议
        
        参数：
            diagnosis (str): 诊断结果
            
        返回：
            Dict[str, Any]: 外科治疗建议
        """
        try:
            recommendations_prompt = f"""基于以下诊断结果，请提供外科治疗建议：

诊断结果：{diagnosis}

请提供：
1. 手术治疗建议
2. 保守治疗选择
3. 术前准备事项
4. 术后康复指导
5. 复查时间安排
6. 紧急情况处理

请用简洁明了的语言回答。"""
            
            recommendations = await self.caller(recommendations_prompt, self.model_config)
            
            return {
                "content": recommendations,
                "category": "外科治疗建议",
                "priority": "high"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成外科治疗建议失败: {str(e)}")
            return {
                "content": "建议咨询专业外科医生获取详细治疗建议",
                "category": "外科治疗建议",
                "priority": "high"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的外科智能体，提供外科诊断和手术建议",
            "capabilities": [
                "外科症状分析",
                "手术适应症评估",
                "外科诊断建议",
                "手术方案推荐"
            ]
        }
