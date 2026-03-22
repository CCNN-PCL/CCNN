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
经验丰富的医生智能体 (CybertwinAgent)
====================================

作为一位经验丰富的医生，以温柔亲切的语气与患者交流，
通过多轮追问收集完整信息，提供专业且耐心的医疗建议。

主要功能：
1. 医生式问诊：模拟真实医生的问诊流程
2. 多轮追问：通过1轮追问收集完整症状信息
3. 数据分析：分析患者病历、影像、体检报告等数据
4. 专业诊断：基于完整信息提供专业医疗建议
5. 温柔关怀：以亲切耐心的语气与患者交流

作者: Q开发团队
版本: 2.0 - 医生人设优化版
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

# 导入基础智能体类
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent

# 为了向后兼容，保留全局logging使用
# 但建议在需要的地方使用 self.logger 而不是 logging
from agents.medical.internal_medicine import InternalMedicineAgent
from agents.medical.surgical import SurgicalAgent
from agents.medical.summary import SummaryAgent
from agents.medical.triage import TriageAgent
from agents.image.coordinator import ImageAnalysisCoordinator
from agents.llm.intent_recognition import IntentRecognition, IntentType


@dataclass
class CybertwinConfig:
    """经验丰富的医生智能体配置"""
    model_config: Dict[str, Any]
    enable_auth: bool = True
    enable_audit: bool = True
    max_context_length: int = 4000
    intent_threshold: float = 0.7
    max_questioning_rounds: int = 1  # 最大追问轮数（用户回答追问的次数）
    min_questioning_rounds: int = 1  # 最小追问轮数
    doctor_persona: str = "温柔亲切的专业医生"  # 医生人设
    enable_data_analysis_notification: bool = True  # 启用数据分析通知


class CybertwinAgent(BaseAgent):
    """
    经验丰富的医生智能体
    
    作为一位经验丰富的医生，以温柔亲切的语气与患者交流：
    1. 医生式问诊：模拟真实医生的问诊流程
    2. 多轮追问：通过1轮追问收集完整症状信息
    3. 数据分析：分析患者病历、影像、体检报告等数据
    4. 专业诊断：基于完整信息提供专业医疗建议
    5. 温柔关怀：以亲切耐心的语气与患者交流
    """
    
    def __init__(self, config: CybertwinConfig):
        """
        初始化经验丰富的医生智能体
        
        参数：
            config (CybertwinConfig): 智能体配置
        """
        super().__init__(config.model_config)
        self.config = config
        self.agent_id = "cybertwin"
        self.name = "经验丰富的医生"
        
        # 初始化子智能体
        self._init_sub_agents()
        
        # 初始化认证授权系统
        self._init_auth_system()
        
        # 初始化意图识别系统
        self._init_intent_recognition()
        
        # 初始化追问系统
        self._init_questioning_system()
        
        # 影像分析协调器（延迟初始化）
        self.image_coordinator = None
        
        # 对话状态管理
        self.conversation_states = {}
        
        logging.info(f"[{self.name}] 初始化完成")
    
    def _init_sub_agents(self):
        """初始化子智能体"""
        try:
            # 导入模型配置
            from shared.config.model_config import get_config
            
            # 医疗智能体使用huatuogpt模型
            medical_model_config = get_config("huatuo").to_dict()
            
            self.internal_medicine_agent = InternalMedicineAgent(medical_model_config)
            self.surgical_agent = SurgicalAgent(medical_model_config)
            self.summary_agent = SummaryAgent(medical_model_config)
            self.triage_agent = TriageAgent(medical_model_config)
            logging.info(f"[{self.name}] 子智能体初始化完成")
        except Exception as e:
            logging.error(f"[{self.name}] 子智能体初始化失败: {str(e)}")
            raise
    
    def _init_auth_system(self):
        """初始化认证授权系统"""
        if not self.config.enable_auth:
            self.authz_manager = None
            self.audit_manager = None
            logging.info(f"[{self.name}] 认证授权系统已禁用")
            return
        
        try:
            from auth_manager import authz_manager, audit_manager
            self.authz_manager = authz_manager
            self.audit_manager = audit_manager
            logging.info(f"[{self.name}] 认证授权系统初始化完成")
        except ImportError as e:
            logging.warning(f"[{self.name}] 认证授权模块未找到: {str(e)}")
            self.authz_manager = None
            self.audit_manager = None
    
    def _init_intent_recognition(self):
        """初始化意图识别系统"""
        try:
            self.intent_recognition = IntentRecognition(self.caller, self.model_config)
            logging.info(f"[{self.name}] 意图识别系统初始化完成")
        except Exception as e:
            logging.warning(f"[{self.name}] 意图识别系统初始化失败: {str(e)}")
            self.intent_recognition = None
    
    def _init_questioning_system(self):
        """初始化追问系统"""
        try:
            from agents.medical.questioning_agent import QuestioningAgent
            from agents.medical.multimodal_questioning_agent import MultimodalQuestioningAgent
            from shared.config.model_config import get_config
            
            # 追问智能体使用huatuogpt模型
            medical_model_config = get_config("huatuo").to_dict()
            
            self.questioning_agent = QuestioningAgent(medical_model_config)
            self.multimodal_questioning_agent = MultimodalQuestioningAgent(medical_model_config)
            logging.info(f"[{self.name}] 追问系统初始化完成")
        except Exception as e:
            logging.warning(f"[{self.name}] 追问系统初始化失败: {str(e)}")
            self.questioning_agent = None
            self.multimodal_questioning_agent = None
    
    def _init_image_coordinator(self):
        """初始化影像分析协调器"""
        if self.image_coordinator is None:
            try:
                # 影像分析协调器使用qwen-3b模型
                from shared.config.model_config import get_config
                image_model_config = get_config("qwen").to_dict()
                self.image_coordinator = ImageAnalysisCoordinator(image_model_config)
                logging.info(f"[{self.name}] 影像分析协调器初始化完成")
            except Exception as e:
                logging.error(f"[{self.name}] 影像分析协调器初始化失败: {str(e)}")
                raise
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Tuple[str, Any]:
        """
        执行医生式问诊流程
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息，包含角色和权限
            
        返回：
            Tuple[str, Any]: 包含智能体名称和结果的元组
        """
        try:
            logging.info(f"[{self.name}] 开始执行问诊流程，用户输入: {user_input[:50]}...")
            
            # 权限验证
            logging.info(f"[{self.name}] 开始权限验证")
            auth_result = await self._verify_permissions(user_id, user_info)
            if auth_result is not None:
                logging.warning(f"[{self.name}] 权限验证失败: {auth_result}")
                return auth_result
            
            # 获取对话上下文
            logging.info(f"[{self.name}] 获取对话历史")
            context = self.get_context_from_memory(user_id)
            logging.info(f"[{self.name}] 获取到对话历史：\n{context}")
            
            # 获取对话状态
            logging.info(f"[{self.name}] 获取对话状态")
            conversation_state = self._get_conversation_state(user_id)
            logging.info(f"[{self.name}] 当前对话状态: {conversation_state}")
            
            # 医生式问诊流程
            if conversation_state["phase"] == "initial":
                logging.info(f"[{self.name}] 进入初次问诊阶段")
                # 初次问诊，进行意图识别和初步分析
                return await self._initial_consultation(user_input, user_id, user_info, context)
            elif conversation_state["phase"] == "questioning":
                logging.info(f"[{self.name}] 进入追问阶段")
                # 追问阶段，收集更多信息
                return await self._questioning_phase(user_input, user_id, user_info, context)
            elif conversation_state["phase"] == "data_analysis":
                logging.info(f"[{self.name}] 进入数据分析阶段")
                # 数据分析阶段
                return await self._data_analysis_phase(user_input, user_id, user_info, context)
            elif conversation_state["phase"] == "diagnosis":
                logging.info(f"[{self.name}] 进入诊断阶段")
                # 诊断阶段
                return await self._diagnosis_phase(user_input, user_id, user_info, context)
            else:
                logging.info(f"[{self.name}] 进入默认处理（初次问诊）")
                # 默认处理
                return await self._initial_consultation(user_input, user_id, user_info, context)
            
        except Exception as e:
            logging.error(f"[{self.name}] 执行错误：{str(e)}", exc_info=True)
            return "Error", f"⚠️ 抱歉，我在处理您的咨询时遇到了问题，请稍后再试。{str(e)}"
    
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
                "phase": "initial",  # initial, questioning, data_analysis, diagnosis
                "question_round": 0,
                "max_rounds": self.config.max_questioning_rounds,
                "symptom_info": {},
                "collected_data": {},
                "intent": None,
                "needs_data_analysis": False
            }
        return self.conversation_states[user_id]
    
    def _update_conversation_state(self, user_id: str, updates: Dict[str, Any]):
        """
        更新对话状态
        
        参数：
            user_id (str): 用户ID
            updates (Dict[str, Any]): 更新内容
        """
        if user_id in self.conversation_states:
            self.conversation_states[user_id].update(updates)
    
    def _reset_conversation_state(self, user_id: str):
        """
        重置对话状态
        
        参数：
            user_id (str): 用户ID
        """
        if user_id in self.conversation_states:
            del self.conversation_states[user_id]
    
    async def _initial_consultation(self, user_input: str, user_id: str, user_info: Optional[Dict], context: str) -> Tuple[str, Any]:
        """
        初次问诊阶段
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            logging.info(f"[{self.name}] 开始初次问诊阶段")
            
            # 医生式问候
            logging.info(f"[{self.name}] 开始生成医生式问候")
            greeting = await self._generate_doctor_greeting(user_input, user_info)
            logging.info(f"[{self.name}] 问候生成完成: {greeting[:50]}...")
            
            # 意图识别
            logging.info(f"[{self.name}] 开始意图识别")
            intent = await self._recognize_intent(user_input, context)
            logging.info(f"[{self.name}] 识别到意图: {intent}")
            
            # 检查是否为影像分析意图
            if "影像分析" in intent:
                logging.info(f"[{self.name}] 检测到影像分析意图，直接进入影像分析流程")
                # 直接调用影像分析处理
                return await self._handle_image_analysis(user_input, user_id, user_info)
            
            # 更新对话状态
            logging.info(f"[{self.name}] 更新对话状态")
            self._update_conversation_state(user_id, {
                "intent": intent,
                "phase": "questioning",
                "question_round": 0
            })
            
            # 更新症状信息
            logging.info(f"[{self.name}] 更新症状信息")
            self._update_symptom_info(user_id, user_input)
            
            # 分析症状信息完整性
            logging.info(f"[{self.name}] 开始分析症状信息完整性")
            completeness_analysis = await self._analyze_symptom_completeness(user_input, user_id, context)
            logging.info(f"[{self.name}] 症状完整性分析完成: {completeness_analysis}")
            
            # 生成追问问题
            logging.info(f"[{self.name}] 开始生成追问问题")
            questions = await self._generate_doctor_questions(user_input, user_id, context, completeness_analysis)
            logging.info(f"[{self.name}] 追问问题生成完成: {questions}")
            
            # 构建医生式响应
            response = {
                "greeting": greeting,
                "intent": intent,
                "questions": questions,
                "phase": "questioning",
                "completeness_analysis": completeness_analysis,
                "needs_more_info": len(questions) > 0
            }
            
            # 记录对话轮次
            self.dialogue_memory.add_turn(user_id, user_input, self.name, f"初次问诊，识别意图：{intent}")
            
            return "DoctorConsultation", response
            
        except Exception as e:
            logging.error(f"[{self.name}] 初次问诊失败: {str(e)}")
            return "Error", f"抱歉，我在分析您的问题时遇到了困难，请重新描述一下您的症状。"
    
    async def _questioning_phase(self, user_input: str, user_id: str, user_info: Optional[Dict], context: str) -> Tuple[str, Any]:
        """
        追问阶段
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            conversation_state = self._get_conversation_state(user_id)
            current_round = conversation_state["question_round"]
            max_rounds = conversation_state["max_rounds"]
            
            # 更新症状信息
            self._update_symptom_info(user_id, user_input)
            
            # 更新追问轮次
            self._update_conversation_state(user_id, {
                "question_round": current_round + 1
            })
            
            # 检查是否收集到足够信息（在更新轮次后检查）
            updated_round = current_round + 1
            logging.info(f"[{self.name}] 检查轮次: current_round={current_round}, max_rounds={max_rounds}, 更新后轮次={updated_round}")
            if updated_round >= max_rounds:
                logging.info(f"[{self.name}] 达到最大轮次，进入诊断阶段")
                self._update_conversation_state(user_id, {"phase": "data_analysis"})
                return await self._data_analysis_phase(user_input, user_id, user_info, context)
            elif await self._has_sufficient_info(user_id, user_input, updated_round):
                logging.info(f"[{self.name}] 信息收集充分，进入诊断阶段")
                self._update_conversation_state(user_id, {"phase": "data_analysis"})
                return await self._data_analysis_phase(user_input, user_id, user_info, context)
            
            # 继续追问
            completeness_analysis = await self._analyze_symptom_completeness(user_input, user_id, context)
            questions = await self._generate_doctor_questions(user_input, user_id, context, completeness_analysis)
            
            # 构建追问响应
            response = {
                "phase": "questioning",
                "questions": questions,
                "round": current_round + 1,
                "max_rounds": max_rounds,
                "completeness_analysis": completeness_analysis,
                "encouragement": await self._generate_encouragement_message(current_round + 1)
            }
            
            # 记录对话轮次
            self.dialogue_memory.add_turn(user_id, user_input, self.name, f"追问第{current_round + 1}轮")
            
            return "DoctorQuestioning", response
            
        except Exception as e:
            logging.error(f"[{self.name}] 追问阶段失败: {str(e)}")
            return "Error", f"抱歉，我在收集信息时遇到了问题，让我们重新开始吧。"
    
    async def _data_analysis_phase(self, user_input: str, user_id: str, user_info: Optional[Dict], context: str) -> Tuple[str, Any]:
        """
        数据分析阶段
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            conversation_state = self._get_conversation_state(user_id)
            intent = conversation_state.get("intent", "内科咨询")
            
            # 生成数据分析通知
            analysis_notification = await self._generate_data_analysis_notification(intent)
            
            # 检查是否需要分析用户数据
            needs_data_analysis = await self._check_needs_data_analysis(user_id, intent)
            
            if needs_data_analysis:
                # 分析用户数据
                data_analysis_result = await self._analyze_user_data(user_id, intent, user_info)
                
                # 更新对话状态
                self._update_conversation_state(user_id, {
                    "phase": "diagnosis",
                    "data_analysis_result": data_analysis_result
                })
                
                response = {
                    "phase": "data_analysis",
                    "notification": analysis_notification,
                    "data_analysis_result": data_analysis_result,
                    "ready_for_diagnosis": True
                }
                
                return "DataAnalysis", response
            else:
                # 直接进入诊断阶段
                self._update_conversation_state(user_id, {"phase": "diagnosis"})
                return await self._diagnosis_phase(user_input, user_id, user_info, context)
            
        except Exception as e:
            logging.error(f"[{self.name}] 数据分析阶段失败: {str(e)}")
            return "Error", f"抱歉，我在分析您的数据时遇到了问题，让我们继续诊断吧。"
    
    async def _diagnosis_phase(self, user_input: str, user_id: str, user_info: Optional[Dict], context: str) -> Tuple[str, Any]:
        """
        诊断阶段
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            conversation_state = self._get_conversation_state(user_id)
            intent = conversation_state.get("intent", "内科咨询")
            
            # 收集所有症状信息
            all_symptom_info = self._get_all_symptom_info(user_id)
            
            # 根据意图进行专业诊断
            if "影像分析" in intent:
                return await self._handle_image_analysis(user_input, user_id, user_info)
            elif "内科咨询" in intent:
                return await self._handle_internal_medicine(user_input, user_id, user_info, all_symptom_info)
            elif "外科咨询" in intent:
                return await self._handle_surgical(user_input, user_id, user_info, all_symptom_info)
            else:
                return await self._handle_general_advice(user_input, user_id, all_symptom_info)
            
        except Exception as e:
            logging.error(f"[{self.name}] 诊断阶段失败: {str(e)}")
            return "Error", f"抱歉，我在进行诊断时遇到了问题，请稍后再试。"
    
    # ==================== 辅助方法 ====================
    
    async def _generate_doctor_greeting(self, user_input: str, user_info: Optional[Dict]) -> str:
        """生成医生式问候"""
        try:
            greeting_prompt = f"""作为一位经验丰富的医生，请生成一个温柔亲切的问候语：

患者描述：{user_input}
用户信息：{user_info.get('username', '患者') if user_info else '患者'}

请用温柔、关怀的语气问候患者，表达理解和关心，让患者感到安心。
问候语应该：
1. 表达对患者症状的理解和关心
2. 语气温柔亲切，让患者感到安心
3. 体现医生的专业性和人文关怀
4. 长度控制在50字以内

请直接返回问候语："""
            
            greeting = await self.caller(greeting_prompt, self.model_config)
            return greeting.strip()
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成医生问候失败: {str(e)}")
            return "您好，我是您的私人医生。我理解您的担心，让我们一起来仔细了解您的情况。"
    
    async def _analyze_symptom_completeness(self, user_input: str, user_id: str, context: str) -> Dict[str, Any]:
        """分析症状信息完整性"""
        try:
            if self.questioning_agent:
                result = await self.questioning_agent.safe_execute(user_input, user_id, None)
                return result.get("completeness_analysis", {
                    "completeness_score": 60,
                    "needs_follow_up": True,
                    "missing_info": ["需要更多详细信息"]
                })
            else:
                # 备用分析
                analysis_prompt = f"""作为专业医生，请分析患者症状描述的完整性：

患者描述：{user_input}
对话历史：{context}

请评估：
1. 症状描述是否清晰具体？
2. 是否缺少关键信息（时间、强度、性质等）？
3. 是否需要了解伴随症状？
4. 症状严重程度如何？

请用JSON格式返回：
{{
    "completeness_score": 0-100,
    "needs_follow_up": true/false,
    "missing_info": ["缺少的关键信息"],
    "severity": "轻度/中度/重度"
}}"""
                
                analysis = await self.caller(analysis_prompt, self.model_config)
                try:
                    import json
                    return json.loads(analysis)
                except:
                    return {
                        "completeness_score": 60,
                        "needs_follow_up": True,
                        "missing_info": ["需要更多详细信息"],
                        "severity": "中度"
                    }
                    
        except Exception as e:
            logging.error(f"[{self.name}] 症状完整性分析失败: {str(e)}")
            return self._get_fallback_completeness_analysis(user_input)
    
    def _get_fallback_completeness_analysis(self, user_input: str) -> Dict[str, Any]:
        """获取备用症状完整性分析"""
        # 简单的关键词分析
        missing_info = []
        
        # 检查时间信息
        time_keywords = ["时间", "多久", "持续", "开始", "昨天", "今天", "上周", "最近"]
        if not any(keyword in user_input for keyword in time_keywords):
            missing_info.append("症状持续时间")
        
        # 检查强度信息
        intensity_keywords = ["轻微", "中等", "严重", "很疼", "有点", "非常", "强烈"]
        if not any(keyword in user_input for keyword in intensity_keywords):
            missing_info.append("症状强度")
        
        # 检查伴随症状
        if len(user_input) < 20:  # 描述太简短
            missing_info.append("伴随症状")
        
        return {
            "completeness_score": 60 if missing_info else 80,
            "needs_follow_up": len(missing_info) > 0,
            "missing_info": missing_info,
            "severity": "中度",
            "urgency": "中"
        }
    
    async def _generate_doctor_questions(self, user_input: str, user_id: str, context: str, completeness_analysis: Dict[str, Any]) -> List[str]:
        """生成医生式追问问题"""
        try:
            if self.questioning_agent:
                result = await self.questioning_agent.safe_execute(user_input, user_id, None)
                questions = result.get("questions", [])
                
                # 检查是否包含错误信息
                if questions and isinstance(questions[0], str) and "模型调用失败" in questions[0]:
                    logging.warning(f"[{self.name}] QuestioningAgent返回错误，使用备用问题生成")
                    return self._get_fallback_questions(user_input, completeness_analysis)
                
                return questions
            else:
                return self._get_fallback_questions(user_input, completeness_analysis)
                
        except Exception as e:
            logging.error(f"[{self.name}] 生成追问问题失败: {str(e)}")
            return self._get_fallback_questions(user_input, completeness_analysis)
    
    def _get_fallback_questions(self, user_input: str, completeness_analysis: Dict[str, Any]) -> List[str]:
        """获取备用追问问题"""
        missing_info = completeness_analysis.get("missing_info", [])
        
        # 基于缺失信息生成问题
        questions = []
        if "症状持续时间" in missing_info or "时间" in str(missing_info):
            questions.append("请问您的症状持续多长时间了？")
        if "症状强度" in missing_info or "强度" in str(missing_info):
            questions.append("请描述一下症状的强度，是轻微、中等还是严重？")
        if "伴随症状" in missing_info or "其他症状" in str(missing_info):
            questions.append("除了主要症状外，还有其他不适吗？")
        if "诱发因素" in missing_info or "诱因" in str(missing_info):
            questions.append("您觉得是什么原因引起的这些症状？")
        
        # 如果没有特定问题，使用通用问题
        if not questions:
            questions = [
                "请详细描述一下您的症状，包括症状的持续时间、强度等。",
                "除了刚才提到的，还有其他不适吗？"
            ]
        
        return questions[:3]  # 限制问题数量
    
    def _update_symptom_info(self, user_id: str, user_input: str):
        """更新症状信息"""
        try:
            conversation_state = self._get_conversation_state(user_id)
            if "symptom_info" not in conversation_state:
                conversation_state["symptom_info"] = {}
            
            # 获取当前轮次，如果是在初次问诊阶段，使用0
            current_round = conversation_state.get("question_round", 0)
            
            # 简单的症状信息提取
            conversation_state["symptom_info"][f"round_{current_round}"] = user_input
            
            # 保存更新后的对话状态
            self._update_conversation_state(user_id, {"symptom_info": conversation_state["symptom_info"]})
            
            logging.info(f"[{self.name}] 更新症状信息: round_{current_round} = {user_input[:50]}...")
            
        except Exception as e:
            logging.error(f"[{self.name}] 更新症状信息失败: {str(e)}")
    
    async def _has_sufficient_info(self, user_id: str, user_input: str, current_round: int = None) -> bool:
        """检查是否收集到足够信息"""
        try:
            conversation_state = self._get_conversation_state(user_id)
            if current_round is None:
                current_round = conversation_state["question_round"]
            
            # 如果已经达到最大轮次，认为信息足够
            if current_round >= self.config.max_questioning_rounds:
                return True
            
            # 分析当前输入的信息完整性
            completeness_analysis = await self._analyze_symptom_completeness(user_input, user_id, "")
            completeness_score = completeness_analysis.get("completeness_score", 0)
            
            # 如果完整性评分达到80分以上，认为信息足够
            return completeness_score >= 80
            
        except Exception as e:
            logging.error(f"[{self.name}] 检查信息充分性失败: {str(e)}")
            return False
    
    def _get_all_symptom_info(self, user_id: str) -> str:
        """获取所有症状信息"""
        try:
            conversation_state = self._get_conversation_state(user_id)
            symptom_info = conversation_state.get("symptom_info", {})
            
            if not symptom_info:
                return ""
            
            # 按轮次排序，构建清晰的症状描述
            all_info = []
            
            # 提取原始问题（round_0）
            if "round_0" in symptom_info:
                all_info.append(f"【用户原始问题】\n{symptom_info['round_0']}")
            
            # 提取补充信息（round_1 及以后）
            supplementary_info = []
            for round_key in sorted(symptom_info.keys()):
                if round_key != "round_0":
                    round_num = round_key.replace("round_", "")
                    supplementary_info.append(f"【医生追问补充的症状信息 - 第{round_num}轮】\n{symptom_info[round_key]}")
            
            if supplementary_info:
                all_info.extend(supplementary_info)
            
            return "\n\n".join(all_info)
            
        except Exception as e:
            logging.error(f"[{self.name}] 获取症状信息失败: {str(e)}")
            return ""
    
    async def _generate_encouragement_message(self, current_round: int) -> str:
        """生成鼓励信息"""
        try:
            encouragement_messages = [
                "很好，这些信息很有帮助。",
                "谢谢您的详细描述，这对诊断很重要。",
                "您的回答很详细，让我们继续了解。",
                "这些信息很有价值，请继续。",
                "感谢您的耐心，我们快完成了。"
            ]
            
            if current_round <= len(encouragement_messages):
                return encouragement_messages[current_round - 1]
            else:
                return "感谢您的耐心配合。"
                
        except Exception as e:
            logging.error(f"[{self.name}] 生成鼓励信息失败: {str(e)}")
            return "感谢您的配合。"
    
    async def _generate_data_analysis_notification(self, intent: str) -> str:
        """生成数据分析通知"""
        try:
            if not self.config.enable_data_analysis_notification:
                return ""
            
            notification_templates = {
                "影像分析": "我正在仔细分析您上传的医学影像，请稍候...",
                "内科咨询": "我正在查看您的病历记录和体检报告，请稍候...",
                "外科咨询": "我正在分析您的症状和相关检查结果，请稍候...",
                "其他": "我正在综合分析您的症状信息，请稍候..."
            }
            
            return notification_templates.get(intent, notification_templates["其他"])
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成数据分析通知失败: {str(e)}")
            return "我正在分析您的信息，请稍候..."
    
    async def _check_needs_data_analysis(self, user_id: str, intent: str) -> bool:
        """检查是否需要数据分析"""
        try:
            # 检查用户是否有相关数据
            if "影像分析" in intent:
                return await self._check_user_images(user_id)
            else:
                # 检查是否有病历记录等
                return await self._check_user_medical_records(user_id)
                
        except Exception as e:
            logging.error(f"[{self.name}] 检查数据分析需求失败: {str(e)}")
            return False
    
    async def _analyze_user_data(self, user_id: str, intent: str, user_info: Optional[Dict]) -> Dict[str, Any]:
        """分析用户数据"""
        try:
            analysis_result = {
                "intent": intent,
                "data_available": False,
                "analysis_summary": "",
                "recommendations": []
            }
            
            if "影像分析" in intent:
                # 分析影像数据
                analysis_result.update(await self._analyze_image_data(user_id))
            else:
                # 分析病历数据
                analysis_result.update(await self._analyze_medical_records(user_id))
            
            return analysis_result
            
        except Exception as e:
            logging.error(f"[{self.name}] 分析用户数据失败: {str(e)}")
            return {
                "intent": intent,
                "data_available": False,
                "analysis_summary": "数据分析遇到问题，将基于症状描述进行诊断。",
                "recommendations": []
            }
    
    async def _analyze_image_data(self, user_id: str) -> Dict[str, Any]:
        """分析影像数据"""
        try:
            # 初始化影像分析协调器
            self._init_image_coordinator()
            
            # 真正调用影像分析协调器进行影像分析
            image_result = await self.image_coordinator.analyze_images(user_id, "影像分析请求")
            
            if isinstance(image_result, dict):
                # 提取分析结果
                analysis_summary = image_result.get("analysis", "影像分析完成")
                recommendations = image_result.get("recommendations", [])
                
                # 如果recommendations是字符串，转换为列表
                if isinstance(recommendations, str):
                    recommendations = [recommendations]
                
                return {
                    "data_available": True,
                    "analysis_summary": analysis_summary,
                    "recommendations": recommendations,
                    "image_analysis_result": image_result  # 保存完整的分析结果
                }
            else:
                # 如果返回的是字符串或其他类型
                return {
                    "data_available": True,
                    "analysis_summary": str(image_result),
                    "recommendations": [],
                    "image_analysis_result": {"raw_result": str(image_result)}
                }
                
        except Exception as e:
            logging.error(f"[{self.name}] 影像数据分析失败: {str(e)}")
            return {
                "data_available": False,
                "analysis_summary": f"影像分析失败：{str(e)}",
                "recommendations": [],
                "error": str(e)
            }
    
    async def _analyze_medical_records(self, user_id: str) -> Dict[str, Any]:
        """分析病历数据"""
        try:
            # 这里可以调用病历分析功能
            return {
                "data_available": True,
                "analysis_summary": "病历分析完成，发现相关病史。",
                "recommendations": ["注意既往病史", "建议定期复查"]
            }
        except Exception as e:
            logging.error(f"[{self.name}] 病历数据分析失败: {str(e)}")
            return {
                "data_available": False,
                "analysis_summary": "病历分析遇到问题。",
                "recommendations": []
            }
    
    async def _check_user_medical_records(self, user_id: str) -> bool:
        """检查用户是否有病历记录"""
        try:
            # 这里可以检查用户是否有病历记录
            return False  # 暂时返回False
        except Exception as e:
            logging.error(f"[{self.name}] 检查病历记录失败: {str(e)}")
            return False
    
    async def _verify_permissions(self, user_id: str, user_info: Optional[Dict]) -> Optional[Tuple[str, str]]:
        """
        验证用户权限
        
        参数：
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Optional[Tuple[str, str]]: 如果权限验证失败，返回错误信息
        """
        if not user_info or not self.authz_manager:
            return None
        
        try:
            user_role = user_info.get("role")
            if not user_role:
                logging.warning(f"[{self.name}] 用户 {user_id} 角色信息缺失")
                return "AuthorizationError", "⚠️ 用户角色信息缺失，无法进行权限验证。"
            
            # 转换角色为UserRole枚举
            if isinstance(user_role, str):
                from auth_manager import UserRole
                user_role_enum = UserRole(user_role)
            else:
                user_role_enum = user_role
            
            # 检查智能体访问权限
            if not self.authz_manager.check_agent_access(user_role_enum, "CybertwinAgent"):
                logging.warning(f"[{self.name}] 用户 {user_id} ({user_role_enum.value}) 无法访问Cybertwin智能体")
                return "AuthorizationError", "⚠️ 权限不足，无法访问数字孪生智能体。"
            
            logging.info(f"[{self.name}] 用户 {user_id} ({user_role_enum.value}) 权限验证通过")
            return None
            
        except (ValueError, TypeError) as e:
            logging.warning(f"[{self.name}] 权限验证失败: {str(e)}")
            return "AuthorizationError", "⚠️ 权限验证失败，无法进行权限验证。"
    
    async def _recognize_intent(self, user_input: str, context: str) -> str:
        """
        识别用户意图
        
        参数：
            user_input (str): 用户输入
            context (str): 对话上下文
            
        返回：
            str: 识别到的意图
        """
        if self.intent_recognition:
            try:
                intent_result = await self.intent_recognition.recognize_intent(user_input, context)
                
                # 转换意图类型为中文描述
                if intent_result.intent_type == IntentType.IMAGE_ANALYSIS:
                    return "影像分析"
                elif intent_result.intent_type == IntentType.MEDICAL_CONSULTATION:
                    if intent_result.specialty:
                        if "外科" in str(intent_result.specialty.value):
                            return "外科咨询"
                        else:
                            return "内科咨询"
                    else:
                        return "内科咨询"
                else:
                    return "内科咨询"
                    
            except Exception as e:
                logging.warning(f"[{self.name}] 意图识别失败，使用备用方法: {str(e)}")
        
        # 备用方法：使用LLM进行意图识别
        intent_prompt = f"""请分析用户输入，判断需要哪种类型的医疗服务：




1. 影像分析：需要分析医学影像（包含"影像"、"X光"、"CT"、"MRI"、"检查"、"片子"、"胸部影像"等关键词）
2. 内科咨询：需要内科专家建议（包含"症状"、"疼痛"、"不舒服"、"生病"等关键词）
3. 外科咨询：需要外科专家建议（包含"手术"、"外伤"、"外科"等关键词）

用户输入：{user_input}

对话上下文：{context}

注意：如果用户提到"影像"、"检查"、"片子"等关键词，优先选择"影像分析"。

请只返回：影像分析/内科咨询/外科咨询"""
        
        intent = await self.caller(intent_prompt, self.model_config)
        return intent.strip()
    
    async def _dispatch_task(self, intent: str, user_input: str, user_id: str, user_info: Optional[Dict]) -> Tuple[str, Any]:
        """
        根据意图分发任务到相应的智能体
        
        参数：
            intent (str): 识别的意图
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        if "影像分析" in intent:
            return await self._handle_image_analysis(user_input, user_id, user_info)
        elif "内科咨询" in intent:
            return await self._handle_internal_medicine(user_input, user_id, user_info)
        elif "外科咨询" in intent:
            return await self._handle_surgical(user_input, user_id, user_info)
        else:
            return await self._handle_general_advice(user_input, user_id)
    
    async def _handle_image_analysis(self, user_input: str, user_id: str, user_info: Optional[Dict]) -> Tuple[str, Any]:
        """处理影像分析请求"""
        logging.info(f"[{self.name}] 分发到影像分析流程")
        
        # 权限验证
        if user_info and self.authz_manager:
            auth_result = await self._verify_agent_access(user_id, user_info, "ImageAnalysisAgent")
            if auth_result is not None:
                return auth_result
        
        # 初始化影像分析协调器
        self._init_image_coordinator()
        
        # 检查用户是否已上传影像
        if not await self._check_user_images(user_id):
            return "AuthorizationPending", "⚠️ 请先上传医学影像。"
        
        # 使用影像分析协调器分析影像
        image_result = await self.image_coordinator.analyze_images(user_id, user_input)
        return "ImageAnalysis", image_result
    
    async def _handle_internal_medicine(self, user_input: str, user_id: str, user_info: Optional[Dict], all_symptom_info: str = "") -> Tuple[str, Any]:
        """处理内科咨询请求 - 医生人设优化版"""
        logging.info(f"[{self.name}] 分发到内科咨询流程")
        
        try:
            # 权限验证
            if user_info and self.authz_manager:
                auth_result = await self._verify_agent_access(user_id, user_info, "InternalMedicineAgent")
                if auth_result is not None:
                    return auth_result
            
            # 构建完整的症状描述（all_symptom_info 已包含所有信息，包括原始问题和补充信息）
            full_symptom_description = all_symptom_info if all_symptom_info else user_input
            logging.info(f"[{self.name}] 传递给内科智能体的完整症状描述: {full_symptom_description[:200]}...")
            
            # 执行内科诊断
            internal_result = await self.internal_medicine_agent.safe_execute(full_symptom_description, user_id, user_info)
            
            # 简化诊断流程，直接生成综合报告
            logging.info(f"[{self.name}] 生成综合诊断报告")
            
            # 生成医生式诊断报告（包含分诊建议）
            doctor_diagnosis = await self._generate_simplified_diagnosis_report(
                internal_result, all_symptom_info, "内科"
            )
            
            # 重置对话状态
            self._reset_conversation_state(user_id)
            
            # 处理不同的返回类型
            if isinstance(internal_result, dict):
                diagnosis_content = internal_result.get("diagnosis", "")
            else:
                diagnosis_content = str(internal_result)
            
            return "InternalMedicineAgent", {
                "diagnosis": diagnosis_content,
                "doctor_report": doctor_diagnosis,
                "phase": "completed"
            }
            
        except Exception as e:
            logging.error(f"[{self.name}] 内科咨询处理失败: {str(e)}")
            return "Error", f"抱歉，我在进行内科诊断时遇到了问题，请稍后再试。"
    
    async def _handle_surgical(self, user_input: str, user_id: str, user_info: Optional[Dict], all_symptom_info: str = "") -> Tuple[str, Any]:
        """处理外科咨询请求 - 医生人设优化版"""
        logging.info(f"[{self.name}] 分发到外科咨询流程")
        
        try:
            # 权限验证
            if user_info and self.authz_manager:
                auth_result = await self._verify_agent_access(user_id, user_info, "SurgicalAgent")
                if auth_result is not None:
                    return auth_result
            
            # 构建完整的症状描述（all_symptom_info 已包含所有信息，包括原始问题和补充信息）
            full_symptom_description = all_symptom_info if all_symptom_info else user_input
            logging.info(f"[{self.name}] 传递给外科智能体的完整症状描述: {full_symptom_description[:200]}...")
            
            # 执行外科诊断
            surgical_result = await self.surgical_agent.safe_execute(full_symptom_description, user_id, user_info)
            
            # 生成综合建议
            logging.info(f"[{self.name}] 调用SummaryAgent生成汇总报告")
            expert_results = {"外科建议": surgical_result}
            summary = await self.summary_agent.safe_execute(expert_results, user_id)
            
            # 进行分诊推荐
            logging.info(f"[{self.name}] 调用TriageAgent进行分诊")
            triage = await self.triage_agent.safe_execute(summary, user_id)
            
            # 生成医生式诊断报告
            doctor_diagnosis = await self._generate_doctor_diagnosis_report(
                surgical_result, summary, triage, "外科"
            )
            
            # 重置对话状态
            self._reset_conversation_state(user_id)
            
            return "SurgicalAgent", {
                "diagnosis": surgical_result.get("diagnosis", ""),
                "summary": summary,
                "triage": triage,
                "doctor_report": doctor_diagnosis,
                "phase": "completed"
            }
            
        except Exception as e:
            logging.error(f"[{self.name}] 外科咨询处理失败: {str(e)}")
            return "Error", f"抱歉，我在进行外科诊断时遇到了问题，请稍后再试。"
    
    async def _handle_general_advice(self, user_input: str, user_id: str, all_symptom_info: str = "") -> Tuple[str, Any]:
        """处理通用医疗建议 - 医生人设优化版"""
        logging.warning(f"[{self.name}] 无法识别的意图，提供通用医疗建议")
        
        try:
            # 构建完整的症状描述（all_symptom_info 已包含所有信息，包括原始问题和补充信息）
            full_symptom_description = all_symptom_info if all_symptom_info else user_input
            logging.info(f"[{self.name}] 传递给通用建议的完整症状描述: {full_symptom_description[:200]}...")
            
            general_prompt = f"""作为一位经验丰富的医生，请根据患者的健康问题提供专业且温暖的医疗建议：
            
患者问题：{full_symptom_description}

请用温柔亲切的语气提供：
1. 症状分析（用患者能理解的语言）
2. 可能的病因（简单明了）
3. 建议的检查项目（具体可行）
4. 推荐的科室（明确指导）
5. 注意事项（贴心提醒）

请用专业但温暖的语言回答，让患者感到安心和被关怀。"""
            
            general_response = await self.caller(general_prompt, self.model_config)
            
            # 生成医生式建议报告
            doctor_advice = await self._generate_doctor_advice_report(general_response)
            
            # 重置对话状态
            self._reset_conversation_state(user_id)
            
            return "GeneralAdvice", {
                "diagnosis": general_response,
                "summary": general_response,
                "triage": "建议根据症状选择相应科室就诊",
                "doctor_advice": doctor_advice,
                "phase": "completed"
            }
            
        except Exception as e:
            logging.error(f"[{self.name}] 通用建议处理失败: {str(e)}")
            return "Error", f"抱歉，我在提供建议时遇到了问题，请稍后再试。"
    
    async def _generate_simplified_diagnosis_report(self, internal_result: Dict, all_symptom_info: str, specialty: str) -> str:
        """
        生成简化的诊断报告 - 包含病史关联分析
        
        参数：
            internal_result: 内科诊断结果（包含病史分析）
            all_symptom_info: 所有症状信息
            specialty: 专科类型
            
        返回：
            str: 诊断报告
        """
        try:
            # 处理不同的返回类型
            if isinstance(internal_result, dict):
                diagnosis = internal_result.get("diagnosis", "")
                advice = internal_result.get("advice", "")
                history_analysis = internal_result.get("history_analysis", {})
            else:
                diagnosis = str(internal_result)
                advice = ""
                history_analysis = {}
            
            # 提取病史分析信息
            history_info = ""
            if isinstance(history_analysis, dict):
                history_content = history_analysis.get("analysis", "")
                risk_assessment = history_analysis.get("risk_assessment", {})
                recommendations = history_analysis.get("recommendations", {})
                
                if history_content:
                    history_info = f"""
**📋 病史关联分析**
{history_content}

**⚠️ 风险评估**
{risk_assessment.get('content', '基于您的病史，建议定期监测健康状况')}

**💡 病史建议**
{recommendations.get('content', '请继续关注症状变化，必要时及时就医')}
"""
            
            report_prompt = f"""作为一位经验丰富的{specialty}医生，请基于以下信息生成一份温暖、专业的诊断报告：

患者症状：
{all_symptom_info}

初步分析：
{diagnosis}

{history_info}

请以医生对患者对话的方式，生成一份条理清晰、温暖专业的诊断报告，包含以下内容：

**📋 症状理解**
- 症状的完整性描述总结
- **详细解读用户提供的检查数据**（如血糖、血压等具体数值和时间线变化）
- **分析数据的时间线和发展趋势**（如血糖从 5.8 → 6.0 → 6.4 的变化及其医学意义）
- 对患者症状的理解和关心
- 症状的严重程度评估

**🔍 可能原因**
- 用患者能理解的语言解释可能的病因
- 结合病史分析，说明症状与既往病史的关联

**📊 病史关联分析**
- 分析当前症状与既往病史的关联性
- 评估既往疾病对当前症状的影响
- 提供基于病史的个性化建议

**💊 治疗建议**
- 具体的治疗建议和注意事项
- 考虑既往病史的用药建议
- 生活方式调整建议

**🏥 就医建议**
- 推荐的检查项目（如需要）
- 推荐的科室（如需要转诊）
- 紧急情况处理
- 基于病史的复查建议

请让患者感到被理解和关怀，语言要温暖、专业、条理清晰。报告长度控制在500字以内，使用适当的emoji和分段。"""
            
            doctor_report = await self.caller(report_prompt, self.model_config)
            return doctor_report.strip()
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成简化诊断报告失败: {str(e)}")
            return f"基于您的症状描述，建议您及时就医进行详细检查。如有紧急情况，请立即前往医院急诊科。"
    
    async def _generate_doctor_diagnosis_report(self, diagnosis_result: Any, summary: Any, triage: Any, specialty: str) -> str:
        """生成医生式诊断报告 - 包含病史关联分析"""
        try:
            # 提取病史分析信息（如果诊断结果包含病史分析）
            history_info = ""
            if isinstance(diagnosis_result, dict) and "history_analysis" in diagnosis_result:
                history_analysis = diagnosis_result.get("history_analysis", {})
                if isinstance(history_analysis, dict):
                    history_content = history_analysis.get("analysis", "")
                    risk_assessment = history_analysis.get("risk_assessment", {})
                    recommendations = history_analysis.get("recommendations", {})
                    
                    if history_content:
                        history_info = f"""
**📊 病史关联分析**
- 分析当前症状与既往病史的关联性
- 评估既往疾病对当前症状的影响
- 提供基于病史的个性化建议

**⚠️ 风险评估**
{risk_assessment.get('content', '基于您的病史，建议定期监测健康状况')}

**💡 病史建议**
{recommendations.get('content', '请继续关注症状变化，必要时及时就医')}
"""
            
            report_prompt = f"""作为一位经验丰富的{specialty}医生，请基于以下信息生成一份温暖、专业的诊断报告：

诊断结果：{diagnosis_result}
综合建议：{summary}
分诊建议：{triage}

{history_info}

请以医生对患者对话的方式，生成一份条理清晰、温暖专业的诊断报告，包含以下内容：

**📋 症状理解**
- 症状的完整性描述总结
- **详细解读用户提供的检查数据**（如血糖、血压等具体数值和时间线变化）
- **分析数据的时间线和发展趋势**（如血糖从 5.8 → 6.0 → 6.4 的变化及其医学意义）
- 症状的严重程度评估

**🔍 诊断分析**
- 用患者能理解的语言解释诊断结果
- 结合病史分析，说明症状与既往病史的关联

**💊 治疗建议**
- 具体的治疗建议和注意事项
- 考虑既往病史的用药建议
- 生活方式调整建议

**🏥 就医指导**
- 推荐的检查项目（如需要）
- 推荐的科室（如需要转诊）
- 紧急情况处理
- 基于病史的复查建议

请让患者感到被理解和关怀，语言要温暖、专业、条理清晰。报告长度控制在500字以内，使用适当的emoji和分段。"""
            
            doctor_report = await self.caller(report_prompt, self.model_config)
            return doctor_report.strip()
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成医生诊断报告失败: {str(e)}")
            return f"基于您的症状描述，我建议您及时就医进行专业检查。请保持乐观，积极配合治疗。"
    
    async def _generate_doctor_advice_report(self, advice: str) -> str:
        """生成医生式建议报告"""
        try:
            report_prompt = f"""作为一位经验丰富的医生，请将以下建议转化为更温暖亲切的表达：

原始建议：{advice}

请用温柔关怀的语气重新组织内容，让患者感到：
1. 被理解和关心
2. 获得专业的指导
3. 明确知道下一步该怎么做

请保持专业性，但语气要温暖亲切。"""
            
            doctor_advice = await self.caller(report_prompt, self.model_config)
            return doctor_advice.strip()
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成医生建议报告失败: {str(e)}")
            return advice
    
    async def _verify_agent_access(self, user_id: str, user_info: Dict, agent_name: str) -> Optional[Tuple[str, str]]:
        """验证特定智能体的访问权限"""
        try:
            user_role = user_info.get("role")
            if isinstance(user_role, str):
                from auth_manager import UserRole
                user_role_enum = UserRole(user_role)
            else:
                user_role_enum = user_role
            
            if not self.authz_manager.check_agent_access(user_role_enum, agent_name):
                logging.warning(f"[{self.name}] 用户 {user_id} 无法访问{agent_name}")
                return "AuthorizationError", f"⚠️ 权限不足，无法进行{agent_name}相关操作。"
            
            return None
            
        except (ValueError, TypeError) as e:
            logging.warning(f"[{self.name}] 权限验证失败: {str(e)}")
            return "AuthorizationError", f"⚠️ 权限验证失败，无法进行{agent_name}相关操作。"
    
    async def _check_user_images(self, user_id: str) -> bool:
        """检查用户是否已上传影像"""
        try:
            # 首先尝试从medical service数据库检查影像
            import sqlite3
            import os
            
            data_dir = "data"
            db_path = os.path.join(data_dir, "chat_history.db")
            
            if os.path.exists(db_path):
                db = sqlite3.connect(db_path)
                cursor = db.cursor()
                
                # 查询用户是否有影像数据
                cursor.execute("""
                    SELECT COUNT(*) FROM medical_images 
                    WHERE user_id = ?
                """, (user_id,))
                
                count = cursor.fetchone()[0]
                db.close()
                
                if count > 0:
                    logging.info(f"[{self.name}] 用户 {user_id} 有 {count} 张影像")
                    return True
            
            # 如果medical service没有数据，尝试从hospital registry获取
            if self.image_coordinator and self.image_coordinator.hospital_registry:
                for hospital in self.image_coordinator.hospital_registry.hospitals.values():
                    if hospital.get_image(user_id):
                        return True
            
            logging.info(f"[{self.name}] 用户 {user_id} 没有找到影像数据")
            return False
            
        except Exception as e:
            logging.error(f"[{self.name}] 检查用户影像失败: {str(e)}")
            return False
    
    async def _log_audit(self, user_id: str, intent: str, result: Tuple[str, Any]):
        """记录审计日志"""
        try:
            if self.audit_manager:
                audit_data = {
                    "user_id": user_id,
                    "action": "cybertwin_execute",
                    "intent": intent,
                    "agent_name": result[0],
                    "timestamp": self.dialogue_memory.get_current_timestamp()
                }
                await self.audit_manager.log_action(audit_data)
        except Exception as e:
            logging.error(f"[{self.name}] 审计日志记录失败: {str(e)}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": "经验丰富的医生智能体，以温柔亲切的语气与患者交流，通过多轮追问收集完整信息",
            "persona": self.config.doctor_persona,
            "capabilities": [
                "医生式问诊",
                "多轮追问（1轮）",
                "数据分析通知",
                "专业诊断",
                "温柔关怀",
                "意图识别",
                "任务分发",
                "权限控制",
                "结果汇总",
                "分诊建议"
            ],
            "questioning_features": {
                "max_rounds": self.config.max_questioning_rounds,
                "min_rounds": self.config.min_questioning_rounds,
                "data_analysis_notification": self.config.enable_data_analysis_notification
            },
            "sub_agents": [
                "InternalMedicineAgent",
                "SurgicalAgent", 
                "SummaryAgent",
                "TriageAgent",
                "ImageAnalysisCoordinator",
                "QuestioningAgent",
                "MultimodalQuestioningAgent"
            ],
            "conversation_phases": [
                "initial",      # 初次问诊
                "questioning",  # 追问阶段
                "data_analysis", # 数据分析
                "diagnosis"     # 诊断阶段
            ]
        }
