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
多模态对话增强器 (MultimodalDialogueEnhancer)
==========================================

利用多模态医疗大模型增强对话交互逻辑。

主要功能：
1. 多模态症状分析
2. 智能追问管理
3. 图像理解集成
4. 综合诊断支持

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional, List, Union
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.medical.multimodal_questioning_agent import MultimodalQuestioningAgent


class MultimodalDialogueEnhancer:
    """
    多模态对话增强器
    
    利用多模态医疗大模型提供增强的对话交互功能，包括：
    - 多模态症状分析
    - 智能追问管理
    - 图像理解集成
    - 综合诊断支持
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化多模态对话增强器
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        self.model_config = model_config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 初始化多模态追问智能体
        self.multimodal_questioning_agent = MultimodalQuestioningAgent(model_config)
        
        # 对话状态管理
        self.conversation_states = {}
        
        # 多模态支持的症状类型
        self.multimodal_symptom_types = [
            "疼痛分析", "皮肤症状", "眼部症状", "消化系统", 
            "呼吸系统", "神经系统", "症状描述"
        ]
        
        self.logger.info(f"[{self.__class__.__name__}] 初始化完成")
    
    async def enhance_multimodal_dialogue(self, user_input: str, user_id: str, 
                                        agent_response: Any, user_info: Optional[Dict] = None,
                                        images: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        增强多模态对话交互
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            agent_response (Any): 智能体响应
            user_info (Dict, optional): 用户信息
            images (List[Any], optional): 图像数据列表
            
        返回：
            Dict[str, Any]: 增强后的对话结果
        """
        try:
            # 分析是否需要多模态追问
            multimodal_result = await self.multimodal_questioning_agent.safe_execute(
                user_input, user_id, user_info, images
            )
            
            # 检查对话状态
            conversation_state = self._get_conversation_state(user_id)
            
            # 决定是否需要追问
            should_question = self._should_ask_multimodal_questions(
                multimodal_result, conversation_state, images
            )
            
            # 构建增强响应
            enhanced_response = self._build_multimodal_enhanced_response(
                agent_response, 
                multimodal_result, 
                should_question,
                conversation_state,
                images
            )
            
            # 更新对话状态
            self._update_conversation_state(user_id, user_input, multimodal_result, images)
            
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"[{self.__class__.__name__}] 多模态对话增强失败: {str(e)}")
            return {
                "response": agent_response,
                "questions": [],
                "enhanced": False,
                "multimodal": False,
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
                "conversation_phase": "initial",
                "asked_questions": [],
                "has_images": False,
                "multimodal_analysis_count": 0
            }
        
        return self.conversation_states[user_id]
    
    def _should_ask_multimodal_questions(self, multimodal_result: Dict[str, Any], 
                                       conversation_state: Dict[str, Any], 
                                       images: Optional[List[Any]]) -> bool:
        """
        判断是否需要多模态追问
        
        参数：
            multimodal_result (Dict[str, Any]): 多模态分析结果
            conversation_state (Dict[str, Any]): 对话状态
            images (List[Any], optional): 图像数据
            
        返回：
            bool: 是否需要追问
        """
        # 如果信息已经足够完整，不需要追问
        if not multimodal_result.get("follow_up_needed", False):
            return False
        
        # 如果已经问过太多问题，停止追问
        if conversation_state["question_count"] >= 3:
            return False
        
        # 如果有图像但分析置信度低，需要追问
        if images and len(images) > 0:
            confidence = multimodal_result.get("multimodal_analysis", {}).get("confidence", 0)
            if confidence < 0.7:
                return True
        
        # 如果症状信息不够完整，需要追问
        completeness_score = multimodal_result.get("multimodal_analysis", {}).get("confidence", 0)
        if completeness_score < 70:
            return True
        
        return False
    
    def _build_multimodal_enhanced_response(self, agent_response: Any, 
                                          multimodal_result: Dict[str, Any], 
                                          should_question: bool,
                                          conversation_state: Dict[str, Any],
                                          images: Optional[List[Any]]) -> Dict[str, Any]:
        """
        构建多模态增强响应
        
        参数：
            agent_response (Any): 原始智能体响应
            multimodal_result (Dict[str, Any]): 多模态分析结果
            should_question (bool): 是否需要追问
            conversation_state (Dict[str, Any]): 对话状态
            images (List[Any], optional): 图像数据
            
        返回：
            Dict[str, Any]: 增强后的响应
        """
        enhanced_response = {
            "response": agent_response,
            "questions": [],
            "enhanced": should_question,
            "multimodal": images is not None and len(images) > 0,
            "conversation_phase": conversation_state["conversation_phase"],
            "symptom_completeness": multimodal_result.get("multimodal_analysis", {}).get("confidence", 0),
            "symptom_type": multimodal_result.get("symptom_type", "未知"),
            "multimodal_analysis": multimodal_result.get("multimodal_analysis", {})
        }
        
        if should_question:
            # 添加追问问题
            questions = multimodal_result.get("questions", [])
            enhanced_response["questions"] = questions[:2]  # 限制问题数量
            
            # 添加多模态追问提示
            enhanced_response["multimodal_questioning_prompt"] = self._generate_multimodal_questioning_prompt(
                questions, images, multimodal_result.get("symptom_type", "未知")
            )
            
            # 更新对话阶段
            enhanced_response["conversation_phase"] = "multimodal_questioning"
        
        return enhanced_response
    
    def _generate_multimodal_questioning_prompt(self, questions: List[str], 
                                              images: Optional[List[Any]], 
                                              symptom_type: str) -> str:
        """
        生成多模态追问提示
        
        参数：
            questions (List[str]): 追问问题列表
            images (List[Any], optional): 图像数据
            symptom_type (str): 症状类型
            
        返回：
            str: 多模态追问提示
        """
        if not questions:
            return ""
        
        prompt = f"为了更好地帮助您，我需要了解一些详细信息：\n\n"
        
        # 根据症状类型添加特殊提示
        if symptom_type in ["皮肤症状", "眼部症状"] and images:
            prompt += "💡 基于您上传的图像，我注意到一些特征，请详细回答以下问题：\n\n"
        elif images:
            prompt += "💡 结合您的描述和图像，我需要了解以下详细信息：\n\n"
        else:
            prompt += "💡 为了更好地分析您的症状，请详细回答以下问题：\n\n"
        
        for i, question in enumerate(questions, 1):
            prompt += f"{i}. {question}\n"
        
        # 添加图像相关提示
        if images and len(images) > 0:
            prompt += f"\n📷 如果您有其他角度的照片或更清晰的图像，也请一并上传，这将帮助我进行更准确的分析。"
        
        prompt += f"\n\n请您详细回答这些问题，这样我就能为您提供更准确的医疗建议。"
        
        return prompt
    
    def _update_conversation_state(self, user_id: str, user_input: str, 
                                 multimodal_result: Dict[str, Any], 
                                 images: Optional[List[Any]]):
        """
        更新对话状态
        
        参数：
            user_id (str): 用户ID
            user_input (str): 用户输入
            multimodal_result (Dict[str, Any]): 多模态分析结果
            images (List[Any], optional): 图像数据
        """
        state = self.conversation_states[user_id]
        
        # 更新问题计数
        if multimodal_result.get("follow_up_needed", False):
            state["question_count"] += 1
        
        # 更新症状完整性
        confidence = multimodal_result.get("multimodal_analysis", {}).get("confidence", 0)
        state["symptom_completeness"] = confidence
        
        # 更新图像状态
        state["has_images"] = images is not None and len(images) > 0
        
        # 更新多模态分析计数
        if state["has_images"]:
            state["multimodal_analysis_count"] += 1
        
        # 更新对话阶段
        if confidence >= 80:
            state["conversation_phase"] = "multimodal_diagnosis"
        elif state["question_count"] >= 3:
            state["conversation_phase"] = "multimodal_follow_up"
        elif state["has_images"]:
            state["conversation_phase"] = "multimodal_analysis"
        
        # 记录已问过的问题
        questions = multimodal_result.get("questions", [])
        state["asked_questions"].extend(questions)
    
    def reset_conversation_state(self, user_id: str):
        """
        重置对话状态
        
        参数：
            user_id (str): 用户ID
        """
        if user_id in self.conversation_states:
            del self.conversation_states[user_id]
    
    def get_multimodal_conversation_summary(self, user_id: str) -> Dict[str, Any]:
        """
        获取多模态对话摘要
        
        参数：
            user_id (str): 用户ID
            
        返回：
            Dict[str, Any]: 多模态对话摘要
        """
        if user_id not in self.conversation_states:
            return {"status": "no_conversation"}
        
        state = self.conversation_states[user_id]
        return {
            "status": "active",
            "question_count": state["question_count"],
            "symptom_completeness": state["symptom_completeness"],
            "conversation_phase": state["conversation_phase"],
            "total_questions_asked": len(state["asked_questions"]),
            "has_images": state["has_images"],
            "multimodal_analysis_count": state["multimodal_analysis_count"]
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": "multimodal_dialogue_enhancer",
            "name": "多模态对话增强器",
            "description": "利用多模态医疗大模型增强对话交互逻辑",
            "capabilities": [
                "多模态症状分析",
                "智能追问管理",
                "图像理解集成",
                "综合诊断支持"
            ],
            "supported_modalities": ["text", "image"],
            "model_type": "multimodal_medical"
        }
