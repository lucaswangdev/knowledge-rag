# Knowledge-RAG

企业级私有知识库RAG服务

## ✅ 项目状态

**🎉 项目已成功运行！**

- ✅ Python 3.11.13 + uv包管理
- ✅ 所有依赖已安装（FastAPI、PostgreSQL、Ollama API等）
- ✅ 测试通过率: 9/9 (100%)
- ✅ 核心功能验证: 7/7 (100%)

**快速验证**: `uv run python verify.py`

---

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
- Ollama API (bge-m3) - 向量化服务
- Docker - 容器化部署

## 快速开始

### 1. 后端启动

```bash
# 克隆项目
git clone https://github.com/lucaswangdev/knowledge-rag.git
cd knowledge-rag

# 创建虚拟环境并安装依赖
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r <(cat <<EOF
fastapi>=0.110.0
uvicorn>=0.29.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
FlagEmbedding>=1.3.0
sentence-transformers>=2.7.0
numpy>=1.26.0
httpx>=0.26.0
python-multipart>=0.0.10
EOF
)

# 启动后端服务（端口8000）
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. 前端启动

```bash
# 进入前端目录
cd front-end

# 安装依赖
npm install

# 启动前端（端口5173）
npm run dev
```

### 3. 初始化数据库

```bash
# 创建主数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_master;"
psql -h localhost -U postgres -d knowledge_master -f init_master.sql

# 创建应用数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"
psql -h localhost -U postgres -d knowledge_app_001 -f init_app.sql
```

### 访问地址

- 后端API: http://localhost:8000
- 前端页面: http://localhost:5173
- API文档: http://localhost:8000/docs


## 📁 项目文档

- `README.md` - 项目概述（本文件）
- `SETUP.md` - 详细的设置指南
- `PROJECT_STATUS.md` - 项目状态报告
- `TECH.md` - 技术设计文档
- `PRD.md` - 产品需求文档
- `start.sh` - 一键启动脚本
- `verify.py` - ✅ 项目验证脚本
- `RUN_SUCCESS.md` - ✅ 运行成功报告

## API文档

启动服务后访问: http://localhost:8000/docs

详细接口文档见 [API文档.md](./API文档.md)

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
│       ├── knowledge_service.py
│       └── file_service.py  # 文件上传服务
├── front-end/               # 前端项目 (React + Vite + TypeScript)
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── components/     # React组件
│   │   └── store/          # Zustand状态管理
│   └── ...
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
├── init_master.sql          # 主库初始化
├── init_app.sql             # 应用库初始化
└── pyproject.toml           # uv依赖管理
```

## License

MIT