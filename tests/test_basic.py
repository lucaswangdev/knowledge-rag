"""Knowledge-RAG - 测试"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import():
    """测试模块导入"""
    from app.config import settings
    from app.services.bge_service import bge3_service
    from app.services.db_service import db_router
    assert settings is not None
    assert bge3_service is not None


def test_config():
    """测试配置"""
    from app.config import settings
    assert settings.master_db_host == "localhost"
    assert settings.app_port == 8000
    assert settings.vector_dimension == 1024


def test_chunk_text():
    """测试文本分块"""
    from app.services.document_service import DocumentService
    
    service = DocumentService()
    text = "第一段内容\n\n第二段内容\n\n第三段内容"
    chunks = service._chunk_text(text, chunk_size=10)
    
    assert len(chunks) > 0
    assert isinstance(chunks, list)


def test_bge_service_mock():
    """测试向量化服务（模拟模式）"""
    from app.services.bge_service import bge3_service
    
    # 测试向量化
    result = bge3_service.encode_texts(["测试文本"])
    assert 'dense_vecs' in result
    assert len(result['dense_vecs']) > 0
    
    # 测试查询向量化
    vec = bge3_service.encode_query("测试查询")
    assert len(vec) == 1024


def test_api_response_format():
    """测试API响应格式"""
    from app.models.response import ApiResponse
    
    response = ApiResponse(success=True, code=0, message="success", data={"test": "value"})
    assert response.success is True
    assert response.code == 0
    assert response.data["test"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])