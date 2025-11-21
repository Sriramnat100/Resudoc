import os
from reportlab.pdfgen import canvas
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from pdf_reader import PDFReader

def create_dummy_pdf(filename, text):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, text)
    c.save()

def test_pdf_reader():
    filename = "test_resume.pdf"
    expected_text = "This is a test resume content."
    
    print(f"Creating dummy PDF: {filename}...")
    create_dummy_pdf(filename, expected_text)
    
    reader = PDFReader()
    
    try:
        print("Reading PDF...")
        content = reader.read_pdf(filename)
        print(f"Extracted Content: '{content}'")
        
        if expected_text in content:
            print("SUCCESS: Text extracted correctly.")
        else:
            print("FAILURE: Extracted text does not match expected text.")
            
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print("Cleaned up test file.")

if __name__ == "__main__":
    test_pdf_reader()
