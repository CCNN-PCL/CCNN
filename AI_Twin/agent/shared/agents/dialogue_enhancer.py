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
对话增强器 (DialogueEnhancer)
============================

增强智能体交互逻辑，提供更好的用户体验。

主要功能：
1. 智能追问管理
2. 对话流程控制
3. 用户引导
4. 交互优化

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.medical.questioning_agent import QuestioningAgent


class DialogueEnhancer:
    """
    对话增强器
    
    提供增强的对话交互功能，包括：
    - 智能追问管理
    - 对话流程控制
    - 用户引导
    - 交互优化
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化对话增强器
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        self.model_config = model_config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化追问智能体
        self.questioning_agent = QuestioningAgent(model_config)
        
        # 对话状态管理
        self.conversation_states = {}
        
        self.logger.info(f"[{self.__class__.__name__}] 初始化完成")
    
    async def enhance_dialogue(self, user_input: str, user_id: str, 
                             agent_response: Any, user_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        增强对话交互
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            agent_response (Any): 智能体响应
            user_info (Dict, optional): 用户信息
            
        返回：
            Dict[str, Any]: 增强后的对话结果
        """
        try:
            # 分析是否需要追问
            questioning_result = await self.questioning_agent.safe_execute(user_input, user_id, user_info)
            
            # 检查对话状态
            conversation_state = self._get_conversation_state(user_id)
            
            # 决定是否需要追问
            should_question = self._should_ask_questions(questioning_result, conversation_state)
            
            # 构建增强响应
            enhanced_response = self._build_enhanced_response(
                agent_response, 
                questioning_result, 
                should_question,
                conversation_state
            )
            
            # 更新对话状态
            self._update_conversation_state(user_id, user_input, questioning_result)
            
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"[{self.__class__.__name__}] 对话增强失败: {str(e)}")
            return {
                "response": agent_response,
                "questions": [],
                "enhanced": False,
                "error": str(e)
            }
    
    def _get_conversation_state(self, user_id: str) -> Dict[str, Any]:
        """
        获取对话状态
        
        参数：
            user_id (str): 用户ID
            
        返回：
            Dict[str, Any]: 对话状态
        """
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = {
                "question_count": 0,
                "last_question_time": None,
                "symptom_completeness": 0,
                "conversation_phase": "initial",  # initial, questioning, diagnosis, follow_up
                "asked_questions": []
            }
        
        return self.conversation_states[user_id]
    
    def _should_ask_questions(self, questioning_result: Dict[str, Any], 
                            conversation_state: Dict[str, Any]) -> bool:
        """
        判断是否需要追问
        
        参数：
            questioning_result (Dict[str, Any]): 追问分析结果
            conversation_state (Dict[str, Any]): 对话状态
            
        返回：
            bool: 是否需要追问
        """
        # 如果信息已经足够完整，不需要追问
        if not questioning_result.get("follow_up_needed", False):
            return False
        
        # 如果已经问过太多问题，停止追问
        if conversation_state["question_count"] >= 3:
            return False
        
        # 如果症状信息不够完整，需要追问
        completeness_score = questioning_result.get("completeness_analysis", {}).get("completeness_score", 0)
        if completeness_score < 70:
            return True
        
        return False
    
    def _build_enhanced_response(self, agent_response: Any, questioning_result: Dict[str, Any], 
                               should_question: bool, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建增强响应
        
        参数：
            agent_response (Any): 原始智能体响应
            questioning_result (Dict[str, Any]): 追问分析结果
            should_question (bool): 是否需要追问
            conversation_state (Dict[str, Any]): 对话状态
            
        返回：
            Dict[str, Any]: 增强后的响应
        """
        enhanced_response = {
            "response": agent_response,
            "questions": [],
            "enhanced": should_question,
            "conversation_phase": conversation_state["conversation_phase"],
            "symptom_completeness": questioning_result.get("completeness_analysis", {}).get("completeness_score", 0)
        }
        
        if should_question:
            # 添加追问问题
            questions = questioning_result.get("questions", [])
            enhanced_response["questions"] = questions[:2]  # 限制问题数量
            
            # 添加追问提示
            enhanced_response["questioning_prompt"] = self._generate_questioning_prompt(questions)
            
            # 更新对话阶段
            enhanced_response["conversation_phase"] = "questioning"
        
        return enhanced_response
    
    def _generate_questioning_prompt(self, questions: List[str]) -> str:
        """
        生成追问提示
        
        参数：
            questions (List[str]): 追问问题列表
            
        返回：
            str: 追问提示
        """
        if not questions:
            return ""
        
        prompt = "为了更好地帮助您，我需要了解一些详细信息：\n\n"
        for i, question in enumerate(questions, 1):
            prompt += f"{i}. {question}\n"
        
        prompt += "\n请您详细回答这些问题，这样我就能为您提供更准确的建议。"
        
        return prompt
    
    def _update_conversation_state(self, user_id: str, user_input: str, 
                                 questioning_result: Dict[str, Any]):
        """
        更新对话状态
        
        参数：
            user_id (str): 用户ID
            user_input (str): 用户输入
            questioning_result (Dict[str, Any]): 追问分析结果
        """
        state = self.conversation_states[user_id]
        
        # 更新问题计数
        if questioning_result.get("follow_up_needed", False):
            state["question_count"] += 1
        
        # 更新症状完整性
        completeness_score = questioning_result.get("completeness_analysis", {}).get("completeness_score", 0)
        state["symptom_completeness"] = completeness_score
        
        # 更新对话阶段
        if completeness_score >= 80:
            state["conversation_phase"] = "diagnosis"
        elif state["question_count"] >= 3:
            state["conversation_phase"] = "follow_up"
        
        # 记录已问过的问题
        questions = questioning_result.get("questions", [])
        state["asked_questions"].extend(questions)
    
    def reset_conversation_state(self, user_id: str):
        """
        重置对话状态
        
        参数：
            user_id (str): 用户ID
        """
        if user_id in self.conversation_states:
            del self.conversation_states[user_id]
    
    def get_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """
        获取对话摘要
        
        参数：
            user_id (str): 用户ID
            
        返回：
            Dict[str, Any]: 对话摘要
        """
        if user_id not in self.conversation_states:
            return {"status": "no_conversation"}
        
        state = self.conversation_states[user_id]
        return {
            "status": "active",
            "question_count": state["question_count"],
            "symptom_completeness": state["symptom_completeness"],
            "conversation_phase": state["conversation_phase"],
            "total_questions_asked": len(state["asked_questions"])
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": "dialogue_enhancer",
            "name": "对话增强器",
            "description": "增强智能体交互逻辑，提供更好的用户体验",
            "capabilities": [
                "智能追问管理",
                "对话流程控制",
                "用户引导",
                "交互优化"
            ]
        }
