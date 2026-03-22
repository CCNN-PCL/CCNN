# 使用官方Python 3.10镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app


# 使用国内镜像源
RUN [ -f /etc/apt/sources.list.d/debian.sources ] && sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || true && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list/debian.sources || true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt pyproject.toml uv.lock ./

# 使用国内pip镜像源安装Python依赖
RUN pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install --no-cache-dir uv -i https://mirrors.aliyun.com/pypi/simple/ && \
    uv pip install --system --no-cache -r pyproject.toml -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY ./src ./src
COPY ./scripts ./scripts

# 创建数据目录
RUN mkdir -p /app/data/北京/BJ001 /app/data/上海/SH001 /app/data/backups

# 设置权限
RUN chmod -R 755 /app/data

# 启动命令
CMD ["python", "-m", "src.main"]
