-- Migration: Add semantic search RPC function for pgvector similarity search
-- This function enables efficient vector similarity search using cosine distance

CREATE OR REPLACE FUNCTION match_conversations(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    session_id varchar(255),
    timestamp timestamp,
    user_input text,
    brain_response text,
    confidence_score integer,
    embedding vector(1536),
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.session_id,
        c.timestamp,
        c.user_input,
        c.brain_response,
        c.confidence_score,
        c.embedding,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM conversations c
    WHERE 1 - (c.embedding <=> query_embedding) >= match_threshold
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Add comment for documentation
COMMENT ON FUNCTION match_conversations IS 
'Performs semantic similarity search on conversation embeddings using cosine distance. 
Returns conversations with similarity >= match_threshold, ordered by relevance.';
