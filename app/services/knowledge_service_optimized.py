"""
知识检索服务 - 带去重优化版本

优化点：
1. 对检索结果按文档去重，只保留每个文档的最佳chunk
2. 提升Precision指标
"""
import logging
from typing import Dict, Any, List, Optional

from sqlalchemy import text

from app.services.db_service import AppConfig, db_router
from app.services.bge_service import bge3_service
from app.config import settings

logger = logging.getLogger(__name__)


class KnowledgeServiceOptimized:
    """知识检索服务（优化版）"""

    def __init__(self):
        pass

    def search(self, app_config: AppConfig, query: str,
               top_k: int = None, deduplicate: bool = True) -> Dict[str, Any]:
        """
        语义搜索

        Args:
            app_config: 应用配置
            query: 查询文本
            top_k: 返回数量
            deduplicate: 是否去重（按文档，只保留每个文档的最佳chunk）
        """
        if top_k is None:
            top_k = settings.default_top_k

        # 1. 查询向量化
        query_vector = bge3_service.encode_query(query)
        query_vec_str = '[' + ','.join(str(float(v)) for v in query_vector) + ']'

        # 2. 如果需要去重，先检索更多结果
        fetch_k = top_k * 3 if deduplicate else top_k

        with db_router.get_connection(app_config) as conn:
            # 3. 向量检索
            sql = text("""
                SELECT
                    dc.chunk_text,
                    dc.document_id,
                    d.title as document_title,
                    1 - (dc.dense_vector <=> CAST(:query_vec AS vector)) as similarity,
                    dc.chunk_index
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE d.status = 'active'
                ORDER BY dc.dense_vector <=> CAST(:query_vec AS vector)
                LIMIT :fetch_k
            """)

            rows = conn.execute(sql, {
                "query_vec": query_vec_str,
                "fetch_k": fetch_k
            }).fetchall()

            results = []
            for r in rows:
                results.append({
                    "chunk_text": r.chunk_text,
                    "document_id": r.document_id,
                    "document_title": r.document_title,
                    "similarity_score": round(float(r.similarity), 4),
                    "chunk_index": r.chunk_index
                })

            # 4. 去重：每个文档只保留最佳chunk
            if deduplicate and results:
                seen_docs = set()
                dedup_results = []
                for result in results:
                    doc_id = result['document_id']
                    if doc_id not in seen_docs:
                        seen_docs.add(doc_id)
                        dedup_results.append(result)
                        if len(dedup_results) >= top_k:
                            break
                results = dedup_results

            logger.info(f"搜索完成: query={query}, results={len(results)}, deduplicate={deduplicate}")
            return {
                "query": query,
                "total": len(results),
                "results": results,
                "deduplicated": deduplicate
            }

    def chat(self, app_config: AppConfig, query: str,
             top_k: int = 3, session_id: int = None) -> Dict[str, Any]:
        """RAG问答"""
        # 1. 检索相关文档（使用去重）
        search_result = self.search(app_config, query, top_k, deduplicate=True)

        if not search_result['results']:
            return {
                "answer": "抱歉，知识库中没有找到相关信息。",
                "sources": []
            }

        # 2. 构建上下文
        context_parts = []
        for i, r in enumerate(search_result['results']):
            context_parts.append(f"[文档{i+1}]: {r['chunk_text']}")
        context = "\n\n".join(context_parts)

        # 3. 构建Prompt（这里可以接入LLM）
        prompt = f"""基于以下资料回答问题。

资料：
{context}

问题：{query}

请根据资料给出回答："""

        # 返回模拟回答（实际应调用LLM）
        answer = self._generate_answer(prompt, search_result['results'])

        return {
            "answer": answer,
            "sources": search_result['results']
        }

    def _generate_answer(self, prompt: str, sources: List[Dict]) -> str:
        """生成回答（TODO: 接入LLM）"""
        # 这里应该调用LLM API
        # 目前返回基于检索结果的摘要
        if sources:
            best_match = sources[0]
            return f"根据检索到的资料，您询问的内容与「{best_match['document_title']}」相关度最高。\n\n参考内容：{best_match['chunk_text'][:200]}..."
        return "抱歉，无法找到相关信息。"


# 全局实例
knowledge_service_optimized = KnowledgeServiceOptimized()
