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
聊天服务
========

提供智能体对话、聊天历史管理等服务

作者: AI开发团队
版本: 1.0
"""

import logging
import sys
import os
import asyncio
import time
from typing import Optional, Dict, Any, List, AsyncGenerator
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.agents.coordinator.cybertwin_agent import CybertwinAgent, CybertwinConfig
from shared.agents.coordinator.user_agent import CybertwinConfig, UserAgent
from shared.config.model_config import get_config

logger = logging.getLogger(__name__)

class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        """初始化聊天服务"""
        logger.info("=" * 80)
        logger.info("[ChatService] 开始初始化聊天服务...")
        self.cybertwin_agent = None
        self._init_cybertwin_agent()
        logger.info("[ChatService] 聊天服务初始化完成")
        logger.info("=" * 80)
    
    def _init_cybertwin_agent(self):
        """初始化Cybertwin智能体"""
        try:
            logger.info("[ChatService] 开始初始化Cybertwin智能体...")
            
            # 创建CybertwinAgent配置
            logger.info("[ChatService] 获取模型配置...")
            model_config = get_config("qwen")  # 使用qwen-3b模型
            logger.info(f"[ChatService] 模型配置获取成功: {model_config.model_name}")
            
            cybertwin_config = CybertwinConfig(
                model_config=model_config.to_dict(),
                enable_auth=False,  # 在服务层处理认证
                enable_audit=False,  # 在服务层处理审计
                max_context_length=4000,
                intent_threshold=0.7
            )
            logger.info("[ChatService] 创建CybertwinAgent配置成功")
            
            # 初始化智能体
            logger.info("[ChatService] 创建CybertwinAgent实例...")
            # self.cybertwin_agent = CybertwinAgent(cybertwin_config)
            self.cybertwin_agent = UserAgent(cybertwin_config)
            logger.info("=" * 80)
            logger.info("✅ Cybertwin智能体初始化完成")
            logger.info("=" * 80)
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ Cybertwin智能体初始化失败: {str(e)}")
            logger.error("=" * 80)
            import traceback
            logger.error(traceback.format_exc())
            self.cybertwin_agent = None
    
    async def handle_chat(self, user_input: str, user_id: str, user_info: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        处理聊天消息
        
        参数:
            user_input: 用户输入
            user_id: 用户ID
            user_info: 用户信息
            context: 对话上下文
            
        返回:
            Optional[Dict[str, Any]]: 聊天响应
        """
        try:
            print("\n" + "📞" * 40)
            print("📞 聊天服务开始处理消息...")
            print(f"📞 用户ID: {user_id}")
            print(f"📞 消息: {user_input[:50]}...")
            print("📞" * 40 + "\n")
            
            if not self.cybertwin_agent:
                logger.error("Cybertwin智能体未初始化")
                print("❌ ERROR: Cybertwin智能体未初始化")
                return None
            
            logger.info(f"[聊天服务] 开始处理用户 {user_id} 的聊天消息: {user_input[:50]}...")
            logger.info(f"[聊天服务] 用户信息: {user_info}")
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 调用CybertwinAgent处理聊天
            print("🤖 准备调用CybertwinAgent处理聊天...")
            logger.info(f"[聊天服务] 开始调用CybertwinAgent.execute()")
            intent, result = await self.cybertwin_agent.safe_execute(user_input, user_id, user_info)
            print(f"✅ CybertwinAgent处理完成！")
            
            # 记录处理时间
            processing_time = time.time() - start_time
            logger.info(f"[聊天服务] CybertwinAgent处理完成，耗时: {processing_time:.2f}秒")
            logger.info(f"[聊天服务] 返回结果 - 智能体: {intent}, 结果类型: {type(result)}")
            
            # 存储聊天记录
            logger.info(f"[聊天服务] 开始存储聊天记录")
            # await self._store_chat_message(user_id, "user", user_input)
            # await self._store_chat_message(user_id, "assistant", str(result))
            
            # 构建响应
            response = {
                "agent_name": intent,
                "response": self._format_response_for_frontend(intent, result),
                "metadata": self._build_metadata(intent, result, user_id),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[聊天服务] 聊天处理完成: {intent}, 总耗时: {processing_time:.2f}秒")
            return response
            
        except Exception as e:
            logger.error(f"[聊天服务] 聊天处理失败: {str(e)}", exc_info=True)
            return None

    async def judge_chat(self, user_input: str, user_id: str, user_info: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        处理聊天消息
        
        参数:
            user_input: 用户输入
            user_id: 用户ID
            user_info: 用户信息
            context: 对话上下文
            
        返回:
            Optional[Dict[str, Any]]: 聊天响应
        """
        try:
            print("\n" + "📞" * 40)
            print("📞 聊天服务开始处理消息...")
            print(f"📞 用户ID: {user_id}")
            print(f"📞 消息: {user_input[:50]}...")
            print("📞" * 40 + "\n")
            
            if not self.cybertwin_agent:
                logger.error("Cybertwin智能体未初始化")
                print("❌ ERROR: Cybertwin智能体未初始化")
                return None
            
            logger.info(f"[聊天服务] 开始处理用户 {user_id} 的聊天消息: {user_input[:50]}...")
            logger.info(f"[聊天服务] 用户信息: {user_info}")
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 调用CybertwinAgent处理聊天
            print("🤖 准备调用CybertwinAgent处理聊天...")
            logger.info(f"[聊天服务] 开始调用CybertwinAgent.execute()")
            intent, result = await self.cybertwin_agent.judge(user_input, user_id, user_info)
            print(f"✅ CybertwinAgent处理完成！")
            
            # 记录处理时间
            processing_time = time.time() - start_time
            logger.info(f"[聊天服务] CybertwinAgent处理完成，耗时: {processing_time:.2f}秒")
            logger.info(f"[聊天服务] 返回结果 - 智能体: {intent}, 结果类型: {type(result)}")
                       
            # 构建响应
            response = {
                "agent_name": intent,
                "response": self._format_response_for_frontend(intent, result),
                "metadata": self._build_metadata(intent, result, user_id),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[聊天服务] 聊天处理完成: {intent}, 总耗时: {processing_time:.2f}秒")
            return response
            
        except Exception as e:
            logger.error(f"[聊天服务] 聊天处理失败: {str(e)}", exc_info=True)
            return None

    async def get_available_agents(self, user_role: str) -> List[Dict[str, Any]]:
        """
        获取可用智能体列表
        
        参数:
            user_role: 用户角色
            
        返回:
            List[Dict[str, Any]]: 智能体列表
        """
        try:
            # 根据用户角色返回可用智能体
            agents = []
            
            # 基础智能体（所有角色都可访问）
            agents.extend([
                {
                    "agent_id": "cybertwin",
                    "name": "数字孪生智能体",
                    "description": "意图识别和任务分发",
                    "available": True
                },
                {
                    "agent_id": "internal_medicine",
                    "name": "内科智能体",
                    "description": "内科诊断和建议",
                    "available": True
                },
                {
                    "agent_id": "surgical",
                    "name": "外科智能体",
                    "description": "外科诊断和建议",
                    "available": True
                }
            ])
            
            # 根据角色添加特殊智能体
            if user_role in ["doctor", "admin"]:
                agents.extend([
                    {
                        "agent_id": "image_analysis",
                        "name": "影像分析智能体",
                        "description": "医疗影像分析",
                        "available": True
                    },
                    {
                        "agent_id": "permission_admin",
                        "name": "权限管理智能体",
                        "description": "权限管理功能",
                        "available": True
                    }
                ])
            
            return agents
            
        except Exception as e:
            logger.error(f"获取智能体列表失败: {str(e)}")
            return []
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取智能体状态
        
        参数:
            agent_id: 智能体ID
            
        返回:
            Optional[Dict[str, Any]]: 智能体状态
        """
        try:
            if agent_id == "cybertwin" and self.cybertwin_agent:
                return {
                    "agent_id": agent_id,
                    "status": "active",
                    "name": self.cybertwin_agent.name,
                    "description": "数字孪生智能体，负责意图识别和任务分发",
                    "capabilities": [
                        "意图识别",
                        "任务分发",
                        "权限控制",
                        "结果汇总",
                        "分诊建议"
                    ],
                    "last_activity": datetime.now().isoformat()
                }
            else:
                return {
                    "agent_id": agent_id,
                    "status": "inactive",
                    "message": "智能体不可用"
                }
                
        except Exception as e:
            logger.error(f"获取智能体状态失败: {str(e)}")
            return None
    
    def _format_response_for_frontend(self, intent: str, result: Any) -> str:
        """
        格式化响应内容供前端显示
        
        参数:
            intent: 智能体名称
            result: 智能体返回结果
            
        返回:
            str: 格式化后的响应内容
        """
        try:
            logger.info(f"[格式化响应] 意图: {intent}, 结果类型: {type(result)}")
            logger.info(f"[格式化响应] 结果内容: {result}")
            
            # 如果result是字典类型，根据intent进行格式化
            if isinstance(result, dict):
                if intent == "DoctorQuestioning":
                    # 追问阶段：只显示问候语和问题
                    greeting = result.get("greeting", "")
                    questions = result.get("questions", [])
                    
                    # 构建用户友好的响应
                    response_parts = [greeting] if greeting else []
                    
                    if questions:
                        response_parts.append("\n为了更好地帮助您，我需要了解一些详细信息：")
                        for i, question in enumerate(questions, 1):
                            response_parts.append(f"{i}. {question}")
                    
                    return "\n".join(response_parts)
                
                elif intent == "DoctorConsultation":
                    # 初次问诊：只显示问候语和问题
                    greeting = result.get("greeting", "")
                    questions = result.get("questions", [])
                    
                    response_parts = [greeting] if greeting else []
                    
                    if questions:
                        response_parts.append("\n为了更好地帮助您，我需要了解一些详细信息：")
                        for i, question in enumerate(questions, 1):
                            response_parts.append(f"{i}. {question}")
                    
                    return "\n".join(response_parts)
                
                elif intent == "InternalMedicineAgent":
                    # 内科诊断结果：优先显示医生报告，更友好和条理化
                    logger.info(f"[格式化响应] 处理内科诊断结果")
                    if "doctor_report" in result and result["doctor_report"]:
                        logger.info(f"[格式化响应] 找到doctor_report字段，使用医生报告")
                        return result["doctor_report"]
                    elif "diagnosis" in result and result["diagnosis"]:
                        logger.info(f"[格式化响应] 使用diagnosis字段")
                        return result["diagnosis"]
                    else:
                        logger.info(f"[格式化响应] 未找到有效字段，使用默认消息")
                        return "感谢您的咨询，建议您及时就医进行详细检查。"
                
                elif intent == "SurgicalAgent":
                    # 外科诊断结果：优先显示医生报告，更友好和条理化
                    logger.info(f"[格式化响应] 处理外科诊断结果")
                    if "doctor_report" in result and result["doctor_report"]:
                        logger.info(f"[格式化响应] 找到doctor_report字段，使用医生报告")
                        return result["doctor_report"]
                    elif "summary" in result and result["summary"]:
                        logger.info(f"[格式化响应] 使用summary字段")
                        return result["summary"]
                    elif "diagnosis" in result and result["diagnosis"]:
                        logger.info(f"[格式化响应] 使用diagnosis字段")
                        return result["diagnosis"]
                    else:
                        logger.info(f"[格式化响应] 未找到有效字段，使用默认消息")
                        return "感谢您的咨询，建议您及时就医进行详细检查。"
                
                elif intent in ["ImageAnalysis", "MedicalAnalysis"]:
                    # 分析结果：显示主要分析内容
                    logger.info(f"[格式化响应] 处理影像分析结果，查找comprehensive_analysis字段")
                    if "comprehensive_analysis" in result:
                        # 跨医院协作分析结果
                        logger.info(f"[格式化响应] 找到comprehensive_analysis字段: {result['comprehensive_analysis'][:100]}...")
                        return result["comprehensive_analysis"]
                    elif "analysis_result" in result:
                        logger.info(f"[格式化响应] 找到analysis_result字段")
                        return result["analysis_result"]
                    elif "diagnosis" in result:
                        logger.info(f"[格式化响应] 找到diagnosis字段")
                        return result["diagnosis"]
                    elif "summary" in result:
                        logger.info(f"[格式化响应] 找到summary字段")
                        return result["summary"]
                    elif "analysis" in result:
                        logger.info(f"[格式化响应] 找到analysis字段")
                        return result["analysis"]
                    else:
                        # 如果没有找到标准字段，返回第一个字符串值
                        logger.info(f"[格式化响应] 未找到标准字段，查找其他字符串值")
                        for key, value in result.items():
                            if isinstance(value, str) and len(value) > 10:
                                logger.info(f"[格式化响应] 找到字符串字段 {key}: {value[:100]}...")
                                return value
                
                # 其他情况：尝试提取主要信息
                if "message" in result:
                    return result["message"]
                elif "response" in result:
                    return result["response"]
                elif "content" in result:
                    return result["content"]
                else:
                    # 如果都没有，返回第一个字符串值
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 10:
                            return value
            
            # 如果result不是字典，直接转换为字符串
            return str(result)
            
        except Exception as e:
            logger.error(f"格式化响应失败: {str(e)}")
            return str(result)
    
    def _build_metadata(self, intent: str, result: Any, user_id: str) -> Dict[str, Any]:
        """
        构建元数据
        
        参数:
            intent: 智能体名称
            result: 智能体返回结果
            user_id: 用户ID
            
        返回:
            Dict[str, Any]: 元数据
        """
        try:
            metadata = {
                "intent": intent,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # 如果result是字典，提取有用的元数据
            if isinstance(result, dict):
                # 提取阶段信息
                if "phase" in result:
                    metadata["phase"] = result["phase"]
                
                # 提取完整性分析（用于内部处理）
                if "completeness_analysis" in result:
                    metadata["completeness_analysis"] = result["completeness_analysis"]
                
                # 提取其他有用的元数据
                for key in ["round", "max_rounds", "encouragement", "needs_more_info"]:
                    if key in result:
                        metadata[key] = result[key]
            
            return metadata
            
        except Exception as e:
            logger.error(f"构建元数据失败: {str(e)}")
            return {
                "intent": intent,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }

    # async def _store_chat_message(self, user_id: str, role: str, content: str) -> bool:
    #     """
    #     存储聊天消息
        
    #     参数:
    #         user_id: 用户ID
    #         role: 消息角色
    #         content: 消息内容
            
    #     返回:
    #         bool: 存储结果
    #     """
    #     try:
    #         db = get_database()
    #         if not db:
    #             logger.error("数据库连接失败")
    #             return False
            
    #         # 插入聊天消息
    #         query = """
    #             INSERT INTO history (user_id, role, content, timestamp)
    #             VALUES (?, ?, ?, ?)
    #         """
    #         cursor = db.cursor()
    #         cursor.execute(query, (user_id, role, content, datetime.now()))
    #         db.commit()
            
    #         return True
            
        except Exception as e:
            logger.error(f"存储聊天消息失败: {str(e)}")
            return False
