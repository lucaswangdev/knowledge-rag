# Knowledge-RAG 项目设置指南

## 环境要求

- Python 3.11+
- uv (Python包管理器)
- PostgreSQL 15+ (带pgvector扩展)

## 使用uv快速开始

### 1. 安装uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用pip
pip install uv
```

### 2. 克隆项目并设置环境

```bash
git clone <your-repo-url>
cd knowledge-rag

# uv会自动创建虚拟环境并安装依赖
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，配置数据库连接信息
```

### 4. 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试文件
uv run pytest tests/test_basic.py -v
```

### 5. 启动开发服务器

```bash
# 使用uvicorn启动
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用Python直接运行
uv run python -m app.main
```

### 6. 访问API文档

启动服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 常用uv命令

```bash
# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 更新依赖
uv sync --upgrade

# 运行Python脚本
uv run python script.py

# 运行任意命令
uv run <command>

# 激活虚拟环境（可选）
source .venv/bin/activate
```

## 项目结构

```
knowledge-rag/
├── app/                    # 应用代码
│   ├── main.py            # FastAPI入口
│   ├── config.py          # 配置管理
│   ├── router.py          # 路由定义
│   ├── middleware/        # 中间件
│   ├── models/            # 数据模型
│   └── services/          # 业务服务
├── tests/                 # 测试文件
├── pyproject.toml         # 项目配置和依赖
├── .env                   # 环境变量
└── README.md              # 项目说明
```

## 依赖说明

### 核心依赖
- **FastAPI**: Web框架
- **torch 2.2.2**: PyTorch (最后支持macOS x86_64的版本)
- **FlagEmbedding**: BGE-M3向量模型
- **sentence-transformers**: 句子向量化
- **SQLAlchemy**: ORM
- **psycopg2-binary**: PostgreSQL驱动
- **numpy<2**: 数值计算 (兼容torch 2.2.2)
- **transformers<5**: Hugging Face模型库 (兼容torch 2.2.2)

### 开发依赖
- **pytest**: 测试框架
- **pytest-asyncio**: 异步测试支持

## 注意事项

1. **Python版本**: 项目使用Python 3.11，因为torch 2.2.2不支持Python 3.12
2. **macOS x86_64**: torch 2.3+不再支持Intel Mac，所以使用2.2.2版本
3. **numpy版本**: 必须使用numpy<2以兼容torch 2.2.2
4. **数据库**: 需要PostgreSQL并安装pgvector扩展

## 故障排除

### 问题: torch安装失败
```bash
# 确保使用Python 3.11
uv venv --python 3.11
uv sync
```

### 问题: 测试失败
```bash
# 清理并重新安装
rm -rf .venv
uv sync
uv run pytest tests/ -v
```

### 问题: 导入错误
```bash
# 确保在项目根目录
cd knowledge-rag
uv run python -c "from app.main import app; print('OK')"
```
