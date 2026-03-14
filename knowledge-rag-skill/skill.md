# Knowledge-RAG Skill for OpenClaw

## 技能描述

当用户询问需要特定领域知识的问题时，使用 Knowledge-RAG 服务进行语义检索和智能问答，提供更准确、有来源的答案。

## 何时使用

✅ **应该使用此技能的场景：**
- 用户询问特定领域的专业知识（如创业、技术、产品等）
- 需要引用准确资料来源的问题
- 需要基于已存储文档的事实性回答
- 多轮对话中需要上下文记忆的问答

❌ **不应使用此技能的场景：**
- 通用常识问题（OpenClaw 自身已足够）
- 创意类、开放性问题
- 实时信息查询（如天气、新闻）
- 不需要引用来源的简单对话

## 工作流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant OpenClaw as OpenClaw
    participant RAG as Knowledge-RAG API
    participant Ollama as Ollama (bge-m3)
    participant DB as PostgreSQL+pgvector
    participant LLM as LLM服务(可选)

    User->>OpenClaw: 提问
    OpenClaw->>OpenClaw: 判断是否需要使用 RAG

    alt 使用语义搜索
        OpenClaw->>RAG: POST /api/v1/knowledge/search
        RAG->>Ollama: 问题向量化
        Ollama-->>RAG: 返回 1024维向量
        RAG->>DB: 向量相似度搜索 (pgvector)
        DB-->>RAG: Top-K 相关文档块
        RAG-->>OpenClaw: 返回搜索结果 + 相似度分数
        OpenClaw->>OpenClaw: 基于检索结果生成答案
        OpenClaw-->>User: 返回答案 + 来源引用
    end

    alt 使用 RAG 问答
        OpenClaw->>RAG: POST /api/v1/knowledge/chat
        RAG->>Ollama: 问题向量化
        Ollama-->>RAG: 返回向量
        RAG->>DB: 向量检索
        DB-->>RAG: 相关上下文
        RAG->>RAG: 构造 Prompt (问题+上下文)
        RAG->>LLM: 调用大模型生成答案(可选)
        LLM-->>RAG: 生成的答案
        RAG->>DB: 保存对话历史
        RAG-->>OpenClaw: 返回答案 + 来源
        OpenClaw-->>User: 返回完整答案
    end
