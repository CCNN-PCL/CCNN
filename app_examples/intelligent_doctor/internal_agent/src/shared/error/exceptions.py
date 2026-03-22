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

from typing import Any, Dict, List

from fastapi import HTTPException, status

from src.shared.error.error_code import ErrorCode, ErrorDetail, ErrorResponse


class APIException(HTTPException):
    """基础API异常类"""

    def __init__(
        self,
        status_code: int,
        status: str,
        error_code: ErrorCode,
        message: str,
        details: List[ErrorDetail] | None = None,
        headers: Dict[str, Any] | None = None,
    ):
        self.status = status
        self.status_code = status_code
        self.error_code = error_code
        self.error_message = message
        self.error_details = details or []
        super().__init__(status_code=status_code, detail=message, headers=headers)

    def to_api_error(self, request_id: str | None = None) -> ErrorResponse:
        """转换为APIError对象"""
        return ErrorResponse(
            status=self.status,
            error_code=self.error_code,
            error_message=self.error_message,
            error_details=self.error_details,
            request_id=request_id,
        )


class BadRequestException(APIException):
    """错误请求异常"""

    def __init__(
        self,
        message: str = "请求参数错误",
        details: List[ErrorDetail] | None = None,
        headers: Dict[str, Any] | None = None,
    ):
        super().__init__(
            status="error",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.VALIDATION_INVALID_PARAM,
            message=message,
            details=details,
            headers=headers,
        )


class InternalServerError(APIException):
    """服务器内部错误"""

    def __init__(
        self,
        message: str = "服务器内部错误",
        headers: Dict[str, Any] | None = None,
    ):
        super().__init__(
            status="error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=message,
            headers=headers,
        )


class DiagnosisError(APIException):
    """诊断错误"""

    def __init__(
        self,
        message: str = "诊断错误",
        detail: list[ErrorDetail] | None = None,
        headers: Dict[str, Any] | None = None,
    ):
        super().__init__(
            status="error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=ErrorCode.DIAGNOSIS_ERROR,
            message=message,
            headers=headers,
            details=detail,
        )


class DiagnosisModelError(APIException):
    """诊断模型错误"""

    def __init__(
        self,
        message: str = "诊断模型错误",
        detail: list[ErrorDetail] | None = None,
        headers: Dict[str, Any] | None = None,
    ):
        super().__init__(
            status="error",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=ErrorCode.DIAGNOSIS_MODEL_ERROR,
            message=message,
            headers=headers,
            details=detail,
        )
