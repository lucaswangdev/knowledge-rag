-- Knowledge-RAG 应用数据库初始化脚本
-- 每个应用独立的数据库需要执行此脚本

-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 文档表
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100),
    tags JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 向量表 (bge-m3: 1024维)
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INT,
    dense_vector vector(1024),
    sparse_weights JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 向量索引 (HNSW近似搜索)
CREATE INDEX IF NOT EXISTS idx_chunks_vector_hnsw 
ON document_chunks USING hnsw (dense_vector vector_cosine_ops);

-- 全文检索索引 (GIN)
CREATE INDEX IF NOT EXISTS idx_chunks_text_gin 
ON document_chunks USING gin (to_tsvector('chinese', chunk_text));

-- 文档索引
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at DESC);

-- 对话会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 对话消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 注释
COMMENT ON TABLE documents IS '文档表';
COMMENT ON TABLE document_chunks IS '文档向量表';
COMMENT ON TABLE chat_sessions IS '对话会话表';
COMMENT ON TABLE chat_messages IS '对话消息表';