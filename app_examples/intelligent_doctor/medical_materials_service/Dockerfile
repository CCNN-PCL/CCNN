# Build stage
FROM golang:1.23.0-alpine AS builder

# 安装动态编译依赖（Alpine 下编译 CGO 需 gcc/musl-dev）
RUN echo -e "https://mirrors.aliyun.com/alpine/v3.20/main\nhttps://mirrors.aliyun.com/alpine/v3.20/community" > /etc/apk/repositories && \
    apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    musl-utils \
    libc6-compat

# 设置默认编译参数（动态链接）
ENV CGO_ENABLED=1 \
    GOOS=linux \
    GOARCH=amd64 \
    CGO_CFLAGS="-O2 -g" \
    CGO_LDFLAGS="-Wl,-rpath=/lib"

WORKDIR /app

ENV GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
COPY go.mod go.sum ./

COPY . .

# 构建应用
RUN go build -ldflags="-linkmode=external -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.Version=${VERSION:-0.1.0}' -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.BuildTime=$(date -u '+%Y-%m-%d_%H:%M:%S')' -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.GitCommit=${GIT_COMMIT:-unknown}' -X 'git.pcl.ac.cn/CN/MedicalMaterialsMcpService/config.GitBranch=${GIT_BRANCH:-unknown}'" -o /app/server ./cmd/server

# Final stage
FROM alpine:3.20

# 安装必要的运行时依赖
RUN echo -e "https://mirrors.aliyun.com/alpine/v3.20/main\nhttps://mirrors.aliyun.com/alpine/v3.20/community" > /etc/apk/repositories && \
    apk update && \
    apk add --no-cache \
    ca-certificates \
    tzdata \
    libc6-compat

# 设置时区
ENV TZ=Asia/Shanghai

WORKDIR /app

# 创建必要的目录
RUN mkdir -p /app/logs /app/conf && \
    chmod 755 /app/logs

# 从构建阶段复制文件
COPY --from=builder /app/server /app/server
COPY --from=builder /app/conf/config.yaml /app/conf/config.yaml

# 设置文件权限
RUN chmod +x /app/server

# 创建非root用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

EXPOSE 8080

# 使用exec形式启动应用
ENTRYPOINT ["/app/server"]
