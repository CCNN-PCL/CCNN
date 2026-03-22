# Makefile 和版本管理指南

## 概述

本项目现已提供完整的 **Makefile** 和 **版本管理系统**，支持编译时动态注入版本信息和通过 API 接口返回版本详情。

---

## 🎯 主要功能

### 1. **完善的 Makefile 命令**

提供了多个实用的命令用于开发、测试、构建和部署：

```bash
make help              # 显示所有命令帮助
make version           # 显示版本信息
make install           # 安装依赖（创建虚拟环境）
make run               # 运行应用（开发模式）
make dev               # 开发模式（带热重载）
make test              # 运行单元测试
make lint              # 代码静态检查
make format            # 代码格式化
make clean             # 清理临时文件
make build             # 构建Docker镜像
make push              # 推送镜像到远程仓库
make inject-version    # 注入版本信息（编译时）
```

### 2. **编译时版本注入**

支持通过 Makefile 变量动态注入版本信息到 `src/version.py`:

```bash
# 使用默认版本 (0.1.0)
make inject-version

# 使用自定义版本号
make inject-version BUILD_VERSION=1.2.3 VERSION_MAJOR=1 VERSION_MINOR=2 VERSION_PATCH=3

# 配合构建使用
make build BUILD_VERSION=1.2.3
```

版本信息包括：
- `__version__` - 完整版本号（如 "1.2.3"）
- `__major__` - 主版本号
- `__minor__` - 次版本号
- `__patch__` - 补丁版本号
- `__git_commit__` - Git提交哈希（短格式）
- `__build_time__` - 构建时间戳

### 3. **API 版本接口**

通过 `/api/v1/version` 端点返回详细的版本和应用信息：

#### 请求
```bash
GET /api/v1/version
```

#### 响应示例
```json
{
  "status": "success",
  "data": {
    "application": "智慧医疗外科医生Agent",
    "service_name": "surgical",
    "specialization": "外科",
    "version": "0.1.0",
    "major": 0,
    "minor": 1,
    "patch": 0,
    "build_time": "2026-02-27 09:16:30",
    "git_commit": "392019e"
  }
}
```

---

## 📋 详细命令说明

### 基础命令

#### `make help`
显示所有可用的 Makefile 命令及使用说明。

```bash
$ make help
==================================
surgical-agent - Makefile 命令
==================================

📋 基础命令:
  make help              显示此帮助信息
  make version           显示版本信息
  ...
```

#### `make version`
显示当前项目版本信息。

```bash
$ make version
==================================
surgical-agent 版本信息
==================================
版本号: 0.1.0
主版本: 0
子版本: 1
修订版: 0
Git commit: 392019e
构建时间: 2026-02-27 09:16:30
```

### 依赖管理

#### `make install`
创建虚拟环境并安装 `requirements.txt` 中的所有依赖。

```bash
$ make install
📦 安装依赖...
虚拟环境已创建
✅ 依赖安装完成
```

#### `make poetry-install`
使用 Poetry 安装依赖（需先安装 Poetry）。

```bash
$ make poetry-install
📦 使用Poetry安装依赖...
✅ Poetry依赖安装完成
```

### 开发和测试

#### `make run`
启动应用（开发模式，带自动重载）。

```bash
$ make run
▶️  启动应用 (端口: 8004)...
INFO:     Uvicorn running on http://0.0.0.0:8004
```

#### `make dev`
开发模式启动（带热重载和调试日志）。

```bash
$ make dev
▶️  开发模式启动应用 (带热重载, 端口: 8004)...
```

#### `make test`
运行单元测试并生成覆盖率报告。

```bash
$ make test
🧪 运行测试...
✅ 测试完成
```

### 代码质量

#### `make lint`
使用 pylint 进行代码静态检查。

```bash
$ make lint
🔍 运行代码检查...
✅ 代码检查完成
```

#### `make format`
使用 black 和 isort 格式化代码。

```bash
$ make format
🎨 格式化代码...
✅ 代码格式化完成
```

### Docker 构建和部署

#### `make build` 或 `make docker-build`
构建 Docker 镜像（自动注入版本信息）。

```bash
$ make build
🐳 构建 Docker 镜像...
   镜像标签: surgical-agent:0.1.0
   平台: linux/amd64
✅ Docker 镜像构建成功
```

#### `make push` 或 `make docker-push`
推送镜像到远程仓库。

```bash
$ make push
📤 推送镜像到远程仓库...
   目标: 192.168.64.60:31304/medical-app/surgical-agent:0.1.0
✅ 镜像推送成功
```

### 清理

#### `make clean`
清理所有临时文件（缓存、编译产物、测试数据等）。

```bash
$ make clean
🧹 清理临时文件...
✅ 清理完成
```

---

## 🔧 版本管理工作流

### 场景 1：本地开发

```bash
# 1. 安装依赖
make install

# 2. 启动应用
make dev

# 3. 运行测试
make test

# 4. 提交前清理
make clean
```

### 场景 2：发布新版本

```bash
# 1. 确定新版本号（例如 1.0.0）
VERSION=1.0.0
MAJOR=1
MINOR=0
PATCH=0

# 2. 注入版本信息
make inject-version BUILD_VERSION=$VERSION VERSION_MAJOR=$MAJOR VERSION_MINOR=$MINOR VERSION_PATCH=$PATCH

# 3. 构建 Docker 镜像
make build BUILD_VERSION=$VERSION

# 4. 推送到仓库
make push BUILD_VERSION=$VERSION
```

### 场景 3：CI/CD 管道

```bash
# 在 CI 脚本中使用
make install
make lint
make test
make build BUILD_VERSION=$CI_COMMIT_TAG
make push BUILD_VERSION=$CI_COMMIT_TAG
```

---

## 📁 版本相关文件

### `src/version.py`
自动生成的版本信息文件（编译时注入）。此文件 **不应手动编辑**，由 Makefile 在编译时自动生成。

```python
# -*- coding: utf-8 -*-
"""版本管理模块 - 自动生成 (不要手动编辑)"""

__version__ = "0.1.0"
__major__ = 0
__minor__ = 1
__patch__ = 0
__git_commit__ = "392019e"
__build_time__ = "2026-02-27 09:16:30"

def get_version() -> str:
    """获取完整版本字符串"""
    return __version__

def get_version_info() -> dict:
    """获取详细的版本信息"""
    return {...}
```

### `scripts/inject_version.py`
版本注入脚本，由 Makefile 调用，负责生成 `src/version.py`。

### `Makefile`
增强的构建配置文件，包含所有开发和部署命令。

---

## 🌐 在应用中使用版本信息

### Python 代码

```python
from src.version import get_version, get_version_info
from src.config.settings import settings

# 获取简单版本号
version = get_version()  # "0.1.0"

# 获取完整版本信息
info = get_version_info()
# {
#     "version": "0.1.0",
#     "major": 0,
#     "minor": 1,
#     "patch": 0,
#     "build_time": "2026-02-27 09:16:30",
#     "git_commit": "392019e"
# }

# 从设置中获取
version = settings.VERSION  # "0.1.0"
```

### FastAPI 应用

```python
from fastapi import FastAPI
from src.version import get_version_info
from src.config.settings import settings

app = FastAPI(version=settings.VERSION)

@app.get("/api/v1/version")
async def get_version_endpoint():
    """获取应用版本信息"""
    version_info = get_version_info()
    return {
        "status": "success",
        "data": {
            "application": settings.PROJECT_NAME,
            "service_name": settings.SERVICE_NAME,
            **version_info,
        },
    }
```

---

## 💡 最佳实践

1. **版本号规范**：遵循 [Semantic Versioning](https://semver.org/zh-CN/)
   - MAJOR.MINOR.PATCH (例如 1.2.3)
   - MAJOR: 不兼容变更
   - MINOR: 新增功能，向后兼容
   - PATCH: 修复bug

2. **编译时注入**：总是在构建 Docker 镜像时注入版本信息
   ```bash
   make build BUILD_VERSION=1.2.3
   ```

3. **标签化发布**：在 Git 中使用版本标签
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

4. **自动化**：在 CI/CD 管道中自动注入版本信息
   ```bash
   make inject-version BUILD_VERSION=${GIT_TAG}
   ```

---

## 🐛 故障排除

### 问题：`make: command not found`
**解决方案**：安装 make 工具
```bash
# Ubuntu/Debian
sudo apt-get install make

# macOS
brew install make

# CentOS/RHEL
yum install make
```

### 问题：`python3: command not found`
**解决方案**：安装 Python 3
```bash
python --version  # 检查是否已安装
```

### 问题：虚拟环境未激活
**解决方案**：Makefile 会自动激活虚拟环境，但如需手动激活：
```bash
source .venv/bin/activate
```

---

## 📚 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Python Makefile 最佳实践](https://www.gnu.org/software/make/manual/)
- [Semantic Versioning](https://semver.org/)
- [Docker 官方文档](https://docs.docker.com/)

---

## 📝 更新历史

- **2026-02-27**: 新增 Makefile 和版本管理系统
  - 完善 Makefile 功能
  - 实现编译时版本注入
  - 添加版本 API 接口
  - 支持灵活的版本号管理
