# Knowledge-RAG

企业级私有知识库RAG服务

## ✅ 项目状态

**🎉 项目已成功运行！**

- ✅ Python 3.11.13 + uv包管理
- ✅ 所有依赖已安装（torch 2.2.2, FlagEmbedding, FastAPI等）
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
- FlagEmbedding (bge-m3) - 向量化模型
- Docker - 容器化部署

## 快速开始

### 使用uv快速启动（推荐）

```bash
# 1. 安装uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone https://github.com/your-repo/knowledge-rag.git
cd knowledge-rag

# 3. 一键启动（自动安装依赖、运行测试、启动服务）
./start.sh

# 或手动启动
uv sync                    # 安装依赖
uv run pytest tests/ -v    # 运行测试
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 传统方式启动

```bash
# 1. 配置环境
cp .env.example .env
# 编辑 .env 配置数据库连接

# 2. 使用Docker
docker-compose up -d

# 或本地开发
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 初始化数据库

```bash
# 创建主数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_master;"

# 执行初始化SQL
psql -h localhost -U postgres -d knowledge_master -f init_master.sql

# 创建应用数据库（示例）
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"
psql -h localhost -U postgres -d knowledge_app_001 -f init_app.sql
```

## 🔑 关键技术决策

- **Python 3.11**: torch 2.2.2不支持Python 3.12
- **torch 2.2.2**: 最后支持macOS x86_64 (Intel Mac)的版本
- **numpy<2**: 兼容torch 2.2.2
- **transformers<5**: 兼容torch 2.2.2
- **uv包管理**: 现代化的Python包管理器，速度快、依赖解析准确

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