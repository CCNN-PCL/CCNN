# Cybertwin-Agent 微服务

## 概述

Cybertwin-Agent 服务是分诊医生微服务，作为API网关接收所有前端请求，负责意图识别、智能路由、调用专科医生微服务进行诊断、结果聚合等功能。

## 服务信息

- **服务名称**: cybertwin-agent
- **端口**: 8001
- **开发团队**: Team A
- **仓库**: cybertwin-agent-service

## 核心职责

根据《微服务拆分设计方案.md》第4.1节：

- 作为API网关，接收所有前端请求
- 用户认证和授权管理
- 意图识别和智能路由
- 调用专科医生微服务进行诊断
- 结果聚合和综合报告生成
- 医疗数据管理（影像、病历）
- 用户管理
- 聊天历史管理

## 服务架构

### API层 (backend/api/*)
- `auth.py` - 认证API
- `chat.py` - 聊天API
- `medical.py` - 医疗数据API
- `user.py` - 用户管理API
- `oidc_rp.py` - OIDC认证

### 服务层 (backend/services/*)
- `auth_service.py` - 认证服务
- `user_service.py` - 用户服务
- `medical_service.py` - 医疗数据服务
- `chat_service.py` - 聊天服务（需修改为调用远程服务）

### 核心逻辑层 (shared/agents/coordinator/*)
- `cybertwin_agent_refactored.py` - 协调器（需修改为使用HTTP客户端）
- `location_router.py` - 路由引擎
- `intent_recognition.py` - 意图识别

### 服务间通信
- `shared/clients/specialist_service_client.py` - HTTP客户端

## 环境变量配置

```bash
# 服务配置
SERVICE_PORT=8001
SERVICE_NAME=cybertwin-agent

# 专科医生服务地址
INTERNAL_MEDICINE_BEIJING_URL=http://internal-medicine-beijing:8002
INTERNAL_MEDICINE_SHANGHAI_URL=http://internal-medicine-shanghai:8003
SURGICAL_BEIJING_URL=http://surgical-beijing:8004
SURGICAL_SHANGHAI_URL=http://surgical-shanghai:8005

# API Keys（用于调用专科医生服务）
INTERNAL_MEDICINE_BEIJING_API_KEY=<api_key>
INTERNAL_MEDICINE_SHANGHAI_API_KEY=<api_key>
SURGICAL_BEIJING_API_KEY=<api_key>
SURGICAL_SHANGHAI_API_KEY=<api_key>

# OIDC认证配置
OIDC_ISSUER=http://192.168.193.12:31111
OIDC_CLIENT_ID=agent_doctor1
OIDC_CLIENT_SECRET=agent_doctor1-secret
OIDC_REDIRECT_URI=http://172.25.22.129:8001/oidc/callback
OIDC_SCOPE=openid profile email
OIDC_POST_LOGOUT_REDIRECT_URI=http://172.25.21.129:8089
MEDICAL_FRONTEND_URL=http://172.25.21.129:8089
OIDC_SESSION_SECRET=oidc-rp-secret-key-32-bytes
```

**注意**: 
- `OIDC_CLIENT_SECRET` 和 `OIDC_SESSION_SECRET` 属于敏感信息，在 Kubernetes 部署时应放在 Secrets 中
- 详细配置说明请参考 `microservices/完整环境变量配置指南.md`

## 部署方式

### 使用Docker

```bash
docker build -t cybertwin-agent-service .
docker run -p 8001:8001 \
  -e SERVICE_PORT=8001 \
  -e INTERNAL_MEDICINE_BEIJING_URL=http://internal-medicine-beijing:8002 \
  -e INTERNAL_MEDICINE_SHANGHAI_URL=http://internal-medicine-shanghai:8003 \
  -e SURGICAL_BEIJING_URL=http://surgical-beijing:8004 \
  -e SURGICAL_SHANGHAI_URL=http://surgical-shanghai:8005 \
  cybertwin-agent-service
```

### 直接运行

```bash
cd cybertwin-agent-service
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

## 待完成工作

### ⚠️ 重要：需要修改的文件

1. **chat_service.py**
   - 移除本地专科医生智能体调用
   - 改为使用 `SpecialistServiceClient` 进行HTTP调用
   - 更新诊断流程，调用远程服务

2. **cybertwin_agent_refactored.py**
   - 移除 `_init_specialists()` 方法中的本地智能体实例化
   - 改为使用 `SpecialistServiceClient` 进行HTTP调用
   - 更新 `_basic_diagnosis_flow()` 方法

详细修改说明请参考 `MIGRATION_NOTES.md`

## 接口文档

详见 [微服务接口契约文档](../../docs/api/微服务接口契约文档.md)

## 健康检查

```bash
curl http://localhost:8001/health
```

## 服务状态

```bash
curl http://localhost:8001/api/v1/status
```
