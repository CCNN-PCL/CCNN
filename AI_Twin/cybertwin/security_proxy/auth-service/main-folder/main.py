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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr
from typing import Literal, Optional, Dict, List
import httpx
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
import logging
import time  # 新增：时间处理
import math  # 新增：指数运算
import re  # 新增：MAC地址格式校验辅助

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化FastAPI应用
app = FastAPI(title="授权微服务", description="处理三种授权请求", version="1.0")

# K8s客户端初始化（Pod内自动使用InClusterConfig，本地开发用kubeconfig）
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()  # 本地开发时启用
v1 = client.CoreV1Api()

# ------------------------------
# 常量配置（新增JWT验证服务地址）
# ------------------------------
NAMESPACE = "cybertwin"  # 与模型服务同一命名空间
# ConfigMap名称（K8s中存储配置的资源名）
APP_ROLE_CM = "app-role-config"       # 应用→角色映射
ROLE_PERM_CM = "role-perm-config"     # 角色→权限映射
COMMON_DEVICE_CM = "common-device-config"  # 常用设备列表
IP_LOCATION_CM = "ip-location-config" # IP→地点映射
IP_ACCESS_SCORE_CM = "ip-access-score-config" # IP→接入得分映射
# 新增：JWT验证服务地址（按你提供的配置）
JWT_VERIFY_URL = "http://cybertwin-backend.cybertwin.svc.cluster.local:5000/jwt/verify"
# 模型调用地址（保持不变）
SENSITIVITY_MODEL_URL = "http://datainfer-service.abacmodel:80/predict_sensitivity"
MATCH_MODEL_URL = "http://matchinfer-service.abacmodel.svc.cluster.local:8000/predict"
USER_TRUST_MODEL_URL = "http://userinfer-service.abacmodel:80/evaluate"
# 超时配置（统一沿用10秒）
TIMEOUT = 10.0

# 新增：ConfigMap名称（对应新增的两个配置）
IP_CONNECTION_TYPE_CM = "ip-connection-type-config"  # IP→连接方式映射
CITY_NETWORK_RISK_CM = "city-network-risk-config"    # 城市→网络风险值映射
# 新增：敏感度减分值配置的ConfigMap
ADD_VALUE_CM = "add-value-config"  # 存储addvalue的ConfigMap
# 新增：衰减率配置的ConfigMap
DECAY_RATE_CM = "decay-rate-config"  # 存储decayrate1（密码衰减率）、decayrate2（生物特征衰减率）
# 新增：信任度加分值配置的ConfigMap
TRUST_SCORE_ADD_CM = "trust-score-add-config"  # 存储trust_score_add_value的ConfigMap

# ------------------------------
# 新增：mac/imsi白名单对应的ConfigMap名称（核心新增）
# ------------------------------
MAC_WHITELIST_CM = "mac-whitelist-config"  # 存储合法MAC地址白名单的ConfigMap
IMSI_WHITELIST_CM = "imsi-whitelist-config"  # 存储合法IMSI号码白名单的ConfigMap

# 新增：连接方式→固定得分映射（需求指定：5G=0.5，wifi=0.7，有线=0.9）
CONNECTION_SCORE_MAP = {
    "5G": 0.5,
    "wifi": 0.7,
    "有线": 1.2,
    "unknown": 0.5
}

# 新增：数据类型→格式映射（按需求定义）
CONTENT_TYPE_MAP = {
    "病史数据": "text",
    "用药记录": "text",
    "化验报告": "text",
    "手术记录": "text",
    "影像数据": "image"
}

# 允许的原始数据类型（用于校验）
ALLOWED_RAW_TYPES = set(CONTENT_TYPE_MAP.keys())

# ------------------------------
# 全局变量（核心修改）
# ------------------------------
# 初始默认值0.5，每次调用/evaluate/user-trust成功后自动更新
saved_trust_score: float = 0.5

# 新增：用户登录相关全局变量
last_pswd_login_time: Optional[float] = None  # 上次密码登录时间戳（秒）
last_bio_login_time: Optional[float] = None  # 上次生物登录时间戳（秒）
pswdold: float = 0.0  # 上次密码登录的pswd值（初始默认0.0）
bioold: float = 0.0   # 上次生物登录的bio值（初始默认0.0）
timegap_pswd: int = 0  # 密码登录时间差（分钟，四舍五入后）
timegap_bio: int = 0  # 生物登录时间差（分钟，四舍五入后）

# ------------------------------
# 请求/响应数据模型（核心修改 + 新增mac/imsi请求模型）
# ------------------------------
# 1. 应用-角色-权限授权请求（保持不变）
class AppAuthRequest(BaseModel):
    app_name: str = Field(..., description="应用名称（如medicalAI）")
    data_type: str = Field(..., description="数据类型（如medical）")
    operation_type: Literal["read", "write", "delete", "update"] = Field(..., description="操作类型")

# 2. 信任度-敏感度授权请求（核心修改：仅保留token字段）
class NewTrustSensitivityAuthRequest(BaseModel):
    token: str = Field(..., description="JWT令牌（payload需包含department和type字段，type格式为'病史数据 用药记录 ...'）")

# 3. 用户信任度评估请求（核心修改：新增pswd字段）
class UserTrustRequest(BaseModel):
    ipaddress: str = Field(..., description="IP地址（如192.168.1.100）")
    time: int = Field(..., ge=0, le=23, description="访问时间（小时，0-23）")
    bio: float = Field(..., ge=0.0, le=1.0, description="生物特征匹配度（0-1）")
    device: str = Field(..., description="设备标识（如device_123、iPhone14）")
    city: str = Field(..., description="城市（如长沙）")
    # 新增pswd字段 ↓↓↓
    pswd: float = Field(..., ge=0.0, le=1.0, description="密码验证得分（0-1）")

# 4. 新增：简易敏感度授权请求模型（仅输入数据敏感度等级）
class SensitivitySimpleAuthRequest(BaseModel):
    sensitivity_score: float = Field(..., ge=0.0, description="数据敏感度等级（数值越大敏感度越高）")

# ------------------------------
# 新增：mac/imsi校验请求模型（核心新增）
# ------------------------------
class MacImsiAuthRequest(BaseModel):
    mac: str = Field(
        ...,
        description="设备MAC地址（格式如70:C9:4E:E2:FF:1B）",
        # 可选：MAC地址格式正则校验，提高接口健壮性
        pattern=r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
    )
    imsi: str = Field(
        ...,
        description="用户IMSI号码（格式如466920000000001）",
        # 可选：IMSI格式校验（15位数字）
        min_length=15,
        max_length=15,
        pattern=r"^\d{15}$"
    )

# 响应模型（核心修改）
class AuthResponse(BaseModel):
    result: Literal["allow", "deny"] = Field(..., description="授权结果")
    message: Optional[str] = Field(None, description="附加信息")

class TrustScoreResponse(BaseModel):
    trust_score: float = Field(..., description="用户信任度打分（0-1）")
    status: str = Field(..., description="状态（success/failed）")
    message: str = Field(..., description="描述信息")

# 新增：信任度-敏感度授权专用响应模型（替换原AuthResponse）
class TrustSensitivityAuthResponse(BaseModel):
    valid: bool = Field(..., description="授权结果（true=通过，false=拒绝/令牌无效/调用失败）")
    message: Optional[str] = Field(None, description="附加信息（错误原因/授权详情）")

# ------------------------------
# 工具函数（保持不变）
# ------------------------------
def get_configmap(cm_name: str) -> Dict[str, str]:
    """读取K8s ConfigMap数据，失败则抛异常"""
    try:
        cm = v1.read_namespaced_config_map(name=cm_name, namespace=NAMESPACE)
        return cm.data or {}
    except ApiException as e:
        logger.error(f"读取ConfigMap[{cm_name}]失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置读取失败：{cm_name}")

def parse_json_config(cm_name: str, key: str) -> Dict:
    """解析ConfigMap中JSON格式的配置（如角色权限、常用设备）"""
    cm_data = get_configmap(cm_name)
    value = cm_data.get(key)
    if not value:
        raise HTTPException(status_code=500, detail=f"ConfigMap[{cm_name}]缺少key: {key}")
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"ConfigMap[{cm_name}][{key}]格式错误（需JSON）")

# ------------------------------
# 新增：辅助函数 - 从ConfigMap中提取白名单列表（核心新增）
# ------------------------------
def get_whitelist_from_cm(cm_name: str, key: str = "whitelist") -> List[str]:
    """
    从ConfigMap中提取白名单列表（支持换行/逗号分隔格式）
    :param cm_name: ConfigMap名称
    :param key: ConfigMap中存储白名单的键名
    :return: 去重、过滤空值后的白名单列表（统一转大写/去除空格，提高兼容性）
    """
    cm_data = get_configmap(cm_name)
    whitelist_str = cm_data.get(key, "")
    
    if not whitelist_str:
        logger.warning(f"ConfigMap[{cm_name}]的key[{key}]为空，返回空白名单")
        return []
    
    # 支持两种分隔格式：换行（优先）、逗号
    if "\n" in whitelist_str:
        whitelist_list = whitelist_str.split("\n")
    else:
        whitelist_list = whitelist_str.split(",")
    
    # 数据清洗：去重、过滤空值、去除首尾空格、MAC地址统一转大写（IMSI不影响）
    cleaned_whitelist = []
    for item in whitelist_list:
        cleaned_item = item.strip()
        if cleaned_item:
            # MAC地址统一转大写，提高匹配兼容性（如70:c9:4e → 70:C9:4E）
            if ":" in cleaned_item:
                cleaned_item = cleaned_item.upper()
            cleaned_whitelist.append(cleaned_item)
    
    # 去重（保持顺序）
    final_whitelist = list(dict.fromkeys(cleaned_whitelist))
    logger.info(f"从ConfigMap[{cm_name}]提取到有效白名单，共{len(final_whitelist)}条记录")
    return final_whitelist

# ------------------------------
# 核心接口实现（核心修改 + 新增mac/imsi校验接口）
# ------------------------------
@app.post("/auth/app-role", response_model=AuthResponse, summary="应用-角色-权限授权")
async def app_role_auth(request: AppAuthRequest):
    """逻辑：应用名称→角色→权限，判断是否允许操作数据"""
    # 1. 应用→角色（ConfigMap: app-role-config，key=应用名，value=角色名）
    app_role_data = get_configmap(APP_ROLE_CM)
    role = app_role_data.get(request.app_name)
    if not role:
        return AuthResponse(result="deny", message=f"应用[{request.app_name}]未配置角色")
    
    # 2. 角色→权限（ConfigMap: role-perm-config，key=角色名，value=JSON{"数据类型": ["操作列表"]}）
    role_perm = parse_json_config(ROLE_PERM_CM, role)
    allowed_ops = role_perm.get(request.data_type, [])
    
    # 3. 权限校验
    if request.operation_type in allowed_ops:
        return AuthResponse(
            result="allow",
            message=f"授权通过：应用[{request.app_name}]（角色[{role}]）拥有{request.data_type}:{request.operation_type}权限"
        )
    else:
        return AuthResponse(
            result="deny",
            message=f"授权拒绝：应用[{request.app_name}]缺少{request.data_type}:{request.operation_type}权限"
        )

@app.post(
    "/auth/trust-sensitivity", 
    response_model=TrustSensitivityAuthResponse,  # 改用新响应模型
    summary="信任度-敏感度授权"
)
async def trust_sensitivity_auth(request: NewTrustSensitivityAuthRequest):
    """逻辑：验证JWT令牌→提取department和type→拆分类型→合并生成内容→多轮调用敏感度模型→取最高分→调用匹配模型→返回结果
    核心修改：
    1. 响应改为 valid: true/false，所有异常场景均返回 valid: false
    2. 取消HTTP异常抛出，统一返回200状态码+valid字段标识结果
    3. 新增读取addvalue配置并调整敏感度分数：max{1, 原分数 - addvalue}
    """
    async with httpx.AsyncClient() as client:
        # ------------------------------
        # 步骤1：验证JWT令牌有效性并提取关键信息
        # ------------------------------
        logger.info(f"开始处理信任度-敏感度授权请求，使用保存的信任度：{saved_trust_score}")
        try:
            # 调用外部JWT验证服务
            jwt_resp = await client.post(
                JWT_VERIFY_URL,
                json={"token": request.token},  # 按JWT服务要求的格式传参
                timeout=TIMEOUT
            )
            jwt_resp.raise_for_status()  # 抛出HTTP错误（如404、500）
            jwt_data = jwt_resp.json()
            logger.info(f"JWT验证服务返回结果：{jwt_data}")
        except httpx.RequestError as e:
            # 场景1：JWT验证服务调用失败（超时/不可达）→ 返回valid: false
            logger.error(f"调用JWT验证服务失败：{e}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="JWT验证服务不可用，请稍后重试"
            )
        
        # 场景2：令牌无效（valid=false）→ 返回valid: false
        if not jwt_data.get("valid", False):
            error_msg = jwt_data.get("error", "未知错误")
            logger.warning(f"JWT令牌无效：{error_msg}，令牌：{request.token[:20]}...")
            return TrustSensitivityAuthResponse(
                valid=False,
                message=f"令牌无效：{error_msg}（请重新获取令牌）"
            )
        
        # 提取payload中的department和type字段
        payload = jwt_data.get("payload", {})
        department = payload.get("department")
        # 场景3：缺少有效department字段→ 返回valid: false
        if not department or not isinstance(department, str):
            logger.warning(f"JWT令牌payload中缺少有效department字段，payload：{payload}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="令牌中未包含有效部门信息（department字段缺失或格式错误）"
            )
        
        type_val = payload.get("data_types")  # 变量名修改为type_val，避免与关键字冲突
        # 场景4：缺少有效type字段→ 返回valid: false
        if not type_val or not isinstance(type_val, str):
            logger.warning(f"JWT令牌payload中缺少有效type字段，payload：{payload}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="令牌中未包含有效类型信息（type字段缺失或格式错误）"
            )
        
        logger.info(f"JWT验证通过，提取部门信息：{department}，原始类型信息：{type_val}")

        # ------------------------------
        # 步骤2：拆分类型、过滤无效值、合并生成数据内容
        # ------------------------------
        # 按空格拆分类型，去重并过滤空字符串
        raw_type_list = list(set(type_val.split()))  # 去重
        raw_type_list = [t.strip() for t in raw_type_list if t.strip()]  # 过滤空字符串
        
        # 场景5：拆分后无有效类型→ 返回valid: false
        if not raw_type_list:
            logger.warning(f"拆分后的类型列表为空，原始type值：{type_val}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="令牌中type字段格式错误，未提取到有效数据类型"
            )
        
        # 过滤不允许的类型
        valid_type_list = [t for t in raw_type_list if t in ALLOWED_RAW_TYPES]
        invalid_type_list = [t for t in raw_type_list if t not in ALLOWED_RAW_TYPES]
        
        if invalid_type_list:
            logger.warning(f"存在不支持的原始类型，已忽略：{invalid_type_list}，支持的类型：{list(ALLOWED_RAW_TYPES)}")
        
        # 场景6：无有效支持的类型→ 返回valid: false
        if not valid_type_list:
            logger.warning(f"无有效数据类型，原始类型列表：{raw_type_list}，支持的类型：{list(ALLOWED_RAW_TYPES)}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message=f"无支持的数据类型，支持的类型：{list(ALLOWED_RAW_TYPES)}"
            )
        
        # 生成数据内容列表和对应的data_type
        data_content_list = []
        data_meta_list = []
        for raw_type in valid_type_list:
            data_content = f"{department}{raw_type}"  # 合并：部门+原始类型
            data_type = CONTENT_TYPE_MAP[raw_type]    # 动态获取数据格式
            data_content_list.append(data_content)
            data_meta_list.append({
                "content": data_content,
                "data_type": data_type
            })
        
        logger.info(f"生成有效数据内容列表：{data_content_list}，对应的data_type：{[meta['data_type'] for meta in data_meta_list]}")

        # ------------------------------
        # 步骤3：多轮调用敏感度模型，收集分数并取最高分
        # ------------------------------
        sensitivity_scores = []
        for idx, data_meta in enumerate(data_meta_list):
            content = data_meta["content"]
            data_type = data_meta["data_type"]
            logger.info(f"第{idx+1}/{len(data_meta_list)}次调用敏感度模型，输入：{data_meta}")
            
            try:
                sens_resp = await client.post(
                    SENSITIVITY_MODEL_URL,
                    json=data_meta,
                    timeout=TIMEOUT
                )
                sens_resp.raise_for_status()
                sens_data = sens_resp.json()
                score = sens_data.get("final_sensitivity_score")
                
                if score is None or not isinstance(score, (int, float)):
                    logger.warning(f"第{idx+1}次调用敏感度模型未返回有效分数，响应：{sens_data}")
                    continue
                
                score = float(score)
                sensitivity_scores.append(score)
                logger.info(f"第{idx+1}次调用成功，内容：{content}，分数：{score}")
            except httpx.RequestError as e:
                logger.error(f"第{idx+1}次调用敏感度模型失败（内容：{content}）：{e}")
                # 单个调用失败不中断，继续处理其他内容
                continue
        
        # 场景7：所有敏感度模型调用均未返回有效分数→ 返回valid: false
        if not sensitivity_scores:
            logger.error(f"所有敏感度模型调用均未返回有效分数，数据内容列表：{data_content_list}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="敏感度模型调用失败，未获取到有效分数"
            )
        
        # 取最高分作为最终敏感度分数
        sensitivity_score = max(sensitivity_scores)
        logger.info(f"所有有效分数：{sensitivity_scores}，最终取最高分：{sensitivity_score}")

        # ------------------------------
        # 步骤4前置：读取addvalue配置并计算新的敏感度分数
        # ------------------------------
        try:
            # 读取存储addvalue的ConfigMap
            add_value_data = get_configmap(ADD_VALUE_CM)
            addvalue = float(add_value_data.get("addvalue", 0))  # 默认值2
            logger.info(f"从ConfigMap[{ADD_VALUE_CM}]读取到addvalue：{addvalue}")
        except Exception as e:
            # 读取失败时使用默认值2（兼容ConfigMap不存在/读取异常等场景）
            logger.warning(f"读取addvalue ConfigMap[{ADD_VALUE_CM}]失败，使用默认值2，错误：{e}")
            addvalue = 0
        
        # 计算新的敏感度分数：max{1, 原分数 - addvalue}
        
        new_saved_trust_score = min(1.0, saved_trust_score + addvalue)
        logger.info(f"调整后的信任度分数：{new_saved_trust_score}（原分数：{saved_trust_score}，addvalue：{addvalue}）")

        # ------------------------------
        # 步骤4：调用信任度-敏感度匹配模型（使用保存的信任度和调整后的敏感度分数）
        # ------------------------------
        try:
            match_resp = await client.post(
                MATCH_MODEL_URL,
                params={
                    "trust_score": new_saved_trust_score,  # 改用服务内保存的信任度
                    "sensitivity_level": sensitivity_score  # 使用调整后的分数
                },
                timeout=TIMEOUT
            )
            match_resp.raise_for_status()
            match_data = match_resp.json()
            allowed = match_data.get("allowed", False)
            logger.info(f"匹配模型返回授权结果：{'允许' if allowed else '拒绝'}")
        except httpx.RequestError as e:
            # 场景8：匹配模型调用失败→ 返回valid: false
            logger.error(f"匹配模型调用失败：{e}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="信任度-敏感度匹配模型不可用"
            )
    
    # 正常流程：映射结果为valid（allow→true，deny→false）
    valid = True if allowed else False
    message = (
        f"授权结果：{'通过' if valid else '拒绝'} | 保存的信任度：{saved_trust_score:.3f} | "
        f"有效数据内容：{data_content_list} | 各内容敏感度分数：{sensitivity_scores} | "
        f"原始信任度：{saved_trust_score} | addvalue：{addvalue} | "
        f"调整后信任度：{new_saved_trust_score}"
    )
    return TrustSensitivityAuthResponse(valid=valid, message=message)

# ------------------------------
# 新增：简易敏感度授权接口
# ------------------------------
@app.post(
    "/auth/sensitivity-simple",
    response_model=TrustSensitivityAuthResponse,
    summary="简易敏感度授权（仅输入敏感度等级）"
)
async def sensitivity_simple_auth(request: SensitivitySimpleAuthRequest):
    """逻辑：仅输入数据敏感度等级→读取addvalue调整信任度→调用匹配模型→返回授权结果"""
    async with httpx.AsyncClient() as client:
        logger.info(f"开始处理简易敏感度授权请求，输入敏感度等级：{request.sensitivity_score}")
        
        # ------------------------------
        # 步骤1：读取addvalue配置并调整信任度
        # ------------------------------
        try:
            # 读取存储addvalue的ConfigMap
            add_value_data = get_configmap(ADD_VALUE_CM)
            addvalue = float(add_value_data.get("addvalue", 0))
            logger.info(f"从ConfigMap[{ADD_VALUE_CM}]读取到addvalue：{addvalue}")
        except Exception as e:
            # 读取失败时使用默认值0（兼容异常场景）
            logger.warning(f"读取addvalue ConfigMap[{ADD_VALUE_CM}]失败，使用默认值0，错误：{e}")
            addvalue = 0
        
        # 调整信任度（限制在0-1范围内）
        new_saved_trust_score = min(1.0, saved_trust_score + addvalue)
        logger.info(f"调整后的信任度分数：{new_saved_trust_score}（原分数：{saved_trust_score}，addvalue：{addvalue}）")

        # ------------------------------
        # 步骤2：调用信任度-敏感度匹配模型
        # ------------------------------
        try:
            match_resp = await client.post(
                MATCH_MODEL_URL,
                params={
                    "trust_score": new_saved_trust_score,  # 调整后的信任度
                    "sensitivity_level": request.sensitivity_score  # 输入的敏感度等级
                },
                timeout=TIMEOUT
            )
            match_resp.raise_for_status()
            match_data = match_resp.json()
            allowed = match_data.get("allowed", False)
            logger.info(f"匹配模型返回授权结果：{'允许' if allowed else '拒绝'}")
        except httpx.RequestError as e:
            # 匹配模型调用失败→ 返回valid: false
            logger.error(f"匹配模型调用失败：{e}")
            return TrustSensitivityAuthResponse(
                valid=False,
                message="信任度-敏感度匹配模型不可用"
            )
    
    # 构建返回结果
    valid = True if allowed else False
    message = (
        f"授权结果：{'通过' if valid else '拒绝'} | 原始信任度：{saved_trust_score:.3f} | "
        f"addvalue：{addvalue} | 调整后信任度：{new_saved_trust_score:.3f} | "
        f"输入敏感度等级：{request.sensitivity_score}"
    )
    return TrustSensitivityAuthResponse(valid=valid, message=message)

@app.post("/evaluate/user-trust", response_model=TrustScoreResponse, summary="用户信任度评估")
async def user_trust_evaluate(request: UserTrustRequest):
    """逻辑：查询ConfigMap补充信息→处理登录时间/分数衰减→调用评估模型→更新保存的信任度→返回打分"""
    # 1. 补充common_device（不变）
    device_data = get_configmap(COMMON_DEVICE_CM)
    common_devices = parse_json_config(COMMON_DEVICE_CM, "common_devices")
    common_device = request.device in common_devices

    # 新增：输出设备标识 + 是否为常用设备
    logger.info(f"设备标识[{request.device}]→是否为常用设备[{common_device}]")
    
    # 2. 补充location（不变）
    ip_location_data = get_configmap(IP_LOCATION_CM)
    location = ip_location_data.get(request.ipaddress, "others")
    
    # 3. IP→连接方式→access_network_score（不变）
    ip_conn_data = get_configmap(IP_CONNECTION_TYPE_CM)
    connection_type = ip_conn_data.get(request.ipaddress, "unknown")
    access_network_score = CONNECTION_SCORE_MAP.get(connection_type, 0.0)
    logger.info(f"IP[{request.ipaddress}]→连接方式[{connection_type}]→接入得分[{access_network_score}]")
    
    # 4. 修正逻辑：从JSON格式的ConfigMap中获取城市对应的network_risk（不变）
    try:
        # 4.1 读取ConfigMap的JSON字符串（Key=city_risk_map）
        city_risk_json = parse_json_config(CITY_NETWORK_RISK_CM, "city_risk_map")
        # 4.2 根据请求的城市名获取风险值（支持中文）
        network_risk_str = city_risk_json.get(request.city, "0.5")
        # 4.3 转换为浮点数并校验范围
        network_risk = float(network_risk_str)
        if not (0.0 <= network_risk <= 1.0):
            network_risk = 0.5
            logger.warning(f"城市[{request.city}]的网络风险值[{network_risk_str}]超出0-1范围，使用默认值0.5")
    except ValueError:
        # 配置值不是数字时，使用默认0.5
        network_risk = 0.5
        logger.error(f"城市[{request.city}]的网络风险值[{network_risk_str}]格式错误，使用默认值0.5")
    except Exception as e:
        # 其他异常（如JSON解析失败），使用默认0.5
        network_risk = 0.5
        logger.error(f"获取城市[{request.city}]网络风险值失败：{e}，使用默认值0.5")
    logger.info(f"城市[{request.city}]→网络风险值[{network_risk}]")
    
    # ------------------------------
    # 核心新增：处理登录时间和分数衰减逻辑
    # ------------------------------
    global pswdold, bioold, last_pswd_login_time, last_bio_login_time, timegap_pswd, timegap_bio
    current_time = time.time()  # 获取当前时间戳（秒）
    
    # 判断pswd或bio是否为1（浮点精度容错）
    pswd_is_1 = abs(request.pswd - 1.0) < 1e-9
    bio_is_not_0 = abs(request.bio) > 1e-9


    # 处理pswd_is_1的情况
    if pswd_is_1:
        last_pswd_login_time = current_time
        timegap_pswd = 0
        pswdold = request.pswd
        logger.info(
            f"触发密码登录更新：pswd={request.pswd:.4f}(1={pswd_is_1}) → "
            f"last_pswd_login_time={last_pswd_login_time:.2f}，pswdold={pswdold:.4f}，timegap_pswd={timegap_pswd}"
        )
    else:
        # 处理密码登录时间差
        if last_pswd_login_time is None:
            # 首次调用且无密码登录记录 → 初始化
            last_pswd_login_time = current_time
            timegap_pswd = 0
            pswdold = request.pswd
            logger.warning(
                f"首次调用且pswd非1、bio为0 → 初始化密码登录记录：last_pswd_login_time={last_pswd_login_time:.2f}，"
                f"pswdold={pswdold:.4f}，timegap_pswd={timegap_pswd}"
            )
        else:
            # 计算密码登录时间差（秒→分钟）并四舍五入
            time_diff_seconds = current_time - last_pswd_login_time
            time_diff_minutes = time_diff_seconds / 60
            timegap_pswd = round(time_diff_minutes)
            logger.info(
                f"计算密码登录时间差：上次密码登录={last_pswd_login_time:.2f}，当前={current_time:.2f} → "
                f"差值={time_diff_seconds:.2f}秒={time_diff_minutes:.2f}分钟 → 四舍五入timegap_pswd={timegap_pswd}分钟"
            )

    # 处理bio_is_not_0的情况
    if bio_is_not_0:
        last_bio_login_time = current_time
        timegap_bio = 0
        bioold = request.bio  # 修正用户描述中可能的笔误（原描述为pswdold，此处按逻辑调整为bioold）
        logger.info(
            f"触发生物登录更新：bio={request.bio:.4f}(1={bio_is_not_0}) → "
            f"last_bio_login_time={last_bio_login_time:.2f}，bioold={bioold:.4f}，timegap_bio={timegap_bio}"
        )
    else:
        # 处理生物登录时间差
        if last_bio_login_time is None:
            # 首次调用且无生物登录记录 → 初始化
            last_bio_login_time = current_time
            timegap_bio = 0
            bioold = request.bio
            logger.warning(
                f"首次调用且pswd非1、bio为0 → 初始化生物登录记录：last_bio_login_time={last_bio_login_time:.2f}，"
                f"bioold={bioold:.4f}，timegap_bio={timegap_bio}"
            )
        else:
            # 计算生物登录时间差（秒→分钟）并四舍五入
            time_diff_seconds = current_time - last_bio_login_time
            time_diff_minutes = time_diff_seconds / 60
            timegap_bio = round(time_diff_minutes)
            logger.info(
                f"计算生物登录时间差：上次生物登录={last_bio_login_time:.2f}，当前={current_time:.2f} → "
                f"差值={time_diff_seconds:.2f}秒={time_diff_minutes:.2f}分钟 → 四舍五入timegap_bio={timegap_bio}分钟"
            )

    # 读取衰减率配置（新增核心逻辑）
    try:
        decay_rate_data = get_configmap(DECAY_RATE_CM)
        # 读取并转换为浮点数，设置默认值10（兼容配置缺失场景）
        decayrate1 = float(decay_rate_data.get("decayrate1", 10))
        decayrate2 = float(decay_rate_data.get("decayrate2", 10))
        logger.info(f"从ConfigMap[{DECAY_RATE_CM}]读取到衰减率：decayrate1={decayrate1}, decayrate2={decayrate2}")
    except (ValueError, HTTPException) as e:
        # 转换失败或读取失败时使用默认值10
        decayrate1 = 10.0
        decayrate2 = 10.0
        logger.warning(f"读取/解析衰减率配置失败，使用默认值10，错误：{e}")

    # 分别计算密码和生物登录的衰减因子及衰减后的值（修改固定值为动态配置）
    decay_factor_pswd = math.exp(-timegap_pswd / decayrate1)
    decay_factor_bio = math.exp(-timegap_bio / decayrate2)
    decay_pswd = pswdold * decay_factor_pswd * 0.3 if pswdold is not None else 0
    decay_bio = bioold * decay_factor_bio if bioold is not None else 0

    # 确保分数在0-1范围内（防止浮点误差超出范围）
    decay_pswd = max(0.0, min(1.0, decay_pswd))
    decay_bio = max(0.0, min(1.0, decay_bio))

    logger.info(
        f"衰减计算结果：密码衰减因子={decay_factor_pswd:.4f}，衰减后pswd={decay_pswd:.4f}；"
        f"生物衰减因子={decay_factor_bio:.4f}，衰减后bio={decay_bio:.4f}"
    )
    
    
    # ------------------------------
    # 调用模型（使用衰减后的pswd和bio）
    # ------------------------------
    model_request = {
        "subject_type": "user",
        "common_device": common_device,
        "time": request.time,
        "location": location,
        "bio": decay_bio,  # 使用衰减后的bio
        "pswd": decay_pswd,  # 使用衰减后的pswd
        "access_network_score": access_network_score,
        "network_risk": network_risk
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                USER_TRUST_MODEL_URL,
                json=model_request,
                timeout=TIMEOUT
            )
            resp.raise_for_status()
            result = resp.json()
            
            # ------------------------------
            # 核心修改：读取trust_score_add_value并计算最终信任度
            # ------------------------------
            try:
                # 读取信任度加分值配置
                trust_add_data = get_configmap(TRUST_SCORE_ADD_CM)
                trust_score_add_value = float(trust_add_data.get("trust_score_add_value", 0.0))
                logger.info(f"从ConfigMap[{TRUST_SCORE_ADD_CM}]读取到trust_score_add_value：{trust_score_add_value}")
            except (ValueError, HTTPException) as e:
                # 读取/转换失败时使用默认值0.0
                trust_score_add_value = 0.0
                logger.warning(f"读取/解析trust_score_add_value失败，使用默认值0.0，错误：{e}")
            
            # 计算最终信任度（确保在0-1范围内）
            original_trust_score = result["trust_score"]
            final_trust_score = original_trust_score + trust_score_add_value
            final_trust_score = max(0.0, min(1.0, final_trust_score))  # 限制范围在0-1
            
            # 更新全局保存的信任度（使用最终值）
            global saved_trust_score
            saved_trust_score = final_trust_score
            
            logger.info(
                f"信任度评估成功：模型返回值={original_trust_score:.3f} + 加分值={trust_score_add_value:.3f} = 最终值={final_trust_score:.3f}，"
                f"已更新保存的信任度为：{saved_trust_score:.3f}"
            )
            
            return TrustScoreResponse(
                trust_score=final_trust_score,  # 返回加完分后的信任度
                status=result["status"],
                message=f"{result['message']} | 模型原始信任度：{original_trust_score:.3f} | 加分值：{trust_score_add_value:.3f} | 最终信任度：{final_trust_score:.3f}"
            )
        except httpx.RequestError as e:
            logger.error(f"信任度评估模型调用失败：{e}")
            raise HTTPException(status_code=503, detail="用户信任度评估模型不可用")

# ------------------------------
# 新增：mac/imsi白名单校验接口（核心新增，对应用户需求）
# ------------------------------
@app.post(
    "/auth/5g",  # 与用户示例curl的接口路径保持一致
    response_model=AuthResponse,
    summary="MAC/IMSI白名单授权校验"
)
async def mac_imsi_auth(request: MacImsiAuthRequest):
    """
    逻辑：校验MAC地址是否在MAC白名单ConfigMap中，且IMSI号码是否在IMSI白名单ConfigMap中
    仅当两者均存在时，返回授权通过；任一不存在或配置读取失败，返回授权拒绝
    """
    logger.info(f"开始处理MAC/IMSI授权请求：MAC={request.mac}，IMSI={request.imsi}")
    
    # 步骤1：统一MAC地址格式（转大写，避免大小写匹配问题）
    target_mac = request.mac.upper()
    target_imsi = request.imsi.strip()
    
    # 步骤2：读取MAC白名单和IMSI白名单
    try:
        mac_whitelist = get_whitelist_from_cm(MAC_WHITELIST_CM)
        imsi_whitelist = get_whitelist_from_cm(IMSI_WHITELIST_CM)
    except HTTPException as e:
        logger.error(f"读取白名单ConfigMap失败：{e.detail}")
        return AuthResponse(
            result="deny",
            message=f"授权失败：配置读取异常（{e.detail}）"
        )
    
    # 步骤3：执行匹配判断
    mac_is_valid = target_mac in mac_whitelist
    imsi_is_valid = target_imsi in imsi_whitelist
    
    # 步骤4：构建返回结果
    if mac_is_valid and imsi_is_valid:
        logger.info(f"授权通过：MAC={target_mac}、IMSI={target_imsi}均在白名单中")
        return AuthResponse(
            result="allow",
            message=f"授权通过：MAC={target_mac}、IMSI={target_imsi}均为合法资源"
        )
    else:
        error_details = []
        if not mac_is_valid:
            error_details.append(f"MAC={target_mac}不在白名单中")
        if not imsi_is_valid:
            error_details.append(f"IMSI={target_imsi}不在白名单中")
        error_msg = "授权拒绝：" + "；".join(error_details)
        logger.warning(error_msg)
        return AuthResponse(
            result="deny",
            message=error_msg
        )

# 健康检查接口（K8s探针使用）
@app.get("/health", summary="健康检查")
async def health_check():
    return {
        "status": "healthy",
        "current_trust_score": saved_trust_score,
        "last_bio_login_time": last_bio_login_time,
        "last_pswd_login_time": last_pswd_login_time,
        "pswdold": pswdold,
        "bioold": bioold
    }