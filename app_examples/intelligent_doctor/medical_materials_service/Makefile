# Makefile for MedicalMaterialsMcpService
# Go项目构建和开发工具

# 项目信息
PROJECT_NAME := medical_materials
MODULE_NAME := git.pcl.ac.cn/CN/MedicalMaterialsMcpService
VERSION ?= 0.1.0
BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")

# Docker相关配置
DOCKER_REGISTRY ?= 
DOCKER_NAMESPACE ?= 
# Docker镜像名称必须全部小写
DOCKER_IMAGE_NAME := medical-materials
DOCKER_IMAGE_TAG := $(VERSION)
DOCKER_IMAGE_FULL_NAME := $(if $(DOCKER_REGISTRY),$(DOCKER_REGISTRY)/$(if $(DOCKER_NAMESPACE),$(DOCKER_NAMESPACE)/)$(DOCKER_IMAGE_NAME),$(DOCKER_IMAGE_NAME))
DOCKER_PLATFORMS ?= linux/amd64,linux/arm64
DOCKER_BUILDX_NAME ?= medical-materials-builder

# Go相关配置
GO := go
GO_BUILD := $(GO) build
GO_TEST := $(GO) test
GO_CLEAN := $(GO) clean
GO_MOD := $(GO) mod
GO_FMT := $(GO) fmt
GO_VET := $(GO) vet
GO_TIDY := $(GO) mod tidy

# 构建目录
BIN_DIR := bin
DIST_DIR := dist

# 输出文件
BINARY_NAME := medical-materials-mcp-service
BINARY_PATH := $(BIN_DIR)/$(BINARY_NAME)

# 构建参数
LDFLAGS := -ldflags "\
	-X '$(MODULE_NAME)/config.Version=$(VERSION)' \
	-X '$(MODULE_NAME)/config.BuildTime=$(BUILD_TIME)' \
	-X '$(MODULE_NAME)/config.GitCommit=$(GIT_COMMIT)' \
	-X '$(MODULE_NAME)/config.GitBranch=$(GIT_BRANCH)'"

# 帮助信息
.PHONY: help
help:
	@echo "MedicalMaterialsMcpService Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "常用目标:"
	@echo "  build      - 编译项目"
	@echo "  run        - 运行项目"
	@echo "  clean      - 清理构建文件"
	@echo "  test       - 运行测试"
	@echo "  fmt        - 格式化代码"
	@echo "  vet        - 代码静态检查"
	@echo "  tidy       - 整理go.mod依赖"
	@echo "  deps       - 下载依赖"
	@echo ""
	@echo "Docker相关:"
	@echo "  docker-build      - 构建Docker镜像"
	@echo "  docker-build-dev  - 构建开发环境Docker镜像"
	@echo "  docker-buildx     - 使用buildx构建多平台Docker镜像"
	@echo "  docker-push       - 推送Docker镜像到仓库"
	@echo "  docker-run        - 运行Docker容器"
	@echo "  docker-run-dev    - 运行开发环境Docker容器"
	@echo "  docker-stop       - 停止Docker容器"
	@echo "  docker-clean      - 清理Docker镜像和容器"
	@echo "  docker-logs       - 查看Docker容器日志"
	@echo "  docker-shell      - 进入Docker容器shell"
	@echo ""
	@echo "其他目标:"
	@echo "  build-all  - 编译所有平台"
	@echo "  build-fast - 快速编译（不包含版本信息）"
	@echo "  test-cover - 运行测试并生成覆盖率报告"
	@echo "  version    - 显示版本信息"
	@echo "  help       - 显示此帮助信息"

# 创建目录
$(BIN_DIR):
	@mkdir -p $(BIN_DIR)

$(DIST_DIR):
	@mkdir -p $(DIST_DIR)

# 下载依赖
.PHONY: deps
deps:
	@echo "下载依赖..."
	$(GO_MOD) download

# 整理依赖
.PHONY: tidy
tidy:
	@echo "整理go.mod依赖..."
	$(GO_TIDY)

# 格式化代码
.PHONY: fmt
fmt:
	@echo "格式化代码..."
	$(GO_FMT) ./...

# 代码静态检查
.PHONY: vet
vet:
	@echo "运行go vet..."
	$(GO_VET) ./...

# 编译项目
.PHONY: build
build: $(BIN_DIR)
	@echo "编译项目..."
	@echo "版本: $(VERSION)"
	@echo "提交: $(GIT_COMMIT)"
	@echo "分支: $(GIT_BRANCH)"
	@echo "时间: $(BUILD_TIME)"
	$(GO_BUILD) $(LDFLAGS) -o $(BINARY_PATH) ./cmd/server
	@echo "编译完成: $(BINARY_PATH)"

# 快速编译（不包含版本信息）
.PHONY: build-fast
build-fast: $(BIN_DIR)
	@echo "快速编译..."
	$(GO_BUILD) -o $(BINARY_PATH) ./cmd/server
	@echo "快速编译完成: $(BINARY_PATH)"

# 编译所有平台
.PHONY: build-all
build-all: $(DIST_DIR)
	@echo "编译所有平台..."
	@echo "版本: $(VERSION)"
	
	@echo "编译 Linux amd64..."
	GOOS=linux GOARCH=amd64 $(GO_BUILD) $(LDFLAGS) -o $(DIST_DIR)/$(BINARY_NAME)-linux-amd64 ./cmd/server
	
	@echo "编译 Linux arm64..."
	GOOS=linux GOARCH=arm64 $(GO_BUILD) $(LDFLAGS) -o $(DIST_DIR)/$(BINARY_NAME)-linux-arm64 ./cmd/server
	
	@echo "编译 Darwin amd64..."
	GOOS=darwin GOARCH=amd64 $(GO_BUILD) $(LDFLAGS) -o $(DIST_DIR)/$(BINARY_NAME)-darwin-amd64 ./cmd/server
	
	@echo "编译 Darwin arm64..."
	GOOS=darwin GOARCH=arm64 $(GO_BUILD) $(LDFLAGS) -o $(DIST_DIR)/$(BINARY_NAME)-darwin-arm64 ./cmd/server
	
	@echo "编译 Windows amd64..."
	GOOS=windows GOARCH=amd64 $(GO_BUILD) $(LDFLAGS) -o $(DIST_DIR)/$(BINARY_NAME)-windows-amd64.exe ./cmd/server
	
	@echo "编译完成！文件保存在 $(DIST_DIR) 目录"

# 运行项目
.PHONY: run
run: build
	@echo "运行项目..."
	@$(BINARY_PATH)

# 运行测试
.PHONY: test
test:
	@echo "运行测试..."
	$(GO_TEST) -v ./...

# 运行测试并生成覆盖率报告
.PHONY: test-cover
test-cover:
	@echo "运行测试并生成覆盖率报告..."
	$(GO_TEST) -coverprofile=coverage.out ./...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "覆盖率报告已生成: coverage.html"

# 清理构建文件
.PHONY: clean
clean:
	@echo "清理构建文件..."
	$(GO_CLEAN)
	@rm -rf $(BIN_DIR) $(DIST_DIR)
	@rm -f coverage.out coverage.html
	@echo "清理完成"

# ==================== Docker相关目标 ====================

# 构建Docker镜像
.PHONY: docker-build
docker-build:
	@echo "构建Docker镜像..."
	@echo "镜像名称: $(DOCKER_IMAGE_FULL_NAME):$(DOCKER_IMAGE_TAG)"
	docker build \
		--build-arg VERSION=$(VERSION) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg GIT_BRANCH=$(GIT_BRANCH) \
		-t $(DOCKER_IMAGE_FULL_NAME):$(DOCKER_IMAGE_TAG) \
		.
	@echo "镜像构建完成:"
	@echo "  $(DOCKER_IMAGE_FULL_NAME):$(DOCKER_IMAGE_TAG)"

# 构建开发环境Docker镜像
.PHONY: docker-build-dev
docker-build-dev:
	@echo "构建开发环境Docker镜像..."
	docker build \
		-f Dockerfile.dev \
		--build-arg VERSION=dev \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg GIT_BRANCH=$(GIT_BRANCH) \
		-t $(DOCKER_IMAGE_FULL_NAME):dev \
		.
	@echo "开发镜像构建完成: $(DOCKER_IMAGE_FULL_NAME):dev"

# 初始化docker buildx
.PHONY: docker-buildx-init
docker-buildx-init:
	@echo "初始化docker buildx..."
	docker buildx create --name $(DOCKER_BUILDX_NAME) --use 2>/dev/null || docker buildx use $(DOCKER_BUILDX_NAME)
	docker buildx inspect --bootstrap

# 使用buildx构建多平台Docker镜像
.PHONY: docker-buildx
docker-buildx: docker-buildx-init
	@echo "使用buildx构建多平台Docker镜像..."
	@echo "平台: $(DOCKER_PLATFORMS)"
	@echo "镜像名称: $(DOCKER_IMAGE_FULL_NAME):$(DOCKER_IMAGE_TAG)"
	docker buildx build \
		--platform $(DOCKER_PLATFORMS) \
		--build-arg VERSION=$(VERSION) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg GIT_BRANCH=$(GIT_BRANCH) \
		-t $(DOCKER_IMAGE_FULL_NAME):$(DOCKER_IMAGE_TAG) \
		-f Dockerfile.multiarch \
		--push \
		.
	@echo "多平台镜像构建并推送完成"

# 运行Docker容器
.PHONY: docker-run
docker-run:
	@echo "运行Docker容器..."
	docker-compose up -d
	@echo "容器已启动，使用 'make docker-logs' 查看日志"

# 运行开发环境Docker容器
.PHONY: docker-run-dev
docker-run-dev:
	@echo "运行开发环境Docker容器..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "开发容器已启动，使用 'make docker-logs-dev' 查看日志"

# 停止Docker容器
.PHONY: docker-stop
docker-stop:
	@echo "停止Docker容器..."
	docker-compose down
	@echo "容器已停止"

# 停止开发环境Docker容器
.PHONY: docker-stop-dev
docker-stop-dev:
	@echo "停止开发环境Docker容器..."
	docker-compose -f docker-compose.dev.yml down
	@echo "开发容器已停止"

# 清理Docker镜像和容器
.PHONY: docker-clean
docker-clean:
	@echo "清理Docker资源..."
	@echo "停止并删除容器..."
	docker-compose down --rmi local -v 2>/dev/null || true
	docker-compose -f docker-compose.dev.yml down --rmi local -v 2>/dev/null || true
	@echo "删除未使用的镜像..."
	docker image prune -f
	@echo "删除未使用的卷..."
	docker volume prune -f
	@echo "Docker资源清理完成"

# 查看Docker容器日志
.PHONY: docker-logs
docker-logs:
	@echo "查看Docker容器日志..."
	docker-compose logs -f

# 查看开发环境Docker容器日志
.PHONY: docker-logs-dev
docker-logs-dev:
	@echo "查看开发环境Docker容器日志..."
	docker-compose -f docker-compose.dev.yml logs -f

# 进入Docker容器shell
.PHONY: docker-shell
docker-shell:
	@echo "进入Docker容器shell..."
	docker-compose exec medical-materials-mcp-service sh

# 进入开发环境Docker容器shell
.PHONY: docker-shell-dev
docker-shell-dev:
	@echo "进入开发环境Docker容器shell..."
	docker-compose -f docker-compose.dev.yml exec medical-materials-mcp-service sh

# 显示版本信息
.PHONY: version
version:
	@echo "项目: $(PROJECT_NAME)"
	@echo "模块: $(MODULE_NAME)"
	@echo "版本: $(VERSION)"
	@echo "提交: $(GIT_COMMIT)"
	@echo "分支: $(GIT_BRANCH)"
	@echo "时间: $(BUILD_TIME)"
	@echo "Docker镜像: $(DOCKER_IMAGE_FULL_NAME):$(DOCKER_IMAGE_TAG)"

# 默认目标
.DEFAULT_GOAL := help

# 兼容旧版本
.PHONY: docker
docker: docker-build
