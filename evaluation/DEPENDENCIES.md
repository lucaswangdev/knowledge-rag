# 向量检索评估依赖安装指南

## 使用 uv 安装（推荐）

```bash
# 安装必需依赖
uv pip install numpy pydantic-settings psycopg2-binary

# 或者一次性安装所有依赖
uv pip install numpy pydantic-settings psycopg2-binary sqlalchemy httpx
```

## 使用 pip 安装

```bash
# 安装必需依赖
pip install numpy pydantic-settings psycopg2-binary

# 或者一次性安装所有依赖
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

# 运行评估脚本
python evaluation/evaluate_retrieval.py
```

## 常见问题

### Q: 提示找不到模块？
A: 确保已安装所有依赖，并在项目根目录运行

### Q: 数据库连接失败？
A: 确保PostgreSQL服务已启动，数据库已初始化

### Q: 首次查询很慢？
A: 这是正常的（冷启动），后续查询会很快（~250ms）
