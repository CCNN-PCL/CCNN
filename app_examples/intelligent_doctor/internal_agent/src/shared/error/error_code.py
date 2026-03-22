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

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

    VALIDATION_INVALID_PARAM = "VALIDATION_INVALID_PARAM"
    VALIDATION_MISSING_PARAM = "VALIDATION_MISSING_PARAM"
    AUTH_INVALID_API_KEY = "AUTH_INVALID_API_KEY"
    AUTH_MISSING_API_KEY = "AUTH_MISSING_API_KEY"
    DIAGNOSIS_ERROR = "DIAGNOSIS_ERROR"
    DIAGNOSIS_MODEL_ERROR = "DIAGNOSIS_MODEL_ERROR"
    DIAGNOSIS_TIMEOUT = "DIAGNOSIS_TIMEOUT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"


class ErrorDetail(BaseModel):
    """错误详情"""

    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """API错误响应格式"""

    status: str = Field(..., description="处理结果")
    error_code: ErrorCode = Field(..., description="业务错误代码")
    error_message: str = Field(..., description="错误消息")
    error_details: list[ErrorDetail] = Field(
        default_factory=list, description="错误详情列表"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="错误发生时间"
    )
    request_id: str | None = Field(None, description="请求ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "error",
                "error_code": "ERROR_CODE",
                "error_message": "错误描述",
                "error_details": {"field": "additional_info"},
                "request_id": "req_20250105_001",
                "timestamp": "2025-01-05T10:30:00Z",
            }
        }
    }
