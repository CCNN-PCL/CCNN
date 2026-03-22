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
个人助理智能体 (UserAgent)
====================================

"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

# 导入基础智能体类
import sys
import os
from pathlib import Path
import json
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent
from backend.services.redis_service import RedisService
from backend.services.auth_service import AuthService
from config.url_config import JWR_URL, RBAC_URL, MCP_URL
from backend.mcp.mcp_client_new import Server

# 为了向后兼容，保留全局logging使用
# 但建议在需要的地方使用 self.logger 而不是 logging
from agents.medical.internal_medicine import InternalMedicineAgent
from agents.medical.surgical import SurgicalAgent
from agents.medical.summary import SummaryAgent
from agents.medical.triage import TriageAgent
from agents.image.coordinator import ImageAnalysisCoordinator
from agents.llm.intent_recognition import IntentRecognition, IntentType

#A2A协议
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_text_message, new_task
from a2a.types import TaskState, Part, TextPart

@dataclass
class CybertwinConfig:
    """个人助理智能体配置"""
    model_config: Dict[str, Any]
    enable_auth: bool = True
    enable_audit: bool = True
    max_context_length: int = 4000
    intent_threshold: float = 0.7
    max_questioning_rounds: int = 1  # 最大追问轮数（用户回答追问的次数）
    min_questioning_rounds: int = 1  # 最小追问轮数
    doctor_persona: str = "专业的个人助理"  # 个人助理人设
    enable_data_analysis_notification: bool = True  # 启用数据分析通知


class UserAgent(BaseAgent):
    
    def __init__(self, config: CybertwinConfig):
        """
        初始化经验丰富的个人助理智能体
        
        参数：
            config (CybertwinConfig): 智能体配置
        """
        super().__init__(config.model_config)
        self.config = config
        self.agent_id = "userAgent"
        self.name = "专业的个人助理"
        self.auth_service = AuthService()
           
        # 初始化认证授权系统
        #self._init_auth_system()
        
        # 初始化意图识别系统
        self._init_intent_recognition()
              
        # 对话状态管理
        self.conversation_states = {}
        
        logging.info(f"[{self.name}] 初始化完成")

    def _init_intent_recognition(self):
        """初始化意图识别系统"""
        try:
            self.intent_recognition = IntentRecognition(self.caller, self.model_config)
            logging.info(f"[{self.name}] 意图识别系统初始化完成")
        except Exception as e:
            logging.warning(f"[{self.name}] 意图识别系统初始化失败: {str(e)}")
            self.intent_recognition = None
    
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
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Tuple[str, Any]:
        """       
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息，包含角色和权限
            
        返回：
            Tuple[str, Any]: 包含智能体名称和结果的元组
        """
        try:
            logging.info(f"[{self.name}] 开始执行回答流程，用户输入: {user_input[:50]}...")
            logging.info(f"用户ID: {user_id}")
            
            # 权限验证
            # logging.info(f"[{self.name}] 开始权限验证")
            # auth_result = await self._verify_permissions(user_id, user_info)
            # if auth_result is not None:
            #     logging.warning(f"[{self.name}] 权限验证失败: {auth_result}")
            #     return auth_result
            
            # 获取对话上下文
            logging.info(f"[{self.name}] 获取对话历史")
            context = self.get_context_from_memory(user_id)
            logging.info(f"[{self.name}] 获取到对话历史：\n{context}")
            
            # 获取对话状态
            logging.info(f"[{self.name}] 获取对话状态")
            conversation_state = self._get_conversation_state(user_id)
            logging.info(f"[{self.name}] 当前对话状态: {conversation_state}")
            
            # 智能助理流程
            logging.info(f"[{self.name}] 进入回答阶段")
            # 进行意图识别和初步分析
            return await self._initial_asistant(user_input, user_id, user_info, context)

            
        except Exception as e:
            logging.error(f"[{self.name}] 执行错误：{str(e)}", exc_info=True)
            return "Error", f"⚠️ 抱歉，我在处理您的咨询时遇到了问题，请稍后再试。{str(e)}"

    async def judge(self, user_input: str, user_id: str, user_info: Optional[Dict] = None) -> Tuple[str, Any]:
        """       
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息，包含角色和权限
            
        返回：
            Tuple[str, Any]: 包含智能体名称和结果的元组
        """
        try:
            logging.info(f"[{self.name}] 开始执行回答流程，用户输入: {user_input[:50]}...")
            logging.info(f"用户ID: {user_id}")
           
            # 智能助理流程
            logging.info(f"[{self.name}] 进入回答阶段")
            # 进行意图识别和初步分析
            return await self._judge_asistant(user_input, user_id, user_info)

            
        except Exception as e:
            logging.error(f"[{self.name}] 执行错误：{str(e)}", exc_info=True)
            return "Error", f"⚠️ 抱歉，我在处理您的咨询时遇到了问题，请稍后再试。{str(e)}"

    async def a2aExecute(self, user_input: str,token: str, user_info: Optional[Dict] = None) -> Tuple[str, Any]:
        """       
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息，包含角色和权限
            
        返回：
            Tuple[str, Any]: 包含智能体名称和结果的元组
        """
        try:
            logging.info(f"[{self.name}] 开始执行回答流程，用户输入: {user_input[:50]}...")
           
            print("JWR_URL:",JWR_URL)
            print("token:",token)
            redis_service = RedisService()
            result = self.auth_service.jwt_verify(url=JWR_URL,json_data={"token": token})
            print("jwt_verify 请求成功:", result)
            isValid = result['valid']
            user_id = result['payload']['sub']
            client_id = result['payload']['aud']
            print("isValid:",isValid)
            print("user_id:",user_id)
            print("client_id:",client_id)

            query_str = "接收到智慧医疗智能体的A2A请求：" + user_input
            redis_service.save_chat_message(user_id, query_str)
            if(isValid):
                result = self.auth_service.rbac_verify(url=RBAC_URL,json_data={"app_name": client_id, "data_type": "medical", "operation_type": "read"})
                is_rbac_valid = result['result']
                if is_rbac_valid == "allow":
                    print("✅ RBAC授权成功")
                    logging.info("✅ RBAC授权成功")
                    redis_service.save_chat_message(user_id, "✅ Cybertwin已授权数据访问权限给智慧医疗智能体")
                else:
                    redis_service.save_chat_message(user_id, "⚠️ RBAC鉴权失败")
                    logging.info("⚠️ RBAC鉴权失败")
                    return "Error", f"⚠️ RBAC鉴权失败。{str(e)}"
            else:
                if(user_id):
                    redis_service.save_chat_message(user_id, "⚠️ JWT Token鉴权失败")
                    logging.info("⚠️ JWT Token鉴权失败")
                return "Error", f"⚠️ JWT Token鉴权失败。{str(e)}"


            logging.info(f"用户ID: {user_id}")

            if "健康监测" in user_input:
                agent_name, response = await self._bracelet_asistant(user_input, user_id, user_info)
                #对话消息存入缓存               
                print("🎯🎯🎯 存入缓存！🎯🎯🎯")
                # 格式化数据
                formatted_data = self.format_health_data(response["answer"])
                # 获取格式化字符串
                formatted_string = self.format_data_to_string(formatted_data)
                print(formatted_string)
                # report_string = (f"📊 已发送手环健康数据报告到私人医生智能体 ")
                # redis_service.save_chat_message(user_id, report_string)
                redis_service.save_chat_message(user_id, formatted_string)
                history = redis_service.get_chat_history(user_id)
                print(history)
                print("🎯🎯🎯 存入缓存！🎯🎯🎯")
                result = self.process_health_data_from_json(response["answer"])
                result_str = json.dumps(result, indent=2, ensure_ascii=False)
                # 构建响应
                newResponse = {
                    "answer": result_str
                }
                return "HealthWatch", newResponse

            if "内科" in user_input and "健康监测" not in user_input:
                print("=================================第一次请求================================")
                mcp_server_url = MCP_URL + "/sse"
                server = Server(name="user_agent_request", token=token, server_url=mcp_server_url, config=None, transport_type="streamable-http")
                await server.initialize()
                department = "内分泌科"
                result = await server.execute_tool("query_hospital_medical_data", {
                    "department": department,
                    "user_id": user_id
                })
                result_dict = result.model_dump()
                structured_content = result_dict.get('structuredContent')
                # type = structured_content["datas"][0]["data_types"]
                # department = structured_content["datas"][0]["department"]
                await server.cleanup()


                for i, item in enumerate(structured_content["datas"]):
                    print("item:",item)
                    item["user_id"] = user_id
                    jwt_generate_result = self.auth_service.jwt_generate(url=JWR_URL,json_data={"payload": item})
                    jwt_generate_token = jwt_generate_result['token']
                    item["access_token"] = jwt_generate_token                  
                # jwt_generate_result = self.auth_service.jwt_generate(url=JWR_URL,json_data={"payload": structured_content})
                # jwt_generate_token = jwt_generate_result['token']
                # structured_content["access_token"] = jwt_generate_token
                structured_content_str = json.dumps(structured_content, ensure_ascii=False, indent=2)
                print("structured_content_str:",structured_content_str)               
                # 构建响应
                newResponse = {
                    "answer": structured_content_str
                }
                return "Hostiptal", newResponse
            

            # 获取对话上下文
            logging.info(f"[{self.name}] 获取对话历史")
            context = self.get_context_from_memory(user_id)
            logging.info(f"[{self.name}] 获取到对话历史：\n{context}")
            
            # 获取对话状态
            logging.info(f"[{self.name}] 获取对话状态")
            conversation_state = self._get_conversation_state(user_id)
            logging.info(f"[{self.name}] 当前对话状态: {conversation_state}")
            
            # 智能助理流程
            logging.info(f"[{self.name}] 进入回答阶段")
            # 进行意图识别和初步分析
            return await self._initial_asistant(user_input, user_id, user_info, context)

            
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

    async def _initial_asistant(self, user_input: str, user_id: str, user_info: Optional[Dict], context: str) -> Tuple[str, Any]:
        """
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            logging.info(f"[{self.name}] 开始初次回答阶段")
            
            # 医生式问候
            logging.info(f"[{self.name}] 开始生成助理回答")
            answer = await self._generate_answer(user_input, user_info)
            logging.info(f"[{self.name}] 回答生成完成: {answer[:50]}...")
                    
            # 构建响应
            response = {
                "answer": answer,
                "phase": "questioning"
            }
            
            # 记录对话轮次
            #self.dialogue_memory.add_turn(user_id, user_input, self.name, f"初次询问，识别意图：{intent}")
            
            return "PrivateAssistant", response
            
        except Exception as e:
            logging.error(f"[{self.name}] 初次回答失败: {str(e)}")
            return "Error", f"抱歉，我在分析您的问题时遇到了困难，请重新描述一下您的问题。"   

    async def _judge_asistant(self, user_input: str, user_id: str, user_info: Optional[Dict]) -> Tuple[str, Any]:
        """
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            logging.info(f"[{self.name}] 开始初次回答阶段")
            
            # 医生式问候
            logging.info(f"[{self.name}] 开始生成助理回答")
            answer = await self._judge_answer(user_input, user_info)
            logging.info(f"[{self.name}] 回答生成完成: {answer[:50]}...")
                    
            # 构建响应
            response = answer
                    
            return "JudgeAssistant", response
            
        except Exception as e:
            logging.error(f"[{self.name}] 初次回答失败: {str(e)}")
            return "Error", f"抱歉，我在分析您的问题时遇到了困难，请重新描述一下您的问题。"  

    async def _bracelet_asistant(self, user_input: str, user_id: str, user_info: Optional[Dict]) -> Tuple[str, Any]:
        """
        
        参数：
            user_input (str): 用户输入
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            context (str): 对话上下文
            
        返回：
            Tuple[str, Any]: 智能体名称和结果
        """
        try:
            logging.info(f"[{self.name}] 开始进入手环回答阶段")
            
            # 医生式问候
            logging.info(f"[{self.name}] 开始生成手环助理回答")
            
            # 获取当前文件的路径
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            # 构建 bracelet.json 的路径
            file_path = os.path.join(root_dir, 'data', 'bracelet.json')
            json_string = ''
            print(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                dates = [(datetime.today() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
                for item, d in zip(json_data, dates):
                    item["date"] = d
                json_string = json.dumps(json_data)
            print(json_data)
           
            logging.info(f"[{self.name}] 回答生成完成: {json_string[:50]}...")
                    
            # 构建响应
            response = {
                "answer": json_string,
                "phase": "bracelet_asistant"
            }
                        
            return "PrivateAssistant", response
            
        except Exception as e:
            logging.error(f"[{self.name}] 初次回答失败: {str(e)}")
            return "Error", f"抱歉，我在分析您的问题时遇到了困难，请重新描述一下您的问题。"   



    # ==================== 辅助方法 ====================

    def _save_assistant_message(self, user_id: str, content: str):
        """保存助手回复"""
        try:
            redis_service = RedisService()
            redis_service.save_chat_message(user_id, content)
        except Exception as e:
            logging.warning(f"保存助手消息失败: {e}")

    async def _generate_answer(self, user_input: str, user_info: Optional[Dict]) -> str:
        try:
            answer_prompt = f"""作为一位私人助理，请耐心回答客人问题：

客人描述：{user_input}

请用亲切的语气回答客人，专业的解答客人的问题。
应该遵循以下原则：
1. 不替用户做决定，每次重大行动前用一句话向用户确认。
2. 绝不在任何对话或日志中泄露用户真名、地址、密码、密钥。
3. 优先调用已注册工具解决实际问题，无工具时坦诚说明局限。
5. 体现私人助理的专业性。
4. 长度控制在50字以内

请直接返回回答："""
            
            answer = await self.caller(answer_prompt, self.model_config)
            return answer.strip()
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成助理回答失败: {str(e)}")
            return "您好，我是您的私人助理。让我们一起来仔细了解您的情况。"   

    async def _judge_answer(self, user_input: str, user_info: Optional[Dict]) -> str:
        try:
            answer_prompt = f"""请判断用户的问题是否属于个人身体健康，身体状况相关的问题，如果是请回复'True',如果不是请回复'False'：

客人描述：{user_input}

请按指定内容进行回复

请直接返回回答："""
            
            answer = await self.caller(answer_prompt, self.model_config)
            return answer.strip()
            
        except Exception as e:
            logging.error(f"[{self.name}] 生成助理回答失败: {str(e)}")
            return "您好，我是您的私人助理。让我们一起来仔细了解您的情况。"  

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

    @staticmethod
    def format_health_data(data) -> List[Dict[str, Any]]:
        """
        格式化健康数据，以美观的中文形式呈现
        支持字符串、字典列表、单个字典等多种输入格式
        """
        # 处理不同类型的输入
        if isinstance(data, str):
            try:
                # 如果是JSON字符串，解析为Python对象
                parsed_data = json.loads(data)
                # 确保是列表格式
                if isinstance(parsed_data, dict):
                    data = [parsed_data]
                else:
                    data = parsed_data
            except json.JSONDecodeError as e:
                raise ValueError(f"无法解析JSON字符串: {e}")
        
        elif isinstance(data, dict):
            # 如果是单个字典，转换为列表
            data = [data]
        
        # 确保数据是列表类型
        if not isinstance(data, list):
            raise TypeError(f"期望列表类型，但得到 {type(data)}")
        
        # 验证列表中的每个元素都是字典
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise TypeError(f"列表中的第 {i} 个元素应该是字典，但得到 {type(item)}")
        
        print(f"调试信息: 数据长度 = {len(data)}, 数据类型 = {type(data)}")
        if data:
            print(f"调试信息: 第一个元素类型 = {type(data[0])}")
            print(f"调试信息: 第一个元素键 = {list(data[0].keys())}")

        # 中文释义映射
        field_names = {
            "date": "日期",
            "heart_rate": "心率指标",
            "avg_bpm": "平均心率",
            "max_bpm": "最高心率", 
            "min_bpm": "最低心率",
            "resting_bpm": "静息心率",
            "blood_glucose": "血糖指标",
            "morning_mmol": "早晨空腹血糖",
            "evening_mmol": "晚间餐后血糖",
            "sleep": "睡眠指标",
            "total_minutes": "总睡眠时长",
            "deep_minutes": "深睡时长",
            "light_minutes": "浅睡时长", 
            "rem_minutes": "快速眼动期",
            "bedtime": "入睡时间",
            "wake_time": "醒来时间",
            "steps": "步数",
            "distance_km": "步行距离",
            "calories_kcal": "消耗热量",
            "stress_level": "压力指数",
            "spo2_percent": "血氧饱和度",
            "skin_temp_celsius": "皮肤温度"
        }
        
        # 单位映射
        units = {
            "avg_bpm": "次/分钟",
            "max_bpm": "次/分钟", 
            "min_bpm": "次/分钟",
            "resting_bpm": "次/分钟",
            "morning_mmol": "mmol/L",
            "evening_mmol": "mmol/L",
            "total_minutes": "分钟",
            "deep_minutes": "分钟",
            "light_minutes": "分钟",
            "rem_minutes": "分钟",
            "steps": "步",
            "distance_km": "公里",
            "calories_kcal": "千卡",
            "stress_level": "",
            "spo2_percent": "%",
            "skin_temp_celsius": "°C"
        }
        
        result = []
        
        for day_index, day_data in enumerate(data):
            try:
                # 移除用户标识信息
                formatted_data = {}
                
                # 基本信息 - 添加类型转换确保安全
                formatted_data[field_names["date"]] = str(day_data.get("date", "未知日期"))
                
                # 心率数据
                hr_data = day_data.get("heart_rate", {})
                formatted_data[field_names["heart_rate"]] = {
                    field_names["avg_bpm"]: f"{int(hr_data.get('avg_bpm', 0))} {units['avg_bpm']}",
                    field_names["max_bpm"]: f"{int(hr_data.get('max_bpm', 0))} {units['max_bpm']}",
                    field_names["min_bpm"]: f"{int(hr_data.get('min_bpm', 0))} {units['min_bpm']}",
                    field_names["resting_bpm"]: f"{int(hr_data.get('resting_bpm', 0))} {units['resting_bpm']}"
                }
                
                # 血糖数据
                bg_data = day_data.get("blood_glucose", {})
                formatted_data[field_names["blood_glucose"]] = {
                    field_names["morning_mmol"]: f"{float(bg_data.get('morning_mmol', 0))} {units['morning_mmol']}",
                    field_names["evening_mmol"]: f"{float(bg_data.get('evening_mmol', 0))} {units['evening_mmol']}"
                }
                
                # 睡眠数据 - 转换分钟为小时分钟格式
                sleep_data = day_data.get("sleep", {})
                def format_minutes(minutes):
                    minutes_int = int(minutes)
                    hours = minutes_int // 60
                    mins = minutes_int % 60
                    return f"{hours}小时{mins}分钟"
                
                formatted_data[field_names["sleep"]] = {
                    field_names["total_minutes"]: format_minutes(sleep_data.get("total_minutes", 0)),
                    field_names["deep_minutes"]: format_minutes(sleep_data.get("deep_minutes", 0)),
                    field_names["light_minutes"]: format_minutes(sleep_data.get("light_minutes", 0)),
                    field_names["rem_minutes"]: format_minutes(sleep_data.get("rem_minutes", 0)),
                    field_names["bedtime"]: str(sleep_data.get("bedtime", "未知")),
                    field_names["wake_time"]: str(sleep_data.get("wake_time", "未知"))
                }
                
                # 活动数据
                formatted_data[field_names["steps"]] = f"{int(day_data.get('steps', 0)):,} {units['steps']}"
                formatted_data[field_names["distance_km"]] = f"{float(day_data.get('distance_km', 0))} {units['distance_km']}"
                formatted_data[field_names["calories_kcal"]] = f"{int(day_data.get('calories_kcal', 0))} {units['calories_kcal']}"
                
                # 其他指标
                formatted_data[field_names["stress_level"]] = f"{int(day_data.get('stress_level', 0))}{units['stress_level']}"
                formatted_data[field_names["spo2_percent"]] = f"{int(day_data.get('spo2_percent', 0))}{units['spo2_percent']}"
                formatted_data[field_names["skin_temp_celsius"]] = f"{float(day_data.get('skin_temp_celsius', 0))}{units['skin_temp_celsius']}"
                
                result.append(formatted_data)
                
            except Exception as e:
                print(f"处理第 {day_index + 1} 天数据时出错: {e}")
                continue
        
        return result

    @staticmethod
    def format_data_to_string(formatted_data):
        """
        将格式化后的数据转换为字符串
        返回: 包含所有格式化信息的字符串
        """
        output_lines = []
        
        output_lines.append(f"📊 已发送手环健康数据报告到私人医生智能体 ")
        for i, day_data in enumerate(formatted_data, 1):
            output_lines.append(f"\n{'='*55}")
            output_lines.append(f"📊 手环健康数据报告 - 第{i}天")
            output_lines.append(f"{'='*55}")
            
            output_lines.append(f"📅 {day_data['日期']}")
            output_lines.append("")
            
            # 心率指标
            output_lines.append("❤️  心率指标:")
            hr_data = day_data['心率指标']
            for key, value in hr_data.items():
                output_lines.append(f"   • {key}: {value}")
            output_lines.append("")
            
            # 血糖指标
            output_lines.append("🩸 血糖指标:")
            bg_data = day_data['血糖指标']
            for key, value in bg_data.items():
                output_lines.append(f"   • {key}: {value}")
            output_lines.append("")
            
            # 睡眠指标
            output_lines.append("😴 睡眠指标:")
            sleep_data = day_data['睡眠指标']
            for key, value in sleep_data.items():
                if key in ['入睡时间', '醒来时间']:
                    output_lines.append(f"   • {key}: {value}")
                else:
                    output_lines.append(f"   • {key}: {value}")
            output_lines.append("")
            
            # 活动数据
            output_lines.append("🚶 活动数据:")
            output_lines.append(f"   • 步数: {day_data['步数']}")
            output_lines.append(f"   • 步行距离: {day_data['步行距离']}")
            output_lines.append(f"   • 消耗热量: {day_data['消耗热量']}")
            output_lines.append("")
            
            # 其他指标
            output_lines.append("📈 其他指标:")
            output_lines.append(f"   • 压力指数: {day_data['压力指数']}")
            output_lines.append(f"   • 血氧饱和度: {day_data['血氧饱和度']}")
            output_lines.append(f"   • 皮肤温度: {day_data['皮肤温度']}")
        
        return "\n".join(output_lines)
    
    def process_health_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理健康数据，提取最近一天的数据并转换为指定格式
        
        Args:
            raw_data: 原始健康数据列表
            
        Returns:
            Dict: 处理后的健康数据格式
        """
        if not raw_data:
            return self.create_empty_response()
        
        # 找到最近一天的数据（按日期排序）
        sorted_data = sorted(raw_data, key=lambda x: x['date'], reverse=True)
        latest_data = sorted_data[0]
        
        # 构建响应数据
        result = {
            "health_monitoring": {
                "blood_pressure": {
                    "systolic": latest_data['heart_rate']['max_bpm'],  # 使用最高心率作为收缩压
                    "diastolic": latest_data['heart_rate']['min_bpm'], # 使用最低心率作为舒张压
                    "unit": "mmHg",
                    "timestamp": latest_data['date']
                },
                "blood_glucose": {
                    "value": latest_data['blood_glucose']['evening_mmol'],  # 使用晚间血糖值
                    "unit": "mmol/L",
                    "timestamp": latest_data['date']
                },
                "heart_rate": {
                    "value": latest_data['heart_rate']['avg_bpm'],  # 使用平均心率
                    "unit": "bpm",
                    "timestamp": latest_data['date']
                },
                "body_temperature": {
                    "value": latest_data['skin_temp_celsius'],  # 使用皮肤温度作为体温
                    "unit": "°C",
                    "timestamp": latest_data['date']
                }
            },
            "available_data_types": ["健康监测数据"]
        }
        
        return result

    def create_empty_response() -> Dict[str, Any]:
        """创建空数据响应"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return {
            "health_monitoring": {
                "blood_pressure": {
                    "systolic": 0,
                    "diastolic": 0,
                    "unit": "mmHg",
                    "timestamp": current_date
                },
                "blood_glucose": {
                    "value": 0.0,
                    "unit": "mmol/L",
                    "timestamp": current_date
                },
                "heart_rate": {
                    "value": 0,
                    "unit": "bpm",
                    "timestamp": current_date
                },
                "body_temperature": {
                    "value": 0.0,
                    "unit": "°C",
                    "timestamp": current_date
                }
            },
            "available_data_types": ["健康监测数据"]
        }

    def process_health_data_from_json(self, json_str: str) -> Dict[str, Any]:
        """
        从 JSON 字符串处理健康数据
        
        Args:
            json_str: JSON 格式的字符串数据
            
        Returns:
            Dict: 处理后的健康数据格式
        """
        try:
            # 解析 JSON 字符串
            raw_data = json.loads(json_str)
            return self.process_health_data(raw_data)
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return self.create_empty_response()
        except Exception as e:
            print(f"数据处理错误: {e}")
            return self.create_empty_response()


class UserAgentExecutor(AgentExecutor):
    def __init__(self, agent: UserAgent) -> None:
        self.agent = agent
    
    # 必须实现execute和cancel方法
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # 给request对应的response

        message = {
            #"role": "user" if context.message.role == "user" else "assistant",
            # "user_id": context.message.metadata.get("user_id"),
            "token": context.message.metadata.get("token"),
            "user_input": context.get_user_input(),
        }
        #messages = [message]

        logging.info(message)
        # message['user_input'] = message.pop('content')
        # message['user_id'] = "111"
        # logging.info(message)

        # 找到当前任务
        task = context.current_task
        if not task:
            task = new_task(context.message)
            context.current_task = task
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            # 解析了A2A Client发来的请求，就可以让Server智能体干活了，按照正常逻辑进行调用，需要注意执行过程和结束都需要跟Client保持通信，要不断更新当前任务的状态
            response = await self.agent.a2aExecute(**message)

            # 解析响应
            logging.info(response)
            agent_name, response_dict = response
            content = response_dict['answer']
            await updater.add_artifact(
                parts=[Part(root=TextPart(text=content))],
                name="result",
                last_chunk=True,
            )
            await updater.complete()


            # is_final_answer = response.get("is_final_answer")
            # content = response.get("content")

            # if not is_final_answer:
            #     await updater.update_status(
            #         TaskState.working,
            #         new_agent_text_message(
            #             content,
            #             task.context_id,
            #             task.id,
            #         ),
            #     )
            # else:
            #     # 任务完成了，加一个工件artifact
            #     await updater.add_artifact(
            #         parts=[Part(root=TextPart(text=content))],
            #         name="coding_result",
            #         last_chunk=True,
            #     )
            #     await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    str(e),
                    task.context_id,
                    task.id,
                ),
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")