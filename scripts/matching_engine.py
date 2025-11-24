from typing import List, Dict, Any
from db_manager import DbManager
from nearest_neighbor import NearestNeighbor
from embedder import Embedder
from llm_ranker import LLMRanker

class MatchingEngine:
    """
    Orchestrates the matching process:
    1. Embeds the Job Description (JD).
    2. Finds nearest neighbors using vector similarity.
    3. Uses LLM to rank all k candidates in a single batch call.
    """

    def __init__(self, db_manager: DbManager, embedder: Embedder):
        self.db = db_manager
        self.embedder = embedder
        self.nn = NearestNeighbor(db_manager)
        self.llm_ranker = LLMRanker()

    def match_best_resume(self, user_id: str, jd_text: str, k: int = 5, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Finds and ranks the best resumes for a given JD using LLM-based ranking.
        """
        if not jd_text:
            return []

        # 1. Generate JD Embedding
        print("   [MatchingEngine] Generating JD embedding...")
        jd_embedding = self.embedder.get_embedding(jd_text)

        # 2. Find Nearest Neighbors (Semantic Search)
        print(f"   [MatchingEngine] Finding top {k} candidates via vector search...")
        candidates = self.nn.find_nearest_resumes(user_id, jd_embedding, k=k, tags=tags)
        
        if not candidates:
            print("   [MatchingEngine] No candidates found.")
            return []

        # 3. Fetch Resume Content
        print("   [MatchingEngine] Fetching candidate content...")
        resume_ids = [c['resume_id'] for c in candidates]
        resume_details = self.db.get_resumes_by_ids(resume_ids)

        # 4. Prepare candidates for batch ranking
        candidates_for_ranking = []
        for candidate in candidates:
            rid = candidate['resume_id']
            details = resume_details.get(rid, {})
            
            candidates_for_ranking.append({
                'resume_id': rid,
                'filename': details.get('filename', 'Unknown'),
                'content': details.get('content', '')
            })

        # 5. Batch LLM Ranking (SINGLE CALL for all k candidates)
        print(f"   [MatchingEngine] Ranking {len(candidates_for_ranking)} candidates with LLM...")
        ranked_results = self.llm_ranker.rank_resumes_batch(jd_text, candidates_for_ranking)
        
        print(f"   [MatchingEngine] Ranking complete!")
        
        return ranked_results
