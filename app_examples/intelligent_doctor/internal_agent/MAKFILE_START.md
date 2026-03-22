# Makfile 快速开始指南

## 概述

本项目现已配备完整的 Makfile，支持以下功能：

✅ **依赖管理** - 安装项目和开发依赖  
✅ **版本管理** - 自动注入版本信息到代码  
✅ **构建系统** - 编译和构建项目  
✅ **Docker** - 构建和运行 Docker 镜像  
✅ **测试** - 运行单元测试和覆盖率报告  
✅ **代码质量** - 代码检查和格式化  
✅ **API 接口** - 通过 REST API 获取版本信息  

## 文件清单

| 文件 | 说明 |
|------|------|
| [Makfile](Makfile) | 主构建配置文件 |
| [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) | 详细使用指南 |
| [BUILD_AND_DEPLOY_GUIDE.md](BUILD_AND_DEPLOY_GUIDE.md) | 构建和部署指南 |
| [Dockerfile](Dockerfile) | Docker 镜像配置（已更新） |
| [src/shared/version.py](src/shared/version.py) | 版本信息模块 |
| [src/api/version.py](src/api/version.py) | 版本信息 API 端点 |
| [scripts/inject_version.sh](scripts/inject_version.sh) | 版本注入脚本 |
| [scripts/test_version_api.py](scripts/test_version_api.py) | 版本 API 测试脚本 |
| [scripts/makefile_example.sh](scripts/makefile_example.sh) | Makfile 使用示例 |

## 快速开始（3 步）

### 1️⃣ 显示版本信息

```bash
make version
```

**输出示例：**
```
版本信息: 
  项目版本: 0.1.3 
  Git提交: 2b95935 
  构建时间: 2026-02-27T01:39:45Z
```

### 2️⃣ 注入版本信息

```bash
make version-inject
```

**输出示例：**
```
注入版本信息... 
✓ 版本信息已注入: src/shared/version.py 
  版本: 0.1.3 
  提交: 2b95935
```

### 3️⃣ 启动应用

```bash
# 开发模式（热重载）
make dev-run

# 或生产模式
make run
```

## 主要命令

### 依赖和构建

```bash
# 安装依赖
make install

# 安装开发依赖
make install-dev

# 构建项目
make build

# 注入版本信息
make version-inject
```

### Docker

```bash
# 构建 Docker 镜像
make docker-build

# 运行 Docker 容器
make docker-run
```

### 测试

```bash
# 运行测试
make test

# 运行测试并生成覆盖率报告
make test-cov
```

### 清理

```bash
# 清理缓存
make clean

# 深度清理（删除虚拟环境）
make clean-all
```

### 查看帮助

```bash
make help
```

## 版本信息 API

项目自动提供版本信息 API 端点：

### 获取版本信息

```bash
curl http://localhost:8000/api/v1/version
```

**响应:**
```json
{
    "version": "0.1.3",
    "version_string": "0.1.3+2b95935",
    "git_commit": "2b95935",
    "build_date": "2026-02-27T01:39:45Z"
}
```

### 其他端点

- `GET /api/v1/version/simple` - 简单版本号
- `GET /api/v1/version/string` - 版本字符串
- `GET /api/v1/version/detail` - 详细版本信息

## 版本注入如何工作

```
┌──────────────────────┐
│   git commit hash    │  ← from Git
└──────────────────────┘
           ↓
┌──────────────────────┐
│  make version-inject │  ← 注入版本信息
└──────────────────────┘
           ↓
┌──────────────────────┐
│  src/shared/         │
│  version.py          │  ← 生成版本模块
└──────────────────────┘
           ↓
┌──────────────────────┐
│   FastAPI 应用       │  ← 自动暴露 API
└──────────────────────┘
           ↓
┌──────────────────────┐
│  /api/v1/version     │  ← 获取版本信息
└──────────────────────┘
```

## Docker 镜像版本标签

`make docker-build` 会同时创建两个镜像标签：

```
registry.example.com/cybertwin-internal-medicine-agent:latest
registry.example.com/cybertwin-internal-medicine-agent:0.1.3
```

## 工作流示例

### 开发工作流

```bash
# 初始化
make install-dev

# 开发
make dev-run             # 启动应用，自动热重载
make test                # 运行单元测试
make lint                # 代码检查

# 清理
make clean
```

### 发布工作流

```bash
# 更新版本（编辑 pyproject.toml）
nano pyproject.toml

# 构建和测试
make install-dev
make test-cov
make clean

# 注入版本信息
make version-inject

# 构建 Docker 镜像
make docker-build

# 验证
docker run -p 8000:8000 registry.example.com/cybertwin-internal-medicine-agent:0.1.3
curl http://localhost:8000/api/v1/version
```

## 配置

### 自定义镜像仓库

编辑 Makfile 中的以下行：

```makefile
IMAGE_REGISTRY := your-registry.com
```

### 自定义 Python 版本

```makefile
PYTHON_VERSION := 3.13
```

## 测试脚本

### 测试版本 API

```bash
python3 scripts/test_version_api.py
```

会测试所有版本信息 API 端点并显示结果。

### Makfile 使用示例

```bash
bash scripts/makefile_example.sh
```

演示完整的 Makfile 使用流程。

## 更多文档

- **[MAKFILE_GUIDE.md](MAKEFILE_GUIDE.md)** - 详细的 Makfile 使用说明
- **[BUILD_AND_DEPLOY_GUIDE.md](BUILD_AND_DEPLOY_GUIDE.md)** - 完整的构建和部署指南
- **[Dockerfile](Dockerfile)** - Docker 配置（支持版本注入）

## 常见命令速查表

| 命令 | 说明 |
|------|------|
| `make help` | 显示所有可用命令 |
| `make version` | 显示版本信息 |
| `make version-inject` | 注入版本到代码 |
| `make install` | 安装依赖 |
| `make dev-run` | 开发模式运行 |
| `make docker-build` | 构建 Docker 镜像 |
| `make test` | 运行测试 |
| `make clean` | 清理缓存 |

## 下一步

1. 📖 查看 [MAKFILE_GUIDE.md](MAKEFILE_GUIDE.md) 了解更多细节
2. 🚀 运行 `make version-inject` 注入版本信息
3. 🐳 运行 `make docker-build` 构建 Docker 镜像
4. 🧪 运行 `make test` 执行测试
5. 🌐 访问 http://localhost:8000/api/v1/version 查看版本信息

## 支持

- 运行 `make help` 查看所有可用命令
- 查看 Makfile 中的注释了解更多细节
- 参考 BUILD_AND_DEPLOY_GUIDE.md 了解常见问题

---

**版本**: 0.1.3  
**最后更新**: 2026-02-27
