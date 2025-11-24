import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2

def add_tags_column():
    """
    Migration script to add tags column to existing resumes table.
    """
    connection_string = os.getenv("DATABASE_URL")
    
    if not connection_string:
        print("Error: DATABASE_URL not found in environment")
        return False
    
    try:
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()
        
        print("Adding tags column to resumes table...")
        
        # Add tags column if it doesn't exist
        cur.execute("""
            ALTER TABLE resumes 
            ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
        """)
        
        print("Creating GIN index on tags...")
        
        # Create GIN index for fast tag queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_resumes_tags 
            ON resumes USING GIN(tags);
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    add_tags_column()
