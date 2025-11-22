from typing import List, Dict, Any
from db_manager import DbManager

class NearestNeighbor:
    """
    Handles logic for finding nearest neighbors using vector similarity.
    """

    def __init__(self, db_manager: DbManager):
        self.db = db_manager

    def find_nearest_resumes(self, user_id: str, job_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Finds the k nearest resumes for a given user and job description embedding.
        Uses pgvector's <-> operator for Euclidean distance (or <=> for cosine distance).
        Since we want similarity, we can use cosine distance (<=>).
        """
        # Query to find nearest neighbors
        # We select 1 - (embedding <=> query) to get cosine similarity (where 1 is identical)
        # Note: pgvector expects the embedding to be cast to vector type
        query = """
            SELECT resume_id, 1 - (embedding <=> %s::vector) as similarity
            FROM resume_embeddings
            WHERE user_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """
        
        # In mock mode, return dummy data
        if not self.db.conn:
            print(f"[MOCK NN] Finding {k} nearest resumes for user {user_id}")
            return [
                {"resume_id": "mock-resume-1", "similarity": 0.95},
                {"resume_id": "mock-resume-2", "similarity": 0.88}
            ]

        # Convert embedding list to string format for pgvector: '[1,2,3,...]'
        embedding_str = '[' + ','.join(map(str, job_embedding)) + ']'
        
        rows = self.db.fetch_all(query, (embedding_str, user_id, embedding_str, k))
        
        results = []
        for row in rows:
            results.append({
                "resume_id": str(row[0]),
                "similarity": float(row[1])
            })
            
        return results
