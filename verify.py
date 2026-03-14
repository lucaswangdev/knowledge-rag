#!/usr/bin/env python
"""Knowledge-RAG 项目验证脚本"""

import sys
from app.main import app
from fastapi.testclient import TestClient

def main():
    print("🔍 Knowledge-RAG 项目验证")
    print("=" * 50)
    print()
    
    client = TestClient(app)
    
    # 1. 测试根路径
    print("1️⃣  测试根路径...")
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['data']['service'] == 'knowledge-rag'
    print(f"   ✅ 服务名称: {data['data']['service']}")
    print(f"   ✅ 版本: {data['data']['version']}")
    print()
    
    # 2. 测试健康检查
    print("2️⃣  测试健康检查...")
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['data']['status'] == 'ok'
    print(f"   ✅ 状态: {data['data']['status']}")
    print(f"   ✅ 模型加载: {data['data']['model_loaded']}")
    print()
    
    # 3. 测试配置加载
    print("3️⃣  测试配置加载...")
    from app.config import settings
    print(f"   ✅ 主数据库: {settings.master_db_host}:{settings.master_db_port}/{settings.master_db_name}")
    print(f"   ✅ 向量维度: {settings.vector_dimension}")
    print(f"   ✅ 分块大小: {settings.chunk_size}")
    print()
    
    # 4. 测试BGE服务
    print("4️⃣  测试BGE向量化服务...")
    from app.services.bge_service import bge3_service
    test_texts = ["测试文本1", "测试文本2"]
    result = bge3_service.encode_texts(test_texts)
    assert 'dense_vecs' in result
    assert len(result['dense_vecs']) == 2
    print(f"   ✅ 批量向量化: {len(test_texts)} 个文本")
    
    vec = bge3_service.encode_query("测试查询")
    assert len(vec) == settings.vector_dimension
    print(f"   ✅ 查询向量化: {len(vec)} 维")
    print()
    
    # 5. 测试文档服务
    print("5️⃣  测试文档服务...")
    from app.services.document_service import DocumentService
    doc_service = DocumentService()
    chunks = doc_service._chunk_text("第一段\n\n第二段\n\n第三段", chunk_size=20)
    assert len(chunks) > 0
    print(f"   ✅ 文本分块: {len(chunks)} 个块")
    print()
    
    # 6. 测试API响应格式
    print("6️⃣  测试API响应格式...")
    from app.models.response import ApiResponse
    resp = ApiResponse(success=True, code=0, message="test", data={"key": "value"})
    assert resp.success is True
    assert resp.code == 0
    print(f"   ✅ 响应格式验证通过")
    print()
    
    # 7. 测试认证中间件
    print("7️⃣  测试认证中间件...")
    response = client.post("/api/v1/document/list", json={"data": {}})
    assert response.status_code == 400  # 缺少凭证
    print(f"   ✅ 认证检查正常")
    print()
    
    print("=" * 50)
    print("🎉 所有验证通过！项目已成功运行！")
    print()
    print("📚 下一步:")
    print("   1. 配置数据库连接 (.env)")
    print("   2. 初始化数据库 (init_master.sql, init_app.sql)")
    print("   3. 启动服务: uv run uvicorn app.main:app --reload")
    print("   4. 访问文档: http://localhost:8000/docs")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
