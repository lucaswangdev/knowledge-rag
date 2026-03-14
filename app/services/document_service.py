"""Knowledge-RAG - 文档服务"""
import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import text

from app.services.db_service import AppConfig, db_router
from app.services.bge_service import bge3_service
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """文档服务"""
    
    def __init__(self):
        pass
    
    def create_document(self, app_config: AppConfig, title: str, content: str, 
                        tags: List[str] = None, source: str = "manual") -> Dict[str, Any]:
        """创建文档（自动分块、向量化）"""
        with db_router.get_connection(app_config) as conn:
            # 1. 插入文档
            result = conn.execute(text("""
                INSERT INTO documents (title, content, tags, source)
                VALUES (:title, :content, :tags, :source)
                RETURNING id, created_at
            """), {
                "title": title,
                "content": content,
                "tags": json.dumps(tags) if tags is not None else None,
                "source": source
            })
            row = result.fetchone()
            doc_id = row.id
            created_at = row.created_at
            
            # 2. 智能分块
            chunks = self._chunk_text(content)
            
            # 3. 向量化并存储
            vectors = bge3_service.encode_texts(chunks)
            dense_vecs = vectors.get('dense_vecs', [])
            
            for i, chunk in enumerate(chunks):
                vec = dense_vecs[i] if i < len(dense_vecs) else [0.0] * settings.vector_dimension
                conn.execute(text("""
                    INSERT INTO document_chunks 
                    (document_id, chunk_text, chunk_index, dense_vector)
                    VALUES (:doc_id, :chunk, :index, :vec)
                """), {
                    "doc_id": doc_id,
                    "chunk": chunk,
                    "index": i,
                    "vec": vec
                })
            
            conn.commit()
            logger.info(f"文档创建成功: doc_id={doc_id}, chunks={len(chunks)}")
            return {
                "document_id": doc_id,
                "chunks_created": len(chunks),
                "title": title,
                "created_at": created_at.isoformat() if created_at else None
            }
    
    def _chunk_text(self, text: str, chunk_size: int = None) -> List[str]:
        """智能分块（按段落）"""
        if chunk_size is None:
            chunk_size = settings.chunk_size
            
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if current_length + len(para) > chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(para)
            current_length += len(para)
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks if chunks else [text]
    
    def list_documents(self, app_config: AppConfig, page: int = 1, 
                       page_size: int = 10, tags: List[str] = None) -> Dict[str, Any]:
        """文档列表"""
        with db_router.get_connection(app_config) as conn:
            offset = (page - 1) * page_size
            
            # 查询总数
            count_result = conn.execute(
                text("SELECT COUNT(*) FROM documents WHERE status = 'active'")
            )
            total = count_result.fetchone()[0]
            
            # 查询列表
            sql = text("""
                SELECT id, title, tags, source, created_at
                FROM documents 
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """)
            rows = conn.execute(sql, {"limit": page_size, "offset": offset}).fetchall()
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "list": [
                    {
                        "id": r.id,
                        "title": r.title,
                        "tags": r.tags,
                        "source": r.source,
                        "created_at": r.created_at.isoformat() if r.created_at else None
                    }
                    for r in rows
                ]
            }
    
    def get_document(self, app_config: AppConfig, document_id: int) -> Optional[Dict[str, Any]]:
        """文档详情"""
        with db_router.get_connection(app_config) as conn:
            result = conn.execute(text("""
                SELECT id, title, content, tags, source, created_at
                FROM documents 
                WHERE id = :id AND status = 'active'
            """), {"id": document_id}).fetchone()
            
            if not result:
                return None
            
            return {
                "id": result.id,
                "title": result.title,
                "content": result.content,
                "tags": result.tags,
                "source": result.source,
                "created_at": result.created_at.isoformat() if result.created_at else None
            }
    
    def delete_document(self, app_config: AppConfig, document_id: int) -> bool:
        """删除文档（软删除）"""
        with db_router.get_connection(app_config) as conn:
            conn.execute(text("""
                UPDATE documents SET status = 'deleted' WHERE id = :id
            """), {"id": document_id})
            conn.commit()
            logger.info(f"文档删除: doc_id={document_id}")
            return True


# 全局实例
document_service = DocumentService()