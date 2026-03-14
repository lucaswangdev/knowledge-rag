"""Knowledge-RAG - 请求/响应模型"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ========== 通用模型 ==========

class ApiRequest(BaseModel):
    """通用API请求"""
    app_id: str = Field(..., description="应用ID")
    app_secret: str = Field(..., description="应用密钥")
    request_id: Optional[str] = Field(None, description="请求ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="业务数据")


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool = True
    code: int = 0
    message: str = "success"
    data: Any = None


# ========== 应用相关 ==========

class AppInfoRequest(BaseModel):
    """获取应用信息请求"""
    pass


class AppInfoResponse(BaseModel):
    """应用信息响应"""
    app_id: str
    app_name: str
    db_name: str
    status: str


# ========== 文档相关 ==========

class DocumentCreateRequest(BaseModel):
    """创建文档请求"""
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    tags: Optional[List[str]] = Field(None, description="标签")
    source: str = Field("manual", description="来源")


class DocumentListRequest(BaseModel):
    """文档列表请求"""
    page: int = Field(1, description="页码")
    page_size: int = Field(10, description="每页数量")
    tags: Optional[List[str]] = Field(None, description="标签筛选")


class DocumentGetRequest(BaseModel):
    """文档详情请求"""
    document_id: int = Field(..., description="文档ID")


class DocumentDeleteRequest(BaseModel):
    """删除文档请求"""
    document_id: int = Field(..., description="文档ID")


# ========== 知识检索相关 ==========

class KnowledgeSearchRequest(BaseModel):
    """语义搜索请求"""
    query: str = Field(..., description="查询内容")
    top_k: int = Field(5, description="返回数量")
    filters: Optional[Dict] = Field(None, description="筛选条件")


class KnowledgeChatRequest(BaseModel):
    """RAG问答请求"""
    query: str = Field(..., description="问题内容")
    top_k: int = Field(3, description="参考文档数量")
    session_id: Optional[int] = Field(None, description="会话ID")