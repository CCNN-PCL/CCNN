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

from re import I
from typing import Any, Dict, Optional

from src.config.settings import settings
from src.logger.logger import get_logger
from src.shared.agents.specialists import (
    SurgicalAgent,
)
from src.shared.agents.utils.shared_context import SharedContext
from src.shared.config.model_config import get_config

logger = get_logger(__name__)


class DiagnosisService:
    def __init__(self):
        self.model = settings.MODEL_NAME
        self.name = settings.SERVICE_NAME
        self.location = settings.LOCATION
        self.logger = logger.bind(
            service_name=self.name, location=self.location, model_name=self.model
        )
        self._init_specialists()

    def _init_specialists(self):
        """
        初始化地域专科医生实例

        """

        try:
            self.logger.info("专科医生实例初始化")
            # 外科医生 - 北京（使用huatuogpt-2）
            surgical_config = get_config(self.model).to_dict()
            self.specialist = SurgicalAgent(
                surgical_config, location=self.location
            )
            self.logger.info("专科医生实例初始化完成")

        except Exception as e:
            self.logger.error(f"专科医生实例初始化失败: {str(e)}")
            raise

    async def handle_chat(
        self,
        user_input: str,
        user_id: str,
        data_addresses: list[Dict[str, Any]],
        shared_context: Dict[str, Any] | None = None,
        user_info: Dict[str, Any] | None = None,
    ) -> Optional[Dict[str, Any]]:
        """
        处理聊天消息

        参数:
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            data_addresses (List[Dict], optional): 数据地址列表（包含地域信息）
            shared_context (SharedContext, optional): 共享上下文
            user_info (Dict, optional): 用户信息

        返回:
            Optional[Dict[str, Any]]: 聊天响应
        """
        self.logger.info(
            "handle diagnosis chat", user_id=user_id, user_input=user_input[:50]
        )

        result = await self.specialist.execute(
            user_input=user_input,
            user_id=user_id,
            data_addresses=data_addresses,
            shared_context=SharedContext.from_dict(shared_context)
            if shared_context
            else None,
            user_info=user_info,
        )
        if not result:
            self.logger.error(
                "handle diagnosis chat no result",
                user_id=user_id,
                user_input=user_input[:50],
            )
            raise Exception("no result from model")
        I
        self.logger.info(
            f"handle diagnosis chat result={result}",
            user_id=user_id,
            user_input=user_input[:50],
        )
        return result
