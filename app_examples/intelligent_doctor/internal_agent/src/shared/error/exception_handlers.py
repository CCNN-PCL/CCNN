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

from typing import Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.logger.logger import get_logger
from src.shared.error.error_code import ErrorCode, ErrorResponse
from src.shared.error.exceptions import APIException

logger = get_logger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """API异常处理器"""
    path = str(request.url.path)
    request_id = request.headers.get("X-Request-ID")

    error_response = exc.to_api_error(request_id=request_id)

    # 记录错误日志（根据不同级别）
    if 400 <= exc.status_code < 500:
        logger.warning(
            "客户端错误",
            status_code=exc.status_code,
            error_code=exc.error_code.value,
            message=exc.error_message,
            path=path,
            request_id=request_id,
            details=exc.error_details,
        )
    else:
        logger.error(
            "服务器错误",
            status_code=exc.status_code,
            error_code=exc.error_code.value,
            message=exc.error_message,
            path=path,
            request_id=request_id,
            details=exc.error_details,
            exc_info=True,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump_json(),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """参数验证异常处理器"""
    path = str(request.url.path)
    request_id = request.headers.get("X-Request-ID")

    # 转换错误详情格式
    details = []
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
    else:
        errors = exc.errors()

    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        if field.startswith("body."):
            field = field[5:]  # 移除 "body." 前缀

        details.append(
            {
                "field": field if field else None,
                "message": error.get("msg", "验证失败"),
                "code": error.get("type", "VALIDATION_ERROR"),
            }
        )

    error_response = ErrorResponse(
        status="error",
        error_code=ErrorCode.VALIDATION_ERROR,
        error_message="请求参数验证失败",
        error_details=details,
        request_id=request_id,
    )

    logger.warning(
        "参数验证失败",
        path=path,
        request_id=request_id,
        details=details,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump_json(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器（处理FastAPI内置异常）"""
    path = str(request.url.path)
    request_id = request.headers.get("X-Request-ID")

    # 映射HTTP状态码到错误代码
    error_code_mapping = {
        400: ErrorCode.VALIDATION_INVALID_PARAM,
        401: ErrorCode.AUTH_INVALID_API_KEY,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        503: ErrorCode.DIAGNOSIS_MODEL_ERROR,
        504: ErrorCode.DIAGNOSIS_TIMEOUT,
    }

    error_code = error_code_mapping.get(
        exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR
    )

    error_response = ErrorResponse(
        status="error",
        error_code=error_code,
        error_message=str(exc.detail),
        request_id=request_id,
    )

    logger.warning(
        "HTTP异常",
        status_code=exc.status_code,
        message=str(exc.detail),
        path=path,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump_json(),
        headers=exc.headers,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器（兜底处理）"""
    path = str(request.url.path)
    request_id = request.headers.get("X-Request-ID")

    error_response = ErrorResponse(
        status="error",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        error_message="服务器内部错误",
        request_id=request_id,
    )

    # 记录完整的异常信息
    logger.error(
        "未捕获的异常",
        exception_type=exc.__class__.__name__,
        exception_message=str(exc),
        path=path,
        request_id=request_id,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump_json(),
    )


def register_exception_handlers(app: FastAPI):
    """注册所有异常处理器"""

    # 注册自定义异常处理器
    app.add_exception_handler(APIException, api_exception_handler)

    # 注册验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)

    # 注册HTTP异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)

    # 注册通用异常处理器（应该最后注册）
    app.add_exception_handler(Exception, generic_exception_handler)
