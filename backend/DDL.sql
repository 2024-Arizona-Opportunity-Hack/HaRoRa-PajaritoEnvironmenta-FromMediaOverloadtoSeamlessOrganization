CREATE
EXTENSION IF NOT EXISTS vector;
CREATE
EXTENSION IF NOT EXISTS postgis;


CREATE TABLE IF NOT EXISTS users (
  user_id TEXT PRIMARY KEY,  
  user_name TEXT NOT NULL,   
  email TEXT NOT NULL,       
  access_token TEXT NOT NULL, 
  refresh_token TEXT NOT NULL, 
  template_id TEXT NOT NULL,
  cursor TEXT,               
  initials VARCHAR(3),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS image_detail (
  uuid UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  url TEXT NOT NULL,
  thumbnail_url TEXT NOT NULL,
  title TEXT,
  caption TEXT,
  tags TEXT,
  title_caption_tags_fts_vector tsvector generated always as (to_tsvector('english', COALESCE(tags, '') || ' ' ||
                                                                                   COALESCE(title, '') || ' ' ||
                                                                                   COALESCE(caption, ''))) stored,
  embedding_vector VECTOR(512),
  coordinates GEOMETRY(POINT, 4326),
  capture_time TIMESTAMP,
  extended_meta JSON,
  season TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS FileQueue (
  tmp_file_loc TEXT PRIMARY KEY,
  tag_list TEXT NOT NULL,
  access_token TEXT NOT NULL,
  user_id TEXT NOT NULL,
  image_id TEXT NOT NULL,
  batch_id TEXT,
  is_saved_to_db BOOLEAN DEFAULT FALSE,
  is_cleaned_from_disk BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS BatchQueue (
  batch_id TEXT PRIMARY KEY,
  input_file_id TEXT NOT NULL,
  batch_jsonl_filepath TEXT NOT NULL,
  batch_metadata_filepath TEXT NOT NULL,
  status TEXT DEFAULT 'submitted',
  output_file_id TEXT,
  are_all_files_updated_in_db BOOLEAN DEFAULT FALSE,
  are_files_deleted_from_oai_storage BOOLEAN DEFAULT FALSE,
  is_cleaned_from_disk BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE
OR REPLACE FUNCTION update_fts_col()
RETURNS TRIGGER AS $$
BEGIN
  NEW.title_caption_tags_fts_vector = to_tsvector('english', COALESCE(tags, '') || ' ' || COALESCE(title, '') || ' ' || COALESCE(caption, ''));
  RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

CREATE
OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON image_detail
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON FileQueue
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON BatchQueue
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- CREATE TRIGGER update_updated_at
    -- BEFORE UPDATE
    -- ON image_detail
    -- FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Index creation for searching on coordinates
CREATE INDEX IF NOT EXISTS idx_image_detail_coordinates ON image_detail USING GIST (coordinates);

-- Index creation for searching on the embedding vector
-- This assumes the use of the pgvector extension or a similar extension
CREATE INDEX IF NOT EXISTS idx_image_detail_embedding ON image_detail USING hnsw (embedding_vector vector_ip_ops);
