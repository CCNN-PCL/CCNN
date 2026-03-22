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

from fastapi import APIRouter

from src.logger.logger import get_logger
from src.utils.database import health_check

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check_handler():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db_hc = await health_check()
        if db_hc.get("status", "unhealthy") == "healthy":
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
            return db_hc
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
