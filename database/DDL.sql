CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table creation 
CREATE TABLE image_detail (
    uuid UUID PRIMARY KEY,
    url TEXT,
    title TEXT,
    caption TEXT,
    tags TEXT,
    embedding_vector VECTOR(2048),
    coordinates GEOMETRY(POINT, 4326),
    capture_time TIMESTAMP,
    extended_meta JSON,
    updated_at TIMESTAMP,
    created_at TIMESTAMP
);

-- Index creation for searching on coordinates
CREATE INDEX CONCURRENTLY idx_image_detail_coordinates ON image_detail USING GIST (coordinates);

-- Index creation for searching on the embedding vector
-- This assumes the use of the pgvector extension or a similar extension
CREATE INDEX CONCURRENTLY idx_image_detail_embedding ON image_detail USING hnsw (embedding_vector);


