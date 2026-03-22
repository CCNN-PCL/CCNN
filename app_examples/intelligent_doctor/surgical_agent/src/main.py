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
后端API主服务
=============

基于FastAPI的后端API服务，提供RESTful接口
支持认证、聊天、医疗数据管理等功能

作者: QSIR
版本: 1.0
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter as Router
from fastapi import FastAPI
from starlette.types import Receive, Scope, Send

from src.api import auth, diagnosis
from src.api.oidc_rp import FlaskLikeSessionMiddleware
from src.config.settings import settings
from src.logger.log_middleware import LoggingMiddleware
from src.logger.logger import get_logger, setup_logging
from src.utils.database import get_database
from src.version import get_version, get_version_info

logger = get_logger(__name__)
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging()
    logger.info(
        "应用启动",
        version=get_version(),
        env="development" if settings.DEBUG else "production",
    )
    yield
    # 关闭时
    logger.info("应用关闭")


class NoSlashRedirectRouter(Router):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            path = scope["path"]
            # 去掉路径结尾的 /（根路径 / 保留）
            if path != "/" and path.endswith("/"):
                scope["path"] = path.rstrip("/")
        await super().__call__(scope, receive, send)


def create_application() -> FastAPI:
    # 创建FastAPI应用
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=get_version(),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )
    app.router = NoSlashRedirectRouter()

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(FlaskLikeSessionMiddleware)

    # 包含API路由
    app.include_router(auth.router, prefix="/api/v1/status", tags=["检查状态"])
    app.include_router(diagnosis.router, prefix="/api/v1/diagnosis", tags=["诊断"])

    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        try:
            # 检查数据库连接
            db = get_database()
            if db:
                return {
                    "status": "healthy",
                    "database": "connected",
                    "services": {
                        "auth": "running",
                        "chat": "running",
                        "medical": "running",
                        "user": "running",
                    },
                }
            else:
                return {"status": "unhealthy", "database": "disconnected"}
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @app.get("/api/v1/status")
    async def get_status():
        """获取系统状态"""
        return {
            "api_version": "1.0.0",
            "services": {
                "authentication": "active",
                "chat_agents": "active",
                "medical_data": "active",
                "user_management": "active",
            },
            "models": {
                "qwen": "available",
                "huatuo": "available",
                "huatuo2": "available",
            },
        }

    @app.get("/api/v1/version")
    async def get_version_endpoint():
        """获取应用版本信息"""
        version_info = get_version_info()
        return {
            "status": "success",
            "data": {
                "application": settings.PROJECT_NAME,
                "service_name": settings.SERVICE_NAME,
                "specialization": settings.SPECIALIZATION,
                **version_info,
            },
        }

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
