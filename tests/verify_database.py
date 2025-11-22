import os
import psycopg2
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def verify_connection():
    url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {url}")
    
    try:
        conn = psycopg2.connect(url)
        print("SUCCESS: Connected to database!")
        
        # Verify vector extension
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            if cur.fetchone():
                print("SUCCESS: pgvector extension is enabled.")
            else:
                print("WARNING: pgvector extension is NOT enabled.")
                
        conn.close()
        
    except Exception as e:
        print(f"FAILURE: Could not connect. Error: {e}")

if __name__ == "__main__":
    verify_connection()
