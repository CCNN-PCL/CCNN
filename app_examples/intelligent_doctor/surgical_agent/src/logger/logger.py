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
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from structlog.contextvars import merge_contextvars
from structlog.types import EventDict

from src.config.settings import settings

# 上下文变量用于存储请求ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def add_request_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """添加请求ID到日志"""
    request_id = request_id_ctx.get()
    if request_id:
        event_dict["request_id"] = request_id

    user_id = user_id_ctx.get()
    if user_id:
        event_dict["user_id"] = user_id

    return event_dict


def add_timestamp(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """添加ISO格式的时间戳"""
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """添加日志级别"""
    event_dict["level"] = method_name.upper()
    return event_dict


def rename_event_key(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """重命名事件键名"""
    event_dict["message"] = event_dict.pop("event")
    return event_dict


def sanitize_sensitive_data(
    logger: Any, method_name: str, event_dict: EventDict
) -> EventDict:
    """脱敏处理敏感数据"""
    sensitive_keys = ["password", "token", "secret", "key", "authorization"]

    for key in list(event_dict.keys()):
        key_lower = key.lower()
        for sensitive in sensitive_keys:
            if sensitive in key_lower:
                event_dict[key] = "***REDACTED***"
                break

    return event_dict


# 处理器链
COMMON_PROCESSORS = [
    merge_contextvars,  # 合并上下文变量
    add_timestamp,  # 添加时间戳
    add_log_level,  # 添加日志级别
    add_request_id,  # 添加请求ID
    sanitize_sensitive_data,  # 脱敏处理
    rename_event_key,  # 重命名事件键
]


def get_development_processors():
    """开发环境处理器链"""
    return [
        *COMMON_PROCESSORS,
        structlog.dev.ConsoleRenderer(colors=True),  # 彩色控制台输出
    ]


def get_production_processors():
    """生产环境处理器链"""
    return [
        *COMMON_PROCESSORS,
        structlog.processors.JSONRenderer(),  # JSON格式输出
    ]


def setup_logging():
    """配置结构化日志系统"""

    # 配置日志 - 详细格式输出
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # 禁用第三方库的噪声日志
    logging.getLogger("uvicorn.access").disabled = True

    # 根据环境选择处理器
    if settings.DEBUG:
        processors = get_development_processors()
    else:
        processors = get_production_processors()

    # 配置structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper())
        ),
        cache_logger_on_first_use=True,
    )


# 导出日志记录器
def get_logger(name: str = "app") -> structlog.BoundLogger:
    """获取日志记录器实例"""
    return structlog.get_logger(name)


# 上下文管理器
class LogContext:
    """日志上下文管理器"""

    def __init__(self, request_id: Optional[str] = None, user_id: Optional[str] = None):
        self.request_id = request_id
        self.user_id = user_id
        self._token_request_id = None
        self._token_user_id = None

    def __enter__(self):
        if self.request_id:
            self._token_request_id = request_id_ctx.set(self.request_id)
        if self.user_id:
            self._token_user_id = user_id_ctx.set(self.user_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token_request_id:
            request_id_ctx.reset(self._token_request_id)
        if self._token_user_id:
            user_id_ctx.reset(self._token_user_id)
