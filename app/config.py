import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
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
    
    # 模型配置（保留兼容字段）
    model_path: str = "./models"
    model_name: str = "BAAI/bge-m3"
    use_fp16: bool = False
    device: str = "cpu"

    # Ollama 配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_embed_model: str = "bge-m3"
    
    # 向量配置
    vector_dimension: int = 1024
    chunk_size: int = 512
    default_top_k: int = 5
    
    @property
    def master_db_url(self) -> str:
        return f"postgresql://{self.master_db_user}:{self.master_db_password}@{self.master_db_host}:{self.master_db_port}/{self.master_db_name}"


settings = Settings()