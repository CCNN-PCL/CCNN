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
总结智能体 (SummaryAgent)
========================

专门处理多个智能体结果的汇总和整合。

主要功能：
1. 多智能体结果汇总
2. 结果整合分析
3. 综合报告生成
4. 优先级排序

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent


class SummaryAgent(BaseAgent):
    """
    总结智能体
    
    专门处理多个智能体结果的汇总和整合，包括：
    - 多智能体结果汇总
    - 结果整合分析
    - 综合报告生成
    - 优先级排序
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化总结智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "summary"
        self.name = "综合总结智能体"
        self.specialization = "结果汇总"
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, expert_results: Dict[str, Any], user_id: str, user_info: Optional[Dict] = None) -> str:
        """
        执行结果汇总
        
        参数：
            expert_results (Dict[str, Any]): 各专家智能体的结果
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            str: 汇总结果
        """
        try:
            # 验证输入
            if not expert_results:
                return "⚠️ 没有可汇总的结果。"
            
            # 获取对话历史
            context = self.get_context_from_memory(user_id)
            
            # 构建汇总提示
            summary_prompt = self._build_summary_prompt(expert_results, context)
            
            # 调用LLM进行汇总
            summary = await self.caller(summary_prompt, self.model_config)
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, f"汇总{len(expert_results)}个专家结果", self.name, summary)
            
            self.logger.info(f"[{self.name}] 汇总完成，处理了{len(expert_results)}个专家结果")
            return summary
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 结果汇总错误：{str(e)}"
    
    def _build_summary_prompt(self, expert_results: Dict[str, Any], context: str) -> str:
        """
        构建汇总提示 - 医生人设优化版
        
        参数：
            expert_results (Dict[str, Any]): 专家结果
            context (str): 对话上下文
            
        返回：
            str: 汇总提示
        """
        # 格式化专家结果
        results_text = ""
        for expert_name, result in expert_results.items():
            results_text += f"\n{expert_name}的结果：\n"
            if isinstance(result, dict):
                for key, value in result.items():
                    results_text += f"- {key}: {value}\n"
            else:
                results_text += f"{result}\n"
        
        prompt = f"""作为一位经验丰富的医疗专家，请汇总以下多个专家的分析结果，用温柔亲切的语气为患者提供综合报告：

对话上下文：
{context}

专家分析结果：
{results_text}

请以温柔关怀的医生身份，提供综合汇总报告，让患者感到被理解和关心：

## 🔍 **主要发现**
- 总结各专家的主要发现，用患者能理解的语言
- 突出重要的诊断信息和建议
- 让患者了解病情的整体情况

## 🤝 **专家意见一致性**
- 分析各专家意见的一致性
- 用温和的语气解释专家们的共识
- 让患者对诊断结果更有信心

## 📊 **差异分析**
- 如有差异，用关怀的语气分析差异原因
- 解释不同观点的合理性
- 让患者了解不同治疗选择的考虑

## 💡 **综合诊断**
- 基于所有专家意见的综合诊断
- 用通俗易懂的语言解释诊断结果
- 让患者明确了解自己的病情

## 📋 **优先级排序**
- 按重要性排序的建议，让患者知道重点
- 用温和的语气解释每个建议的重要性
- 让患者有明确的行动方向

## 🚀 **下一步行动**
- 建议的下一步行动，具体可操作
- 用鼓励的语气指导患者
- 让患者知道如何配合治疗

## ⚠️ **注意事项**
- 需要特别注意的事项，用关切的语气提醒
- 让患者了解可能的风险和预防措施
- 提供紧急情况下的处理建议

请用温柔亲切、专业负责的语气，让患者感到：
- 被理解和关心
- 获得专业的医疗指导
- 感到安心和希望
- 明确知道下一步该怎么做

请避免使用过于专业的医学术语，用患者能理解的语言表达。"""
        
        return prompt
    
    async def generate_priority_list(self, expert_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成优先级列表
        
        参数：
            expert_results (Dict[str, Any]): 专家结果
            
        返回：
            List[Dict[str, Any]]: 优先级列表
        """
        try:
            priority_prompt = f"""基于以下专家分析结果，请按优先级排序：

专家分析结果：
{expert_results}

请按以下格式输出优先级列表：
1. [高优先级] 具体建议
2. [中优先级] 具体建议
3. [低优先级] 具体建议

请用简洁明了的语言回答。"""
            
            priority_text = await self.caller(priority_prompt, self.model_config)
            
            # 解析优先级列表
            priorities = []
            lines = priority_text.split('\n')
            for line in lines:
                if line.strip() and '[' in line and ']' in line:
                    priority_level = line.split('[')[1].split(']')[0]
                    content = line.split(']')[1].strip()
                    priorities.append({
                        "level": priority_level,
                        "content": content,
                        "order": len(priorities) + 1
                    })
            
            return priorities
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成优先级列表失败: {str(e)}")
            return [{
                "level": "中优先级",
                "content": "建议咨询专业医生获取详细建议",
                "order": 1
            }]
    
    async def generate_action_plan(self, expert_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成行动计划
        
        参数：
            expert_results (Dict[str, Any]): 专家结果
            
        返回：
            Dict[str, Any]: 行动计划
        """
        try:
            action_prompt = f"""基于以下专家分析结果，请制定详细的行动计划：

专家分析结果：
{expert_results}

请制定行动计划，包括：
1. 立即行动（24小时内）
2. 短期行动（1-7天）
3. 中期行动（1-4周）
4. 长期行动（1-3个月）
5. 监测计划
6. 复查安排

请用简洁明了的语言回答。"""
            
            action_plan = await self.caller(action_prompt, self.model_config)
            
            return {
                "content": action_plan,
                "category": "综合行动计划",
                "priority": "high"
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成行动计划失败: {str(e)}")
            return {
                "content": "建议咨询专业医生制定详细行动计划",
                "category": "综合行动计划",
                "priority": "high"
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的总结智能体，提供多专家结果的汇总和整合",
            "capabilities": [
                "多智能体结果汇总",
                "结果整合分析",
                "综合报告生成",
                "优先级排序"
            ]
        }
