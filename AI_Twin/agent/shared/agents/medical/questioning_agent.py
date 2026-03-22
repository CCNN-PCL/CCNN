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
医生追问智能体 (QuestioningAgent)
================================

专门负责模拟医生追问，帮助用户准确描述症状。

主要功能：
1. 智能症状追问
2. 症状信息收集
3. 问诊流程引导
4. 症状完整性评估

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent


class QuestioningAgent(BaseAgent):
    """
    医生追问智能体
    
    专门负责模拟医生追问，包括：
    - 智能症状追问
    - 症状信息收集
    - 问诊流程引导
    - 症状完整性评估
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化医生追问智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "questioning"
        self.name = "医生追问智能体"
        self.specialization = "症状追问"
        
        # 症状追问模板
        self.question_templates = {
            "疼痛": [
                "疼痛的具体位置在哪里？",
                "疼痛是什么性质的？(刺痛、胀痛、隐痛等)",
                "疼痛的强度如何？(1-10分，10分最痛)",
                "疼痛是持续的还是间歇性的？",
                "什么情况下疼痛会加重或缓解？",
                "疼痛持续多长时间了？"
            ],
            "发热": [
                "体温大概多少度？",
                "发热是持续的还是间歇性的？",
                "发热时有没有其他症状？",
                "发热多长时间了？",
                "有没有寒战或出汗？"
            ],
            "消化系统": [
                "有没有恶心、呕吐？",
                "食欲如何？",
                "大便情况怎么样？",
                "有没有腹痛、腹胀？",
                "最近饮食有什么变化？"
            ],
            "呼吸系统": [
                "有没有咳嗽？",
                "咳嗽有痰吗？痰是什么颜色？",
                "有没有胸闷、气短？",
                "有没有呼吸困难？",
                "咳嗽多长时间了？"
            ],
            "神经系统": [
                "有没有头痛、头晕？",
                "有没有失眠或嗜睡？",
                "有没有记忆力减退？",
                "有没有肢体麻木或无力？",
                "有没有意识障碍？"
            ],
            "其他": [
                "请详细描述一下您的症状，包括症状的持续时间、强度等。",
                "症状是什么时候开始的？",
                "症状的严重程度如何？",
                "是否有其他伴随症状？"
            ]
        }
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Any:
        """
        执行医生追问
        
        参数：
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Any: 追问结果
        """
        try:
            # 记录输入参数
            self.logger.info(f"[{self.name}] 开始执行医生追问")
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
            
            # 分析症状信息完整性
            self.logger.info(f"[{self.name}] 开始分析症状信息完整性")
            completeness_analysis = await self._analyze_symptom_completeness(user_input, context)
            self.logger.info(f"[{self.name}] 症状完整性分析完成: {completeness_analysis}")
            
            # 生成追问问题
            self.logger.info(f"[{self.name}] 开始生成追问问题")
            questions = await self._generate_questions(user_input, context, completeness_analysis)
            self.logger.info(f"[{self.name}] 追问问题生成完成，问题数量: {len(questions)}")
            self.logger.info(f"[{self.name}] 生成的问题: {questions}")
            
            # 构建追问结果
            self.logger.info(f"[{self.name}] 开始构建追问结果")
            result = {
                "questions": questions,
                "completeness_analysis": completeness_analysis,
                "specialization": self.specialization,
                "follow_up_needed": len(questions) > 0
            }
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, user_input, self.name, str(result))
            
            self.logger.info(f"[{self.name}] 追问分析完成")
            self.logger.info(f"[{self.name}] 输出结果 - 问题数量: {len(questions)}")
            self.logger.info(f"[{self.name}] 输出结果 - 需要追问: {len(questions) > 0}")
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 追问分析错误：{str(e)}"
    
    async def _analyze_symptom_completeness(self, user_input: str, context: str) -> Dict[str, Any]:
        """
        分析症状信息完整性
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            
        返回：
            Dict[str, Any]: 完整性分析结果
        """
        try:
            analysis_prompt = f"""作为专业医生，请分析患者症状描述的完整性：

患者描述：{user_input}

对话历史：
{context}

请分析以下方面：
1. 症状描述是否清晰具体？
2. 是否缺少关键信息（如时间、强度、性质等）？
3. 是否需要了解伴随症状？
4. 是否需要了解诱发因素？
5. 是否需要了解缓解因素？
6. 症状严重程度如何？

请用JSON格式返回分析结果：
{{
    "symptom_clarity": "清晰/一般/模糊",
    "missing_info": ["缺少的关键信息列表"],
    "severity": "轻度/中度/重度",
    "urgency": "低/中/高",
    "completeness_score": 0-100,
    "needs_follow_up": true/false
}}"""
            
            analysis = await self.caller(analysis_prompt, self.model_config)
            
            # 尝试解析JSON，如果失败则返回默认值
            try:
                import json
                return json.loads(analysis)
            except:
                return {
                    "symptom_clarity": "一般",
                    "missing_info": ["症状持续时间", "症状强度"],
                    "severity": "中度",
                    "urgency": "中",
                    "completeness_score": 60,
                    "needs_follow_up": True
                }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 症状完整性分析失败: {str(e)}")
            return {
                "symptom_clarity": "一般",
                "missing_info": ["需要更多详细信息"],
                "severity": "中度",
                "urgency": "中",
                "completeness_score": 50,
                "needs_follow_up": True
            }
    
    async def _generate_questions(self, user_input: str, context: str, completeness_analysis: Dict[str, Any]) -> List[str]:
        """
        生成追问问题
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            completeness_analysis (Dict[str, Any]): 完整性分析结果
            
        返回：
            List[str]: 追问问题列表
        """
        try:
            # 如果信息已经足够完整，不需要追问
            if not completeness_analysis.get("needs_follow_up", True):
                return []
            
            # 识别主要症状类型
            symptom_type = await self._identify_symptom_type(user_input)
            self.logger.info(f"[{self.name}] 识别症状类型: {symptom_type}")
            
            # 生成针对性问题
            questions = await self._generate_targeted_questions(user_input, symptom_type, completeness_analysis)
            self.logger.info(f"[{self.name}] 生成问题: {questions}")
            
            return questions[:3]  # 限制问题数量，避免过度追问
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成追问问题失败: {str(e)}")
            return ["请详细描述一下您的症状，包括症状的持续时间、强度等。"]
    
    async def _identify_symptom_type(self, user_input: str) -> str:
        """
        识别症状类型
        
        参数：
            user_input (str): 用户输入
            
        返回：
            str: 症状类型
        """
        try:
            identification_prompt = f"""请识别以下症状描述的主要类型：

症状描述：{user_input}

请从以下类型中选择最匹配的：
- 疼痛
- 发热
- 消化系统
- 呼吸系统
- 神经系统
- 其他

只返回类型名称，不要其他内容。"""
            
            symptom_type = await self.caller(identification_prompt, self.model_config)
            return symptom_type.strip()
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 症状类型识别失败: {str(e)}")
            return "其他"
    
    async def _generate_targeted_questions(self, user_input: str, symptom_type: str, completeness_analysis: Dict[str, Any]) -> List[str]:
        """
        生成针对性问题
        
        参数：
            user_input (str): 用户输入
            symptom_type (str): 症状类型
            completeness_analysis (Dict[str, Any]): 完整性分析结果
            
        返回：
            List[str]: 针对性问题列表
        """
        try:
            # 获取基础问题模板
            base_questions = self.question_templates.get(symptom_type, self.question_templates["其他"])
            
            # 基于缺失信息生成问题
            missing_info = completeness_analysis.get("missing_info", [])
            
            if not missing_info:
                return base_questions[:2]
            
            # 生成针对性问题
            targeted_prompt = f"""作为专业医生，基于以下信息生成2-3个追问问题：

患者症状：{user_input}
症状类型：{symptom_type}
缺失信息：{missing_info}

请生成具体、有针对性的问题，帮助收集缺失信息。
每个问题要简洁明了，便于患者回答。

请直接返回问题列表，每行一个问题："""
            
            questions_text = await self.caller(targeted_prompt, self.model_config)
            
            # 过滤掉"Thinking"内容，只保留实际问题
            if "Thinking" in questions_text or "思考" in questions_text:
                # 如果包含Thinking标记，尝试提取实际问题
                lines = questions_text.split('\n')
                questions = []
                in_thinking = False
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    # 跳过Thinking内容
                    if "Thinking" in line or "思考" in line:
                        in_thinking = True
                        continue
                    if in_thinking and (line.endswith('？') or line.endswith('?') or '。' in line):
                        # 如果是思考内容中的句子，跳过
                        if len(line) > 30 and not line[0].isdigit():
                            continue
                    # 保留以数字开头的问题或以问号结尾的问题
                    if line[0].isdigit() or line.endswith('？') or line.endswith('?'):
                        # 移除数字编号
                        cleaned = line.lstrip('0123456789.、。 ')
                        if cleaned and (cleaned.endswith('？') or cleaned.endswith('?')):
                            questions.append(cleaned)
            else:
                # 正常处理
                questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            
            # 如果LLM调用失败或返回空问题，使用基础模板
            if not questions:
                self.logger.warning(f"[{self.name}] LLM调用失败或无法提取问题，使用基础模板")
                return base_questions[:2]
            
            return questions[:3]  # 最多返回3个问题
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成针对性问题失败: {str(e)}")
            return self.question_templates.get(symptom_type, ["请详细描述一下您的症状。"])[:2]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "专业的医生追问智能体，帮助收集完整的症状信息",
            "capabilities": [
                "智能症状追问",
                "症状信息收集",
                "问诊流程引导",
                "症状完整性评估"
            ]
        }
