-- ============================================================
-- 智能体重构数据库迁移脚本
-- ============================================================
-- 说明：此脚本用于添加重构方案中需要的新表和字段
-- 版本：2.0 - 重构版
-- 日期：2025-01-28
-- ============================================================

-- 使用数据库
\c private_doctor_db;

-- ============================================================
-- 1. 更新chat_history表（添加重构需要的字段）
-- ============================================================

-- 添加round_number字段（多轮协调的轮次）
ALTER TABLE chat_history 
ADD COLUMN IF NOT EXISTS round_number INTEGER;

-- 添加metadata字段（存储额外的元数据）
ALTER TABLE chat_history 
ADD COLUMN IF NOT EXISTS metadata JSONB;

-- 添加索引
CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_round_number ON chat_history(round_number);

-- ============================================================
-- 2. 更新user_profiles表（根据重构方案调整）
-- ============================================================

-- 注意：如果user_profiles表已经包含allergies、medications、medical_conditions字段
-- 这些字段可以保留，但根据重构方案，这些详细医疗数据应该存储在第三方数据库存储服务
-- 这里只更新注释说明，不删除现有字段（保持向后兼容）

COMMENT ON TABLE user_profiles IS '用户基础档案表（推荐保留）- 仅存储基础信息，不包含详细医疗数据。详细医疗数据存储在第三方数据库存储服务。';

-- ============================================================
-- 3. 创建diagnosis_sessions表（诊断会话表）
-- ============================================================

CREATE TABLE IF NOT EXISTS diagnosis_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
    intent VARCHAR(50),  -- 意图类型
    status VARCHAR(20) DEFAULT 'in_progress',  -- in_progress, completed, failed
    current_round INTEGER DEFAULT 0,
    max_rounds INTEGER DEFAULT 5,
    shared_context JSONB,  -- 存储SharedContext的快照
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_diagnosis_sessions_user_id ON diagnosis_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_diagnosis_sessions_session_id ON diagnosis_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_diagnosis_sessions_status ON diagnosis_sessions(status);

COMMENT ON TABLE diagnosis_sessions IS '诊断会话表（必需）- 存储多轮协调的诊断会话状态';

-- ============================================================
-- 4. 创建diagnosis_results表（诊断结果缓存表）
-- ============================================================

CREATE TABLE IF NOT EXISTS diagnosis_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES diagnosis_sessions(session_id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    agent_name VARCHAR(100) NOT NULL,  -- 专科医生名称
    location VARCHAR(50),  -- 地域信息
    diagnosis_summary TEXT,  -- 诊断摘要（不包含详细医疗数据）
    confidence DECIMAL(3,2),
    data_requirements JSONB,  -- 数据需求列表
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_session_id ON diagnosis_results(session_id);
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_round_number ON diagnosis_results(round_number);
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_agent_name ON diagnosis_results(agent_name);

COMMENT ON TABLE diagnosis_results IS '诊断结果缓存表（必需）- 缓存诊断结果，不存储原始医疗数据';

-- ============================================================
-- 5. 创建data_address_history表（数据地址历史表）
-- ============================================================

CREATE TABLE IF NOT EXISTS data_address_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES diagnosis_sessions(session_id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL,
    data_addresses JSONB,  -- 存储数据地址列表（不包含实际数据）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_data_address_history_session_id ON data_address_history(session_id);
CREATE INDEX IF NOT EXISTS idx_data_address_history_round_number ON data_address_history(round_number);

COMMENT ON TABLE data_address_history IS '数据地址历史表（推荐保留）- 记录获取的数据地址，不存储实际数据。用途：避免重复获取、审计、问题排查、数据分析';

-- ============================================================
-- 6. 创建comprehensive_reports表（综合诊断报告表）
-- ============================================================

CREATE TABLE IF NOT EXISTS comprehensive_reports (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES diagnosis_sessions(session_id) ON DELETE CASCADE,
    report_content TEXT NOT NULL,  -- 综合诊断报告内容
    evolution_summary JSONB,  -- 诊断演进过程摘要
    specialist_results JSONB,  -- 专科医生诊断结果摘要
    total_rounds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_comprehensive_reports_session_id ON comprehensive_reports(session_id);

COMMENT ON TABLE comprehensive_reports IS '综合诊断报告表（必需）- 存储最终生成的综合诊断报告';

-- ============================================================
-- 7. 更新hospitals表（添加重构需要的字段）
-- ============================================================

-- 添加database_storage_endpoint字段（第三方数据库存储服务端点）
ALTER TABLE hospitals 
ADD COLUMN IF NOT EXISTS database_storage_endpoint VARCHAR(500);

COMMENT ON COLUMN hospitals.database_storage_endpoint IS '对应的第三方数据库存储服务端点';

-- ============================================================
-- 8. 验证表创建结果
-- ============================================================

-- 显示所有表
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 显示诊断相关表的索引
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public' 
  AND tablename IN ('diagnosis_sessions', 'diagnosis_results', 'data_address_history', 'comprehensive_reports')
ORDER BY tablename, indexname;

-- ============================================================
-- 迁移完成
-- ============================================================

