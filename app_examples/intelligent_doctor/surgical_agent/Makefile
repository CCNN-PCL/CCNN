#===============================================================
# Surgical Agent - Makefile
#===============================================================
# 目标平台和版本配置
SHELL := /bin/bash
.DEFAULT_GOAL := help

# 项目配置
PROJECT_NAME = surgical-agent
PROJECT_DIR := $(shell pwd)
PYTHON := python3
PIP := pip3
VENV_DIR := .venv

# 版本配置
BUILD_VERSION ?= 0.1.0
VERSION_MAJOR ?= 0
VERSION_MINOR ?= 1
VERSION_PATCH ?= 0
BUILD_TIME := $(shell date '+%Y-%m-%d %H:%M:%S')
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Docker 配置
IMAGE_NAME ?= surgical-agent
IMAGE_TAG = $(IMAGE_NAME):$(BUILD_VERSION)
PLATFORM ?= linux/amd64
REMOTE_REPO = 192.168.64.60:31304
REMOTE_GROUP = medical-app
REMOTE_IMAGE = $(REMOTE_REPO)/$(REMOTE_GROUP)/$(IMAGE_NAME):$(BUILD_VERSION)

# 开发配置
SERVICE_PORT ?= 8004
SERVICE_NAME ?= surgical

#===============================================================
# Phony targets definition
#===============================================================
.PHONY: help install dev test run clean build push version inject-version \
        lint format check-env docker-build docker-push poetry-install

#===============================================================
# Help target - 显示所有可用的Make命令
#===============================================================
help:
	@echo "=================================="
	@echo "$(PROJECT_NAME) - Makefile 命令"
	@echo "=================================="
	@echo ""
	@echo "📋 基础命令:"
	@echo "  make help              显示此帮助信息"
	@echo "  make version           显示版本信息"
	@echo ""
	@echo "🏗️  构建和部署:"
	@echo "  make install           安装依赖（创建虚拟环境）"
	@echo "  make build             构建Docker镜像"
	@echo "  make push              推送镜像到远程仓库"
	@echo ""
	@echo "▶️  运行和测试:"
	@echo "  make run               运行应用（开发模式）"
	@echo "  make dev               开发模式（带热重载）"
	@echo "  make test              运行单元测试"
	@echo ""
	@echo "🧹 清理和维护:"
	@echo "  make clean             清理临时文件"
	@echo "  make lint              代码静态检查"
	@echo "  make format            代码格式化"
	@echo ""
	@echo "🔧 工具:"
	@echo "  make inject-version    注入版本信息（编译时使用）"
	@echo ""
	@echo "版本信息: $(BUILD_VERSION) (Git commit: $(GIT_COMMIT))"
	@echo "目标平台: $(PLATFORM)"
	@echo ""

#===============================================================
# 版本管理
#===============================================================
version:
	@echo "=================================="
	@echo "$(PROJECT_NAME) 版本信息"
	@echo "=================================="
	@echo "版本号: $(BUILD_VERSION)"
	@echo "主版本: $(VERSION_MAJOR)"
	@echo "子版本: $(VERSION_MINOR)"
	@echo "修订版: $(VERSION_PATCH)"
	@echo "Git commit: $(GIT_COMMIT)"
	@echo "构建时间: $(BUILD_TIME)"
	@echo ""

inject-version:
	@echo "⚙️  正在注入版本信息到 src/version.py ..."
	@mkdir -p src
	@python3 scripts/inject_version.py $(BUILD_VERSION) $(VERSION_MAJOR) $(VERSION_MINOR) $(VERSION_PATCH) "$(GIT_COMMIT)" "$(BUILD_TIME)"
	@echo "✅ 版本信息注入完成"

#===============================================================
# 环境和依赖
#===============================================================
check-env:
	@echo "检查环境..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python3 未安装"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "⚠️  Docker 未安装"; }
	@echo "✅ 环境检查完成"

install: check-env
	@echo "📦 安装依赖..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "虚拟环境已创建"; \
	fi
	@. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade pip setuptools wheel
	@. $(VENV_DIR)/bin/activate && $(PIP) install -r requirements.txt
	@echo "✅ 依赖安装完成"

poetry-install: check-env
	@echo "📦 使用Poetry安装依赖..."
	@command -v poetry >/dev/null 2>&1 || { echo "❌ Poetry 未安装"; exit 1; }
	poetry install
	@echo "✅ Poetry依赖安装完成"

#===============================================================
# 开发和测试
#===============================================================
run: install inject-version
	@echo "▶️  启动应用 (端口: $(SERVICE_PORT))..."
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m uvicorn src.main:app \
		--host 0.0.0.0 --port $(SERVICE_PORT) --reload

dev: install inject-version
	@echo "▶️  开发模式启动应用 (带热重载, 端口: $(SERVICE_PORT))..."
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m uvicorn src.main:app \
		--host 0.0.0.0 --port $(SERVICE_PORT) --reload --log-level debug

test: install
	@echo "🧪 运行测试..."
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m pytest tests/ -v --cov=src
	@echo "✅ 测试完成"

#===============================================================
# 代码质量
#===============================================================
lint: install
	@echo "🔍 运行代码检查..."
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m pylint src/ || true
	@echo "✅ 代码检查完成"

format: install
	@echo "🎨 格式化代码..."
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m black src/ tests/ || true
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -m isort src/ tests/ || true
	@echo "✅ 代码格式化完成"

#===============================================================
# Docker 构建和推送
#===============================================================
docker-build: inject-version
	@echo "🐳 构建 Docker 镜像..."
	@echo "   镜像标签: $(IMAGE_TAG)"
	@echo "   平台: $(PLATFORM)"
	docker build \
		--platform $(PLATFORM) \
		--build-arg BUILD_VERSION=$(BUILD_VERSION) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg BUILD_TIME="$(BUILD_TIME)" \
		-t $(IMAGE_TAG) .
	@echo "✅ Docker 镜像构建成功"

build: docker-build
	@echo "✅ 构建成功: $(IMAGE_TAG)"

docker-push: docker-build
	@echo "📤 推送镜像到远程仓库..."
	@echo "   目标: $(REMOTE_IMAGE)"
	docker tag $(IMAGE_TAG) $(REMOTE_IMAGE)
	docker push $(REMOTE_IMAGE)
	@echo "✅ 镜像推送成功"

push: docker-push
	@echo "✅ 推送成功"

#===============================================================
# 清理
#===============================================================
clean:
	@echo "🧹 清理临时文件..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ 清理完成"

#===============================================================
# 默认目标
#===============================================================
all: clean install test build
	@echo "✅ 完整构建流程完成"