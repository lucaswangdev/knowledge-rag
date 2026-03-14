-- Knowledge-RAG 主数据库初始化脚本
-- 用于存储应用配置信息

-- 创建应用配置表
CREATE TABLE IF NOT EXISTS apps (
    id SERIAL PRIMARY KEY,
    app_id VARCHAR(50) NOT NULL UNIQUE,
    app_secret VARCHAR(128) NOT NULL,
    app_name VARCHAR(100),
    db_name VARCHAR(50) NOT NULL,
    db_host VARCHAR(100) DEFAULT 'localhost',
    db_port INT DEFAULT 5432,
    db_user VARCHAR(50),
    db_password VARCHAR(128),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_apps_app_id ON apps(app_id);
CREATE INDEX IF NOT EXISTS idx_apps_status ON apps(status);

-- 初始化示例数据（请修改密码）
INSERT INTO apps (app_id, app_secret, app_name, db_name, db_host, db_port, db_user, db_password) VALUES
('app_001', 'test_secret_001', '测试应用1', 'knowledge_app_001', 'localhost', 5432, 'postgres', 'postgres'),
('app_002', 'test_secret_002', '测试应用2', 'knowledge_app_002', 'localhost', 5432, 'postgres', 'postgres')
ON CONFLICT (app_id) DO NOTHING;

-- 注释
COMMENT ON TABLE apps IS '应用配置表';
COMMENT ON COLUMN apps.app_id IS '应用ID（固定格式）';
COMMENT ON COLUMN apps.app_secret IS '应用密钥';
COMMENT ON COLUMN apps.db_name IS '对应的独立数据库名';
COMMENT ON COLUMN apps.status IS '应用状态：active/disabled';