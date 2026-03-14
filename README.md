# Knowledge-RAG

企业级私有知识库RAG服务

## 项目简介

Knowledge-RAG 是面向企业的私有知识库RAG服务，基于bge-m3向量模型和PostgreSQL+pgvector实现语义搜索和智能问答。

## 核心特性

- 🔐 多租户隔离：每个应用独立数据库，物理隔离
- 🔍 语义搜索：基于bge-m3的深度语义理解
- 💬 智能问答：RAG架构，支持引用来源
- 🚀 快速部署：Docker一键部署
- 📦 开箱即用：自动向量化存储

## 技术栈

- FastAPI - Web框架
- PostgreSQL + pgvector - 向量数据库
- FlagEmbedding (bge-m3) - 向量化模型
- Docker - 容器化部署

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/knowledge-rag.git
cd knowledge-rag
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 配置数据库连接
```

### 3. 启动服务

```bash
# 使用Docker
docker-compose up -d

# 或本地开发
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. 初始化数据库

```bash
# 创建主数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_master;"

# 执行初始化SQL
psql -h localhost -U postgres -d knowledge_master -f init_master.sql

# 创建应用数据库（示例）
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"
psql -h localhost -U postgres -d knowledge_app_001 -f init_app.sql
```

## API文档

启动服务后访问: http://localhost:8000/docs

## 接口示例

### 创建文档

```bash
curl -X POST "http://localhost:8000/api/v1/document/create" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "your_secret",
    "data": {
      "title": "测试文档",
      "content": "文档内容...",
      "tags": ["测试"]
    }
  }'
```

### 语义搜索

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "your_secret",
    "data": {
      "query": "如何融资？",
      "top_k": 5
    }
  }'
```

## 目录结构

```
knowledge-rag/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI入口
│   ├── config.py            # 配置
│   ├── router.py            # 路由
│   ├── middleware/
│   │   └── auth.py          # 认证中间件
│   ├── models/
│   │   ├── request.py       # 请求模型
│   │   └── response.py      # 响应模型
│   └── services/
│       ├── bge_service.py   # 向量化服务
│       ├── db_service.py    # 数据库服务
│       ├── document_service.py
│       └── knowledge_service.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
├── init_master.sql          # 主库初始化
├── init_app.sql             # 应用库初始化
├── requirements.txt
└── .env.example
```

## License

MIT