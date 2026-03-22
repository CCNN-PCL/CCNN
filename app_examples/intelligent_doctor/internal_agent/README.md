# 智慧医生智能医疗辅助系统

## 📋 项目简介

智慧医生是一个基于大语言模型（LLM）的智能医疗辅助系统，采用多智能体架构，能够提供专业的医疗咨询、诊断建议和医疗数据管理服务。系统支持前后端分离架构

### 技术栈

- **后端框架**: FastAPI 0.110.0
- **前端框架**: Streamlit 1.32.0（可选）
- **数据库**: 
  - MySQL（生产环境）
  - SQLite（开发/测试环境）
- **认证**: OIDC、JWT
- **协议支持**: A2A、MCP
- **LLM支持**: 通义千问（Qwen）、华佗（Huatuo）等



## 📁 项目结构

```
private-doctor-demo-v4/
├── backend/                    # 后端API服务
│   ├── api/                   # API路由层
│   │   ├── auth.py           # 认证API
│   │   ├── chat.py           # 聊天API
│   │   ├── medical.py        # 医疗数据API
│   │   ├── user.py           # 用户管理API
│   │   ├── oidc_rp.py        # OIDC认证
│   │   └── third_party_reserve.py  # 第三方交互API
│   ├── services/             # 业务逻辑层
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── medical_service.py
│   │   └── user_service.py
│   ├── models/               # 数据模型
│   ├── utils/                # 工具类
│   └── main.py              # FastAPI应用入口
│
├── shared/                   # 共享模块（核心智能体系统）
│   ├── agents/              # 智能体系统
│   │   ├── coordinator/     # 协调器智能体
│   │   │   ├── cybertwin_agent_refactored.py  # 主协调器
│   │   │   ├── location_router.py            # 地域路由
│   │   │   ├── protocol_selector.py         # 协议选择器
│   │   │   └── two_round_diagnosis_coordinator.py  # 两轮诊断协调器
│   │   ├── specialists/     # 专科医生智能体
│   │   │   ├── internal_medicine_agent.py   # 内科智能体
│   │   │   └── surgical_agent.py            # 外科智能体
│   │   ├── image/           # 影像分析智能体
│   │   └── llm/             # LLM相关
│   ├── config/              # 配置管理
│   ├── protocols/           # 协议支持（A2A、MCP）
│   └── mysql_database_manager.py  # 数据库管理器
│
├── config/                   # 配置文件
│   ├── config_manager.py
│   ├── database_config.py
│   ├── hospital_config.py
│   └── third_party_config.py
│
├── data/                     # 数据目录
│   ├── auth.db              # SQLite认证数据库（开发用）
│   └── images/              # 医疗影像文件
│
├── scripts/                  # 脚本工具
│   ├── migration/           # 数据库迁移脚本
│   └── startup/             # 启动脚本
│       ├── start_backend.py # 后端启动脚本
│       └── start_all.py     # 全服务启动脚本
│
├── docs/                     # 文档目录
├── requirements.txt          # Python依赖
├── docker-compose.yml        # Docker编排配置
└── README.md                # 本文件
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ 或 SQLite 3（开发环境）
- pip 或 conda

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd private-doctor-demo-v4-qm-mysql-v2-test-frontend-ok-confirm-2025-12-5
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

创建 `.env` 文件（可选，系统会从环境变量读取配置）：

```env
# 数据库配置
DATABASE_TYPE=mysql  
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=private_doctor_db
MYSQL_USER=doctor_user
MYSQL_PASSWORD=doctor_password


# LLM模型配置
QWEN_API_KEY=your-qwen-api-key                        # 通义千问API密钥
QWEN_MODEL=qwen-turbo                                  # 通义千问模型名称
QWEN_BASE_URL=http://192.168.64.60:32568/v1           # 通义千问API地址
HUATUO_BASE_URL=http://192.168.64.60:32508/v1         # 华佗GPT API地址
HUATUO2_BASE_URL=http://172.22.11.169:30466/v1        # 华佗GPT-2 API地址

# OIDC配置（如需要）
OIDC_ISSUER=http://192.168.193.12:31111          # OIDC提供者地址
OIDC_CLIENT_ID=agent_doctor1                    # 客户端ID
OIDC_CLIENT_SECRET=agent_doctor1-secret         # 客户端密钥
OIDC_REDIRECT_URI=http://172.25.22.129:8000/oidc/callback  # 回调地址（需与OIDC提供者配置一致）
OIDC_SCOPE=openid profile email                 # 请求的权限范围
OIDC_POST_LOGOUT_REDIRECT_URI=http://172.25.21.129:8089  # 登出后重定向地址（前端地址）
MEDICAL_FRONTEND=http://172.25.21.129:8089     # 医疗前端应用地址
SESSION_SECRET=oidc-rp-secret-key-32-bytes      # 会话密钥（生产环境请使用强随机密钥）
```



#### 方式2: 直接运行

```bash
# 启动后端
python backend/main.py

# 或使用uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```


### 演示模式

系统支持演示模式，当检测到糖尿病相关内容时，会自动触发两轮诊断流程：



### LLM模型配置

系统支持多种LLM模型，配置位于 `shared/config/model_config.py`。

#### 支持的模型

- **通义千问（Qwen）**: 通用对话模型
- **华佗GPT（Huatuo）**: 医疗专用模型
- **华佗GPT-2（Huatuo2）**: 医疗专用模型（升级版）




### OIDC认证配置

系统支持OIDC（OpenID Connect）认证，配置位于 `backend/api/oidc_rp.py`。

#### 配置方式

**方式1: 直接修改代码（当前实现）**

在 `backend/api/oidc_rp.py` 文件中修改 `OIDC_CONFIG` 字典：

```python
OIDC_CONFIG = {
    'issuer': 'http://192.168.193.12:31111',                    # OIDC提供者地址
    'client_id': 'agent_doctor1',                               # 客户端ID
    'client_secret': 'agent_doctor1-secret',                    # 客户端密钥
    'redirect_uri': 'http://172.25.22.129:8000/oidc/callback',  # 回调地址
    'scope': 'openid profile email',                            # 权限范围
    'post_logout_redirect_uri': 'http://172.25.21.129:8089'     # 登出重定向地址
}
```

**方式2: 使用环境变量（后面需修改代码）**

在 `.env` 文件中配置（见上方环境变量配置部分），然后修改代码从环境变量读取：

```python
import os
OIDC_CONFIG = {
    'issuer': os.getenv('OIDC_ISSUER', 'http://192.168.193.12:31111'),
    'client_id': os.getenv('OIDC_CLIENT_ID', 'agent_doctor1'),
    'client_secret': os.getenv('OIDC_CLIENT_SECRET', 'agent_doctor1-secret'),
    'redirect_uri': os.getenv('OIDC_REDIRECT_URI', 'http://172.25.22.129:8000/oidc/callback'),
    'scope': os.getenv('OIDC_SCOPE', 'openid profile email'),
    'post_logout_redirect_uri': os.getenv('OIDC_POST_LOGOUT_REDIRECT_URI', 'http://172.25.21.129:8089')
}
```


## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

## 👥 作者

- **QSIR** - 初始开发和维护


**注意**: 本项目仅供学习和研究使用，不提供医疗诊断服务。任何医疗决策应咨询专业医生。

