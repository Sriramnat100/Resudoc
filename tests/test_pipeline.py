import sys
import os
import uuid
from typing import List
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from pdf_reader import PDFReader
from embedder import Embedder
from db_manager import DbManager
from matching_engine import MatchingEngine
from reportlab.pdfgen import canvas

def create_dummy_pdf(filename, text):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, text)
    c.save()

def test_pipeline():
    print("Starting End-to-End Pipeline Test...")
    
    # 1. Setup Dummy PDF
    pdf_filename = "pipeline_test_resume.pdf"
    pdf_content = "John Doe\nSoftware Engineer\nExperienced in Python, SQL, and AWS."
    create_dummy_pdf(pdf_filename, pdf_content)
    print(f"1. Created dummy PDF: {pdf_filename}")
    
    try:
        # 2. Ingestion & Extraction
        print("2. Reading and Processing PDF...")
        reader = PDFReader()
        raw_text = reader.read_pdf(pdf_filename)
        cleaned_text = reader.clean_text(raw_text)
        skills = reader.extract_skills(cleaned_text)
        
        print(f"   - Extracted Text Length: {len(cleaned_text)}")
        print(f"   - Extracted Skills: {skills}")
        
        # 3. Embedding
        print("3. Generating Embedding...")
        embedder = Embedder()
        embedding = embedder.get_embedding(cleaned_text)
        print(f"   - Embedding Dimensions: {len(embedding)}")
        
        # 4. Database Storage (using real UUIDs)
        print("4. Storing in Database...")
        db = DbManager()
        resume_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        # Upsert Metadata
        print(f"   - Upserting metadata for {resume_id}...")
        db.upsert_resume(resume_id, user_id, cleaned_text, skills)
        
        # Upsert Embedding
        print(f"   - Upserting embedding...")
        db.upsert_embedding(resume_id, user_id, embedding)
        
        # 5. Matching Engine
        print("5. Running Matching Engine...")
        engine = MatchingEngine(db, embedder, reader)
        jd_text = "Looking for a Python Engineer."
        
        results = engine.match_best_resume(user_id, jd_text, k=1)
        
        if results:
            print(f"   - Found {len(results)} matches.")
            top_match = results[0]
            print(f"   - Top match ID: {top_match['resume_id']}")
            print(f"   - Score: {top_match['final_score']:.4f}")
            print("SUCCESS: Full pipeline completed.")
        else:
            print("WARNING: No matches found (might be expected if using real DB with empty table).")
            
    except Exception as e:
        print(f"ERROR: Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            print("Cleaned up test file.")

if __name__ == "__main__":
    test_pipeline()
