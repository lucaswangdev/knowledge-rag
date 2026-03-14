import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 主数据库配置
    master_db_host: str = "localhost"
    master_db_port: int = 5432
    master_db_user: str = "postgres"
    master_db_password: str = "postgres"
    master_db_name: str = "knowledge_master"
    
    # 应用配置
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_workers: int = 1
    
    # 模型配置
    model_path: str = "./models"
    model_name: str = "BAAI/bge-m3"
    use_fp16: bool = False
    device: str = "cpu"
    
    # 向量配置
    vector_dimension: int = 1024
    chunk_size: int = 512
    default_top_k: int = 5
    
    @property
    def master_db_url(self) -> str:
        return f"postgresql://{self.master_db_user}:{self.master_db_password}@{self.master_db_host}:{self.master_db_port}/{self.master_db_name}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()