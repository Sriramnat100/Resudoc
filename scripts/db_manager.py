import os
import psycopg2
from pgvector.psycopg2 import register_vector
from typing import List, Any, Optional, Tuple, Dict

class DbManager:
    """
    Manages low-level interactions with the PostgreSQL database.
    Handles connection, raw execution, and embedding storage plumbing.
    """

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv("DATABASE_URL")
        self.conn = None
        
        if self.connection_string:
            try:
                self.conn = psycopg2.connect(self.connection_string)
                register_vector(self.conn)
            except Exception as e:
                print(f"Error connecting to database: {e}")
                self.conn = None
        else:
            print("Warning: No DATABASE_URL provided. Running in MOCK mode.")

    def upsert_embedding(self, resume_id: str, user_id: str, embedding: List[float]) -> bool:
        """
        Inserts or updates a resume embedding.
        """
        if not self.conn:
            print(f"[MOCK DB] Upserting embedding for resume {resume_id}, user {user_id}")
            return True

        query = """
            INSERT INTO resume_embeddings (resume_id, user_id, embedding)
            VALUES (%s, %s, %s)
            ON CONFLICT (resume_id) 
            DO UPDATE SET embedding = EXCLUDED.embedding, user_id = EXCLUDED.user_id;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (resume_id, user_id, embedding))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error upserting embedding: {e}")
            self.conn.rollback()
            return False

    def delete_embedding(self, resume_id: str) -> bool:
        """
        Deletes a resume embedding.
        """
        if not self.conn:
            print(f"[MOCK DB] Deleting embedding for resume {resume_id}")
            return True

        query = "DELETE FROM resume_embeddings WHERE resume_id = %s;"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (resume_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting embedding: {e}")
            self.conn.rollback()
            return False

    def upsert_resume(self, resume_id: str, user_id: str, content: str, skills: List[str]) -> bool:
        """
        Inserts or updates resume metadata (content, skills).
        """
        if not self.conn:
            print(f"[MOCK DB] Upserting resume metadata for {resume_id}")
            return True

        # We assume a 'resumes' table exists as per schema.sql
        # id, user_id, content, skills
        query = """
            INSERT INTO resumes (id, user_id, content, skills)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) 
            DO UPDATE SET content = EXCLUDED.content, skills = EXCLUDED.skills, user_id = EXCLUDED.user_id;
        """
        try:
            with self.conn.cursor() as cur:
                from psycopg2.extras import Json
                cur.execute(query, (resume_id, user_id, content, Json(skills)))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error upserting resume metadata: {e}")
            self.conn.rollback()
            return False

    def get_resumes_by_ids(self, resume_ids: List[str]) -> Dict[str, Any]:
        """
        Fetches resume details (content, skills) for a list of IDs.
        Returns a dictionary mapping resume_id to details.
        """
        if not resume_ids:
            return {}

        if not self.conn:
            print(f"[MOCK DB] Fetching details for {len(resume_ids)} resumes")
            return {
                rid: {"content": f"Mock Content for {rid}", "skills": ["Mock Skill"]}
                for rid in resume_ids
            }

        query = "SELECT id, content, skills FROM resumes WHERE id = ANY(%s);"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (resume_ids,))
                rows = cur.fetchall()
                
            return {
                str(row[0]): {"content": row[1], "skills": row[2]}
                for row in rows
            }
        except Exception as e:
            print(f"Error fetching resume details: {e}")
            return {}

    def execute(self, query: str, params: Tuple = None):
        """
        Executes a raw SQL query (for inserts/updates without return).
        """
        if not self.conn:
            print(f"[MOCK DB] Executing: {query}")
            return

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            print(f"Error executing query: {e}")
            self.conn.rollback()

    def fetch_all(self, query: str, params: Tuple = None) -> List[Tuple]:
        """
        Executes a query and returns all results.
        """
        if not self.conn:
            print(f"[MOCK DB] Fetching all: {query}")
            return []

        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
