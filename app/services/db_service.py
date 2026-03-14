"""Knowledge-RAG - 数据库服务"""
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import Session

from app.config import settings

logger = logging.getLogger(__name__)


class AppConfig:
    """应用配置"""
    def __init__(self, app_id: str, app_secret: str, app_name: str,
                 db_name: str, db_host: str, db_port: int,
                 db_user: str, db_password: str, status: str = "active"):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_name = app_name
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.status = status
    
    @property
    def db_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class DatabaseRouter:
    """数据库路由器 - 根据appId路由到不同数据库"""
    
    def __init__(self):
        self._engines: Dict[str, Any] = {}
        self._master_engine = None
    
    def init_master(self):
        """初始化主数据库连接"""
        self._master_engine = create_engine(
            settings.master_db_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        logger.info(f"主数据库连接初始化: {settings.master_db_host}/{settings.master_db_name}")
    
    def get_app_config(self, app_id: str) -> Optional[AppConfig]:
        """从主库获取应用配置"""
        if self._master_engine is None:
            self.init_master()
            
        with self._master_engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT app_id, app_secret, app_name, db_name, 
                           db_host, db_port, db_user, db_password, status
                    FROM apps 
                    WHERE app_id = :app_id AND status = 'active'
                """),
                {"app_id": app_id}
            )
            row = result.fetchone()
            if not row:
                return None
            
            return AppConfig(
                app_id=row.app_id,
                app_secret=row.app_secret,
                app_name=row.app_name,
                db_name=row.db_name,
                db_host=row.db_host,
                db_port=row.db_port,
                db_user=row.db_user,
                db_password=row.db_password,
                status=row.status
            )
    
    def get_engine(self, app_config: AppConfig):
        """获取应用数据库引擎（带缓存）"""
        app_id = app_config.app_id
        if app_id not in self._engines:
            self._engines[app_id] = create_engine(
                app_config.db_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )
            logger.info(f"应用数据库连接初始化: {app_id} -> {app_config.db_name}")
        return self._engines[app_id]
    
    @contextmanager
    def get_connection(self, app_config: AppConfig):
        """获取应用数据库连接"""
        engine = self.get_engine(app_config)
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_master_connection(self):
        """获取主库连接"""
        if self._master_engine is None:
            self.init_master()
        conn = self._master_engine.connect()
        try:
            yield conn
        finally:
            conn.close()


# 全局实例
db_router = DatabaseRouter()