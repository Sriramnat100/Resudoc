import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from db_manager import DbManager
from embedder import Embedder
from pdf_reader import PDFReader
from matching_engine import MatchingEngine

def test_matching_engine():
    print("Starting Matching Engine Test...")
    
    # Setup Mock Components
    # We rely on the mock modes of these classes for simplicity in this unit test
    db = DbManager() # Mock mode
    embedder = Embedder() # Mock mode
    reader = PDFReader() # Mock mode
    
    engine = MatchingEngine(db, embedder, reader)
    
    user_id = "mock-user"
    jd_text = "Looking for a Python Engineer with SQL skills."
    
    # In mock mode:
    # - Embedder returns [0.0...]
    # - PDFReader returns ["Mock Skill 1", "Mock Skill 2", "Python (Mock)"]
    # - NearestNeighbor returns mock-resume-1 (0.95) and mock-resume-2 (0.88)
    # - DbManager.get_resumes_by_ids returns mock content/skills
    
    # To make this test meaningful without real DB/OpenAI, we need to inspect the logic flow.
    # Ideally we would mock the return values to control the scenario, but for now we verify the plumbing.
    
    results = engine.match_best_resume(user_id, jd_text, k=2)
    
    print(f"Results found: {len(results)}")
    for i, res in enumerate(results):
        print(f"{i+1}. ID: {res['resume_id']}")
        print(f"   Final Score: {res['final_score']:.4f}")
        print(f"   Semantic: {res['semantic_score']:.4f}, Skill: {res['skill_score']:.4f}")
        print(f"   Overlap: {res['overlap_count']}")
        
    if results:
        print("SUCCESS: Matching Engine returned results.")
    else:
        print("FAILURE: No results returned.")

if __name__ == "__main__":
    test_matching_engine()
