# Knowledge-RAG API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **协议**: 全部使用 POST（除健康检查）
- **Content-Type**: `application/json`
- **认证**: 每个请求携带 `app_id` + `app_secret`

## 统一请求结构

```json
{
    "app_id": "app_001",
    "app_secret": "your_secret",
    "data": { }
}
```

## 统一响应结构

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": { }
}
```

---

## 接口列表

| 方法 | 路径 | 描述 |
|------|------|------|
| GET  | /health | 健康检查 |
| GET  | / | 服务信息 |
| POST | /api/v1/app/info | 获取应用信息 |
| POST | /api/v1/document/create | 创建文档 |
| POST | /api/v1/document/list | 文档列表 |
| POST | /api/v1/document/get | 文档详情 |
| POST | /api/v1/document/delete | 删除文档 |
| POST | /api/v1/knowledge/search | 语义搜索 |
| POST | /api/v1/knowledge/chat | RAG问答 |

---

## 通用接口

### 健康检查

**GET** `/health`

```bash
curl http://localhost:8000/health
```

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "status": "ok",
        "model_loaded": false
    }
}
```

### 服务信息

**GET** `/`

```bash
curl http://localhost:8000/
```

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "service": "knowledge-rag",
        "version": "1.0.0",
        "docs": "/docs"
    }
}
```

---

## 应用管理

### 获取应用信息

**POST** `/api/v1/app/info`

```bash
curl -X POST "http://localhost:8000/api/v1/app/info" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {}
  }'
```

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "app_id": "app_001",
        "app_name": "测试应用1",
        "db_name": "knowledge_app_001",
        "status": "active"
    }
}
```

---

## 文档管理

### 创建文档

**POST** `/api/v1/document/create`

```bash
curl -X POST "http://localhost:8000/api/v1/document/create" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "title": "字节跳动创业故事",
      "content": "张一鸣在2012年创立了字节跳动...",
      "tags": ["创业", "互联网"],
      "source": "manual"
    }
  }'
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ✅ | 文档标题 |
| content | string | ✅ | 文档内容（自动分块向量化） |
| tags | array | ❌ | 标签列表 |
| source | string | ❌ | 来源，默认 `manual` |

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "document_id": 1,
        "chunks_created": 3,
        "title": "字节跳动创业故事",
        "created_at": "2026-03-14T15:33:50.687793"
    }
}
```

### 文档列表

**POST** `/api/v1/document/list`

```bash
curl -X POST "http://localhost:8000/api/v1/document/list" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "page": 1,
      "page_size": 10
    }
  }'
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | ❌ | 页码，默认 1 |
| page_size | int | ❌ | 每页数量，默认 10 |
| tags | array | ❌ | 按标签筛选 |

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "total": 3,
        "page": 1,
        "page_size": 10,
        "list": [
            {
                "id": 2,
                "title": "字节跳动创业故事",
                "tags": ["创业"],
                "source": "manual",
                "created_at": "2026-03-14T15:33:50.687793"
            }
        ]
    }
}
```

### 文档详情

**POST** `/api/v1/document/get`

```bash
curl -X POST "http://localhost:8000/api/v1/document/get" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "document_id": 2
    }
  }'
```

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "id": 2,
        "title": "字节跳动创业故事",
        "content": "张一鸣在2012年创立了字节跳动...",
        "tags": ["创业"],
        "source": "manual",
        "created_at": "2026-03-14T15:33:50.687793"
    }
}
```

### 删除文档

**POST** `/api/v1/document/delete`

```bash
curl -X POST "http://localhost:8000/api/v1/document/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "document_id": 2
    }
  }'
```

```json
{
    "success": true,
    "code": 0,
    "message": "删除成功",
    "data": null
}
```

> 软删除，数据不会物理删除，status 变为 `deleted`。

---

## 知识检索

### 语义搜索

**POST** `/api/v1/knowledge/search`

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/search" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "query": "字节跳动是什么公司？",
      "top_k": 5
    }
  }'
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 查询内容 |
| top_k | int | ❌ | 返回数量，默认 5 |
| filters | object | ❌ | 筛选条件 |

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "query": "字节跳动是什么公司？",
        "total": 1,
        "results": [
            {
                "chunk_text": "张一鸣在2012年创立了字节跳动...",
                "document_id": 2,
                "document_title": "字节跳动创业故事",
                "similarity_score": 0.9823,
                "chunk_index": 0
            }
        ]
    }
}
```

### RAG 问答

**POST** `/api/v1/knowledge/chat`

```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "app_001",
    "app_secret": "test_secret_001",
    "data": {
      "query": "字节跳动是什么公司？",
      "top_k": 3
    }
  }'
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | ✅ | 问题内容 |
| top_k | int | ❌ | 参考文档数量，默认 3 |
| session_id | int | ❌ | 会话ID（多轮对话） |

```json
{
    "success": true,
    "code": 0,
    "message": "success",
    "data": {
        "answer": "根据检索到的资料，您询问的内容与「字节跳动创业故事」相关度最高。\n\n参考内容：张一鸣在2012年创立了字节跳动...",
        "sources": [
            {
                "chunk_text": "张一鸣在2012年创立了字节跳动...",
                "document_id": 2,
                "document_title": "字节跳动创业故事",
                "similarity_score": 0.9823,
                "chunk_index": 0
            }
        ]
    }
}
```

---

## 错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| 400 | 请求参数错误（缺少 app_id/app_secret） |
| 401 | 认证失败（无效的 app_id 或 app_secret） |
| 403 | 应用已禁用 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 在线文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
