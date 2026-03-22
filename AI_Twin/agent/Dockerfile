# 使用官方Python 3.10镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 使用国内镜像源
RUN [ -f /etc/apt/sources.list.d/debian.sources ] && sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || true && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list/debian.sources || true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsqlite3-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 使用国内pip镜像源安装Python依赖
RUN pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ 

# 复制应用代码
COPY . .

# 注入构建信息
ARG BUILD_VERSION=dev
ARG BUILD_DATE
ARG GIT_COMMIT
ARG GIT_BRANCH

# 创建构建信息文件
RUN echo "{\"build_version\": \"${BUILD_VERSION:-dev}\", \"build_date\": \"${BUILD_DATE:-$(date -Iseconds)}\", \"git_commit\": \"${GIT_COMMIT:-}\", \"git_branch\": \"${GIT_BRANCH:-}\"}" > /app/BUILD_INFO.json

# 设置权限
RUN chmod -R 755 /app/data

# 暴露端口
EXPOSE 5050
EXPOSE 9090

# 启动命令
CMD ["python", "scripts/startup/start_backend_all.py"]
