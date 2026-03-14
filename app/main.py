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
    
    # 预加载模型（可选，懒加载也可以）
    # bge3_service.load_model(
    #     model_name=settings.model_name,
    #     use_fp16=settings.use_fp16,
    #     device=settings.device,
    #     cache_folder=settings.model_path
    # )
    
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