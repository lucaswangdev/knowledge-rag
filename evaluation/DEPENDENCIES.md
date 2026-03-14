# 向量检索评估依赖安装指南

## 使用 uv 安装（推荐）

```bash
# 方式1：使用 uv pip（推荐）
uv pip install numpy pydantic-settings psycopg2-binary sqlalchemy httpx

# 方式2：使用 uv add（如果是 uv 项目）
uv add numpy pydantic-settings psycopg2-binary sqlalchemy httpx

# 方式3：单独安装每个依赖
uv pip install numpy
uv pip install pydantic-settings
uv pip install psycopg2-binary
uv pip install sqlalchemy
uv pip install httpx
```

## 使用 pip 安装（备选）

```bash
# 一次性安装所有依赖
pip install numpy pydantic-settings psycopg2-binary sqlalchemy httpx
```

## 依赖说明

- **numpy**: 用于评估指标计算（Recall、Precision、NDCG等）
- **pydantic-settings**: 配置管理（项目依赖）
- **psycopg2-binary**: PostgreSQL数据库连接（项目依赖）
- **sqlalchemy**: ORM框架（项目依赖）
- **httpx**: HTTP客户端（项目依赖）

## 运行评估

```bash
# 确保在项目根目录
cd /path/to/knowledge-rag

# 使用 uv run 运行（推荐）
uv run python evaluation/evaluate_retrieval.py

# 或者直接运行
python evaluation/evaluate_retrieval.py
```

## 常见问题

### Q: 提示找不到模块？
A: 确保已安装所有依赖，并在项目根目录运行

### Q: 数据库连接失败？
A: 确保PostgreSQL服务已启动，数据库已初始化

### Q: 首次查询很慢？
A: 这是正常的（冷启动），后续查询会很快（~250ms）
