import os
import sys
import uuid
from typing import List

# Add scripts dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_reader import PDFReader
from embedder import Embedder
from db_manager import DbManager

def ingest_resumes(directory: str = "Resumes"):
    """
    Reads all PDFs in the directory, processes them, and uploads to Supabase.
    """
    # Go up one level to find the Resumes folder if running from scripts/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, directory)

    if not os.path.exists(full_path):
        print(f"Directory '{full_path}' not found.")
        return

    # Initialize components
    pdf_reader = PDFReader()
    embedder = Embedder()
    db = DbManager()

    # Test User ID for this batch (using deterministic UUID)
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "test-user-123")) 

    files = [f for f in os.listdir(full_path) if f.lower().endswith('.pdf')]
    
    if not files:
        print(f"No PDF files found in '{full_path}'.")
        return

    print(f"Found {len(files)} resumes in {full_path}. Starting ingestion...")

    for filename in files:
        filepath = os.path.join(full_path, filename)
        print(f"\nProcessing: {filename}")
        
        try:
            # 1. Extract Text & Skills
            text = pdf_reader.read_pdf(filepath)
            cleaned_text = pdf_reader.clean_text(text)
            skills = pdf_reader.extract_skills(cleaned_text)
            
            print(f"   - Extracted {len(cleaned_text)} chars")
            print(f"   - Found {len(skills)} skills: {skills[:3]}...")

            # 2. Generate Embedding
            embedding = embedder.get_embedding(cleaned_text)
            print(f"   - Generated embedding ({len(embedding)} dim)")

            # 3. Generate a deterministic ID based on filename
            resume_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, filename))

            # 4. Upsert to DB
            # Upsert Metadata (including filename)
            db.upsert_resume(resume_id, user_id, cleaned_text, skills, filename)
            # Upsert Embedding
            db.upsert_embedding(resume_id, user_id, embedding)
            
            print(f"   - Saved to DB (ID: {resume_id})")

        except Exception as e:
            print(f"   - ERROR: {e}")

    print("\nIngestion Complete!")
    db.close()

if __name__ == "__main__":
    ingest_resumes()
    

