"""Knowledge-RAG - 向量化服务（单例模式）"""
import logging
import threading
from typing import List, Dict, Any

try:
    from FlagEmbedding import BGEM3FlagModel
except ImportError:
    BGEM3FlagModel = None

logger = logging.getLogger(__name__)


class BGE3Service:
    """BGE-M3向量化服务（单例模式）"""
    
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
            self.model = None
            BGE3Service._initialized = True
    
    def load_model(self, model_name: str = "BAAI/bge-m3", 
                   use_fp16: bool = False, 
                   device: str = "cpu",
                   cache_folder: str = "./models"):
        """加载模型"""
        if self.model is not None:
            logger.info("模型已加载")
            return
        
        if BGEM3FlagModel is None:
            logger.warning("FlagEmbedding未安装，使用模拟模型")
            self.model = None
            return
            
        logger.info(f"正在加载BGE-M3模型: {model_name}")
        try:
            self.model = BGEM3FlagModel(
                model_name,
                use_fp16=use_fp16,
                device=device,
                cache_folder=cache_folder
            )
            logger.info("BGE-M3模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            self.model = None
    
    def encode_texts(self, texts: List[str], 
                     return_dense: bool = True,
                     return_sparse: bool = False) -> Dict[str, Any]:
        """批量文本向量化"""
        if self.model is None:
            # 返回模拟向量（用于测试）
            return {
                "dense_vecs": [[0.1] * 1024 for _ in texts],
                "lexical_weights": [{} for _ in texts]
            }
        
        result = self.model.encode(
            texts,
            return_dense=return_dense,
            return_sparse=return_sparse,
            return_colbert_vecs=False
        )
        
        output = {}
        if return_dense:
            output['dense_vecs'] = result['dense_vecs']
        if return_sparse:
            output['lexical_weights'] = result['lexical_weights']
        return output
    
    def encode_query(self, query: str) -> List[float]:
        """单个查询向量化"""
        if self.model is None:
            # 返回模拟向量
            return [0.1] * 1024
            
        result = self.model.encode([query])
        return result['dense_vecs'][0].tolist()
    
    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """计算两段文本相似度"""
        if self.model is None:
            return 0.5
            
        import numpy as np
        embeddings = self.model.encode([text_a, text_b])
        vec_a = embeddings['dense_vecs'][0]
        vec_b = embeddings['dense_vecs'][1]
        return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))


# 全局单例
bge3_service = BGE3Service()