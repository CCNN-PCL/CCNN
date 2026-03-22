# 版本信息管理

本文档介绍 User-agent 项目的版本信息管理系统。

## 概述

项目集成了完整的版本信息管理功能，包括：
- 自动版本信息生成和注入
- Git 信息集成
- 构建信息跟踪
- API 端点提供版本查询
- Makefile 命令管理版本

## 文件结构

```
.
├── backend/version.py          # 版本信息管理模块
├── VERSION.json               # 版本信息存储文件
├── scripts/build.sh           # 构建脚本（自动注入版本信息）
├── scripts/test_version.py    # 版本信息测试脚本
└── docs/version-management.md # 本文档
```

## 版本信息模块

### 主要功能

`backend/version.py` 模块提供以下功能：

1. **版本信息管理**：管理版本号、构建标识、构建日期等
2. **Git 信息集成**：自动获取 Git 提交、分支、标签信息
3. **版权信息**：从 Git 配置获取版权所有者信息
4. **环境信息**：收集 Python 和系统环境信息
5. **序列化输出**：支持 JSON、字符串等多种格式输出

### 使用方法

```python
# 导入版本信息模块
from backend.version import get_version_info, get_version_string

# 获取版本信息实例
version_info = get_version_info()

# 获取版本号
version = version_info.get_version()  # "1.0.0"

# 获取构建标识
build = version_info.get_build()  # "dev"

# 获取Git信息
git_info = version_info.get_git_info()
# {'commit': 'a1b2c3d', 'branch': 'main', 'tag': 'v1.0.0', 'dirty': False}

# 获取版本字符串
simple_version = get_version_string("simple")  # "v1.0.0-dev"
compact_version = get_version_string("compact")  # "v1.0.0-dev+a1b2c3d"

# 保存版本信息到文件
version_info.save_to_file("VERSION.json")
```

### 命令行接口

```bash
# 显示简单版本信息
python backend/version.py --format=simple

# 显示详细版本信息（JSON格式）
python backend/version.py --format=json

# 更新版本号
python backend/version.py --update-version=2.0.0

# 更新构建标识
python backend/version.py --update-build=prod

# 保存版本信息到文件
python backend/version.py --save
```

## Makefile 版本命令

### 基本命令

```bash
# 显示版本信息
make version

# 显示详细版本信息（JSON格式）
make version-show

# 初始化版本信息
make version-init
```

### 版本管理命令

```bash
# 更新版本号（需要指定版本号）
make version-update VERSION=2.0.0

# 自动递增版本号（major/minor/patch）
make version-bump BUMP_TYPE=patch    # 递增修订号，如 1.0.0 -> 1.0.1
make version-bump BUMP_TYPE=minor    # 递增次版本号，如 1.0.0 -> 1.1.0
make version-bump BUMP_TYPE=major    # 递增主版本号，如 1.0.0 -> 2.0.0

# 更新构建标识
make version-build BUILD=prod
```

### 集成命令

```bash
# 构建Docker镜像（自动包含版本信息）
make build

# 部署应用（包含版本信息）
make deploy
```

## API 端点

项目提供了以下版本信息 API 端点：

### 1. 根路径 `/`
```json
{
  "message": "欢迎使用 UserAgent 私人代理 API",
  "version": "v1.0.0-dev+a1b2c3d",
  "docs": "/api/docs",
  "status": "/api/v1/status",
  "version_info": "/api/v1/version"
}
```

### 2. 简单版本信息 `/api/v1/version/simple`
```json
{
  "version": "v1.0.0-dev",
  "full_version": "v1.0.0-dev+a1b2c3d"
}
```

### 3. 详细版本信息 `/api/v1/version`
```json
{
  "version": "1.0.0",
  "build": "dev",
  "build_date": "2024-02-12T16:39:00",
  "git": {
    "commit": "a1b2c3d",
    "branch": "main",
    "tag": "",
    "dirty": false
  },
  "copyright": {
    "owner": "Your Name",
    "email": "your.email@example.com",
    "year": 2024
  },
  "metadata": {
    "project_name": "User-agent",
    "description": "UserAgent辅助系统后端API",
    "license": "Proprietary"
  },
  "python": {
    "version": "3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0]",
    "implementation": "cpython"
  },
  "system": {
    "platform": "linux",
    "machine": "x86_64"
  }
}
```

### 4. 系统状态 `/api/v1/status`
```json
{
  "api_version": "1.0.0-dev",
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
```

## 构建脚本

`scripts/build.sh` 提供了智能的构建功能：

### 基本用法
```bash
# 构建Docker镜像（自动注入版本信息）
./scripts/build.sh build

# 显示版本信息
./scripts/build.sh version

# 清理构建缓存
./scripts/build.sh clean

# 显示帮助信息
./scripts/build.sh help
```

### 推送镜像
```bash
# 推送镜像到私有仓库
./scripts/build.sh push registry.example.com
```

### 构建过程

构建脚本会自动：
1. 读取 `VERSION.json` 文件获取版本信息
2. 获取当前 Git 提交和分支信息
3. 生成构建时间戳
4. 将这些信息作为构建参数传递给 Docker
5. 创建包含构建信息的镜像

## Docker 构建信息

Docker 镜像构建时会注入以下构建信息：

### 构建参数
```dockerfile
ARG BUILD_VERSION=dev
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_BRANCH
```

### 构建信息文件
构建过程中会创建 `/app/BUILD_INFO.json` 文件：
```json
{
  "build_version": "1.0.0-dev",
  "build_date": "2024-02-12T16:39:00+08:00",
  "git_commit": "a1b2c3d",
  "git_branch": "main"
}
```

### 镜像标签
镜像使用版本-构建标识作为标签：
```
user-agent:1.0.0-dev
user-agent:latest
```

## 版本管理流程

### 开发阶段
1. 使用 `dev` 作为构建标识
2. 版本信息自动从 Git 获取
3. 每次构建都会更新构建日期

### 测试阶段
1. 使用 `test` 或 `beta` 作为构建标识
2. 可以递增修订号：`make version-bump BUMP_TYPE=patch`
3. 构建信息包含测试环境标识

### 生产发布
1. 更新构建标识为 `prod`：`make version-build BUILD=prod`
2. 递增版本号（如果需要）：`make version-bump BUMP_TYPE=minor`
3. 构建生产镜像：`make build`
4. 部署：`make deploy`

### 版本发布流程
```bash
# 1. 确保代码已提交
git add .
git commit -m "准备发布 v1.1.0"

# 2. 创建标签
git tag -a v1.1.0 -m "版本 1.1.0"

# 3. 更新构建标识为生产环境
make version-build BUILD=prod

# 4. 构建生产镜像
make build

# 5. 推送镜像到仓库（如果需要）
./scripts/build.sh push registry.example.com

# 6. 部署
make deploy
```

## 测试

### 运行版本信息测试
```bash
# 运行完整的版本信息测试
python scripts/test_version.py

# 测试特定功能
python scripts/test_version.py --test module    # 测试版本模块
python scripts/test_version.py --test makefile  # 测试Makefile命令
python scripts/test_version.py --test api       # 测试API端点
```

### 测试内容
1. **版本信息模块测试**：验证版本信息生成和序列化
2. **Makefile命令测试**：验证版本管理命令
3. **构建脚本测试**：验证构建脚本功能
4. **API端点测试**：验证版本信息API

## 故障排除

### 常见问题

#### 1. 版本信息不显示 Git 信息
**原因**：项目目录不是 Git 仓库或 Git 未安装
**解决**：
```bash
# 初始化Git仓库
git init
git add .
git commit -m "初始提交"

# 或确保Git已安装
which git
```

#### 2. Makefile 版本命令失败
**原因**：虚拟环境未激活或依赖未安装
**解决**：
```bash
# 创建虚拟环境并安装依赖
make venv
make install

# 或手动激活虚拟环境
source .venv/bin/activate
```

#### 3. API 端点返回 404
**原因**：服务器未运行或路由配置错误
**解决**：
```bash
# 启动开发服务器
make start

# 测试API端点
curl http://localhost:5050/api/v1/version
```

#### 4. 构建脚本权限问题
**原因**：脚本没有执行权限
**解决**：
```bash
chmod +x scripts/build.sh
```

### 调试技巧

1. **查看版本文件**：
   ```bash
   cat VERSION.json | python -m json.tool
   ```

2. **手动测试版本模块**：
   ```bash
   python -c "from backend.version import get_version_info; import json; print(json.dumps(get_version_info().to_dict(), indent=2))"
   ```

3. **检查构建信息**：
   ```bash
   # 运行容器并检查构建信息
   docker run --rm user-agent:latest cat /app/BUILD_INFO.json
   ```

## 最佳实践

### 1. 版本命名规范
- 使用语义化版本控制：`主版本.次版本.修订版本`
- 构建标识：`dev`（开发）、`test`（测试）、`prod`（生产）
- Git 标签：`v1.0.0`、`v1.1.0-rc1`

### 2. 提交信息规范
- 功能开发：`feat: 添加用户认证功能`
- 错误修复：`fix: 修复登录页面样式问题`
- 版本发布：`chore: 发布 v1.1.0`

### 3. 构建流程
- 开发环境：每次提交后自动构建 `dev` 版本
- 测试环境：合并到测试分支后构建 `test` 版本
- 生产环境：发布标签后构建 `prod` 版本

### 4. 监控和日志
- 在日志中包含版本信息
- 监控 API 的版本端点
- 记录构建和部署历史

## 扩展功能

### 自定义版本信息
可以修改 `backend/version.py` 来添加自定义信息：

```python
class VersionInfo:
    def __init__(self):
        # ... 现有代码 ...
        
        # 添加自定义信息
        version_data["custom"] = {
            "deployment_environment": os.getenv("DEPLOYMENT_ENV", "development"),
            "feature_flags": self._get_feature_flags(),
            "dependencies": self._get_dependency_versions()
        }
```

### 集成 CI/CD
在 CI/CD 流水线中使用版本信息：

```yaml
# GitHub Actions 示例
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0  # 获取所有Git历史
      
      - name: Set up Python
        uses: actions/setup-python@v2
      
      - name: Initialize version
        run: make version-init
      
      - name: Build Docker image
        run: ./scripts/build.sh build
      
      - name: Push to registry
        run: ./scripts/build.sh push ${{ secrets.DOCKER_REGISTRY }}
```

### 健康检查端点
可以添加健康检查端点，包含版本信息：

```python
@app.get("/health")
async def health_check():
    """健康检查端点"""
    version_info = get_version_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": version_info.get_version(),
        "build": version_info.get_build(),
        "services": {
            "database": check_database(),
            "redis": check_redis(),
            "external_api": check_external_api()
        }
    }
```

## 总结

版本信息管理系统提供了完整的版本跟踪、构建信息注入和 API 查询功能。通过集成到开发、构建和部署流程中，可以确保：

1. **可追溯性**：每个构建都有完整的版本和构建信息
2. **一致性**：开发、测试和生产环境使用相同的版本管理
3. **自动化**：版本信息自动生成和注入，减少手动错误
4. **可查询性**：通过 API 端点随时查询版本信息
5. **标准化**：遵循语义化版本控制和最佳实践

通过这套系统，团队可以更好地管理项目版本，跟踪构建历史，快速定位问题，提高开发和运维效率。
