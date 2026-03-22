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
第三方应用交互预留接口
====================

本模块提供与第三方数据代理应用和数据库存储服务的交互接口，
支持模拟测试和真实API调用切换，不影响现有功能运行。

功能特性：
1. 预留接口设计：为未来第三方应用集成预留接口
2. 模拟测试支持：提供完整的模拟数据用于测试
3. 配置切换：支持模拟模式和真实API模式切换
4. 错误处理：完善的错误处理和降级机制
5. 日志记录：详细的操作日志和调试信息

作者: QSIR
版本: 1.0
"""

import logging
import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from enum import Enum

# 配置日志
logger = logging.getLogger(__name__)

# ==================== 数据模型定义 ====================

class ThirdPartyMode(str, Enum):
    """第三方应用模式"""
    # 【已禁用】模拟模式已不再使用
    # SIMULATION = "simulation"  # 模拟模式
    REAL_API = "real_api"      # 真实API模式
    # 【已禁用】混合模式已不再使用
    # HYBRID = "hybrid"          # 混合模式（优先真实API，失败时使用模拟）

class DataProxyRequest(BaseModel):
    """数据代理请求模型"""
    intent_type: str = Field(..., description="意图类型")
    specialty: str = Field(..., description="专科类型")
    user_id: str = Field(..., description="用户ID")
    symptoms: List[str] = Field(default=[], description="症状列表")
    context: Dict[str, Any] = Field(default={}, description="上下文信息")
    request_id: str = Field(..., description="请求ID")
    priority: str = Field(default="medium", description="优先级")

class DataProxyResponse(BaseModel):
    """数据代理响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data_addresses: List[Dict[str, Any]] = Field(default=[], description="数据地址列表")
    request_id: str = Field(..., description="请求ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    mode: str = Field(default="simulation", description="响应模式")

class DataRetrievalRequest(BaseModel):
    """数据检索请求模型"""
    data_addresses: List[Dict[str, Any]] = Field(..., description="数据地址列表")
    user_id: str = Field(..., description="用户ID")
    request_id: str = Field(..., description="请求ID")
    timeout: int = Field(default=30, description="超时时间（秒）")

class DataRetrievalResponse(BaseModel):
    """数据检索响应模型"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    medical_data: Dict[str, Any] = Field(default={}, description="医疗数据")
    request_id: str = Field(..., description="请求ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    mode: str = Field(default="simulation", description="响应模式")

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    version: str = Field(..., description="版本号")
    mode: str = Field(..., description="当前模式")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    third_party_status: Dict[str, Any] = Field(default={}, description="第三方服务状态")

# ==================== 配置管理 ====================

class ThirdPartyConfig:
    """第三方应用配置"""
    
    def __init__(self):
        # 【已修改】默认模式改为real_api，不再使用模拟模式
        self.mode = os.getenv("THIRD_PARTY_MODE", "real_api")
        
        # ✅ EntryAgent配置（A2A协议）
        self.use_entry_agent = os.getenv("USE_ENTRY_AGENT", "false").lower() == "true"
        self.data_proxy_url = os.getenv("DATA_PROXY_APP_URL", "http://data-proxy-app:9000")
        self.data_proxy_api_key = os.getenv("DATA_PROXY_API_KEY", "")
        
        # ✅ MCP协议配置（数据存储服务）
        self.use_mcp = os.getenv("USE_MCP_PROTOCOL", "false").lower() == "true"
        self.mcp_beijing_url = os.getenv("MCP_SERVER_BEIJING_URL", "")
        self.mcp_shanghai_url = os.getenv("MCP_SERVER_SHANGHAI_URL", "")
        self.mcp_token = os.getenv("MCP_SERVER_TOKEN", "")
        self.mcp_transport_type = os.getenv("MCP_TRANSPORT_TYPE", "streamable-http")
        self.mcp_timeout = int(os.getenv("MCP_TIMEOUT", "60"))
        
        # ⚠️ HTTP协议配置（降级方案）
        self.database_storage_url = os.getenv("DATABASE_STORAGE_URL", "http://database-storage:8000")
        self.database_storage_api_key = os.getenv("DATABASE_STORAGE_API_KEY", "")
        
        self.timeout = int(os.getenv("THIRD_PARTY_TIMEOUT", "30"))
        self.retry_count = int(os.getenv("THIRD_PARTY_RETRY_COUNT", "3"))
        self.enable_logging = os.getenv("THIRD_PARTY_ENABLE_LOGGING", "true").lower() == "true"
        
        logger.info(f"[ThirdPartyConfig] 初始化配置 - 模式: {self.mode}")
        logger.info(f"[ThirdPartyConfig] EntryAgent: {self.use_entry_agent}")
        logger.info(f"[ThirdPartyConfig] MCP协议: {self.use_mcp}")
        if self.use_mcp:
            logger.info(f"[ThirdPartyConfig] MCP北京服务器: {self.mcp_beijing_url}")
            logger.info(f"[ThirdPartyConfig] MCP上海服务器: {self.mcp_shanghai_url}")
        logger.info(f"[ThirdPartyConfig] 数据代理URL: {self.data_proxy_url}")
        logger.info(f"[ThirdPartyConfig] 数据库存储URL: {self.database_storage_url}")

# ==================== 模拟数据生成器 ====================
# 【已禁用】模拟模式已不再使用，整个 SimulationDataGenerator 类已删除
# ============================================================
# 
# 注意：模拟数据生成器类已完全禁用，不再使用
# 默认模式已改为 real_api，仅支持真实API调用
#
# 如果需要恢复模拟模式，请参考备份文件或版本历史记录
#
#     """模拟数据生成器"""
#     
#     @staticmethod
#     def generate_data_addresses(intent_type: str, specialty: str, user_id: str, symptoms: List[str]) -> List[Dict[str, Any]]:
#         """生成模拟数据地址"""
#         logger.info(f"[SimulationDataGenerator] 生成模拟数据地址 - 意图: {intent_type}, 专科: {specialty}")
#         
#         data_addresses = []
#         
#         # 根据专科和症状生成相应的数据地址
#         if specialty == "内科" or "内科" in intent_type:
#             data_addresses.extend([
#                 {
#                     "data_type": "病史数据",
#                     "address": "db://hospital_beijing/medical_records",
#                     "parameters": {
#                         "user_id": user_id,
#                         "conditions": ["高血压", "心脏病", "糖尿病"],
#                         "date_range": "2020-01-01:2024-12-31"
#                     },
#                     "access_token": f"token_beijing_{user_id}_{int(datetime.now().timestamp())}",
#                     "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
#                     "priority": "high",
#                     "source": "simulation"
#                 },
#                 {
#                     "data_type": "用药记录",
#                     "address": "db://hospital_shanghai/medications",
#                     "parameters": {
#                         "user_id": user_id,
#                         "medication_types": ["降压药", "心脏药物"],
#                         "status": "current"
#                     },
#                     "access_token": f"token_shanghai_{user_id}_{int(datetime.now().timestamp())}",
#                     "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
#                     "priority": "high",
#                     "source": "simulation"
#                 }
#             ])
#         
#         if specialty == "外科" or "外科" in intent_type:
#             data_addresses.extend([
#                 {
#                     "data_type": "手术记录",
#                     "address": "db://hospital_beijing/surgical_records",
#                     "parameters": {
#                         "user_id": user_id,
#                         "surgery_types": ["阑尾炎", "胆囊切除"],
#                         "date_range": "2020-01-01:2024-12-31"
#                     },
#                     "access_token": f"token_beijing_surg_{user_id}_{int(datetime.now().timestamp())}",
#                     "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
#                     "priority": "high",
#                     "source": "simulation"
#                 }
#             ])
#         
#         # 影像数据（如果症状包含影像相关关键词）
#         if any(keyword in " ".join(symptoms) for keyword in ["影像", "X光", "CT", "MRI", "检查"]):
#             data_addresses.append({
#                 "data_type": "影像数据",
#                 "address": "db://hospital_beijing/images/cardiac",
#                 "parameters": {
#                     "user_id": user_id,
#                     "imaging_types": ["心电图", "心脏超声", "胸部X光"],
#                     "date_range": "2023-01-01:2024-12-31"
#                 },
#                 "access_token": f"token_beijing_img_{user_id}_{int(datetime.now().timestamp())}",
#                 "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
#                 "priority": "medium",
#                 "source": "simulation"
#             })
#         
#         logger.info(f"[SimulationDataGenerator] 生成了 {len(data_addresses)} 个数据地址")
#         return data_addresses
#     
#     @staticmethod
#     def generate_medical_data(data_addresses: List[Dict[str, Any]], user_id: str) -> Dict[str, Any]:
#         """生成模拟医疗数据"""
#         logger.info(f"[SimulationDataGenerator] 生成模拟医疗数据 - 用户: {user_id}")
#         
#         medical_data = {
#             "user_info": {
#                 "user_id": user_id,
#                 "name": "模拟用户",
#                 "age": 45,
#                 "gender": "男"
#             },
#             "medical_history": {
#                 "chronic_diseases": ["高血压", "II型糖尿病"],
#                 "past_illnesses": ["胃炎", "阑尾炎"],
#                 "family_history": [
#                     {"relationship": "父亲", "condition": "心脏病"},
#                     {"relationship": "母亲", "condition": "糖尿病"}
#                 ],
#                 "allergies": [
#                     {"allergen": "青霉素", "severity": "严重"},
#                     {"allergen": "海鲜", "severity": "轻度"}
#                 ]
#             },
#             "medications": [
#                 {
#                     "medication_name": "盐酸氨氯地平",
#                     "dosage": "5mg",
#                     "frequency": "每日一次",
#                     "start_date": "2023-01-15",
#                     "status": "current",
#                     "hospital": "北京医院"
#                 },
#                 {
#                     "medication_name": "二甲双胍",
#                     "dosage": "500mg",
#                     "frequency": "每日两次",
#                     "start_date": "2023-03-20",
#                     "status": "current",
#                     "hospital": "上海医院"
#                 }
#             ],
#             "imaging_data": [
#                 {
#                     "imaging_type": "心电图",
#                     "examination_date": "2024-10-20",
#                     "findings": "窦性心律不齐，心率95次/分",
#                     "conclusion": "建议进一步检查",
#                     "hospital": "北京医院",
#                     "image_url": "https://storage.example.com/ecg_20241020.jpg"
#                 },
#                 {
#                     "imaging_type": "心脏超声",
#                     "examination_date": "2024-05-15",
#                     "findings": "左心室轻度肥厚",
#                     "conclusion": "符合高血压性心脏病",
#                     "hospital": "北京医院",
#                     "image_url": "https://storage.example.com/echo_20240515.jpg"
#                 }
#             ],
#             "lab_results": [
#                 {
#                     "test_name": "血糖",
#                     "value": "6.4",
#                     "unit": "mmol/L",
#                     "reference_range": "3.9-6.1",
#                     "test_date": "2024-10-15",
#                     "status": "异常",
#                     "hospital": "北京医院"
#                 },
#                 {
#                     "test_name": "血压",
#                     "value": "145/90",
#                     "unit": "mmHg",
#                     "reference_range": "<140/90",
#                     "test_date": "2024-10-15",
#                     "status": "异常",
#                     "hospital": "北京医院"
#                 }
#             ],
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "source": "simulation",
#                 "data_count": {
#                     "medical_history": 4,
#                     "medications": 2,
#                     "imaging_data": 2,
#                     "lab_results": 2
#                 }
#             }
#         }
#         
#         logger.info(f"[SimulationDataGenerator] 生成了完整的模拟医疗数据")
#         return medical_data

# ==================== 第三方应用客户端 ====================

class ThirdPartyClient:
    """第三方应用客户端"""
    
    def __init__(self, config: ThirdPartyConfig):
        self.config = config
        self.session = None
        # 【已禁用】模拟数据生成器已不再使用
        # self.simulation_generator = SimulationDataGenerator()
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def request_data_proxy(self, request: DataProxyRequest) -> DataProxyResponse:
        """请求数据代理应用"""
        logger.info(f"[ThirdPartyClient] 请求数据代理 - 模式: {self.config.mode}")
        
        # 【已禁用】模拟模式和混合模式已不再使用
        # if self.config.mode == ThirdPartyMode.SIMULATION:
        #     return await self._simulate_data_proxy_request(request)
        # elif self.config.mode == ThirdPartyMode.HYBRID:
        #     try:
        #         return await self._real_data_proxy_request(request)
        #     except Exception as e:
        #         logger.warning(f"[ThirdPartyClient] 真实API调用失败，切换到模拟模式: {str(e)}")
        #         return await self._simulate_data_proxy_request(request)
        
        if self.config.mode == ThirdPartyMode.REAL_API:
            return await self._real_data_proxy_request(request)
        else:
            raise ValueError(f"不支持的第三方应用模式: {self.config.mode}（仅支持real_api模式）")
    
    async def retrieve_medical_data(self, request: DataRetrievalRequest) -> DataRetrievalResponse:
        """检索医疗数据"""
        logger.info(f"[ThirdPartyClient] 检索医疗数据 - 模式: {self.config.mode}")
        
        # 【已禁用】模拟模式和混合模式已不再使用
        # if self.config.mode == ThirdPartyMode.SIMULATION:
        #     return await self._simulate_data_retrieval(request)
        # elif self.config.mode == ThirdPartyMode.HYBRID:
        #     try:
        #         return await self._real_data_retrieval(request)
        #     except Exception as e:
        #         logger.warning(f"[ThirdPartyClient] 真实API调用失败，切换到模拟模式: {str(e)}")
        #         return await self._simulate_data_retrieval(request)
        
        if self.config.mode == ThirdPartyMode.REAL_API:
            return await self._real_data_retrieval(request)
        else:
            raise ValueError(f"不支持的第三方应用模式: {self.config.mode}（仅支持real_api模式）")
    
    # 【已禁用】模拟数据代理请求方法已不再使用
    # async def _simulate_data_proxy_request(self, request: DataProxyRequest) -> DataProxyResponse:
    #     """模拟数据代理请求"""
    #     logger.info(f"[ThirdPartyClient] 执行模拟数据代理请求")
    #     
    #     # 模拟网络延迟
    #     await asyncio.sleep(0.1)
    #     
    #     # 生成模拟数据地址
    #     data_addresses = self.simulation_generator.generate_data_addresses(
    #         request.intent_type,
    #         request.specialty,
    #         request.user_id,
    #         request.symptoms
    #     )
    #     
    #     return DataProxyResponse(
    #         success=True,
    #         message="模拟数据代理请求成功",
    #         data_addresses=data_addresses,
    #         request_id=request.request_id,
    #         mode="simulation"
    #     )
    
    async def _real_data_proxy_request(self, request: DataProxyRequest) -> DataProxyResponse:
        """
        真实数据代理请求（使用EntryAgent）
        
        ════════════════════════════════════════════════════════════
        【✅ 已更新】使用EntryAgent替代HTTP API
        ════════════════════════════════════════════════════════════
        
        此方法现在使用EntryAgent（A2A协议）调用真实的数据代理应用，
        而不是HTTP API。
        
        配置要求:
        - USE_ENTRY_AGENT=true
        - DATA_PROXY_APP_URL: 数据代理应用URL
        
        详细说明请参考：EntryAgent和MCP配置文档.md
        ════════════════════════════════════════════════════════════
        """
        logger.info(f"[ThirdPartyClient] 执行真实数据代理请求（EntryAgent）")
        
        # ✅ 优先使用EntryAgent
        if self.config.use_entry_agent:
            try:
                from shared.agents.coordinator.data_proxy_client import DataProxyClient, DataProxyConfig
                from shared.agents.utils.shared_context import SharedContext
                
                # 创建EntryAgent配置
                config = DataProxyConfig()
                
                # 创建共享上下文
                shared_context = SharedContext(
                    user_id=request.user_id,
                    intent=request.intent_type,
                    user_input=" ".join(request.symptoms),
                    user_info={}
                )
                
                # 使用EntryAgent调用数据代理应用
                async with DataProxyClient(config) as client:
                    response_data = await client.interact_with_context(
                        intent=request.intent_type,
                        user_input=" ".join(request.symptoms),
                        user_id=request.user_id,
                        shared_context=shared_context
                    )
                
                logger.info(f"[ThirdPartyClient] EntryAgent数据代理请求成功")
                return DataProxyResponse(
                    success=response_data.get("success", False),
                    message=response_data.get("message", ""),
                    data_addresses=response_data.get("data_addresses", []),
                    request_id=request.request_id,
                    mode="real_api_entryagent"
                )
                
            except Exception as e:
                logger.error(f"[ThirdPartyClient] EntryAgent数据代理请求失败: {str(e)}")
                # 如果EntryAgent失败，可以降级到HTTP（如果配置了）
                if self.config.data_proxy_url and not self.config.data_proxy_url.startswith("http://data-proxy-app"):
                    logger.warning(f"[ThirdPartyClient] EntryAgent失败，尝试HTTP降级")
                    return await self._real_data_proxy_request_http(request)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"EntryAgent数据代理请求失败: {str(e)}"
                    )
        else:
            # ⚠️ 降级到HTTP协议（如果EntryAgent未启用）
            return await self._real_data_proxy_request_http(request)
    
    async def _real_data_proxy_request_http(self, request: DataProxyRequest) -> DataProxyResponse:
        """HTTP协议数据代理请求（降级方案）"""
        logger.info(f"[ThirdPartyClient] 执行HTTP协议数据代理请求（降级）")
        
        if not self.session:
            raise RuntimeError("HTTP会话未初始化")
        
        headers = {
            "Authorization": f"Bearer {self.config.data_proxy_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "intent_type": request.intent_type,
            "specialty": request.specialty,
            "user_id": request.user_id,
            "symptoms": request.symptoms,
            "context": request.context,
            "request_id": request.request_id,
            "priority": request.priority
        }
        
        url = f"{self.config.data_proxy_url}/api/v1/data-proxy/request"
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return DataProxyResponse(
                    success=result.get("success", False),
                    message=result.get("message", ""),
                    data_addresses=result.get("data_addresses", []),
                    request_id=request.request_id,
                    mode="real_api_http"
                )
            else:
                error_text = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"数据代理请求失败: {error_text}"
                )
    
    # 【已禁用】模拟数据检索方法已不再使用
    # async def _simulate_data_retrieval(self, request: DataRetrievalRequest) -> DataRetrievalResponse:
    #     """模拟数据检索"""
    #     logger.info(f"[ThirdPartyClient] 执行模拟数据检索")
    #     
    #     # 模拟网络延迟
    #     await asyncio.sleep(0.2)
    #     
    #     # 生成模拟医疗数据
    #     medical_data = self.simulation_generator.generate_medical_data(
    #         request.data_addresses,
    #         request.user_id
    #     )
    #     
    #     return DataRetrievalResponse(
    #         success=True,
    #         message="模拟数据检索成功",
    #         medical_data=medical_data,
    #         request_id=request.request_id,
    #         mode="simulation"
    #     )
    
    async def _real_data_retrieval(self, request: DataRetrievalRequest) -> DataRetrievalResponse:
        """
        真实数据检索（使用MCP协议）
        
        ════════════════════════════════════════════════════════════
        【✅ 已更新】使用MCP协议替代HTTP API
        ════════════════════════════════════════════════════════════
        
        此方法现在使用MCP协议调用真实的第三方数据存储服务，
        而不是HTTP API。
        
        配置要求:
        - USE_MCP_PROTOCOL=true
        - MCP_SERVER_BEIJING_URL: 北京地域MCP服务器URL
        - MCP_SERVER_TOKEN: MCP服务器认证令牌
        
        详细说明请参考：MCP标准对接兼容性检查报告.md
        ════════════════════════════════════════════════════════════
        """
        logger.info(f"[ThirdPartyClient] 执行真实数据检索（MCP协议）")
        
        # ✅ 优先使用MCP协议
        if self.config.use_mcp:
            try:
                from shared.agents.utils.database_storage_client import DatabaseStorageClient, DatabaseStorageConfig
                
                # 创建MCP配置
                storage_config = DatabaseStorageConfig(
                    beijing_url=self.config.mcp_beijing_url or os.getenv("DATABASE_STORAGE_BEIJING_URL", ""),
                    shanghai_url=self.config.mcp_shanghai_url or os.getenv("DATABASE_STORAGE_SHANGHAI_URL", ""),
                    timeout=self.config.timeout,
                    retry_count=self.config.retry_count,
                    use_mcp=True  # ✅ 启用MCP协议
                )
                
                # 使用MCP协议调用数据存储服务
                async with DatabaseStorageClient(storage_config) as client:
                    medical_data = await client.retrieve_medical_data(
                        request.data_addresses,
                        request.user_id
                    )
                
                logger.info(f"[ThirdPartyClient] MCP协议数据检索成功")
                return DataRetrievalResponse(
                    success=True,
                    message="MCP协议数据检索成功",
                    medical_data=medical_data,
                    request_id=request.request_id,
                    mode="real_api_mcp"
                )
                
            except Exception as e:
                logger.error(f"[ThirdPartyClient] MCP协议数据检索失败: {str(e)}")
                # 如果MCP失败，可以降级到HTTP（如果配置了）
                if self.config.database_storage_url and not self.config.database_storage_url.startswith("http://database-storage"):
                    logger.warning(f"[ThirdPartyClient] MCP失败，尝试HTTP降级")
                    return await self._real_data_retrieval_http(request)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"MCP协议数据检索失败: {str(e)}"
                    )
        else:
            # ⚠️ 降级到HTTP协议（如果MCP未启用）
            return await self._real_data_retrieval_http(request)
    
    async def _real_data_retrieval_http(self, request: DataRetrievalRequest) -> DataRetrievalResponse:
        """HTTP协议数据检索（降级方案）"""
        logger.info(f"[ThirdPartyClient] 执行HTTP协议数据检索（降级）")
        
        if not self.session:
            raise RuntimeError("HTTP会话未初始化")
        
        headers = {
            "Authorization": f"Bearer {self.config.database_storage_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "data_addresses": request.data_addresses,
            "user_id": request.user_id,
            "request_id": request.request_id,
            "timeout": request.timeout
        }
        
        url = f"{self.config.database_storage_url}/api/v1/storage/retrieve"
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return DataRetrievalResponse(
                    success=result.get("success", False),
                    message=result.get("message", ""),
                    medical_data=result.get("data", {}),
                    request_id=request.request_id,
                    mode="real_api_http"
                )
            else:
                error_text = await response.text()
                raise HTTPException(
                    status_code=response.status,
                    detail=f"数据检索失败: {error_text}"
                )
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        logger.info(f"[ThirdPartyClient] 执行健康检查")
        
        health_status = {
            "third_party_mode": self.config.mode,
            "data_proxy_status": "unknown",
            "database_storage_status": "unknown",
            "last_check": datetime.now().isoformat()
        }
        
        # 【已禁用】模拟模式已不再使用
        # if self.config.mode == ThirdPartyMode.SIMULATION:
        #     health_status.update({
        #         "data_proxy_status": "simulation_mode",
        #         "database_storage_status": "simulation_mode"
        #     })
        # else:
        # 检查真实API状态
        try:
            if self.session:
                # 检查数据代理应用
                try:
                    async with self.session.get(f"{self.config.data_proxy_url}/api/v1/data-proxy/health") as response:
                        if response.status == 200:
                            health_status["data_proxy_status"] = "healthy"
                        else:
                            health_status["data_proxy_status"] = "unhealthy"
                except Exception as e:
                    health_status["data_proxy_status"] = f"error: {str(e)}"
                
                # 检查数据库存储服务
                try:
                    async with self.session.get(f"{self.config.database_storage_url}/api/v1/storage/health") as response:
                        if response.status == 200:
                            health_status["database_storage_status"] = "healthy"
                        else:
                            health_status["database_storage_status"] = "unhealthy"
                except Exception as e:
                    health_status["database_storage_status"] = f"error: {str(e)}"
        except Exception as e:
            logger.error(f"[ThirdPartyClient] 健康检查失败: {str(e)}")
            health_status["error"] = str(e)
        
        return health_status

# ==================== FastAPI 路由 ====================

router = APIRouter(prefix="/api/v1/third-party", tags=["第三方应用交互"])

# 全局配置和客户端
config = ThirdPartyConfig()
client = ThirdPartyClient(config)

@router.post("/request-data-proxy", response_model=DataProxyResponse)
async def request_data_proxy(
    request: DataProxyRequest,
    background_tasks: BackgroundTasks
):
    """
    向数据代理应用请求数据地址
    
    参数:
        request: 数据代理请求
        background_tasks: 后台任务管理器
    
    返回:
        DataProxyResponse: 数据地址信息
    """
    try:
        logger.info(f"[API] 收到数据代理请求: {request.request_id}")
        
        # 记录请求日志
        if config.enable_logging:
            background_tasks.add_task(
                _log_request,
                "data_proxy_request",
                request.dict(),
                datetime.now().isoformat()
            )
        
        # 使用第三方客户端处理请求
        async with client as third_party_client:
            response = await third_party_client.request_data_proxy(request)
        
        logger.info(f"[API] 数据代理请求处理完成: {request.request_id}")
        return response
        
    except Exception as e:
        logger.error(f"[API] 数据代理请求失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"数据代理请求失败: {str(e)}"
        )

@router.post("/retrieve-medical-data", response_model=DataRetrievalResponse)
async def retrieve_medical_data(
    request: DataRetrievalRequest,
    background_tasks: BackgroundTasks
):
    """
    从数据库存储服务检索医疗数据
    
    参数:
        request: 数据检索请求
        background_tasks: 后台任务管理器
    
    返回:
        DataRetrievalResponse: 医疗数据
    """
    try:
        logger.info(f"[API] 收到数据检索请求: {request.request_id}")
        
        # 记录请求日志
        if config.enable_logging:
            background_tasks.add_task(
                _log_request,
                "data_retrieval_request",
                request.dict(),
                datetime.now().isoformat()
            )
        
        # 使用第三方客户端处理请求
        async with client as third_party_client:
            response = await third_party_client.retrieve_medical_data(request)
        
        logger.info(f"[API] 数据检索请求处理完成: {request.request_id}")
        return response
        
    except Exception as e:
        logger.error(f"[API] 数据检索失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"数据检索失败: {str(e)}"
        )

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    第三方应用健康检查
    
    返回:
        HealthCheckResponse: 健康状态信息
    """
    try:
        logger.info("[API] 执行第三方应用健康检查")
        
        # 使用第三方客户端进行健康检查
        async with client as third_party_client:
            third_party_status = await third_party_client.health_check()
        
        return HealthCheckResponse(
            status="healthy",
            service="第三方应用交互服务",
            version="1.0.0",
            mode=config.mode,
            third_party_status=third_party_status
        )
        
    except Exception as e:
        logger.error(f"[API] 健康检查失败: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            service="第三方应用交互服务",
            version="1.0.0",
            mode=config.mode,
            third_party_status={"error": str(e)}
        )

@router.get("/config")
async def get_config():
    """
    获取第三方应用配置信息
    
    返回:
        Dict[str, Any]: 配置信息
    """
    try:
        return {
            "mode": config.mode,
            "data_proxy_url": config.data_proxy_url,
            "database_storage_url": config.database_storage_url,
            "timeout": config.timeout,
            "retry_count": config.retry_count,
            "enable_logging": config.enable_logging,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"[API] 获取配置失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取配置失败: {str(e)}"
        )

# 【已禁用】模拟功能测试端点已不再使用
# @router.post("/test-simulation")
# async def test_simulation():
#     """
#     测试模拟功能
#     
#     返回:
#         Dict[str, Any]: 测试结果
#     """
#     try:
#         logger.info("[API] 开始测试模拟功能")
#         
#         # 测试数据代理请求
#         test_request = DataProxyRequest(
#             intent_type="内科咨询",
#             specialty="内科",
#             user_id="test_user",
#             symptoms=["心慌", "心跳加快"],
#             context={"test": True},
#             request_id=f"test_{int(datetime.now().timestamp())}"
#         )
#         
#         async with client as third_party_client:
#             # 测试数据代理
#             proxy_response = await third_party_client.request_data_proxy(test_request)
#             
#             # 测试数据检索
#             retrieval_request = DataRetrievalRequest(
#                 data_addresses=proxy_response.data_addresses,
#                 user_id="test_user",
#                 request_id=f"test_retrieval_{int(datetime.now().timestamp())}"
#             )
#             
#             retrieval_response = await third_party_client.retrieve_medical_data(retrieval_request)
#         
#         return {
#             "success": True,
#             "message": "模拟功能测试成功",
#             "test_results": {
#                 "data_proxy_test": {
#                     "success": proxy_response.success,
#                     "data_addresses_count": len(proxy_response.data_addresses),
#                     "mode": proxy_response.mode
#                 },
#                 "data_retrieval_test": {
#                     "success": retrieval_response.success,
#                     "medical_data_keys": list(retrieval_response.medical_data.keys()),
#                     "mode": retrieval_response.mode
#                 }
#             },
#             "timestamp": datetime.now().isoformat()
#         }
#         
#     except Exception as e:
#         logger.error(f"[API] 模拟功能测试失败: {str(e)}")
        return {
            "success": False,
            "message": f"模拟功能测试失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# ==================== 辅助函数 ====================

async def _log_request(request_type: str, request_data: Dict[str, Any], timestamp: str):
    """记录请求日志"""
    try:
        log_entry = {
            "type": request_type,
            "data": request_data,
            "timestamp": timestamp
        }
        
        # 这里可以将日志写入文件或数据库
        logger.info(f"[LOG] {request_type}: {json.dumps(log_entry, ensure_ascii=False)}")
        
    except Exception as e:
        logger.error(f"[LOG] 记录请求日志失败: {str(e)}")

# ==================== 初始化 ====================

def init_third_party_reserve():
    """初始化第三方应用预留接口"""
    logger.info("=" * 80)
    logger.info("[ThirdPartyReserve] 初始化第三方应用预留接口")
    logger.info(f"[ThirdPartyReserve] 当前模式: {config.mode}")
    logger.info(f"[ThirdPartyReserve] 数据代理URL: {config.data_proxy_url}")
    logger.info(f"[ThirdPartyReserve] 数据库存储URL: {config.database_storage_url}")
    logger.info("=" * 80)

# 自动初始化
init_third_party_reserve()
