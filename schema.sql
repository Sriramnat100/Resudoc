-- 1. Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- 2. Create a table to store resume metadata (Content, Skills, etc.)
-- This replaces the need for MongoDB for now.
create table if not exists resumes (
  id uuid primary key,
  user_id uuid not null,
  filename text, -- Original PDF filename for easy identification
  content text,
  skills jsonb, -- This stores your list of skills as a JSON array
  created_at timestamptz default now()
);

-- 3. Create a table to store resume embeddings
-- References the resumes table so if you delete a resume, the embedding goes too.
create table if not exists resume_embeddings (
  resume_id uuid primary key references resumes(id) on delete cascade,
  user_id uuid not null,
  embedding vector(1536), -- OpenAI text-embedding-3-small dimension
  created_at timestamptz default now()
);

-- 4. Create an ivfflat index for fast approximate nearest neighbor search
-- Note: It's recommended to create this index after inserting some data (e.g. >1000 rows), 
-- but defining it here is fine for starting out.
create index on resume_embeddings using ivfflat (embedding vector_cosine_ops)
with (lists = 100);