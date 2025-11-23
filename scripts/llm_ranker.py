import os
from dotenv import load_dotenv
load_dotenv()
import json
from typing import List, Dict, Any
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMRanker:
    """
    Uses LLM to rank multiple resume candidates against a job description in a single batch call.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the LLM Ranker.
        
        Args:
            api_key (str): OpenAI API key. If None, reads from env OPENAI_API_KEY.
            model (str): The model to use. Defaults to "gpt-4o" for best reasoning.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def rank_resumes_batch(self, jd_text: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks all k resume candidates against a job description in ONE LLM call.
        
        Args:
            jd_text (str): The job description text
            candidates (List[Dict]): List of candidate dicts with keys:
                - 'resume_id': str
                - 'filename': str
                - 'content': str
        
        Returns:
            List[Dict] sorted by score (highest first), each containing:
                - 'resume_id': str
                - 'filename': str
                - 'score': float (0-100)
                - 'reasoning': str
                - 'key_matches': List[str]
                - 'gaps': List[str]
        """
        if not candidates:
            return []
        
        if not self.client:
            print("Warning: OpenAI client not initialized. Returning mock rankings.")
            # Return mock data for testing
            return [
                {
                    "resume_id": c['resume_id'],
                    "filename": c['filename'],
                    "score": 75.0 - (i * 10),
                    "reasoning": f"Mock ranking for {c['filename']}",
                    "key_matches": ["Python", "Mock Skill"],
                    "gaps": ["Mock Gap"]
                }
                for i, c in enumerate(candidates)
            ]
        
        # Build the prompt with JD and all candidates
        prompt = self._build_batch_ranking_prompt(jd_text, candidates)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical recruiter with deep knowledge of software engineering, AI/ML, and technology roles. Your job is to objectively evaluate resume-job fit."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            
            # Extract rankings and sort by score
            rankings = result.get("rankings", [])
            
            # Sort by score (highest first)
            rankings.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return rankings
            
        except Exception as e:
            print(f"Error in LLM ranking: {e}")
            # Return candidates with default scores
            return [
                {
                    "resume_id": c['resume_id'],
                    "filename": c['filename'],
                    "score": 50.0,
                    "reasoning": f"Error during ranking: {str(e)}",
                    "key_matches": [],
                    "gaps": []
                }
                for c in candidates
            ]
    
    def _build_batch_ranking_prompt(self, jd_text: str, candidates: List[Dict[str, Any]]) -> str:
        """
        Builds the prompt for batch ranking all candidates.
        """
        # Build candidate sections
        candidate_sections = []
        for i, candidate in enumerate(candidates, 1):
            candidate_sections.append(f"""
=== CANDIDATE {i}: {candidate['filename']} ===
Resume ID: {candidate['resume_id']}

{candidate['content'][:3000]}
{'...(truncated)' if len(candidate['content']) > 3000 else ''}
""")
        
        candidates_text = "\n".join(candidate_sections)
        
        prompt = f"""You are evaluating {len(candidates)} resume candidates for the following job description.

=== JOB DESCRIPTION ===
{jd_text[:2000]}
{'...(truncated)' if len(jd_text) > 2000 else ''}

=== CANDIDATES ===
{candidates_text}

=== TASK ===
Rank ALL {len(candidates)} candidates from best to worst fit for this job description.

For each candidate, provide:
1. **score** (0-100): Overall fit score
   - 90-100: Exceptional fit, exceeds requirements
   - 75-89: Strong fit, meets most requirements
   - 60-74: Good fit, meets core requirements
   - 40-59: Moderate fit, some gaps
   - 0-39: Poor fit, significant gaps

2. **reasoning** (2-3 sentences): Why this score? What stands out?

3. **key_matches** (list of 3-5 strings): Specific skills, experiences, or qualifications that match the JD

4. **gaps** (list of 2-4 strings): What's missing or weak compared to the JD

Return your response as a JSON object with this EXACT structure:
{{
  "rankings": [
    {{
      "resume_id": "candidate resume_id here",
      "filename": "candidate filename here",
      "score": 85.0,
      "reasoning": "Your reasoning here",
      "key_matches": ["match1", "match2", "match3"],
      "gaps": ["gap1", "gap2"]
    }},
    ... (one entry for each of the {len(candidates)} candidates)
  ]
}}

IMPORTANT: Include ALL {len(candidates)} candidates in your rankings array. Be objective and specific in your evaluations."""

        return prompt


if __name__ == "__main__":
    # Simple test
    ranker = LLMRanker()
    
    test_jd = "Looking for a Python engineer with ML experience."
    test_candidates = [
        {
            "resume_id": "test-1",
            "filename": "resume1.pdf",
            "content": "Python developer with 5 years experience in machine learning and TensorFlow."
        },
        {
            "resume_id": "test-2",
            "filename": "resume2.pdf",
            "content": "Java developer with backend experience."
        }
    ]
    
    results = ranker.rank_resumes_batch(test_jd, test_candidates)
    
    print("Rankings:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['filename']} - Score: {result['score']}")
        print(f"   Reasoning: {result['reasoning']}")
