"""Knowledge-RAG - 路由"""
import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.middleware.auth import get_app_config, AuthService
from app.services.db_service import AppConfig
from app.services.document_service import document_service
from app.services.knowledge_service import knowledge_service
from app.services.bge_service import bge3_service
from app.models.response import ApiResponse
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== 通用响应构建 ==========

def success_response(data=None, message: str = "success"):
    return ApiResponse(success=True, code=0, message=message, data=data)


def error_response(code: int, message: str):
    return JSONResponse(
        status_code=200,
        content={"success": False, "code": code, "message": message, "data": None}
    )


# ========== 应用相关 ==========

@router.post("/api/v1/app/info")
async def app_info(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """获取应用信息"""
    return success_response({
        "app_id": app_config.app_id,
        "app_name": app_config.app_name,
        "db_name": app_config.db_name,
        "status": app_config.status
    })


# ========== 文档管理 ==========

@router.post("/api/v1/document/create")
async def create_document(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """创建文档"""
    body = await request.json()
    data = body.get('data', {})
    
    try:
        result = document_service.create_document(
            app_config=app_config,
            title=data.get('title'),
            content=data.get('content'),
            tags=data.get('tags'),
            source=data.get('source', 'manual')
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"创建文档失败: {e}")
        return error_response(500, f"创建文档失败: {str(e)}")


@router.post("/api/v1/document/list")
async def list_documents(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """文档列表"""
    body = await request.json()
    data = body.get('data', {})
    
    try:
        result = document_service.list_documents(
            app_config=app_config,
            page=data.get('page', 1),
            page_size=data.get('page_size', 10),
            tags=data.get('tags')
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"查询文档列表失败: {e}")
        return error_response(500, f"查询失败: {str(e)}")


@router.post("/api/v1/document/get")
async def get_document(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """文档详情"""
    body = await request.json()
    data = body.get('data', {})
    
    try:
        result = document_service.get_document(
            app_config=app_config,
            document_id=data.get('document_id')
        )
        if not result:
            return error_response(404, "文档不存在")
        return success_response(result)
    except Exception as e:
        logger.error(f"查询文档失败: {e}")
        return error_response(500, f"查询失败: {str(e)}")


@router.post("/api/v1/document/delete")
async def delete_document(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """删除文档"""
    body = await request.json()
    data = body.get('data', {})
    
    try:
        document_service.delete_document(
            app_config=app_config,
            document_id=data.get('document_id')
        )
        return success_response(message="删除成功")
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        return error_response(500, f"删除失败: {str(e)}")


# ========== 知识检索 ==========

@router.post("/api/v1/knowledge/search")
async def knowledge_search(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """语义搜索"""
    body = await request.json()
    data = body.get('data', {})
    
    try:
        result = knowledge_service.search(
            app_config=app_config,
            query=data.get('query'),
            top_k=data.get('top_k', 5),
            filters=data.get('filters')
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return error_response(500, f"搜索失败: {str(e)}")


@router.post("/api/v1/knowledge/chat")
async def knowledge_chat(request: Request, app_config: AppConfig = Depends(get_app_config)):
    """RAG问答"""
    body = await request.json()
    data = body.get('data', {})
    
    try:
        result = knowledge_service.chat(
            app_config=app_config,
            query=data.get('query'),
            top_k=data.get('top_k', 3),
            session_id=data.get('session_id')
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"问答失败: {e}")
        return error_response(500, f"问答失败: {str(e)}")


# ========== 健康检查 ==========

@router.get("/health")
async def health_check():
    """健康检查"""
    return success_response({
        "status": "ok",
        "model_loaded": bge3_service.model is not None
    })


@router.get("/")
async def root():
    """根路径"""
    return success_response({
        "service": "knowledge-rag",
        "version": "1.0.0",
        "docs": "/docs"
    })