-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store resume embeddings
-- We assume there is a separate 'resumes' table or 'users' table for metadata, 
-- but for this specific task we focus on the embeddings table as requested.
create table if not exists resume_embeddings (
  resume_id uuid primary key,
  user_id uuid not null,
  embedding vector(1536), -- OpenAI text-embedding-3-small dimension
  created_at timestamptz default now()
);

-- Create an ivfflat index for fast approximate nearest neighbor search
-- Note: It's recommended to create this index after inserting some data, 
-- but defining it here for schema completeness.
-- lists = rows / 1000 is a good starting point.
create index on resume_embeddings using ivfflat (embedding vector_cosine_ops)
with (lists = 100);
