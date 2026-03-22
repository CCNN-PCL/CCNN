# 使用官方Python 3.10镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 使用国内镜像源（健壮写法）
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
COPY requirements.txt pyproject.toml uv.lock ./

# 使用国内pip镜像源安装Python依赖
RUN pip install --no-cache-dir --upgrade pip -i  https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir uv -i  https://mirrors.aliyun.com/pypi/simple/ && \
    uv pip install --system --no-cache -r pyproject.toml -i  https://mirrors.aliyun.com/pypi/simple/

# 创建应用目录结构
RUN mkdir -p /app/src/shared /app/data/backups

# 复制应用代码
COPY ./src /app/src
COPY ./scripts /app/scripts

# 创建数据目录
RUN mkdir -p /app/data/北京/BJ001 /app/data/上海/SH001 /app/data/backups

# 设置权限
RUN chmod -R 755 /app/data

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

