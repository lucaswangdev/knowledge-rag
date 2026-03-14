"""Knowledge-RAG - 向量化服务（基于 Ollama API）"""
import logging
import threading
from typing import List, Dict, Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class BGE3Service:
    """BGE-M3 向量化服务（单例模式，调用 Ollama API）"""

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not BGE3Service._initialized:
            self.model = True  # 标记为"已就绪"，兼容 health check
            BGE3Service._initialized = True

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _embed(self, inputs: List[str]) -> List[List[float]]:
        """调用 Ollama embed API，返回向量列表"""
        url = f"{settings.ollama_base_url}/api/embed"
        payload = {"model": settings.ollama_embed_model, "input": inputs}
        try:
            resp = httpx.post(url, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()["embeddings"]
        except Exception as e:
            logger.error(f"Ollama embed 调用失败: {e}")
            raise

    # ------------------------------------------------------------------
    # 公开接口（保持与原来一致）
    # ------------------------------------------------------------------

    def load_model(self, **kwargs):
        """兼容旧接口，Ollama 模式无需加载模型"""
        logger.info(f"使用 Ollama 向量化服务: {settings.ollama_base_url} / {settings.ollama_embed_model}")

    def encode_texts(self, texts: List[str],
                     return_dense: bool = True,
                     return_sparse: bool = False) -> Dict[str, Any]:
        """批量文本向量化"""
        vecs = self._embed(texts)
        return {"dense_vecs": vecs}

    def encode_query(self, query: str) -> List[float]:
        """单个查询向量化"""
        return self._embed([query])[0]

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """计算余弦相似度"""
        import numpy as np
        vecs = self._embed([text_a, text_b])
        a, b = np.array(vecs[0]), np.array(vecs[1])
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# 全局单例
bge3_service = BGE3Service()
