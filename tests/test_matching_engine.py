import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from db_manager import DbManager
from embedder import Embedder
from matching_engine import MatchingEngine

def test_matching_engine():
    print("Starting Matching Engine Test (LLM-Based Ranking)...")
    
    # Setup Components
    db = DbManager()
    embedder = Embedder()
    
    engine = MatchingEngine(db, embedder)
    
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "test-user-123")) 
    jd_text = "Responsibilities: Generative AI is a rapidly evolving field and the priorities a genAI team change over time.  We expect internships to cover some of the following responsibilities, but new priorities may emerge Build generative AI applications for Bloomberg Law, Tax, and Government products, and the News and Content teams across those products. Develop or enhance AI agent workflows, including multi-step reasoning and task orchestration. Work with MCP systems to extend agent capabilities and control context. Prototype reinforcement learning for genAI systems to optimize prompts, context and tool calls. Collaborate with news, content, and product teams to evaluate, refine, and integrate models into production environments. Document and present technical findings and prototype outcomes. Qualifications: Pursuing a degree in Computer Science, Machine Learning, Sciences, Math's, or related field. Proficiency in Python Experience with large language models, agentic systems, or reinforcement learning concepts. Be open to full-time work in 2027 How to stand out An exceptional candidate may differentiate themselves with some of the following. These are not requirements and you should feel comfortable applying if you do not meet all of these: Motivation and curiosity: Strong interest in understanding problems, questioning assumptions and then designing solutions. Proactive ownership: when assigned a task, be eager to understand the end goal and to step outside of areas of formal responsibility to meet that goal Built something:  In school or hobby, have built something from scratch or overhauled a non-functional part of a system. Bayesian statistics: Have formal background or work experience in A/B testing and Bayesian statistics Relevant work experience: Exposure to professional Application Design or Data Engineering. Finally, we highlight that excellence has no single mold, particularly in a field as rapidly evolving as AI. We're looking for excellent candidates of all backgrounds with strong business intuition and coding skills, and welcome applicants regardless of ethnic/national origin, gender, race, religious beliefs, disability, sexual orientation or age."
    
    results = engine.match_best_resume(user_id, jd_text, k=3)
    
    print(f"\n{'='*80}")
    print(f"RESULTS: Found {len(results)} candidates")
    print(f"{'='*80}\n")
    
    for i, res in enumerate(results, 1):
        print(f"{i}. {res.get('filename', 'Unknown')}")
        print(f"   Resume ID: {res['resume_id']}")
        print(f"   Score: {res.get('score', 0):.1f}/100")
        print(f"   Reasoning: {res.get('reasoning', 'N/A')}")
        print(f"   Key Matches: {', '.join(res.get('key_matches', []))}")
        print(f"   Gaps: {', '.join(res.get('gaps', []))}")
        print()
        
    if results:
        print("SUCCESS: Matching Engine returned LLM-ranked results.")
    else:
        print("FAILURE: No results returned.")

if __name__ == "__main__":
    test_matching_engine()
