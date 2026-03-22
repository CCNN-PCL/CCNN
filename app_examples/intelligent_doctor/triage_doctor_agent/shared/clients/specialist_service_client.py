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
专科医生服务客户端
用于调用专科医生微服务的HTTP客户端
"""

import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class SpecialistServiceClient:
    """专科医生服务客户端"""
    
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        """
        初始化客户端
        
        参数:
            base_url (str): 服务基础URL
            api_key (str): API密钥
            timeout (float): 超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        return f"req_{uuid.uuid4().hex[:8]}"
    
    async def diagnose(
        self,
        user_input: str,
        user_id: str,
        intent: str,
        data_addresses: List[Dict] = None,
        user_info: Dict = None,
        shared_context: Dict = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """
        调用诊断接口
        
        参数:
            user_input (str): 用户输入
            user_id (str): 用户ID
            intent (str): 意图类型
            data_addresses (List[Dict]): 数据地址列表
            user_info (Dict): 用户信息
            shared_context (Dict): 共享上下文
            metadata (Dict): 元数据
            
        返回:
            Dict[str, Any]: 诊断结果
        """
        # 先尝试不带斜杠的URL（与路由定义一致）
        url = f"{self.base_url}/api/v1/diagnosis"
        request_id = self._generate_request_id()
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": self.api_key,
            "X-Request-ID": request_id,
            "X-User-ID": user_id,
            "X-Service-Name": "cybertwin-agent",
            "X-Timestamp": str(int(datetime.now().timestamp())),
            "X-API-Version": "v1"
        }
        
        payload = {
            "user_input": user_input,
            "user_id": user_id,
            "intent": intent,
            "data_addresses": data_addresses or [],
            "shared_context": shared_context,
            "user_info": user_info or {},
            "metadata": metadata or {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "source": "cybertwin_agent"
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # 先尝试不带斜杠的URL
                response = await client.post(url, json=payload, headers=headers)
                # 如果返回307重定向，httpx会自动跟随，但POST重定向可能有问题
                # 如果返回307或404，尝试带斜杠的URL
                if response.status_code in (307, 404):
                    url_with_slash = f"{url}/"
                    response = await client.post(url_with_slash, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.content else {}
                logger.error(f"诊断请求失败: {error_data.get('error_message', str(e))}")
                raise Exception(f"Diagnosis failed: {error_data.get('error_message', str(e))}")
            except httpx.TimeoutException:
                logger.error(f"诊断请求超时: {url}")
                raise Exception("Diagnosis request timeout")
            except Exception as e:
                logger.error(f"诊断请求异常: {str(e)}")
                raise
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        返回:
            Dict[str, Any]: 健康状态
        """
        url = f"{self.base_url}/health"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"健康检查失败: {str(e)}")
                raise
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        返回:
            Dict[str, Any]: 服务状态
        """
        # 先尝试不带斜杠的URL（与路由定义一致）
        url = f"{self.base_url}/api/v1/status"
        headers = {
            "X-API-Key": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=2.0, follow_redirects=True) as client:
            try:
                # 先尝试不带斜杠的URL
                response = await client.get(url, headers=headers)
                # 如果返回307重定向，httpx会自动跟随
                # 如果返回307或404，尝试带斜杠的URL
                if response.status_code in (307, 404):
                    url_with_slash = f"{url}/"
                    response = await client.get(url_with_slash, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"获取服务状态失败: {str(e)}")
                raise


async def call_all_specialists(
    user_input: str,
    user_id: str,
    intent: str,
    data_addresses: List[Dict] = None,
    user_info: Dict = None,
    shared_context: Dict = None,
    metadata: Dict = None,
    service_configs: List[Dict] = None
) -> List[Dict[str, Any]]:
    """
    并行调用所有专科医生服务
    
    参数:
        user_input (str): 用户输入
        user_id (str): 用户ID
        intent (str): 意图类型
        data_addresses (List[Dict]): 数据地址列表
        user_info (Dict): 用户信息
        shared_context (Dict): 共享上下文
        metadata (Dict): 元数据
        service_configs (List[Dict]): 服务配置列表，格式: [{"base_url": "...", "api_key": "..."}, ...]
        
    返回:
        List[Dict[str, Any]]: 所有服务的诊断结果列表
    """
    if service_configs is None:
        # 默认服务配置
        service_configs = [
            {"base_url": "http://localhost:8002", "api_key": "test_api_key"},  # 内科-北京
            {"base_url": "http://localhost:8003", "api_key": "test_api_key"},  # 内科-上海
            {"base_url": "http://localhost:8004", "api_key": "test_api_key"},  # 外科-北京
            {"base_url": "http://localhost:8005", "api_key": "test_api_key"},  # 外科-上海
        ]
    
    clients = [
        SpecialistServiceClient(config["base_url"], config["api_key"])
        for config in service_configs
    ]
    
    tasks = [
        client.diagnose(
            user_input=user_input,
            user_id=user_id,
            intent=intent,
            data_addresses=data_addresses,
            user_info=user_info,
            shared_context=shared_context,
            metadata=metadata
        )
        for client in clients
    ]
    
    # 并行调用，即使部分失败也返回成功的结果
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤掉异常结果
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"服务 {service_configs[i]['base_url']} 调用失败: {str(result)}")
        else:
            valid_results.append(result)
    
    return valid_results
