import sys
import os
import uuid
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
    
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "test-user-123")) 
    jd_text = "Responsibilities: Generative AI is a rapidly evolving field and the priorities a genAI team change over time.  We expect internships to cover some of the following responsibilities, but new priorities may emerge Build generative AI applications for Bloomberg Law, Tax, and Government products, and the News and Content teams across those products. Develop or enhance AI agent workflows, including multi-step reasoning and task orchestration. Work with MCP systems to extend agent capabilities and control context. Prototype reinforcement learning for genAI systems to optimize prompts, context and tool calls. Collaborate with news, content, and product teams to evaluate, refine, and integrate models into production environments. Document and present technical findings and prototype outcomes. Qualifications: Pursuing a degree in Computer Science, Machine Learning, Sciences, Math's, or related field. Proficiency in Python Experience with large language models, agentic systems, or reinforcement learning concepts. Be open to full-time work in 2027 How to stand out An exceptional candidate may differentiate themselves with some of the following. These are not requirements and you should feel comfortable applying if you do not meet all of these: Motivation and curiosity: Strong interest in understanding problems, questioning assumptions and then designing solutions. Proactive ownership: when assigned a task, be eager to understand the end goal and to step outside of areas of formal responsibility to meet that goal Built something:  In school or hobby, have built something from scratch or overhauled a non-functional part of a system. Bayesian statistics: Have formal background or work experience in A/B testing and Bayesian statistics Relevant work experience: Exposure to professional Application Design or Data Engineering. Finally, we highlight that excellence has no single mold, particularly in a field as rapidly evolving as AI. We’re looking for excellent candidates of all backgrounds with strong business intuition and coding skills, and welcome applicants regardless of ethnic/national origin, gender, race, religious beliefs, disability, sexual orientation or age."
    
    # In mock mode:
    # - Embedder returns [0.0...]
    # - PDFReader returns ["Mock Skill 1", "Mock Skill 2", "Python (Mock)"]
    # - NearestNeighbor returns mock-resume-1 (0.95) and mock-resume-2 (0.88)
    # - DbManager.get_resumes_by_ids returns mock content/skills
    
    # To make this test meaningful without real DB/OpenAI, we need to inspect the logic flow.
    # Ideally we would mock the return values to control the scenario, but for now we verify the plumbing.
    
    results = engine.match_best_resume(user_id, jd_text, k=3)
    
    print(f"Results found: {len(results)}")
    for i, res in enumerate(results):
        print(f"{i+1}. {res.get('filename', 'Unknown')} (ID: {res['resume_id']})")
        print(f"   Final Score: {res['final_score']:.4f}")
        print(f"   Semantic: {res['semantic_score']:.4f}, Skill: {res['skill_score']:.4f}")
        print(f"   Overlap: {res['overlap_count']}")
        
    if results:
        print("SUCCESS: Matching Engine returned results.")
    else:
        print("FAILURE: No results returned.")

if __name__ == "__main__":
    test_matching_engine()
