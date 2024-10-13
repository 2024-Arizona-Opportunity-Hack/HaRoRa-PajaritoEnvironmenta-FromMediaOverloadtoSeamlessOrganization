CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table creation
CREATE TABLE image_detail (
                              uuid UUID PRIMARY KEY,
                              url TEXT,
                              title TEXT,
                              caption TEXT,
                              tags TEXT,
                              title_caption_tags_fts_vector tsvector generated always as  (to_tsvector('english', COALESCE(tags, '') || ' ' || COALESCE(title, '') || ' ' || COALESCE(caption, ''))) stored,
                              embedding_vector VECTOR(768),
                              coordinates GEOMETRY(POINT, 4326),
                              capture_time TIMESTAMP,
                              extended_meta JSON,
                              season TEXT,
                              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Index creation for searching on coordinates
CREATE INDEX CONCURRENTLY idx_image_detail_coordinates ON image_detail USING GIST (coordinates);

-- Index creation for searching on the embedding vector
-- This assumes the use of the pgvector extension or a similar extension
CREATE INDEX CONCURRENTLY idx_image_detail_embedding ON image_detail USING hnsw (embedding_vector);


