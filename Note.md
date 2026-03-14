项目总结
📁 项目结构
knowledge-rag/
├── app/
│   ├── main.py              # FastAPI入口
│   ├── config.py            # 配置
│   ├── router.py            # 路由
│   ├── middleware/auth.py   # 认证中间件
│   ├── models/
│   │   ├── request.py       # 请求模型
│   │   └── response.py      # 响应模型
│   └── services/
│       ├── bge_service.py   # 向量化服务(单例)
│       ├── db_service.py    # 数据库路由
│       ├── document_service.py
│       └── knowledge_service.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
│   ├── test_basic.py
│   └── test_api.py
├── init_master.sql          # 主库初始化
├── init_app.sql             # 应用库初始化
├── requirements.txt
├── README.md
├── PRD.md
└── TECH.md
✅ 测试结果
| 测试项        | 状态    |
| ---------- | ----- |
| 配置加载       | ✓ 通过  |
| 请求/响应模型    | ✓ 通过  |
| 向量服务       | ✓ 通过  |
| 文档服务       | ✓ 通过  |
| 知识服务       | ✓ 通过  |
| 文本分块       | ✓ 通过  |
| 向量化(1024维) | ✓ 通过  |
| API健康检查    | ✓ 200 |
| API根路径     | ✓ 200 |
| 认证校验       | ✓ 400 |
🚀 启动方式
# 1. 初始化数据库
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_master;"
psql -h localhost -U postgres -d knowledge_master -f init_master.sql
psql -h localhost -U postgres -c "CREATE DATABASE knowledge_app_001;"
psql -h localhost -U postgres -d knowledge_app_001 -f init_app.sql

# 2. 启动服务
cd knowledge-rag
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload