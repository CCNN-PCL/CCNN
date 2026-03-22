# Build stage
FROM golang:1.23.0-alpine AS builder

# 安装动态编译依赖
# 安装动态编译依赖（Alpine 下编译 CGO 需 gcc/musl-dev）
RUN echo -e "https://mirrors.aliyun.com/alpine/v3.20/main\nhttps://mirrors.aliyun.com/alpine/v3.20/community" > /etc/apk/repositories && \
    apk update && \
    apk add --no-cache \
    gcc \
    musl-dev \
    musl-utils \
    libc6-compat

# 版本信息
ARG BUILD_VERSION=0.1.5
ARG GIT_COMMIT=unknown
ARG GIT_BRANCH=unknown
ARG BUILD_TIME=unknown

WORKDIR /app

ENV GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
COPY go.mod go.sum ./
#RUN go mod download

COPY . .

# 构建时注入版本信息
RUN CGO_ENABLED=1 GOOS=linux go build \
    -ldflags="-X git.pcl.ac.cn/CN/Cybertwin-DataProxy/config.Version=${BUILD_VERSION} \
    -X git.pcl.ac.cn/CN/Cybertwin-DataProxy/config.Commit=${GIT_COMMIT} \
    -X git.pcl.ac.cn/CN/Cybertwin-DataProxy/config.Branch=${GIT_BRANCH} \
    -X git.pcl.ac.cn/CN/Cybertwin-DataProxy/config.BuildTime=${BUILD_TIME}" \
    -o /app/server .

# Final stage
FROM alpine:latest

WORKDIR /app

# 复制二进制文件
COPY --from=builder /app/server .
# 复制配置文件
COPY conf/ ./conf/

# 创建日志目录
RUN mkdir -p /app/logs && chmod 755 /app/logs

EXPOSE 8080

# 支持命令行参数
ENTRYPOINT ["/app/server"]
CMD [""]
