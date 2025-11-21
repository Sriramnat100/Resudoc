from typing import List, Dict, Any
from db_manager import DbManager
from nearest_neighbor import NearestNeighbor
from embedder import Embedder
from pdf_reader import PDFReader

class MatchingEngine:
    """
    Orchestrates the matching process:
    1. Embeds the Job Description (JD).
    2. Finds nearest neighbors using vector similarity.
    3. Fetches full resume metadata.
    4. Scores candidates based on semantic similarity and skill overlap.
    """

    def __init__(self, db_manager: DbManager, embedder: Embedder, pdf_reader: PDFReader):
        self.db = db_manager
        self.embedder = embedder
        self.pdf_reader = pdf_reader
        self.nn = NearestNeighbor(db_manager)

    def match_best_resume(self, user_id: str, jd_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Finds and ranks the best resumes for a given JD.
        """
        if not jd_text:
            return []

        # 1. Analyze JD
        print("   [MatchingEngine] Analyzing JD...")
        jd_embedding = self.embedder.get_embedding(jd_text)
        jd_skills = self.pdf_reader.extract_skills(jd_text)
        # Normalize JD skills for comparison
        jd_skills_set = set(s.lower() for s in jd_skills)

        # 2. Find Nearest Neighbors (Semantic Search)
        print(f"   [MatchingEngine] Finding top {k} candidates via vector search...")
        candidates = self.nn.find_nearest_resumes(user_id, jd_embedding, k=k)
        
        if not candidates:
            return []

        # 3. Fetch Metadata
        print("   [MatchingEngine] Fetching candidate metadata...")
        resume_ids = [c['resume_id'] for c in candidates]
        resume_details = self.db.get_resumes_by_ids(resume_ids)

        # 4. Score Candidates
        scored_candidates = []
        for candidate in candidates:
            rid = candidate['resume_id']
            semantic_score = candidate['similarity']
            
            details = resume_details.get(rid, {})
            resume_skills = details.get('skills', [])
            # Handle case where skills might be None or list
            if not resume_skills:
                resume_skills = []
            
            resume_skills_set = set(s.lower() for s in resume_skills)
            
            # Calculate Skill Overlap Score
            if jd_skills_set:
                overlap = len(jd_skills_set.intersection(resume_skills_set))
                skill_score = overlap / len(jd_skills_set)
            else:
                skill_score = 0.0

            # Final Weighted Score
            # Adjust weights as needed. 
            # Semantic is usually strong, but skills ensure specific keywords are present.
            final_score = (semantic_score * 0.7) + (skill_score * 0.3)
            
            scored_candidates.append({
                "resume_id": rid,
                "final_score": final_score,
                "semantic_score": semantic_score,
                "skill_score": skill_score,
                "overlap_count": len(jd_skills_set.intersection(resume_skills_set)),
                "content_preview": details.get('content', '')[:100] + "..."
            })

        # 5. Sort by Final Score
        scored_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        return scored_candidates
