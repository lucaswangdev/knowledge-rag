# Knowledge-RAG 技术设计文档

## 一、系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端请求                               │
│              (appId + appSecret 认证)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI REST API                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  中间件层                                                  │  │
│  │  - 认证校验 (appId/appSecret)                              │  │
│  │  - 请求路由 (根据appId路由到对应数据库)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  业务路由                                                  │  │
│  │  - /api/v1/document/*  (文档管理)                         │  │
│  │  - /api/v1/knowledge/* (知识检索)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  BGE-M3         │  │  主数据库       │  │  向量存储       │
│  向量化服务     │  │  (应用配置)     │  │  (各项目独立PG) │
│  (单例模式)     │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 1.2 部署架构

```
┌─────────────────────────────────────────┐
│           Nginx 负载均衡                 │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       FastAPI 服务 (多实例)              │
│  - 自动根据appId路由                    │
│  - bge-m3模型单例                       │
└─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│DB_1     │   │DB_2     │   │DB_3     │
│(app_001)│   │(app_002)│   │(app_003)│
│pgvector │   │pgvector │   │pgvector │
└─────────┘   └─────────┘   └─────────┘
```

---

## 二、技术栈

| 组件 | 技术选型 | 版本 | 说明 |
|------|----------|------|------|
| Web框架 | FastAPI | 0.110.x | 高性能异步框架 |
| 向量模型 | FlagEmbedding | 1.3.0 | bge-m3封装 |
| 向量数据库 | pgvector | - | PostgreSQL插件 |
| 数据库 | PostgreSQL | 15+ | 主数据库 |
| 深度学习 | torch | 2.1.2 | CPU优化版本 |
| 文档解析 | python-docx, PyPDF2 | latest | 文档处理 |
| 部署 | Docker + Gunicorn | latest | 容器化部署 |
| API文档 | Swagger UI | built-in | 自动生成 |

---

## 三、数据库设计

### 3.1 主数据库 (knowledge_master)

存储应用配置信息。

```sql
-- 应用配置表
CREATE TABLE apps (
    id SERIAL PRIMARY KEY,
    app_id VARCHAR(50) NOT NULL UNIQUE,    -- 固定appId，如 "app_001"
    app_secret VARCHAR(128) NOT NULL,      -- 加密存储
    app_name VARCHAR(100),                 -- 应用名称
    db_name VARCHAR(50),                   -- 对应的独立数据库名
    db_host VARCHAR(100) DEFAULT 'localhost',
    db_port INT DEFAULT 5432,
    db_user VARCHAR(50),
    db_password VARCHAR(128),
    status VARCHAR(20) DEFAULT 'active',   -- active/disabled
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_apps_app_id ON apps(app_id);
CREATE INDEX idx_apps_status ON apps(status);

-- 初始化示例数据
INSERT INTO apps (app_id, app_secret, app_name, db_name) VALUES
('app_001', 'secret_xxx_team_a', 'Team A知识库', 'knowledge_app_001'),
('app_002', 'secret_xxx_team_b', 'Team B知识库', 'knowledge_app_002');
```

### 3.2 项目数据库 (knowledge_app_xxx)

每个应用独立的数据库，结构相同。

```sql
-- 文档表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100),
    tags JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 向量表 (bge-m3: 1024维)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INT,
    dense_vector vector(1024),
    sparse_weights JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 向量索引 (HNSW近似搜索)
CREATE INDEX ON document_chunks 
USING hnsw (dense_vector vector_cosine_ops);

-- 全文检索索引 (混合检索用)
CREATE INDEX ON document_chunks 
USING gin (to_tsvector('chinese', chunk_text));

-- 文档状态索引
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created ON documents(created_at DESC);

-- 对话会话表
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 对话消息表
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id} INT REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 全文检索配置
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

## 四、API设计

### 4.1 统一请求结构

```json
{
    "app_id": "app_001",
    "app_secret": "your_secret_here",
    "request_id": "req_xxx",
    "data": { }
}
```

### 4.2 统一响应结构

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": { }
}
```

### 4.3 接口列表 (全部POST)

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/app/info | 获取应用信息 |
| POST | /api/v1/document/create | 创建文档 |
| POST | /api/v1/document/list | 文档列表 |
| POST | /api/v1/document/get | 文档详情 |
| POST | /api/v1/document/delete | 删除文档 |
| POST | /api/v1/knowledge/search | 语义搜索 |
| POST | /api/v1/knowledge/chat | RAG问答 |

### 4.4 接口详细设计

#### 4.4.1 创建文档

**POST** `/api/v1/document/create`

```json
// Request
{
    "app_id": "app_001",
    "app_secret": "secret_xxx",
    "data": {
        "title": "字节跳动创业故事",
        "content": "张一鸣在2012年创立了字节跳动...",
        "tags": ["创业", "互联网"],
        "source": "manual"
    }
}

// Response
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "document_id": 1,
        "chunks_created": 5,
        "title": "字节跳动创业故事"
    }
}
```

#### 4.4.2 语义搜索

**POST** `/api/v1/knowledge/search`

```json
// Request
{
    "app_id": "app_001",
    "app_secret": "secret_xxx",
    "data": {
        "query": "如何融资？",
        "top_k": 5,
        "filters": {
            "tags": ["创业"]
        }
    }
}

// Response
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "query": "如何融资？",
        "total": 5,
        "results": [
            {
                "chunk_text": "早期融资建议先找天使投资人...",
                "document_id": 1,
                "document_title": "创业融资指南",
                "similarity_score": 0.8723,
                "chunk_index": 0
            }
        ]
    }
}
```

#### 4.4.3 RAG问答

**POST** `/api/v1/knowledge/chat`

```json
// Request
{
    "app_id": "app_001",
    "app_secret": "secret_xxx",
    "data": {
        "query": "创业初期如何组建团队？",
        "session_id": 1,
        "top_k": 3
    }
}

// Response
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "answer": "根据您上传的资料，创业初期组建团队建议...",
        "sources": [
            {
                "document_id": 1,
                "chunk_text": "核心团队至少需要...",
                "similarity_score": 0.8567
            }
        ]
    }
}
```

---

## 五、核心代码设计

### 5.1 项目结构

```
knowledge-rag/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI入口
│   ├── config.py               # 配置
│   ├── router.py               # 路由
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # 认证中间件
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py          # 请求模型
│   │   └── response.py         # 响应模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bge_service.py      # 向量化服务
│   │   ├── db_service.py       # 数据库服务
│   │   ├── document_service.py # 文档服务
│   │   └── knowledge_service.py# 知识服务
│   └── db/
│       ├── __init__.py
│       ├── connection.py       # 连接管理
│       └── migrations/         # 迁移脚本
├── models/                     # 预下载模型
├── tests/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

### 5.2 向量化服务 (单例模式)

```python
# app/services/bge_service.py
from FlagEmbedding import BGEM3FlagModel
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BGE_M3Service:
    """BGE-M3向量化服务（单例模式）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_model()
        return cls._instance
    
    def _init_model(self):
        """懒加载模型，CPU模式"""
        logger.info("正在加载BGE-M3模型（CPU模式）...")
        self.model = BGEM3FlagModel(
            'BAAI/bge-m3',
            use_fp16=False,  # CPU环境禁用FP16
            device='cpu',
            cache_folder='./models'
        )
        logger.info("BGE-M3模型加载成功")
    
    def encode_texts(self, texts: list, 
                     return_dense: bool = True,
                     return_sparse: bool = False) -> dict:
        """批量文本向量化"""
        result = self.model.encode(
            texts,
            return_dense=return_dense,
            return_sparse=return_sparse,
            return_colbert_vecs=False
        )
        
        output = {}
        if retu}rn_dense:
            output['dense_vectors'] = result['dense_vecs'].tolist()
        if return_sparse:
            output['sparse_weights'] = result['lexical_weights']
        return output
    
    def encode_query(self, query: str) -> list:
        """单个查询向量化"""
        result = self.model.encode([query])
        return result['dense_vecs'][0].tolist()
    
    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """计算两段文本相似度"""
        embeddings = self.model.encode([text_a, text_b])
        import numpy as np
        vec_a, vec_b = embeddings['dense_vecs']
        return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))

# 全局单例
bge_service = BGE_M3Service()
```

### 5.3 数据库连接管理

```python
# app/services/db_service.py
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import json

class DatabaseRouter:
    """数据库路由器 - 根据appId路由到不同数据库"""
    
    def __init__(self):
        self._engines = {}  # app_id -> engine
        self._master_engine = None
    
    def init_master(self, master_config: dict):
        """初始化主数据库连接"""
        self._master_engine = create_engine(
            f"postgresql://{master_config['user']}:{master_config['password']}"
            f"@{master_config['host']}:{master_config['port']}/{master_config['db']}",
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10
        )
    
    def get_app_config(self, app_id: str) -> dict:
        """从主库获取应用配置"""
        with self._master_engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM apps WHERE app_id = :app_id AND status = 'active'"),
                {"app_id": app_id}
            )
            row = result.fetchone()
            if not row:
                return None
            return {
                "app_id": row.app_id,
                "app_secret": row.app_secret,
                "app_name": row.app_name,
                "db_name": row.db_name,
                "db_host": row.db_host,
                "db_port": row.db_port,
                "db_user": row.db_user,
                "db_password": row.db_password
            }
    
    def get_engine(self, app_config: dict):
        """获取应用数据库引擎（带缓存）"""
        app_id = app_config['app_id']
        if app_id not in self._engines:
            self._engines[app_id] = create_engine(
                f"postgresql://{app_config['db_user']}:{app_config['db_password']}"
                f"@{app_config['db_host']}:{app_config['db_port']}/{app_config['db_name']}",
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10
            )
        return self._engines[app_id]
    
    @contextmanager
    def get_connection(self, app_config: dict):
        """获取数据库连接"""
        engine = self.get_engine(app_config)
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_master_connection(self):
        """获取主库连接"""
        conn = self._master_engine.connect()
        try:
            yield conn
        finally:
            conn.close()

# 全局实例
db_router = DatabaseRouter()
```

### 5.4 认证中间件

```python
# app/middleware/auth.py
from fastapi import HTTPException, Request
from functools import wraps
import hmac

class AuthMiddleware:
    def __init__(self, db_router: DatabaseRouter):
        self.db = db_router
    
    async def verify_request(self, app_id: str, app_secret: str) -> dict:
        """验证请求"""
        # 获取应用配置
        app_config = self.db.get_app_config(app_id)
        if not app_config:
            raise HTTPException(status_code=401, detail="无效的appId")
        
        # 校验secret
        if not self._verify_secret(app_secret, app_config['app_secret']):
            raise HTTPException(status_code=401, detail="appSecret错误")
        
        return app_config
    
    def _verify_secret(self, provided: str, stored: str) -> bool:
        """校验secret"""
        return hmac.compare_digest(provided, stored)

def create_auth_dependency(db_router: DatabaseRouter):
    """创建认证依赖"""
    async def verify(request: Request) -> dict:
        body = await request.json()
        app_id = body.get('app_id')
        app_secret = body.get('app_secret')
        
        if not app_id or not app_secret:
            raise HTTPException(status_code=400, detail="缺少appId或appSecret")
        
        auth = AuthMiddleware(db_router)
        return await auth.verify_request(app_id, app_secret)
    
    return verify
```

### 5.5 文档服务

```python
# app/services/document_service.py
from sqlalchemy import text
from .bge_service import bge_service

class DocumentService:
    def __init__(self, db_router):
        self.db = db_router
    
    def create_document(self, app_config: dict, title: str, content: str, 
                        tags: list = None, source: str = "manual") -> dict:
        """创建文档（自动分块、向量化）"""
        with self.db.get_connection(app_config) as conn:
            # 1. 插入文档
            result = conn.execute(text("""
                INSERT INTO documents (title, content, tags, source)
                VALUES (:title, :content, :tags, :source)
                RETURNING id
            """), {
                "title": title,
                "content": content,
                "tags": tags,
                "source": source
            })
            doc_id = result.fetchone()[0]
            
            # 2. 智能分块
            chunks = self._chunk_text(content)
            
            # 3. 向量化并存储
            vectors = bge_service.encode_texts(chunks)
            for i, (chunk, vec) in enumerate(zip(chunks, vectors['dense_vectors'])):
                conn.execute(text("""
                    INSERT INTO document_chunks 
                    (document_id, chunk_text, chunk_index, dense_vector)
                    VALUES (:doc_id, :chunk, :index, :vec)
                """), {
                    "doc_id": doc_id,
                    "chunk": chunk,
                    "index": i,
                    "vec": vec
                })
            
            conn.commit()
            return {"document_id": doc_id, "chunks_created": len(chunks), "title": title}
    
    def _chunk_text(self, text: str, chunk_size: int = 512) -> list:
        """智能分块（按段落）"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 简单按字符计数，实际可用tokenizer
}            if current_length + len(para) > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(para)
            current_length += len(para)
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks if chunks else [text]
    
    def list_documents(self, app_config: dict, page: int = 1, 
                       page_size: int = 10, tags: list = None) -> dict:
        """文档列表"""
        with self.db.get_connection(app_config) as conn:
            offset = (page - 1) * page_size
            
            # 查询总数
            count_sql = text("SELECT COUNT(*) FROM documents WHERE status = 'active'")
            total = conn.execute(count_sql).fetchone()[0]
            
            # 查询列表
            sql = text("""
                SELECT id, title, tags, source, created_at
                FROM documents 
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            rows = conn.execute(sql, {"limit": page_size, "offset": offset}).fetchall()
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "list": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "tags": r.tags,
                        "source": r.source,
                        "created_at": r.created_at.isoformat()
                    }
                    for r in rows
                ]
            }
    
    def get_document(self, app_config: dict, document_id: int) -> dict:
        """文档详情"""
        with self.db.get_connection(app_config) as conn:
            result = conn.execute(text("""
                SELECT id, title, content, tags, source, created_at
                FROM documents 
                WHERE id = :id AND status = 'active'
            """), {"id": document_id}).fetchone()
            
            if not result:
                return None
            
            return {
                "id": result.id,
                "title": result.title,
                "content": result.content,
                "tags": result.tags,
                "source": result.source,
                "created_at": result.created_at.isoformat()
            }
    
    def delete_document(self, app_config: dict, document_id: int) -> bool:
        """删除文档（级联删除向量）"""
        with self.db.get_connection(app_config) as conn:
            conn.execute(text("""
                UPDATE documents SET status = 'deleted' WHERE id = :id
            """), {"id": document_id})
            conn.commit()
            return True
```

### 5.6 知识检索服务

```python
# app/services/knowledge_service.py
from sqlalchemy import text
from .bge_service import bge_service

class KnowledgeService:
    def __init__(self, db_router):
        self.db = db_router
    
    def search(self, app_config: dict, query: str, top_k: int = 5, 
               filters: dict = None) -> dict:
        """语义搜索"""
        # 1. 查询向量化
        query_vector = bge_service.encode_query(query)
        
        with self.db.get_connection(app_config) as conn:
            # 2. 向量检索
            sql = text("""
                SELECT 
                    dc.chunk_text,
                    dc.document_id,
                    d.title as document_title,
                    1 - (dc.dense_vector <=> :query_vec) as similarity,
                    dc.chunk_index
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.status = 'active'
                ORDER BY dc.dense_vector <=> :query_vec
                LIMIT :top_k
            """)
            
            rows = conn.execute(sql, {
                "query_vec": query_vector,
                "top_k": top_k
            }).fetchall()
            
            results = []
            for r in rows:
                results.append({
                    "chunk_text": r.chunk_text,
                    "document_id": r.document_id,
                    "document_title": r.document_title,
                    "similarity_score": round(float(r.similarity), 4),
                    "chunk_index": r.chunk_index
                })
            
            return {
                "query": query,
                "total": len(results),
                "results": results
            }
    
    def chat(self, app_config: dict, query: str, top_k: int = 3) -> dict:
        """RAG问答"""
        # 1. 检索相关文档
        search_result = self.search(app_config, query, top_k)
        
        # 2. 构建上下文
        context = "\n\n".join([
            f"[文档{i+1}] {r['chunk_text']}"
            for i, r in enumerate(search_result['results'])
        ])
        
        # 3. 构建Prompt（这里可以接入LLM）
        prompt = f"""基于以下资料回答问题。如果资料中没有相关信息，请如实说明。

资料：
{context}

问题：{query}

回答："""
        
        # TODO: 调用LLM生成回答（当前返回检索结果）
        return {
            "answer": prompt,  # 实际应调用LLM
            "sources": search_result['results']
        }
```

---

## 六、部署方案

### 6.1 Docker配置

```dockerfile
# docker/Dockerfile
FROM python:3.9-slim-bookworm

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制模型缓存（提前下载）
COPY mod}COPY models/ ./models/

# 复制应用代码
COPY app/ ./app/

# 创建非root用户
RUN groupadd -g 1001 appgroup && \
    useradd -r -u 1001 -g appgroup appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Docker Compose

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  knowledge-rag:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - MASTER_DB_HOST=postgres-master
      - MASTER_DB_PORT=5432
      - MASTER_DB_USER=postgres
      - MASTER_DB_PASSWORD=your_password
      - MASTER_DB_NAME=knowledge_master
    volumes:
      - ./models:/app/models
    depends_on:
      - postgres-master
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: knowledge_master
    volumes:
      - postgres-master-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres-master-data:
```

### 6.3 环境变量

```bash
# .env.example
# 主数据库配置
MASTER_DB_HOST=localhost
MASTER_DB_PORT=5432
MASTER_DB_USER=postgres
MASTER_DB_PASSWORD=your_password
MASTER_DB_NAME=knowledge_master

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
APP_WORKERS=1

# 模型配置
MODEL_PATH=./models
```

### 6.4 资源规划

| 资源 | 最低配置 | 推荐配置 |
|------|----------|----------|
| 内存 | 4GB | 8GB |
| CPU | 2核 | 4核 |
| 磁盘 | 10GB | 50GB |

---

## 七、安全配置

### 7.1 应用创建流程

```python
# 创建应用的SQL
INSERT INTO apps (app_id, app_secret, app_name, db_name, db_host, db_port, db_user, db_password)
VALUES (
    'app_001',                           -- app_id (固定格式)
    'hmac:generated_secret_here',       -- app_secret (HMAC加密)
    'Team A知识库',                      -- app_name
    'knowledge_app_001',                -- db_name
    'localhost',                        -- db_host
    5432,                               -- db_port
    'postgres',                         -- db_user
    'encrypted_password'                -- db_password
);
```

### 7.2 新建项目数据库

```bash
# 创建独立数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"

# 初始化表结构
psql -h localhost -U postgres -d knowledge_app_001 -f migrations/init.sql
```

---

## 八、测试用例

### 8.1 认证测试

```python
# test_auth.py
def test_valid_credentials():
    response = client.post("/api/v1/document/list", json={
        "app_id": "app_001",
        "app_secret": "valid_secret",
        "data": {"page": 1, "page_size": 10}
    })
    assert response.status_code == 200

def test_invalid_app_id():
    response = client.post("/api/v1/document/list", json={
        "app_id": "invalid",
        "app_secret": "secret",
        "data": {}
    })
    assert response.status_code == 401

def test_invalid_secret():
    response = client.post("/api/v1/document/list", json={
        "app_id": "app_001",
        "app_secret": "wrong_secret",
        "data": {}
    })
    assert response.status_code == 401
```

### 8.2 文档测试

```python
# test_document.py
def test_create_document():
    response = client.post("/api/v1/document/create", json={
        "app_id": "app_001",
        "app_secret": "valid_secret",
        "data": {
            "title": "测试文档",
            "content": "这是测试内容" * 100,
            "tags": ["测试"]
        }
    })
    assert response.status_code == 200
    assert response.json()["data"]["document_id"] > 0

def test_search():
    response = client.post("/api/v1/knowledge/search", json={
        "app_id": "app_001",
        "app_secret": "valid_secret",
        "data": {
            "query": "测试查询",
            "top_k": 5
        }
    })
    assert response.status_code == 200
    assert "results" in response.json()["data"]
```

---

## 九、常见问题

### Q1: 首次请求很慢？
A: 模型首次加载需要20-30秒，之后会缓存。可以添加预热接口。

### Q2: 如何新增应用？
A: 在主库插入应用记录，然后创建对应的数据库并初始化表结构。

### Q3: 支持哪些文档格式？
A: 当前支持纯文本和Markdown。PDF/Word需要额外解析库。

### Q4: 如何备份数据？
A: 使用PostgreSQL的标准备份工具pg_dump，每个应用的数据库独立备份。
