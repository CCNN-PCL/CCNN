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

import time
from datetime import datetime

from fastapi import APIRouter

from src.api.models.diagnosis import (
    DiagnosisRequest,
    DiagnosisResponse,
    SharedContext,
    Status,
    UserInfo,
    from_dict,
)
from src.logger.logger import get_logger
from src.services.diagnosis_service import DiagnosisService
from src.shared.error.error_code import ErrorDetail
from src.shared.error.exceptions import (
    BadRequestException,
    DiagnosisError,
    DiagnosisModelError,
)

logger = get_logger(__name__)

router = APIRouter()


@router.post("", response_model=DiagnosisResponse)
async def diagnosis(request: DiagnosisRequest):
    """
    专科智能体服务（内科和外科服务）提供给Cybertwin-Agent分诊服务的接口，用于接收诊断请求并返回诊断结果。

    参数:
        request: 诊断请求数据

    返回:
        DiagnosisResponse: 返回诊断结果
    """
    if not request.user_id:
        logger.error("invalid user_id")
        raise BadRequestException(
            details=[ErrorDetail(field="user_id", message="it is empty")]
        )
    if not request.user_input:
        logger.error("invalid user input")
        raise BadRequestException(
            details=[ErrorDetail(field="user_input", message="it is empty")]
        )
    if not request.intent:
        logger.error("invalid intent")
        raise BadRequestException(
            details=[ErrorDetail(field="intent", message="it is empty")]
        )

    logger.info("=" * 80)
    logger.info("🎯 收到聊天请求！")
    logger.info(f"用户: {request.user_info} (ID: {request.user_id})")
    logger.info(f"消息: {request.user_input[:50]}...")
    logger.info("=" * 80)
    # 处理聊天消息
    diagnosis_service = DiagnosisService()
    data_address = []
    if request.data_addresses:
        for add in request.data_addresses:
            data_address.append(add.to_dict())

    user_info = request.user_info
    if not user_info:
        user_info = UserInfo(userid=request.user_id, username="", id_token="")
    shared_context = request.shared_context
    if not shared_context:
        shared_context = SharedContext(
            user_id=request.user_id,
            intent=request.intent,
            user_input=request.user_input,
            round_number=0,
        )

    logger.info(f"用户消息: {user_info}...")
    logger.info("SharedContext", **shared_context.to_dict())
    for s in data_address:
        logger.info("数据源", **s)

    logger.info("=" * 80)

    start_time = time.perf_counter()
    result = await diagnosis_service.handle_chat(
        user_input=request.user_input,
        user_id=request.user_id,
        data_addresses=data_address,
        shared_context=shared_context.to_dict(),
        user_info=user_info.to_dict(),
    )
    elapsed_seconds = time.perf_counter() - start_time

    if not result:
        raise DiagnosisError(message="诊断错误")
    if result.get("error", "") != "":
        raise DiagnosisModelError(
            message="诊断模型出现错误",
            detail=[ErrorDetail(field=k, message=v) for k, v in result],
        )

    # 构建响应
    result["status"] = Status.SUCCESS
    result["timestamp"] = datetime.now()
    result["processing_time"] = elapsed_seconds

    response = from_dict(result)
    logger.info(f"聊天响应生成成功: {result.get('agent_name')}")
    return response
