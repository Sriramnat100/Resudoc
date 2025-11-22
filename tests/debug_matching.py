import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from db_manager import DbManager
from embedder import Embedder
from pdf_reader import PDFReader
from matching_engine import MatchingEngine

def debug_matching():
    print("=== DEBUGGING MATCHING ENGINE ===\n")
    
    db = DbManager()
    embedder = Embedder()
    reader = PDFReader()
    
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "test-user-123"))
    jd_text = "Responsibilities: Generative AI is a rapidly evolving field and the priorities a genAI team change over time.  We expect internships to cover some of the following responsibilities, but new priorities may emerge Build generative AI applications for Bloomberg Law, Tax, and Government products, and the News and Content teams across those products. Develop or enhance AI agent workflows, including multi-step reasoning and task orchestration. Work with MCP systems to extend agent capabilities and control context. Prototype reinforcement learning for genAI systems to optimize prompts, context and tool calls. Collaborate with news, content, and product teams to evaluate, refine, and integrate models into production environments. Document and present technical findings and prototype outcomes. Qualifications: Pursuing a degree in Computer Science, Machine Learning, Sciences, Math's, or related field. Proficiency in Python Experience with large language models, agentic systems, or reinforcement learning concepts. Be open to full-time work in 2027 How to stand out An exceptional candidate may differentiate themselves with some of the following. These are not requirements and you should feel comfortable applying if you do not meet all of these: Motivation and curiosity: Strong interest in understanding problems, questioning assumptions and then designing solutions. Proactive ownership: when assigned a task, be eager to understand the end goal and to step outside of areas of formal responsibility to meet that goal Built something:  In school or hobby, have built something from scratch or overhauled a non-functional part of a system. Bayesian statistics: Have formal background or work experience in A/B testing and Bayesian statistics Relevant work experience: Exposure to professional Application Design or Data Engineering. Finally, we highlight that excellence has no single mold, particularly in a field as rapidly evolving as AI. We're looking for excellent candidates of all backgrounds with strong business intuition and coding skills, and welcome applicants regardless of ethnic/national origin, gender, race, religious beliefs, disability, sexual orientation or age."
    
    # Extract JD skills
    print("1. EXTRACTING JD SKILLS...")
    jd_skills = reader.extract_skills(jd_text)
    print(f"   Found {len(jd_skills)} skills in JD:")
    for i, skill in enumerate(jd_skills, 1):
        print(f"   {i}. {skill}")
    
    # Get top 3 resume IDs
    print("\n2. FETCHING TOP 3 RESUMES...")
    resume_ids = [
        "77145d8a-3a5f-579a-9b6f-25388d4b0f5a",  # Bloomberg
        "653d3f74-f715-55a4-a798-d0aee43b67f9",  # Regular
        "1870da77-1d10-5598-826c-2fc912fac973"   # Fortive
    ]
    
    resume_details = db.get_resumes_by_ids(resume_ids)
    
    # Show skills for each resume
    print("\n3. RESUME SKILLS COMPARISON:")
    jd_skills_set = set(s.lower() for s in jd_skills)
    
    for rid in resume_ids:
        details = resume_details.get(rid, {})
        filename = details.get('filename', 'Unknown')
        resume_skills = details.get('skills', [])
        
        print(f"\n   {filename}:")
        print(f"   - Total skills: {len(resume_skills)}")
        print(f"   - Skills: {resume_skills[:10]}...")  # Show first 10
        
        # Calculate overlap
        resume_skills_set = set(s.lower() for s in resume_skills)
        overlap = jd_skills_set.intersection(resume_skills_set)
        print(f"   - Overlapping skills: {overlap}")
        print(f"   - Overlap count: {len(overlap)}")
        print(f"   - Skill score: {len(overlap) / len(jd_skills_set) if jd_skills_set else 0:.4f}")
    
    db.close()

if __name__ == "__main__":
    debug_matching()
