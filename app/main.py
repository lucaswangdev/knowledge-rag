"""Knowledge-RAG - FastAPI主入口"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import router
from app.services.bge_service import bge3_service
from app.services.db_service import db_router
from app.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info("Knowledge-RAG 启动中...")

    # 初始化主数据库连接
    db_router.init_master()

    # 加载BGE-M3模型
    bge3_service.load_model(
        model_name=settings.model_name,
        use_fp16=settings.use_fp16,
        device=settings.device,
        cache_folder=settings.model_path
    )

    # 预热：执行一次向量编码
    try:
        logger.info("🔥 预热向量模型...")
        _ = bge3_service.encode_query("预热测试查询")
        logger.info("✅ 向量模型预热完成")
    except Exception as e:
        logger.warning(f"⚠️  向量模型预热失败: {e}")

    # 预热：预热数据库连接和向量索引
    try:
        logger.info("🔥 预热数据库连接和向量索引...")
        app_config = db_router.get_app_config("app_001")
        from app.services.knowledge_service import knowledge_service
        # 执行一次空查询，预热HNSW索引
        knowledge_service.search(app_config, "预热查询", top_k=5)
        logger.info("✅ 数据库和索引预热完成")
    except Exception as e:
        logger.warning(f"⚠️  数据库预热失败: {e}")

    logger.info("Knowledge-RAG 启动完成")
    logger.info("=" * 50)

    yield

    # 关闭时
    logger.info("Knowledge-RAG 关闭")


# 创建FastAPI应用
app = FastAPI(
    title="Knowledge-RAG",
    description="企业级私有知识库RAG服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )