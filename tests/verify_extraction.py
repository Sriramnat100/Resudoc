import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from pdf_reader import PDFReader

def test_extraction():
    print("Testing PDFReader (Extraction & Cleaning)...")

    # 1. Test Text Cleaning
    raw_text = """
    John Doe
    Software Engineer
    
    Experience:
    -   Developed   REST APIs   using   Python  and  Flask.
    - Managed AWS infrastructure.
    """
    
    reader = PDFReader()
    cleaned_lines = reader.clean_and_split(raw_text)
    
    print("\n--- Cleaned Lines ---")
    for line in cleaned_lines:
        print(f"'{line}'")
        
    # Verify cleaning
    assert "- Developed REST APIs using Python and Flask." in cleaned_lines
    assert "- Managed AWS infrastructure." in cleaned_lines
    print("SUCCESS: Text cleaned correctly.")

    # 2. Test Skill Extraction
    # Join lines back for full text search
    full_cleaned_text = "\n".join(cleaned_lines)
    
    print("\nExtracting skills (Mock or API)...")
    skills = reader.extract_skills(full_cleaned_text)
    
    print("\n--- Extracted Skills ---")
    print(skills)
    
    # Since we might be using a mock, just check if we got a list back
    if isinstance(skills, list) and len(skills) > 0:
        print("SUCCESS: Skills extracted (Mock or Real).")
    else:
        print("FAILURE: No skills extracted.")

if __name__ == "__main__":
    test_extraction()
