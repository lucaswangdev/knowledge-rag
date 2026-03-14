FROM python:3.9-slim-bookworm

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制模型缓存（提前下载好）
COPY models/ ./models/

# 复制应用代码
COPY app/ ./app/
COPY *.sql ./
COPY .env.example ./

# 创建非root用户
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]