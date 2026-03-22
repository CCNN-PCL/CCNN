# MedicalMaterialsMcpService

MCP server built with mcp-go

## 🚀 Getting Started

This project was generated with [`kmcp`](https://github.com/kagent-dev/kmcp).

### Prerequisites

- [Go](https://golang.org/doc/install) (1.23 or later)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Local Development

1.  **Tidy dependencies:**
    ```bash
    go mod tidy
    ```

2.  **Run the server:**
    ```bash
    go run cmd/server/main.go
    ```

### Building the Docker Image

To build a Docker image for this project, run:

```bash
kmcp build
```

This will create an image named `MedicalMaterialsMcpService:latest`.

### Deploying to Kubernetes

To deploy the MCP server to Kubernetes, first ensure you have a running cluster and `kubectl` is configured. Then, run:

```bash
kmcp deploy mcp
```

This will create an `MCPServer` custom resource in the `default` namespace.

## 🛠️ Adding a New Tool

To add a new tool to your project, use the `kmcp add-tool` command:

```bash
kmcp add-tool <tool-name>
```

This will generate a new Go file in the `tools/` directory with a template for your new tool. You will need to add the new tool to the `main.go` file.

## 📦 Makefile 使用说明

项目包含一个完整的 Makefile，用于简化构建、测试和开发流程。

### 常用命令

```bash
# 显示帮助信息
make help

# 编译项目（包含版本信息）
make build

# 快速编译（不包含版本信息）
make build-fast

# 运行项目
make run

# 清理构建文件
make clean

# 运行测试
make test

# 格式化代码
make fmt

# 代码静态检查
make vet

# 整理依赖
make tidy

# 下载依赖
make deps
```

### Docker 相关命令

```bash
# 构建生产环境Docker镜像
make docker-build

# 构建开发环境Docker镜像（支持热重载）
make docker-build-dev

# 运行生产环境Docker容器
make docker-run

# 运行开发环境Docker容器
make docker-run-dev

# 查看容器日志
make docker-logs

# 停止容器
make docker-stop

# 清理Docker资源
make docker-clean

# 进入容器shell
make docker-shell

# 构建多平台镜像（需要docker buildx）
make docker-buildx

# 推送镜像到仓库
make docker-push
```

### 其他命令

```bash
# 编译所有平台（Linux、macOS、Windows）
make build-all

# 运行测试并生成覆盖率报告
make test-cover

# 显示版本信息
make version
```

### 构建目录结构

- `bin/` - 编译生成的可执行文件
- `dist/` - 多平台编译输出文件

### 版本信息

Makefile会自动注入以下版本信息到二进制文件中：
- 版本号（默认 0.1.0）
- Git提交哈希
- Git分支
- 构建时间

## 🔧 版本信息功能

### 命令行 Flag

项目支持 `--version` flag 显示详细的版本信息：

```bash
# 显示版本信息
./medical-materials-mcp-service --version

# 输出示例：
MedicalMaterialsMcpService
Version:    0.1.0
Build Time: 2026-02-26_02:59:28
Git Commit: 322d002
Git Branch: master
```

### 帮助信息

```bash
# 显示帮助信息
./medical-materials-mcp-service --help

# 输出示例：
Usage of ./medical-materials-mcp-service:
  -version
    	显示版本信息
```

### 版本信息注入

版本信息在编译时通过 `-ldflags` 注入：

```bash
# 编译时注入版本信息
go build -ldflags "\
  -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.Version=0.1.0' \
  -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.BuildTime=2026-02-26_02:59:28' \
  -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.GitCommit=322d002' \
  -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.GitBranch=master'" \
  -o medical-materials-mcp-service ./cmd/server
```

### 构建类型

1. **完整构建**（包含版本信息）:
   ```bash
   make build
   ```

2. **快速构建**（不包含版本信息，使用默认值）:
   ```bash
   make build-fast
   # 版本信息显示为默认值：
   # Version:    0.0.0-dev
   # Build Time: unknown
   # Git Commit: unknown
   # Git Branch: unknown
   ```

## 🐳 Docker 构建指南

### 快速开始

1. **构建生产镜像：**
   ```bash
   make docker-build
   ```

2. **运行生产容器：**
   ```bash
   make docker-run
   ```

3. **查看日志：**
   ```bash
   make docker-logs
   ```

### 开发环境

1. **构建开发镜像（支持热重载）：**
   ```bash
   make docker-build-dev
   ```

2. **运行开发容器：**
   ```bash
   make docker-run-dev
   ```

3. **查看开发日志：**
   ```bash
   make docker-logs-dev
   ```

### 多平台构建

支持构建多平台镜像（Linux amd64/arm64）：

```bash
# 初始化buildx
make docker-buildx-init

# 构建并推送多平台镜像
make docker-buildx
```

### 镜像配置

编辑 `.env.docker` 文件配置镜像仓库：

```bash
# 设置镜像仓库地址
DOCKER_REGISTRY=registry.example.com

# 设置命名空间
DOCKER_NAMESPACE=your-org

# 设置镜像标签
DOCKER_IMAGE_TAG=1.0.0
```

### 镜像命名规范

**重要**: Docker 镜像名称必须遵循以下规范：
- 必须全部小写字母
- 可以包含数字、点、下划线和连字符
- 必须以字母或数字开头
- 不能包含大写字母

**错误示例**（会导致构建失败）:
```bash
MedicalMaterialsMcpService:0.1.0  # 包含大写字母，错误！
```

**正确示例**:
```bash
medical-materials-mcp-service:0.1.0  # 全部小写，正确！
```

### 详细文档

更多详细信息请查看 [DOCKER_USAGE.md](./DOCKER_USAGE.md)。

## 🐛 已知问题

### Docker 构建问题

1. **镜像名称大小写错误**（已修复）:
   - 问题: Docker 镜像名称包含大写字母
   - 错误信息: `ERROR: invalid tag MedicalMaterialsMcpService:0.1.0: repository name must be lowercase`
   - 修复: 镜像名称已改为全小写的 `medical-materials-mcp-service`

### Go 代码问题

运行 `make vet` 时可能会报告结构体标签语法错误，需要手动修复以下文件中的标签：
1. `api/model/images.go` - 第10行：将中文冒号 `：` 改为英文冒号 `:`
2. `api/model/visit.go` - 第144行：修复不完整的JSON标签
3. `db/model/check.go` - 第72行：修复不完整的JSON标签

修复后即可正常通过 `make vet` 检查。

## 📁 项目结构

```
.
├── Makefile              # 构建和开发工具
├── Dockerfile            # 生产环境Dockerfile
├── Dockerfile.dev        # 开发环境Dockerfile
├── Dockerfile.multiarch  # 多平台构建Dockerfile
├── docker-compose.yml    # 生产环境Docker Compose配置
├── docker-compose.dev.yml # 开发环境Docker Compose配置
├── .air.toml            # 热重载配置
├── .env.docker          # Docker环境变量配置
├── DOCKER_USAGE.md      # Docker使用文档
├── cmd/                 # 应用入口
├── internal/            # 内部包
├── api/                 # API定义
├── db/                  # 数据库相关
├── auth/                # 认证相关
├── config/              # 配置（包含version.go）
├── conf/                # 配置文件
└── logger/              # 日志
```
