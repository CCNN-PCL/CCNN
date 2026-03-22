# Cybertwin-Agent 分诊服务与专科智能体服务对接接口文档

## 文档概述

### 服务架构

1. **cybertwin-agent-service** (分诊服务) ###triage-agent-service   ##############后面调整适配
   - 端口: 8001
   - 职责: 分诊医生、意图识别、路由、API网关、结果聚合

2. **internal-medicine-service** (内科微服务)
   - 端口: 8002 (北京实例)
   - 端口: 8003 (上海实例)
   - 职责: 内科专科诊断

3. **surgical-service** (外科微服务)
   - 端口: 8004 (北京实例)
   - 端口: 8005 (上海实例)
   - 职责: 外科专科诊断

### 服务调用关系

```
用户请求
    │
    ▼
Cybertwin-Agent (8001) (分诊服务) ###triage-agent-service   ##############后面调整适配
    │
    ├──► Internal-Medicine-Beijing (8002)
    ├──► Internal-Medicine-Shanghai (8003)
    ├──► Surgical-Beijing (8004)
    └──► Surgical-Shanghai (8005)
```

---

## 第一部分：Cybertwin-Agent 调用专科智能体服务

### 1.1 诊断接口

#### 接口定义

**接口路径**: `POST /api/v1/diagnosis`

**接口版本**: `v1`

**服务端点**:
- 内科-北京: `http://internal-medicine-beijing:8002/api/v1/diagnosis`
- 内科-上海: `http://internal-medicine-shanghai:8003/api/v1/diagnosis`
- 外科-北京: `http://surgical-beijing:8004/api/v1/diagnosis`
- 外科-上海: `http://surgical-shanghai:8005/api/v1/diagnosis`

#### 请求规范

**请求方法**: `POST`

**请求头**:
```
Content-Type: application/json
Accept: application/json
X-API-Key: <service_api_key>
X-Request-ID: <unique_request_id>
X-User-ID: <user_id>
X-Service-Name: cybertwin-agent
X-Timestamp: <unix_timestamp>
X-API-Version: v1
```

**请求体结构**:
```json
{
  "user_input": "我最近总是感觉头晕，有时候还会心慌",
  "user_id": "user_12345",
  "intent": "内科咨询",
  "data_addresses": [
    {
      "data_type": "病史数据",
      "location": "beijing",
      "address": "db://hospital_beijing/medical_records/user_12345",
      "hospital": "北京协和医院"
    },
    {
      "data_type": "用药记录",
      "location": "beijing",
      "address": "db://hospital_beijing/medications/user_12345",
      "hospital": "北京协和医院"
    }
  ],
  "shared_context": {
    "user_id": "user_12345",
    "intent": "内科咨询",
    "user_input": "我最近总是感觉头晕，有时候还会心慌",
    "round_number": 1,
    "data_addresses_history": [],
    "diagnosis_results_history": []
  },
  "user_info": {
    "userid": "user_12345",
    "username": "张三",
    "id_token": "<jwt_token>"
  },
  "metadata": {
    "request_id": "req_20250105_001",
    "timestamp": "2025-01-05T10:30:00Z",
    "source": "cybertwin_agent"
  }
}
```

#### 响应规范

**成功响应（HTTP 200）**:
```json
{
  "status": "success",
  "agent": "internal_medicine_beijing",
  "location": "beijing",
  "specialization": "内科",
  "diagnosis": {
    "diagnosis": "根据您描述的症状，结合您的病史和用药记录，初步判断可能是高血压或心律失常。建议您进行血压监测和心电图检查。",
    "confidence": 0.85,
    "symptoms_analysis": "头晕和心慌是常见的心血管系统症状",
    "recommendations": [
      "监测血压，每日早晚各一次",
      "进行24小时动态心电图检查",
      "避免剧烈运动和情绪激动",
      "如症状持续，建议尽快就医"
    ],
    "surgical_indication": null
  },
  "needs_more_data": false,
  "data_requirements": [],
  "data_sources": [
    "北京协和医院 - 病史数据",
    "北京协和医院 - 用药记录"
  ],
  "available_data_types": [
    "病史数据",
    "用药记录"
  ],
  "data_usage_summary": "使用了患者的既往病史和当前用药记录进行诊断分析",
  "confidence": 0.85,
  "processing_time": 2.5,
  "timestamp": "2025-01-05T10:30:02Z"
}
```


**错误响应（HTTP 4xx/5xx）**:
```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "error_message": "错误描述",
  "error_details": {
    "field": "additional_info"
  },
  "request_id": "req_20250105_001",
  "timestamp": "2025-01-05T10:30:00Z"
}
```

**错误码规范**:

| HTTP状态码 | 错误码 | 说明 | 处理建议 |
|-----------|--------|------|----------|
| 400 | VALIDATION_INVALID_PARAM | 请求参数无效 | 检查请求参数格式和类型 |
| 400 | VALIDATION_MISSING_PARAM | 缺少必需参数 | 补充必需参数 |
| 401 | AUTH_INVALID_API_KEY | API Key无效 | 检查API Key配置 |
| 401 | AUTH_MISSING_API_KEY | 缺少API Key | 添加API Key到请求头 |
| 500 | DIAGNOSIS_ERROR | 诊断处理失败 | 记录错误，可重试 |
| 503 | DIAGNOSIS_MODEL_ERROR | 模型服务错误 | 记录错误，稍后重试 |
| 504 | DIAGNOSIS_TIMEOUT | 诊断超时 | 增加超时时间或重试 |
| 429 | RATE_LIMIT_EXCEEDED | 请求频率超限 | 降低请求频率 |

---

### 1.2 健康检查接口

#### 接口定义

**接口路径**: `GET /health`

**接口版本**: `v1`

**服务端点**:
- 内科-北京: `http://internal-medicine-beijing:8002/health`
- 内科-上海: `http://internal-medicine-shanghai:8003/health`
- 外科-北京: `http://surgical-beijing:8004/health`
- 外科-上海: `http://surgical-shanghai:8005/health`

#### 请求规范

**请求方法**: `GET`

**请求头**: 无特殊要求

#### 响应规范

**成功响应（HTTP 200）**:
```json
{
  "status": "healthy",
  "service": "internal-medicine-beijing",
  "version": "1.0.0",
  "uptime": 3600,
  "model_status": {
    "model_name": "HuatuoGPT-2",
    "status": "available",
    "last_check": "2025-01-05T10:30:00Z"
  },
  "timestamp": "2025-01-05T10:30:00Z"
}
```

**不健康响应（HTTP 503）**:
```json
{
  "status": "unhealthy",
  "service": "internal-medicine-beijing",
  "version": "1.0.0",
  "error": "Model service unavailable",
  "timestamp": "2025-01-05T10:30:00Z"
}
```

---

### 1.3 服务状态接口

#### 接口定义

**接口路径**: `GET /api/v1/status`

**接口版本**: `v1`

**服务端点**:
- 内科-北京: `http://internal-medicine-beijing:8002/api/v1/status`
- 内科-上海: `http://internal-medicine-shanghai:8003/api/v1/status`
- 外科-北京: `http://surgical-beijing:8004/api/v1/status`
- 外科-上海: `http://surgical-shanghai:8005/api/v1/status`

#### 请求规范

**请求方法**: `GET`

**请求头**:
```
X-API-Key: <service_api_key>
```

#### 响应规范

**成功响应（HTTP 200）**:
```json
{
  "service": "internal-medicine-beijing",
  "status": "running",
  "location": "beijing",
  "specialization": "内科",
  "model": "HuatuoGPT-2",
  "version": "1.0.0",
  "capabilities": [
    "内科症状分析",
    "病史关联分析",
    "内科诊断建议",
    "治疗方案推荐"
  ],
  "statistics": {
    "total_requests": 1250,
    "successful_requests": 1200,
    "failed_requests": 50,
    "average_response_time": 2.3
  }
}
```



## 第三部分：接口调用要求

### 3.1 Cybertwin-Agent 调用要求

#### 3.1.1 请求构建

- ✅ 必须包含所有必需的请求头
- ✅ 必须生成唯一的 `X-Request-ID`
- ✅ 必须包含正确的 `X-API-Key`
- ✅ 请求体必须符合JSON Schema

#### 3.1.2 超时和重试

- **诊断接口超时**: 30秒
- **健康检查超时**: 5秒
- **服务状态超时**: 2秒
- **重试策略**: 最多3次，指数退避（1s, 2s, 4s）
- **仅对5xx错误和超时进行重试**

#### 3.1.3 并发调用

- ✅ 并行调用所有专科医生服务
- ✅ 使用 `asyncio.gather` 或类似机制
- ✅ 即使部分服务失败，也要聚合成功的结果

#### 3.1.4 错误处理

- ✅ 解析错误响应，提取 `error_code` 和 `error_message`
- ✅ 记录错误日志（包含request_id）
- ✅ 实现熔断器模式（连续失败5次后熔断）
- ✅ 实现降级策略（服务不可用时的处理）

### 3.2 专科服务实现要求

#### 3.2.1 请求验证

- ✅ 验证 `X-API-Key` 请求头
- ✅ 验证请求体格式（使用Pydantic模型验证）
- ✅ 验证必需参数是否存在
- ✅ 验证参数类型和格式

#### 3.2.2 响应格式

- ✅ 必须严格按照响应规范返回数据
- ✅ 所有字段必须符合接口契约定义
- ✅ 错误响应必须包含 `error_code` 和 `error_message`

#### 3.2.3 性能要求

- **诊断接口响应时间**: P95 < 30秒
- **健康检查接口响应时间**: < 1秒
- **服务状态接口响应时间**: < 2秒

#### 3.2.4 错误处理

- ✅ 所有错误必须返回标准错误响应格式
- ✅ 记录详细错误日志（包含request_id）
- ✅ 区分客户端错误（4xx）和服务器错误（5xx）

---

## 第四部分：服务配置

### 4.1 Cybertwin-Agent 服务配置

**环境变量**:
```bash
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

# 超时配置
DIAGNOSIS_TIMEOUT=30
HEALTH_CHECK_TIMEOUT=5

# 服务配置
SERVICE_PORT=8001
SERVICE_NAME=triage-agent-service   ##############后面调整适配
```

### 4.2 内科微服务配置

**北京实例配置** (端口 8002):
```bash
SERVICE_NAME=internal-medicine-beijing
SERVICE_PORT=8002
LOCATION=beijing
SPECIALIZATION=内科
MODEL_NAME=HuatuoGPT-2
API_KEY=<api_key>
```

**上海实例配置** (端口 8003):
```bash
SERVICE_NAME=internal-medicine-shanghai
SERVICE_PORT=8003
LOCATION=shanghai
SPECIALIZATION=内科
MODEL_NAME=HuatuoGPT
API_KEY=<api_key>
```

### 4.3 外科微服务配置

**北京实例配置** (端口 8004):
```bash
SERVICE_NAME=surgical-beijing
SERVICE_PORT=8004
LOCATION=beijing
SPECIALIZATION=外科
MODEL_NAME=HuatuoGPT-2
API_KEY=<api_key>
```

**上海实例配置** (端口 8005):
```bash
SERVICE_NAME=surgical-shanghai
SERVICE_PORT=8005
LOCATION=shanghai
SPECIALIZATION=外科
MODEL_NAME=HuatuoGPT
API_KEY=<api_key>
```


---

## 第八部分：专科智能体服务提供给Cybertwin-Agent的接口规范

### 8.1 接口概述

专科智能体服务（内科和外科服务）提供给Cybertwin-Agent分诊服务的接口，用于接收诊断请求并返回诊断结果。

### 8.2 接口列表

#### 8.2.1 诊断接口

**接口路径**: `POST /api/v1/diagnosis`

**提供方**: 专科智能体服务（内科/外科，北京/上海）

**调用方**: Cybertwin-Agent 分诊服务


#### 8.2.2 健康检查接口

**接口路径**: `GET /health`

**提供方**: 专科智能体服务

**调用方**: Cybertwin-Agent 分诊服务（用于服务健康监控）



#### 8.2.3 服务状态接口

**接口路径**: `GET /api/v1/status`

**提供方**: 专科智能体服务

**调用方**: Cybertwin-Agent 分诊服务（用于获取服务状态和统计信息）



### 8.3 接口调用示例

#### 示例1：Cybertwin-Agent 调用内科服务（北京）

```python
from shared.clients.specialist_service_client import SpecialistServiceClient

# 初始化客户端
client = SpecialistServiceClient(
    base_url="http://internal-medicine-beijing:8002",
    api_key="internal_medicine_beijing_api_key",
    timeout=30.0
)

# 调用诊断接口
result = await client.diagnose(
    user_input="我最近总是感觉头晕，有时候还会心慌",
    user_id="user_12345",
    intent="内科咨询",
    data_addresses=[
        {
            "data_type": "病史数据",
            "location": "beijing",
            "address": "db://hospital_beijing/medical_records/user_12345",
            "hospital": "北京协和医院"
        },
        {
            "data_type": "用药记录",
            "location": "beijing",
            "address": "db://hospital_beijing/medications/user_12345",
            "hospital": "北京协和医院"
        }
    ],
    user_info={
        "userid": "user_12345",
        "username": "张三",
        "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    shared_context={
        "user_id": "user_12345",
        "intent": "内科咨询",
        "user_input": "我最近总是感觉头晕，有时候还会心慌",
        "round_number": 1,
        "data_addresses_history": [],
        "diagnosis_results_history": []
    }
)

# 处理响应
if result["status"] == "success":
    print(f"诊断结果: {result['diagnosis']['diagnosis']}")
    print(f"置信度: {result['confidence']}")
    
    # 检查是否需要更多数据
    if result.get("needs_more_data"):
        print(f"需要更多数据: {result['data_requirements']}")
else:
    print(f"诊断失败: {result.get('error_message')}")
```

#### 示例2：并行调用所有专科服务

```python
from shared.clients.specialist_service_client import call_all_specialists

# 并行调用所有专科服务
results = await call_all_specialists(
    user_input="我最近总是感觉头晕，有时候还会心慌",
    user_id="user_12345",
    intent="内科咨询",
    data_addresses=[
        {
            "data_type": "病史数据",
            "location": "beijing",
            "address": "db://hospital_beijing/medical_records/user_12345",
            "hospital": "北京协和医院"
        }
    ],
    user_info={
        "userid": "user_12345",
        "username": "张三"
    },
    service_configs=[
        {"base_url": "http://internal-medicine-beijing:8002", "api_key": "key1"},
        {"base_url": "http://internal-medicine-shanghai:8003", "api_key": "key2"},
        {"base_url": "http://surgical-beijing:8004", "api_key": "key3"},
        {"base_url": "http://surgical-shanghai:8005", "api_key": "key4"}
    ]
)

# 处理所有结果
for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"服务 {i} 调用失败: {str(result)}")
    else:
        print(f"服务 {i} 诊断结果: {result.get('diagnosis', {}).get('diagnosis', 'N/A')}")
```

#### 示例3：健康检查

```python
from shared.clients.specialist_service_client import SpecialistServiceClient

client = SpecialistServiceClient(
    base_url="http://internal-medicine-beijing:8002",
    api_key="test_api_key"
)

# 健康检查
health_status = await client.health_check()
print(f"服务状态: {health_status['status']}")
print(f"模型状态: {health_status['model_status']['status']}")
```

#### 示例4：获取服务状态

```python
from shared.clients.specialist_service_client import SpecialistServiceClient

client = SpecialistServiceClient(
    base_url="http://internal-medicine-beijing:8002",
    api_key="test_api_key"
)

# 获取服务状态
status = await client.get_status()
print(f"服务: {status['service']}")
print(f"位置: {status['location']}")
print(f"专科: {status['specialization']}")
print(f"总请求数: {status['statistics']['total_requests']}")
```


## 第九部分：Cybertwin-Agent提供给专科智能体服务的接口规范

### 9.1 接口概述

**重要说明**：
- 在实际数据流中，专科智能体服务**不直接调用**这些接口
- 数据传递通过诊断接口的 `data_addresses` 参数完成
- 这些接口主要用于 Cybertwin-Agent 内部获取数据，然后传递给专科医

### 9.2 接口列表

#### 9.2.1 获取医疗记录接口

**接口路径**: `GET /api/v1/medical/records`

**接口版本**: `v1`

**提供方**: Cybertwin-Agent 分诊服务

**调用方**: Cybertwin-Agent 内部调用（专科服务间接使用）

**接口描述**: 获取用户的医疗记录（病史、用药记录、检查报告等）


**请求示例**:
```bash
GET /api/v1/medical/records?user_id=user_12345&record_type=病史&location=beijing
Authorization: Bearer <jwt_token>
```

**响应体**:
```json
{
  "status": "success",
  "records": [
    {
      "record_id": "rec_001",
      "user_id": "user_12345",
      "hospital_id": "hospital_beijing_001",
      "hospital_name": "北京协和医院",
      "record_type": "病史",
      "description": "高血压病史3年",
      "examination_date": "2024-12-01",
      "content": {
        "diagnosis": "高血压",
        "symptoms": ["头晕", "心慌"],
        "medications": ["降压药A", "降压药B"]
      },
      "upload_time": "2024-12-01T10:00:00Z"
    }
  ],
  "total_count": 1
}
```

**错误响应**:
```json
{
  "status": "error",
  "error_code": "DATA_NOT_FOUND",
  "error_message": "未找到指定的医疗记录",
  "timestamp": "2025-01-05T10:30:00Z"
}
```

**实现代码示例**:
```python
# microservices/cybertwin-agent-service/backend/api/medical.py

@router.get("/api/v1/medical/records")
async def get_medical_records(
    user_id: str,
    record_type: Optional[str] = None,
    hospital_id: Optional[str] = None,
    location: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(auth_service.get_current_user)
):
    """
    获取医疗记录接口
    
    提供给专科服务间接使用（通过data_addresses传递）
    """
    try:
        # 验证用户ID
        if current_user.get('user_id') != user_id:
            raise HTTPException(
                status_code=403,
                detail="无权访问该用户的数据"
            )
        
        # 获取医疗记录
        records = await medical_service.get_medical_records(
            user_id=user_id,
            record_type=record_type,
            hospital_id=hospital_id,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "status": "success",
            "records": records,
            "total_count": len(records)
        }
    except Exception as e:
        logger.error(f"获取医疗记录失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "SERVER_ERROR",
                "error_message": str(e)
            }
        )
```

#### 9.2.2 获取医疗影像接口  ######################暂时可忽略

**接口路径**: `GET /api/v1/medical/images`

**接口版本**: `v1`

**提供方**: Cybertwin-Agent 分诊服务

**调用方**: Cybertwin-Agent 内部调用（专科服务间接使用）

**接口描述**: 获取用户的医疗影像数据（CT、MRI、X光等）


**请求示例**:
```bash
GET /api/v1/medical/images?user_id=user_12345&image_type=CT&location=beijing
Authorization: Bearer <jwt_token>
```

**响应体**:
```json
{
  "status": "success",
  "images": [
    {
      "image_id": "img_001",
      "user_id": "user_12345",
      "hospital_id": "hospital_beijing_001",
      "hospital_name": "北京协和医院",
      "image_type": "CT",
      "image_category": "胸部CT",
      "examination_date": "2024-12-01",
      "description": "胸部CT平扫",
      "file_url": "http://storage.example.com/images/img_001.dcm",
      "file_size": 1048576,
      "upload_time": "2024-12-01T10:00:00Z"
    }
  ],
  "total_count": 1
}
```

#### 9.2.3 获取健康监测数据接口

**接口路径**: `GET /api/v1/medical/health-monitoring`

**接口版本**: `v1`

**提供方**: Cybertwin-Agent 分诊服务

**调用方**: Cybertwin-Agent 内部调用（专科服务间接使用）

**接口描述**: 获取用户的健康监测数据（血糖、血压、心率等）

**请求示例**:
```bash
GET /api/v1/medical/health-monitoring?user_id=user_12345&data_type=血糖
Authorization: Bearer <jwt_token>
```

**响应体**:
```json
{
  "status": "success",
  "data": [
    {
      "data_id": "hm_001",
      "user_id": "user_12345",
      "data_type": "血糖",
      "value": 7.2,
      "unit": "mmol/L",
      "measurement_time": "2025-01-05T08:00:00Z",
      "device": "血糖仪A",
      "notes": "空腹血糖"
    },
    {
      "data_id": "hm_002",
      "user_id": "user_12345",
      "data_type": "血压",
      "value": {
        "systolic": 140,
        "diastolic": 90
      },
      "unit": "mmHg",
      "measurement_time": "2025-01-05T08:30:00Z",
      "device": "血压计B"
    }
  ],
  "total_count": 2
}
```

#### 9.2.4 批量获取医疗数据接口

**接口路径**: `POST /api/v1/medical/batch-query`

**接口版本**: `v1`

**提供方**: Cybertwin-Agent 分诊服务

**调用方**: Cybertwin-Agent 内部调用（专科服务间接使用）

**接口描述**: 根据数据需求批量获取多种类型的医疗数据

**请求体**:
```json
{
  "user_id": "user_12345",
  "data_requirements": [
    {
      "data_type": "病史数据",
      "location": "beijing"
    },
    {
      "data_type": "健康监测数据",
      "data_subtype": "血糖"
    }
  ]
}
```

**响应体**:
```json
{
  "status": "success",
  "data_addresses": [
    {
      "data_type": "病史数据",
      "location": "beijing",
      "address": "db://hospital_beijing/medical_records/user_12345",
      "hospital": "北京协和医院",
      "data": {
        "records": [
          {
            "record_id": "rec_001",
            "record_type": "病史",
            "content": "..."
          }
        ]
      }
    },
    {
      "data_type": "健康监测数据",
      "location": "beijing",
      "address": "db://health_monitoring/user_12345/blood_glucose",
      "data": {
        "measurements": [
          {
            "value": 7.2,
            "unit": "mmol/L",
            "time": "2025-01-05T08:00:00Z"
          }
        ]
      }
    }
  ]
}
```


#### 数据流图

```
用户咨询
    │
    ▼
Cybertwin-Agent
    │
    ├──► 调用 /api/v1/medical/* 获取数据
    │    （内部调用）
    │
    ├──► 将数据地址传递给专科医生
    │    （通过诊断接口的 data_addresses 参数）
    │
    ▼
专科医生微服务
    │
    ├──► 使用数据地址获取数据进行诊断
    │
    └──► 返回诊断结果 + data_requirements（如果需要）
         │
         ▼
    Cybertwin-Agent
         │
         └──► 根据 data_requirements 获取补充数据
              （调用 /api/v1/medical/*）


```