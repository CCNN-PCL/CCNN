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
后端API主服务 - Cybertwin-Agent微服务
====================================

基于FastAPI的后端API服务，提供RESTful接口
支持认证、聊天、医疗数据管理等功能

作者: QSIR
版本: 2.0 - 微服务版本（端口8001）
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
import sys
import os

# 添加项目根目录到Python路径
# 从 backend/main.py 向上找到项目根目录
# backend/main.py -> backend -> cybertwin-agent-service -> microservices -> 项目根目录
current_file = os.path.abspath(__file__)
# 向上3级到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 加载.env文件（如果存在）
def load_env_file():
    """从 .env 文件加载环境变量"""
    from pathlib import Path
    env_file = Path('.env')
    if env_file.exists():
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(env_file, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            try:
                with open(env_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except Exception:
                return
        
        # 解析内容
        loaded_count = 0
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # 只有当前环境变量未设置时才设置（允许命令行覆盖）
                if key and key not in os.environ:
                    os.environ[key] = value
                    loaded_count += 1
        
        if loaded_count > 0:
            print(f"[环境变量] 从.env文件加载了 {loaded_count} 个环境变量")
    else:
        print("[环境变量] 未找到.env文件，使用默认配置或环境变量")

# 加载.env文件
load_env_file()

# 版本信息导入
from backend.version import get_version, get_version_info

from backend.api import auth, chat, medical, user, oidc_rp
from backend.api import third_party_reserve
from backend.services.auth_service import AuthService
from backend.utils.database import get_database
from shared.config.model_config import get_config
from backend.api.oidc_rp import FlaskLikeSessionMiddleware

# 配置日志 - 详细格式输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 设置共享模块的日志级别
logging.getLogger('shared').setLevel(logging.INFO)
logging.getLogger('shared.agents').setLevel(logging.INFO)
logging.getLogger('shared.llm_caller').setLevel(logging.INFO)

# 设置智能体的详细日志级别
agent_loggers = [
    'BaseAgent', 'CybertwinAgent', 'QuestioningAgent', 'InternalMedicineAgent', 
    'SurgicalAgent', 'SummaryAgent', 'TriageAgent', 'HistoryAgent',
    'ComprehensiveAgent', 'ImageAnalysisCoordinator', 'IntentRecognition'
]
for agent_name in agent_loggers:
    logging.getLogger(agent_name).setLevel(logging.INFO)

# 服务配置 - 微服务版本
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
SERVICE_NAME = os.getenv("SERVICE_NAME", "cybertwin-agent")

# 专科医生服务配置（从环境变量读取）
INTERNAL_MEDICINE_BEIJING_URL = os.getenv("INTERNAL_MEDICINE_BEIJING_URL", "http://localhost:8002")
INTERNAL_MEDICINE_SHANGHAI_URL = os.getenv("INTERNAL_MEDICINE_SHANGHAI_URL", "http://localhost:8003")
SURGICAL_BEIJING_URL = os.getenv("SURGICAL_BEIJING_URL", "http://localhost:8004")
SURGICAL_SHANGHAI_URL = os.getenv("SURGICAL_SHANGHAI_URL", "http://localhost:8005")

logger.info(f"[{SERVICE_NAME}] 服务配置:")
logger.info(f"  端口: {SERVICE_PORT}")
logger.info(f"  内科-北京: {INTERNAL_MEDICINE_BEIJING_URL}")
logger.info(f"  内科-上海: {INTERNAL_MEDICINE_SHANGHAI_URL}")
logger.info(f"  外科-北京: {SURGICAL_BEIJING_URL}")
logger.info(f"  外科-上海: {SURGICAL_SHANGHAI_URL}")

# 创建FastAPI应用
app = FastAPI(
    title="Cybertwin-Agent 微服务",
    description="智能医疗辅助系统 - 分诊医生微服务（API网关）",
    version=get_version(),
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS - 从环境变量读取前端地址，支持Kubernetes部署时配置
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://172.25.21.129:8089")
# 支持多个源，用逗号分隔
cors_origins_list = [origin.strip() for origin in CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,  # 支持多个源，从环境变量读取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(FlaskLikeSessionMiddleware)
# 安全配置
security = HTTPBearer()

# 初始化服务
auth_service = AuthService()

# 包含API路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天"])
app.include_router(medical.router, prefix="/api/v1/medical", tags=["医疗数据"])
app.include_router(user.router, prefix="/api/v1/user", tags=["用户管理"])
app.include_router(third_party_reserve.router, prefix="", tags=["第三方应用交互"])
app.include_router(oidc_rp.router, prefix="", tags=["OIDC-RP"])

@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db = get_database()
        if db:
            return {
                "status": "healthy",
                "service": SERVICE_NAME,
                "port": SERVICE_PORT,
                "database": "connected",
                "services": {
                    "auth": "running",
                    "chat": "running", 
                    "medical": "running",
                    "user": "running"
                },
                "specialist_services": {
                    "internal_medicine_beijing": INTERNAL_MEDICINE_BEIJING_URL,
                    "internal_medicine_shanghai": INTERNAL_MEDICINE_SHANGHAI_URL,
                    "surgical_beijing": SURGICAL_BEIJING_URL,
                    "surgical_shanghai": SURGICAL_SHANGHAI_URL
                }
            }
        else:
            return {
                "status": "unhealthy",
                "service": SERVICE_NAME,
                "database": "disconnected"
            }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "service": SERVICE_NAME,
            "error": str(e)
        }

@app.get("/version")
async def get_version_info_endpoint():
    """获取详细的版本信息"""
    version_info = get_version_info()
    return {
        "service": SERVICE_NAME,
        "port": SERVICE_PORT,
        "version_info": version_info,
        "health_check": "/health",
        "status": "/api/v1/status",
        "docs": "/api/docs"
    }

@app.get("/api/v1/status")
async def get_status():
    """获取系统状态"""
    return {
        "service": SERVICE_NAME,
        "api_version": get_version(),
        "port": SERVICE_PORT,
        "services": {
            "authentication": "active",
            "chat_agents": "active",
            "medical_data": "active",
            "user_management": "active"
        },
        "specialist_services": {
            "internal_medicine_beijing": INTERNAL_MEDICINE_BEIJING_URL,
            "internal_medicine_shanghai": INTERNAL_MEDICINE_SHANGHAI_URL,
            "surgical_beijing": SURGICAL_BEIJING_URL,
            "surgical_shanghai": SURGICAL_SHANGHAI_URL
        },
        "models": {
            "qwen": "available",
            "huatuo": "available",
            "huatuo2": "available"
        }
    }

# 依赖注入：获取当前用户
async def get_current_user(request: Request) -> dict:
    """
    依赖：Request（OIDC 会话）
    返回：{"userid": <sub>, "username": <name>}
    未登录直接抛 401，和原来 JWT 版本行为一致。
    """
    user_info = request.scope["session"].get("user_info")
    token = request.scope["session"].get("id_token")

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或会话已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("userid: ",user_info["sub"], "username:", user_info["name"])
    return {"userid": user_info["sub"], "username": user_info["name"],"token": token}

if __name__ == "__main__":
    # 确保项目根目录在Python路径中（修复多进程导入问题）
    import sys
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=SERVICE_PORT,
        reload=True,
        log_level="info"
    )
