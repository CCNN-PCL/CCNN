# Makefile for Cybertwin Security Microservices
# Build Docker images for all four Python microservices

# Configuration
VERSION ?= latest

# Service names and directories
AUTH_SERVICE_DIR = auth-service/main-folder
DATAMODEL_DIR = datamodel
MATCHMODEL_DIR = matchmodel
USERMODEL_DIR = usermodel

# Image names
AUTH_IMAGE = auth-service:$(VERSION)
DATAMODEL_IMAGE = datamodel:$(VERSION)
MATCHMODEL_IMAGE = matchmodel:$(VERSION)
USERMODEL_IMAGE = usermodel:$(VERSION)

# Default target
.PHONY: help
help:
	@echo "Cybertwin Security Microservices Docker Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  build-all      - Build all four microservice images"
	@echo "  build-auth     - Build auth-service image"
	@echo "  build-datamodel - Build datamodel image"
	@echo "  build-matchmodel - Build matchmodel image"
	@echo "  build-usermodel - Build usermodel image"
	@echo "  push-all       - Push all images to registry"
	@echo "  push-auth      - Push auth-service image"
	@echo "  push-datamodel - Push datamodel image"
	@echo "  push-matchmodel - Push matchmodel image"
	@echo "  push-usermodel - Push usermodel image"
	@echo "  clean          - Remove all built images"
	@echo ""
	@echo "Configuration:"
	@echo "  VERSION=$(VERSION)"
	@echo ""
	@echo "Example usage:"
	@echo "  make build-all"
	@echo "  make build-all VERSION=1.0.0"
	@echo "  make build-auth push-auth"

# Build targets
.PHONY: build-all
build-all: build-auth build-datamodel build-matchmodel build-usermodel

.PHONY: build-auth
build-auth:
	@echo "Building auth-service image..."
	docker build -t $(AUTH_IMAGE) -f $(AUTH_SERVICE_DIR)/Dockerfile $(AUTH_SERVICE_DIR)
	@echo "✓ Built $(AUTH_IMAGE)"

.PHONY: build-datamodel
build-datamodel:
	@echo "Building datamodel image..."
	docker build -t $(DATAMODEL_IMAGE) -f $(DATAMODEL_DIR)/Dockerfile $(DATAMODEL_DIR)
	@echo "✓ Built $(DATAMODEL_IMAGE)"

.PHONY: build-matchmodel
build-matchmodel:
	@echo "Building matchmodel image..."
	docker build -t $(MATCHMODEL_IMAGE) $(MATCHMODEL_DIR)
	@echo "✓ Built $(MATCHMODEL_IMAGE)"

.PHONY: build-usermodel
build-usermodel:
	@echo "Building usermodel image..."
	docker build -t $(USERMODEL_IMAGE) $(USERMODEL_DIR)
	@echo "✓ Built $(USERMODEL_IMAGE)"

# Push targets
.PHONY: push-all
push-all: push-auth push-datamodel push-matchmodel push-usermodel

.PHONY: push-auth
push-auth:
	@echo "Pushing auth-service image..."
	docker push $(AUTH_IMAGE)
	@echo "✓ Pushed $(AUTH_IMAGE)"

.PHONY: push-datamodel
push-datamodel:
	@echo "Pushing datamodel image..."
	docker push $(DATAMODEL_IMAGE)
	@echo "✓ Pushed $(DATAMODEL_IMAGE)"

.PHONY: push-matchmodel
push-matchmodel:
	@echo "Pushing matchmodel image..."
	docker push $(MATCHMODEL_IMAGE)
	@echo "✓ Pushed $(MATCHMODEL_IMAGE)"

.PHONY: push-usermodel
push-usermodel:
	@echo "Pushing usermodel image..."
	docker push $(USERMODEL_IMAGE)
	@echo "✓ Pushed $(USERMODEL_IMAGE)"

# Clean target
.PHONY: clean
clean:
	@echo "Removing local Docker images..."
	-docker rmi $(AUTH_IMAGE) 2>/dev/null || true
	-docker rmi $(DATAMODEL_IMAGE) 2>/dev/null || true
	-docker rmi $(MATCHMODEL_IMAGE) 2>/dev/null || true
	-docker rmi $(USERMODEL_IMAGE) 2>/dev/null || true
	@echo "✓ Cleaned up images"

# Test targets (optional)
.PHONY: test-build
test-build:
	@echo "Testing build commands (dry-run)..."
	@echo "Would run: docker build -t $(AUTH_IMAGE) -f $(AUTH_SERVICE_DIR)/Dockerfile $(AUTH_SERVICE_DIR)"
	@echo "Would run: docker build -t $(DATAMODEL_IMAGE) $(DATAMODEL_DIR)"
	@echo "Would run: docker build -t $(MATCHMODEL_IMAGE) $(MATCHMODEL_DIR)"
	@echo "Would run: docker build -t $(USERMODEL_IMAGE) $(USERMODEL_DIR)"

# Quick build with specific version
.PHONY: version
version:
	@echo "Current version: $(VERSION)"
	@echo "Images would be tagged as:"
	@echo "  $(AUTH_IMAGE)"
	@echo "  $(DATAMODEL_IMAGE)"
	@echo "  $(MATCHMODEL_IMAGE)"
	@echo "  $(USERMODEL_IMAGE)"
