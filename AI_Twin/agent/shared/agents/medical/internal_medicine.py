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
内科智能体 (InternalMedicineAgent)
=================================

基于用户病历和当前症状，提供内科诊断和建议。

主要功能：
1. 内科症状分析
2. 病史关联分析
3. 内科诊断建议
4. 治疗方案推荐

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


class InternalMedicineAgent(BaseAgent):
    """
    内科智能体
    
    专门处理内科相关的医疗咨询，包括：
    - 内科症状分析
    - 病史关联分析
    - 内科诊断建议
    - 治疗方案推荐
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化内科智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "internal_medicine"
        self.name = "内科专家智能体"
        self.specialization = "内科"
        
        # 初始化病史智能体
        self.history_agent = HistoryAgent(model_config)
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Any:
        """
        执行内科诊断
        
        参数：
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Any: 内科诊断结果
        """
        try:
            # 记录输入参数
            self.logger.info(f"[{self.name}] 开始执行内科诊断")
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
            
            # 构建内科诊断提示
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
                "recommendations": await self._generate_recommendations(diagnosis)
            }
            
            self.logger.info(f"[{self.name}] 诊断完成")
            self.logger.info(f"[{self.name}] 输出结果 - 诊断内容长度: {len(diagnosis)} 字符")
            self.logger.info(f"[{self.name}] 输出结果 - 专业领域: {self.specialization}")
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 内科诊断错误：{str(e)}"
    
    def _build_diagnosis_prompt(self, user_input: str, context: str, history_result: Any) -> str:
        """
        构建内科诊断提示 - 医生人设优化版
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            history_result (Any): 病史分析结果
            
        返回：
            str: 诊断提示
        """
        prompt = f"""作为一位经验丰富的内科医生，请根据以下信息进行诊断：

患者症状描述：{user_input}

对话历史：
{context}

病史分析：
{history_result}

请以温柔亲切、专业负责的医生身份进行诊断，让患者感到被理解和关怀：

## 🩺 **症状分析**
- 详细分析患者的症状表现，**尤其是检查结果数据**（如血糖、血压、化验指标等数值）
- **对于用户提供的检查数据，必须详细说明：**
  - 具体数值和参考范围
  - 数据的时间线和发展趋势（如血糖从 5.8 → 6.0 → 6.4 的变化）
  - 数据的严重程度评估
- 用患者能理解的语言解释这些数据的医学意义
- 评估症状的严重程度和紧急程度，给予患者安心感
- 分析症状的可能发展轨迹，提供预防建议

## 🔍 **可能病因分析**
- 基于症状和病史分析可能的疾病原因
- 按可能性从高到低排序，并解释每种可能性的依据
- 用温和的语气解释，避免引起患者过度担心

## 💡 **诊断建议**
- 基于所有信息的综合诊断建议
- 说明诊断的置信度，诚实但不过分担心
- 指出需要进一步确认的方面，给予患者希望

## 🧪 **检查建议**
- 建议进行的检查项目（按重要性排序）
- 用通俗易懂的语言解释每项检查的目的和必要性
- 提供检查的时机建议，让患者有明确的时间安排

## 💊 **治疗建议**
- 提供初步的治疗方案，包括药物和非药物治疗
- 详细说明药物治疗的用法用量和注意事项
- 提供具体的生活方式调整建议，让患者知道如何配合治疗

## ⚠️ **注意事项**
- 需要患者密切观察的症状，用关切的语气提醒
- 紧急情况下的处理建议，让患者有安全感
- 复诊时间安排，体现对患者的持续关怀

## 🤝 **后续建议**
- 是否需要进一步追问症状细节
- 建议患者补充的信息，用鼓励的语气
- 下次咨询的重点，让患者有期待感

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
    
    async def _generate_recommendations(self, diagnosis: str) -> Dict[str, Any]:
        """
        生成治疗建议 - 医生人设优化版
        
        参数：
            diagnosis (str): 诊断结果
            
        返回：
            Dict[str, Any]: 治疗建议
        """
        try:
            recommendations_prompt = f"""作为一位经验丰富的内科医生，基于以下诊断结果，请提供温暖详细的治疗建议：

诊断结果：{diagnosis}

请用温柔亲切的语气提供以下建议：

## 💊 **药物治疗建议**
- 详细说明每种药物的作用机制（用患者能理解的语言）
- 具体的用法用量和服用时间
- 可能的副作用和应对方法
- 用药期间的注意事项

**📊 病史关联分析**
- 分析当前症状与既往病史的关联性
- 评估既往疾病对当前症状的影响
- 提供基于病史的个性化建议

## 🏃‍♂️ **生活方式建议**
- 饮食调整建议（具体到食物种类和烹饪方法）
- 运动锻炼建议（适合的运动类型和强度）
- 作息时间调整建议
- 心理调节和压力管理建议

## 📅 **复查时间安排**
- 具体的复查时间节点
- 每次复查需要检查的项目
- 复查前的准备工作
- 复查结果的意义解释

## 🚨 **紧急情况处理**
- 需要立即就医的症状表现
- 紧急情况下的自救措施
- 紧急联系方式
- 就医时的注意事项

## 🛡️ **预防措施**
- 日常预防措施（具体可操作）
- 定期健康检查建议
- 风险因素的控制方法
- 长期健康管理计划

请用温暖关怀的语气，让患者感到被关心和指导，同时提供具体可操作的建议。"""
            
            recommendations = await self.caller(recommendations_prompt, self.model_config)
            
            return {
                "content": recommendations,
                "category": "内科治疗建议",
                "priority": "medium",
                "doctor_tone": "温柔亲切",
                "patient_care": "体现人文关怀"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成治疗建议失败: {str(e)}")
            return {
                "content": "建议咨询专业医生获取详细治疗建议，我会继续为您提供关怀和支持。",
                "category": "内科治疗建议",
                "priority": "medium",
                "doctor_tone": "温柔亲切"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的内科智能体，提供内科诊断和治疗建议",
            "capabilities": [
                "内科症状分析",
                "病史关联分析",
                "内科诊断建议",
                "治疗方案推荐"
            ],
            "dependencies": ["HistoryAgent"]
        }
