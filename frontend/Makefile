SHELL := /bin/bash

# Editable variables
PKG_MANAGER ?= npm
APP_NAME ?= frontend
BUILD_DIR ?= dist
DOCKERFILE ?= Dockerfile

# Version management - can be overridden from root Makefile
# If VERSION is passed from root Makefile, use it; otherwise use package.json version
ifdef VERSION
  # Use version from root Makefile
  ROOT_VERSION := $(VERSION)
  # Update package.json with root version
  UPDATE_PACKAGE_VERSION := true
else
  # Use version from package.json
  ROOT_VERSION := $(shell node -e "console.log(require('./package.json').version)")
  UPDATE_PACKAGE_VERSION := false
endif

# Final version to use
FINAL_VERSION ?= $(ROOT_VERSION)
IMAGE_NAME ?= $(APP_NAME):$(FINAL_VERSION)

.PHONY: help install build clean docker-image docker-build docker-run version

help:
	@echo "Makefile targets:"
	@echo "  install           Install project dependencies (uses $(PKG_MANAGER))"
	@echo "  build             Build production bundle (auto-updates version)"
	@echo "  clean             Remove build artifacts"
	@echo "  docker-image      Build Docker image with auto-generated version tag"
	@echo "  docker-build      Alias for docker-image"
	@echo "  docker-run        Run the built image locally (port 8080)"
	@echo "  version           Show current version"
	@echo ""
	@echo "Version Information:"
	@echo "  Root Version: $(if $(VERSION),$(VERSION),not provided)"
	@echo "  Package Version: $(shell node -e "console.log(require('./package.json').version)" 2>/dev/null || echo 'unknown')"
	@echo "  Final Version: $(FINAL_VERSION)"

install:
	@echo "Installing dependencies with $(PKG_MANAGER)..."
	@if [ "$(PKG_MANAGER)" = "yarn" ]; then \
		yarn install --frozen-lockfile; \
	else \
		npm ci || npm install; \
	fi

# Helper target to update package.json with root version
update-package-version:
	@if [ "$(UPDATE_PACKAGE_VERSION)" = "true" ]; then \
		echo "📦 Updating package.json with root version: $(ROOT_VERSION)"; \
		node -e "const fs = require('fs'); const pkg = JSON.parse(fs.readFileSync('./package.json', 'utf8')); pkg.version = '$(ROOT_VERSION)'; fs.writeFileSync('./package.json', JSON.stringify(pkg, null, 2) + '\n', 'utf8'); console.log('✅ Updated package.json version to: $(ROOT_VERSION)')"; \
	else \
		echo "📦 Using existing package.json version"; \
	fi

build: install update-package-version
	@echo "Building production bundle..."
	@echo "🔧 Using version: $(FINAL_VERSION)..."
	@echo "🚀 Injecting version information..."
	@npm run version:inject
	@echo "🏗️  Building with $(PKG_MANAGER)..."
	@if [ "$(PKG_MANAGER)" = "yarn" ]; then \
		yarn build; \
	else \
		npm run build; \
	fi
	@echo "✅ Build completed for version: $(FINAL_VERSION)"

clean:
	@echo "Cleaning $(BUILD_DIR) and node_modules..."
	-rm -rf $(BUILD_DIR) node_modules

docker-image: build
	@echo "Building Docker image..."
	@echo "  - Version tag: $(IMAGE_NAME)"
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .

docker-build: docker-image

docker-run:
	@echo "Running $(IMAGE_NAME) on localhost:8080 (press Ctrl+C to stop)"
	docker run --rm -p 8080:80 $(IMAGE_NAME)

# Version management
version:
	@echo "Current version information:"
	@echo "  Root Version (from parent): $(if $(VERSION),$(VERSION),not provided)"
	@echo "  Package Version: $(shell node -e "console.log(require('./package.json').version)" 2>/dev/null || echo 'unknown')"
	@echo "  Final Version: $(FINAL_VERSION)"
	@echo "  Docker Image: $(IMAGE_NAME)"
