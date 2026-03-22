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
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.logger.logger import LogContext, get_logger

logger = get_logger("http")


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())

        # 记录请求开始
        start_time = time.time()

        # 设置请求ID到上下文
        with LogContext(request_id=request_id):
            try:
                # 处理请求
                response = await call_next(request)

                # 计算处理时间
                process_time = time.time() - start_time

                # 记录请求完成
                logger.info(
                    "HTTP请求完成",
                    method=request.method,
                    url=str(request.url),
                    status_code=response.status_code,
                    process_time=f"{process_time:.4f}s",
                    client_ip=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )

                # 添加请求ID到响应头
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as exc:
                # 计算处理时间
                process_time = time.time() - start_time

                # 记录异常
                logger.error(
                    "HTTP请求异常",
                    method=request.method,
                    url=str(request.url),
                    process_time=f"{process_time:.4f}s",
                    client_ip=request.client.host if request.client else None,
                    error=str(exc),
                    exc_info=True,
                )
                raise
