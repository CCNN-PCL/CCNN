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
两轮诊断协调器 (TwoRoundDiagnosisCoordinator)
============================================

协调两轮诊断流程：
- 第一轮：获取初始数据，进行初步诊断
- 第二轮：请求补充健康监测数据，进行深入诊断

作者: QSIR
版本: 1.0
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from agents.utils.shared_context import SharedContext
from agents.coordinator.location_router import LocationRouter
from agents.coordinator.data_proxy_client import DataProxyClient, DataProxyConfig


class TwoRoundDiagnosisCoordinator:
    """两轮诊断协调器"""
    
    # 意图到专科类型的映射（简化版）
    INTENT_TO_SPECIALTY = {
        "内科咨询": "internal_medicine",
        "外科咨询": "surgical",
        "影像分析": "internal_medicine",  # 影像分析暂时路由到内科
        "药物查询": "internal_medicine",  # 药物查询路由到内科
        "一般问题": "internal_medicine",  # 一般问题路由到内科
        "未知": "internal_medicine"       # 未知意图路由到内科
    }
    
    def __init__(self, specialists: Dict[str, Dict[str, Any]], token: Optional[str] = None):
        """
        初始化两轮诊断协调器
        
        参数:
            specialists: 专科医生实例字典
            token: JWT token，用于 EntryAgent 认证（可选）
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.specialists = specialists
        self.location_router = LocationRouter()
        
        # 初始化数据代理客户端
        config = DataProxyConfig(token=token)  # 传递 token 到配置
        self.data_proxy_client = DataProxyClient(config)
        
        if token:
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 初始化完成，已设置 token: {token[:20]}...")
        else:
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 初始化完成（未设置 token）")
    
    def _map_intent_to_specialty(self, intent: str) -> str:
        """
        将意图映射到专科类型
        
        参数:
            intent: 意图类型
            
        返回:
            str: 专科类型
        """
        return self.INTENT_TO_SPECIALTY.get(intent, "internal_medicine")
    
    def _get_specialist(self, specialty_type: str, location: str):
        """
        获取专科医生服务配置（微服务拆分后）
        
        参数:
            specialty_type: 专科类型
            location: 地域
            
        返回:
            服务配置字典或None
        """
        try:
            return self.specialists.get(specialty_type, {}).get(location)
        except Exception as e:
            self.logger.error(f"[TwoRoundDiagnosisCoordinator] 获取专科医生配置失败: {str(e)}")
            return None
    
    async def first_round_diagnosis(
        self,
        user_input: str,
        user_id: str,
        data_addresses: List[Dict[str, Any]],
        shared_context: SharedContext,
        intent: str,
        user_info: Optional[Dict[str, Any]] = None,
        diagnosis_logger=None
    ) -> Dict[str, Any]:
        """
        第一轮诊断
        
        参数:
            user_input: 用户输入
            user_id: 用户ID
            data_addresses: 数据地址列表
            shared_context: 共享上下文
            intent: 识别的意图（如：内科咨询、外科咨询等）
            user_info: 用户信息，包含userid、username、id_token等字段
            # 注意：影像分析暂时已注释掉
            
        返回:
            Dict[str, Any]: 第一轮诊断结果（包含intent字段）
        """
        try:
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 开始第一轮诊断，意图: {intent}")
            
            # 打印第一轮诊断开始信息
            print(f"\n[第一轮诊断] 开始诊断")
            print(f"  意图: {intent}")
            print(f"  数据地址数量: {len(data_addresses)}")
            
            # 1. 按地域分组数据地址
            location_groups = self.location_router.group_data_addresses_by_location(
                data_addresses
            )
            
            print(f"  地域分组: {list(location_groups.keys())}")
            for location, addresses in location_groups.items():
                print(f"    - {location}: {len(addresses)} 个数据地址")
            
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 数据地址按地域分组: {list(location_groups.keys())}")
            
            # 记录数据地址接收
            if diagnosis_logger:
                await diagnosis_logger.log_data_addresses_received(
                    round_num=1,
                    data_addresses=data_addresses,
                    has_direct_data=False
                )
            
            # 2. 根据意图路由到对应地域专科医生
            # 注意：这里需要根据意图确定专科类型
            specialty_type = self._map_intent_to_specialty(intent)
            print(f"  专科类型: {specialty_type}")
            
            # 记录路由
            if diagnosis_logger:
                await diagnosis_logger.log_routing(
                    location_groups, 
                    specialty_type,
                    service_configs=self.specialists
                )
            
            specialist_tasks = []
            task_info_list = []  # 保存每个任务对应的信息：(location, addresses, specialty)
            for location, addresses in location_groups.items():
                service_config = self._get_specialist(specialty_type, location)
                if service_config:
                    self.logger.info(f"[TwoRoundDiagnosisCoordinator] 路由到 {specialty_type} - {location}")
                    print(f"  路由到专科医生: {specialty_type} - {location}")
                    
                    # 【微服务拆分后】使用HTTP客户端调用专科医生服务
                    from shared.clients.specialist_service_client import SpecialistServiceClient
                    
                    client = SpecialistServiceClient(
                        base_url=service_config["base_url"],
                        api_key=service_config["api_key"]
                    )
                    
                    task = client.diagnose(
                        user_input=user_input,
                        user_id=user_id,
                        intent=intent,
                        data_addresses=addresses,
                        user_info=user_info or {},
                        shared_context=shared_context.to_dict() if hasattr(shared_context, 'to_dict') else {},
                        metadata={
                            "location": location,
                            "specialization": specialty_type,
                            "round": 1
                        }
                    )
                    specialist_tasks.append(task)
                    # 保存任务对应的信息，用于后续记录MCP交互
                    task_info_list.append((location, addresses, specialty_type))
                else:
                    self.logger.warning(f"[TwoRoundDiagnosisCoordinator] 未找到专科医生配置: {specialty_type} - {location}")
                    print(f"  [警告] 未找到专科医生配置: {specialty_type} - {location}")
            
            # 3. 并行执行诊断
            print(f"  开始执行专科医生诊断（{len(specialist_tasks)} 个任务）...")
            if specialist_tasks:
                import time
                diagnosis_results = []
                for i, task in enumerate(specialist_tasks):
                    start_time = time.time()
                    try:
                        result = await task
                        duration = (time.time() - start_time) * 1000  # 毫秒
                        if not isinstance(result, Exception):
                            diagnosis_results.append(result)
                            # 记录专科医生诊断
                            if diagnosis_logger and isinstance(result, dict):
                                # 从结果或任务信息中获取location和specialty
                                location = result.get('location', task_info_list[i][0] if i < len(task_info_list) else 'unknown')
                                specialty = result.get('specialization', task_info_list[i][2] if i < len(task_info_list) else specialty_type)
                                addresses = task_info_list[i][1] if i < len(task_info_list) else []
                                
                                # 记录MCP交互
                                # 优先从诊断结果中获取MCP信息（如果专科服务返回了）
                                mcp_info = result.get('mcp_interaction', {})
                                if mcp_info:
                                    # 使用专科服务返回的MCP信息
                                    mcp_address = mcp_info.get('mcp_server_address', addresses[0].get('address', 'N/A') if addresses else 'N/A')
                                    mcp_token = mcp_info.get('token', addresses[0].get('access_token', '') if addresses else '')
                                    data_summary = mcp_info.get('data_summary', {"患者基本信息": "已获取", "历史病历": "已获取", "检查报告": "已获取", "数据完整性": "完整"})
                                elif addresses:
                                    # 使用数据地址信息
                                    addr = addresses[0]  # 使用第一个数据地址
                                    mcp_address = addr.get('address', 'N/A')
                                    mcp_token = addr.get('access_token', '')
                                    data_summary = {"患者基本信息": "已获取", "历史病历": "已获取", "检查报告": "已获取", "数据完整性": "完整"}
                                else:
                                    # 没有数据地址，使用默认值
                                    mcp_address = 'N/A'
                                    mcp_token = ''
                                    data_summary = {"数据状态": "无数据地址"}
                                
                                await diagnosis_logger.log_mcp_interaction(
                                    round_num=1,
                                    location=location,
                                    specialty=specialty,
                                    mcp_address=mcp_address,
                                    token=mcp_token,
                                    success=True,
                                    data_summary=data_summary
                                )
                                # 记录专科医生诊断
                                await diagnosis_logger.log_specialist_diagnosis(
                                    round_num=1,
                                    location=location,
                                    specialty=specialty,
                                    diagnosis_result=result,
                                    duration=duration
                                )
                    except Exception as e:
                        self.logger.error(f"诊断任务执行失败: {e}")
                print(f"  诊断完成，有效结果数量: {len(diagnosis_results)}")
            else:
                diagnosis_results = []
                print(f"  [警告] 没有可执行的诊断任务")
            
            # 4. 评估是否需要补充数据
            needs_more_data = self._evaluate_needs_more_data(diagnosis_results)
            
            print(f"  需要补充更多近期健康监测数据: {needs_more_data}")
            if not needs_more_data:
                print(f"  [警告] 评估结果为不需要补充数据，可能的原因:")
                if not diagnosis_results:
                    print(f"    - 诊断结果为空（可能没有找到专科医生或诊断失败）")
                else:
                    print(f"    - 诊断结果数量: {len(diagnosis_results)}")
                    for idx, result in enumerate(diagnosis_results, 1):
                        if isinstance(result, dict):
                            confidence = result.get("confidence", 1.0)
                            needs_more = result.get("needs_more_data", False)
                            print(f"    - 结果 {idx}: confidence={confidence}, needs_more_data={needs_more}")
            print(f"[第一轮诊断] 完成\n")
            
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 第一轮诊断完成，需要补充更多数据: {needs_more_data}")
            
            # 记录第一轮诊断结果
            if diagnosis_logger:
                await diagnosis_logger.log_round_result(
                    round_num=1,
                    results=diagnosis_results,
                    needs_more_data=needs_more_data
                )
            
            return {
                "diagnosis_results": diagnosis_results,
                "needs_more_data": needs_more_data,
                "round": 1,
                "intent": intent  # 保存意图，供第二轮使用
            }
            
        except Exception as e:
            self.logger.error(f"[TwoRoundDiagnosisCoordinator] 第一轮诊断失败: {str(e)}", exc_info=True)
            return {
                "diagnosis_results": [],
                "needs_more_data": False,
                "round": 1,
                "intent": intent
            }
    
    def _evaluate_needs_more_data(self, diagnosis_results: List[Any]) -> bool:
        """
        评估是否需要补充数据
        
        参数:
            diagnosis_results: 诊断结果列表
            
        返回:
            bool: 是否需要补充数据
        """
        # 简化版：如果第一轮有结果，默认需要第二轮（演示模式）
        # 实际应用中应该根据诊断结果的置信度、数据完整性等来判断
        if not diagnosis_results:
            return False
        
        # 检查诊断结果中是否有需要更多数据的标识
        for result in diagnosis_results:
            if isinstance(result, dict):
                # 检查置信度
                confidence = result.get("confidence", 1.0)
                if confidence < 0.8:
                    return True
                
                # 检查是否有数据需求
                needs_more = result.get("needs_more_data", False)
                if needs_more:
                    return True
        
        # 演示模式：默认需要第二轮
        return True
    
    async def second_round_diagnosis(
        self,
        user_input: str,
        user_id: str,
        first_round_results: Dict[str, Any],
        shared_context: SharedContext,
        token: Optional[str] = None,
        user_info: Optional[Dict[str, Any]] = None,
        diagnosis_logger=None
    ) -> Dict[str, Any]:
        """
        第二轮诊断（请求补充健康监测数据）
        
        第二轮诊断明确请求"健康监测数据"，无需复杂判断。
        此方法已优化，直接请求健康监测数据，简化了数据需求提取逻辑。
        
        参数:
            user_input: 用户输入
            user_id: 用户ID
            first_round_results: 第一轮诊断结果
            shared_context: 共享上下文
            token: JWT token，用于 EntryAgent 认证（可选，如果提供则更新配置）
            user_info: 用户信息，包含userid、username、id_token等字段
            
        返回:
            Dict[str, Any]: 第二轮诊断结果
        """
        try:
            # 如果提供了 token，更新 DataProxyClient 的配置
            if token and token != self.data_proxy_client.config.token:
                self.logger.info(f"[TwoRoundDiagnosisCoordinator] 更新 token: {token[:20]}...")
                self.data_proxy_client.config.token = token
                # 如果 EntryAgent 适配器已初始化，更新其 token
                if self.data_proxy_client.entry_agent_adapter:
                    self.data_proxy_client.entry_agent_adapter.token = token
                    self.logger.info(f"[TwoRoundDiagnosisCoordinator] 已更新 EntryAgent 适配器的 token")
            
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 开始第二轮诊断")
            
            print(f"\n[第二轮诊断] 开始诊断")
            print(f"  第一轮诊断结果数量: {len(first_round_results.get('diagnosis_results', []))}")
            
            # 检查EntryAgent配置
            if self.data_proxy_client.config.use_entry_agent:
                self.logger.info(f"[TwoRoundDiagnosisCoordinator] ✅ EntryAgent已启用，第二轮将使用EntryAgent协议（A2A SDK）")
                print(f"  ✅ EntryAgent已启用，第二轮将使用EntryAgent协议（A2A SDK）")
            else:
                self.logger.warning(f"[TwoRoundDiagnosisCoordinator] ⚠️ EntryAgent未启用，第二轮将使用HTTP协议")
                print(f"  ⚠️ EntryAgent未启用，第二轮将使用HTTP协议")
            
            # 记录第二轮请求
            if diagnosis_logger:
                await diagnosis_logger.log_second_round_request()
            
            # 1. 第二轮诊断明确请求健康监测数据（已优化简化）
            data_requirements = self._extract_data_requirements(
                first_round_results,
                user_input=user_input,
                shared_context=shared_context
            )
            print(f"  数据需求: {data_requirements} (明确请求健康监测数据)")
            
            # 2. 更新共享上下文，添加数据需求
            shared_context.specialist_requests = data_requirements
            
            # 2.1 确保 round_number 正确设置（第一轮已完成，应该为1）
            # 这样第二轮调用 interact_with_context 时，conversation_round 才会是 2
            if shared_context.round_number < 1:
                shared_context.round_number = 1
                self.logger.info(f"[TwoRoundDiagnosisCoordinator] 更新 round_number 为 1（第一轮已完成）")
                print(f"[第二轮诊断] 更新 round_number: {shared_context.round_number}")
            
            # 3. 请求补充数据（使用原始意图）
            # 注意：需要从第一轮结果中获取原始意图
            original_intent = first_round_results.get("intent", "内科咨询")
            
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 请求补充健康监测数据，意图: {original_intent}")
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 当前 round_number: {shared_context.round_number}，第二轮时 conversation_round 应为: {shared_context.round_number + 1}")
            
            # 打印第二轮数据请求信息
            print("\n" + "=" * 80)
            print("[演示模式] 第二轮诊断 - 请求补充近期健康监测数据")
            print("=" * 80)
            print(f"意图: {original_intent}")
            print(f"用户ID: {user_id}")
            print(f"当前 round_number: {shared_context.round_number}")
            print(f"预期 conversation_round: {shared_context.round_number + 1}")
            print(f"数据需求: {data_requirements}")
            print("-" * 80)
            
            async with self.data_proxy_client:
                additional_data_addresses = await self.data_proxy_client.interact_with_context(
                    intent=original_intent,  # 使用原始识别的意图
                    user_input=user_input,
                    user_id=user_id,
                    shared_context=shared_context,
                    ask_user_callback=None,  # 演示模式不需要用户交互
                    diagnosis_logger=diagnosis_logger
                )
            
            # 打印第二轮数据响应信息
            print("-" * 80)
            print(f"[演示模式] 第二轮补充数据请求完成")
            print(f"获取到补充数据地址数量: {len(additional_data_addresses)}")
            if additional_data_addresses:
                print("补充数据地址列表:")
                for i, addr in enumerate(additional_data_addresses, 1):
                    print(f"  {i}. 类型: {addr.get('data_type', 'N/A')}, 地域: {addr.get('location', 'N/A')}, 地址: {addr.get('address', 'N/A')[:50]}...")
            else:
                print("  [警告] 未获取到补充数据地址")
            print("=" * 80 + "\n")
            
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 获取到 {len(additional_data_addresses)} 个补充数据地址")
            
            # 检查是否有直接医疗数据
            has_direct_data = shared_context.direct_medical_data is not None
            medical_data = shared_context.direct_medical_data if has_direct_data else None
            
            # 记录第二轮数据接收
            if diagnosis_logger:
                await diagnosis_logger.log_data_addresses_received(
                    round_num=2,
                    data_addresses=additional_data_addresses,
                    has_direct_data=has_direct_data,
                    medical_data=medical_data
                )
            
            # 4. 根据意图路由到对应地域专科医生进行第二轮诊断
            specialty_type = self._map_intent_to_specialty(original_intent)
            location_groups = self.location_router.group_data_addresses_by_location(
                additional_data_addresses
            )
            
            # 第二轮诊断开始（已通过log_data_addresses_received记录）
            
            specialist_tasks = []
            for location, addresses in location_groups.items():
                service_config = self._get_specialist(specialty_type, location)
                if service_config:
                    self.logger.info(f"[TwoRoundDiagnosisCoordinator] 第二轮路由到 {specialty_type} - {location}")
                    
                    # 【微服务拆分后】使用HTTP客户端调用专科医生服务
                    from shared.clients.specialist_service_client import SpecialistServiceClient
                    
                    client = SpecialistServiceClient(
                        base_url=service_config["base_url"],
                        api_key=service_config["api_key"]
                    )
                    
                    task = client.diagnose(
                        user_input=user_input,
                        user_id=user_id,
                        intent=original_intent,
                        data_addresses=addresses,
                        user_info=user_info or {},
                        shared_context=shared_context.to_dict() if hasattr(shared_context, 'to_dict') else {},
                        metadata={
                            "location": location,
                            "specialization": specialty_type,
                            "round": 2
                        }
                    )
                    specialist_tasks.append(task)
            
            # 5. 执行第二轮诊断（逐个执行以便记录日志）
            print(f"  开始执行专科医生诊断（{len(specialist_tasks)} 个任务）...")
            
            if specialist_tasks:
                import time
                second_round_results = []
                # 需要跟踪每个任务对应的location和addresses
                task_info = []  # [(location, addresses, specialty), ...]
                for location, addresses in location_groups.items():
                    task_info.append((location, addresses, specialty_type))
                
                for i, task in enumerate(specialist_tasks):
                    start_time = time.time()
                    try:
                        result = await task
                        duration = (time.time() - start_time) * 1000  # 毫秒
                        if not isinstance(result, Exception) and result is not None:
                            second_round_results.append(result)
                            # 记录专科医生诊断
                            if diagnosis_logger and isinstance(result, dict):
                                location = result.get('location', task_info[i][0] if i < len(task_info) else 'unknown')
                                specialty = result.get('specialization', task_info[i][2] if i < len(task_info) else specialty_type)
                                addresses = task_info[i][1] if i < len(task_info) else []
                                # 记录MCP交互（如果有数据地址或直接数据）
                                if has_direct_data and medical_data:
                                    # 直接数据，记录MCP交互（简化版）
                                    await diagnosis_logger.log_mcp_interaction(
                                        round_num=2,
                                        location=location,
                                        specialty=specialty,
                                        mcp_address="健康监测数据（直接数据）",
                                        token="已授权",
                                        success=True,
                                        data_summary={"健康监测数据": "已获取", "数据完整性": "完整"}
                                    )
                                elif addresses:
                                    addr = addresses[0]  # 使用第一个数据地址
                                    await diagnosis_logger.log_mcp_interaction(
                                        round_num=2,
                                        location=location,
                                        specialty=specialty,
                                        mcp_address=addr.get('address', 'N/A'),
                                        token=addr.get('access_token', ''),
                                        success=True,
                                        data_summary={"健康监测数据": "已获取", "数据完整性": "完整"}
                                    )
                                # 记录专科医生诊断
                                await diagnosis_logger.log_specialist_diagnosis(
                                    round_num=2,
                                    location=location,
                                    specialty=specialty,
                                    diagnosis_result=result,
                                    duration=duration
                                )
                    except Exception as e:
                        self.logger.error(f"第二轮诊断任务执行失败: {e}")
                
                print(f"\n  诊断完成，有效结果数量: {len(second_round_results)}")
                
                # 详细打印第二轮诊断结果（完整内容）
                if second_round_results:
                    print(f"\n" + "=" * 80)
                    print(f"[第二轮诊断] 完整诊断结果详情")
                    print("=" * 80)
                    for idx, result in enumerate(second_round_results, 1):
                        if isinstance(result, dict):
                            print(f"\n  【诊断结果 {idx}】")
                            print(f"  " + "-" * 76)
                            print(f"    - 智能体ID: {result.get('agent', 'N/A')}")
                            print(f"    - 地域: {result.get('location', 'N/A')}")
                            print(f"    - 专科: {result.get('specialization', 'N/A')}")
                            print(f"    - 置信度: {result.get('confidence', 'N/A')}")
                            print(f"    - 需要更多健康监测数据: {result.get('needs_more_data', 'N/A')}")
                            
                            # 打印数据需求
                            data_requirements = result.get('data_requirements', [])
                            if data_requirements:
                                print(f"    - 数据需求 ({len(data_requirements)} 项):")
                                for i, req in enumerate(data_requirements, 1):
                                    print(f"      {i}. {req}")
                            
                            # 打印数据来源
                            data_sources = result.get('data_sources', [])
                            if data_sources:
                                print(f"    - 数据来源: {data_sources}")
                            
                            # 打印完整的诊断结果
                            diagnosis = result.get('diagnosis', {})
                            if isinstance(diagnosis, dict):
                                diagnosis_text = diagnosis.get('diagnosis', '')
                                if diagnosis_text:
                                    print(f"    - 【完整诊断内容】:")
                                    print(f"      {diagnosis_text}")
                                
                                reasoning = diagnosis.get('reasoning', '')
                                if reasoning:
                                    print(f"    - 【推理过程】:")
                                    print(f"      {reasoning}")
                                
                                # 打印其他诊断字段
                                for key in ['symptoms', 'analysis', 'recommendation', 'treatment']:
                                    if key in diagnosis and diagnosis[key]:
                                        print(f"    - {key}: {diagnosis[key]}")
                            elif isinstance(diagnosis, str):
                                print(f"    - 【完整诊断内容】:")
                                print(f"      {diagnosis}")
                            
                            # 打印推理过程（如果单独存在）
                            reasoning = result.get('reasoning', '')
                            if reasoning:
                                print(f"    - 【推理过程】:")
                                print(f"      {reasoning}")
                            
                            # 打印错误信息
                            if 'error' in result:
                                print(f"    - [错误] {result.get('error', 'N/A')}")
                            
                            print(f"  " + "-" * 76)
                        else:
                            print(f"  结果 {idx}: {type(result).__name__}")
                    print("=" * 80 + "\n")
                else:
                    print(f"  [警告] 第二轮诊断没有产生有效结果")
            else:
                second_round_results = []
                print(f"  [警告] 没有可执行的诊断任务")
            
            print(f"\n[第二轮诊断] 完成")
            print(f"  总结果数量: {len(second_round_results)}\n")
            
            # 记录第二轮诊断结果
            if diagnosis_logger:
                await diagnosis_logger.log_round_result(
                    round_num=2,
                    results=second_round_results,
                    needs_more_data=False
                )
            
            self.logger.info(f"[TwoRoundDiagnosisCoordinator] 第二轮诊断完成")
            
            return {
                "diagnosis_results": second_round_results,
                "round": 2
            }
            
        except Exception as e:
            self.logger.error(f"[TwoRoundDiagnosisCoordinator] 第二轮诊断失败: {str(e)}", exc_info=True)
            return {
                "diagnosis_results": [],
                "round": 2
            }
    
    def _extract_data_requirements(
        self, 
        first_round_results: Dict[str, Any],
        user_input: Optional[str] = None,
        shared_context: Optional[SharedContext] = None
    ) -> List[Dict[str, Any]]:
        """
        提取第二轮诊断的数据需求
        
        第二轮诊断明确要求"健康监测数据"，无需复杂判断。
        此方法已优化简化，直接返回健康监测数据需求。
        
        参数:
            first_round_results: 第一轮诊断结果（保留用于兼容性，但不再使用）
            user_input: 用户输入（保留用于兼容性，但不再使用）
            shared_context: 共享上下文（保留用于兼容性，但不再使用）
            
        返回:
            List[Dict[str, Any]]: 数据需求列表，始终包含"健康监测数据"
        """
        # 第二轮诊断直接返回健康监测数据需求
        requirements = [
            {
                "data_type": "健康监测数据",
                "description": "需要补充近期实时健康监测数据以进一步诊断",
                "priority": "high"
            }
        ]
        
        self.logger.info(f"[TwoRoundDiagnosisCoordinator] 第二轮诊断：明确请求健康监测数据")
        
        return requirements
    
    def _should_request_health_monitoring(
        self,
        user_input: Optional[str],
        shared_context: Optional[SharedContext],
        diagnosis_results: List[Any]
    ) -> bool:
        """
        判断是否需要健康监测数据
        
        @deprecated 此方法已废弃，不再使用。
        第二轮诊断现在直接请求"健康监测数据"，无需复杂判断。
        
        参数:
            user_input: 用户输入
            shared_context: 共享上下文
            diagnosis_results: 诊断结果列表
            
        返回:
            bool: 是否需要健康监测数据（始终返回True，以保持兼容性）
        """
        # 已废弃：第二轮诊断现在直接请求健康监测数据
        # 保留此方法仅用于向后兼容，但不再执行实际判断逻辑
        self.logger.warning(f"[TwoRoundDiagnosisCoordinator] _should_request_health_monitoring() 方法已废弃，不再使用")
        return True  # 始终返回True，因为第二轮诊断总是请求健康监测数据

