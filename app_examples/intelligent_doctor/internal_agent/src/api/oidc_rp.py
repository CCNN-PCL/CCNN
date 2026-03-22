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

# oidc_rp.py
import logging
import time
import uuid
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import jwt
import requests
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

# 复用 main.py 的日志配置
logger = logging.getLogger(__name__)
medical_frontend = "http://172.25.21.129:8089"
# OIDC提供者配置
OIDC_CONFIG = {
    "issuer": "http://192.168.193.12:31111",  # cybertwin安全代理
    "client_id": "agent_doctor1",
    "client_secret": "agent_doctor1-secret",
    "redirect_uri": "http://172.25.22.129:8000/oidc/callback",  # 本机回调地址
    "scope": "openid profile email",
    "post_logout_redirect_uri": medical_frontend,  # 登出回调地址
}

# ---------- 工具：OP 配置 & JWKS ----------
_op_config: Optional[dict] = None
# 全局变量用于缓存 JWKS 和缓存时间
_jwks: Optional[dict] = None
_jwks_timestamp: Optional[float] = None
JWKS_CACHE_DURATION = 3600  # 缓存1小时（3600秒）
UserInput_data = ""
userinfo: dict[str, str | None] = {"username": None, "userid": None}


def get_oidc_config() -> dict:
    global _op_config
    if _op_config is None:
        resp = requests.get(f"{OIDC_CONFIG['issuer']}/.well-known/openid-configuration")
        resp.raise_for_status()
        _op_config = resp.json()
    return _op_config


def get_jwks() -> dict:
    global _jwks, _jwks_timestamp
    current_time = time.time()

    # 如果缓存存在且未过期，直接返回
    if (
        _jwks is not None
        and _jwks_timestamp is not None
        and current_time - _jwks_timestamp < JWKS_CACHE_DURATION
    ):
        return _jwks

    # 否则重新获取 JWKS
    cfg = get_oidc_config()
    resp = requests.get(cfg["jwks_uri"])
    resp.raise_for_status()
    _jwks = resp.json()
    _jwks_timestamp = current_time
    return _jwks


# ---------- FastAPI ----------
router = APIRouter(tags=["OIDC-RP"])

# ---------- 浏览器加密 Cookie Session（Flask 同款） ----------
from itsdangerous import URLSafeTimedSerializer

SESSION_COOKIE_NAME = "rp_session"
SESSION_SECRET = "oidc-rp-secret-key-32-bytes"  # 生产换环境变量
SERIALIZER = URLSafeTimedSerializer(SESSION_SECRET, salt="session")
from starlette.middleware.base import BaseHTTPMiddleware

"""'
request.scope["session"]：在 FastAPI 内部传递会话数据的键名
SESSION_COOKIE_NAME：浏览器中存储的 cookie 的名称
"""


# 在oidc_rp.py中修复会话处理
class FlaskLikeSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        cookie = request.cookies.get(SESSION_COOKIE_NAME)
        session_data = {}

        if cookie:
            try:
                session_data = SERIALIZER.loads(cookie, max_age=3600)
            except Exception as e:
                logger.warning(f"Session cookie invalid: {e}")
                session_data = {}

        request.scope["session"] = session_data
        response = await call_next(request)

        current_session = request.scope.get("session", {})

        if current_session:
            value = SERIALIZER.dumps(current_session)
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=value,
                # max_age=3600 * 24 * 7,  # 延长有效期
                httponly=True,
                secure=False,
                samesite="lax",
                path="/",  # 确保根路径
                domain=None,  # 明确设置为 None
            )
        elif cookie:
            response.delete_cookie(SESSION_COOKIE_NAME, path="/")

        return response


# def get_session(request: Request) -> Dict[str, Any]:
#     cookie = request.cookies.get(SESSION_COOKIE_NAME)
#     if not cookie:
#         return {}
#     try:
#         return SERIALIZER.loads(cookie, max_age=3600)
#     except Exception:
#         return {}

# def set_session(response: Response, data: Dict[str, Any]):
#     value = SERIALIZER.dumps(data)
#     response.set_cookie(
#         SESSION_COOKIE_NAME,
#         value,
#         max_age=3600,
#         httponly=True,
#         samesite="lax",
#         secure=False,  # 开发用 http
#     )

# def clear_session(response: Response):
#     response.delete_cookie(SESSION_COOKIE_NAME)


# ---------- 路由：首页（/） ----------
@router.get("/")
def index(request: Request, user_id: str = Query(None), user_input: str = Query(None)):
    logger.info(
        "===========================启动程序=============================================="
    )

    global UserInput_data
    global userinfo
    print("输入参数user_id", user_id, "user_input", user_input)
    UserInput_data = {"user_id": user_id, "user_input": user_input}
    """已登录→跳聊天；未登录→跳登录"""
    # session = get_session(request)
    session = request.scope["session"]
    logger.info("[OIDC] session=%s user_info=%s", session, session.get("user_info"))
    if session.get("user_info") or userinfo.get("username"):
        print(userinfo, session.get("user_info"))
        if session.get("user_info"):
            return JSONResponse(
                {
                    "islogin": True,
                    "username": session["user_info"]["name"],  # 跨域的情况获取不了
                    "userid": session["user_info"]["sub"],  # user_id
                    "id_token": session["id_token"],
                    "userinput": user_input,
                }
            )
        else:
            return JSONResponse(
                {
                    "islogin": True,
                    "username": userinfo.get("username"),  # 跨域的情况获取不了
                    "userid": userinfo.get("userid"),  # user_id
                    "id_token": userinfo.get("id_token"),
                    "userinput": user_input,
                }
            )
    else:
        return JSONResponse(
            {
                "islogin": False,
            }
        )


# # ---------- 路由：登录 ----------
@router.get("/oidc/login")
def oidc_login(request: Request):
    logger.info(
        "===========================开始登录=============================================="
    )
    cfg = get_oidc_config()
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    # 保存 state 和 nonce 到会话
    session = request.scope["session"]
    session["oidc_state"] = state
    session["oidc_nonce"] = nonce
    response = RedirectResponse(
        f"{cfg['authorization_endpoint']}?"
        + urlencode(
            {
                "response_type": "code",
                "client_id": OIDC_CONFIG["client_id"],
                "redirect_uri": OIDC_CONFIG["redirect_uri"],
                "scope": OIDC_CONFIG["scope"],
                "state": state,
                "nonce": nonce,
            }
        )
    )
    # set_session(response, session)
    return response


# ---------- 路由：回调 ----------
@router.get("/oidc/callback")
async def oidc_callback(code: str, state: str, request: Request, response: Response):
    logger.info(
        "===========================回调认证=============================================="
    )

    session = request.scope["session"]
    saved_state = session.get("oidc_state")
    saved_nonce = session.get("oidc_nonce")

    if not (saved_state and saved_nonce) or saved_state != state:
        raise HTTPException(status_code=400, detail="Invalid state or nonce")
    try:
        # 换取令牌
        oidc_config = get_oidc_config()
        token_response = requests.post(
            oidc_config["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": OIDC_CONFIG["client_id"],
                "client_secret": OIDC_CONFIG["client_secret"],
                "redirect_uri": OIDC_CONFIG["redirect_uri"],
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_response.status_code != 200:
            # 打印日志 + 返回 400 + 原文
            print(
                f"Token request failed: {token_response.status_code} - {token_response.text}"
            )
            raise HTTPException(
                status_code=400, detail=f"Token request failed: {token_response.text}"
            )
        token_data = token_response.json()
        id_token = token_data["id_token"]
        access_token = token_data["access_token"]

        # 保存ID Token和过期时间，用于本地轻量检查
        # request.session['id_token'] = id_token
        # request.session['id_token_exp'] = jwt.decode(id_token, options={"verify_signature": False})['exp']
        if not id_token or not access_token:
            return "Token request failed: missing tokens", 400

        # 验证ID令牌
        jwks = get_jwks()
        if not jwks:
            return "JWKS not available", 500

        # 获取公钥
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwks["keys"][0])

        # ✅ 关键修复：创建自定义验证函数来处理时区差异
        def custom_time_verification(payload):
            """自定义时间验证，处理8小时时区差异"""
            current_time = time.time()

            # 调整当前时间：减去8小时（28800秒）
            adjusted_current_time = current_time - 28800

            # 检查过期时间
            if "exp" in payload:
                if payload["exp"] < adjusted_current_time:
                    raise jwt.ExpiredSignatureError("Token expired")

            # 检查签发时间（iat）
            if "iat" in payload:
                # 如果令牌的签发时间比调整后的当前时间还晚，说明令牌尚未生效
                if payload["iat"] > adjusted_current_time:
                    # 计算具体差异
                    time_diff = payload["iat"] - adjusted_current_time
                    raise jwt.InvalidTokenError(
                        f"Token not yet valid by {time_diff} seconds"
                    )

            # 检查生效时间（nbf）
            if "nbf" in payload:
                if payload["nbf"] > adjusted_current_time:
                    time_diff = payload["nbf"] - adjusted_current_time
                    raise jwt.InvalidTokenError(
                        f"Token not active for {time_diff} seconds"
                    )

            return True

        # 验证ID令牌
        id_payload = jwt.decode(
            id_token,  # ① 要验证的令牌
            public_key,  # ② 用来验签的公钥
            algorithms=["RS256"],  # ③ 指定只允许 RS256 算法
            audience=OIDC_CONFIG["client_id"],  # ④ 校验 "aud" 必须等于本客户端 ID
            # options={'verify_exp': True}       # ⑤ 强制校验过期时间 exp
            options={
                "verify_exp": False,  # 禁用自动过期验证
                "verify_iat": False,  # 禁用自动签发时间验证
                "verify_nbf": False,  # 禁用自动生效时间验证
            },
        )

        # 验证nonce
        if id_payload.get("nonce") != session.get("oidc_nonce"):
            return "ID token validation failed: invalid nonce", 401

        # 获取用户信息
        userinfo_response = requests.get(
            oidc_config["userinfo_endpoint"],
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            return f"Userinfo request failed: {userinfo_response.text}", 400

        user_info = userinfo_response.json()
        global userinfo
        userinfo["username"] = user_info["name"]
        userinfo["userid"] = user_info["sub"]
        userinfo["id_token"] = id_token
        # 存储用户信息到会话
        session["user_info"] = user_info
        # 额外保存 id_token 原文（供登出时用）
        session["id_token"] = id_token
        session["_permanent"] = True
        # 自己约定字段名
        # 清除临时值
        session.pop("oidc_state", None)
        session.pop("oidc_nonce", None)
        logger.info(f"用户信息已保存到会话: {session['user_info']}")
        user_params = session.get("user_params", {})

        # ✅ 创建响应并设置会话
        # 把参数继续拼到 8088/chat 上
        # url = f"http://192.168.193.12:31362/chat?{UserInput_data}"

        # response = RedirectResponse(url)
        # # response = RedirectResponse('http://localhost:8088/chat')
        # return response
        # 设置 Cookie
        response.set_cookie(
            key="session",
            value=session,  # 假设 session 是一个字符串
            httponly=True,  # 防止前端 JavaScript 访问
            samesite="None",  # 允许跨域
            secure="False",  # 只通过 HTTPS 传输
            path="/",  # 确保根路径
            domain=None,  # 明确设置为 None
        )

        url = medical_frontend
        return RedirectResponse(url=url, status_code=302)

    except jwt.ExpiredSignatureError:
        return "ID token expired", 401
    except jwt.InvalidTokenError as e:
        return f"Invalid token: {str(e)}", 401
    except Exception as e:
        return f"Callback processing failed: {str(e)}", 500


# # ---------- 小接口：当前用户名 ----------
# @router.get("/oidc/me")
# def oidc_me(request: Request):
#     logger.info("===========================获取用户名=========================================")
#     session = request.scope["session"]
#     logger.info(f"[OIDC] 当前会话: {session}")
#     global userinfo
#     if not session.get("user_info") and not userinfo:
#         return "未登录", 401


#     if session.get("user_info"):
#         return { "userid": session["user_info"]["sub"], "username": session["user_info"]["name"] }
#     else:
#         return { "userid": userinfo["userid"], "username": userinfo["username"]}
# ---------- 小接口：当前用户名 ----------
@router.get("/oidc/me")
def oidc_me(request: Request):
    logger.info(
        "===========================获取用户名========================================="
    )
    session = request.scope["session"]

    # session = get_session(request)
    print(session)
    if not session.get("user_info"):
        return JSONResponse(None, status_code=401)
    return {
        "userid": session["user_info"]["sub"],
        "username": session["user_info"]["name"],
        "token": session["id_token"],
    }


def get_current_user_info(session: dict) -> dict | None:
    """纯业务函数，和 FastAPI/HTTP 无关。"""
    user_info = session.get("user_info")
    if not user_info:
        return None
    return {"userid": user_info["sub"], "username": user_info["name"]}


def get_current_user_info(session: dict) -> dict | None:
    """纯业务函数，和 FastAPI/HTTP 无关。"""
    user_info = session.get("user_info")
    if not user_info:
        return None
    return {"userid": user_info["sub"], "username": user_info["name"]}


# ---------- 登出 ----------
@router.get("/oidc/logout")
def oidc_logout(request: Request):
    logger.info(
        "===========================登出========================================="
    )
    # 获取会话数据
    global userinfo
    session = request.scope["session"]
    user_info = session.get("user_info", {})
    user_id = user_info.get("sub") if user_info else userinfo.get("userid")

    # 清除对话记忆（如果用户已登录）
    if user_id:
        try:
            # 延迟导入，避免循环导入
            # 尝试从chat.py导入全局实例，如果失败则创建新实例
            try:
                from backend.api.chat import chat_service
            except ImportError:
                from backend.services.chat_service import ChatService

                chat_service = ChatService()

            chat_service.clear_dialogue_memory(user_id)
            logger.info(f"[OIDC登出] 已清除用户 {user_id} 的对话记忆")
        except Exception as e:
            logger.warning(f"[OIDC登出] 清除对话记忆失败: {str(e)}")

    userinfo = {"username": None, "userid": None}
    id_token_hint = session.get("id_token", "")
    logger.info(f"Logging out with id_token_hint: {id_token_hint}")

    # 清除服务器端会话数据（重要！）
    request.scope["session"] = {}  # 清空会话数据

    # 构建响应
    cfg = get_oidc_config()
    if "end_session_endpoint" in cfg:
        params = {"post_logout_redirect_uri": OIDC_CONFIG["post_logout_redirect_uri"]}
        if id_token_hint:
            params["id_token_hint"] = id_token_hint
        url = f"{cfg['end_session_endpoint']}?{urlencode(params)}"
        logger.info(f"Redirecting to end_session_endpoint: {url}")
        response = RedirectResponse(url)
    else:
        response = RedirectResponse("/")

    # 清除客户端 cookie
    response.delete_cookie(SESSION_COOKIE_NAME)

    return response


def get_current_session(request: Request) -> Dict[str, Any]:
    """获取当前会话（基于中间件）"""
    return request.scope.get("session", {})


def update_session(request: Request, updates: Dict[str, Any]):
    """更新会话数据"""
    session = request.scope.get("session", {})
    session.update(updates)
    request.scope["session"] = session
