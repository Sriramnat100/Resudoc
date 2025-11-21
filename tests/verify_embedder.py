import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from embedder import Embedder
import os

def test_embedder():
    print("Testing Embedder...")
    
    # Check if API key is present
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("NOTE: OPENAI_API_KEY not found. Expecting mock embedding.")
    
    embedder = Embedder()
    text = "This is a test resume summary."
    
    print(f"Generating embedding for: '{text}'")
    vector = embedder.get_embedding(text)
    
    print(f"Vector length: {len(vector)}")
    
    # text-embedding-3-small has 1536 dimensions
    expected_dim = 1536
    
    if len(vector) == expected_dim:
        print(f"SUCCESS: Generated embedding with correct dimension ({expected_dim}).")
    else:
        print(f"FAILURE: Expected dimension {expected_dim}, got {len(vector)}.")

    # Check content (just ensure it's not all zeros if we have a key)
    if api_key and all(v == 0.0 for v in vector):
         print("WARNING: Vector is all zeros despite having API key. Something might be wrong.")
    elif not api_key and all(v == 0.0 for v in vector):
         print("SUCCESS: Mock embedding returned (all zeros) as expected without key.")

    # Test Batch Embedding
    print("\nTesting Batch Embedding...")
    texts = ["Hello world", "Another sentence", "Python is great"]
    vectors = embedder.get_embeddings_from_list(texts)
    
    print(f"Generated {len(vectors)} vectors for {len(texts)} texts.")
    
    if len(vectors) == len(texts):
        if all(len(v) == expected_dim for v in vectors):
            print("SUCCESS: Batch embeddings generated with correct dimensions.")
        else:
            print("FAILURE: Incorrect vector dimensions in batch.")
    else:
        print("FAILURE: Batch size mismatch.")

if __name__ == "__main__":
    test_embedder()
