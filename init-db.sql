-- JARVIS Database Initialization Script
-- This script sets up the PostgreSQL database schema with pgvector extension

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Conversations table with vector embeddings for semantic search
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_input TEXT NOT NULL,
    brain_response TEXT NOT NULL,
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    embedding vector(1536),  -- OpenAI embedding dimension
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector similarity search using ivfflat
CREATE INDEX IF NOT EXISTS conversations_embedding_idx 
ON conversations USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index for session lookup
CREATE INDEX IF NOT EXISTS conversations_session_idx ON conversations(session_id);

-- Create index for timestamp ordering
CREATE INDEX IF NOT EXISTS conversations_timestamp_idx ON conversations(timestamp DESC);

-- Personal profile table for user preferences and learned behaviors
CREATE TABLE IF NOT EXISTS personal_profile (
    user_id VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    habits JSONB DEFAULT '{}',
    interests TEXT[] DEFAULT '{}',
    communication_style VARCHAR(50) DEFAULT 'casual',
    work_hours JSONB DEFAULT '{"start": "09:00", "end": "18:00"}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Episodic memory table for interaction logs
CREATE TABLE IF NOT EXISTS episodic_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    interaction_type VARCHAR(50) NOT NULL,
    context TEXT,
    action_taken TEXT,
    outcome TEXT,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for timestamp-based queries
CREATE INDEX IF NOT EXISTS episodic_memory_timestamp_idx ON episodic_memory(timestamp DESC);

-- Create index for interaction type filtering
CREATE INDEX IF NOT EXISTS episodic_memory_type_idx ON episodic_memory(interaction_type);

-- Reminders table for scheduled tasks
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task TEXT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    delivered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP
);

-- Create index for scheduled time lookup
CREATE INDEX IF NOT EXISTS reminders_scheduled_idx ON reminders(scheduled_time) 
WHERE delivered = FALSE;

-- Audit log table for security and action tracking
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    action_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    details JSONB DEFAULT '{}',
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for timestamp-based queries
CREATE INDEX IF NOT EXISTS audit_log_timestamp_idx ON audit_log(timestamp DESC);

-- Create index for action type filtering
CREATE INDEX IF NOT EXISTS audit_log_action_idx ON audit_log(action_type);

-- Create index for user filtering
CREATE INDEX IF NOT EXISTS audit_log_user_idx ON audit_log(user_id);

-- Insert default personal profile
INSERT INTO personal_profile (user_id, first_name, timezone, communication_style)
VALUES ('default_user', 'Boss', 'UTC', 'casual')
ON CONFLICT (user_id) DO NOTHING;

-- Log initialization
INSERT INTO audit_log (action_type, details, success)
VALUES ('database_initialization', '{"message": "Database schema initialized successfully"}', TRUE);
