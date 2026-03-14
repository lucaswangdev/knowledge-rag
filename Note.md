# Knowledge-RAG 项目笔记

## 最新变更（2026-03-14）

### 向量化服务切换为 Ollama API
- 移除本地模型加载（FlagEmbedding / torch），改为调用 Ollama HTTP API
- `app/services/bge_service.py` 完全重写，通过 `httpx` 调用 `POST /api/embed`
- 新增配置项 `OLLAMA_BASE_URL`、`OLLAMA_EMBED_MODEL`（默认 `bge-m3`）
- 依赖从 14 个精简到 8 个，移除 torch / torchvision / flagembedding / sentence-transformers / transformers / numpy 共 62 个包

### Bug 修复
- `document_service.py`：`tags` 字段写入 PostgreSQL jsonb 时需 `json.dumps()` 序列化，否则报 `DatatypeMismatch` 错误

### 依赖清理
```toml
# 移除
torch==2.2.2
torchvision==0.17.2
flagembedding>=1.3.5
sentence-transformers>=5.3.0
transformers<5
numpy<2

# 保留核心依赖
fastapi / uvicorn / sqlalchemy / psycopg2-binary / pydantic / httpx
```

---

## 项目结构

```
knowledge-rag/
├── app/
│   ├── main.py                 # FastAPI 入口，启动时调用 bge3_service.load_model()
│   ├── config.py               # 配置（含 ollama_base_url / ollama_embed_model）
│   ├── router.py               # 路由
│   ├── middleware/auth.py      # 认证中间件（appId + appSecret）
│   ├── models/
│   │   ├── request.py
│   │   └── response.py
│   └── services/
│       ├── bge_service.py      # 向量化服务 → Ollama API
│       ├── db_service.py       # 数据库路由（多租户）
│       ├── document_service.py # 文档 CRUD + 分块向量化
│       └── knowledge_service.py# 语义搜索 + RAG 问答
├── tests/
│   ├── test_basic.py
│   └── test_api.py
├── init_master.sql             # 主库初始化
├── init_app.sql                # 应用库初始化
├── pyproject.toml              # uv 依赖管理
├── API文档.md                  # 接口文档
└── .env.example
```

---

## 环境要求

- Python 3.11+
- uv 包管理器
- PostgreSQL 15+ with pgvector
- Ollama（本地运行，需拉取 bge-m3 模型）

```bash
# 安装 Ollama 模型
ollama pull bge-m3

# 验证
curl http://localhost:11434/api/embed \
  -d '{"model": "bge-m3", "input": "测试"}'
```

---

## 启动方式

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp .env.example .env

# 3. 初始化数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_master;"
psql -h localhost -U postgres -d knowledge_master -f init_master.sql
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"
psql -h localhost -U postgres -d knowledge_app_001 -f init_app.sql

# 4. 启动服务
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 测试结果（9/9 通过）

| 测试项 | 状态 |
|--------|------|
| 模块导入 | ✅ |
| 配置加载 | ✅ |
| 文本分块 | ✅ |
| BGE 向量化服务 | ✅ |
| API 响应格式 | ✅ |
| 健康检查 | ✅ |
| 根路径 | ✅ |
| 缺少凭证 | ✅ |
| 无效 appId | ✅ |

---

## 语义搜索验证

| 查询 | Top1 结果 | 相似度 |
|------|-----------|--------|
| 创业公司怎么拿到第一笔钱？ | 如何进行天使轮融资 | 0.67 |
| 早期员工股权激励怎么做？ | 创业公司如何组建核心团队 | 0.67 |
| 怎么判断产品是否符合市场需求？ | 产品市场契合度PMF验证方法 | 0.66 |
