# Knowledge-RAG 快速开始指南

## 📋 项目概述

**Knowledge-RAG** 是一个企业级私有知识库RAG服务，基于 bge-m3 向量模型和 PostgreSQL + pgvector 实现语义搜索和智能问答。

**核心特性：**
- 🔐 多租户物理隔离（每个应用独立数据库）
- 🔍 语义搜索（基于 bge-m3 深度语义理解）
- 💬 智能问答（RAG 架构，支持引用来源）
- 📁 文件上传（支持 Markdown/TXT 文件）
- 🚀 快速部署（Docker 一键部署）

---

## ✅ 项目状态

**最新更新：** 2026-03-14
**测试状态：** ✅ 9/9 通过 (100%)
**评估状态：** ✅ 向量检索质量评估完成

### 核心指标
- **Recall@5**: 95.0% （优秀）
- **MRR**: 0.956 （优秀）
- **P50 响应时间**: 250ms
- **向量模型**: bge-m3 (1024维) via Ollama API

---

## 🚀 快速开始

### 前置要求

- **Python**: 3.11+ （⚠️ 不支持 3.12+，因向量模型兼容性）
- **uv**: 0.9.28+ （Python 包管理器）
- **PostgreSQL**: 15+ with pgvector 扩展
- **Ollama**: 本地运行，需拉取 bge-m3 模型

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 2. 克隆项目并安装依赖

```bash
git clone https://github.com/lucaswangdev/knowledge-rag.git
cd knowledge-rag

# uv 会自动创建虚拟环境并安装所有依赖
uv sync
```

### 3. 安装 Ollama 并拉取模型

```bash
# 安装 Ollama（访问 https://ollama.com）

# 拉取 bge-m3 模型
ollama pull bge-m3

# 验证模型
curl http://localhost:11434/api/embed \
  -d '{"model": "bge-m3", "input": "测试"}'
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库连接
vim .env
```

**必需配置项：**
```bash
# 主数据库配置
MASTER_DB_HOST=localhost
MASTER_DB_PORT=5432
MASTER_DB_USER=postgres
MASTER_DB_PASSWORD=your_password
MASTER_DB_NAME=knowledge_master

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=bge-m3
```

### 5. 初始化数据库

```bash
# 创建主数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_master;"
psql -h localhost -U postgres -d knowledge_master -f init_master.sql

# 创建应用数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"
psql -h localhost -U postgres -d knowledge_app_001 -f init_app.sql
```

### 6. 启动服务

**方式1：使用启动脚本（推荐）**
```bash
./start.sh
```

**方式2：使用 uv run**
```bash
# 开发模式（自动重载）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**方式3：激活虚拟环境后运行**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 访问服务

启动成功后访问：
- **前端页面**: http://localhost:5173 （需单独启动前端）
- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 🧪 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行向量检索质量评估
uv run python evaluation/evaluate_retrieval.py
```

---

## 📁 项目结构

```
knowledge-rag/
├── app/                         # 后端应用
│   ├── main.py                 # FastAPI 入口
│   ├── config.py               # 配置管理
│   ├── router.py               # 路由定义
│   ├── middleware/             # 中间件
│   │   └── auth.py            # 认证中间件
│   ├── models/                 # 数据模型
│   │   ├── request.py
│   │   └── response.py
│   └── services/               # 业务服务
│       ├── bge_service.py      # 向量化服务（Ollama API）
│       ├── db_service.py       # 数据库服务
│       ├── document_service.py # 文档服务
│       ├── knowledge_service.py# 知识检索服务
│       └── file_service.py     # 文件上传服务
│
├── front-end/                   # 前端应用（React + Vite + TypeScript）
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── components/         # React 组件
│   │   └── store/              # Zustand 状态管理
│   └── ...
│
├── evaluation/                  # 向量检索质量评估
│   ├── evaluate_retrieval.py   # 评估脚本
│   ├── test_cases.json         # 测试用例
│   └── reports/                # 评估报告
│
├── docs/                        # 文档
│   ├── database-design-analysis.md
│   └── retrieval-quality-evaluation.md
│
├── tests/                       # 测试文件
│   ├── test_basic.py
│   └── test_api.py
│
├── init_master.sql              # 主数据库初始化
├── init_app.sql                 # 应用数据库初始化
├── DATABASE.md                  # 数据库设计文档
├── README.md                    # 项目说明
├── pyproject.toml               # uv 项目配置
├── .env.example                 # 环境变量模板
└── start.sh                     # 一键启动脚本
```

---

## 🔧 技术栈

### 后端
- **框架**: FastAPI 0.135.1+
- **数据库**: PostgreSQL 15+ with pgvector
- **ORM**: SQLAlchemy 2.0+
- **向量化**: Ollama API (bge-m3模型)
- **包管理**: uv 0.9.28+

### 前端
- **框架**: React + Vite
- **语言**: TypeScript
- **状态管理**: Zustand
- **样式**: Tailwind CSS

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Uvicorn

---

## 📦 常用 uv 命令

```bash
# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 更新依赖
uv sync --upgrade

# 运行 Python 脚本
uv run python script.py

# 运行任意命令
uv run <command>

# 激活虚拟环境（可选）
source .venv/bin/activate
```

---

## 🎯 核心功能

### 1. 文档管理
- ✅ 文本文档创建
- ✅ Markdown 文件上传
- ✅ 文档列表查询
- ✅ 文档删除
- ✅ 自动文本分块
- ✅ 自动向量化

### 2. 语义搜索
- ✅ 向量相似度检索
- ✅ Top-K 结果排序
- ✅ 相似度分数展示
- ✅ HNSW 索引加速

### 3. RAG 问答
- ✅ 基于检索结果的问答
- ✅ 引用来源追溯
- ⚠️  LLM 集成（待实现）

### 4. 多租户支持
- ✅ 应用级隔离
- ✅ 独立数据库
- ✅ app_id/app_secret 认证

---

## 📊 性能指标

### 检索质量（基于20个测试用例）
| 指标 | 当前值 | 评级 |
|------|--------|------|
| Recall@5 | 95.0% | 🟢 优秀 |
| Precision@3 | 41.67% | 🟡 合格 |
| MRR | 0.956 | 🟢 优秀 |
| NDCG@5 | 0.986 | 🟢 优秀 |

### 性能表现
- **平均响应时间**: 250ms
- **P50 响应时间**: 250ms
- **P95 响应时间**: 298ms
- **向量编码**: ~50-100ms
- **数据库查询**: ~20-50ms

---

## 🔍 关键变更历史

### 2026-03-14 - 向量化服务优化
- ✅ 切换为 Ollama API（移除本地模型加载）
- ✅ 移除 torch/torchvision/FlagEmbedding 等62个依赖包
- ✅ 依赖从14个精简到8个
- ✅ 修复 tags 字段 JSONB 序列化问题

### 2026-03-14 - 文件上传功能
- ✅ 新增 /api/v1/document/upload 接口
- ✅ 支持 Markdown/TXT 文件上传
- ✅ 自动文本提取和向量化
- ✅ 文件存储到 storage/ 目录

### 2026-03-14 - 向量检索评估
- ✅ 建立评估体系（8大核心指标）
- ✅ 完成首次评估（20个测试用例）
- ✅ 添加应用启动预热
- ✅ 创建去重优化版检索服务

---

## 🐛 故障排除

### 问题1: Ollama 连接失败
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 重启 Ollama
ollama serve
```

### 问题2: 数据库连接失败
```bash
# 检查 PostgreSQL 服务
pg_isready -h localhost -p 5432

# 检查数据库是否存在
psql -h localhost -U postgres -l | grep knowledge
```

### 问题3: 向量模型加载失败
```bash
# 重新拉取模型
ollama pull bge-m3

# 测试模型
ollama run bge-m3
```

### 问题4: 依赖安装失败
```bash
# 清理并重新安装
rm -rf .venv uv.lock
uv sync
```

---

## 📚 相关文档

- **README.md** - 项目概述
- **DATABASE.md** - 数据库设计详解
- **docs/database-design-analysis.md** - 两表vs单表设计分析
- **docs/retrieval-quality-evaluation.md** - 完整评估框架
- **evaluation/EVALUATION_REPORT.md** - 评估结果报告
- **evaluation/OPTIMIZATION_SUMMARY.md** - 优化总结

---

## 🤝 前端项目启动

```bash
# 进入前端目录
cd front-end

# 安装依赖
npm install

# 启动开发服务器（端口5173）
npm run dev
```

访问：http://localhost:5173

---

## 📝 环境变量说明

```bash
# 主数据库配置
MASTER_DB_HOST=localhost          # 数据库主机
MASTER_DB_PORT=5432               # 数据库端口
MASTER_DB_USER=postgres           # 数据库用户
MASTER_DB_PASSWORD=postgres       # 数据库密码
MASTER_DB_NAME=knowledge_master   # 主数据库名

# 应用配置
APP_HOST=0.0.0.0                  # 服务监听地址
APP_PORT=8000                     # 服务端口
APP_WORKERS=1                     # 工作进程数

# Ollama 配置（向量化服务）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=bge-m3

# 向量配置
VECTOR_DIMENSION=1024             # 向量维度
CHUNK_SIZE=512                    # 分块大小
DEFAULT_TOP_K=5                   # 默认返回数量
```

---

## 🎉 总结

Knowledge-RAG 是一个生产就绪的企业级 RAG 服务，具备：

- ✅ **高召回率**（95%）- 几乎找到所有相关信息
- ✅ **快速响应**（250ms）- 满足实时查询需求
- ✅ **多租户支持** - 物理隔离，安全可靠
- ✅ **完整测试** - 100% 测试通过
- ✅ **现代化架构** - uv 包管理，FastAPI 框架

**立即开始使用吧！** 🚀

---

*最后更新: 2026-03-14*
