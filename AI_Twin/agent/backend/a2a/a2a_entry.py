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

import logging
import httpx
from typing import Dict, Any, AsyncIterator
from uuid import uuid4
from a2a.types import AgentCard, Message, TextPart
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import SendMessageRequest, MessageSendParams, SendStreamingMessageRequest, Message
from urllib.parse import urlparse, parse_qs, urlunparse


# 入口（主控&规划）智能体，将任务发给其他智能体搞定
class EntryAgent:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)  # 获得logger实例

    def _extract_token_from_url(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            token_list = query_params.get('token', [])
            print("token_list:",token_list)
            
            if token_list:
                token = token_list[0]  # 取第一个值
                self.logger.info(f"从URL中提取到token: {token}")
                return token
            else:
                self.logger.warning("URL中未找到token参数，使用默认值'unknown'")
                return "unknown"
                
        except Exception as e:
            self.logger.error(f"解析URL参数失败: {e}，使用默认值'unknown'")
            return "unknown"

    def _remove_from_url(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # 移除token参数
            if 'token' in query_params:
                del query_params['token']

            # 重建查询字符串
            new_query = '&'.join([f"{k}={v[0]}" for k, v in query_params.items()])
            
            # 重建URL
            clean_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            self.logger.info(f"清理后的URL: {clean_url}")
            return clean_url
            
        except Exception as e:
            self.logger.error(f"清理URL参数失败: {e}，返回原始URL")
            return url


    async def invoke(self, base_url: str, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """
        调用该智能体，通过A2A协议与server智能体进行交互

        Args:
            base_url (str): server智能体的url
            prompt (str): 智能体的输入提示

        Returns:
            AsyncIterator[Dict[str, Any]]: server智能体的响应流
        """

        # 从base_url中提取user_id
        token = self._extract_token_from_url(base_url)
        
        # 清理URL，移除user_id参数
        clean_base_url = self._remove_from_url(base_url)

        async with httpx.AsyncClient() as httpx_client:
            # 获取agent card
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=clean_base_url)

            final_agent_card_to_use: AgentCard | None = None

            try:
                self.logger.info(
                    f"尝试获取agent card，url为{base_url}{resolver.agent_card_path}"
                )
                final_agent_card_to_use = await resolver.get_agent_card()

                self.logger.info(f"已成功获取agent card：")
                self.logger.info(
                    f"{final_agent_card_to_use.model_dump_json(indent=2, exclude_none=True)}"
                )

                self.logger.info(f"使用该agent card初始化client")

            except Exception as e:
                self.logger.error(f"获取agent card失败，错误信息为：{e}")
                raise RuntimeError(f"获取agent card失败，无法继续运行") from e

            # 初始化client
            try:
                self.logger.info(f"尝试初始化client")
                client = A2AClient(
                    httpx_client=httpx_client, agent_card=final_agent_card_to_use
                )
                self.logger.info(f"已成功初始化client")
            except Exception as e:
                self.logger.error(f"初始化client失败，错误信息为：{e}")
                raise RuntimeError(f"初始化client失败，无法继续运行") from e

            # A2A协议规定的标准Message数据格式
            send_message_payload: Message = Message(
                role="user",
                parts=[TextPart(text=prompt)],
                message_id=uuid4().hex,
                metadata={"token": token}
            )

            # 请求：使用A2A SDK封装好的SendMessageRequest
            request = SendMessageRequest(
                id=str(uuid4()), params=MessageSendParams(message=send_message_payload)
            )

            response = await client.send_message(request)

            # 返回响应对象或转换后的字典
            if hasattr(response, 'model_dump'):
                return response.model_dump()
            else:
                return response


import logging
import httpx
from typing import Dict, Any, AsyncIterator
from uuid import uuid4
from a2a.types import AgentCard, Message, TextPart
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import SendMessageRequest, MessageSendParams, SendStreamingMessageRequest, Message
from urllib.parse import urlparse, parse_qs, urlunparse


# 入口（主控&规划）智能体，将任务发给其他智能体搞定
class EntryAgent:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)  # 获得logger实例

    def _extract_user_id_from_url(self, url: str) -> str:
        """
        从URL中提取user_id参数
        
        Args:
            url (str): 包含user_id参数的URL
            
        Returns:
            str: 提取到的user_id，如果不存在则返回默认值"unknown"
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            user_id_list = query_params.get('user_id', [])
            
            if user_id_list:
                user_id = user_id_list[0]  # 取第一个值
                self.logger.info(f"从URL中提取到user_id: {user_id}")
                return user_id
            else:
                self.logger.warning("URL中未找到user_id参数，使用默认值'unknown'")
                return "unknown"
                
        except Exception as e:
            self.logger.error(f"解析URL参数失败: {e}，使用默认值'unknown'")
            return "unknown"

    def _extract_token_from_url(self, url: str) -> str:
        """
        从URL中提取user_id参数
        
        Args:
            url (str): 包含user_id参数的URL
            
        Returns:
            str: 提取到的user_id，如果不存在则返回默认值"unknown"
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            token_list = query_params.get('token', [])
            print("token_list:",token_list)
            
            if token_list:
                token = token_list[0]  # 取第一个值
                self.logger.info(f"从URL中提取到token: {token}")
                return token
            else:
                self.logger.warning("URL中未找到token参数，使用默认值'unknown'")
                return "unknown"
                
        except Exception as e:
            self.logger.error(f"解析URL参数失败: {e}，使用默认值'unknown'")
            return "unknown"

    def _remove_user_id_from_url(self, url: str) -> str:
        """
        从URL中移除user_id参数，返回干净的base_url
        
        Args:
            url (str): 原始URL
            
        Returns:
            str: 移除user_id参数后的URL
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # 移除user_id参数
            if 'user_id' in query_params:
                del query_params['user_id']

            # 移除token参数
            if 'token' in query_params:
                del query_params['token']

            # 重建查询字符串
            new_query = '&'.join([f"{k}={v[0]}" for k, v in query_params.items()])
            
            # 重建URL
            clean_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            self.logger.info(f"清理后的URL: {clean_url}")
            return clean_url
            
        except Exception as e:
            self.logger.error(f"清理URL参数失败: {e}，返回原始URL")
            return url


    async def invoke(self, base_url: str, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """
        调用该智能体，通过A2A协议与server智能体进行交互

        Args:
            base_url (str): server智能体的url
            prompt (str): 智能体的输入提示

        Returns:
            AsyncIterator[Dict[str, Any]]: server智能体的响应流
        """

        # 从base_url中提取user_id
        user_id = self._extract_user_id_from_url(base_url)

        # 从base_url中提取user_id
        token = self._extract_token_from_url(base_url)
        
        # 清理URL，移除user_id参数
        clean_base_url = self._remove_user_id_from_url(base_url)

        async with httpx.AsyncClient() as httpx_client:
            # 获取agent card
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=clean_base_url)

            final_agent_card_to_use: AgentCard | None = None

            try:
                self.logger.info(
                    f"尝试获取agent card，url为{base_url}{resolver.agent_card_path}"
                )
                final_agent_card_to_use = await resolver.get_agent_card()

                self.logger.info(f"已成功获取agent card：")
                self.logger.info(
                    f"{final_agent_card_to_use.model_dump_json(indent=2, exclude_none=True)}"
                )

                self.logger.info(f"使用该agent card初始化client")

            except Exception as e:
                self.logger.error(f"获取agent card失败，错误信息为：{e}")
                raise RuntimeError(f"获取agent card失败，无法继续运行") from e

            # 初始化client
            try:
                self.logger.info(f"尝试初始化client")
                client = A2AClient(
                    httpx_client=httpx_client, agent_card=final_agent_card_to_use
                )
                self.logger.info(f"已成功初始化client")
            except Exception as e:
                self.logger.error(f"初始化client失败，错误信息为：{e}")
                raise RuntimeError(f"初始化client失败，无法继续运行") from e

            # A2A协议规定的标准Message数据格式
            send_message_payload: Message = Message(
                role="user",
                parts=[TextPart(text=prompt)],
                message_id=uuid4().hex,
                metadata={"user_id": user_id,"token": token}
            )

            # 请求：使用A2A SDK封装好的SendMessageRequest
            request = SendMessageRequest(
                id=str(uuid4()), params=MessageSendParams(message=send_message_payload)
            )

            response = await client.send_message(request)

            # 返回响应对象或转换后的字典
            if hasattr(response, 'model_dump'):
                return response.model_dump()
            else:
                return response

