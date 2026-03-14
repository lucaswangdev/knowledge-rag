"""Knowledge-RAG - 响应模型"""
from typing import Any, List, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool = True
    code: int = 0
    message: str = "success"
    data: Any = None


class DocumentCreateResponse(BaseModel):
    """创建文档响应"""
    document_id: int
    chunks_created: int
    title: str


class SearchResultItem(BaseModel):
    """搜索结果项"""
    chunk_text: str
    document_id: int
    document_title: str
    similarity_score: float
    chunk_index: int


class KnowledgeSearchResponse(BaseModel):
    """语义搜索响应"""
    query: str
    total: int
    results: List[SearchResultItem]


class ChatSourceItem(BaseModel):
    """问答来源项"""
    document_id: int
    chunk_text: str
    similarity_score: float


class KnowledgeChatResponse(BaseModel):
    """RAG问答响应"""
    answer: str
    sources: List[ChatSourceItem]