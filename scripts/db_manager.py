import os
from dotenv import load_dotenv
load_dotenv()
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

    def upsert_resume(self, resume_id: str, user_id: str, content: str, skills: List[str] = [], filename: str = None, tags: List[str] = []) -> bool:
        """
        Inserts or updates resume metadata (content, skills, filename, tags).
        """
        if not self.conn:
            print(f"[MOCK DB] Upserting resume metadata for {resume_id}")
            return True

        # Try with tags first, fall back to without tags if column doesn't exist
        try:
            query = """
                INSERT INTO resumes (id, user_id, filename, content, skills, tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) 
                DO UPDATE SET filename = EXCLUDED.filename, content = EXCLUDED.content, skills = EXCLUDED.skills, tags = EXCLUDED.tags, user_id = EXCLUDED.user_id;
            """
            with self.conn.cursor() as cur:
                from psycopg2.extras import Json
                cur.execute(query, (resume_id, user_id, filename, content, Json(skills), tags))
            self.conn.commit()
            return True
        except Exception as e:
            # If tags column doesn't exist, try without it
            if "tags" in str(e).lower():
                print(f"Warning: tags column not found, inserting without tags")
                self.conn.rollback()
                try:
                    query = """
                        INSERT INTO resumes (id, user_id, filename, content, skills)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) 
                        DO UPDATE SET filename = EXCLUDED.filename, content = EXCLUDED.content, skills = EXCLUDED.skills, user_id = EXCLUDED.user_id;
                    """
                    with self.conn.cursor() as cur:
                        from psycopg2.extras import Json
                        cur.execute(query, (resume_id, user_id, filename, content, Json(skills)))
                    self.conn.commit()
                    return True
                except Exception as e2:
                    print(f"Error upserting resume metadata: {e2}")
                    self.conn.rollback()
                    return False
            else:
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

        # Cast the string array to UUID array for PostgreSQL
        query = "SELECT id, filename, content, skills FROM resumes WHERE id = ANY(%s::uuid[]);"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (resume_ids,))
                rows = cur.fetchall()
                
            return {
                str(row[0]): {"filename": row[1], "content": row[2], "skills": row[3]}
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

    def list_resumes(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Lists all resumes for a given user with their tags.
        """
        if not self.conn:
            print(f"[MOCK DB] Listing resumes for user {user_id}")
            return []

        query = """
            SELECT id, filename, created_at, tags 
            FROM resumes 
            WHERE user_id = %s 
            ORDER BY created_at DESC;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (user_id,))
                rows = cur.fetchall()
                
            return [
                {
                    "id": str(row[0]),
                    "filename": row[1],
                    "created_at": str(row[2]) if row[2] else None,
                    "tags": row[3] if row[3] else []
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error listing resumes: {e}")
            return []

    def delete_resume(self, resume_id: str) -> bool:
        """
        Deletes a resume and its embedding (cascade will handle embedding).
        """
        if not self.conn:
            print(f"[MOCK DB] Deleting resume {resume_id}")
            return True

        query = "DELETE FROM resumes WHERE id = %s;"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (resume_id,))
                deleted = cur.rowcount > 0
            self.conn.commit()
            return deleted
        except Exception as e:
            print(f"Error deleting resume: {e}")
            self.conn.rollback()
            return False

    def list_folders(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Lists all unique tags/folders for a user with resume counts.
        Returns empty list if tags column doesn't exist.
        """
        if not self.conn:
            print(f"[MOCK DB] Listing folders for user {user_id}")
            return []

        try:
            query = """
                SELECT UNNEST(tags) as tag, COUNT(*) as count
                FROM resumes
                WHERE user_id = %s AND tags IS NOT NULL AND array_length(tags, 1) > 0
                GROUP BY tag
                ORDER BY tag;
            """
            with self.conn.cursor() as cur:
                cur.execute(query, (user_id,))
                rows = cur.fetchall()
                
            return [
                {
                    "name": row[0],
                    "count": row[1]
                }
                for row in rows
            ]
        except Exception as e:
            # If tags column doesn't exist, just return empty list
            if "tags" in str(e).lower() or "does not exist" in str(e).lower():
                return []
            print(f"Error listing folders: {e}")
            return []

    def get_resumes_by_tags(self, user_id: str, tags: List[str]) -> List[str]:
        """
        Gets resume IDs that match ANY of the given tags.
        """
        if not self.conn:
            print(f"[MOCK DB] Getting resumes by tags for user {user_id}")
            return []

        query = """
            SELECT id
            FROM resumes
            WHERE user_id = %s AND tags && %s
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (user_id, tags))
                rows = cur.fetchall()
                
            return [str(row[0]) for row in rows]
        except Exception as e:
            print(f"Error getting resumes by tags: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
