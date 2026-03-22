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

作者: AI开发团队
版本: 1.0
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import socketio
import uvicorn
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import requests
import jwt
from typing import Dict, Any, Optional
import uuid
from urllib.parse import urlencode
from config.url_config import ISSUER_URL, REDIRECT_URL, ORIGINS_URL
from backend.api import  chat
from backend.version import get_version_info, get_version_string
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import socketio
import uvicorn
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import requests
import jwt
from typing import Dict, Any, Optional
import uuid
from urllib.parse import urlencode
from config.url_config import ISSUER_URL, REDIRECT_URL, ORIGINS_URL
from backend.api import  chat

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

#URL参数
# print("*" * 80)
# print("✅ Simple URL config imported successfully")
# print(f"ISSUER_URL: {ISSUER_URL}")
# print(f"REDIRECT_URL: {REDIRECT_URL}")
# print(f"Full config: {URL_CONFIG}")
# print("*" * 80)

# 获取版本信息
version_info = get_version_info()
app_version = version_info.get_version()
app_build = version_info.get_build()

# 创建FastAPI应用
app = FastAPI(
    title="UserAgent私人代理API",
    description="UserAgent辅助系统后端API",
    version=f"{app_version}-{app_build}",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8080"], 
    allow_origins=[ORIGINS_URL], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.secret_key = 'oidc-client-secret-key'
SESSION_LIFETIME = timedelta(hours=1)
SESSION_CONFIG = {
    'cookie_name': 'rp_session',
    'samesite': 'lax',
    'secure': False,
    'httponly': True,
    'max_age': 3600  # 1小时
}

# 包含API路由
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["聊天"])
# app.include_router(medical.router, prefix="/api/v1/medical", tags=["医疗数据"])
#app.include_router(user.router, prefix="/api/v1/user", tags=["用户管理"])

# Socket.IO 配置
# sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# OIDC提供者配置
OIDC_CONFIG = {
    # 'issuer': 'http://localhost:5000',
    'issuer': ISSUER_URL,
    'client_id': 'user_agent',
    'client_secret': 'user_agent-secret',
    # 'redirect_uri': 'http://localhost:5050/callback',
    'redirect_uri': REDIRECT_URL + '/callback',
    'scope': 'openid profile email',
    # 'post_logout_redirect_uri': 'http://localhost:5050'
    'post_logout_redirect_uri': REDIRECT_URL
}

# 内存会话存储（生产环境用Redis）
session_store: Dict[str, Dict[str, Any]] = {}

def get_session(request: Request) -> Dict[str, Any]:
    """获取会话数据"""
    session_id = request.cookies.get(SESSION_CONFIG['cookie_name'])
    if session_id and session_id in session_store:
        # 检查会话是否过期
        session_data = session_store[session_id]
        if datetime.now() - session_data.get("created_at", datetime.now()) < SESSION_LIFETIME:
            return session_data.get("data", {})
        else:
            # 会话过期，删除
            del session_store[session_id]
    return {}

def update_session_data(session_id: str, data: Dict[str, Any]) -> None:
    """更新会话数据"""
    session_store[session_id] = {
        "created_at": datetime.now(),
        "data": data
    }

def get_or_create_session_id(request: Request) -> str:
    """获取或创建会话ID"""
    session_id = request.cookies.get(SESSION_CONFIG['cookie_name'])
    if not session_id or session_id not in session_store:
        session_id = str(uuid.uuid4())
        update_session_data(session_id, {})
    return session_id

def clear_session(session_id: str) -> None:
    """清除会话"""
    if session_id in session_store:
        del session_store[session_id]

def create_response_without_session(url: str) -> RedirectResponse:
    """创建不带会话cookie的重定向响应"""
    response = RedirectResponse(url=url)
    response.delete_cookie(SESSION_CONFIG['cookie_name'])
    return response

# 获取OIDC配置
def get_oidc_config():
    try:
        response = requests.get(f"{OIDC_CONFIG['issuer']}/.well-known/openid-configuration")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting OIDC config: {str(e)}")
    return None

# 获取JWKS
def get_jwks():
    try:
        oidc_config = get_oidc_config()
        if oidc_config:
            jwks_uri = oidc_config.get('jwks_uri')
            if jwks_uri:
                response = requests.get(jwks_uri)
                if response.status_code == 200:
                    return response.json()
    except Exception as e:
        print(f"Error getting JWKS: {str(e)}")
    return None

@app.get("/")
async def root(request: Request):
    # 获取会话数据
    session_data = get_session(request)
    print("Session data:", session_data)
    # 检查用户是否已登录
    if 'user_info' not in session_data:
        return RedirectResponse(url='/login')
    return RedirectResponse(url='/chat')

@app.route('/login')
async def login(request: Request):
    """登录重定向"""
    oidc_config = get_oidc_config()
    if not oidc_config:
        return "OIDC provider configuration not available", 500

    # 生成随机state和nonce
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())

    # 获取或创建会话ID
    session_id = get_or_create_session_id(request)

    # 初始化会话存储
    if session_id not in session_store:
        session_store[session_id] = {"data": {}}


    # 存储state和nonce到会话
    session_store[session_id]["data"]['oidc_state'] = state
    session_store[session_id]["data"]['oidc_nonce'] = nonce
    print("login - session_id:", session_id)
    print("login - session_data:", session_store[session_id]["data"])
    print("保存state:", state)

    # 构建授权请求URL
    auth_endpoint = oidc_config['authorization_endpoint']
    params = {
        'response_type': 'code',
        'client_id': OIDC_CONFIG['client_id'],
        'redirect_uri': OIDC_CONFIG['redirect_uri'],
        'scope': OIDC_CONFIG['scope'],
        'state': state,
        'nonce': nonce
    }

    auth_url = f"{auth_endpoint}?{urlencode(params)}"
    print("auth_url", auth_url)

     # 创建重定向响应并设置cookie
    response = RedirectResponse(url=auth_url) 
    response.set_cookie(
        key="rp_session",
        value=session_id,
        max_age=3600,  # 1小时过期
        httponly=True,
        samesite="lax"
    )
    return response

@app.get("/callback")
async def callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None
):
    """处理OIDC回调"""
    print("callback") 
    
     # 获取会话数据
    session_data = get_session(request)
    session_id = get_or_create_session_id(request)

    print("callback message:", code, state) 
    print("oidc_state:", session_data.get('oidc_state'))  
    
    # 验证参数
    if not code or not state:
        raise HTTPException(
            status_code=400, 
            detail="Authorization failed: missing parameters"
        )  

    # 验证state
    if state != session_data.get('oidc_state'):
        raise HTTPException(
            status_code=400, 
            detail="Authorization failed: invalid state"
        )  

    try:
        oidc_config = get_oidc_config()
        if not oidc_config:
            raise HTTPException(
                status_code=500,
                detail="OIDC provider configuration not available"
            ) 

        # 获取令牌
        token_response = requests.post(
            oidc_config['token_endpoint'],
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': OIDC_CONFIG['client_id'],
                'client_secret': OIDC_CONFIG['client_secret'],
                'redirect_uri': OIDC_CONFIG['redirect_uri']
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )

        if token_response.status_code != 200:
            print(f"Token request failed: {token_response.status_code} - {token_response.text}")
            raise HTTPException(
                status_code=400,
                detail=f"Token request failed: {token_response.text}"
            )  

        token_data = token_response.json()
        id_token = token_data.get('id_token')
        access_token = token_data.get('access_token')

        print("id_token:", id_token)

        if not id_token or not access_token:
            raise HTTPException(
                status_code=400,
                detail="Token request failed: missing tokens"
            ) 

        # 验证ID令牌
        jwks = get_jwks()
        if not jwks:
            raise HTTPException(
                status_code=500,
                detail="JWKS not available"
            )  # 对应Flask的 return "JWKS not available", 500

        # 获取公钥
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwks['keys'][0])

        # 验证ID令牌
        id_payload = jwt.decode(
            id_token,
            public_key,
            algorithms=['RS256'],
            audience=OIDC_CONFIG['client_id'],
            options={'verify_exp': True}
        )

        # 验证nonce
        if id_payload.get('nonce') != session_data.get('oidc_nonce'):
            raise HTTPException(
                status_code=401,
                detail="ID token validation failed: invalid nonce"
            )  # 对应Flask的 return "ID token validation failed: invalid nonce", 401

        # 获取用户信息
        userinfo_response = requests.get(
            oidc_config['userinfo_endpoint'],
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Userinfo request failed: {userinfo_response.text}"
            )  # 对应Flask的 return f"Userinfo request failed: {userinfo_response.text}", 400

        user_info = userinfo_response.json()

        # 存储用户信息到会话
        new_session_data = session_data.copy()
        new_session_data['user_info'] = user_info
        new_session_data['id_token'] = id_token
        
        # 清除临时值
        new_session_data.pop('oidc_state', None)
        new_session_data.pop('oidc_nonce', None)
        
        # 保存更新后的会话数据
        update_session_data(session_id, new_session_data)
        
        username = user_info.get('sub')
        print(f"用户 {username} 登录成功")
        
        # 重定向到前端应用
        # return RedirectResponse(url='http://localhost:8080/chat')
        return RedirectResponse(url=ORIGINS_URL+'/chat')

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="ID token expired"
        )  # 对应Flask的 return "ID token expired", 401
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )  # 对应Flask的 return f"Invalid token: {str(e)}", 401
    except requests.exceptions.RequestException as e:
        print(f"Network error during callback processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Network error: {str(e)}"
        )
    except Exception as e:
        print(f"Callback processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Callback processing failed: {str(e)}"
        )  # 对应Flask的 return f"Callback processing failed: {str(e)}", 500

@app.get("/api/me")
async def me(request: Request):
    """获取当前用户信息"""
    # 获取会话数据
    session_data = get_session(request)
    session_id = get_or_create_session_id(request)
    
    print("Session data:", session_data) 
    user_info = session_data.get('user_info')
    print("User info:", user_info)
    
    if not user_info:
        # 对应Flask的 return jsonify(None), 401
        return JSONResponse(
            content=None,
            status_code=401
        )
    
    # 对应Flask的 return jsonify(username=session['user_info']['sub'])
    return {
        "userid": user_info.get('sub'),
        "username": user_info.get('name'),
        "trustscore":user_info.get('trustscore')
    }

@app.get("/logout")
async def logout(request: Request):
    """退出登录：通知 OP 并清本地会话"""
    # 获取会话数据
    session_data = get_session(request)
    session_id = get_or_create_session_id(request)
    
    try:
        oidc_config = get_oidc_config()
        if oidc_config and 'end_session_endpoint' in oidc_config:
            params = {
                'post_logout_redirect_uri': OIDC_CONFIG['post_logout_redirect_uri']
            }
            if 'user_info' in session_data:
                params['id_token_hint'] = session_data.get('id_token', '')
            
            print("params['id_token_hint']", params['id_token_hint'])
            
            logout_url = f"{oidc_config['end_session_endpoint']}?{urlencode(params)}"
            
            # 清除本地会话
            clear_session(session_id)
            
            print("会话已清除，session_id:", session_id)
            
            # 重定向到OP的登出端点
            return create_response_without_session(logout_url) 
            
    except Exception as e:
        print(f"SSO logout failed: {str(e)}") 

    # 兜底：异常或 OP 没有提供 end_session_endpoint 时
    clear_session(session_id)
    
    # 回到首页（未登录）
    return create_response_without_session("/")

@app.get("/api/v1/status")
async def get_status():
    """获取系统状态"""
    return {
        "api_version": "1.0.0",
        "services": {
            "authentication": "active",
            "chat_agents": "active",
            "medical_data": "active",
            "user_management": "active"
        },
        "models": {
            "qwen": "available",
            "huatuo": "available",
            "huatuo2": "available"
        }
    }

@app.get("/api/v1/version")
async def get_version_info_api():
    """获取详细的版本信息"""
    version_info = get_version_info()
    return {
        "version": version_info.get_version(),
        "build": version_info.get_build(),
        "build_date": version_info.get_build_date(),
        "git": version_info.get_git_info(),
        "copyright": version_info.get_copyright_info(),
        "metadata": version_info.get_metadata(),
        "python": version_info.get_python_info(),
        "system": version_info.get_system_info()
    }

@app.get("/api/v1/version/simple")
async def get_simple_version():
    """获取简化的版本信息"""
    return {
        "version": get_version_string("simple"),
        "full_version": get_version_string("compact")
    }

@app.get("/")
async def root(request: Request):
    """根路径 - 显示欢迎信息和版本"""
    version_str = get_version_string("compact")
    return {
        "message": "欢迎使用 UserAgent 私人代理 API",
        "version": version_str,
        "docs": "/api/docs",
        "status": "/api/v1/status",
        "version_info": "/api/v1/version"
    }


# Socket.IO 事件处理
# @sio.event
# async def connect(sid, environ):
#     print(f"✅ Socket.IO 客户端连接: {sid}")

# @sio.event
# async def disconnect(sid):
#     print(f"🔌 Socket.IO 客户端断开: {sid}")

# @sio.event
# async def message(sid, data):
#     print(f"📨 Socket.IO消息 from {sid}: {data}")
    
#     # 发送两次响应
#     await sio.emit('acknowledge', {
#         'message': 'Socket.IO请求已接收',
#         'timestamp': datetime.now().isoformat()
#     }, room=sid)
    
#     await sio.emit('chat_response', {
#         'agent_name': 'quwen',
#         'response': '这是通过Socket.IO的回复',
#         'timestamp': datetime.now().isoformat()
#     }, room=sid)

# # 挂载 Socket.IO
# socketio_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=5050,
        reload=True,
        log_level="info"
    )
